    .section .init,"ax"
    .globl _start
    .option norelax
_start:
    li sp, 0x90010000
    csrw mie, zero
    li t0, 8
    csrc mstatus, t0
    la t0, trap
    csrw mtvec, t0
    call main
1:  j 1b
    .balign 4
trap:
    li t0, 0xb0000ff0
    li t1, 0xbad00002
    sw t1, 0(t0)
2:  j 2b
