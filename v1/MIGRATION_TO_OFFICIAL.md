# Migration to the official server — same v1

1. Read shared/CONTEXT_CHECKPOINT.md, state, decisions and acceptance; fetch the
   specified repository and record the server checkout path/branch/commit.
   Do not create v2 or replace the repository. Never copy Windows binaries to Linux.
2. Audit the actual tool versions/license method without logging credentials;
   official E203 top, clocks/resets, bus/NICE, address map, testbench and firmware
   loader; shared SRAM ports/arbitration and macro interfaces; cell/SRAM libraries,
   corners/area data, SDC and power/activity flow. Hash restricted files locally.
3. Copy official.template.json to an ignored inputs/official profile. Fill exact
   paths and commands arrays for synth/sta/power/benchmark. Do not commit restricted
   bytes, private server addresses, accounts, library content or license details.
   Add the actual sim-soc/regress command arrays too. An explicit official profile
   never falls back to the public reference simulation. Commands must not contain
   plaintext credentials; license access is configured outside the recorded argv.
4. Recreate a Python environment matching the organizer's prescribed runtime. The
   local lock is Python 3.10 / TensorFlow 2.10.1; upstream used 2.4.0rc1. Validate
   explicit checkpoint bindings and unchanged preprocessing/layers. Regenerate
   cutpoints, numeric metrics and vector hashes; compare without lowering 3%.
5. Replace only the reference platform wrapper and SRAM binding first. The compute
   core has request/response/output handshakes; linear_mmio uses one synchronous
   port per bank. Official macros may have different polarity/latency/read-during-
   write semantics. Implement an audited adapter; do not invent macro pin names.
   Reference addresses are proposals only. Confirm external shared SRAM port rights
   before adapting the serialized result writeback.
6. Run the unchanged official SoC baseline, then the actual C driver and full-matrix
   hardware path. Integrate the official parameter loader and cold-cache clearing.
   Include its input/parameter loading, E203 scheduling, arbitration/waits and final
   writeback in timing. Current local CPU-load cycle counts exclude testbench
   preload; they are not the official benchmark.
7. Repeat numeric, boundary/reset/backpressure, full 12-layer, official SoC and
   post-synthesis regressions. Run official 150 MHz STA without hiding paths;
   sum accelerator/interface/internal SRAM area <=2.25 mm2 and report fixed SoC
   area separately. Audit activity annotation and SRAM power; report total system
   dynamic/static power and matching-window J/task. Unknown power stays unknown.
8. Freeze one configuration before matched-condition optimization/ablation. Preserve
   the baseline and failed experiments. Innovation cannot displace mandatory gates.
9. Clean-checkout replay, update requirement matrix and checkpoint, secret scan,
   commit/push only permitted text. Verdict remains REVISE while mandatory official
   gates are open. No release, spending or irreversible action is authorized.

Portable interfaces: v1/rtl/linear_engine.sv; v1/rtl/linear_mmio.sv;
v1/model/integer_reference.py; v1/firmware/driver.h and driver.c. Reference-only
bindings: reference_soc.sv, sram16_reference.sv, local addresses/linker and local tools.
