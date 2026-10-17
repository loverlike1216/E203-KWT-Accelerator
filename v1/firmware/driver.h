#ifndef KWT_DRIVER_H
#define KWT_DRIVER_H
#include <stdint.h>
#ifndef KWT_MMIO_BASE
#define KWT_MMIO_BASE 0xb0000000u
#endif
#ifndef KWT_SHARED_BASE
#define KWT_SHARED_BASE 0xa0000000u
#endif
/* Local map. Rebind only after official address-map and bus review. */
enum { KWT_BUSY=1, KWT_DONE=2, KWT_ERROR=4, KWT_CLEARING=8 };
int kwt_run(const volatile uint32_t *input,const volatile uint32_t *weight,
            const volatile uint32_t *bias,uint32_t timeout);
#endif
