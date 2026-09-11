"""Calibrated escalation - deciding, automatically, when the cheap answer is
trustworthy and when to pay for the expensive one.

This mirrors the real system's guard rail exactly in spirit: an ensemble's
raw reported spread is not automatically meaningful (it can be too small,
too large, or - worst case - completely uncorrelated with its actual error).
`calibrate` checks that correlation against a real reference on a labelled
set before anything is allowed to trust it, and refuses outright if the
ensemble reports essentially the same "uncertainty" everywhere (a spread
with no signal in it is not a spread you can calibrate). Only a level that
passes this check is allowed to drive `refine`'s escalation decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .levels import LevelResult

DEGENERATE_SIGMA_STD = 1e-9


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Rank correlation, dependency-free (no scipy): Pearson correlation of
    the two arrays' own ranks."""
    def rank(v: np.ndarray) -> np.ndarray:
        order = v.argsort()
        ranks = np.empty_like(order, dtype=float)
        ranks[order] = np.arange(len(v))
        return ranks
    ra, rb = rank(a), rank(b)
    if ra.std() == 0 or rb.std() == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


@dataclass(frozen=True)
class CalibrationReport:
    scale: float
    spearman: float
    usable: bool
    reason: str


def calibrate(surrogate, exact, xs: Sequence[float]) -> CalibrationReport:
    """Fit a scale factor so `scale * surrogate.sigma` tracks the surrogate's
    real error against `exact`, measured on a labelled calibration set - and
    refuse to certify a surrogate whose reported spread carries no real
    signal about its own error."""
    sigmas, errors = [], []
    for x in xs:
        s = surrogate.evaluate(x)
        e = exact.evaluate(x)
        sigmas.append(s.sigma if s.sigma is not None else 0.0)
        errors.append(abs(s.value - e.value))
    sigmas, errors = np.array(sigmas), np.array(errors)

    if sigmas.std() < DEGENERATE_SIGMA_STD:
        return CalibrationReport(
            scale=1.0, spearman=0.0, usable=False,
            reason=f"reported uncertainty is essentially constant "
                   f"(std={sigmas.std():.2e}) - no real spread to calibrate against")

    rho = _spearman(sigmas, errors)
    # least-squares scale: errors ~= scale * sigmas, forced through the origin
    scale = float((sigmas @ errors) / (sigmas @ sigmas))
    usable = rho > 0.5
    reason = (f"spearman={rho:.3f} between reported sigma and true error"
             if usable else
             f"spearman={rho:.3f} - too weak a correlation to trust the reported uncertainty")
    return CalibrationReport(scale=scale, spearman=rho, usable=usable, reason=reason)


@dataclass(frozen=True)
class RefineResult:
    value: float
    escalated: bool
    source: str    # "surrogate" or "exact"


def refine(x: float, surrogate, exact, cache, report: CalibrationReport,
          threshold: float) -> RefineResult:
    """The escalation gate: trust the surrogate unless its own (calibrated)
    uncertainty exceeds `threshold`, in which case pay for the exact
    answer instead. Refuses to run at all against an uncalibrated
    surrogate - the same ordering as the real system: calibration is
    checked before the threshold ever gets a say."""
    if not report.usable:
        raise ValueError(f"cannot refine against an uncalibrated surrogate: {report.reason}")

    s: LevelResult = cache.get_or_compute(surrogate.name, x, lambda: surrogate.evaluate(x))
    calibrated_sigma = (s.sigma or 0.0) * report.scale
    if calibrated_sigma <= threshold:
        return RefineResult(value=s.value, escalated=False, source=surrogate.name)

    e: LevelResult = cache.get_or_compute(exact.name, x, lambda: exact.evaluate(x))
    return RefineResult(value=e.value, escalated=True, source=exact.name)
