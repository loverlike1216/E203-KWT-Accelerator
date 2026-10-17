# v1 requirement traceability — local reference scope

Source: original official PDF SHA256
b73a5414b4dcdb2cca337778a133be88705e207bec080687731d63b413ea927c;
physical page numbers below include the cover. Bootstrap 02/04 add execution gates.

| ID | Source / requirement | Implementation / real command | Evidence / current boundary |
|---|---|---|---|
| Q01 | p6 fixed ARM commit and best_weights | model_check.py, exact semantic tensor binding | checkpoint_inventory.json: local PASS, 12 real kernels/biases |
| Q02 | p7 FFN cut after attention/residual/first norm | model_check.cutpoints, quant_check | original class calls and reconstructed logits exact, real calibration/validation |
| Q03 | p8 64-term dot, numeric handling and reset | linear_engine.sv, tb_core_edges.sv | RTL and generic mapped core boundary simulation PASS |
| Q04 | p8 full 99x64 @64x256+bias and writeback | linear_mmio.sv, tb_engine.sv | 25,344 exact outputs per task, local PASS |
| Q05 | p8 twelve layer parameter replacement | sim_engine.py | 12 physically cleared/reloaded tasks, 304,128 checked outputs PASS |
| Q06 | p11 max per-layer aggregate NRMSE <=3%; p12 each performance task <=3% | quant_check.py / integer_reference.py | 89 train /45 validation, INT16 max aggregate 0.01030%, local PASS; official 600 and performance selections NOT_VERIFIED |
| Q07 | p11 RTL/model raw bits equal | full tb_engine and integer vectors | 304,128 exact signed48 comparisons PASS |
| Q08 | p8 E203 real driver and exchange | reference_soc.sv, driver.c, sim_accelerator_soc.py | local reference integration execution status in soc reports; official platform BLOCKED |
| Q09 | p12 synthesis/constraint/function consistency | synth_reference.py, optional equiv_reference.py | generic mapped boundary simulation PASS; bounded formal attempt UNVERIFIED; full official netlist equivalence BLOCKED |
| Q10 | p4/p12 150 MHz | candidate clock SDC | no false/multicycle paths; official STA BLOCKED, not inferred from simulation period |
| Q11 | p13 <=2.25 mm2 core/interface/internal macros | 6x16x4096 +12x16x128 reference bank geometry | capacity 52,224 bytes, 18 inferred memories; official area BLOCKED |
| Q12 | p12 complete E203/engine/interconnect/SRAM activity power | debug VCD only at present | formal representative activity mapping and SRAM/standard-cell power BLOCKED |
| Q13 | p12 cold task load through final writeback, schedule/waits included | reference SoC cycle counters | local first CPU source read to serialized writeback only; external preload not timed; official throughput/energy NOT_VERIFIED |
| Q14 | p14 clean repeat / versions/hashes | bootstrap, source lock, run.py, clean replay | local replay under verification; Linux/official clean replay pending |
| Q15 | p13 same-condition innovation and ablation | baseline preserved; memory/scheduling research deferred | OPTIONAL, no novelty/energy/performance improvement claim |

Additional invariants: p4 no external DDR, shared SRAM 512 KiB; p5 no training,
fine-tuning or CPU/TB arithmetic substitution; p7 no test-set tuning; p8 official
600 selection released after evaluation; p15 no precomputed evaluation answers.
Public code and real data are cached locally; restricted original inputs are ignored.

This is not a table of official PASS results. Official mandatory evidence remains
open and the final competition verdict is REVISE.
