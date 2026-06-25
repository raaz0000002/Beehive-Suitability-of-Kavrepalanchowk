import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
from rasterio.features import rasterize
import geopandas as gpd

def load_aligned(template_path, source_path):
    """
    Loads and reprojects a source raster to match the spatial template raster (LULC).
    """
    with rasterio.open(template_path) as tgt:
        tmeta = tgt.meta.copy()
        with rasterio.open(source_path) as src:
            out = np.empty(
                (tmeta['height'], tmeta['width']),
                dtype=np.float32
            )
            reproject(
                source        = rasterio.band(src, 1),
                destination   = out,
                src_transform = src.transform,
                src_crs       = src.crs,
                dst_transform = tmeta['transform'],
                dst_crs       = tmeta['crs'],
                resampling    = Resampling.bilinear
            )
            if src.nodata is not None:
                out[out == src.nodata] = np.nan
            return out

def create_study_area_mask(shapefile_path, meta, data_stack):
    """
    Builds a boolean study area mask based on shapefile boundaries intersected
    with valid raster data cells.
    """
    # Load the shapefile
    gdf = gpd.read_file(shapefile_path)

    # Reproject shapefile to match raster's CRS
    if gdf.crs != meta['crs']:
        gdf = gdf.to_crs(meta['crs'])

    # Rasterize the shapefile boundary
    shapefile_mask_arr = rasterize(
        [(geom, 1) for geom in gdf.geometry.values],
        out_shape=(meta['height'], meta['width']),
        transform=meta['transform'],
        fill=0,
        all_touched=True,
        dtype=np.uint8
    )
    shapefile_mask = (shapefile_mask_arr == 1)

    # Base LULC mask
    LULC_raw = data_stack['LULC'].copy()
    study_area_mask_data = ~np.isnan(LULC_raw)

    # Check validity across terrain layers
    for name in ['Elevation', 'Slope', 'Aspect']:
        if name in data_stack:
            terrain_valid = ~np.isnan(data_stack[name])
            study_area_mask_data = study_area_mask_data | terrain_valid

    # Intersection of shapefile and raster data mask
    study_area_mask = study_area_mask_data & shapefile_mask
    return study_area_mask
