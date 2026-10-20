"""Fixed five-class scheme on the 1-9 scale and agreement statistics."""
import numpy as np

CLASSES = ["Very Low", "Low", "Moderate", "High", "Very High"]
BREAKS = [1.0, 2.6, 4.2, 5.8, 7.4, 9.0]          # five 1.6-wide classes; upper bound inclusive


def classify(score, breaks=BREAKS):
    """Return class index 0..4 (0 = Very Low)."""
    return np.digitize(score, breaks[1:-1], right=True).astype(np.int8)


def weighted_kappa(a, b, k=5):
    """Quadratic-weighted Cohen's kappa between two class arrays (0..k-1)."""
    cm = np.bincount(a.astype(np.int64) * k + b, minlength=k * k).reshape(k, k).astype(float)
    n = cm.sum()
    if n == 0:
        return 1.0
    i, j = np.indices((k, k))
    W = (i - j) ** 2 / (k - 1) ** 2
    E = np.outer(cm.sum(1), cm.sum(0)) / n
    denom = (W * E).sum()
    if denom == 0:
        return 1.0 if np.array_equal(a, b) else 0.0
    return 1 - (W * cm).sum() / denom

