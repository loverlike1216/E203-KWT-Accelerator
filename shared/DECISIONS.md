# Effective decisions

- D-20261017-001, source User, status APPROVED_BY_USER: Project ID
  E203-KWT-Accelerator, repository loverlike1216/E203-KWT-Accelerator, workspace
  E:\Codex_project\E203-KWT-Accelerator, initialize v1. Identity confirmed through
  the user's reply and actual GitHub ownership/permissions queries.
- D-20261017-002, source User, status SUPERSEDED: stop after identity audit and
  wait for official server. Superseded by the next explicit user instruction.
- D-20261017-003, source User, status ACTIONABLE: build a suitable substitute
  environment and develop now for later migration to the official server.
  Record local results as ALTERNATIVE_VALIDATION; official validation remains open.
- D-20261017-004, source Codex implementation choice within approved scope:
  local native Windows tools and isolated Python 3.10 / TF 2.10.1; explicit
  semantic checkpoint mapping avoids old CLI side effects. No claim of TF 2.4
  equivalence; see v1/reports/model/COMPATIBILITY_RCA.md.

No ChatGPT decision has been imported. No version upgrade is approved.

- D-20261017-005, source Codex implementation within user-approved local scope:
  four signed16 MAC lanes / signed48 exact accumulators, interleaved synchronous
  one-port operand banks and a reference ICB adapter. Actual public E203 memory
  interface was inspected before implementation. Shared SRAM dual-port binding
  and local addresses remain reference-specific; official interface choice awaits
  the organizer's code. No fabricated DMA or hard-macro pin mapping is assumed.
- D-20261017-006, source observed simulation evidence: compile a 1ns/1ps timescale
  prefix before unchanged E203 units that contain #1 simulation flop delays.
  Initial CPU-stuck runs were failed/stopped, not counted as PASS. Corrected
  diagnostics execute firmware and load operands; reference ISA regression passes.
