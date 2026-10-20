# Data sources and licences

Most layers were built in Google Earth Engine (Gorelick et al., 2017) with the scripts in `gee/`, exported on one grid
(EPSG:32645, 10 m cells, 4,703 × 4,871 cells) and scored to 1–9 (`scripts/02_prep_layers.py`, Table 2 of the paper).
The climate layers are exported on their native grids by `gee/05_climate_1991_2020.js` (files in `raw/`) and resampled
bilinearly to the 10 m grid and scored by `scripts/02_prep_layers.py climate`.

| Layer | Product | Earth Engine ID / source | Period | Licence of the source | Citation |
|---|---|---|---|---|---|
| LULC | Esri Global LULC 10 m Time Series | `projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS` | 2024 | CC BY 4.0 | Esri (2025); Karra et al. (2021) |
| Air temperature (TEMP, `AIRT_1991_2020.tif`) | Mean of Mar–May and Sep–Nov; WorldClim V1 1960–1990 pattern + TerraClimate change 1961–1990 → 1991–2020 (additive, by month) | `WORLDCLIM/V1/MONTHLY`; `IDAHO_EPSCOR/TERRACLIMATE` | 1991–2020 normals | WorldClim terms of use; TerraClimate CC0 | Hijmans et al. (2005); Abatzoglou et al. (2018); Hay et al. (2000) |
| Precipitation (PREC, `PREC_1991_2020.tif`) | Annual total; WorldClim V1 pattern × TerraClimate change ratio (by month) | `WORLDCLIM/V1/MONTHLY`; `IDAHO_EPSCOR/TERRACLIMATE` | 1991–2020 normals | as above | as above |
| Climate, scenario (`AIRT_TC1991_2020.tif`, `PREC_TC1991_2020.tif`) | TerraClimate at native ~4 km | `IDAHO_EPSCOR/TERRACLIMATE` | 1991–2020 | CC0 | Abatzoglou et al. (2018) |
| Climate, scenario (`AIRT_WC1960_1990.tif`, `PREC_WC1960_1990.tif`) | WorldClim V1 (`gee/02_air_temperature.js`, `gee/04_precip_worldclim.js`) | `WORLDCLIM/V1/MONTHLY` | 1960–1990 normals | WorldClim terms of use | Hijmans et al. (2005) |
| Distance to stream (WATER) | MERIT Hydro, upstream area ≥ 1 km² | `MERIT/Hydro/v1_0_1` | static | Dual: CC BY-NC 4.0 or ODbL 1.0 | Yamazaki et al. (2019) |
| Elevation, slope, aspect | Copernicus DEM GLO-30 | `COPERNICUS/DEM/GLO30` | ~2011–2015 | Copernicus DEM licence (free, attribution required) | ESA (2022), https://doi.org/10.5270/ESA-c5d3d65 |
| Distance to road | OpenStreetMap via Geofabrik (`gis_osm_roads_free_1`, vehicular classes) | uploaded table asset | downloaded 15 October 2026 | ODbL 1.0 — derived rasters are shared under ODbL with attribution "© OpenStreetMap contributors" | OpenStreetMap contributors (2026) |
| Distance to stream, robustness run | OpenStreetMap waterways (`gis_osm_waterways_free_1`) | uploaded table asset | downloaded 15 October 2026 | ODbL 1.0 | OpenStreetMap contributors (2026) |
| NDVI (scenario only) | Sentinel-2 L2A median NDVI, SCL mask, ≤ 20% cloud | `COPERNICUS/S2_SR_HARMONIZED` | 2019–2023 | Copernicus free and open data licence | ESA (2015) |
| LST (scenario only) | MODIS MOD11A2 V061 day LST, QC-filtered | `MODIS/061/MOD11A2` | 2020–2024 | NASA LP DAAC, no restrictions | Wan et al. (2021) |
| District boundary (analysis) | GADM 4.1 level 3 (Kavrepalanchok) | `gadm41_NPL_3`, gadm.org | 2022 | **Not redistributable** (GADM licence) — not included; download from gadm.org | GADM (2022) |
| Boundaries for Figure 2 | Kavre district polygon (Survey Department of Nepal); geoBoundaries NPL ADM0–ADM3 | user-supplied; geoboundaries.org | 2019–2022 | Survey Department terms; geoBoundaries CC BY 3.0 IGO (ADM1) and CC BY-SA 4.0 (ADM3) | Survey Department (2022); Runfola et al. (2020) |
| Documented beekeeping locations | 7 publicly identifiable sites | Neupane et al. (2024); Limbu & Man Singh (2025); organizational records | — | Shared by the authors | paper Section 2.9 and Table 10 |
| Literature weights | 13 published apiary-suitability weight sets | `data/literature/evidence_weights.csv` (DOI of each study listed) | — | Numbers extracted from the cited papers | paper Table 3 |

## Full references

- Abatzoglou, J.T.; Dobrowski, S.Z.; Parks, S.A.; Hegewisch, K.C. (2018). TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958–2015. Scientific Data, 5, 170191. https://doi.org/10.1038/sdata.2017.191
- Esri. (2025). Esri global land use/land cover 10 m time series [Data set]. https://livingatlas.arcgis.com/landcoverexplorer/
- European Space Agency. (2015). Sentinel-2 user handbook (Issue 1, Rev. 2).
- European Space Agency. (2022). Copernicus DEM GLO-30 [Data set]. https://doi.org/10.5270/ESA-c5d3d65
- GADM. (2022). GADM database of global administrative areas, version 4.1 [Data set]. https://gadm.org
- Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
- Hay, L.E., Wilby, R.L., & Leavesley, G.H. (2000). A comparison of delta change and downscaled GCM scenarios for three mountainous basins in the United States. Journal of the American Water Resources Association, 36(2), 387–397. https://doi.org/10.1111/j.1752-1688.2000.tb04276.x
- Hijmans, R. J., Cameron, S. E., Parra, J. L., Jones, P. G., & Jarvis, A. (2005). Very high resolution interpolated climate surfaces for global land areas. International Journal of Climatology, 25(15), 1965–1978. https://doi.org/10.1002/joc.1276
- Karra, K., Kontgis, C., Statman-Weil, Z., Mazzariello, J. C., Mathis, M., & Brumby, S. P. (2021). Global land use/land cover with Sentinel 2 and deep learning. IGARSS 2021, 4704–4707. https://doi.org/10.1109/IGARSS47720.2021.9553499
- OpenStreetMap contributors. (2026). OpenStreetMap data extract for Nepal [Data set]. Geofabrik GmbH. https://download.geofabrik.de/asia/nepal.html (accessed 15 October 2026)
- Runfola, D., et al. (2020). geoBoundaries: A global database of political administrative boundaries. PLoS ONE, 15(4), e0231866. https://doi.org/10.1371/journal.pone.0231866
- Wan, Z., Hook, S., & Hulley, G. (2021). MODIS/Terra land surface temperature/emissivity 8-day L3 global 1km SIN grid V061 [Data set]. NASA EOSDIS LP DAAC. https://doi.org/10.5067/MODIS/MOD11A2.061
- Yamazaki, D., Ikeshima, D., Sosa, J., Bates, P. D., Allen, G. H., & Pavelsky, T. M. (2019). MERIT Hydro: A high-resolution global hydrography map based on latest topography dataset. Water Resources Research, 55(6), 5053–5073. https://doi.org/10.1029/2019WR024873

The licence column is a summary for planning the deposit, not legal advice; confirm each provider's current terms.
