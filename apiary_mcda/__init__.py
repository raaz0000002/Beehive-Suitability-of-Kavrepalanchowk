"""Apiary-site suitability MCDA for Kavrepalanchowk, Nepal: aggregation models, classification and helpers."""
from .models import MODELS, wlc, wpm, topsis
from .classify import BREAKS, CLASSES, classify, weighted_kappa
from .io import load_stack

__version__ = "1.0.0"
