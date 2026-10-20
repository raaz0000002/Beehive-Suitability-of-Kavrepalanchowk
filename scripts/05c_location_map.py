#!/usr/bin/env python3
"""Figure 2: location of Kavrepalanchowk District (study-area map).

Boundaries are not redistributed with the code. Inputs:
  --kavre  district polygon (Survey Department of Nepal; any CRS readable by geopandas)
  --adm0 --adm1 --adm2 --adm3  geoBoundaries gbOpen NPL ADM0 (country), ADM1 (provinces; Survey Department/OCHA,
           CC BY 3.0 IGO), ADM2 (districts, used only to group local levels) and ADM3 (local levels; Open Data
           Nepal/MoFAGA, CC BY-SA 4.0), from
           https://www.geoboundaries.org (Runfola et al. 2020)
  --points documented beekeeping locations (id,lat,lon)
Districts in panel (b) are dissolved from the local levels so that all internal lines share one source.
Needs geopandas and matplotlib.
"""
import argparse, csv, warnings
import numpy as np, geopandas as gpd, matplotlib
from shapely.ops import unary_union
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e"})
INK, MUTED, LINE = "#0b0b0b", "#52514e", "#9b9a96"
NEPAL, BAGMATI, KAVRE, ACCENT = "#efeeea", "#cde2fb", "#2a78d6", "#eb6834"

