"""qpu4qc — toy reference implementation.

This package is a small, self-contained, from-scratch illustration of the
architectural pattern described in ../../WHITEPAPER.md: treat every source of
a property (a fast classical surrogate, a slow "exact" reference, and a
quantum-hardware-computed answer for a reduced active space) as an
interchangeable, content-addressed `Level`, cache every result, and use a
surrogate's own reported uncertainty to decide - automatically - when the
cheap answer is trustworthy and when to pay for the expensive one.

It is NOT the production system: no real DFT/MLIP/QPU code lives here, only
synthetic stand-ins (an analytic double-well "molecule" and a small toy
Hamiltonian) chosen so the *pattern* is checkable by anyone in a few seconds,
with no GPU, no heavy dependencies (numpy only), and no proprietary data.
"""
from .levels import SurrogateLevel, ExactLevel, QuantumLevel
from .cache import ContentAddressedCache
from .calibrate import CalibrationReport, calibrate, refine

__all__ = [
    "SurrogateLevel", "ExactLevel", "QuantumLevel",
    "ContentAddressedCache",
    "CalibrationReport", "calibrate", "refine",
]
