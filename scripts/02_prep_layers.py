#!/usr/bin/env python3
"""Prepare layers for rerun_model.py.

  climate : two-band climate GeoTIFF exported by gee/05_climate_1991_2020.js (band 1 = flow-season mean air
            temperature, degC; band 2 = annual precipitation, mm) on its native grid -> bilinear onto the 10 m
            template grid -> raw rasters and 1-9 scores (nine equal intervals over the range inside the common mask)
            python3 scripts/02_prep_layers.py climate --src raw/clim_1991_2020_main_wcgrid.tif \
                --template data/standardised/LULC.tif --mask-config config/weights_main.json --tag 1991_2020 \
                --out-dir data/standardised --raw-dir raw
  airtemp : WorldClim monthly mean air temperature files -> aligned 10 m grid -> 1-9 scores
            python3 prep_layers.py airtemp --wc-dir wc2.1_30s_tavg --template rasters/LULC.tif --out rasters/AIRT.tif
  align   : put any raster on the template grid (nearest for categorical, bilinear for continuous)
            python3 prep_layers.py align --src old/slope_score.tif --template rasters/LULC.tif --out rasters/SLOPE.tif --categorical
  points  : convert apiary GPS points (id,lat,lon in decimal degrees) to UTM 45N for rerun_model.py
            python3 prep_layers.py points --src apiaries_latlon.csv --out apiaries.csv
  score   : nine equal intervals (1-9) of a raw continuous raster over its range inside a mask raster
            python3 prep_layers.py score --src raw/raw_AIRT_degC.tif --mask-dir rasters --out rasters/AIRT.tif
  check   : report grid, CRS, value range and NoData share of every .tif in a folder
            python3 prep_layers.py check --dir rasters
Needs numpy and rasterio.
"""
import argparse, glob, os, sys
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.windows import from_bounds


def template(path):
    with rasterio.open(path) as t:
        valid = ~np.ma.getmaskarray(t.read(1, masked=True))
        return t.profile.copy(), t.bounds, t.crs, t.transform, t.shape, valid


def write(path, arr, prof, nodata=-9999):
    p = prof.copy(); p.update(count=1, dtype="float32", nodata=nodata, compress="deflate")
    with rasterio.open(path, "w", **p) as d:
        d.write(np.where(np.isnan(arr), nodata, arr).astype("float32"), 1)


def warp(src_path, prof, crs, tr, shape, resampling):
    out = np.full(shape, np.nan, "float32")
    with rasterio.open(src_path) as s:
        reproject(rasterio.band(s, 1), out, src_nodata=s.nodata, dst_transform=tr, dst_crs=crs,
                  dst_nodata=np.nan, resampling=resampling)
    return out


def airtemp(a):
    prof, bounds, crs, tr, shape, valid = template(a.template)
    months = [int(m) for m in a.months.split(",")]
    files = []
    for m in months:
        f = glob.glob(os.path.join(a.wc_dir, f"*tavg_{m:02d}.tif"))
        if not f: sys.exit(f"No WorldClim file for month {m:02d} in {a.wc_dir}")
        files.append(f[0])
    stack = []
    for f in files:
        with rasterio.open(f) as s:   # read only the district window (plus margin) of the global file
            b = transform_bounds(crs, s.crs, *bounds, densify_pts=21)
            pad = 0.05
            win = from_bounds(b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad, s.transform).round_offsets().round_lengths()
            data = s.read(1, window=win, masked=True).astype("float32").filled(np.nan)
            wtr = s.window_transform(win)
            out = np.full(shape, np.nan, "float32")
            reproject(data, out, src_transform=wtr, src_crs=s.crs, src_nodata=np.nan,
                      dst_transform=tr, dst_crs=crs, dst_nodata=np.nan, resampling=Resampling.bilinear)
            stack.append(out)
    t = np.nanmean(np.stack(stack), axis=0)
    t[~valid] = np.nan
    v = t[~np.isnan(t)]
    lo, hi = float(v.min()), float(v.max())
    edges = np.linspace(lo, hi, 10)
    score = np.digitize(t, edges[1:-1], right=False).astype("float32") + 1   # 1..9, nine equal intervals
    score[np.isnan(t)] = np.nan
    write(a.out.replace(".tif", "_degC.tif"), t, prof)
    write(a.out, score, prof)
    print(f"Months {months}; air temperature {lo:.3f}-{hi:.3f} °C over {v.size} cells")
    print("Class lower bounds (°C) for the paper's standardisation table:")
    for i in range(9):
        print(f"  {i+1} = {edges[i]:.3f} to {'<' if i < 8 else ''}{edges[i+1]:.3f}")


