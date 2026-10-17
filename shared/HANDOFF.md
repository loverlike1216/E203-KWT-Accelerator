# v1 local reference handoff

Goal: portable undergraduate KWT FFN implementation for later official migration.
Current status: local numeric/RTL/reference integration baseline verified with
explicit limits. Formal competition verdict REVISE; same project/repository/v1.

Inputs reviewed: all bootstrap instruction files, complete 15-page official PDF,
actual approved configuration, GitHub identity/remote, fixed ARM checkpoint/source,
public E203 source and dataset. Original inputs remain local/preserved.

Implemented: workspace-local tools and model venv; exact checkpoint binding;
training-calibrated INT16/signed48 contract; four-lane engine and eighteen
synchronous one-port banks; MMIO protocol; public E203 CPU +512 KiB shared-memory
adapter; genuine C firmware, serializer and all-result CPU readback.

Validated: three unmodified-source reference ISA tests; 89 training/45 validation
samples; twelve full accelerator tasks and 304,128 exact outputs; signed/zero/bias,
reset during accumulation/writeback, overflow/errors and stalls; generic mapped
core boundary simulation; CPU/hardware tasks 1/12 (all outputs); second-venv clean
checkout reproduces all vectors/numeric hash and full accelerator tests.

Failures retained: circular/graph-mode checkpoint loader attempts; initial local
SoC timescale mismatch; diagnostic timeouts; optional generic SAT proof timeout.
Root causes and limits are in v1/reports. No test threshold was lowered.

Open gates: official server/platform/loader/macros/library/flows; exact upstream
runtime parity; official 600 samples and performance selections; official SoC/full
CPU twelve-task regression; official post-synthesis function, 150 MHz STA, <=2.25
mm2 accounting, complete activity power, cold benchmark and J/task. Generic SAT
remains UNVERIFIED. Innovation has not been claimed or scored.

Next action: obtain the official server details, audit actual read-only platform/
tool/library facts, port the reference bus and SRAM bindings, then rerun official
gates in the same v1. Read v1/MIGRATION_TO_OFFICIAL.md before adapting interfaces.
Do not invent bus addresses, macro pins/ports/latency, libraries or power values.

Reproduce locally: Python 3.10 bootstrap, then run.ps1 regress. Detailed commands,
outputs and failure handling are in README. CPU simulation is slower; use selected
layers and up to four independent jobs. Official commands return BLOCKED/nonzero
until real configuration is supplied. Restricted files and credentials stay ignored.

Evidence entry: v1/reports/LOCAL_BASELINE_DELIVERY.md and FINAL_STATUS.json;
state entry: shared/CONTEXT_CHECKPOINT.md. Publication commit is recovered with
git log on that file. Packaging artifacts are in ignored work/delivery/.
