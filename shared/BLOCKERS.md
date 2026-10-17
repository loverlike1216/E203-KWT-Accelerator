# Blockers and evidence boundaries

- BLOCKED_OFFICIAL_PLATFORM: organizer's server/source/test environment not yet
  supplied. Public E203 source can support development but cannot close Q08.
- BLOCKED_MEMORY_MACRO: official macro simulation/timing/area/power models absent.
- BLOCKED_ASIC_LIBRARY: official standard-cell library, corners and licensed flow absent.
- BLOCKED_POWER_EVIDENCE: official annotation/coverage and complete SRAM power flow absent.
- UNVERIFIED_OFFICIAL_600_SAMPLES: guide says selection is published after evaluation.
  Local validation must not be reported as the official set. Performance tasks also
  have a separate per-task 3% gate (PDF physical page 12), in addition to per-layer
  aggregate error over the accuracy set (physical page 11).
- CHAT_MEMORY_ACCESS_BLOCKED: no supported ChatGPT conversation history reader
  exposed in the current tool inventory. No chat title is confirmed by the user.

These block formal competition acceptance, not independent local development.

Local validation limitation: generic SAT equivalence did not finish in the bounded
180-second run. Actual metadata/logs and UNVERIFIED result are retained. Generic
mapped boundary simulation passed; full official post-synthesis acceptance stays open.
