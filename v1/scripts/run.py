"""One portable entry point. Missing official tools never return success."""
import argparse
import json
import subprocess
import sys
from common import ROOT, WORK, REPORTS, run, write_json

COMMANDS={
    "env-check":"env_check.py", "model-check":"model_check.py",
    "dataset-check":"prepare_dataset.py", "quant-check":"quant_check.py",
    "sim-reference-soc":"sim_reference_soc.py", "sim-engine":"sim_engine.py",
    "sim-soc":"sim_accelerator_soc.py", "synth-reference":"synth_reference.py",
    "equiv-reference":"equiv_reference.py"
}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("target",choices=list(COMMANDS)+["regress","synth","sta","power","benchmark","package"])
    parser.add_argument("--layers",default="1")
    parser.add_argument("--jobs",type=int,default=1)
    parser.add_argument("--config",default="v1/config/local_reference.json")
    args=parser.parse_args()
    profile=json.loads((ROOT/args.config).read_text())
    if profile.get("profile")=="official" and args.target in list(COMMANDS)+["regress"]:
        command=profile.get("commands",{}).get(args.target)
        missing=[name for name in ("e203_source","official_sram") if not profile.get(name)]
        if missing or not isinstance(command,list) or not command:
            print(json.dumps({"status":"BLOCKED","target":args.target,"missing":missing,
                "reason":"Official profile requires a real official execution command; public reference fallback is prohibited."}))
            raise SystemExit(2)
        for name in ("e203_source","official_sram"):
            if not (ROOT/profile[name]).exists(): raise FileNotFoundError(name)
        _,metadata=run(command,"official_"+args.target,timeout=7200)
        write_json(REPORTS/"official"/(args.target+"_execution.json"),{"status":"RAN_NEEDS_REPORT_REVIEW",**metadata})
        return
    if args.target in COMMANDS:
        command=[sys.executable,ROOT/"v1/scripts"/COMMANDS[args.target]]
        if args.target=="sim-soc": command += ["--layers",args.layers,"--jobs",str(args.jobs)]
        run(command,"target_"+args.target,timeout=7200)
    elif args.target=="regress":
        # Every command does real work; first failure stops the chain.
        for target in ("env-check","model-check","dataset-check","quant-check","sim-reference-soc","sim-engine","synth-reference","sim-soc"):
            command=[sys.executable,__file__,target,"--config",args.config]
            if target=="sim-soc": command += ["--layers",args.layers,"--jobs",str(args.jobs)]
            subprocess.run(command,cwd=ROOT,check=True)
    elif args.target=="package":
        import zipfile
        files=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
        output=WORK/"delivery/E203-KWT-Accelerator-v1-source.zip"
        output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
            for name in filter(None,files):
                if name.startswith(("inputs/official/","AI-interaction-memory/codex/")):
                    continue
                archive.write(ROOT/name,name)
        print(output)
    else:
        config=json.loads((ROOT/args.config).read_text())
        required=("official_pdk","official_sram","official_constraints","e203_source")
        missing=[name for name in required if not config.get(name)]
        command=config.get("commands",{}).get(args.target)
        if config.get("profile")!="official" or missing or not isinstance(command,list) or not command:
            print(json.dumps({"status":"BLOCKED","target":args.target,"missing":missing,
                "reason":"Official source, macro, library/constraints and actual tool command must be supplied."}))
            raise SystemExit(2)
        for name in required:
            location=ROOT/config[name]
            if not location.exists(): raise FileNotFoundError(f"Official input does not exist: {name}")
        _,metadata=run(command,"official_"+args.target,timeout=7200)
        write_json(REPORTS/"official"/(args.target+"_execution.json"),{"status":"RAN_NEEDS_REPORT_REVIEW",**metadata})


if __name__=="__main__":
    main()
