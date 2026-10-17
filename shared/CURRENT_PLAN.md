# Current plan — v1

1. DONE locally: environment, unchanged public E203 ISA baseline and checkpoint audit.
2. DONE locally: training-only calibration, separate validation, exact integer contract.
3. DONE locally: full-matrix RTL, reset/boundaries/backpressure and twelve layer reloads.
4. VERIFIED locally: reference E203 firmware/hardware tasks for layers 1 and 12.
   Full twelve-task CPU regression remains open; all twelve accelerator tasks passed.
5. VERIFIED locally: generic synthesis/mapped boundary checks and clean numeric/RTL
   replay and source/evidence packaging with CRC/hash validation. Generic SAT proof
   is UNVERIFIED. Final state/publication synchronization accompanies delivery.
6. On receipt of official server: platform/macro adapter review; exact upstream
   runtime revalidation; official baseline; official synthesis, STA, power and
   frozen workload acceptance. No version upgrade.

P0 gates take priority. No innovation claim before complete baseline and matched
condition measurements. Missing official PPA is never replaced with a local PASS.
