# v1 portable local baseline delivery

Competition verdict: **REVISE**. Local numeric/RTL/reference integration evidence
is available; required official platform/STA/area/power evidence is absent.
All local results below are **ALTERNATIVE_VALIDATION**.

## Executed local results

- Actual ARM commit 237e4097afd4f6851e0b82f0a8d65c2dfe8eae30 checkpoint,
  every inference tensor restored exactly, twelve 64x256 FFN kernels verified.
- 89 training calibration samples and 45
  separate validation samples, no testing samples. 13,685,760
  software outputs per candidate format evaluated.
- INT16 maximum layer aggregate NRMSE 0.01029856%;
  maximum validation-task NRMSE 0.01560948%.
  Input saturations 0; accumulator overflows
  0. All decoded outputs finite.
- Twelve actual layer RTL tasks, 304,128 raw signed48
  outputs bit-exact. Physical operand clearing, sequential reload, signed extremes,
  zero/bias, reset abort, overflow/errors and channel stalls checked.
- Generic mapped core contains 11,855
  generic logic cells; this is not physical area. Mapped boundary simulation passes;
  complete generic SAT proof timed out and remains UNVERIFIED.
- Clean source checkout and a second venv reproduced all 48 vector files byte for
  byte, the full quantized output hash and twelve-layer RTL results. Verified
  public source/tool caches were reused. Linux/server replay remains open.

## Actual reference CPU / hardware tasks

| Layer | Outputs checked | CPU instructions issued | Shared reads | Engine bus writes | Hardware MACs | CPU-load to final writeback cycles | Total cycles through CPU readback |
|---|---|---|---|---|---|---|---|
| 1 | 25344 | 770030 | 62560 | 11874 | 1622016 | 956689 | 1319761 |
| 12 | 25344 | 770030 | 62560 | 11874 | 1622016 | 956689 | 1319761 |

Each task runs actual ELF/HEX firmware on the public E203 core, copies operands,
starts the hardware, polls completion and reads all results. The testbench compares
every result and the CPU's checksum. No expected results are embedded in firmware.
The two reference CPU tasks are layers 1 and 12; all twelve parameter sets were
tested in the accelerator-level continuous regression. This does not certify the
official SoC or a full twelve-task CPU regression.

Timing above excludes initial testbench preload into shared SRAM. It is not Q13
official cold-start throughput. No task/s or J/task is claimed from these counts.

## Open mandatory official gates

- Official E203/platform/parameter loader and shared SRAM arbitration binding.
- Official SRAM models/area data, standard cells/corners/SDC, 150 MHz STA.
- <=2.25 mm2 accelerator/interface/internal macro accounting.
- Full official netlist function/equivalence and complete activity annotation.
- E203/interconnect/engine/shared and internal SRAM dynamic/static power; matching
  cold-task timing, official workload throughput and J/task.
- Organizer-selected 600 accuracy samples and twelve performance tasks.
- Official-server clean replay and independent final review.

Local TensorFlow is 2.10.1 rather than upstream 2.4.0rc1. Revalidate runtime parity
on the official server. INT8's single-task failures and initial model/SoC harness
failures were preserved. No threshold was weakened. Innovation remains unclaimed
pending a complete baseline and same-condition comparisons.

## Reproduce and migrate

Read README.md, shared/CONTEXT_CHECKPOINT.md, REQUIREMENTS_TRACEABILITY.md,
v1/reports/WARNINGS_AND_LIMITATIONS.md and v1/MIGRATION_TO_OFFICIAL.md.
Use run.ps1 or the portable Python/Make entry. Official missing-input commands fail
with BLOCKED/nonzero. Keep restricted inputs and credentials outside public Git.
Remain in v1; no repository/goal/version upgrade is authorized.
