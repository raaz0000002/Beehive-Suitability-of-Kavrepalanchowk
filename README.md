# Apiary-site suitability for *Apis cerana* in Kavrepalanchowk, Nepal

Code and data for the paper **"[Manuscript title]"** ([Authors], submitted to *Agriculture*, MDPI).
A GIS multi-criteria model of eight criteria on one 10 m grid (13,926,106 cells; 1,392.61 km²), with criterion weights
pooled from 13 published apiary-suitability studies. The output is a relative landscape-suitability index for
planning within the district, not a prediction of apiary presence or productivity.

**Tested with three aggregation models.** The main weighted linear combination (WLC) was recomputed independently
(0 cells differ) and compared with a weighted product model (WPM) and TOPSIS, all with the same criteria and weights.
See [docs/MODEL_TESTING.md](docs/MODEL_TESTING.md).

| Result | Value |
|---|---|
| High + Very High relative suitability (WLC) | 87.08% (1,212.62 km²) |
| Same class in ≥ 90% of 78 weight scenarios | 82.5% of the district |
| Agreement with WLC: TOPSIS / WPM | 84.24% (κ 0.747) / 57.93% (κ 0.518) |
| Documented apiaries in High/Very High (descriptive overlay, no test) | 2 of 7 (WLC, TOPSIS); 1 of 7 (WPM) |

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
  02_prep_layers.py     align and score raw layers to 1-9; convert apiary coordinates
  03_run_main.py        main WLC run, 78 sensitivity scenarios, stability, class areas, manifest
  04_compare_models.py  independent WLC recompute + WPM + TOPSIS comparison
  05_make_figures.py    Figures 4-10 (maps and charts)
  05b_make_flowchart.py Figure 3 (workflow)
  06_verify.py          checks a fresh run against results/expected_results.json
gee/                    Google Earth Engine scripts that build every layer
config/                 weights and file lists (main run: MERIT Hydro streams; robustness run: OSM waterways)
data/standardised/      1-9 criterion rasters, EPSG:32645, 10 m (0 = NoData); PREC = WorldClim 1960-1990,
                        PREC_CHIRPS = CHIRPS 2020-2024 (precipitation sensitivity run only)
data/points/            documented apiary locations (UTM 45N and lat/lon)
data/literature/        study-by-study weights used for pooling
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

`reproduce.sh` ends with `scripts/06_verify.py`, which prints PASS/FAIL for every reported number.
To rebuild the input rasters from the original public data, run the scripts in `gee/` in the Earth Engine code
editor (set your own asset IDs first), then score them with `scripts/02_prep_layers.py`.

## Data

The standardised rasters are included here. The raw continuous layers, the stream-distance raster and all output rasters
are archived on Zenodo: **[Zenodo DOI]**. Sources and licences: [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
The district boundary (GADM 4.1) is not redistributed; download it from https://gadm.org.

## Citation

See `CITATION.cff`. Please cite the paper and the Zenodo archive.

## Licence

Code: MIT (see `LICENSE`). Data in `data/`: see `docs/DATA_SOURCES.md`; the road and OSM-water rasters are derived from
OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0).
