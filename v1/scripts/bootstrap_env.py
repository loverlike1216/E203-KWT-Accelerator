"""Install only workspace-local dependencies; support a later Linux server."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request
from common import ROOT, sha256, write_json

OSS_URL = "https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-10-17/oss-cad-suite-windows-x64-20261017.tgz"
OSS_SHA = "842e7890bbfd1b7527f256ba6ff52666392f9707339f1189829849de9ef77dbf"
SOURCES = {
    "keyword-transformer": ("https://github.com/ARM-software/keyword-transformer.git", "237e4097"),
    "e203_hbirdv2": ("https://github.com/riscv-mcu/e203_hbirdv2.git", "9f3e34f337f5d0a1236a285871ffa2032491617a"),
}


def command(args):
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools-only", action="store_true")
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    records = []
    if not args.tools_only:
        for name, (url, revision) in SOURCES.items():
            target = ROOT / "external/src" / name
            if not target.exists():
                command(["git", "clone", "--no-checkout", url, target])
                command(["git", "-C", target, "checkout", "--detach", revision])
            head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
            expected = subprocess.check_output(["git", "-C", str(target), "rev-parse", revision], text=True).strip()
            if head != expected:
                raise RuntimeError(f"Refusing to change existing {target}: {head} != {expected}")
            dirty = subprocess.check_output(["git", "-C", str(target), "status", "--porcelain"], text=True)
            if dirty:
                raise RuntimeError(f"Pinned dependency is dirty: {target}")
            license_files = list(target.glob("LICENSE*"))
            records.append({"name": name, "url": url, "commit": head,
                            "license_files": {p.name: sha256(p) for p in license_files},
                            "is_official_platform": False, "status": "DOWNLOADED_VERIFIED"})
        if not args.sources_only:
            if sys.version_info[:2] != (3, 10):
                raise RuntimeError("Local model profile requires Python 3.10. Official profile must be revalidated separately.")
            venv = ROOT / "envs/model"
            py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            if not py.exists():
                command([sys.executable, "-m", "venv", venv])
            lock = ROOT / "v1/requirements.local.lock.txt"
            requirements = lock if lock.exists() else ROOT / "v1/requirements.local.txt"
            command([py, "-m", "pip", "install", "-r", requirements])
    if not args.sources_only and os.name == "nt":
        archive = ROOT / "external/cache/oss-cad-suite-windows-x64-20261017.tgz"
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.exists():
            partial = archive.with_suffix(".partial")
            urllib.request.urlretrieve(OSS_URL, partial)
            partial.rename(archive)
        if sha256(archive) != OSS_SHA:
            raise RuntimeError("OSS CAD suite upstream SHA256 mismatch")
        destination = ROOT / "toolchains"
        if not (destination / "oss-cad-suite/bin/iverilog.exe").exists():
            with tarfile.open(archive) as tar:
                for member in tar.getmembers():
                    resolved = (destination / member.name).resolve()
                    if not resolved.is_relative_to(destination.resolve()) or member.issym() or member.islnk():
                        raise RuntimeError(f"Unsafe archive member: {member.name}")
                tar.extractall(destination)
        records.append({"name": "oss-cad-suite", "version": "2026-10-17", "url": OSS_URL,
                        "sha256": OSS_SHA, "status": "DOWNLOADED_VERIFIED"})
    write_json(ROOT / "v1/reports/environment/bootstrap.json", {"sources": records})


if __name__ == "__main__":
    main()
