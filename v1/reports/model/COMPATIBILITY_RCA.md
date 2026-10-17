# Model loader compatibility investigation

Two actual initial attempts failed; raw evidence is retained in work/logs:
model_check.log and model_check_import_fix.log.

1. Importing kws_transformer directly enters a circular CLI registry import.
2. Registry-first import resolves that import, but input_data.py:43 disables eager
   execution. Tensor.numpy() consequently fails. TF 2.10 also emits checkpoint
   graph-reference warnings around the weightless GELU layer in Sequential.

Root cause: old CLI side effects plus changed checkpoint object tracking, not an
absent checkpoint or a different FFN dimension. Direct tf.train.list_variables
shows twelve real 64x256 kernels and 256 biases in the requested best_weights.

Resolution: import the unchanged upstream SpeechFeatures and KWSTransformer
classes directly; construct exactly the same model topology; restore every
inference variable from its explicit semantic checkpoint path. Require shape
matching, exact array equality and complete inference-variable coverage. Ignore
only optimizer slots. Compare captured cutpoints and the reconstructed logits to
the original layer calls. No upstream files or weights are modified.

This is a local compatibility adapter, not evidence of TF 2.4 runtime equivalence.
Revalidate the official runtime when received.
