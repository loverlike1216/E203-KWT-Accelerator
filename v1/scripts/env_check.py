import json
import os
import platform
import subprocess
import sys
from common import ROOT, REPORTS, executable, run, sha256, write_json


def main():
    import tensorflow as tf
    import numpy as np
    import yaml
    config = yaml.safe_load((ROOT / "bootstrap/PROJECT_INPUTS.yaml").read_text(encoding="utf-8"))
    remote = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True).strip()
    if remote != config["repository_url"]:
        raise RuntimeError("Configured repository does not match origin")
    if not all(config[k] for k in ("repository_created_manually_by_user", "user_explicitly_approves_project_start")):
        raise RuntimeError("Start gate not approved")
    versions = {}
    for tool, args in (("iverilog", ["-V"]), ("yosys", ["-V"]), ("git", ["--version"])):
        text, metadata = run([executable(tool), *args], f"version_{tool}")
        versions[tool] = {"version": text.splitlines()[0], "executable_sha256": sha256(executable(tool)), **metadata}
    compiler = ROOT / "toolchains/xpack-riscv-none-elf-gcc-15.2.0-1/bin/riscv-none-elf-gcc.exe"
    if os.name != "nt":
        try:
            compiler = executable("riscv-none-elf-gcc")
        except RuntimeError:
            compiler = executable("riscv64-unknown-elf-gcc")
    if compiler.exists() if hasattr(compiler, "exists") else bool(compiler):
        text, metadata = run([compiler, "--version"], "version_riscv_gcc")
        versions["riscv_gcc"] = {"version": text.splitlines()[0], **metadata}
    else:
        raise RuntimeError("RISC-V compiler installation not complete")
    write_json(REPORTS / "environment/environment.json", {
        "status": "PASS", "profile": "local_reference", "evidence_class": "ALTERNATIVE_VALIDATION",
        "project_id": config["project_id"], "repository": remote, "workspace": str(ROOT),
        "python": sys.version, "platform": platform.platform(), "tensorflow": tf.__version__,
        "numpy": np.__version__, "tools": versions, "official_server": "NOT_PROVIDED",
        "official_pdk": "NOT_PROVIDED", "official_power_flow": "NOT_PROVIDED"})


if __name__ == "__main__":
    main()
