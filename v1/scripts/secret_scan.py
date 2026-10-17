"""Check staged public content, without displaying any matched secret value."""
import json
import re
import subprocess
from pathlib import PurePosixPath
from common import ROOT, REPORTS, write_json


def main():
    names = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=ROOT).decode().split("\0")
    findings = []
    scanned = []
    patterns = (rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b", rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b",
                rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----", rb"(?i)authorization:\s*bearer\s+\S{12,}",
                rb"https?://[^\s/@:]+:[^\s/@]+@")
    for name in filter(None, names):
        suffix = PurePosixPath(name).suffix.lower()
        if suffix in (".pdf", ".lib", ".lef", ".lic", ".pem", ".key", ".wav", ".npz", ".vcd", ".saif") or name.startswith(("envs/", "toolchains/", "work/", "external/src/", "inputs/official/")) and name != "inputs/official/README.md":
            findings.append({"file": name, "reason": "Restricted input or generated payload staged"})
            continue
        result = subprocess.run(["git", "show", ":" + name], cwd=ROOT, capture_output=True)
        if result.returncode:
            continue  # A staged deletion has no secret-bearing new blob.
        if any(re.search(pattern, result.stdout) for pattern in patterns):
            findings.append({"file": name, "reason": "Credential pattern detected; value not printed"})
        scanned.append(name)
    write_json(REPORTS / "environment/interaction_secret_scan.json", {"status": "FAIL" if findings else "PASS",
        "scope": "staged blobs at scan time", "scanned_files": len(scanned), "findings": findings})
    print(json.dumps({"scanned_files": len(scanned), "findings": findings}))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
