# Context Checkpoint CP-20261017-200135__v1

Project: E203-KWT-Accelerator. Repository: https://github.com/loverlike1216/E203-KWT-Accelerator.git
Workspace: E:\Codex_project\E203-KWT-Accelerator. Branch: main. Version: v1 / ACTIVE.
Generation base commit: d98afae8e6c1f018eb7ba7e51ad3c53e88825ea9. Stage: Stage 2 — portable RTL baseline.
Reason: Training-only calibration and real speech validation passed; signed16/acc48 contract locked. Created: 2026-10-17T20:01:35.868021+00:00.

## Goal and architecture
Portable local implementation of the undergraduate FFN linear task; official
platform binding and PPA remain pending. Read shared/EXECUTION_CONTRACT.md.

## Verified evidence
- v1/reports/environment/environment.json: PASS / ALTERNATIVE_VALIDATION / SHA256 bd048d88b352c4128abed41a16d9241653b874e7329c0ce6e0d61ef7ff036561
- v1/reports/soc/reference_baseline.json: PASS / ALTERNATIVE_VALIDATION / SHA256 30b27c9d024c6cd8829037a561d5801da3b30d0b7c6b2bf1f8e625b9ae996a32
- v1/reports/model/checkpoint_inventory.json: PASS / ALTERNATIVE_VALIDATION / SHA256 32932c0ef51b07f37f289514bf0621211c030d19458fd004827a2ca91c189b20
- v1/reports/model/quantization.json: PASS / ALTERNATIVE_VALIDATION / SHA256 2e4144e70277e33d5276660a3df128c7acd93cce172daa0b2f8d264b658c5e5a

## Current plan and next action
Implement four-lane matrix core and synchronous memory wrappers, then test twelve actual layer tasks

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
