# Acceptance status

Official verdict is REVISE until all mandatory competition gates are supported
by actual official evidence. Local reference PASS is ALTERNATIVE_VALIDATION.

| Gate | Required | Current evidence boundary |
|---|---|---|
| Q01 | Actual fixed checkpoint / 12 FFN shapes | Local inventory and complete exact tensor restore |
| Q02 | Correct per-layer cutpoints | Local silence reconstruction; real speech validation next |
| Q03-Q07 | MAC, full matrix, reload, <=3%, bit-exact | Not yet verified |
| Q08 | Official E203 driver/hardware loop | Reference ISA tests only; official platform pending |
| Q09 | Post-synthesis function | Not yet verified |
| Q10 | 150 MHz official STA | Official flow pending |
| Q11 | <=2.25 mm2 including SRAM | Official libraries/area models pending |
| Q12 | Complete activity-based power | Official power flow/models pending |
| Q13 | Cold task throughput and J/task | Not yet verified; no energy without valid power |
| Q14 | Clean reproducibility | Local replay in progress |
| Q15 | Innovation / same-condition ablation | Optional; no innovation claim yet |

The actual thresholds remain in bootstrap/04_验收与质量门禁.md. The original
PDF is preserved locally with SHA256 b73a5414b4dcdb2cca337778a133be88705e207bec080687731d63b413ea927c.
