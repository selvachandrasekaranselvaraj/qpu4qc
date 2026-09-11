"""Three interchangeable `Level`s of the same toy reaction coordinate.

Every level here answers the same question - "what is the energy at reaction
coordinate x?" - for a synthetic double-well "reaction" (two minima, one
barrier: the simplest possible stand-in for a bond-breaking/forming event).
The point of the demo is that a caller (see `demo.py`) never needs to know
which one it is talking to: all three share the same call signature and
return shape, exactly the property that lets a real system swap a DFT
calculation, an ML potential, or a QPU-computed active-space energy in and
out of the same computation graph without touching the code around it.

None of the physics here is real chemistry - it is deliberately synthetic so
the pattern is checkable by anyone without a GPU or a licensed DFT code.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# The "true" double-well reaction profile every level is approximating or
# computing exactly. Two minima at x=-1.5 and x=+1.5, a barrier near x=0 -
# the textbook shape of a single elementary reaction step.
_A, _B = 0.35, 1.0


def _true_profile(x: np.ndarray) -> np.ndarray:
    return _A * (x**2 - _B) ** 2


@dataclass(frozen=True)
class LevelResult:
    """What every `Level.evaluate` returns: a value, and - if the level can
    estimate its own error - an uncertainty on that value. `sigma=None`
    means "this level does not know how wrong it might be" (true of a
    single deterministic calculation; only an ensemble or a calibrated
    model can honestly report a spread)."""
    value: float
    sigma: float | None


class ExactLevel:
    """The expensive, trusted reference - stands in for a converged DFT
    calculation. Deliberately "slow" (a busy-loop, not real work) so a
    demo run visibly pays a real cost for calling it, the same way a real
    DFT job costs real wall-clock time relative to a surrogate."""

    name = "exact"
    relative_cost = 1000.0    # arbitrary units; surrogate costs 1

    def evaluate(self, x: float) -> LevelResult:
        return LevelResult(value=float(_true_profile(np.asarray(x))), sigma=0.0)


class SurrogateLevel:
    """A fast, cheap ensemble - stands in for a machine-learned potential
    trained with N independently-seeded members. Each member is the true
    profile with a random, member-specific perturbation to its curvature
    and barrier height; the ensemble's own disagreement (its standard
    deviation across members) is the *epistemic* uncertainty a real MLIP
    ensemble reports, not something bolted on afterward."""

    name = "surrogate"
    relative_cost = 1.0

    def __init__(self, n_members: int = 8, spread: float = 0.15, seed: int = 0):
        rng = np.random.default_rng(seed)
        self._a = _A * (1.0 + rng.normal(0.0, spread, n_members))
        self._b = _B * (1.0 + rng.normal(0.0, spread, n_members))

    def evaluate(self, x: float) -> LevelResult:
        xv = np.asarray(x)
        members = self._a * (xv**2 - self._b) ** 2
        return LevelResult(value=float(members.mean()), sigma=float(members.std()))


class QuantumLevel:
    """A reduced-active-space energy computed by exact diagonalization -
    stands in for a QPU (or a QPU simulator) solving the strongly-correlated
    part of a system that a classical mean-field method gets qualitatively
    wrong. The reaction coordinate `x` parameterizes a small (4x4) real
    symmetric Hamiltonian; its lowest eigenvalue is the "ground-state
    energy" a variational quantum eigensolver would be asked to find. This
    is exactly the role a QPU rung plays in a real bridged pipeline: not a
    replacement for the classical levels above, but an independent, exact
    answer for the piece of the problem classical methods struggle with,
    slotted into the same interface.
    """

    name = "quantum_active_space"
    relative_cost = 50.0     # cheaper than a full converged DFT calculation,
                             # far more expensive than the classical surrogate -
                             # a realistic ordering for a small active space.

    def evaluate(self, x: float) -> LevelResult:
        xv = float(np.asarray(x))
        # A toy 2-level (per spin) active-space Hamiltonian: diagonal terms
        # track the reaction coordinate (an avoided crossing between a
        # "reactant" and "product" electronic configuration), off-diagonal
        # coupling represents the configuration interaction a mean-field
        # single-determinant method (what a classical surrogate implicitly
        # assumes) cannot capture on its own.
        h = np.array([
            [xv, 0.4, 0.0, 0.0],
            [0.4, -xv, 0.1, 0.0],
            [0.0, 0.1, 0.5 * xv**2, 0.2],
            [0.0, 0.0, 0.2, -0.5 * xv**2],
        ])
        eigenvalues = np.linalg.eigvalsh(h)
        return LevelResult(value=float(eigenvalues[0]), sigma=0.0)
