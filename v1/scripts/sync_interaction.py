"""Export observable user/assistant messages only, never private reasoning."""
import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path
from common import ROOT


def redact(text):
    patterns = (r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b",
                r"(?i)(authorization:\s*bearer\s+)\S+", r"(?i)(password\s*[:=]\s*)[^\s\"']{8,}")
    for pattern in patterns:
        text = re.sub(pattern, "[REDACTED_SECRET]", text)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-log", required=True)
    parser.add_argument("--session-id", required=True)
    args = parser.parse_args()
    messages = []
    for line in Path(args.source_log).read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        p = record.get("payload", {})
        if record.get("type") != "response_item" or p.get("type") != "message":
            continue
        role = p.get("role")
        if role not in ("user", "assistant"):
            continue
        if role == "assistant" and p.get("channel") not in ("commentary", "final"):
            continue
        content = "\n".join(c.get("text", "") for c in p.get("content", []) if c.get("type") in ("input_text", "output_text"))
        if not content:
            continue
        messages.append({"role": role, "timestamp": record.get("timestamp", "UNKNOWN"), "text": redact(content)})
    payload_hash = hashlib.sha256(json.dumps(messages, ensure_ascii=False).encode()).hexdigest()
    target = ROOT / "AI-interaction-memory/codex" / (args.session_id + ".md")
    header = f"""---
project_id: E203-KWT-Accelerator
source: codex
thread_id: {args.session_id}
active_version: v1
sync_status: PARTIAL
message_count: {len(messages)}
content_hash: {payload_hash}
last_updated_at: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
---

# Observable Codex conversation

Snapshot through the export time. Only actual user and user-facing assistant
messages are included. Platform-supplied user context may be present in its original
observable envelope. Hidden reasoning, system/developer messages and raw tool
payloads are excluded. Tool evidence has separate reports. Future messages and
inaccessible other sessions are not claimed complete. Secrets are redacted.

"""
    target.write_text(header + "\n\n".join(f"## Message {i+1:04}\nRole: {m['role']}\nTime: {m['timestamp']}\nMessage ID: UNKNOWN\n\n{m['text']}" for i,m in enumerate(messages)), encoding="utf-8")
    (ROOT / "AI-interaction-memory/INDEX.md").write_text(f"""# AI interaction index

| ID | Source | Type | Version | Record | Status | Impact |
|---|---|---|---|---|---|---|
| {args.session_id} | Codex | Human-AI | v1 | codex/{args.session_id}.md | PARTIAL | IMPLEMENTATION_INPUT |
| CHAT-UNKNOWN | ChatGPT | External history | v1 | ../AI-chat-memory/INDEX.md | BLOCKED | INFORMATION_ONLY |
| T-20261017-001 | CLI / model / EDA | Tool flow | v1 | tool-flow/T-20261017-001__local-reference.md | PARTIAL | VALIDATION_INPUT |

Codex provider: OpenAI. No other AI agent was used. No cross-agent decision is
claimed. Observable tool evidence is recorded by v1/scripts/common.py and reports.
Current conversation content SHA256: {payload_hash}.
""", encoding="utf-8")


if __name__ == "__main__":
    main()
