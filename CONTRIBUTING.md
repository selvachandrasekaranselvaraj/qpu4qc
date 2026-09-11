# Contributing to qpu4qc

This repository publishes the architecture, benchmark results, and a toy
reference implementation for a system whose production code is not open
source (see [`architecture/level_abstraction.md`](architecture/level_abstraction.md#what-this-repo-shows-vs-what-it-doesnt)
for the exact boundary). Contributions here are welcome in a few specific
forms:

## What's genuinely open to contribution

- **The toy demo** (`toy_demo/`): bugs, clearer tests, additional toy
  levels that illustrate the same pattern in a new way (e.g. a toy level
  representing a different quantum-hardware paradigm, or a second kind of
  classical surrogate), improvements to the demo's own explanatory output.
- **The architecture documentation**: clearer diagrams, better explanations
  of the interface contract, corrections to anything inaccurate.
- **The benchmark methodology**: if you spot a way the reported comparisons
  could be made fairer or more rigorous, open an issue.

## What isn't in scope for a PR here

- Production adapters for real DFT codes, MLIP frameworks, or quantum
  hardware/SDKs — those live in a private codebase this repo intentionally
  does not include.
- Changes that would require disclosing tuned calibration thresholds or
  proprietary training data.

## Getting started

```bash
git clone https://github.com/selvachandrasekaranselvaraj/qpu4qc.git
cd qpu4qc/toy_demo
python3 -m pip install -e ".[dev]"
python3 -m pytest -v
python3 demo.py
```

## If you want to build the real thing, not just the toy

If your interest is in the production system this repo describes rather
than the toy demo — see the "Get in touch" section of
[`README.md`](README.md).
