# Acceptance status

Official verdict is REVISE until all mandatory competition gates are supported
by actual official evidence. Local reference PASS is ALTERNATIVE_VALIDATION.

| Gate | Required | Current evidence boundary |
|---|---|---|
| Q01 | Actual fixed checkpoint / 12 FFN shapes | Local inventory and complete exact tensor restore |
| Q02 | Correct per-layer cutpoints | Original-class reconstruction exact; actual speech training/validation extraction locally verified |
| Q03-Q07 | MAC, full matrix, reload, <=3%, bit-exact | Local 12 layers/304,128 RTL outputs PASS; validation NRMSE max layer 0.01030%; official 600/tasks not verified |
| Q08 | Official E203 driver/hardware loop | Reference layers 1/12 actual CPU/hardware/readback PASS; official platform and full CPU 12-task test pending |
| Q09 | Post-synthesis function | Generic mapped boundary tests PASS; generic SAT timeout UNVERIFIED; official full equivalence pending |
| Q10 | 150 MHz official STA | Official flow pending |
| Q11 | <=2.25 mm2 including SRAM | Official libraries/area models pending |
| Q12 | Complete activity-based power | Official power flow/models pending |
| Q13 | Cold task throughput and J/task | Local CPU-load to writeback 956,689 cycles for layers 1/12; excludes TB preload; official throughput/energy not verified |
| Q14 | Clean reproducibility | Clean checkout + second venv numeric/12-layer RTL/synthesis PASS; Linux/official replay pending |
| Q15 | Innovation / same-condition ablation | Optional; no innovation claim yet |

The actual thresholds remain in bootstrap/04_验收与质量门禁.md. The original
PDF is preserved locally with SHA256 b73a5414b4dcdb2cca337778a133be88705e207bec080687731d63b413ea927c.
