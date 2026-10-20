# How the results were tested

The suitability map was checked in four independent ways. All numbers below are produced by `reproduce.sh` and
checked automatically by `scripts/06_verify.py` against `results/expected_results.json`.

## 1. Three aggregation models

The same eight standardised criteria (1–9) and the same pooled weights were combined with three models, each in its own
module under `apiary_mcda/models/`:

| Model | Formula | Character |
|---|---|---|
| **WLC** (main) | S = Σ wᵢ xᵢ | fully compensatory |
| **WPM** (weighted product) | S = Π xᵢ^wᵢ | weighted geometric mean; a low score on any criterion pulls the result down |
| **TOPSIS** | S = 1 + 8·d⁻/(d⁺ + d⁻), with vᵢ = wᵢ(xᵢ − 1)/8, ideal = all 9, anti-ideal = all 1 | distance to fixed ideal / anti-ideal |

All three are classified with the same fixed breaks (1, 2.6, 4.2, 5.8, 7.4, 9; upper bound inclusive).

| Model | High + Very High | Agreement with WLC | Weighted κ | Spearman ρ |
|---|---|---|---|---|
| WLC | 87.08% | — | — | — |
| WPM | 56.73% | 57.93% | 0.518 | 0.9199 |
| TOPSIS | 89.46% | 84.24% | 0.747 | 0.9258 |

All three models give the same class on 51.65% of cells. At the seven documented apiaries, WLC and TOPSIS place 2 of 7 in
High or Very High and WPM places 1 of 7. The seven locations are a small, non-random set, so this is reported as a
descriptive overlay only; no statistical test is applied.

## 2. Independent recomputation of the main score

`scripts/03_run_main.py` writes the main score. `scripts/04_compare_models.py` reads the same rasters through separate code
(`apiary_mcda.io.load_stack` + `apiary_mcda.models.wlc`) and compares the two cell by cell over 13,926,106 cells:
maximum absolute difference 0.0 and 0 cells with a different class. Both run in float64; an earlier float32 run moved
5,814 cells that sit exactly on a class break, which is why double precision is required.

## 3. Unit tests

`tests/test_models.py` (pytest, 12 tests) checks each model against hand-calculated values, that a cell scoring v on every
criterion returns v, that all scores stay in 1–9 and rise when any criterion rises, that WPM ≤ WLC (AM–GM inequality),
the class-break edges, and the weighted kappa.

## 4. Sensitivity, classification and input checks

- 78 weight scenarios (±10/20/30% one-at-a-time, removing each criterion, 90% bootstrap bounds, equal weights, ROC weights,
  previous AHP weights, NDVI split, LST in place of air temperature) — `results/main/scenarios.csv`.
- Three classification methods — `results/main/classification_methods.csv`.
- A second full run with OpenStreetMap waterways instead of MERIT Hydro (`results/osm_water/`): High + Very High 84.77%,
  no apiary changes class.
- A precipitation sensitivity run with CHIRPS 2020–2024 (`data/standardised/PREC_CHIRPS.tif`) in place of the WorldClim
  normals: High + Very High 88.34%, 85.59% of cells in the same class (κ 0.729).
- The pooled weights are recomputed from the study table by `scripts/01_pool_weights.py` (13 studies, 4,996 valid
  bootstrap draws, seed 1).
- Every run's `manifest.json` records the SHA-256 hash of each input raster.
