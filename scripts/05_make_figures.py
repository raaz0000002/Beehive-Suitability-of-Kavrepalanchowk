import csv, json, numpy as np, rasterio, matplotlib
from rasterio.enums import Resampling
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, FancyBboxPatch
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#52514e",
                     "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e"})
import argparse, os
_ap = argparse.ArgumentParser(description="Draw Figures 4-10 of the paper (maps and charts) from a finished run.")
_ap.add_argument("--std", default="data/standardised"); _ap.add_argument("--run", default="results/main")
_ap.add_argument("--models", default="results/model_comparison"); _ap.add_argument("--config", default="config/weights_main_merit.json")
_ap.add_argument("--out", default="results/figures"); _a = _ap.parse_args(); os.makedirs(_a.out, exist_ok=True)
STD, R, MOD, CFG, O = _a.std, _a.run, _a.models, _a.config, _a.out
F = 4  # display at 40 m
SEQ5 = ["#b02e2e", "#e66767", "#e2e1dc", "#6da7ec", "#184f95"]  # diverging: low red, Moderate neutral, high blue
with open(os.path.join(R, "points.csv"), "r", encoding="utf-8") as f:
    pts = list(csv.DictReader(f))

def rd(path, res=Resampling.nearest, masked=True):
    with rasterio.open(path) as r:
        a = r.read(1, out_shape=(r.height // F, r.width // F), resampling=res, masked=masked)
        b = r.bounds
    return a, [b.left / 1000, b.right / 1000, b.bottom / 1000, b.top / 1000]

mask, ext = rd(R + "/class.tif")
valid = ~np.ma.getmaskarray(np.ma.masked_equal(mask, 0))

def frame(ax, km=True):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)

def scalebar(ax):
    x0, y0 = ext[1] - 14, ext[2] + 2
    ax.plot([x0, x0 + 10], [y0, y0], color="#0b0b0b", lw=2); ax.text(x0 + 5, y0 + 0.8, "10 km", ha="center", fontsize=7)
    ax.annotate("N", xy=(ext[1] - 3, ext[3] - 2), xytext=(ext[1] - 3, ext[3] - 7), ha="center", fontsize=9,
                arrowprops=dict(arrowstyle="-|>", color="#0b0b0b", lw=1.2))

def points(ax, labels=True):
    for p in pts:
        x, y = float(p["x"]) / 1000, float(p["y"]) / 1000
        ax.plot(x, y, marker="^", ms=8, color="#eb6834", mec="white", mew=1.2, ls="")
        if labels: ax.annotate(p["id"].split("_")[0], (x, y), xytext=(5, 3), textcoords="offset points", fontsize=8, weight="bold")

def classmap(ax, path, title):
    c, _ = rd(path); c = np.ma.masked_equal(c, 0)
    ax.imshow(c, extent=ext, cmap=ListedColormap(SEQ5), norm=BoundaryNorm(np.arange(0.5, 6.5), 5), interpolation="nearest")
    ax.set_title(title, fontsize=10); frame(ax)

# ---- Figure 5: suitability classes and continuous score
fig, axs = plt.subplots(1, 2, figsize=(11, 5.6))
classmap(axs[0], R + "/class.tif", "(a) Suitability class (fixed 1–9 equal intervals)")
axs[0].legend(handles=[Patch(color=SEQ5[i], label=CLS[i]) for i in range(5)], loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=5, fontsize=8, frameon=False)
scalebar(axs[0])
s, _ = rd(R + "/score.tif", Resampling.average); s = np.ma.masked_less(s, 0)
im = axs[1].imshow(s, extent=ext, cmap=ListedColormap(plt.get_cmap("Blues")(np.linspace(0.15, 1, 256))), vmin=3, vmax=8.5)
axs[1].set_title("(b) Continuous suitability score (WLC)", fontsize=10); frame(axs[1])
plt.colorbar(im, ax=axs[1], shrink=0.7, label="Score (1 = least, 9 = most suitable)")
fig.tight_layout(); fig.savefig(O + "/Figure6_suitability.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# ---- Figure 6: apiaries on the score map + percentile strip
fig = plt.figure(figsize=(11, 5.4)); ax = fig.add_axes([0.0, 0.05, 0.55, 0.9])
ax.imshow(s, extent=ext, cmap="Greys", vmin=2, vmax=9.5); points(ax); frame(ax); scalebar(ax)
ax.set_title("(a) Documented apiaries on the suitability score", fontsize=10)
ax2 = fig.add_axes([0.74, 0.15, 0.25, 0.72])
SHORT = {"Shree_Bhagwati_Beekeeping_Farmers_Group": "Shree Bhagwati group", "Sitaram_Furniture_and_Bee_Industry": "Sitaram Bee Industry"}
names = [SHORT.get(p["id"].split("_", 1)[1], p["id"].split("_", 1)[1].replace("_", " ")) for p in pts]; pc = [float(p["landscape_percentile"]) for p in pts]
order = np.argsort(pc)
with open(os.path.join(R, "manifest.json"), "r", encoding="utf-8") as f:
    HVH = json.load(f)["high_plus_very_high_pct"]
ax2.axvspan(100 - HVH, 100, color="#cde2fb", lw=0, label=f"Share of district in High or Very High ({HVH:.2f}%)")
ax2.scatter([pc[i] for i in order], range(7), s=60, color="#eb6834", edgecolor="white", zorder=3)
for j, i in enumerate(order): ax2.text(pc[i] + 2, j, f"{pc[i]:.1f}", va="center", fontsize=8)
ax2.set_yticks(range(7)); ax2.set_yticklabels([f"{pts[i]['id'].split('_')[0]}  {names[i]}" for i in order], fontsize=8)
ax2.set_xlim(0, 100); ax2.set_xlabel("Landscape percentile of the apiary's score")
ax2.grid(axis="x", color="#e6e5e1", lw=0.6); ax2.set_axisbelow(True)
for sp in ["top", "right"]: ax2.spines[sp].set_visible(False)
ax2.set_title("(b) Where each apiary ranks among all district cells", fontsize=10)
ax2.legend(loc="lower right", fontsize=7.5, frameon=False, bbox_to_anchor=(1, -0.32))
fig.savefig(O + "/Figure10_apiaries.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# ---- Figure 7: stability and SD
fig, axs = plt.subplots(1, 2, figsize=(11, 5.4))
st, _ = rd(R + "/stability_pct.tif", Resampling.average); st = np.ma.masked_less(st, 0)
im = axs[0].imshow(st, extent=ext, cmap="Blues", vmin=0, vmax=100); frame(axs[0]); scalebar(axs[0])
axs[0].set_title("(a) Scenarios keeping the baseline class (%)", fontsize=10); plt.colorbar(im, ax=axs[0], shrink=0.7, label="%")
sd, _ = rd(R + "/score_sd.tif", Resampling.average); sd = np.ma.masked_less(sd, 0)
im = axs[1].imshow(sd, extent=ext, cmap="Blues", vmin=0, vmax=float(np.percentile(sd.compressed(), 99))); frame(axs[1])
axs[1].set_title("(b) Standard deviation of the score across 78 scenarios", fontsize=10); plt.colorbar(im, ax=axs[1], shrink=0.7, label="Score SD")
fig.tight_layout(); fig.savefig(O + "/Figure9_stability.png", dpi=300); plt.close(fig)

# ---- Figure 8: model comparison
fig, axs = plt.subplots(1, 3, figsize=(14, 5.2))
classmap(axs[0], R + "/class.tif", "(a) WLC (main model)")
classmap(axs[1], MOD + "/class_WPM.tif", "(b) Weighted product (WPM)")
classmap(axs[2], MOD + "/class_TOPSIS.tif", "(c) TOPSIS")
for a_ in axs: points(a_, labels=False)
fig.legend(handles=[Patch(color=SEQ5[i], label=CLS[i]) for i in range(5)] +
           [plt.Line2D([], [], marker="^", color="#eb6834", ls="", mec="white", ms=8, label="Documented apiary")],
           loc="lower center", ncol=6, frameon=False, fontsize=8.5)
fig.tight_layout(rect=[0, 0.06, 1, 1]); fig.savefig(O + "/Figure7_model_comparison.png", dpi=300); plt.close(fig)

# ---- Figure 4: standardised criterion maps
keys = [("LULC", "(a) Land use/land cover"), ("AIRT", "(b) Air temperature"), ("PREC", "(c) Precipitation"),
        ("WATER_MERIT", "(d) Distance to stream"), ("ELEV", "(e) Elevation"), ("ROAD", "(f) Distance to road"),
        ("ASPECT", "(g) Aspect"), ("SLOPE", "(h) Slope")]
fig, axs = plt.subplots(2, 4, figsize=(14, 6.0), gridspec_kw=dict(wspace=0.02, hspace=0.08))
cm9 = ListedColormap(plt.get_cmap("Blues")(np.linspace(0.12, 1, 9)))
for ax, (k, t) in zip(axs.ravel(), keys):
    a_, _ = rd(f"{STD}/{k}.tif"); a_ = np.ma.masked_where(~valid, a_)
    im = ax.imshow(a_, extent=ext, cmap=cm9, norm=BoundaryNorm(np.arange(0.5, 10.5), 9), interpolation="nearest")
    ax.set_title(t, fontsize=10); frame(ax)
cb = fig.colorbar(im, ax=axs.ravel().tolist(), shrink=0.6, ticks=range(1, 10)); cb.set_label("Standardised score (1 = least, 9 = most suitable)")
fig.savefig(O + "/Figure5_criteria.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# ---- Figure 9: sensitivity (changed % per scenario group)
with open(os.path.join(R, "scenarios.csv"), "r", encoding="utf-8") as f:
    sc = {r_["scenario"]: r_ for r_ in csv.DictReader(f)}
crit = ["LULC", "TEMP", "PREC", "WATER", "ELEV", "ROAD", "ASPECT", "SLOPE"]
lab = {"LULC": "Land use/land cover", "TEMP": "Air temperature", "PREC": "Precipitation", "WATER": "Distance to stream",
       "ELEV": "Elevation", "ROAD": "Distance to road", "ASPECT": "Aspect", "SLOPE": "Slope"}
m30 = [float(sc[f"{k} -30%"]["changed_pct"]) for k in crit]; p30 = [float(sc[f"{k} +30%"]["changed_pct"]) for k in crit]
rem = [float(sc[f"Remove {k}"]["changed_pct"]) for k in crit]
fig, ax = plt.subplots(figsize=(8, 4.6)); y = np.arange(len(crit)); h = 0.26
ax.barh(y - h, m30, h - 0.03, color="#86b6ef", label="Weight −30%")
ax.barh(y, p30, h - 0.03, color="#2a78d6", label="Weight +30%")
ax.barh(y + h, rem, h - 0.03, color="#eb6834", label="Criterion removed")
for yy, v in zip(y + h, rem): ax.text(v + 0.8, yy, f"{v:.1f}", va="center", fontsize=7.5, color="#52514e")
ax.set_yticks(y); ax.set_yticklabels([lab[k] for k in crit]); ax.invert_yaxis()
ax.set_xlabel("Cells that change class (%)"); ax.grid(axis="x", color="#e6e5e1", lw=0.6); ax.set_axisbelow(True)
for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
ax.legend(frameon=False, loc="lower right", fontsize=8)
fig.tight_layout(); fig.savefig(O + "/Figure8_sensitivity.png", dpi=300); plt.close(fig)

# ---- Figure 10: literature-pooled weights with 90% intervals vs previous AHP weights
with open(CFG, "r", encoding="utf-8") as f:
    cfg = json.load(f)["criteria"]
prev = {"LULC": 0.3164, "TEMP": 0.1448, "PREC": 0.1023, "WATER": 0.0721, "ELEV": 0.0522, "ROAD": 0.0204, "ASPECT": 0.0273, "SLOPE": 0.0382}
fig, ax = plt.subplots(figsize=(7.5, 4.2))
w = [cfg[k]["weight"] for k in crit]; lo = [cfg[k]["lo"] for k in crit]; hi = [cfg[k]["hi"] for k in crit]
ax.errorbar(w, y, xerr=[np.subtract(w, lo), np.subtract(hi, w)], fmt="o", color="#2a78d6", ms=7, capsize=3, lw=1.5, label="Pooled literature weight (90% bootstrap interval)")
ax.scatter([prev[k] for k in crit], y, marker="D", s=30, color="#eb6834", zorder=3, label="Previous AHP weight (draft; LST for temperature)")
ax.set_yticks(y); ax.set_yticklabels([lab[k] for k in crit]); ax.invert_yaxis(); ax.set_xlabel("Weight")
ax.grid(axis="x", color="#e6e5e1", lw=0.6); ax.set_axisbelow(True)
for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.tight_layout(); fig.savefig(O + "/Figure4_weights.png", dpi=300); plt.close(fig)
print("ok")
