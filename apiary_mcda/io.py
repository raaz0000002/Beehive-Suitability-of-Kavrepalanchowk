"""Read the standardised 1-9 rasters named in a weights config onto one common mask."""
import json, os, sys
import numpy as np, rasterio


def load_stack(config_path, include_scenario_layers=False):
    """Return (X, weights, mask, profile). X maps criterion -> 1-D float64 vector of valid cells.

    A cell is valid when every criterion is > 0 (0 = NoData). All rasters must share shape, transform and CRS."""
    cfg = json.load(open(config_path)); root = os.path.dirname(os.path.abspath(config_path))
    layers = dict(cfg["criteria"])
    if include_scenario_layers:
        layers.update(cfg.get("scenario_layers", {}))
    arrs, prof, mask = {}, None, None
    for k, v in layers.items():
        with rasterio.open(os.path.join(root, v["file"])) as r:
            a = r.read(1).astype("float64")
            if prof is None:
                prof = r.profile
            elif (r.height, r.width) != (prof["height"], prof["width"]) or r.transform != prof["transform"] or r.crs != prof["crs"]:
                sys.exit(f"{v['file']}: grid differs from the first raster")
        arrs[k] = a
        m = a > 0
        mask = m if mask is None else mask & m
    X = {k: a[mask] for k, a in arrs.items()}
    w = {k: float(v["weight"]) for k, v in cfg["criteria"].items()}
    s = sum(w.values()); w = {k: v / s for k, v in w.items()}
    return X, w, mask, prof
