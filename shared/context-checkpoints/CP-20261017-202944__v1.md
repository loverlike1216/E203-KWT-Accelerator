# Context Checkpoint CP-20261017-202944__v1

Project: E203-KWT-Accelerator. Repository: https://github.com/loverlike1216/E203-KWT-Accelerator.git
Workspace: E:\Codex_project\E203-KWT-Accelerator. Branch: main. Version: v1 / ACTIVE.
Generation base commit: 1c18221e0222a82e51fca907a2d4670e849e8839. Stage: Local reference baseline verified — official migration pending.
Reason: Real E203 CPU/hardware/readback tasks and clean local replay passed; portable baseline ready for migration. Created: 2026-10-17T20:29:44.674200+00:00.

## Goal and architecture
Portable local implementation of the undergraduate FFN linear task; official
platform binding and PPA remain pending. Read shared/EXECUTION_CONTRACT.md.

## Verified evidence
- v1/reports/environment/environment.json: PASS / ALTERNATIVE_VALIDATION / SHA256 47347e3bf61c17a1e288c881c858f361076f5e3861838ec29f2fee40b52df987
- v1/reports/soc/reference_baseline.json: PASS / ALTERNATIVE_VALIDATION / SHA256 5a05c4b2eb90c9c5d1b536a040c168fc2ef655aa062c013aff5b010b9827ab3c
- v1/reports/model/checkpoint_inventory.json: PASS / ALTERNATIVE_VALIDATION / SHA256 32932c0ef51b07f37f289514bf0621211c030d19458fd004827a2ca91c189b20
- v1/reports/model/quantization.json: PASS / ALTERNATIVE_VALIDATION / SHA256 5157935132d72c63d6dff189aaea9de0ee3bd152ba2320907d60edfb804f9910
- v1/reports/rtl/engine.json: PASS / ALTERNATIVE_VALIDATION / SHA256 ea31a4a7e3f92adeda24fd862e6164afdb5f1f71472d92bf0c8982a04e372773
- v1/reports/soc/accelerator_soc.json: PASS / ALTERNATIVE_VALIDATION / SHA256 bd72d91f000d1d1fa0f420cece77f09b40e64956b1e9473c46158b10ae51d5cb
- v1/reports/synthesis/reference.json: PASS / ALTERNATIVE_VALIDATION / SHA256 76146fd38d424f2f21d211eb6ff26e2515c3325c9023bddb06c9b4120cb85ebd
- v1/reports/environment/clean_replay.json: PASS / ALTERNATIVE_VALIDATION / SHA256 e1a26735170c32c7a184e11361b0ba192c39ac3e583108f1d173b3659463b6cf
- v1/reports/synthesis/equivalence.json: UNVERIFIED / ALTERNATIVE_VALIDATION / SHA256 bbbcd85c011b03b8e4b3e24a1d7be9fdc7cd89149b38dd32a4cafe9603b307b9
- v1/reports/rtl/activity_debug.json: PASS / ALTERNATIVE_VALIDATION / SHA256 9cc7361e39b8e7376c70f0e9ab8e5ede1b2d27874a504234e28b875db09de04e

## Current plan and next action
Audit official server/platform/macros/library/flow on receipt, port adapters and run official gates in the same v1

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
