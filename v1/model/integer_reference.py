"""v1 signed integer linear contract, independent of TensorFlow."""
import math
import numpy as np


def scale_for(max_abs, bits, margin=1.0):
    if max_abs == 0:
        return 1.0
    return float(2.0 ** math.ceil(math.log2(max_abs * margin / (2 ** (bits - 1) - 1))))


def encode(value, scale, bits):
    rounded = np.rint(np.asarray(value, dtype=np.float64) / scale)  # nearest, ties even
    low, high = -(2 ** (bits - 1)), 2 ** (bits - 1) - 1
    saturation_count = int(np.count_nonzero((rounded < low) | (rounded > high)))
    return np.clip(rounded, low, high).astype(np.int64), saturation_count


def linear(x, w, b):
    """Exact signed integer result. Validity bound prevents int64 overflow."""
    x, w, b = (np.asarray(v, dtype=np.int64) for v in (x, w, b))
    if x.shape != (99, 64) or w.shape != (64, 256) or b.shape != (256,):
        raise ValueError("Invalid fixed task shape")
    bound = 64 * int(np.max(np.abs(x))) * int(np.max(np.abs(w))) + int(np.max(np.abs(b)))
    if bound >= 2**47:
        raise OverflowError("48-bit accumulator contract exceeded")
    return x @ w + b


def scalar_dot(x, w, b):
    """Independent scalar Python-int cross-check (no numpy accumulation)."""
    result = int(b)
    for a, weight in zip(x, w):
        result += int(a) * int(weight)
        if not -(2**47) <= result < 2**47:
            raise OverflowError("48-bit accumulation overflow")
    return result
