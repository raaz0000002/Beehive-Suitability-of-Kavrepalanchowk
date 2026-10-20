#!/usr/bin/env python3
"""Neighbourhood context of the documented beekeeping locations (Section 2.9 and Table 10 of the paper).

For each location: the WLC score of its own 10 m cell, its class and landscape percentile; the mean WLC score of all
valid cells within a 500 m radius and the percentile of that mean among the 500 m means of every cell in the
district (a like-for-like comparison); and the share of cells within 500 m that the land-cover layer classes as
Built Area, Bare Ground or Snow/Ice (LULC score 1).

Usage: python scripts/07_point_context.py --score results/main/score.tif --lulc data/standardised/LULC.tif \
          --points data/points/apiaries_utm45n.csv --radius 500 --out results/main/points_500m.csv
Needs numpy, scipy, rasterio (about 3 GB RAM)."""
import argparse, csv, json, os
import numpy as np, rasterio
from scipy.signal import oaconvolve

ap = argparse.ArgumentParser()
ap.add_argument("--score", required=True); ap.add_argument("--lulc", required=True)
ap.add_argument("--points", required=True); ap.add_argument("--radius", type=float, default=500)
ap.add_argument("--out", required=True)
a = ap.parse_args()

BREAKS = [1.0, 2.6, 4.2, 5.8, 7.4, 9.0]; CLASSES = ["Very Low", "Low", "Moderate", "High", "Very High"]
with rasterio.open(a.score) as r:
    s = r.read(1).astype("float64"); nd = r.nodata; tr = r.transform; res = r.res[0]
valid = (s != nd) & np.isfinite(s) & (s >= 1)
with rasterio.open(a.lulc) as r:
    lu = r.read(1)
built = (lu == 1) & valid

rad = int(round(a.radius / res)); yy, xx = np.mgrid[-rad:rad + 1, -rad:rad + 1]
k = ((xx ** 2 + yy ** 2) <= rad ** 2).astype("float64")
num = oaconvolve(np.where(valid, s, 0.0), k, mode="same")
den = oaconvolve(valid.astype("float64"), k, mode="same")
bb = oaconvolve(built.astype("float64"), k, mode="same")
with np.errstate(invalid="ignore", divide="ignore"):
    m500 = num / den
srt_cell = np.sort(s[valid]); srt_m = np.sort(m500[valid])
n = srt_cell.size

rows = []
for p in csv.DictReader(open(a.points)):
    rr, cc = rasterio.transform.rowcol(tr, float(p["x"]), float(p["y"]))
    v = s[rr, cc]; mm = m500[rr, cc]
    rows.append(dict(id=p["id"], score=round(float(v), 3),
                     cls=CLASSES[int(np.digitize([v], BREAKS[1:-1], right=True)[0])],
                     percentile=round(100 * float(np.searchsorted(srt_cell, v)) / n, 1),
                     lulc_score_at_point=int(lu[rr, cc]),
                     mean_score_500m=round(float(mm), 3),
                     mean_500m_percentile=round(100 * float(np.searchsorted(srt_m, mm)) / n, 1),
                     built_or_bare_500m_pct=round(max(0.0, 100 * float(bb[rr, cc] / den[rr, cc])), 1)))
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
with open(a.out, "w", newline="") as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
summary = dict(radius_m=a.radius, district_mean_500m=dict(min=round(float(srt_m[0]), 3), max=round(float(srt_m[-1]), 3)),
               mean_500m_percentile_range=[min(r["mean_500m_percentile"] for r in rows), max(r["mean_500m_percentile"] for r in rows)],
               built_or_bare_500m_pct_range=[min(r["built_or_bare_500m_pct"] for r in rows), max(r["built_or_bare_500m_pct"] for r in rows)])
json.dump(summary, open(a.out.replace(".csv", "_summary.json"), "w"), indent=2)
for r in rows: print(r)
print(summary)
