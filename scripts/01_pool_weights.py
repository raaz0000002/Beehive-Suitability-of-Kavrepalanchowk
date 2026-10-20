#!/usr/bin/env python3
"""Pool published AHP/MCDA criterion weights into one weight set (Section 2.5 of the paper).

Model: ln w[study, criterion] = study effect + criterion effect, fitted by least squares over the
criteria each study actually uses. The exponentiated criterion effects, normalised to sum to 1, are the
pooled weights. Uncertainty: 5,000 study-level bootstrap draws (seed 1; draws that miss a criterion are
discarded) giving 90% percentile intervals, plus leave-one-study-out ranges.

Input : data/literature/evidence_weights.csv (one row per study x criterion, global weights)
Output: results/pooled_weights.csv and a printed table
"""
import csv, os, sys
from collections import OrderedDict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
C = ["VEG", "TEMP", "PREC", "WATER", "ELEV", "SLOPE", "ASPECT", "ROAD"]
MODEL_NAME = {"VEG": "LULC", "TEMP": "TEMP", "PREC": "PREC", "WATER": "WATER", "ELEV": "ELEV",
              "SLOPE": "SLOPE", "ASPECT": "ASPECT", "ROAD": "ROAD"}


def load(path):
    st = OrderedDict()
    for r in csv.DictReader(open(path, encoding="utf-8")):
        st.setdefault(r["study_id"], {})[r["criterion"]] = float(r["weight"])
    return [dict(id=k, w=v) for k, v in st.items()]


def lls(studies):
    rows, y = [], []
    S, K = len(studies), len(C)
    for s, st in enumerate(studies):
        for k, c in enumerate(C):
            if c in st["w"]:
                x = np.zeros(S + K); x[s] = 1; x[S + k] = 1
                rows.append(x); y.append(np.log(st["w"][c]))
    b = np.linalg.lstsq(np.array(rows), np.array(y), rcond=None)[0][S:]
    b -= b.mean(); w = np.exp(b)
    return w / w.sum()


def round_to_one(w, nd=3):
    """Round to nd decimals; push the rounding residue onto the largest weight so the set sums to 1."""
    r = np.round(w, nd); r[np.argmax(w)] += round(1 - r.sum(), nd)
    return np.round(r, nd)


def main(path=os.path.join(ROOT, "data/literature/evidence_weights.csv"), out=os.path.join(ROOT, "results")):
    studies = load(path)
    W = lls(studies)
    rng = np.random.default_rng(1); B = []
    for _ in range(5000):
        sub = [studies[i] for i in rng.integers(0, len(studies), len(studies))]
        if all(any(c in s["w"] for s in sub) for c in C):
            B.append(lls(sub))
    B = np.array(B); lo, hi = np.percentile(B, 5, 0), np.percentile(B, 95, 0)
    L = np.array([lls([s for j, s in enumerate(studies) if j != i]) for i in range(len(studies))])
    top = sum(max(s["w"], key=s["w"].get) == "VEG" for s in studies)
    Wr = round_to_one(W)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "pooled_weights.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["criterion", "n_studies", "pooled_weight_raw", "weight_used", "boot90_lo", "boot90_hi", "loo_min", "loo_max"])
        for k in np.argsort(-W):
            wr.writerow([MODEL_NAME[C[k]], sum(C[k] in s["w"] for s in studies), round(W[k], 4), Wr[k],
                         round(lo[k], 3), round(hi[k], 3), round(L[:, k].min(), 3), round(L[:, k].max(), 3)])
    print(f"studies {len(studies)}  valid bootstrap draws {len(B)}  land cover top-weighted in {top} studies")
    print(open(os.path.join(out, "pooled_weights.csv")).read())
    return dict(W=W, Wr=Wr, lo=lo, hi=hi, n_boot=len(B), top=top)


if __name__ == "__main__":
    main(*sys.argv[1:])
