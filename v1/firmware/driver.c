#include "driver.h"
static volatile uint32_t *const registers=(volatile uint32_t *)KWT_MMIO_BASE;
static int wait_clear(uint32_t timeout) {
    while(timeout--) if((registers[0]&KWT_CLEARING)==0) return 0;
    return -1;
}
int kwt_run(const volatile uint32_t *input,const volatile uint32_t *weight,
            const volatile uint32_t *bias,uint32_t timeout) {
    if(wait_clear(timeout)) return -1;
    registers[0]=2; /* Physically clear operand banks; no cross-task retention. */
    if(wait_clear(timeout)) return -1;
    volatile uint32_t *destination=(volatile uint32_t *)(KWT_MMIO_BASE+0x10000u);
    for(uint32_t i=0;i<3168;i++) destination[i]=input[i];
    destination=(volatile uint32_t *)(KWT_MMIO_BASE+0x20000u);
    for(uint32_t i=0;i<8192;i++) destination[i]=weight[i];
    destination=(volatile uint32_t *)(KWT_MMIO_BASE+0x30000u);
    for(uint32_t i=0;i<512;i++) destination[i]=bias[i];
    __asm__ volatile("fence iorw,iorw" ::: "memory");
    registers[0]=1;
    while(timeout--) {
        uint32_t status=registers[0];
        if(status&KWT_ERROR) return -2;
        if(status&KWT_DONE) return 0;
    }
    return -3;
}
