# Landscape suitability for *Apis cerana* beekeeping in Kavrepalanchowk, Nepal

Code and data for the paper **"Mapping Relative Landscape Suitability for *Apis cerana* Beekeeping in Nepal's Mid-Hills:
Literature-Pooled Weights and Sensitivity Analysis"** (R. Acharya, U. Basnet, A. Akwemoh, I. Familusi, S. Adhikari and
B. Gyawali; submitted to *Agriculture*, MDPI).

A GIS multi-criteria model of eight criteria on one 10 m grid (13,926,106 cells; 1,392.61 km²), with criterion weights
pooled from 13 published apiary-suitability studies and 1991–2020 climate normals. The output is a relative
landscape-suitability index for planning within the district, not a prediction of apiary presence or productivity.

| Result | Value |
|---|---|
| High + Very High relative suitability (WLC) | 86.98% (1,211.26 km²) |
| Same class in ≥ 90% of 81 sensitivity scenarios | 83.3% of the district |
| Agreement with WLC: TOPSIS / WPM | 84.00% (κw 0.744) / 57.90% (κw 0.519) |
| Both climate criteria removed | 31.18% of cells change class; Spearman ρ 0.946 |
| WorldClim 1960–1990 instead of 1991–2020 climate | 0.59% of cells change class |
| Documented beekeeping locations in High/Very High (descriptive overlay, no test) | 2 of 7 (WLC, TOPSIS); 1 of 7 (WPM) |

## Repository layout

```
apiary_mcda/            Python package
  models/wlc.py         weighted linear combination (main model)
  models/wpm.py         weighted product model
  models/topsis.py      TOPSIS with fixed ideal (9) and anti-ideal (1)
  classify.py           fixed 1-9 class breaks, weighted kappa
  io.py                 load standardised rasters on one mask
scripts/
  01_pool_weights.py    pool published weights (log-linear model, bootstrap, leave-one-out)
  02_prep_layers.py     align and score raw layers to 1-9 (incl. `climate` for the Earth Engine climate exports)
  03_run_main.py        main WLC run, 81 sensitivity scenarios, stability, class areas, manifest
  04_compare_models.py  independent WLC recompute + WPM + TOPSIS comparison
  05_make_figures.py    Figures 4-10 (maps and charts)
  05b_make_flowchart.py Figure 3 (workflow)
  05c_location_map.py   Figure 2 (study area; needs boundary files that are not redistributed here)
  06_verify.py          checks a fresh run against results/expected_results.json
  07_point_context.py   500 m neighbourhood statistics of the documented beekeeping locations
gee/                    Google Earth Engine scripts that build every layer (05_climate_1991_2020.js = climate)
config/                 weights and file lists (main run: MERIT Hydro streams; robustness run: OSM waterways)
data/standardised/      1-9 criterion rasters, EPSG:32645, 10 m (0 or -9999 = NoData)
                        AIRT_1991_2020 / PREC_1991_2020 = main climate criteria; *_TC1991_2020 = TerraClimate ~4 km
                        and *_WC1960_1990 = WorldClim 1960-1990 (sensitivity scenarios only)
raw/                    climate exports from gee/05_climate_1991_2020.js on their native grids
data/points/            documented beekeeping locations (UTM 45N and lat/lon)
data/literature/        study-by-study weights used for pooling (evidence_weights.csv) and the reading list of
                        candidate studies from the literature search (Apiary_Literature_Reading_List.xlsx)
tests/                  unit tests for the three models and the classifier
docs/                   data sources and licences; model testing
results/                expected numbers; reproduce.sh writes all outputs here
```

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./reproduce.sh            # about 8 GB RAM; writes results/ and results/figures/, then runs the tests and the checks
```

`reproduce.sh` ends with `scripts/06_verify.py`, which prints PASS/FAIL for every reported number (45 checks).
To rebuild the input rasters from the original public data, run the scripts in `gee/` in the Earth Engine code
editor (set your own asset IDs first), then score them with `scripts/02_prep_layers.py`, for example

```bash
python scripts/02_prep_layers.py climate --src raw/clim_1991_2020_main_wcgrid.tif --template data/standardised/LULC.tif \
       --mask-config config/weights_main.json --tag 1991_2020 --out-dir data/standardised --raw-dir raw
```

## Data

The standardised rasters and the small climate exports are included here. The raw input layers are archived on Zenodo
(version 1.0.0, https://doi.org/10.5281/zenodo.23490045) and the 10 m climate layers, all output rasters and tables and a
code snapshot in version 2 (https://doi.org/10.5281/zenodo.23491480). Sources and licences: [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
The district boundary used for the analysis (GADM 4.1) is not redistributed; download it from https://gadm.org.

## Citation

See `CITATION.cff`. Please cite the paper and the Zenodo archive.

## Licence

Code: MIT (see `LICENSE`). Data in `data/`: see `docs/DATA_SOURCES.md`; the road and OSM-water rasters are derived from
OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0).