def common_mask(config_path, skip):
    """Cells valid (> 0) in every criterion and scenario layer of a weights config, except the layers in skip."""
    import json
    cfg = json.load(open(config_path)); root = os.path.dirname(os.path.abspath(config_path))
    layers = dict(cfg["criteria"]); layers.update(cfg.get("scenario_layers", {}))
    m = None
    for k, v in layers.items():
        f = os.path.normpath(os.path.join(root, v["file"]))
        if k in skip or not os.path.exists(f):
            continue
        with rasterio.open(f) as r:
            x = r.read(1)
            mk = (x > 0) & (x != (r.nodata if r.nodata is not None else 0))
        m = mk if m is None else m & mk
    return m


def nine(x, valid):
    v = x[valid]; lo, hi = float(v.min()), float(v.max())
    edges = np.linspace(lo, hi, 10)
    out = np.digitize(x, edges[1:-1], right=False).astype("float32") + 1
    out[~valid] = np.nan
    return out, edges


def climate(a):
    prof, bounds, crs, tr, shape, tvalid = template(a.template)
    mask = common_mask(a.mask_config, skip={"TEMP", "PREC"} | {k for k in a.skip.split(",") if k})
    if mask is None:
        mask = tvalid
    os.makedirs(a.out_dir, exist_ok=True); os.makedirs(a.raw_dir, exist_ok=True)
    with rasterio.open(a.src) as s:
        if s.count < 2:
            sys.exit(f"{a.src}: expected 2 bands (air temperature, precipitation)")
        for band, key, unit in [(1, "AIRT", "degC"), (2, "PREC", "mm")]:
            out = np.full(shape, np.nan, "float32")
            src = s.read(band).astype("float32")
            if s.nodata is not None:
                src[src == s.nodata] = np.nan
            reproject(src, out, src_transform=s.transform, src_crs=s.crs, src_nodata=np.nan,
                      dst_transform=tr, dst_crs=crs, dst_nodata=np.nan, resampling=Resampling.bilinear)
            valid = mask & ~np.isnan(out)
            if valid.sum() < mask.sum():
                print(f"WARNING {key}: {int(mask.sum() - valid.sum())} mask cells have no climate value")
            raw = np.where(mask, out, np.nan)
            sc, edges = nine(out, valid)
            write(os.path.join(a.raw_dir, f"raw_{key}_{a.tag}_{unit}.tif"), raw, prof)
            write(os.path.join(a.out_dir, f"{key}_{a.tag}.tif"), sc, prof)   # float32, NoData -9999, like the other score layers
            v = out[valid]
            print(f"{key}_{a.tag}: {v.min():.3f}-{v.max():.3f} {unit} over {v.size} cells "
                  f"(mean {v.mean():.2f}, SD {v.std():.2f}, median {np.median(v):.2f})")
            for i in range(9):
                print(f"  {i+1} = {edges[i]:.3f} to {'<' if i < 8 else ''}{edges[i+1]:.3f}")


def align(a):
    prof, bounds, crs, tr, shape, valid = template(a.template)
    out = warp(a.src, prof, crs, tr, shape, Resampling.nearest if a.categorical else Resampling.bilinear)
    write(a.out, out, prof)
    print(f"{a.src} -> {a.out} on the template grid")


