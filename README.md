# E203-KWT-Accelerator — v1

Portable undergraduate KWT-1 FFN accelerator development, pending the organizer's
server and official technology/platform files. Project ID E203-KWT-Accelerator;
repository https://github.com/loverlike1216/E203-KWT-Accelerator.

Current local evidence: actual fixed checkpoint tensors restored exactly; 89
training calibration / 45 separate validation samples; INT16 maximum per-layer
NRMSE 0.01030%; twelve full RTL tasks / 304,128 exact output comparisons; signed
boundaries, reset, errors and backpressure; generic logic synthesis and mapped
core boundary simulation; actual public E203 C driver/hardware/readback tasks for
layers 1 and 12. Read reports for exact values and evidence scope.

Formal competition verdict remains **REVISE**: official SoC, SRAM libraries,
150 MHz STA, 2.25 mm2 area and complete activity-based power are not verified.
The bounded optional generic SAT equivalence attempt timed out; it is not a PASS.
Reference CPU tasks each check all 25,344 outputs, 1,622,016 actual hardware MACs
and the CPU's complete readback checksum. This is reference-platform evidence;
full official SoC and twelve-task CPU regression remain open.

## Restore and reproduce

Read `AGENTS.md`, `bootstrap/PROJECT_INPUTS.yaml`, `shared/CONTEXT_CHECKPOINT.md`,
state, plan, decisions, blockers and acceptance. Continue the same v1.

On Windows, use Python 3.10 and PowerShell 7:

```powershell
python v1/scripts/bootstrap_env.py --dataset
.\run.ps1 env-check
.\run.ps1 dataset-check
.\run.ps1 regress
```

Bootstrap installs into `envs/`, `toolchains/`, `external/src/` and
`external/cache/`; it does not install WSL, alter the global PATH or require paid
services. The dataset is 2.43 GB. All public resources have pinned commits/hashes.
Existing differing/dirty source checkouts cause a failure instead of being reset.

`regress` runs model verification, quantization, public E203 ISA baseline, complete
12-layer RTL, synthesis and one reference SoC task. To exercise more reference SoC
tasks, pass `-Layers '1,2,3,4,5,6,7,8,9,10,11,12' -Jobs 3`. Each selected task boots
independently, with one frozen compiled image and separate process memory/logs.
CPU-level Icarus simulation is
substantially slower than standalone accelerator simulation. Logs are in `work/logs/`.
Each command returns the real failing exit code and stops on failure.

For Linux, provide Icarus/Yosys and a compatible bare-metal RISC-V compiler on PATH,
create the Python 3.10 environment with bootstrap, and use:

```sh
envs/model/bin/python v1/scripts/run.py regress
# Or make regress PYTHON=envs/model/bin/python
```

Linux/official-server replay is pending; Windows results are not represented as
Linux evidence. Official tool/library paths are configured after receipt. `synth`,
`sta`, `power` and `benchmark` deliberately return BLOCKED/nonzero without complete
official configuration; `synth-reference` runs the actual local generic flow.

## Folder map

| Path | Purpose |
|---|---|
| bootstrap/ | Preserved instruction copies and real startup configuration |
| shared/ | Current facts, plan, decisions, blockers and recoverable checkpoints |
| v1/model/ | Numeric contract, scales and independent integer model |
| v1/rtl/ | Compute core, synchronous bank model, MMIO and reference CPU wrapper |
| v1/tb/ | Self-checking core, complete matrix and actual CPU/firmware simulations |
| v1/firmware/ | Genuine RISC-V driver/startup/linker and result-readback program |
| v1/scripts/ | Reproducible acquisition, simulation, synthesis and audit commands |
| v1/reports/ | Compact actual evidence with hashes, commands and limitations |
| work/ | Ignored vectors, logs, waveforms, ELF/HEX, netlists and delivery packages |
| inputs/official/ | Ignored restricted official materials; currently absent |
| AI-interaction-memory/ | Observable conversation and tool-flow provenance |

`external/SOURCES.lock.json` records downloaded public sources. Original preparation
files/PDF stay local and unchanged. PDK, license files, secrets and audio are never
part of source packaging. `run.ps1 package` builds a source archive from tracked
files; dependency caches and full conversation transcripts are excluded.

## Numeric and integration boundaries

X[99,64] x W[64,256] + b[256], twelve distinct layer parameters. INT16 encodings
use training-calibrated power-of-two scales, nearest/ties-even rounding and signed
saturation. Bias and accumulator are signed48; raw outputs decode at the product
scale. Four lanes perform all 1,622,016 MACs per task. No CPU/TB software dot products
replace mandatory arithmetic. INT8 was retained as a rejected screening candidate:
its aggregate error is below 3%, but some single validation tasks exceed 3%.

The local TensorFlow 2.10.1 adapter uses unchanged upstream feature/transformer
classes and exact semantic checkpoint bindings. The upstream runtime was
2.4.0rc1; official-runtime parity remains open. No test-set calibration or model
training was performed. Local samples are not the organizer's 600-sample set.

Read `v1/reports/soc/REFERENCE_INTERFACE.md` for the reference bus/memory map and
timing scope, and **`v1/MIGRATION_TO_OFFICIAL.md`** for the official migration order.
Do not carry reference addresses, macro assumptions, clock-only SDC or generic
gate counts into official acceptance without auditing the actual platform.
