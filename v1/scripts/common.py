"""Portable paths and auditable command execution, no shell interpolation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work"
REPORTS = ROOT / "v1/reports"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def tool_env():
    env = os.environ.copy()
    suite = ROOT / "toolchains/oss-cad-suite"
    dirs = [suite / "bin", suite / "lib"]
    env["PATH"] = os.pathsep.join(str(p) for p in dirs if p.exists()) + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    scratch = WORK / "tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    for name in ("TMP", "TEMP", "TMPDIR"):
        env[name] = str(scratch)
    return env


def executable(name):
    result = shutil.which(name, path=tool_env()["PATH"])
    if not result:
        raise RuntimeError(f"Required tool not found: {name}. Run bootstrap or configure PATH.")
    return result


def run(args, name, cwd=ROOT, timeout=300):
    """Store the real return code and output; failures always propagate."""
    directory = WORK / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    display = " ".join(map(str, args))
    print("RUN", display if len(display) < 600 else display[:550] + f" ... ({len(args)} arguments; full command in metadata)", flush=True)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + f"-{os.getpid()}"
    log = directory / f"{name}-{run_id}.log"
    # Stream directly to a local log so a long simulator is observable mid-run.
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(list(map(str,args)),cwd=cwd,env=tool_env(),stdout=stream,stderr=subprocess.STDOUT)
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            stream.write(f"\nTIMEOUT after {timeout}s\n")
            returncode = 124
    output = log.read_text(encoding="utf-8",errors="replace")
    metadata = {"command": list(map(str, args)), "cwd": str(cwd), "started_at": stamp,
                "returncode": returncode, "elapsed_seconds": time.monotonic() - start,
                "log": str(log.relative_to(ROOT)), "log_sha256": sha256(log)}
    write_json(directory / f"{name}-{run_id}.json", metadata)
    write_json(directory / f"{name}.json", metadata)  # latest pointer; history remains immutable
    print(output[-4000:], flush=True)
    if returncode:
        raise subprocess.CalledProcessError(returncode, args)
    return output, metadata