def points(a):
    import csv
    from rasterio.warp import transform as tf
    rows = list(csv.DictReader(open(a.src, newline="", encoding="utf-8-sig")))
    lat = [float(r["lat"]) for r in rows]; lon = [float(r["lon"]) for r in rows]
    if not all(26 < y < 31 and 80 < x < 89 for x, y in zip(lon, lat)):
        sys.exit("Some points are outside Nepal: check that lat and lon are decimal degrees and not swapped")
    xs, ys = tf("EPSG:4326", "EPSG:32645", lon, lat)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "x", "y"])
        for r, x, y in zip(rows, xs, ys):
            w.writerow([r["id"], round(x, 2), round(y, 2)])
    print(f"{len(rows)} points written to {a.out} (EPSG:32645)")


def score(a):
    with rasterio.open(a.src) as r:
        x = r.read(1, masked=True).astype("float32").filled(np.nan); prof = r.profile.copy()
    valid = ~np.isnan(x)
    for f in sorted(glob.glob(os.path.join(a.mask_dir, "*.tif"))):   # common mask of the score layers (0 = NoData)
        with rasterio.open(f) as r:
            m = r.read(1, masked=True)
            valid &= ~np.ma.getmaskarray(m) & (m.filled(0) != 0)
    v = x[valid]; lo, hi = float(v.min()), float(v.max())
    edges = np.linspace(lo, hi, 10)
    out = np.digitize(x, edges[1:-1]).astype("float32") + 1
    out[~valid] = np.nan
    write(a.out, out, prof)
    print(f"{a.src}: {lo:.3f} to {hi:.3f} over {v.size} cells")
    for i in range(9):
        print(f"  {i+1} = {edges[i]:.3f} to {'<' if i < 8 else ''}{edges[i+1]:.3f}")


def check(a):
    ref = None
    for f in sorted(glob.glob(os.path.join(a.dir, "*.tif"))):
        with rasterio.open(f) as r:
            x = r.read(1, masked=True)
            grid = (r.crs.to_string() if r.crs else None, r.shape, tuple(round(v, 3) for v in r.transform[:6]))
            ref = ref or grid
            flag = "OK" if grid == ref else "GRID DIFFERS"
            print(f"{os.path.basename(f):22s} {grid[0]} {r.shape} cell {r.res[0]:.1f} m  "
                  f"values {x.min():.3f}-{x.max():.3f}  NoData {100*np.ma.getmaskarray(x).mean():.2f}%  {flag}")


ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
p = sub.add_parser("airtemp"); p.add_argument("--wc-dir", required=True); p.add_argument("--template", required=True)
p.add_argument("--out", required=True); p.add_argument("--months", default="3,4,5,9,10,11",
               help="foraging months; default = the main honey flows in Neupane et al. 2024")
p = sub.add_parser("climate"); p.add_argument("--src", required=True); p.add_argument("--template", required=True)
p.add_argument("--mask-config", required=True); p.add_argument("--tag", required=True)
p.add_argument("--out-dir", default="data/standardised"); p.add_argument("--raw-dir", default="raw")
p.add_argument("--skip", default="", help="comma-separated config keys left out of the mask (e.g. layers not built yet)")
p = sub.add_parser("align"); p.add_argument("--src", required=True); p.add_argument("--template", required=True)
p.add_argument("--out", required=True); p.add_argument("--categorical", action="store_true")
p = sub.add_parser("points"); p.add_argument("--src", required=True); p.add_argument("--out", required=True)
p = sub.add_parser("score"); p.add_argument("--src", required=True); p.add_argument("--mask-dir", required=True); p.add_argument("--out", required=True)
p = sub.add_parser("check"); p.add_argument("--dir", required=True)
a = ap.parse_args(); {"climate": climate, "airtemp": airtemp, "align": align, "points": points, "score": score, "check": check}[a.cmd](a)
