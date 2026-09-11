# qpu4qc — toy reference implementation

A from-scratch, ~250-line, numpy-only illustration of the pattern described
in [`../WHITEPAPER.md`](../WHITEPAPER.md): a fast classical surrogate, a slow
"exact" reference, and a quantum-hardware-computed answer, all behind one
interface, content-addressed, with a surrogate's own reported uncertainty
deciding automatically when to trust it and when to escalate.

This is **not** the production system — no real DFT, MLIP, or QPU code lives
here. It exists so the architectural claim is checkable by anyone, in
seconds, with nothing but Python and numpy.

## Run it

```bash
cd toy_demo
python3 demo.py
```

No install required — it only needs `numpy`.

## What you'll see

1. A calibration check on a labelled set — does the surrogate's own
   reported uncertainty actually correlate with its real error against the
   exact reference? (It's refused outright if not.)
2. A 15-point campaign where each point is answered by whichever level is
   appropriate: the cheap surrogate where it's confident, the expensive
   exact reference only where it isn't.
3. The same campaign, repeated — cache hit rate confirms nothing gets
   recomputed.
4. A quantum level (exact diagonalization of a small active-space
   Hamiltonian) answering a different kind of question through the exact
   same call pattern as the two classical levels above.

## Run the tests

```bash
cd toy_demo
python3 -m pytest -v
```

7 tests, each checking one specific claim directly (not just printing it):
caching avoids recomputation, calibration refuses a surrogate whose
uncertainty carries no real signal, escalation triggers only past
threshold, and the quantum level is deterministic and interface-compatible
with the classical ones.
