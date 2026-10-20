# How the results were tested

The suitability map was checked in four independent ways. All numbers below are produced by `reproduce.sh` and
checked automatically by `scripts/06_verify.py` against `results/expected_results.json` (45 checks).

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
| WLC | 86.98% | — | — | — |
| WPM | 56.68% | 57.90% | 0.519 | 0.9205 |
| TOPSIS | 89.45% | 84.00% | 0.744 | 0.9254 |

All three models give the same class on 51.49% of cells. At the seven documented beekeeping locations, WLC and TOPSIS
place 2 of 7 in High or Very High and WPM places 1 of 7. The seven locations are a small, non-random set, so this is
reported as a descriptive overlay only; no statistical test is applied.

## 2. Independent recomputation of the main score

`scripts/03_run_main.py` writes the main score. `scripts/04_compare_models.py` reads the same rasters through separate code
(`apiary_mcda.io.load_stack` + `apiary_mcda.models.wlc`) and compares the two cell by cell over 13,926,106 cells:
maximum absolute difference 0.0 and 0 cells with a different class. Both run in float64, which avoids rounding
artefacts for scores that fall exactly on a class break.

## 3. Unit tests

`tests/test_models.py` (pytest, 12 tests) checks each model against hand-calculated values, that a cell scoring v on every
criterion returns v, that all scores stay in 1–9 and rise when any criterion rises, that WPM ≤ WLC (AM–GM inequality),
the class-break edges, and the weighted kappa.

## 4. Sensitivity, classification and input checks

- 81 scenarios (±10/20/30% one-at-a-time; removing each criterion and both climate criteria together; 90% bootstrap
  bounds; equal, ROC and author AHP weights; NDVI split; LST in place of air temperature; TerraClimate 1991–2020 at
  ~4 km and WorldClim 1960–1990 in place of the main climate layers) — `results/main/scenarios.csv`.
- Removing both climate criteria changes 31.18% of cells (κw 0.606, ρ 0.946); WorldClim 1960–1990 normals change
  0.59% (κw 0.988); TerraClimate at ~4 km changes 7.42% (κw 0.844).
- Three classification methods — `results/main/classification_methods.csv`.
- A second full run with OpenStreetMap waterways instead of MERIT Hydro (`results/osm_water/`): High + Very High 84.68%,
  90.75% of cells in the same class, no documented location changes class.
- Climate resampling check: scoring the WorldClim 1960–1990 export locally (`02_prep_layers.py climate`) reproduces the
  Earth Engine-resampled scores in 99.7% (temperature) and 99.6% (precipitation) of cells; the rest differ by one unit.
- 500 m neighbourhood statistics of the documented locations — `results/main/points_500m.csv` (`07_point_context.py`).
- The pooled weights are recomputed from the study table by `scripts/01_pool_weights.py` (13 studies, 4,996 valid
  bootstrap draws, seed 1).
- Every run's `manifest.json` records the SHA-256 hash of each input raster.
