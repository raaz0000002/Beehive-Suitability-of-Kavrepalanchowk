# 1. Criterion Data Folder

Place your input GIS files in this directory when running locally.

### Required Datasets

#### Unclassified Continuous Rasters (10m Resolution)
1. **Aspect**: `Aspect_degree_10m_Kavrepalanchowk.tif` (Aspect in degrees)
2. **Elevation**: `Elevation_m_10m_Kavrepalanchowk.tif` (Elevation in meters)
3. **Forest Cover**: `Forest_Cover_10m_Kavrepalanchowk.tif` (Forest cover proportion)
4. **NDVI**: `Kavrepalanchowk_5_Year_Average_NDVI_10m.tif` (5-year average NDVI index)
5. **Rainfall**: `Rainfall_mm_10m_Kavrepalanchowk.tif` (Rainfall in mm)
6. **Slope**: `Slope_degree_10m_Kavrepalanchowk.tif` (Slope in degrees)
7. **Temperature**: `Temperature_C_10m_Kavrepalanchowk.tif` (Temperature in °C)

#### Pre-classified Categorical Rasters (1 to 9 standardization scale)
8. **River Distance**: `AHP_Distance_to_Rivers_1_9_10m_Kavrepalanchowk.tif`
9. **Road Distance**: `AHP_Distance_to_Roads_1_9_10m_Kavrepalanchowk.tif`
10. **LULC (Land Use / Land Cover)**: `AHP_LULC_2025_Beehive_Suitability_10m_Kavrepalanchowk.tif` (Also serves as spatial extent template)

#### Administrative District Boundary Vector
- **Kavrepalanchowk District Boundary**: `Kavre.shp` (along with its matching `.dbf`, `.shx`, `.prj` files)
