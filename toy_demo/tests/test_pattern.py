"""The three claims this toy makes, each checked directly rather than just
printed in the demo: caching actually avoids recomputation, calibration
actually refuses a surrogate whose uncertainty carries no signal, and
refine() actually escalates only past its threshold.
"""
import numpy as np
import pytest

from qpu4qc_toy import (ContentAddressedCache, ExactLevel, QuantumLevel,
                        SurrogateLevel, calibrate, refine)
from qpu4qc_toy.calibrate import CalibrationReport


def test_cache_hit_avoids_recomputation():
    cache = ContentAddressedCache()
    calls = []

    def compute():
        calls.append(1)
        return 42

    for _ in range(5):
        assert cache.get_or_compute("level", 1.0, compute) == 42
    assert len(calls) == 1                  # only the first call actually ran
    assert cache.hits == 4 and cache.misses == 1


def test_cache_distinguishes_different_inputs():
    cache = ContentAddressedCache()
    assert cache.address("level", 1.0) != cache.address("level", 2.0)
    assert cache.address("a", 1.0) != cache.address("b", 1.0)


def test_calibrate_certifies_a_real_ensemble():
    surrogate, exact = SurrogateLevel(seed=0), ExactLevel()
    xs = np.random.default_rng(2).uniform(-2.5, 2.5, 40)
    report = calibrate(surrogate, exact, xs)
    assert report.usable
    assert report.spearman > 0.8


def test_calibrate_refuses_a_surrogate_with_no_real_uncertainty_signal():
    """A surrogate that reports a fixed, non-informative 'uncertainty' must
    be refused - the same guard the real system enforces against a
    single-member (non-ensemble) model."""
    class ConstantSigmaSurrogate:
        name = "constant_sigma"

        def evaluate(self, x):
            from qpu4qc_toy.levels import LevelResult, _true_profile
            return LevelResult(value=float(_true_profile(np.asarray(x))) + 5.0, sigma=0.01)

    surrogate, exact = ConstantSigmaSurrogate(), ExactLevel()
    xs = np.linspace(-2.5, 2.5, 20)
    report = calibrate(surrogate, exact, xs)
    assert not report.usable


def test_refine_escalates_past_threshold_and_trusts_below_it():
    surrogate, exact = SurrogateLevel(seed=0), ExactLevel()
    cache = ContentAddressedCache()
    xs = np.random.default_rng(3).uniform(-2.5, 2.5, 40)
    report = calibrate(surrogate, exact, xs)

    loose = refine(0.0, surrogate, exact, cache, report, threshold=1e6)
    assert not loose.escalated and loose.source == "surrogate"

    tight = refine(0.0, surrogate, exact, cache, report, threshold=1e-9)
    assert tight.escalated and tight.source == "exact"


def test_refine_refuses_an_uncalibrated_surrogate():
    surrogate, exact = SurrogateLevel(seed=0), ExactLevel()
    cache = ContentAddressedCache()
    bad_report = CalibrationReport(scale=1.0, spearman=0.0, usable=False, reason="test")
    with pytest.raises(ValueError, match="uncalibrated"):
        refine(0.0, surrogate, exact, cache, bad_report, threshold=0.1)


def test_quantum_level_shares_the_same_interface_and_is_deterministic():
    quantum = QuantumLevel()
    a = quantum.evaluate(0.7)
    b = quantum.evaluate(0.7)
    assert a.value == pytest.approx(b.value)
    assert a.sigma == 0.0
