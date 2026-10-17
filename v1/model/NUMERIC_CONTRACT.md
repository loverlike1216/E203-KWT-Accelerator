# Locked local v1 numeric contract

Input and weight: signed two's-complement INT16, separate per-layer power-of-two
scales from numeric_config.json. Input scale derives only from 89 training samples
with a predeclared 1.25 range margin. Weight scale derives from that layer's actual
fixed checkpoint weights. No gradients, test samples or weight changes are used.

Encode X and W with nearest, ties to even, then signed saturation [-32768,32767].
Bias: nearest, ties to even at input_scale * weight_scale, signed 48-bit. Reject
bias saturation. Dot product: 64 signed 16x16 products, exact sign extension and
48-bit accumulation, with aligned bias added once. Validate a conservative absolute
bound below 2^47 before each task. No intermediate rounding or saturation.

Output: raw signed 48-bit accumulator; decode by multiplying by input_scale *
weight_scale. There is no output requantization. Bus transport uses a low 32-bit
word followed by a sign-extended high 16-bit word (64-bit padded slot). This is a
transport convention, not a different numeric format. RTL must match all 48 bits.

Row-major X[99,64], W[64,256], Y[99,256]. Four output lanes are the initial portable
baseline candidate. Every lane accumulates k=0..63 in order. Backpressure may only
delay operations; it must not duplicate, skip or reorder operands/results.

Evidence: quantization.json compares INT8 and INT16 using 45 separate validation
samples (13,685,760 output values per format). INT8 aggregate error meets 3%, but
some individual validation tasks exceed 3%; retain INT16 as the baseline. The
official 600 samples and official performance tasks remain unverified.

Any change to format, alignment, scale derivation or rounding requires regeneration
of numeric evidence and complete RTL regression. No per-task adaptive tuning.
