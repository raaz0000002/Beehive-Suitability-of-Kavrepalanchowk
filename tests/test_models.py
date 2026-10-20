"""Unit tests for the three aggregation models and the classifier (synthetic data, no rasters needed)."""
import os, sys
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apiary_mcda import MODELS, wlc, wpm, topsis, classify, weighted_kappa, BREAKS

W = {"A": 0.5, "B": 0.3, "C": 0.2}


def stack(*cols):
    return {k: np.asarray(v, dtype="float64") for k, v in zip(W, cols)}


@pytest.mark.parametrize("name", list(MODELS))
def test_uniform_scores_return_that_score(name):
    for v in (1.0, 5.0, 9.0):
        X = stack([v], [v], [v])
        assert MODELS[name](X, W)[0] == pytest.approx(v)


@pytest.mark.parametrize("name", list(MODELS))
def test_range_and_monotonic(name):
    rng = np.random.default_rng(0)
    X = stack(*(rng.uniform(1, 9, 1000) for _ in W))
    s = MODELS[name](X, W)
    assert s.min() >= 1 - 1e-12 and s.max() <= 9 + 1e-12
    X2 = dict(X); X2["A"] = np.minimum(X["A"] + 1, 9)
    assert np.all(MODELS[name](X2, W) >= s - 1e-12)


def test_wlc_hand_value():
    assert wlc(stack([9], [1], [5]), W)[0] == pytest.approx(0.5 * 9 + 0.3 * 1 + 0.2 * 5)


def test_wpm_hand_value():
    assert wpm(stack([9], [1], [5]), W)[0] == pytest.approx(9 ** 0.5 * 1 ** 0.3 * 5 ** 0.2)


def test_topsis_hand_value():
    x = np.array([9, 1, 5.0]); w = np.array([0.5, 0.3, 0.2]); v = w * (x - 1) / 8
    dp, dm = np.sqrt(((w - v) ** 2).sum()), np.sqrt((v ** 2).sum())
    assert topsis(stack(*[[a] for a in x]), W)[0] == pytest.approx(1 + 8 * dm / (dp + dm))


def test_wpm_not_above_wlc():
    """Weighted geometric mean <= weighted arithmetic mean (AM-GM)."""
    rng = np.random.default_rng(1)
    X = stack(*(rng.uniform(1, 9, 5000) for _ in W))
    assert np.all(wpm(X, W) <= wlc(X, W) + 1e-12)


def test_classify_breaks_upper_inclusive():
    s = np.array([1.0, 2.6, 2.6000001, 4.2, 5.8, 5.81, 7.4, 7.41, 9.0])
    assert classify(s).tolist() == [0, 0, 1, 1, 2, 3, 3, 4, 4]
    assert BREAKS == [1.0, 2.6, 4.2, 5.8, 7.4, 9.0]


def test_weighted_kappa():
    a = np.array([0, 1, 2, 3, 4] * 20, dtype=np.int8)
    assert weighted_kappa(a, a) == pytest.approx(1.0)
    assert weighted_kappa(a, a[::-1].copy()) < 0
