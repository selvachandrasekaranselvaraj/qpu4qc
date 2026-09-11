# Benchmark results

Every number below was measured, not modeled or projected — against a real,
already-completed ab initio job's own recorded wall-clock, and a real
quantum-circuit simulation checked against exact diagonalization. The raw
job data lives in a private research environment and isn't included in this
repo (see [`../architecture/level_abstraction.md`](../architecture/level_abstraction.md)
for what is and isn't published here); what's reproducible here is the
*methodology* and the toy demo that proves the underlying pattern.

## 1. Classical surrogate vs. real DFT, same system

A machine-learned interatomic potential (an early-stage checkpoint, not a
finished production model — see caveats below) evaluated on the exact same
real, DFT-relaxed 52-atom lithium argyrodite solid-electrolyte structure a
completed VASP job had already computed, compared against that job's own
recorded wall-clock per step.

| Method | Time per structure | Source |
|---|---|---|
| Real DFT, ab initio MD settings | 2.15 s | production VASP job, 50,000 steps, wall-clock / step count |
| Real DFT, geometry optimization settings | 5.12 s | production VASP job, 300 steps, wall-clock / step count |
| MLIP checkpoint, CPU | 1.58 ms | measured directly, 10-run average |
| MLIP checkpoint, GPU (H100) | 0.48 ms | measured directly, 20-run average |

**Measured speedup: ~4,500× (vs. AIMD-quality settings) to ~10,600× (vs.
optimization-quality settings).**

This is the concrete, quantitative version of the architecture's central
claim: once a structure's energy/forces come from a calibrated surrogate
level instead of solving the electronic structure problem from scratch,
every downstream computation built on it (a relaxation, a transition-state
search, a reaction trajectory) inherits that speedup — and a
content-addressed cache means a given structure's energy is never paid for
twice across an entire campaign.

**Honest caveat**: speed and accuracy are independent axes. Measured against
200 real, multi-temperature ab initio MD structures, this same checkpoint's
mean error was 53.7 meV/atom — large for a production potential — and it
reports zero epistemic uncertainty (a single model, not yet an ensemble),
which is exactly why the calibration guard below refuses to certify it for
real, uncertainty-gated escalation. The speed number is real; it does not
by itself make this particular checkpoint's *numbers* trustworthy.

## 2. Calibration guard: refusing an overconfident model

The same checkpoint, evaluated on 20 real ab initio MD structures:

| Quantity | Measured value |
|---|---|
| Reported uncertainty (single model, no ensemble) | exactly 0.0 for every structure |
| Real \|error\| against ab initio reference | mean 3.62 eV, max 5.43 eV |
| Calibration result | **refused** — "reports essentially the same uncertainty for every structure; no real spread to calibrate against" |

This is a feature, not a bug: a model that is both wrong and silent about
being wrong must never be certified for automated, uncertainty-gated
escalation. Only a genuine multi-member ensemble — one that actually
disagrees with itself in proportion to its real error — is allowed to drive
that decision. See `toy_demo/qpu4qc_toy/calibrate.py` for a small, checkable
version of the same guard.

## 3. Content-addressed caching, real system

A real, multi-step property-engine calculation (relax → interpolate →
saddle-point search → vibrational analysis → rate), executed once against a
real learned potential on real GPU hardware, then repeated against the same
on-disk store:

| Run | Wall clock | Cache stats |
|---|---|---|
| Cold (nothing cached) | 17.8 s (GPU) / 84.6 s (CPU) | 0/16 nodes cached |
| Same program, same store, repeated | **0.0 s** | 16/16 hits, 100% hit rate |

Identical result to full numerical precision on both runs — the second run
does no computation at all.

## 4. The quantum bridge: correctness, not yet scale

A variational quantum eigensolver (simulated, not run on physical quantum
hardware yet) checked against exact diagonalization on a real, small
molecular system (H₂, STO-3G basis, Jordan-Wigner and parity mappings both
checked):

| Quantity | Measured value |
|---|---|
| \|VQE energy − exact diagonalization\| | **5.7 × 10⁻¹¹ Hartree** |

This validates the mechanism — an active-space reduction, a fermion-to-qubit
mapping, and a variational ansatz composed into the same computation graph
as the classical levels above, producing the right answer to the limit of
numerical precision. It does **not** yet demonstrate that this scales to an
engineering-relevant active space, or that it holds on real (noisy) quantum
hardware rather than a simulator — both explicitly future work, not implied
by this result.

## Reproducing what's reproducible here

Section 1's DFT numbers and section 2's calibration measurement depend on
private research data (a completed production ab initio job) not included
in this repository. What *is* fully reproducible by anyone, in seconds, is
the underlying pattern — `toy_demo/demo.py` demonstrates a synthetic version
of the same calibration guard, the same escalation logic, and the same
caching behavior end to end, with nothing but numpy.
