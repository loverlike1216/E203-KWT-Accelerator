# Warning review and scope limits

- Local Python uses TensorFlow 2.10.1 instead of upstream 2.4.0rc1. Every inference
  variable is explicitly checked against the actual checkpoint. No upstream-
  runtime or official-600 equivalence claim follows from that check.
- Native CPU inference reports unavailable CUDA DLLs. GPU is not required for
  this CPU-only environment; no GPU tool or driver was installed.
- Yosys converts four accumulator array entries to registers, as intended. They
  are compute state, not SRAM. Operand storage is separately retained as eighteen
  inferred memory cells, with one synchronous read/write port per bank.
- ABC reports combinational networks while mapping logic cones. Sequential state
  is retained outside those combinational cones; Yosys check reports no problems.
- Standalone RTL units contain no delay statements and inherit simulation units.
  E203 upstream units do contain #1 flop delays. The reference SoC compiles the
  explicit simulation_timescale.v prefix first; failed pre-fix runs are retained.
- The upstream Icarus reference flow disables its unsupported SV assertion blocks
  with DISABLE_SV_ASSERTION, as its Makefile specifies. Project testbench fatal
  checks remain active. This is not proof that every upstream assertion was run.
- Generic mapped core boundary tests pass. The optional 180-second SAT equivalence
  attempt timed out; no full formal equivalence conclusion is claimed.
- Reference CPU/TCMs, ICB addresses and dual-port shared SRAM are local bindings.
  Official bus arbitration/ports/reset/loader and macro latency require a fresh audit.
- Local task timing excludes initial testbench preload into shared SRAM. No official
  throughput, 150 MHz STA, physical area, average power or J/task is reported.
- The debug VCD is a boundary-test waveform, not representative full-system power
  activity. Unknown SRAM power and missing annotation are never treated as zero.
- Clean replay covers model/quantization/twelve-layer RTL/generic synthesis in a
  second venv, sharing verified source/tool caches. It is not Linux/server evidence.
- No innovation/PPA improvement is asserted. Baseline preservation precedes future
  same-condition optimization and ablation.
