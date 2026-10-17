"""Audit actual checkpoint and original inference; never modify upstream files."""
import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
import argparse
import json
import sys
from common import ROOT, WORK, REPORTS, sha256, write_json
sys.path.insert(0, str(ROOT / "external/src/keyword-transformer"))
import numpy as np
import tensorflow as tf
from kws_streaming.train.base_parser import base_parser
from kws_streaming.layers.speech_features import SpeechFeatures
from kws_streaming.models.transformer_utils import KWSTransformer

MODEL_DIR = ROOT / "external/src/keyword-transformer/models_data_v2_12_labels/kwt1"


def load_model():
    tf.keras.backend.clear_session()
    tf.keras.utils.set_random_seed(20261017)
    flags = base_parser().parse_args([])
    flags.__dict__.update(json.loads((MODEL_DIR / "flags.json").read_text()))
    # Explicit inference overrides; pretrained arithmetic and dimensions stay fixed.
    flags.__dict__.update(batch_size=1, training=False, train=0, prenorm=False,
        approximate_gelu=False, distill_teacher_json=None, use_spec_augment=0,
        use_spec_cutout=0, time_shift_ms=0.0, sp_time_shift_ms=0.0,
        resample=0.0, sp_resample=0.0, background_frequency=0.0)
    assert (flags.num_layers, flags.d_model, flags.mlp_dim, flags.heads) == (12, 64, 256, 1)
    # Importing upstream's CLI registry disables eager execution through input_data.
    # Instantiate its unchanged original layers and bind checkpoint tensors by their
    # semantic paths: TF 2.4/2.10 Sequential tracking differs around weightless GELU.
    audio = tf.keras.Input(shape=(16000,), batch_size=1)
    features = SpeechFeatures(SpeechFeatures.get_params(flags))(audio)
    transformer = KWSTransformer(num_patches=98, num_layers=12, num_classes=12,
        d_model=64, num_heads=1, mlp_dim=256, dropout=0.0, prenorm=False,
        distill_token=False, approximate_gelu=False)
    head = tf.keras.Sequential([tf.keras.layers.Dense(12)])
    model = tf.keras.Model(audio, [head(transformer(features, training=False))])
    reader = tf.train.load_checkpoint(str(MODEL_DIR / "best_weights"))
    bindings = []
    def bind(variable, path):
        key = path + "/.ATTRIBUTES/VARIABLE_VALUE"
        value = reader.get_tensor(key)
        assert list(value.shape) == variable.shape.as_list(), (key, value.shape, variable.shape)
        variable.assign(value)
        np.testing.assert_array_equal(variable.numpy(), value)
        bindings.append({"variable": variable.name, "checkpoint_key": key,
                         "sha256": __import__("hashlib").sha256(value.tobytes()).hexdigest()})
    prefix = "layer_with_weights-0/"
    for name in ("class_emb", "pos_emb"):
        bind(getattr(transformer, name), prefix + name)
    for name in ("kernel", "bias"):
        bind(getattr(transformer.patch_proj, name), prefix + "patch_proj/" + name)
        bind(getattr(head.layers[0], name), "layer_with_weights-1/layer_with_weights-0/" + name)
    for i, layer in enumerate(transformer.enc_layers):
        p = prefix + f"enc_layers/{i}/"
        for name in ("query_dense", "key_dense", "value_dense", "combine_heads"):
            dense = getattr(layer.att, name)
            bind(dense.kernel, p + f"att/{name}/kernel")
            if dense.use_bias:
                bind(dense.bias, p + f"att/{name}/bias")
        for j, dense in enumerate((layer.ffn.layers[0], layer.ffn.layers[2])):
            for name in ("kernel", "bias"):
                bind(getattr(dense, name), p + f"ffn/layer_with_weights-{j}/" + name)
        for name in ("layernorm1", "layernorm2"):
            for attr in ("gamma", "beta"):
                bind(getattr(getattr(layer, name), attr), p + name + "/" + attr)
    required = {n for n, _ in tf.train.list_variables(str(MODEL_DIR / "best_weights"))
                if ".OPTIMIZER_SLOT/" not in n and n.startswith("layer_with_weights-")}
    assert required == {b["checkpoint_key"] for b in bindings}
    assert len(bindings) == len(model.weights)
    model.checkpoint_bindings = bindings
    assert len(transformer.enc_layers) == 12
    return model, transformer, flags


