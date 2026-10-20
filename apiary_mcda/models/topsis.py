"""TOPSIS with fixed reference points.

Scores are rescaled to 0-1 as (x - 1) / 8 and weighted (v_i = w_i * r_i). The ideal cell scores 9 on
every criterion (v_i = w_i) and the anti-ideal scores 1 (v_i = 0). Fixed references keep each cell's
result independent of the others. Closeness C = d- / (d+ + d-) is mapped to 1-9 as 1 + 8C."""
import numpy as np


def topsis(X, w):
    dplus = 0.0
    dminus = 0.0
    for k, wk in w.items():
        if not wk:
            continue
        v = float(wk) * (X[k].astype("float64") - 1) / 8
        dplus = dplus + (float(wk) - v) ** 2
        dminus = dminus + v ** 2
    dplus, dminus = np.sqrt(dplus), np.sqrt(dminus)
    return 1 + 8 * dminus / (dplus + dminus)
