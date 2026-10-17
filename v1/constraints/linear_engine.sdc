# Candidate clock target only. Official I/O delays, loads, corners and SRAM
# timing are unknown; this file is not a claim of complete official constraints.
create_clock -name clk -period 6.666666667 [get_ports clk]
# No false-path or multicycle exceptions are used.
