# E203-KWT-Accelerator engineering rules

Read bootstrap/PROJECT_INPUTS.yaml, bootstrap/02_CODEX_总指令.md and
bootstrap/04_验收与质量门禁.md before substantive work. Restore state from
shared/PROJECT_STATE.json, VERSION_STATE.json, CONTEXT_CHECKPOINT.md, CURRENT_PLAN.md,
DECISIONS.md, BLOCKERS.md and ACCEPTANCE.md; reconcile Git and evidence.

- Project ID E203-KWT-Accelerator; official project repository is
  https://github.com/loverlike1216/E203-KWT-Accelerator.git.
- Only v1 is authorized. Continue means continue v1, never create a new version.
- User authorized a local substitute environment on 2026-10-17 pending the official
  server. Mark reference platform and local tools ALTERNATIVE_VALIDATION.
- Official acceptance requires actual official platform, SRAM macros, libraries,
  constraints, synthesis and power flow. Never substitute a reference PASS.
- Preserve pretrained weights, model dimensions, existing user files, failed
  evidence and remote commits. Do not force push or rewrite history.
- Never publish official inputs, PDK, license files, credentials, speech samples
  or unrestricted conversation transcripts. Scan before commits and pushes.
- No costs, global installs, telemetry or startup changes are authorized.
- Numeric contract before RTL. Mandatory MAC must run in hardware. Validate all
  25,344 outputs, 12 layer changes, reset, boundaries and backpressure.
- Training-only calibration; separate validation; no test-set tuning.
- Record actual commands, codes, versions, hashes and limitations. Update shared
  state and checkpoints at milestones. Commit/push authorized project text only.
- No invented ChatGPT transcript or decision. Chat access must be checked;
  inaccessible history is BLOCKED, never reconstructed as verbatim history.
- Ordinary bugs: diagnose/fix/regress autonomously. After 2-3 unsuccessful similar
  attempts, collect evidence and perform root cause analysis before further edits.

Default Windows shell is pwsh. Portable scripts should also run on Linux and
accept official locations through configuration rather than hard-coded host paths.
