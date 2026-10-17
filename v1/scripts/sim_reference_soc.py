"""Run unmodified public E203 SoC with its included ISA firmware images."""
import re
from common import ROOT, WORK, REPORTS, executable, run, sha256, write_json


def main():
    source = ROOT / "external/src/e203_hbirdv2"
    rtl = source / "rtl/e203"
    output = WORK / "reference_soc"
    output.mkdir(parents=True, exist_ok=True)
    files = [ROOT/"v1/tb/simulation_timescale.v"] + sorted(rtl.glob("*/*.v")) + sorted(rtl.glob("*/*/*.v")) + sorted((source / "tb").glob("*.v"))
    image = output / "soc.vvp"
    _, compile_info = run([executable("iverilog"), "-g2005-sv", "-Diverilog",
        "-DDISABLE_SV_ASSERTION=1", "-s", "tb_top", "-I", rtl / "core",
        "-I", rtl / "perips", "-I", rtl / "perips/apb_i2c", "-o", image, *files], "reference_soc_compile")
    tests = []
    for name in ("rv32ui-p-add", "rv32ui-p-lw", "rv32um-p-mul"):
        firmware = source / "riscv-tools/riscv-tests/isa/generated" / name
        text, info = run([executable("vvp"), image, "+DUMPWAVE=0", f"+TESTCASE={firmware.as_posix()}"], name, cwd=output, timeout=180)
        if "TEST_PASS" not in text or "TEST_FAIL" in text or "Time Out" in text:
            raise RuntimeError(f"E203 reference test did not pass: {name}")
        tests.append({"test": name, "status": "PASS", "firmware_sha256": sha256(firmware.with_suffix(".verilog")),
                      "cycles": int(re.search(r"Total cycle_count value:\s*(\d+)", text)[1]), **info})
    write_json(REPORTS / "soc/reference_baseline.json", {
        "status": "PASS", "evidence_class": "ALTERNATIVE_VALIDATION",
        "source_commit": "9f3e34f337f5d0a1236a285871ffa2032491617a",
        "official_platform": False, "unmodified_upstream": True,
        "compile": compile_info, "tests": tests,
        "limitations": ["Upstream testbench clock and TCM configuration are not official competition parameters.",
                        "ISA baseline is not accelerator SoC integration acceptance."]})


if __name__ == "__main__":
    main()
