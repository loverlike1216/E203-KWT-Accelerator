# Changelog

## v1 — 2026-10-17

- User confirmed project identity and authorized a portable local reference
  environment pending the official server; preserve the same v1.
- Installed isolated model dependencies, verified portable Icarus/Yosys and RISC-V
  compiler archives, pinned ARM and public E203 sources and full public dataset.
- Passed three unchanged reference E203 ISA firmware tests.
- Bound every real checkpoint inference tensor exactly and confirmed twelve
  64x256 FFN first-layer kernels; documented old CLI/runtime compatibility.
- Calibrated INT16 with training-only data; passed independent speech validation.
  Retained INT8's single-task failures rather than relaxing the 3% gate.
- Implemented four-lane hardware MAC, one-port synchronous SRAM banks, sequential
  loading/physical clearing and protocol checks. Passed twelve complete real layer
  matrices, all output bits, signed boundaries/reset/error/backpressure.
- Passed generic core synthesis and mapped boundary simulation. Optional bounded
  SAT equivalence timed out and remains UNVERIFIED.
- Passed genuine E203 reference C driver/hardware/readback tasks for layers 1 and
  12, all 25,344 outputs each. Every task issued 770,030 CPU instructions, performed
  62,560 shared reads and 1,622,016 hardware MACs. Initial harness time-unit failures
  were diagnosed, retained and fixed without modifying upstream source.
- Clean checkout / second venv reproduced 48 vector files byte for byte and all
  304,128 RTL output comparisons. Official/Linux replay remains unverified.
- Added reproducible entry points, official-flow guards, migration map, evidence
  boundaries, interaction audit and recoverable checkpoints. Official acceptance
  remains REVISE until official platform/STA/area/power gates are closed.
