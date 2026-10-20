# Data sources and licences

Every layer was built in Google Earth Engine (Gorelick et al., 2017) with the scripts in `gee/`, exported on one grid
(EPSG:32645, 10 m cells, 4,703 × 4,871 cells) and scored to 1–9 (`scripts/02_prep_layers.py`, Table 2 of the paper).

| Layer | Product | Earth Engine ID / source | Period | Licence of the source (check before deposit) | Citation |
|---|---|---|---|---|---|
| LULC | Esri Global LULC 10 m Time Series | `projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS` | 2024 | CC BY 4.0 | Esri (2025); Karra et al. (2021) |
| Air temperature (TEMP) | WorldClim V1 monthly mean temperature, Mar–May and Sep–Nov | `WORLDCLIM/V1/MONTHLY` | 1960–1990 normals | WorldClim terms of use (free for research; see worldclim.org) | Hijmans et al. (2005) |
| Precipitation (PREC) | WorldClim V1 monthly precipitation, sum of 12 months (`gee/04_precip_worldclim.js`) | `WORLDCLIM/V1/MONTHLY` | 1960–1990 normals | WorldClim terms of use (free for research; see worldclim.org) | Hijmans et al. (2005) |
| Precipitation, sensitivity run (PREC_CHIRPS) | CHIRPS daily, annual totals averaged | `UCSB-CHG/CHIRPS/DAILY` | 2020–2024 | Public domain (Climate Hazards Center) | Funk et al. (2015) |
| Distance to stream (WATER) | MERIT Hydro, upstream area ≥ 1 km² | `MERIT/Hydro/v1_0_1` | static | Dual: CC BY-NC 4.0 or ODbL 1.0 | Yamazaki et al. (2019) |
| Elevation, slope, aspect | Copernicus DEM GLO-30 | `COPERNICUS/DEM/GLO30` | ~2011–2015 | Copernicus DEM licence (free, attribution required) | ESA (2022), https://doi.org/10.5270/ESA-c5d3d65 |
| Distance to road | OpenStreetMap via Geofabrik (`gis_osm_roads_free_1`, vehicular classes) | uploaded table asset | **[download date]** | ODbL 1.0 — derived rasters must be shared under ODbL with attribution "© OpenStreetMap contributors" | OpenStreetMap contributors (2026) |
| Distance to stream, robustness run | OpenStreetMap waterways (`gis_osm_waterways_free_1`) | uploaded table asset | **[download date]** | ODbL 1.0 | OpenStreetMap contributors (2026) |
| NDVI (scenario only) | Sentinel-2 L2A median NDVI, SCL mask, ≤ 20% cloud | `COPERNICUS/S2_SR_HARMONIZED` | 2019–2023 | Copernicus free and open data licence | ESA (2015) |
| LST (scenario only) | MODIS MOD11A2 V061 day LST, QC-filtered | `MODIS/061/MOD11A2` | 2020–2024 | NASA LP DAAC, no restrictions | Wan et al. (2021) |
| District boundary | GADM 4.1 level 3 (Kavrepalanchok) | `gadm41_NPL_3`, gadm.org | 2022 | **Not redistributable** (GADM licence) — not included; download from gadm.org | GADM (2022) |
| Apiary locations | 7 documented beekeeping sites | Neupane et al. (2024); Limbu & Man Singh (2025); field records | — | Shared by the authors | see paper Section 3.8 |
| Literature weights | 13 published apiary-suitability weight sets | `data/literature/evidence_weights.csv` (DOI of each study listed) | — | Numbers extracted from the cited papers | paper Table 3 |

## Full references

- Esri. (2025). Esri global land use/land cover 10 m time series [Data set]. https://livingatlas.arcgis.com/landcoverexplorer/
- European Space Agency. (2015). Sentinel-2 user handbook (Issue 1, Rev. 2).
- European Space Agency. (2022). Copernicus DEM GLO-30 [Data set]. https://doi.org/10.5270/ESA-c5d3d65
- Funk, C., Peterson, P., Landsfeld, M., Pedreros, D., Verdin, J., Shukla, S., Husak, G., Rowland, J., Harrison, L., Hoell, A., & Michaelsen, J. (2015). The climate hazards infrared precipitation with stations—A new environmental record for monitoring extremes. Scientific Data, 2, 150066. https://doi.org/10.1038/sdata.2015.66
- GADM. (2022). GADM database of global administrative areas, version 4.1 [Data set]. https://gadm.org
- Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
- Hijmans, R. J., Cameron, S. E., Parra, J. L., Jones, P. G., & Jarvis, A. (2005). Very high resolution interpolated climate surfaces for global land areas. International Journal of Climatology, 25(15), 1965–1978. https://doi.org/10.1002/joc.1276
- Karra, K., Kontgis, C., Statman-Weil, Z., Mazzariello, J. C., Mathis, M., & Brumby, S. P. (2021). Global land use/land cover with Sentinel 2 and deep learning. IGARSS 2021, 4704–4707. https://doi.org/10.1109/IGARSS47720.2021.9553499
- OpenStreetMap contributors. (2026). OpenStreetMap data extract for Nepal [Data set]. Geofabrik GmbH. https://download.geofabrik.de/asia/nepal.html [accessed: **download date**]
- Wan, Z., Hook, S., & Hulley, G. (2021). MODIS/Terra land surface temperature/emissivity 8-day L3 global 1km SIN grid V061 [Data set]. NASA EOSDIS LP DAAC. https://doi.org/10.5067/MODIS/MOD11A2.061
- Yamazaki, D., Ikeshima, D., Sosa, J., Bates, P. D., Allen, G. H., & Pavelsky, T. M. (2019). MERIT Hydro: A high-resolution global hydrography map based on latest topography dataset. Water Resources Research, 55(6), 5053–5073. https://doi.org/10.1029/2019WR024873

The licence column is a summary for planning the deposit, not legal advice; confirm each provider's current terms.
