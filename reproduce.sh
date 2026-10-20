#!/usr/bin/env bash
# Reproduce every number, table and figure in the paper from the standardised rasters in data/standardised.
# Needs Python 3.10+ and the packages in requirements.txt; about 8 GB RAM; roughly 10-20 minutes.
set -euo pipefail
cd "$(dirname "$0")"
python scripts/01_pool_weights.py
python scripts/03_run_main.py --config config/weights_main_merit.json --points data/points/apiaries_utm45n.csv --out results/main
python scripts/04_compare_models.py --config config/weights_main_merit.json --main-score results/main/score.tif \
       --points data/points/apiaries_utm45n.csv --out results/model_comparison
python scripts/03_run_main.py --config config/weights_osm_water.json --points data/points/apiaries_utm45n.csv --out results/osm_water
python scripts/05_make_figures.py --std data/standardised --run results/main --models results/model_comparison \
       --config config/weights_main_merit.json --out results/figures
python scripts/05b_make_flowchart.py results/figures
python -m pytest -q tests
python scripts/06_verify.py
