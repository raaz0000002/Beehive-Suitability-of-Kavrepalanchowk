"""Weighted product model: S = prod_i x_i ** w_i (weighted geometric mean, 1-9 scale).

Less compensatory than WLC: a low score on one criterion pulls the product down more strongly."""
import numpy as np


def wpm(X, w):
    logs = np.zeros_like(next(iter(X.values())), dtype="float64")
    for k, wk in w.items():
        if wk:
            logs += float(wk) * np.log(X[k].astype("float64"))
    return np.exp(logs)