ap = argparse.ArgumentParser()
ap.add_argument("--kavre", required=True); ap.add_argument("--adm0", required=True)
ap.add_argument("--adm1", required=True); ap.add_argument("--adm2", required=True); ap.add_argument("--adm3", required=True)
ap.add_argument("--points", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()

kav = gpd.read_file(a.kavre).to_crs(4326); K = unary_union(kav.geometry.values)
npl = gpd.read_file(a.adm0).to_crs(4326); prov = gpd.read_file(a.adm1).to_crs(4326)
ll = gpd.read_file(a.adm3).to_crs(4326)
bag = prov[prov.shapeName == "Bagmati"].geometry.iloc[0]
# local levels of Kavre; districts of Bagmati dissolved from local levels (grouped by the district polygon they fall in)
llk = ll[ll.representative_point().within(K)].copy()
llb = ll[ll.representative_point().within(bag)].copy()
dist = gpd.read_file(a.adm2).to_crs(4326)
llb["district"] = [next((d.shapeName for d in dist.itertuples() if d.geometry.contains(pt)), None)
                   for pt in llb.representative_point()]
dlines = llb.dissolve("district").boundary

def aspect(ax, lat):
    ax.set_aspect(1 / np.cos(np.deg2rad(lat)))

def bare(ax):
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_visible(False)

fig = plt.figure(figsize=(7.0, 4.75))
axA = fig.add_axes([0.00, 0.55, 0.36, 0.40])
axB = fig.add_axes([0.02, 0.05, 0.32, 0.45])
axC = fig.add_axes([0.40, 0.06, 0.58, 0.90])

# (a) Nepal and its provinces
prov.plot(ax=axA, color=NEPAL, edgecolor=LINE, lw=0.4)
gpd.GeoSeries([bag]).plot(ax=axA, color=BAGMATI, edgecolor=MUTED, lw=0.6)
gpd.GeoSeries([K]).plot(ax=axA, color=KAVRE, edgecolor=KAVRE, lw=0.3)
npl.boundary.plot(ax=axA, color=MUTED, lw=0.7)
aspect(axA, 28.3); bare(axA)
axA.set_title("(a) Nepal", fontsize=8.5, loc="left", color=INK)
bx = bag.bounds
axA.annotate("Bagmati Province", xy=(84.75, 27.35), xytext=(84.2, 26.35), fontsize=7, color=MUTED,
             ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
axA.set_ylim(26.1, 30.6)

# (b) Bagmati Province and its districts
gpd.GeoSeries([bag]).plot(ax=axB, color=BAGMATI, edgecolor="none")
dlines.plot(ax=axB, color="white", lw=0.6)
gpd.GeoSeries([K]).plot(ax=axB, color=KAVRE, edgecolor="white", lw=0.6)
gpd.GeoSeries([bag]).boundary.plot(ax=axB, color=MUTED, lw=0.7)
aspect(axB, 27.7); bare(axB)
axB.set_title("(b) Bagmati Province", fontsize=8.5, loc="left", color=INK)
kc = K.representative_point()
axB.annotate("Kavrepalanchowk", xy=(kc.x - 0.05, kc.y - 0.12), xytext=(85.3, 26.95), fontsize=7, color=INK, ha="center",
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
axB.set_ylim(26.85, 28.45)

# (c) Kavrepalanchowk: local levels and documented beekeeping locations
llk.plot(ax=axC, color="#f6f5f2", edgecolor=LINE, lw=0.5)
gpd.GeoSeries([K]).boundary.plot(ax=axC, color=INK, lw=1.0)
NAME = {"Bethanchowk": "Bethanchok"}
LABEL_AT = {"Mandandeupur": (85.560, 27.722), "Panchkhal": (85.668, 27.624), "Banepa": (85.503, 27.656),
            "Dhulikhel": (85.588, 27.597), "Bhumlu": (85.745, 27.640), "Chaurideurali": (85.840, 27.556),
            "Temal": (85.756, 27.505), "Namobuddha": (85.640, 27.537), "Panauti": (85.447, 27.574),
            "Bethanchowk": (85.495, 27.490), "Roshi": (85.665, 27.472), "Khanikhola": (85.490, 27.425),
            "Mahabharat": (85.625, 27.390)}
for _, r in llk.iterrows():
    p = r.geometry.representative_point(); x, y = LABEL_AT.get(r.shapeName, (p.x, p.y))
    axC.text(x, y, NAME.get(r.shapeName, r.shapeName), fontsize=6.6, color=MUTED, ha="center", va="center")
pts = list(csv.DictReader(open(a.points)))
OFF = {"1": (6, -2), "2": (-12, -1), "3": (6, -2), "4": (6, 2), "5": (-12, -2), "6": (6, 2), "7": (6, 2)}
for p in pts:
    n = p["id"].split("_")[0]; x, y = float(p["lon"]), float(p["lat"])
    axC.plot(x, y, marker="^", ms=7.5, color=ACCENT, mec="white", mew=1.0, ls="", zorder=4)
    axC.annotate(n, (x, y), xytext=OFF.get(n, (6, 2)), textcoords="offset points", fontsize=7.5, weight="bold", color=INK, zorder=5)
axC.plot(85.5461, 27.6195, marker="*", ms=9, color=INK, mec="white", mew=0.6, ls="", zorder=4)
aspect(axC, 27.6)
x0, y0, x1, y1 = K.bounds
axC.set_xlim(x0 - 0.03, x1 + 0.03); axC.set_ylim(y0 - 0.03, y1 + 0.06)
for s in axC.spines.values(): s.set_visible(False)
xt = [85.5, 85.6, 85.7, 85.8, 85.9]; yt = [27.4, 27.5, 27.6, 27.7, 27.8]
axC.set_xticks(xt); axC.set_xticklabels([f"{v:.1f}°E" for v in xt], fontsize=6.5)
axC.set_yticks(yt); axC.set_yticklabels([f"{v:.1f}°N" for v in yt], fontsize=6.5)
axC.tick_params(length=2, color=LINE); axC.set_xlabel(""); axC.set_ylabel("")
axC.grid(color="#e6e5e1", lw=0.4, ls=":"); axC.set_axisbelow(True)
axC.set_title("(c) Kavrepalanchowk District", fontsize=8.5, loc="left", color=INK)
# scale bar (10 km) and north arrow
km = 1 / (111.32 * np.cos(np.deg2rad(27.4)))
sx, sy = x1 - 0.125, y0 + 0.02
axC.plot([sx, sx + 10 * km], [sy, sy], color=INK, lw=2, solid_capstyle="butt")
axC.text(sx + 5 * km, sy + 0.012, "10 km", ha="center", fontsize=6.8, color=INK)
axC.annotate("N", xy=(x1 + 0.005, y1 - 0.01), xytext=(x1 + 0.005, y1 - 0.075), ha="center", fontsize=8, color=INK,
             arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0))
axC.legend(handles=[Line2D([], [], marker="^", color=ACCENT, mec="white", ls="", ms=7, label="Documented beekeeping location"),
                    Line2D([], [], marker="*", color=INK, mec="white", ls="", ms=9, label="Dhulikhel (district headquarters)"),
                    Line2D([], [], color=LINE, lw=0.8, label="Local-level boundary")],
           loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=6.8, handletextpad=0.4)
fig.savefig(a.out, dpi=600, bbox_inches="tight", facecolor="white")
print("written", a.out)
