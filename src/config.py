import os

# ----------------------------------------------------------------
# PATHS AND DIRECTORY SETUP
# ----------------------------------------------------------------
# Default base directories. Can be overridden.
# If running on Google Colab, mount drive first.
USE_COLAB_DEFAULTS = True

if USE_COLAB_DEFAULTS:
    DRIVE_BASE = '/content/drive/MyDrive'
    unclassified_paths = {
        'Aspect'      : f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Aspect_degree_10m_Kavrepalanchowk.tif',
        'Elevation'   : f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Elevation_m_10m_Kavrepalanchowk.tif',
        'Forest_Cover': f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Forest_Cover_10m_Kavrepalanchowk.tif',
        'NDVI'        : f'{DRIVE_BASE}/Kavrepalanchowk_5_Year_Average_NDVI_10m/Kavrepalanchowk_5_Year_Average_NDVI_10m.tif',
        'Rainfall'    : f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Rainfall_mm_10m_Kavrepalanchowk.tif',
        'Slope'       : f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Slope_degree_10m_Kavrepalanchowk.tif',
        'Temperature' : f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Temperature_C_10m_Kavrepalanchowk.tif',
    }
    classified_paths = {
        'River_Distance': f'{DRIVE_BASE}/Kavrepalanchowk_AHP_Only_10m/AHP_Distance_to_Rivers_1_9_10m_Kavrepalanchowk.tif',
        'Road_Distance' : f'{DRIVE_BASE}/Kavrepalanchowk_AHP_Only_10m/AHP_Distance_to_Roads_1_9_10m_Kavrepalanchowk.tif',
        'LULC'          : f'{DRIVE_BASE}/Kavrepalanchowk_AHP_LULC/AHP_LULC_2025_Beehive_Suitability_10m_Kavrepalanchowk.tif',
    }
    shapefile_path = f'{DRIVE_BASE}/Kavrepalanchowk_10m_Data/Kavre.shp'
else:
    # Local paths (users can place datasets relative to the project directory)
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', '1_criterion_data'))
    unclassified_paths = {
        'Aspect'      : os.path.join(DATA_DIR, 'Aspect_degree_10m_Kavrepalanchowk.tif'),
        'Elevation'   : os.path.join(DATA_DIR, 'Elevation_m_10m_Kavrepalanchowk.tif'),
        'Forest_Cover': os.path.join(DATA_DIR, 'Forest_Cover_10m_Kavrepalanchowk.tif'),
        'NDVI'        : os.path.join(DATA_DIR, 'Kavrepalanchowk_5_Year_Average_NDVI_10m.tif'),
        'Rainfall'    : os.path.join(DATA_DIR, 'Rainfall_mm_10m_Kavrepalanchowk.tif'),
        'Slope'       : os.path.join(DATA_DIR, 'Slope_degree_10m_Kavrepalanchowk.tif'),
        'Temperature' : os.path.join(DATA_DIR, 'Temperature_C_10m_Kavrepalanchowk.tif'),
    }
    classified_paths = {
        'River_Distance': os.path.join(DATA_DIR, 'AHP_Distance_to_Rivers_1_9_10m_Kavrepalanchowk.tif'),
        'Road_Distance' : os.path.join(DATA_DIR, 'AHP_Distance_to_Roads_1_9_10m_Kavrepalanchowk.tif'),
        'LULC'          : os.path.join(DATA_DIR, 'AHP_LULC_2025_Beehive_Suitability_10m_Kavrepalanchowk.tif'),
    }
    shapefile_path = os.path.join(DATA_DIR, 'Kavre.shp')

# ----------------------------------------------------------------
# AHP WEIGHTS (Consistency Ratio CR = 0.0325 < 0.10 ✓)
# ----------------------------------------------------------------
weights = {
    'LULC'          : 0.2756,
    'NDVI'          : 0.1941,
    'Forest_Cover'  : 0.1548,
    'Temperature'   : 0.1147,
    'Rainfall'      : 0.0822,
    'River_Distance': 0.0593,
    'Elevation'     : 0.0445,
    'Slope'         : 0.0332,
    'Aspect'        : 0.0238,
    'Road_Distance' : 0.0177,
}

# ----------------------------------------------------------------
# CLASSIFICATION PARAMETERS
# ----------------------------------------------------------------
# Rainfall equal-interval bounds
R_MIN, R_MAX = 1292.4529, 1478.8181
R_STEP       = (R_MAX - R_MIN) / 9

# Temperature equal-interval bounds
T_MIN, T_MAX = 18.6620, 22.7357
T_STEP       = (T_MAX - T_MIN) / 9

# Final 5-Class suitability map settings
labels = {1: 'Very Low', 2: 'Low', 3: 'Moderate', 4: 'High', 5: 'Very High'}
cat_colors = ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']
PIXEL_AREA_M2 = 100

# ----------------------------------------------------------------
# VALIDATION DATASET
# ----------------------------------------------------------------
validation_data = {
    'No': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Place_Organization': [
        'Mandandeupur',
        'Jyamdi',
        'Namobuddha',
        'Satpane Krishi Farm',
        'Shree Bhagwati Beekeeping Farmers Group',
        'Shrestha Furniture & Beehive Industry',
        'Sana Char Agriculture Cooperative',
        'Jagbaideshwar Beekeeping Women Farmers Group',
        'Sitaram Furniture & Bee Industry',
        'Dhungkharka / Dhunkharka'
    ],
    'Local_Level': [
        'Mandandeupur Municipality',
        'Mandandeupur / Jyamdi locality',
        'Namobuddha Municipality',
        'Chauri Deurali Rural Municipality',
        'Panchkhal Municipality',
        'Chauri Deurali Rural Municipality',
        'Namobuddha Municipality',
        'Namobuddha Municipality',
        'Panauti Municipality',
        'Bethanchowk Rural Municipality'
    ],
    'Latitude': [
        27.71450, 27.66652, 27.56213, 27.59140, 27.646809,
        27.59140, 27.56213, 27.56213, 27.585045, 27.52817
    ],
    'Longitude': [
        85.61480, 85.68000, 85.63795, 85.78390, 85.619863,
        85.78390, 85.63795, 85.63795, 85.516022, 85.47860
    ]
}
