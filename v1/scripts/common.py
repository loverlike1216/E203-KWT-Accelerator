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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tool_env():
    env = os.environ.copy()
    suite = ROOT / "toolchains/oss-cad-suite"
    dirs = [suite / "bin", suite / "lib"]
    env["PATH"] = os.pathsep.join(str(p) for p in dirs if p.exists()) + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
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
    result = subprocess.run(list(map(str, args)), cwd=cwd, env=tool_env(),
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=timeout)
    log = directory / f"{name}.log"
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    metadata = {"command": list(map(str, args)), "cwd": str(cwd), "started_at": stamp,
                "returncode": result.returncode, "elapsed_seconds": time.monotonic() - start,
                "log": str(log.relative_to(ROOT)), "log_sha256": sha256(log)}
    write_json(directory / f"{name}.json", metadata)
    print((result.stdout + result.stderr)[-4000:], flush=True)
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, args)
    return result.stdout + result.stderr, metadata
