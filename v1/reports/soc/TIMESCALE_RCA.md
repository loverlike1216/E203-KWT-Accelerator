# Reference SoC startup root cause

Initial local integration runs for layers 1 and 12 were stopped after diagnosis;
they never reached SoC PASS. Their actual nonzero command metadata/logs remain in
work/logs. A separate 30-second diagnostic emitted progress every 1000 cycles:
PC remained 00000000, operand counts and hardware outputs stayed zero.

Upstream general/sirv_gnrl_dffs.v uses nonblocking #1 simulation delays and has
no timescale. The new TB declared 1ns/1ps, while earlier compiled upstream units
inherited Icarus's default time unit. Thus those register delays were enormously
long relative to the TB clock. This is an integration harness error.

Fix: compile v1/tb/simulation_timescale.v first for both reference ISA and actual
driver simulations. It sets 1ns/1ps for the unchanged source units. Do not edit
the upstream models or remove their delays. Rerun ISA baseline and driver tests.
Simulation time units and successful functional execution still do not prove STA.
