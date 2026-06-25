# AHP Beehive Suitability Mapping — Kavrepalanchowk, Nepal

An end-to-end Python workflow utilizing **Analytical Hierarchy Process (AHP)** and **Weighted Overlay Analysis (WOA)** to evaluate and map spatial suitability for beehives (apiculture) at 10-meter resolution in Kavrepalanchowk District, Nepal.

---

## 📌 Project Overview

This repository hosts a multi-criteria GIS evaluation system that standardizes and overlaps **10 environmental, physical, and socio-economic criteria** to locate optimal beekeeping sites. The workflow handles projection alignments, raster standardizations, boundary masking, weighted overlay calculations, and ground-truth validation overlay.

### 📐 AHP Criteria and Weights ($CR = 0.0325$)
The pairwise comparison matrix yields a **Consistency Ratio (CR) of 0.0325**, which is well below the standard consistency threshold of $0.10$, indicating a highly consistent and mathematically valid criteria weighting.

| Rank | Criterion | Weight | Description / Sub-Class Rating Notes |
| :---: | :--- | :---: | :--- |
| **1** | **LULC** | **27.56%** | Land Use Land Cover (Agricultural/Forest zones highly favored) |
| **2** | **NDVI** | **19.41%** | Vegetation density and floral resources index (clipped to range: -0.3357 to 0.8905) |
| **3** | **Forest Cover** | **15.48%** | Percentage density of forest cover (scaled to 0-100%) |
| **4** | **Temperature** | **11.47%** | Equal-interval temperature classification (18.66°C to 22.74°C) |
| **5** | **Rainfall** | **8.22%** | Equal-interval average rainfall classification (1292.5 mm to 1478.8 mm) |
| **6** | **River Distance** | **5.93%** | Proximity to water sources (standardized 1 to 9 scale) |
| **7** | **Elevation** | **4.45%** | Altitude ranges (optimal elevation: 1000m - 1500m rated 9) |
| **8** | **Slope** | **3.32%** | Terrain slope angle (gentler slopes 0-5° rated 9) |
| **9** | **Aspect** | **2.38%** | Sun-facing direction (south/south-east aspects highly rated) |
| **10** | **Road Distance** | **1.77%** | Transport network proximity (standardized 1 to 9 scale) |

---

## 📂 Repository Structure

```text
AHP using python/
│
├── README.md                           # Project Documentation
├── AHP_Beehive_Suitability_Visible_Validation_Numbering_Code.ipynb # Original monolithic workflow
│
├── data/                               # Input & Output GIS files
│   ├── 1_criterion_data/               # Place raw input Geotiffs and Kavre.shp here
│   ├── 2_ahp_map/                      # Generated criterion maps (1-9 scales)
│   └── 3_validation_map/               # Final 5-Class map exports & validation logs
│
├── src/                                # Modular core Python scripts
│   ├── __init__.py
│   ├── config.py                       # Hardcoded constants, paths, validation points, & weights
│   ├── alignment.py                    # Spatial reprojections, alignments, and study area masks
│   ├── reclassification.py            # Reclassification engine (standardizing to 1-9 ratings)
│   ├── overlay.py                      # Multi-criteria weighted overlay calculations
│   └── validation_plot.py              # Unique validation site resolution and map plotting
│
└── notebooks/                          # Interactive divided notebooks for explanation
    ├── Part1_Setup_Alignment.ipynb     # Step 1: Loading, aligning, and masking datasets
    ├── Part2_Reclassification.ipynb    # Step 2: Running reclassification rules & distribution checks
    ├── Part3_Weighted_Overlay.ipynb    # Step 3: Computing suitability overlay & exporting GeoTIFFs
    └── Part4_Validation_Visualization.ipynb # Step 4: Validating map with ground-truth & plotting
```

---

## 🚀 Getting Started

### 📋 Prerequisites & Installation

To run this model on your local machine, install the required geospatial and plotting packages:

```bash
pip install numpy pandas matplotlib rasterio geopandas
```

### ⚙️ How to Run

1. **Prepare Data**:
   Place all 10 criterion Geotiff layers and the Kavre District shapefile inside `data/1_criterion_data/` as guided in [data/1_criterion_data/README.md](file:///c:/Users/Dell/Desktop/AHP%20using%20python/data/1_criterion_data/README.md).
2. **Configure Run Mode**:
   Open `src/config.py` and set `USE_COLAB_DEFAULTS = False` if running locally, or `True` if using Google Drive directories on Google Colab.
3. **Execute Interactive Steps**:
   Open the notebooks inside `notebooks/` sequentially to run, visualize, and validate each part of the workflow.

---

## 🎯 Ground-Truth Map Validation & Renumbering

When rendering validation data points on a final suitability map, some locations share exactly the same coordinates (e.g., duplicate coordinate records from the same farm cluster), leading to overlapping label annotations on matplotlib. 

This workflow implements a **Unique Visible Map Locations Resolution**:
1. Merges points sharing the same coordinate pixel using `src/validation_plot.py`.
2. Renumbers the unique locations sequentially from `1` upwards.
3. Preserves original point numbers inside the exported validation CSV log files under the field name `Original_Point_Nos`.
