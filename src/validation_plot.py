import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from copy import copy
from rasterio.transform import rowcol

def apply_study_mask(arr_float, study_area_mask):
    """
    Sets all pixels outside the study area boundary to NaN for transparency.
    """
    masked = arr_float.copy()
    masked[~study_area_mask] = np.nan
    masked[study_area_mask & (masked == 0)] = np.nan
    return masked

def make_masked_cmap(base_cmap):
    """
    Returns copy of base_cmap with NaN color set to transparent.
    """
    cmap_copy = copy(base_cmap)
    cmap_copy.set_bad(color='white', alpha=0.0)
    return cmap_copy

def make_masked_cat_cmap(colors_list):
    """
    ListedColormap for categorical maps with transparent NaN.
    """
    cmap = mcolors.ListedColormap(colors_list)
    cmap.set_bad(color='white', alpha=0.0)
    return cmap

def add_north_arrow(ax, x=0.975, y=0.975, size=15, color='black'):
    """
    Adds a north arrow to the matplotlib axes.
    """
    ax.text(
        x, y, 'N',
        transform=ax.transAxes,
        fontsize=size,
        color=color,
        ha='center',
        va='top',
        fontweight='bold',
        zorder=60,
        clip_on=False,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.50, pad=0.20)
    )
    ax.annotate(
        '',
        xy=(x, y - 0.055),
        xytext=(x, y - 0.125),
        xycoords=ax.transAxes,
        arrowprops=dict(
            facecolor=color,
            edgecolor=color,
            width=1.8,
            headwidth=8,
            headlength=9,
            shrink=0
        ),
        zorder=60,
        clip_on=False
    )

def add_text_scale_bar(
    ax,
    x=0.045,
    y=0.040,
    width=0.090,
    tick_height=0.012,
    fontsize=7,
    color='black',
    label='Scale: 1 cm = 3 km'
):
    """
    Adds a graphical text scale bar (0 - 1.5 - 3 km).
    """
    half_width = width / 2.0
    y_line = y + 0.022

    ax.text(
        x + width / 2.0,
        y_line + 0.018,
        label,
        transform=ax.transAxes,
        fontsize=fontsize,
        ha='center',
        va='bottom',
        color=color,
        fontweight='bold',
        zorder=55,
        clip_on=False,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.55, pad=0.4)
    )

    ax.plot(
        [x, x + width],
        [y_line, y_line],
        transform=ax.transAxes,
        color=color,
        linewidth=1.4,
        solid_capstyle='butt',
        zorder=55,
        clip_on=False
    )

    ax.plot(
        [x + half_width, x + half_width],
        [y_line - tick_height / 2, y_line + tick_height / 2],
        transform=ax.transAxes,
        color=color,
        linewidth=1.0,
        zorder=56,
        clip_on=False
    )

    for tx in [x, x + width]:
        ax.plot(
            [tx, tx],
            [y_line - tick_height / 2, y_line + tick_height / 2],
            transform=ax.transAxes,
            color=color,
            linewidth=1.0,
            zorder=56,
            clip_on=False
        )

    ax.text(
        x, y_line - 0.010, '0',
        transform=ax.transAxes, fontsize=fontsize - 1,
        ha='center', va='top', color=color, zorder=56, clip_on=False,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.45, pad=0.2)
    )
    ax.text(
        x + half_width, y_line - 0.010, '1.5',
        transform=ax.transAxes, fontsize=fontsize - 1,
        ha='center', va='top', color=color, zorder=56, clip_on=False,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.45, pad=0.2)
    )
    ax.text(
        x + width, y_line - 0.010, '3 km',
        transform=ax.transAxes, fontsize=fontsize - 1,
        ha='center', va='top', color=color, zorder=56, clip_on=False,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.45, pad=0.2)
    )

def process_validation_points(validation_data, meta, study_area_mask, final_cat):
    """
    Aligns and reprojects validation points, extracts suitability at coordinates,
    and groups duplicate locations to prevent numbering overlay issues.
    """
    df = pd.DataFrame(validation_data)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
        crs='EPSG:4326'
    )
    gdf = gdf.to_crs(meta['crs'])

    # Convert map coordinates to raster pixel indices
    gdf['col'], gdf['row'] = zip(*gdf.geometry.apply(
        lambda geom: rowcol(meta['transform'], geom.x, geom.y)[::-1]
    ))

    # Keep only those inside raster boundaries
    height, width = final_cat.shape
    gdf['inside_raster'] = (
        (gdf['row'] >= 0) & (gdf['row'] < height) &
        (gdf['col'] >= 0) & (gdf['col'] < width)
    )
    
    gdf_inside = gdf[gdf['inside_raster']].copy()
    
    # Extract suitability class
    def get_val(r):
        row_idx, col_idx = int(r['row']), int(r['col'])
        return int(final_cat[row_idx, col_idx])
        
    gdf_inside['Suitability_Class_ID'] = gdf_inside.apply(get_val, axis=1)
    gdf_inside['Suitability_Class'] = gdf_inside['Suitability_Class_ID'].map({
        0: 'NoData / Outside Boundary',
        1: 'Very Low',
        2: 'Low',
        3: 'Moderate',
        4: 'High',
        5: 'Very High'
    })

    # Check visibility
    def is_visible(r):
        row_idx, col_idx = int(r['row']), int(r['col'])
        return bool(study_area_mask[row_idx, col_idx] and final_cat[row_idx, col_idx] > 0)
        
    gdf_inside['Visible_On_Map'] = gdf_inside.apply(is_visible, axis=1)
    
    gdf_visible = gdf_inside[gdf_inside['Visible_On_Map']].copy()
    gdf_visible['plot_row'] = gdf_visible['row'].astype(int)
    gdf_visible['plot_col'] = gdf_visible['col'].astype(int)

    def join_unique(values, sep=' / '):
        seen = []
        for value in values:
            text = str(value)
            if text not in seen:
                seen.append(text)
        return sep.join(seen)

    # Group overlapping points
    gdf_plot = (
        gdf_visible
        .groupby(['plot_row', 'plot_col'], as_index=False, sort=False)
        .agg(
            Original_Point_Nos=('No', lambda x: ', '.join(map(str, x))),
            Place_Organization=('Place_Organization', join_unique),
            Local_Level=('Local_Level', join_unique),
            Latitude=('Latitude', 'mean'),
            Longitude=('Longitude', 'mean'),
            Suitability_Class_ID=('Suitability_Class_ID', 'first'),
            Suitability_Class=('Suitability_Class', 'first')
        )
    )
    gdf_plot['Display_No'] = np.arange(1, len(gdf_plot) + 1)
    
    return gdf_inside, gdf_plot