def cutpoints(model, transformer, audio):
    # Run the exact upstream layer calls, capture the specified FFN input.
    features = model.layers[1](audio, training=False)
    x = transformer.patch_proj(features)
    x = tf.concat([tf.broadcast_to(transformer.class_emb, [1, 1, 64]), x], axis=1)
    x = x + transformer.pos_emb
    result = []
    for layer in transformer.enc_layers:
        original_output, _ = layer(x, training=False)
        attention, _ = layer.att(x)
        ff_input = layer.layernorm1(x + layer.dropout1(attention, training=False))
        ff1 = layer.ffn.layers[0]
        y = ff1(ff_input)
        w, b = ff1.get_weights()
        direct = tf.linalg.matmul(ff_input, w) + b
        np.testing.assert_array_equal(y.numpy(), direct.numpy())
        reconstructed = layer.layernorm2(ff_input + layer.dropout2(layer.ffn(ff_input), training=False))
        np.testing.assert_array_equal(reconstructed.numpy(), original_output.numpy())
        assert tuple(ff_input.shape) == (1, 99, 64)
        assert w.shape == (64, 256) and b.shape == (256,)
        result.append((ff_input.numpy()[0], w, b, y.numpy()[0]))
        x = original_output
    original_logits = model(audio, training=False)
    if isinstance(original_logits, (list, tuple)):
        original_logits = original_logits[0]
    reconstructed_logits = model.layers[-1](x[:, 0])
    np.testing.assert_array_equal(original_logits.numpy(), reconstructed_logits.numpy())
    return result


def main():
    model, transformer, flags = load_model()
    inventory = tf.train.list_variables(str(MODEL_DIR / "best_weights"))
    checkpoints = {p.name: sha256(p) for p in MODEL_DIR.glob("best_weights.*")}
    layers = []
    for i, layer in enumerate(transformer.enc_layers):
        dense = layer.ffn.layers[0]
        layers.append({"layer": i + 1, "kernel_name": dense.kernel.name,
            "kernel_shape": dense.kernel.shape.as_list(), "bias_name": dense.bias.name,
            "bias_shape": dense.bias.shape.as_list(),
            "kernel_sha256": __import__("hashlib").sha256(dense.kernel.numpy().tobytes()).hexdigest(),
            "bias_sha256": __import__("hashlib").sha256(dense.bias.numpy().tobytes()).hexdigest()})
    # Official silence is a real defined input, but not speech calibration.
    cuts = cutpoints(model, transformer, tf.zeros([1, 16000], dtype=tf.float32))
    destination = WORK / "model"
    destination.mkdir(parents=True, exist_ok=True)
    np.savez(destination / "silence_cutpoints.npz", **{
        f"layer{l+1}_{name}": value for l, values in enumerate(cuts)
        for name, value in zip(("x", "w", "b", "y"), values)})
    output = {"status": "PASS", "evidence_class": "ALTERNATIVE_VALIDATION",
        "tensorflow": tf.__version__, "upstream_tensorflow": "2.4.0rc1",
        "upstream_commit": "237e4097afd4f6851e0b82f0a8d65c2dfe8eae30",
        "checkpoint_sha256": checkpoints, "flags_sha256": sha256(MODEL_DIR / "flags.json"),
        "layers": layers, "checkpoint_variables": inventory,
        "weight_restore": "semantic binding of every inference variable; array-equal against checkpoint",
        "checkpoint_bindings": model.checkpoint_bindings,
        "silence_cutpoint_and_logits_reconstruction": "EXACT",
        "readme_mlp_dim": 128, "actual_mlp_dim": flags.mlp_dim,
        "official_600_sample_accuracy": "NOT_VERIFIED",
        "silence_vectors_sha256": sha256(destination / "silence_cutpoints.npz")}
    write_json(REPORTS / "model/checkpoint_inventory.json", output)
    print(json.dumps({k: output[k] for k in ("status", "tensorflow", "actual_mlp_dim", "silence_cutpoint_and_logits_reconstruction")}))


if __name__ == "__main__":
    main()
