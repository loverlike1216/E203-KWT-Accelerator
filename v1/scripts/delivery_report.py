import json
from common import ROOT, REPORTS, write_json


def read(name):
    return json.loads((REPORTS/name).read_text(encoding="utf-8"))


def main():
    quant=read("model/quantization.json")
    engine=read("rtl/engine.json")
    soc=read("soc/accelerator_soc.json")
    synthesis=read("synthesis/reference.json")
    replay=read("environment/clean_replay.json")
    if any(d["status"]!="PASS" for d in (quant,engine,soc,synthesis,replay)):
        raise RuntimeError("Local milestone is incomplete; do not write a completed delivery report")
    value=quant["candidate_results"]["16"]
    tests=soc["tests"]
    text=f"""# v1 portable local baseline delivery

Competition verdict: **REVISE**. Local numeric/RTL/reference integration evidence
is available; required official platform/STA/area/power evidence is absent.
All local results below are **ALTERNATIVE_VALIDATION**.

## Executed local results

- Actual ARM commit 237e4097afd4f6851e0b82f0a8d65c2dfe8eae30 checkpoint,
  every inference tensor restored exactly, twelve 64x256 FFN kernels verified.
- {quant['calibration_samples']} training calibration samples and {quant['validation_samples']}
  separate validation samples, no testing samples. {value['total_output_elements']:,}
  software outputs per candidate format evaluated.
- INT16 maximum layer aggregate NRMSE {100*value['max_layer_nrmse']:.8f}%;
  maximum validation-task NRMSE {100*max(value['max_task_nrmse']):.8f}%.
  Input saturations {sum(value['input_saturations'])}; accumulator overflows
  {value['accumulator_overflows']}. All decoded outputs finite.
- Twelve actual layer RTL tasks, {engine['bit_exact_outputs']:,} raw signed48
  outputs bit-exact. Physical operand clearing, sequential reload, signed extremes,
  zero/bias, reset abort, overflow/errors and channel stalls checked.
- Generic mapped core contains {synthesis['core_statistics']['design']['num_cells']:,}
  generic logic cells; this is not physical area. Mapped boundary simulation passes;
  complete generic SAT proof timed out and remains UNVERIFIED.
- Clean source checkout and a second venv reproduced all 48 vector files byte for
  byte, the full quantized output hash and twelve-layer RTL results. Verified
  public source/tool caches were reused. Linux/server replay remains open.

## Actual reference CPU / hardware tasks

| Layer | Outputs checked | CPU instructions issued | Shared reads | Engine bus writes | Hardware MACs | CPU-load to final writeback cycles | Total cycles through CPU readback |
|---|---|---|---|---|---|---|---|
"""
    for t in tests:
        text+=f"| {t['layer']} | {t['outputs']} | {t['instructions_issued']} | {t['shared_reads']} | {t['accelerator_writes']} | {t['macs']} | {t['cpu_load_to_writeback_cycles']} | {t['total_cycles']} |\n"
    text+="""
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
"""
    (REPORTS/"LOCAL_BASELINE_DELIVERY.md").write_text(text,encoding="utf-8")
    write_json(REPORTS/"FINAL_STATUS.json",{"verdict":"REVISE","local_baseline":"VERIFIED_WITH_LIMITATIONS",
        "evidence_class":"ALTERNATIVE_VALIDATION","active_version":"v1",
        "max_validation_layer_nrmse":value["max_layer_nrmse"],"rtl_exact_outputs":engine["bit_exact_outputs"],
        "reference_soc_layers":[t["layer"] for t in tests],"official_timing_150mhz":"NOT_VERIFIED",
        "official_area_mm2":None,"official_power_watts":None,"official_energy_j_per_task":None,
        "official_throughput_tasks_per_second":None,"official_600_samples":"NOT_VERIFIED",
        "official_netlist_equivalence":"NOT_VERIFIED","generic_sat_equivalence":"UNVERIFIED",
        "next_action":"Audit official server/source/macros/flow on receipt, port adapters and re-run official gates in v1."})


if __name__=="__main__":
    main()
