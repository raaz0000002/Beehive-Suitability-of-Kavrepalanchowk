"""Weighted linear combination (main model): S = sum_i w_i * x_i."""
import numpy as np


def wlc(X, w):
    s = np.zeros_like(next(iter(X.values())), dtype="float64")
    for k, wk in w.items():
        if wk:
            s += float(wk) * X[k].astype("float64")
    return s
