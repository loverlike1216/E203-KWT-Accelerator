"""Training-only calibration, separate real-waveform validation and RTL vectors."""
import hashlib
import json
import sys
from common import ROOT, WORK, REPORTS, sha256, write_json
from model_check import load_model, cutpoints, tf, np
sys.path.insert(0, str(ROOT / "v1/model"))
from integer_reference import encode, linear, scalar_dot, scale_for


def waveform(sample):
    if sample["path"] is None:
        return tf.zeros([1, 16000], tf.float32)
    data = tf.io.read_file(str(ROOT / sample["path"]))
    wav, rate = tf.audio.decode_wav(data, desired_channels=1, desired_samples=16000)
    assert int(rate) == 16000
    return tf.reshape(wav, [1, 16000])


def write_hex(path, values, bits):
    mask = (1 << bits) - 1
    path.write_text("".join(f"{int(v) & mask:0{bits//4}x}\n" for v in np.asarray(values).flat), encoding="ascii")


def main():
    manifest = json.loads((REPORTS / "model/dataset_manifest.json").read_text(encoding="utf-8"))
    model, transformer, _ = load_model()
    calibration = [s for s in manifest["samples"] if s["split"] == "training"]
    validation = [s for s in manifest["samples"] if s["split"] == "validation"]
    max_x = np.zeros(12)
    for i, sample in enumerate(calibration):
        cuts = cutpoints(model, transformer, waveform(sample))
        max_x = np.maximum(max_x, [np.max(np.abs(c[0])) for c in cuts])
        if i % 16 == 0:
            print(f"calibration {i+1}/{len(calibration)}", flush=True)
    configs = {}
    for bits in (8, 16):
        configs[bits] = [{"input_scale": scale_for(float(max_x[l]), bits, margin=1.25),
            "weight_scale": scale_for(float(np.max(np.abs(layer.ffn.layers[0].get_weights()[0]))), bits),
            "input_bits": bits, "weight_bits": bits, "bias_bits": 48, "accumulator_bits": 48}
            for l, layer in enumerate(transformer.enc_layers)]
    vector_dir = WORK / "vectors"
    vector_dir.mkdir(parents=True, exist_ok=True)
    metrics = {bits: {"error_sum": np.zeros(12), "reference_sum": np.zeros(12), "elements": np.zeros(12, dtype=np.int64),
        "input_saturations": np.zeros(12, dtype=np.int64), "max_task_nrmse": np.zeros(12)} for bits in configs}
    tasks = []
    raw_hash = hashlib.sha256()
    for sample_index, sample in enumerate(validation):
        cuts = cutpoints(model, transformer, waveform(sample))
        for l, (x, w, b, y) in enumerate(cuts):
            for bits, config in configs.items():
                cfg = config[l]
                sx, sw = cfg["input_scale"], cfg["weight_scale"]
                xq, saturated = encode(x, sx, bits)
                wq, _ = encode(w, sw, bits)
                bq, bias_saturation = encode(b, sx * sw, 48)
                if bias_saturation:
                    raise RuntimeError("Bias does not fit numeric contract")
                raw = linear(xq, wq, bq)
                for row, col in ((0, 0), (98, 255), (37, 127)):
                    assert raw[row, col] == scalar_dot(xq[row], wq[:, col], bq[col])
                decoded = raw.astype(np.float64) * (sx * sw)
                assert np.isfinite(decoded).all()
                e2, r2 = float(np.sum((decoded-y.astype(np.float64))**2)), float(np.sum(y.astype(np.float64)**2))
                m = metrics[bits]
                m["error_sum"][l] += e2
                m["reference_sum"][l] += r2
                m["elements"][l] += y.size
                m["input_saturations"][l] += saturated
                task_nrmse = (e2/y.size)**0.5 / max((r2/y.size)**0.5, 1e-8)
                m["max_task_nrmse"][l] = max(m["max_task_nrmse"][l], task_nrmse)
                if bits == 16:
                    raw_hash.update(raw.tobytes())
                    # Twelve real independent layer tasks; all tasks separately reloaded.
                    if sample_index == l % len(validation):
                        directory = vector_dir / f"layer{l+1:02}"
                        directory.mkdir(exist_ok=True)
                        for name, value, width in (("x", xq, 16), ("w", wq, 16), ("b", bq, 48), ("y", raw, 48)):
                            write_hex(directory / f"{name}.hex", value, width)
                        tasks.append({"layer": l+1, "sample": sample, "nrmse": task_nrmse,
                            "files": {p.name: sha256(p) for p in directory.glob("*.hex")}})
        if sample_index % 8 == 0:
            print(f"validation {sample_index+1}/{len(validation)}", flush=True)
    results = {}
    for bits, m in metrics.items():
        errors = np.sqrt(m["error_sum"]/m["elements"]) / np.maximum(np.sqrt(m["reference_sum"]/m["elements"]), 1e-8)
        results[str(bits)] = {"layer_nrmse": errors.tolist(), "max_layer_nrmse": float(errors.max()),
            "max_task_nrmse": m["max_task_nrmse"].tolist(), "input_saturations": m["input_saturations"].tolist(),
            "total_output_elements": int(m["elements"].sum()), "status": "PASS" if errors.max() <= 0.03 else "FAIL"}
    # Candidate selection uses the declared conservative INT16 baseline, not a test set.
    if results["16"]["status"] != "PASS" or max(t["nrmse"] for t in tasks) > 0.03:
        raise RuntimeError("INT16 validation did not meet 3%; numeric contract not locked")
    write_json(ROOT / "v1/model/numeric_config.json", {"format": "signed16_x_signed16_bias48_acc48",
        "rounding": "nearest_ties_to_even", "input_encoding": "signed_saturating", "output_encoding": "signed48_exact_accumulator_no_requantization",
        "layers": configs[16], "calibration_manifest_sha256": sha256(REPORTS / "model/dataset_manifest.json")})
    write_json(REPORTS / "model/quantization.json", {"status": "PASS", "evidence_class": "ALTERNATIVE_VALIDATION",
        "calibration_samples": len(calibration), "validation_samples": len(validation), "testing_samples": 0,
        "candidate_results": results, "selected_bits": 16, "rtl_tasks": sorted(tasks, key=lambda t:t["layer"]),
        "validation_raw_output_sha256": raw_hash.hexdigest(), "official_600_samples": "NOT_VERIFIED",
        "tensorflow": tf.__version__, "numeric_config_sha256": sha256(ROOT / "v1/model/numeric_config.json")})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
