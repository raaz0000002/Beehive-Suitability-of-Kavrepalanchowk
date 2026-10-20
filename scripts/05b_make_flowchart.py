import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(10, 12.5)); ax.set_xlim(0, 100); ax.set_ylim(0, 125); ax.axis("off")
INK, MUTE = "#0b0b0b", "#52514e"
FILL = {"data": "#e8f1fc", "proc": "#ffffff", "out": "#fde9e1", "check": "#f0efec"}
def box(x, y, w, h, title, body, kind="proc"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=FILL[kind], ec="#52514e", lw=0.9))
    ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=9, weight="bold", color=INK)
    if body: ax.text(x + w / 2, y + h - 4.6, body, ha="center", va="top", fontsize=7.8, color=MUTE, linespacing=1.35)
def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#52514e", lw=1.1))
# Stage 1: data
ax.text(50, 124, "Stage 1  Open data (Google Earth Engine and uploaded vectors)", ha="center", fontsize=10, weight="bold")
box(1, 104, 23, 17, "Land cover & greenness", "Esri LULC 10 m (2024)\nSentinel-2 NDVI median\n2019–2023 (scenario only)", "data")
box(26, 104, 23, 17, "Climate", "1991–2020 normals (~1 km):\nflow-season air temperature,\nannual precipitation;\nLST (scenario only)", "data")
box(51, 104, 23, 17, "Terrain & water", "Copernicus GLO-30 DEM:\nelevation, slope, aspect\nMERIT Hydro streams\n(upstream area ≥ 1 km²)", "data")
box(76, 104, 23, 17, "Access & boundary", "OSM roads (Geofabrik,\nvehicular classes)\nGADM 4.1 district\nboundary", "data")
for x in (12.5, 37.5, 62.5, 87.5): arrow(x, 103.5, 50 if False else x, 99.5)
# Stage 2
box(10, 88, 80, 11, "Stage 2  One analysis grid", "EPSG:32645, 10 m cells; bilinear (continuous) or nearest (categorical) resampling;\ncommon mask = cells valid in every criterion: 13,926,106 cells (1,392.61 km²)")
arrow(50, 87.5, 50, 84)
box(10, 72.5, 80, 11, "Stage 3  Standardise to 1–9", "Fixed rules: elevation bands, slope bands, aspect classes, LULC class scores, 100 m distance bands;\nnine equal intervals over the observed range for air temperature and precipitation")
arrow(50, 72, 50, 68.5)
# Stage 4 weights side by side
box(1, 53, 47, 15, "Stage 4  Literature-pooled weights", "13 published apiary MCDA weight sets\nlog-linear pooling; 5,000-draw bootstrap\nover studies (90% interval); leave-one-out", "data")
box(52, 53, 47, 15, "Stage 5  Aggregation models", "WLC (main):  S = Σ wᵢxᵢ\nWPM:  S = Π xᵢ^wᵢ\nTOPSIS: closeness to ideal (9) vs anti-ideal (1)")
arrow(48.5, 60.5, 51.5, 60.5)
arrow(75.5, 52.5, 75.5, 48.5)
# Stage 6 outputs
box(52, 33, 47, 15, "Stage 6  Classification", "Five classes, fixed 1.6-wide breaks on 1–9\n(Very Low … Very High); observed-range\nequal intervals and quintiles compared", "out")
box(1, 33, 47, 15, "Independent verification", "Separate float64 recomputation of WLC\nfrom the input rasters: identical score\nin all 13,926,106 cells", "check")
arrow(48.5, 40.5, 51.5, 40.5)
arrow(75.5, 32.5, 75.5, 28.5)
box(52, 13, 47, 15, "Stage 7  Sensitivity (81 scenarios)", "±10/20/30% one-at-a-time; remove one or both\nclimate criteria; 90% interval bounds; equal,\nROC and author AHP weights; NDVI, LST and\nalternative climate datasets", "check")
box(1, 13, 47, 15, "Stage 8  Descriptive location overlay", "7 documented locations: class, percentile\nand 500 m neighbourhood score;\ndescriptive overlay, no statistical test", "check")
arrow(51.5, 20.5, 48.5, 20.5)
arrow(50, 12.5, 50, 9)
box(10, 0.5, 80, 8, "Outputs", "Score, class, stability and SD maps; scenario tables; manifest with input SHA-256 hashes", "out")
import os, sys; _o = sys.argv[1] if len(sys.argv) > 1 else "results/figures"; os.makedirs(_o, exist_ok=True)
fig.savefig(os.path.join(_o, "Figure3_workflow.png"), dpi=300, bbox_inches="tight")
