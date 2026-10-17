OUTPUT_ARCH(riscv)
ENTRY(_start)
MEMORY { ITCM (rx) : ORIGIN = 0x80000000, LENGTH = 64K }
SECTIONS {
  .text : { KEEP(*(.init)) *(.text*) *(.rodata*) } > ITCM
  .data : { *(.data*) } > ITCM
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } > ITCM
  ASSERT(SIZEOF(.bss) == 0, "Startup has no implicit BSS initialization")
  ASSERT(. <= 0x80010000, "Firmware exceeds reference ITCM")
}
