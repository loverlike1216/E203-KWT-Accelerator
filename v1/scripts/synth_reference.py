import json
from common import ROOT, WORK, REPORTS, executable, run, sha256, write_json


def quoted(path):
    return '"' + path.as_posix().replace('"','\\"') + '"'


def main():
    output = WORK/"synthesis"
    output.mkdir(parents=True,exist_ok=True)
    core=ROOT/"v1/rtl/linear_engine.sv"
    netlist=output/"linear_engine_netlist.v"
    stat=output/"core_stat.json"
    script=output/"core.ys"
    script.write_text(f"read_verilog -sv {quoted(core)}\nsynth -top linear_engine\ncheck -assert\ntee -o {quoted(stat)} stat -json\nwrite_verilog -noattr {quoted(netlist)}\n",encoding="utf-8")
    _,synthesis=run([executable("yosys"),"-s",script],"synth_core",timeout=300)
    gateimage=output/"gate_edges.vvp"
    _,compile_info=run([executable("iverilog"),"-g2012","-s","tb_core_edges","-o",gateimage,
        netlist,ROOT/"v1/tb/tb_core_edges.sv"],"gate_edges_compile")
    text,gate=run([executable("vvp"),gateimage],"gate_edges",cwd=output,timeout=180)
    if "CORE_EDGES_PASS" not in text:
        raise RuntimeError("Mapped netlist boundary regression did not pass")
    # Keep real inferred memories; do not turn reference storage into fake hard macros.
    wrapper=output/"wrapper.ys"
    wrapper_stat=output/"wrapper_stat.json"
    rtl=[ROOT/"v1/rtl"/name for name in ("linear_engine.sv","sram16_reference.sv","linear_mmio.sv")]
    wrapper.write_text("read_verilog -sv "+" ".join(map(quoted,rtl))+"\nhierarchy -check -top linear_mmio\nproc\nopt\nmemory_dff\nmemory_collect\nopt\ncheck -assert\ntee -o "+quoted(wrapper_stat)+" stat -json\n",encoding="utf-8")
    _,memory=run([executable("yosys"),"-s",wrapper],"synth_wrapper",timeout=300)
    write_json(REPORTS/"synthesis/reference.json",{"status":"PASS","evidence_class":"ALTERNATIVE_VALIDATION",
        "core_rtl_sha256":sha256(core),"mapped_netlist_sha256":sha256(netlist),"mapped_netlist_path":str(netlist.relative_to(ROOT)).replace("\\","/"),
        "core_synthesis":synthesis,"gate_compile":compile_info,"gate_edges":gate,"wrapper_memory_inference":memory,
        "core_statistics":json.loads(stat.read_text()),"wrapper_statistics":json.loads(wrapper_stat.read_text()),
        "official_sta":"NOT_VERIFIED","official_area_mm2":None,"official_power_watts":None,
        "limits":["Generic logic mapping, not official standard cells.","Reference SRAM memories remain inferred, not official macros.",
                  "Post-synthesis boundary tests only; full-matrix post-synthesis equivalence remains open."]})


if __name__=="__main__":
    main()
