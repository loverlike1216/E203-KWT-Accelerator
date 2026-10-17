#include "driver.h"
int main(void) {
    volatile uint32_t *shared=(volatile uint32_t *)KWT_SHARED_BASE;
    int result=kwt_run(shared,shared+4096,shared+12288,1000000u);
    if(result==0) {
        /* CPU actually reads every hardware result; no software dot products. */
        uint32_t checksum=0;
        for(uint32_t i=0;i<50688;i++) checksum^=shared[16384+i];
        shared[81920]=checksum;
        __asm__ volatile("fence iorw,iorw" ::: "memory");
    }
    *(volatile uint32_t *)(KWT_MMIO_BASE+0xff0u)=result==0 ? 0x600d0001u : 0xbad00001u;
    return result;
}
