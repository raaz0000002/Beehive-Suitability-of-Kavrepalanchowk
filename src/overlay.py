import numpy as np

def compute_weighted_overlay(classified_stack, weights):
    """
    Computes weighted score by applying criterion weights to classified rasters.
    Returns float32 array.
    """
    # Initialize mask of valid pixels across all classified rasters
    # (A cell must be valid in all classified rasters to be evaluated)
    valid_all = np.ones(next(iter(classified_stack.values())).shape, dtype=bool)
    for arr in classified_stack.values():
        valid_all &= (arr > 0)

    # Initial final score array
    final_score = np.zeros(valid_all.shape, dtype=np.float32)
    for name, w in weights.items():
        final_score += classified_stack[name].astype(np.float32) * w
        
    final_score[~valid_all] = np.nan
    return final_score, valid_all

def categorize_suitability(final_score):
    """
    Reclassifies the continuous suitability scores into 5 category classes:
      1: Very Low   (1.0 - 2.8)
      2: Low        (2.8 - 4.6)
      3: Moderate   (4.6 - 6.4)
      4: High       (6.4 - 8.2)
      5: Very High  (8.2 - 9.0)
    Returns uint8 array (0 represents NoData/masked values).
    """
    final_cat = np.zeros(final_score.shape, dtype=np.uint8)
    final_cat[(final_score >= 1.0) & (final_score <  2.8)] = 1
    final_cat[(final_score >= 2.8) & (final_score <  4.6)] = 2
    final_cat[(final_score >= 4.6) & (final_score <  6.4)] = 3
    final_cat[(final_score >= 6.4) & (final_score <  8.2)] = 4
    final_cat[(final_score >= 8.2) & (final_score <= 9.0)] = 5
    final_cat[np.isnan(final_score)]                        = 0
    return final_cat
