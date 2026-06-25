import numpy as np
from src.config import R_MIN, R_STEP, T_MIN, T_STEP

def reclassify(arr, name):
    """
    Reclassifies input continuous rasters into classes 1 to 9 based on beehive suitability rules.
    Returns uint8 array with values from 1-9 (0 represents NoData/masked values).
    """
    valid = ~np.isnan(arr)
    v     = np.where(valid, arr, 0.0)
    out   = np.ones(arr.shape, dtype=np.uint8)

    if name == 'Elevation':
        out[valid & (v >= 1000) & (v <= 1500)] = 9
        out[valid & (v >  1500) & (v <= 2000)] = 8
        out[valid & (v >=  800) & (v <  1000)] = 7
        out[valid & (v >  2000) & (v <= 2500)] = 6
        out[valid & (v >=  600) & (v <   800)] = 5
        out[valid & (v >  2500) & (v <= 2930)] = 4
        out[valid & (v >=  400) & (v <   600)] = 3
        out[valid & (v >=  200) & (v <   400)] = 2
        out[valid & (v >=    0) & (v <   200)] = 1

    elif name == 'Slope':
        out[valid & (v >=  0) & (v <=  5)] = 9
        out[valid & (v >   5) & (v <= 10)] = 8
        out[valid & (v >  10) & (v <= 15)] = 7
        out[valid & (v >  15) & (v <= 20)] = 6
        out[valid & (v >  20) & (v <= 25)] = 5
        out[valid & (v >  25) & (v <= 30)] = 4
        out[valid & (v >  30) & (v <= 40)] = 3
        out[valid & (v >  40) & (v <= 55)] = 2
        out[valid & (v >  55)             ] = 1

    elif name == 'Aspect':
        out[valid & (v >= 157.5) & (v <= 202.5)] = 9
        out[valid & ((v >= 112.5) & (v < 157.5) | (v > 202.5) & (v <= 247.5))] = 8
        out[valid & ((v >=  67.5) & (v < 112.5) | (v > 247.5) & (v <= 292.5))] = 7
        out[valid & ((v >=  22.5) & (v <  67.5) | (v > 292.5) & (v <= 337.5))] = 6
        out[valid & ((v <   22.5) | (v >  337.5))] = 5
        out[valid & (v == -1)                     ] = 4

    elif name == 'NDVI':
        out[valid & (v >=  0.70) & (v <= 0.8905)] = 9
        out[valid & (v >=  0.55) & (v <  0.70)  ] = 8
        out[valid & (v >=  0.40) & (v <  0.55)  ] = 7
        out[valid & (v >=  0.25) & (v <  0.40)  ] = 6
        out[valid & (v >=  0.10) & (v <  0.25)  ] = 5
        out[valid & (v >=  0.00) & (v <  0.10)  ] = 4
        out[valid & (v >= -0.10) & (v <  0.00)  ] = 3
        out[valid & (v >= -0.20) & (v < -0.10)  ] = 2
        out[valid & (v >= -0.3357) & (v < -0.20)] = 1

    elif name == 'Forest_Cover':
        out[valid & (v >  70)             ] = 9
        out[valid & (v >  60) & (v <= 70) ] = 8
        out[valid & (v >  50) & (v <= 60) ] = 7
        out[valid & (v >  40) & (v <= 50) ] = 6
        out[valid & (v >  30) & (v <= 40) ] = 5
        out[valid & (v >  20) & (v <= 30) ] = 4
        out[valid & (v >  10) & (v <= 20) ] = 3
        out[valid & (v >   5) & (v <= 10) ] = 2
        out[valid & (v >=  0) & (v <=  5) ] = 1

    elif name == 'Rainfall':
        out[valid & (v >= R_MIN + 8*R_STEP)                          ] = 9
        out[valid & (v >= R_MIN + 7*R_STEP) & (v < R_MIN + 8*R_STEP)] = 8
        out[valid & (v >= R_MIN + 6*R_STEP) & (v < R_MIN + 7*R_STEP)] = 7
        out[valid & (v >= R_MIN + 5*R_STEP) & (v < R_MIN + 6*R_STEP)] = 6
        out[valid & (v >= R_MIN + 4*R_STEP) & (v < R_MIN + 5*R_STEP)] = 5
        out[valid & (v >= R_MIN + 3*R_STEP) & (v < R_MIN + 4*R_STEP)] = 4
        out[valid & (v >= R_MIN + 2*R_STEP) & (v < R_MIN + 3*R_STEP)] = 3
        out[valid & (v >= R_MIN + 1*R_STEP) & (v < R_MIN + 2*R_STEP)] = 2
        out[valid & (v >= R_MIN)            & (v < R_MIN + 1*R_STEP)] = 1

    elif name == 'Temperature':
        out[valid & (v >= T_MIN + 8*T_STEP)                          ] = 9
        out[valid & (v >= T_MIN + 7*T_STEP) & (v < T_MIN + 8*T_STEP)] = 8
        out[valid & (v >= T_MIN + 6*T_STEP) & (v < T_MIN + 7*T_STEP)] = 7
        out[valid & (v >= T_MIN + 5*T_STEP) & (v < T_MIN + 6*T_STEP)] = 6
        out[valid & (v >= T_MIN + 4*T_STEP) & (v < T_MIN + 5*T_STEP)] = 5
        out[valid & (v >= T_MIN + 3*T_STEP) & (v < T_MIN + 4*T_STEP)] = 4
        out[valid & (v >= T_MIN + 2*T_STEP) & (v < T_MIN + 3*T_STEP)] = 3
        out[valid & (v >= T_MIN + 1*T_STEP) & (v < T_MIN + 2*T_STEP)] = 2
        out[valid & (v >= T_MIN)            & (v < T_MIN + 1*T_STEP)] = 1

    out[~valid] = 0
    return out
