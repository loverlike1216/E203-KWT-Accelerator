import json
import subprocess
from common import ROOT, WORK, REPORTS, executable, run, sha256, write_json
from synth_reference import quoted


def main():
    core=ROOT/"v1/rtl/linear_engine.sv"
    netlist=WORK/"synthesis/linear_engine_netlist.v"
    if not netlist.exists():
        raise RuntimeError("Run synth-reference first")
    script=WORK/"synthesis/equivalence.ys"
    script.write_text(f"""read_verilog -sv {quoted(core)}
proc
opt
rename linear_engine gold
read_verilog {quoted(netlist)}
proc
opt
rename linear_engine gate
equiv_make gold gate equiv
hierarchy -top equiv
async2sync
equiv_simple -seq 2
equiv_induct -seq 4
equiv_status -assert
""",encoding="utf-8")
    try:
        text,metadata=run([executable("yosys"),"-s",script],"core_equivalence",timeout=180)
    except subprocess.CalledProcessError:
        metadata=json.loads((WORK/"logs/core_equivalence.json").read_text())
        write_json(REPORTS/"synthesis/equivalence.json",{"status":"UNVERIFIED","evidence_class":"ALTERNATIVE_VALIDATION",
            "reason":"Bounded SAT proof did not complete; this is not a proof of mismatch or equivalence.",
            "rtl_sha256":sha256(core),"netlist_sha256":sha256(netlist),"attempt":metadata})
        raise
    if "Equivalence successfully proven" not in text:
        raise RuntimeError("Equivalence proof completion marker missing")
    write_json(REPORTS/"synthesis/equivalence.json",{"status":"PASS","evidence_class":"ALTERNATIVE_VALIDATION",
        "rtl_sha256":sha256(core),"netlist_sha256":sha256(netlist),"proof":metadata,
        "scope":"Clocked core transition equivalence after common async2sync normalization; separate simulation covers asynchronous reset abort.",
        "official_netlist_equivalence":"NOT_VERIFIED"})


if __name__=="__main__":
    main()
