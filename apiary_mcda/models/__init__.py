"""Aggregation models. Each takes X (dict criterion -> 1-D array of 1-9 scores) and w (dict criterion -> weight,
summing to 1) and returns a 1-D float64 array of scores on the 1-9 scale."""
from .wlc import wlc
from .wpm import wpm
from .topsis import topsis

MODELS = {"WLC": wlc, "WPM": wpm, "TOPSIS": topsis}
