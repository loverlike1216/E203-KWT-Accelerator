# Context Checkpoint CP-20261017-200742__v1

Project: E203-KWT-Accelerator. Repository: https://github.com/loverlike1216/E203-KWT-Accelerator.git
Workspace: E:\Codex_project\E203-KWT-Accelerator. Branch: main. Version: v1 / ACTIVE.
Generation base commit: dd393cbcafc07d38dc4a04cf6e8ee3982f1fe59c. Stage: Stage 3 — reference E203 integration.
Reason: Twelve full matrix RTL tasks and mapped core boundary tests passed. Created: 2026-10-17T20:07:42.549371+00:00.

## Goal and architecture
Portable local implementation of the undergraduate FFN linear task; official
platform binding and PPA remain pending. Read shared/EXECUTION_CONTRACT.md.

## Verified evidence
- v1/reports/environment/environment.json: PASS / ALTERNATIVE_VALIDATION / SHA256 bd048d88b352c4128abed41a16d9241653b874e7329c0ce6e0d61ef7ff036561
- v1/reports/soc/reference_baseline.json: PASS / ALTERNATIVE_VALIDATION / SHA256 30b27c9d024c6cd8829037a561d5801da3b30d0b7c6b2bf1f8e625b9ae996a32
- v1/reports/model/checkpoint_inventory.json: PASS / ALTERNATIVE_VALIDATION / SHA256 32932c0ef51b07f37f289514bf0621211c030d19458fd004827a2ca91c189b20
- v1/reports/model/quantization.json: PASS / ALTERNATIVE_VALIDATION / SHA256 2e4144e70277e33d5276660a3df128c7acd93cce172daa0b2f8d264b658c5e5a
- v1/reports/rtl/engine.json: PASS / ALTERNATIVE_VALIDATION / SHA256 ea31a4a7e3f92adeda24fd862e6164afdb5f1f71472d92bf0c8982a04e372773
- v1/reports/synthesis/reference.json: PASS / ALTERNATIVE_VALIDATION / SHA256 02d28f77d5754c924992a20c8530f56936e43c3189988ca3633161f6540906d1

## Current plan and next action
Complete genuine E203 C driver simulation, then clean replay and official migration handoff

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
