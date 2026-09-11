# qpu4qc

**Bridging quantum chemistry and quantum hardware for real-world engineering
— toward chemistry simulation fast and trustworthy enough to sit inside a
live design loop, not just answer offline queries.**

DFT is accurate and slow. Machine-learned potentials are fast and only as
trustworthy as their calibration. Quantum computers solve exactly the
problems classical methods approximate, and aren't yet at engineering
scale. `qpu4qc` is an architecture that treats all three as interchangeable,
cost-accounted, cached levels of the same computation graph — with a
surrogate's own reported uncertainty deciding, automatically, when its
answer is good enough and when to pay for a better one.

📄 **[Read the full report →](WHITEPAPER.md)**

## What's real here

Every number below was measured against a real, completed research
calculation — not modeled, not projected. Full methodology in
[`benchmarks/results.md`](benchmarks/results.md).

| Claim | Measured result |
|---|---|
| Surrogate vs. real DFT, same structure | **4,500×–10,600× faster**, against the DFT job's own recorded wall-clock |
| Calibration guard correctly refuses an overconfident model | wrong by 3.6 eV mean, reporting 0 uncertainty → refused, not silently trusted |
| Content-addressed caching | repeated run: 100% cache hit, 0.0s, bit-identical result |
| Quantum bridge correctness | VQE vs. exact diagonalization agree to 5.7×10⁻¹¹ Hartree |

## What's honestly not solved yet

- The quantum bridge is validated on small molecules against simulators —
  not an engineering-scale active space, not real quantum hardware.
- Calibrated escalation is validated on synthetic ensembles and shown to
  correctly *refuse* an under-specified real model — a production-scale,
  genuinely well-calibrated ensemble is still training.
- "Real-time" — a campaign that runs continuously against a live
  trajectory rather than answering queries on demand — is the roadmap, not
  a finished capability.

See [§6 of the whitepaper](WHITEPAPER.md#6-whats-not-solved-yet--stated-plainly)
for the full, unhedged list.

## Try the pattern yourself

A small (~250-line), dependency-free (numpy only) reference implementation
that proves the architecture's core mechanism — content-addressed caching,
calibrated escalation, and a quantum level sharing one interface with two
classical ones — runnable in under a second:

```bash
git clone https://github.com/selvachandrasekaranselvaraj/qpu4qc.git
cd qpu4qc/toy_demo
python3 demo.py
```

See [`toy_demo/README.md`](toy_demo/README.md) for details and the test
suite.

## What's open here vs. what stays private

This repository publishes the architecture, the interface contracts, real
measured benchmark results, and a toy reference implementation that proves
the pattern is genuine. It does **not** publish the production DFT/MLIP/
quantum-hardware adapters, tuned calibration thresholds, or the full
operation library the production system runs on. See
[`architecture/level_abstraction.md`](architecture/level_abstraction.md#what-this-repo-shows-vs-what-it-doesnt)
for the exact boundary.

## Get in touch

Building real HPC/ML infrastructure, or working on quantum chemistry,
quantum hardware, or computational materials science, and want to work on
this rather than just read about it?

**Selva Chandrasekaran Selvaraj**
[GitHub](https://github.com/selvachandrasekaranselvaraj) ·
[LinkedIn](https://www.linkedin.com/in/selvachandrasekaranselvaraj) ·
[X / Twitter](https://x.com/selva_odc) ·
[Hugging Face](https://huggingface.co/Selvauma)

## License

[MIT](LICENSE) for everything in this repository.
