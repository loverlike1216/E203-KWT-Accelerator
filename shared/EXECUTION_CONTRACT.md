# v1 local reference environment and portable implementation

Goal: implement the undergraduate first FFN linear layer using actual KWT-1
weights and inputs, then migrate the same v1 to the official environment.

Authorized by the user on 2026-10-17: build a suitable similar environment now
and develop for later migration. This supersedes the preceding wait instruction.

Scope: workspace-local dependencies, pinned ARM model, numeric verification,
synthesizable RTL, reference E203 investigation/integration when feasible,
open source simulation and synthesis, replay scripts, evidence and Git sync.

Non-goals: official PPA acceptance without official libraries and tools; physical
design or fabrication; training or changing the pretrained model; v2.

Constraints and invariants:
- Exactly 99 x 64 input, 64 x 256 weights, 256 bias, 99 x 256 output, 12 layers.
- Extract each FFN input after attention, residual and the first LayerNorm.
- No software or testbench substitution for mandatory hardware arithmetic.
- Calibration uses training data; validation is separate; no test-set tuning.
- Cold task timing includes input/parameter loading and complete output writeback.
- Default clock target 150 MHz; official timing/area/power remain unverified.
- Original preparation materials and all official libraries stay local and ignored.
- Preserve remote history and source evidence; no force push or version upgrades.

Current adopted local baseline: four output-stationary INT16 lanes, exact signed48
bias/accumulation, explicit request/response/writeback handshakes, 6x16x4096 and
12x16x128 single-port operand banks. Reference ICB MMIO loads operands; a serializer
writes results through the second port of a reference 512 KiB shared SRAM. Actual
E203 C firmware controls work and reads every result. Formal official bus, shared
SRAM arbitration/port access and hard-macro bindings remain provisional pending
actual platform evidence. The official architecture is not frozen by this baseline.

Validation: checkpoint tensor inventory; actual inference cutpoints; independent
integer model; actual RTL full-output comparisons; reset/continuous/boundary
tests; honest evidence labels; clean replay and protected-input hashes.

Evidence required: executed commands, return codes, versions, input/output hashes,
raw logs locally, compact reports in Git, and checkpoints at material milestones.

Rollback: source changes tracked in Git; generated data/dependencies isolated in
ignored directories. Do not remove or rewrite user history.

Done when: portable local evidence is reproducible, independent work is complete,
and remaining official-only gates are explicitly recorded with migration steps.
