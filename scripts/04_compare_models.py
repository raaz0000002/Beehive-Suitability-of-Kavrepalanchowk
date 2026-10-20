#!/usr/bin/env python3
"""Multi-model check of the suitability map (Section 2.7 / 3.3 of the paper).

1. Recomputes WLC independently (apiary_mcda.models.wlc, float64) and compares it cell by cell with the
   main run's score.tif written by 03_run_main.py. Expected: max |difference| = 0 and 0 class changes.
2. Computes the weighted product model (WPM) and TOPSIS with the same weights.
3. Classifies all three with the same fixed 1-9 breaks; reports class shares, agreement with WLC,
   quadratic-weighted kappa, Spearman rho (200,000-cell sample, seed 42) and the share of cells on which
   all three models agree.
4. Reports each model's score, class and landscape percentile at the apiary points.

Usage: python scripts/04_compare_models.py --config config/weights_main_merit.json \
          --main-score results/main/score.tif --points data/points/apiaries_utm45n.csv --out results/model_comparison
"""
import argparse
import csv
import json
import os
import sys
import numpy as np
import rasterio
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apiary_mcda import MODELS, CLASSES, classify, weighted_kappa, load_stack

LABEL = {"WLC": "WLC (main)", "WPM": "WPM (weighted product)", "TOPSIS": "TOPSIS (closeness, rescaled 1-9)"}

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
ap.add_argument("--main-score", required=True)
ap.add_argument("--points")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

X, w, mask, prof = load_stack(a.config)
n = int(mask.sum())
tr = prof["transform"]
cell_km2 = abs(tr.a * tr.e) / 1e6
print(f"cells {n}  area {n * cell_km2:.3f} km2")

scores = {m: f(X, w) for m, f in MODELS.items()}
C = {m: classify(s) for m, s in scores.items()}

# 1. verification against the main run
with rasterio.open(a.main_score) as r:
    main = r.read(1).astype("float64")
    nd = r.nodata
mm = main[mask]
diff = np.abs(scores["WLC"] - mm)
ver = dict(cells_compared=n, max_abs_difference=float(diff.max()), mean_abs_difference=float(diff.mean()),
           cells_with_class_change=int((C["WLC"] != classify(mm)).sum()), main_mask_cells=int((main != nd).sum()))
print("verification", ver)

# 2-3. model comparison
rng = np.random.default_rng(42)
samp = rng.choice(n, min(200000, n), replace=False)
rows = []
for m, s in scores.items():
    c = C[m]
    cnt = np.bincount(c, minlength=5)
    rows.append({"model": LABEL[m], "score_min": round(float(s.min()), 4), "score_max": round(float(s.max()), 4),
                 "score_mean": round(float(s.mean()), 4), "score_sd": round(float(s.std()), 4),
                 **{f"{CLASSES[i]}_pct": round(100 * cnt[i] / n, 2) for i in range(5)},
                 "high_plus_very_high_pct": round(100 * (cnt[3] + cnt[4]) / n, 2),
                 "spearman_vs_WLC": round(float(spearmanr(scores["WLC"][samp], s[samp])[0]), 4),
                 "agreement_vs_WLC_pct": round(100 * float((c == C["WLC"]).mean()), 2),
                 "weighted_kappa_vs_WLC": round(float(weighted_kappa(C["WLC"], c)), 3)})
with open(os.path.join(a.out, "model_comparison.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, rows[0].keys())
    wr.writeheader()
    wr.writerows(rows)
for r_ in rows:
    print(r_)
ver["all_three_models_same_class_pct"] = round(100 * float(((C["WLC"] == C["WPM"]) & (C["WLC"] == C["TOPSIS"])).mean()), 2)

# 4. apiary points
if a.points:
    with open(a.points, "r", encoding="utf-8") as f:
        pts = list(csv.DictReader(f))
    srt = {m: np.sort(s) for m, s in scores.items()}
    idx = np.full(mask.shape, -1, np.int64)
    idx[mask] = np.arange(n)
    prow = []
    for p in pts:
        rr, cc = rasterio.transform.rowcol(tr, float(p["x"]), float(p["y"]))
        i = idx[rr, cc] if 0 <= rr < mask.shape[0] and 0 <= cc < mask.shape[1] else -1
        if i < 0:
            print("outside the study area:", p["id"])
            continue
        d = {"id": p["id"]}
        for m in scores:
            v = scores[m][i]
            d[LABEL[m] + " score"] = round(float(v), 3)
            d[LABEL[m] + " class"] = CLASSES[int(classify(np.array([v]))[0])]
            d[LABEL[m] + " percentile"] = round(100 * np.searchsorted(srt[m], v) / n, 1)
        prow.append(d)
    with open(os.path.join(a.out, "model_comparison_points.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, prow[0].keys())
        wr.writeheader()
        wr.writerows(prow)
    summ = {}
    for m, row in zip(scores, rows):
        k = sum(d[LABEL[m] + " class"] in ("High", "Very High") for d in prow)
        share = row["high_plus_very_high_pct"] / 100
        summ[LABEL[m]] = dict(in_high_or_very_high=k, of=len(prow), landscape_share_pct=round(share * 100, 2),
                              median_percentile=float(np.median([d[LABEL[m] + ' percentile'] for d in prow])))
    ver["points"] = summ
    print(summ)

for m in ("WPM", "TOPSIS"):
    out = np.zeros(mask.shape, "int8")
    out[mask] = C[m] + 1
    p = prof.copy()
    p.update(dtype="int8", nodata=0, count=1, compress="deflate")
    with rasterio.open(os.path.join(a.out, f"class_{m}.tif"), "w", **p) as o:
        o.write(out, 1)
with open(os.path.join(a.out, "model_comparison_verification.json"), "w", encoding="utf-8") as f:
    json.dump(ver, f, indent=2)
