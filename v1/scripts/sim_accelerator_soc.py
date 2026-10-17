import argparse
import json
import os
import re
import shutil
from common import ROOT, WORK, REPORTS, executable, run, sha256, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layers", default="1", help="Comma-separated actual layer task IDs")
    args = parser.parse_args()
    layers = [int(n) for n in args.layers.split(",")]
    if any(n<1 or n>12 for n in layers):
        raise ValueError("Layer IDs must be 1..12")
    output = WORK / "accelerator_soc"
    output.mkdir(parents=True, exist_ok=True)
    prefix = ROOT / "toolchains/xpack-riscv-none-elf-gcc-15.2.0-1/bin/riscv-none-elf-"
    linux_prefix=os.environ.get("KWT_RISCV_PREFIX") or ("riscv-none-elf-" if shutil.which("riscv-none-elf-gcc") else "riscv64-unknown-elf-")
    gcc = str(prefix)+"gcc.exe" if os.name=="nt" else executable(linux_prefix+"gcc")
    objcopy = str(prefix)+"objcopy.exe" if os.name=="nt" else executable(linux_prefix+"objcopy")
    objdump = str(prefix)+"objdump.exe" if os.name=="nt" else executable(linux_prefix+"objdump")
    fw = ROOT / "v1/firmware"
    elf, binary = output / "driver.elf", output / "driver.bin"
    _, build = run([gcc,"-march=rv32imac_zicsr","-mabi=ilp32","-mno-relax","-msmall-data-limit=0",
        "-mstrict-align","-ffreestanding","-fno-builtin","-nostdlib","-Os","-Wall","-Wextra","-Werror",
        "-Wl,-T,"+str(fw/"link.ld"),"-Wl,-Map,"+str(output/"driver.map"),
        fw/"start.S",fw/"driver.c",fw/"main.c","-o",elf],"firmware_build")
    run([objcopy,"-O","binary",elf,binary],"firmware_binary")
    disassembly,_ = run([objdump,"-d",elf],"firmware_disassembly")
    (output/"driver.dump").write_text(disassembly,encoding="utf-8")
    content = binary.read_bytes()
    if len(content)>65536:
        raise RuntimeError("Firmware overflows reference ITCM")
    hexfile=output/"driver.hex"
    hexfile.write_text("\n".join(f"{v:02x}" for v in content+bytes(65536-len(content)))+"\n",encoding="ascii")
    source = ROOT/"external/src/e203_hbirdv2/rtl/e203"
    files=sorted(source.glob("*/*.v"))+sorted(source.glob("*/*/*.v"))
    files += [ROOT/"v1/rtl"/n for n in ("linear_engine.sv","sram16_reference.sv","linear_mmio.sv","reference_soc.sv")]
    image=output/"soc.vvp"
    _,compile_info=run([executable("iverilog"),"-g2012","-DDISABLE_SV_ASSERTION=1","-s","tb_accelerator_soc",
        "-I",source/"core","-I",source/"perips","-I",source/"perips/apb_i2c","-o",image,
        *files,ROOT/"v1/tb/tb_accelerator_soc.sv"],"accelerator_soc_compile")
    tests=[]
    for layer in layers:
        task = WORK/f"vectors/layer{layer:02}"
        text,metadata=run([executable("vvp"),image,f"+FIRMWARE={hexfile.as_posix()}",f"+TASK={task.as_posix()}"],
            f"accelerator_soc_layer{layer:02}",cwd=output,timeout=1200)
        pattern=r"SOC_PASS outputs=(\d+) issued=(\d+) shared_reads=(\d+) accelerator_writes=(\d+) result_words=(\d+) macs=(\d+) task_cycles=(\d+) total_cycles=(\d+) checksum=([0-9a-f]+)"
        match=re.search(pattern,text)
        if not match:
            raise RuntimeError("No successful actual E203/hardware completion marker")
        fields=("outputs","instructions_issued","shared_reads","accelerator_writes","result_words","macs","cpu_load_to_writeback_cycles","total_cycles")
        tests.append({"layer":layer,"status":"PASS",**dict(zip(fields,map(int,match.groups()[:-1]))),
            "checksum":match[9],"input_hashes":{p.name:sha256(p) for p in task.glob("*.hex")},**metadata})
        write_json(REPORTS/f"soc/layers/layer{layer:02}.json",tests[-1])
        previous=REPORTS/"soc/accelerator_soc.json"
        combined={t["layer"]:t for t in json.loads(previous.read_text()).get("tests",[])} if previous.exists() else {}
        combined.update({t["layer"]:t for t in tests})
        all_tests=sorted(combined.values(),key=lambda t:t["layer"])
        # Save completed tasks immediately so an interrupted multi-task run is recoverable.
        write_json(REPORTS/"soc/accelerator_soc.json",{"status":"PASS","evidence_class":"ALTERNATIVE_VALIDATION",
            "official_platform":False,"source_commit":"9f3e34f337f5d0a1236a285871ffa2032491617a",
            "firmware_elf_sha256":sha256(elf),"firmware_hex_sha256":sha256(hexfile),"firmware_build":build,
            "compile":compile_info,"tests":all_tests,"tested_layer_count":len(all_tests),"requested_layers":layers,
            "run_complete":all(layer in combined for layer in layers),
            "limitations":["Reference CPU/TCM/bus wrapper, not official SoC.",
                "CPU copy-to-engine timing is measured; initial testbench preload into shared SRAM is not timed. This is not official Q13 throughput.",
                "No official SRAM area/power/timing model.","No official 150 MHz STA or area/power claim."]})


if __name__=="__main__":
    main()
