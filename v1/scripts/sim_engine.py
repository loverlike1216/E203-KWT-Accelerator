import json
import re
from common import ROOT, WORK, REPORTS, executable, run, sha256, write_json


def main():
    numeric = json.loads((REPORTS / "model/quantization.json").read_text())
    assert numeric["selected_bits"] == 16 and numeric["status"] == "PASS"
    directory = WORK / "engine"
    directory.mkdir(parents=True, exist_ok=True)
    rtl = [ROOT / "v1/rtl" / name for name in ("linear_engine.sv", "sram16_reference.sv", "linear_mmio.sv")]
    results = {}
    for top in ("tb_core_edges", "tb_engine"):
        output = directory / (top + ".vvp")
        _, compile_info = run([executable("iverilog"), "-g2012", "-Wall", "-s", top,
            "-o", output, *rtl, ROOT / "v1/tb" / (top + ".sv")], top + "_compile")
        text, info = run([executable("vvp"), output, f"+VECTORS={(WORK/'vectors').as_posix()}"], top, cwd=directory, timeout=900)
        marker = "CORE_EDGES_PASS" if top == "tb_core_edges" else "ENGINE_PASS"
        if marker not in text:
            raise RuntimeError(f"Missing actual simulator completion marker: {marker}")
        results[top] = {"status": "PASS", "compile": compile_info, "run": info}
        if top == "tb_engine":
            layers = [{"layer":int(l),"outputs":int(o),"macs":int(m),"compute_cycles":int(c)}
                      for l,o,m,c in re.findall(r"LAYER_PASS layer=(\d+) outputs=(\d+) macs=(\d+) compute_cycles=(\d+)",text)]
            assert len(layers) == 12 and sum(l["outputs"] for l in layers) == 304128
            results["layers"] = layers
    write_json(REPORTS / "rtl/engine.json", {"status": "PASS", "evidence_class": "ALTERNATIVE_VALIDATION",
        "rtl_sha256": {p.name:sha256(p) for p in rtl}, "numeric_config_sha256":sha256(ROOT/"v1/model/numeric_config.json"),
        "checks":results,"bit_exact_outputs":304128,"cold_clear":"all reference SRAM banks physically zeroed before complete sequential reload",
        "formal_timing_area_power": "NOT_VERIFIED", "sram_binding": "synchronous reference, not official macros"})


if __name__ == "__main__":
    main()
