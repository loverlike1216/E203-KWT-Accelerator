"""Persist reconciled local state; report only evidence files that actually exist."""
import argparse
import datetime
import json
import subprocess
from common import ROOT, REPORTS, sha256, write_json


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--next-action", required=True)
    args = parser.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc)
    identifier = "CP-" + now.strftime("%Y%m%d-%H%M%S") + "__v1"
    branch, head = git("branch", "--show-current"), git("rev-parse", "HEAD")
    remote = git("remote", "get-url", "origin")
    if remote != "https://github.com/loverlike1216/E203-KWT-Accelerator.git":
        raise RuntimeError("Repository identity mismatch")
    version = json.loads((ROOT / "shared/VERSION_STATE.json").read_text())
    assert version["active_version"] == "v1" and not version["upgrade_pending"]
    evidence = []
    for relative in ("environment/environment.json", "soc/reference_baseline.json",
                     "model/checkpoint_inventory.json", "model/quantization.json",
                     "rtl/engine.json", "soc/accelerator_soc.json", "synthesis/reference.json"):
        path = REPORTS / relative
        if path.exists():
            item = json.loads(path.read_text(encoding="utf-8"))
            evidence.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(path), "status": item.get("status", "UNKNOWN"),
                "evidence_class": item.get("evidence_class", "NOT_VERIFIED")})
    state = {"project_id": "E203-KWT-Accelerator", "project_name": "E203-KWT-Accelerator",
        "repository": remote, "workspace_path": str(ROOT), "branch": branch,
        "active_version": "v1", "current_stage": args.stage, "status": "PROJECT_ACTIVE",
        "latest_context_checkpoint": identifier, "checkpoint_commit": None,
        "checkpoint_base_commit": head, "checkpoint_status": "VALID_LOCAL_REFERENCE",
        "chat_source_name": "UNKNOWN", "open_ai_problems": [],
        "blocking_issues": ["OFFICIAL_PLATFORM_PENDING", "OFFICIAL_MACROS_PENDING", "OFFICIAL_ASIC_FLOW_PENDING"],
        "critical_issues": [], "next_action": args.next_action,
        "environment_profile": "local_reference", "formal_acceptance": "NOT_VERIFIED"}
    checkpoint = {**state, "checkpoint_id": identifier, "base_commit": head, "head_commit": head,
        "version_status": "ACTIVE", "created_at": now.isoformat(), "created_by": "Codex",
        "checkpoint_reason": args.reason, "source_of_truth": "repository",
        "architecture_ref": "shared/EXECUTION_CONTRACT.md", "latest_validation": evidence,
        "completed": [e["path"] for e in evidence if e["status"] == "PASS"],
        "next_actions": [args.next_action], "active_decisions": ["D-20261017-001", "D-20261017-003", "D-20261017-004"],
        "known_limitations": ["Local reference results do not close official gates", "TF 2.10.1 differs from upstream 2.4.0rc1", "Official 600 samples not evaluated"],
        "do_not_change": ["v1", "repository", "pretrained weights", "acceptance thresholds", "original inputs"],
        "invariants": ["99x64 @ 64x256 + bias", "12 parameter sets", "training-only calibration", "no software substitution"],
        "evidence_refs": [e["path"] for e in evidence], "resume_from": "shared/CURRENT_PLAN.md",
        "repository_status_at_reconciliation": git("status", "--short"),
        "commit_note": "HEAD is the generation base, not a claim that pending files are committed. Find the checkpoint publication commit with git log -- shared/CONTEXT_CHECKPOINT.md."}
    write_json(ROOT / "shared/PROJECT_STATE.json", state)
    write_json(ROOT / "shared/CONTEXT_CHECKPOINT.json", checkpoint)
    text = f"""# Context Checkpoint {identifier}

Project: E203-KWT-Accelerator. Repository: {remote}
Workspace: {ROOT}. Branch: {branch}. Version: v1 / ACTIVE.
Generation base commit: {head}. Stage: {args.stage}.
Reason: {args.reason}. Created: {now.isoformat()}.

## Goal and architecture
Portable local implementation of the undergraduate FFN linear task; official
platform binding and PPA remain pending. Read shared/EXECUTION_CONTRACT.md.

## Verified evidence
""" + "\n".join(f"- {e['path']}: {e['status']} / {e['evidence_class']} / SHA256 {e['sha256']}" for e in evidence) + f"""

## Current plan and next action
{args.next_action}

## Decisions, blockers and limits
Read shared/DECISIONS.md, BLOCKERS.md and ACCEPTANCE.md. Only user decisions are
recorded as user decisions. No imported ChatGPT decision exists. External history
access is BLOCKED. Official platform, macros and ASIC flow have not been supplied.
No local result is official timing, area or power acceptance. No official 600-sample
claim is made. No architecture or version upgrade is implied by this checkpoint.

## Do Not Change and invariants
Preserve v1, repository, source weights, acceptance thresholds and original inputs.
99x64 @ 64x256 + bias, twelve layers, training-only calibration, actual hardware MAC.
Keep restricted inputs and credentials out of Git.

## Open AI problems
None currently recorded; independent implementation continues within user scope.

## Repository delta and provenance
This snapshot is derived from live Git identity/status, VERSION_STATE, source
configuration, formal user decisions and the evidence files listed above. HEAD is
the generation base. Pending modifications are recorded in the JSON companion;
resolve the containing publication commit with git log on this checkpoint path.
No previous stage is declared complete merely because this checkpoint exists.

## Resume instruction
Read AGENTS.md, PROJECT_STATE, VERSION_STATE, this checkpoint, CURRENT_PLAN,
DECISIONS, BLOCKERS, ACCEPTANCE and the latest reports. Reconcile git status/log
and source hashes, then continue the next action in the same v1.
"""
    (ROOT / "shared/CONTEXT_CHECKPOINT.md").write_text(text, encoding="utf-8")
    (ROOT / "shared/PROJECT_STATE.md").write_text(f"# Project state\n\n{args.stage}\n\nNext: {args.next_action}\n\nCanonical machine state: PROJECT_STATE.json.\n", encoding="utf-8")
    archive = ROOT / "shared/context-checkpoints" / (identifier + ".md")
    if archive.exists():
        raise RuntimeError("Checkpoint IDs must not overwrite historical snapshots")
    archive.write_text(text, encoding="utf-8")
    print(identifier)


if __name__ == "__main__":
    main()
