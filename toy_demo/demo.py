#!/usr/bin/env python3
"""Run this file. It's the whole pattern, end to end, in one pass:

  1. A fast surrogate ensemble and a slow "exact" reference both answer the
     same question (a toy reaction coordinate's energy) through the same
     interface.
  2. calibrate() checks the surrogate's reported uncertainty actually tracks
     its real error, against a labelled calibration set - and would refuse
     to proceed if it didn't.
  3. refine() runs a "campaign" over new points, trusting the cheap surrogate
     except where its calibrated uncertainty is too high, escalating to the
     expensive exact level only there.
  4. A quantum level - a different computational substrate entirely - slots
     into the exact same call pattern, for the piece of the problem the
     classical levels don't model at all.
  5. The content-addressed cache means asking the same question twice never
     pays for it twice.

No GPU, no network, no dependency but numpy. Expected run time: well under
a second.
"""
import numpy as np

from qpu4qc_toy import (ContentAddressedCache, ExactLevel, QuantumLevel,
                        SurrogateLevel, calibrate, refine)


def main() -> None:
    surrogate = SurrogateLevel(n_members=8, spread=0.15, seed=0)
    exact = ExactLevel()
    quantum = QuantumLevel()
    cache = ContentAddressedCache()

    print("=" * 72)
    print("1. Calibration: does the surrogate's own uncertainty mean anything?")
    print("=" * 72)
    rng = np.random.default_rng(1)
    calibration_xs = rng.uniform(-2.5, 2.5, 40)
    report = calibrate(surrogate, exact, calibration_xs)
    print(f"  spearman(sigma, true error) = {report.spearman:.3f}")
    print(f"  calibration scale           = {report.scale:.3f}")
    print(f"  usable                      = {report.usable}  ({report.reason})")
    if not report.usable:
        print("\n  Refusing to run a campaign against an uncalibrated surrogate - exactly "
             "as the real system does.")
        return

    print()
    print("=" * 72)
    print("2. A calibrated campaign: escalate only where the surrogate says it's unsure")
    print("=" * 72)
    campaign_xs = np.linspace(-2.5, 2.5, 15)
    threshold = 0.15
    n_escalated = 0
    for x in campaign_xs:
        result = refine(x, surrogate, exact, cache, report, threshold)
        flag = "-> ESCALATED to exact" if result.escalated else "   (trusted surrogate)"
        n_escalated += result.escalated
        print(f"  x={x:+.2f}  energy={result.value:8.4f}  {flag}")
    print(f"\n  {n_escalated}/{len(campaign_xs)} points needed escalation "
         f"(threshold={threshold} on calibrated sigma)")

    print()
    print("=" * 72)
    print("3. The cache: asking the same question twice never pays for it twice")
    print("=" * 72)
    for x in campaign_xs:
        refine(x, surrogate, exact, cache, report, threshold)     # repeat the whole campaign
    print(f"  cache hit rate after repeating the campaign: {cache.hit_rate:.0%}")
    assert cache.hit_rate > 0.45, "the repeated campaign should be almost entirely cache hits"

    print()
    print("=" * 72)
    print("4. A quantum level, same interface, answering a different question")
    print("=" * 72)
    print("  (the piece classical surrogate/exact levels above don't model at all:")
    print("   an active-space electronic-structure problem, solved exactly)")
    for x in (-1.5, 0.0, 1.5):
        q = quantum.evaluate(x)
        print(f"  x={x:+.2f}  quantum active-space ground state = {q.value:8.4f}")

    print()
    print("Done. Same `LevelResult` shape, same cache, same calibration contract, "
         "for a classical surrogate, a classical reference, and a quantum solver.")


if __name__ == "__main__":
    main()
