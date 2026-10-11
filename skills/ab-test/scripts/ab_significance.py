#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A/B test helper for email and SMS campaigns. Standard library only (Python 3.8+).

Analyze results (two-proportion z-test):
  python3 ab_significance.py analyze --a-n 1000 --a-x 30 --b-n 1000 --b-x 45
    n = messages delivered in the variant, x = successes (for example clicks)

Plan a test (how many people you need):
  python3 ab_significance.py plan --baseline 0.03 --mde 0.01 [--segment-size 4000]
  python3 ab_significance.py plan --baseline 0.03 --mde-rel 0.25

Add --json for machine-readable output. Change the defaults with --alpha 0.05 --power 0.8
"""
import argparse
import json
import math
import sys
from statistics import NormalDist

ND = NormalDist()


def fmt_pct(x, digits=2):
    return "%.*f%%" % (digits, x * 100)


def fmt_pp(x, digits=2):
    return "%+.*f pp" % (digits, x * 100)


def num(x):
    return "%g" % x


def analyze(na, xa, nb, xb, alpha=0.05):
    pa, pb = xa / na, xb / nb
    diff = pb - pa
    rel = diff / pa if pa > 0 else None
    pool = (xa + xb) / (na + nb)
    se_pool = math.sqrt(pool * (1 - pool) * (1 / na + 1 / nb))
    if se_pool > 0:
        z = diff / se_pool
        p = 2 * (1 - ND.cdf(abs(z)))
    else:  # zero successes, or only successes, in both variants
        z, p = 0.0, 1.0
    se_unp = math.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb)
    zc = ND.inv_cdf(1 - alpha / 2)
    ci = (diff - zc * se_unp, diff + zc * se_unp)
    warnings = []
    if min(xa, na - xa, xb, nb - xb) < 5:
        warnings.append("Very few events in at least one cell (fewer than 5): the z-test is unreliable. "
                        "Collect more data or use Fisher's exact test.")
    if min(na, nb) < 100:
        warnings.append("Fewer than 100 per variant: treat the result as a directional signal, not proof.")
    if p < alpha:
        verdict = "B is better than A" if diff > 0 else "A is better than B"
        verdict += " (statistically significant at the %s threshold)" % num(alpha)
    else:
        verdict = ("No difference shown. This does NOT mean there is none: the sample may be too small "
                   "to detect it.")
    return {
        "a": {"n": na, "x": xa, "rate": pa}, "b": {"n": nb, "x": xb, "rate": pb},
        "diff_abs": diff, "diff_rel": rel, "z": z, "p_value": p, "alpha": alpha,
        "ci_diff": list(ci), "significant": p < alpha, "verdict": verdict, "warnings": warnings,
    }


def n_required(p1, p2, alpha=0.05, power=0.8):
    za = ND.inv_cdf(1 - alpha / 2)
    zb = ND.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return num / ((p2 - p1) ** 2)


def mde_for_n(p1, n, alpha=0.05, power=0.8):
    """Smallest absolute increase in the rate that can be detected with n people per variant."""
    lo, hi = 1e-9, 1 - p1 - 1e-9
    if hi <= lo or n_required(p1, p1 + hi, alpha, power) > n:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if n_required(p1, p1 + mid, alpha, power) <= n:
            hi = mid
        else:
            lo = mid
    return hi


def plan(baseline, mde_abs=None, mde_rel=None, alpha=0.05, power=0.8, segment_size=None):
    p1 = baseline
    p2 = p1 + mde_abs if mde_abs is not None else p1 * (1 + mde_rel)
    n = math.ceil(n_required(p1, p2, alpha, power))
    res = {"baseline": p1, "target": p2, "alpha": alpha, "power": power,
           "n_per_variant": n, "n_total": 2 * n}
    if segment_size:
        per = segment_size // 2
        res["segment_size"] = segment_size
        res["feasible"] = per >= n
        res["mde_abs_at_segment"] = mde_for_n(p1, per, alpha, power) if per > 0 else None
    return res


def main(argv=None):
    p = argparse.ArgumentParser(description="Analyze and plan A/B tests (two proportions).")
    sub = p.add_subparsers(dest="cmd", required=True)
    an = sub.add_parser("analyze", help="evaluate an A/B test result")
    an.add_argument("--a-n", type=int, required=True, help="delivered in variant A")
    an.add_argument("--a-x", type=int, required=True, help="successes in variant A (for example clicks)")
    an.add_argument("--b-n", type=int, required=True, help="delivered in variant B")
    an.add_argument("--b-x", type=int, required=True, help="successes in variant B")
    an.add_argument("--alpha", type=float, default=0.05)
    an.add_argument("--json", action="store_true")
    pl = sub.add_parser("plan", help="calculate the required sample size")
    pl.add_argument("--baseline", type=float, required=True, help="current success rate, for example 0.03 for 3%%")
    g = pl.add_mutually_exclusive_group(required=True)
    g.add_argument("--mde", type=float, help="smallest difference worth detecting, absolute, for example 0.01 = +1 pp")
    g.add_argument("--mde-rel", type=float, help="same, relative, for example 0.25 = +25%% over the baseline")
    pl.add_argument("--segment-size", type=int, help="total number of people in the segment")
    pl.add_argument("--alpha", type=float, default=0.05)
    pl.add_argument("--power", type=float, default=0.8)
    pl.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if not 0 < a.alpha < 1:
        p.error("--alpha must be between 0 and 1")
    if a.cmd == "analyze":
        for name, n, x in (("A", a.a_n, a.a_x), ("B", a.b_n, a.b_x)):
            if n <= 0 or x < 0 or x > n:
                p.error("Variant %s: need 0 <= x <= n and n > 0 (got n=%d, x=%d)" % (name, n, x))
        r = analyze(a.a_n, a.a_x, a.b_n, a.b_x, a.alpha)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return 0
        rel = "" if r["diff_rel"] is None else " (relative %+.1f%%)" % (r["diff_rel"] * 100)
        print("A/B test result")
        print("  A: %d / %d = %s" % (a.a_x, a.a_n, fmt_pct(r["a"]["rate"])))
        print("  B: %d / %d = %s" % (a.b_x, a.b_n, fmt_pct(r["b"]["rate"])))
        print("  Difference (B - A): %s%s" % (fmt_pp(r["diff_abs"]), rel))
        print("  %d%% confidence interval of the difference: from %s to %s"
              % (round((1 - a.alpha) * 100), fmt_pp(r["ci_diff"][0]), fmt_pp(r["ci_diff"][1])))
        print("  z = %.2f, p = %.4f (two-sided, threshold %s)" % (r["z"], r["p_value"], num(a.alpha)))
        print("  Verdict: " + r["verdict"])
        for w in r["warnings"]:
            print("  Warning: " + w)
        print("  Remember: one test is one observation. Repeat the winning variant before treating it as a rule.")
        return 0

    if not 0 < a.power < 1:
        p.error("--power must be between 0 and 1")
    if not 0 < a.baseline < 1:
        p.error("--baseline must be between 0 and 1, for example 0.03")
    p2 = a.baseline + a.mde if a.mde is not None else a.baseline * (1 + a.mde_rel)
    if not 0 < p2 < 1 or p2 == a.baseline:
        p.error("The target rate (%.4f) must be between 0 and 1 and different from the baseline" % p2)
    r = plan(a.baseline, a.mde, a.mde_rel, a.alpha, a.power, a.segment_size)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    print("A/B test plan")
    print("  Assumptions: baseline %s, target %s (%s), significance threshold %s, power %d%%"
          % (fmt_pct(r["baseline"]), fmt_pct(r["target"]), fmt_pp(r["target"] - r["baseline"]), num(r["alpha"]),
             round(r["power"] * 100)))
    print("  Required sample: %d people per variant (%d in total)" % (r["n_per_variant"], r["n_total"]))
    if "segment_size" in r:
        if r["feasible"]:
            print("  Your segment (%d people) is large enough for this test." % r["segment_size"])
        else:
            m = r["mde_abs_at_segment"]
            print("  Your segment (%d people) is too small for this test." % r["segment_size"])
            if m is None:
                print("  At this segment size no realistic difference can be detected.")
            else:
                print("  With %d people per variant you can detect a difference of about %s or more; "
                      "test a bigger change, combine several sends, or treat the result as directional."
                      % (r["segment_size"] // 2, fmt_pp(m)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
