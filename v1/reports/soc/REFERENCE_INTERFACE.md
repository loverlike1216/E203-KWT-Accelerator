# Local reference interface and migration boundary

The unchanged public E203 cpu_top exposes a system memory ICB master. The local
candidate uses that interface rather than custom NICE instructions. Reference-only
addresses: shared SRAM A0000000-A007FFFF; accelerator B0000000-B00FFFFF; completion
mailbox B0000FF0. CPU instruction/data TCMs retain their upstream configuration.
This is not the organizer's complete peripheral, ROM/PLL or reset implementation.

Shared SRAM holds X at offset 0, W at 0x4000, padded bias at 0xC000, output at
0x10000, readback checksum at 0x50000. Total occupied end: 0x50004, within 512 KiB.
CPU uses synchronous port A; engine serializes four outputs into eight 32-bit
writes on port B, holding its valid data under backpressure. One write per port
per clock. No invented upstream DMA is used. Official shared SRAM access rights,
arbitration and available ports must be checked and rebound after server receipt.

Accelerator offsets: control/status 0, compute cycles 4, MAC count 8; X 0x10000,
W 0x20000, bias 0x30000. Control 2 starts physical SRAM clearing; 1 starts compute
only after complete sequential loads (3168 X words, 8192 W words, 512 bias words).
Status bits: busy/done/error/clearing in bits 0/1/2/3. Full aligned word writes only.
Invalid address, write mask, order or repeated START sets sticky protocol error;
an in-flight computation completes without operand mutation. Clear while idle
recovers errors; hard reset aborts busy tasks. Firmware polling is bounded and
returns errors; system-reset recovery on a hardware hang is platform-specific.

Internal reference SRAM: 6 banks of 16x4096 (two interleaved X banks and four W
banks), 12 banks of 16x128 for bias chunks. Nominal capacity 52,224 bytes. Every
bank has exactly one synchronous read/write port. The module is a functional and
memory-inference implementation, not a hard-macro area/power estimate. Official
bindings must implement the same timing contract or adapt the handshake.

Tests initialize shared SRAM/ITCM only. They never issue CPU commands or compute
the accelerator's output on its behalf. Actual firmware copies operands, starts
hardware, polls completion and reads all 50,688 result words. The testbench checks
all 25,344 results and the CPU's readback checksum against independently generated
bit-exact vectors. Initial testbench loading is excluded from reported local cycle
counts; official cold-start benchmark remains open until its loader is integrated.
