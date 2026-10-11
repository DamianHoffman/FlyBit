import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "ab-test", "scripts"))
import ab_significance as ab  # noqa: E402

# Wartości referencyjne z scipy.stats.chi2_contingency(correction=False),
# co dla tabeli 2x2 jest równoważne testowi z dla dwóch proporcji.
REFERENCE = [
    ((1000, 30, 1000, 45), 0.0774848651, 1.765470),
    ((5000, 100, 5000, 160), 0.0001629993, 3.770380),
    ((200, 10, 200, 10), 1.0, 0.0),
]


class Analyze(unittest.TestCase):
    def test_matches_reference_values(self):
        for case, p, z in REFERENCE:
            r = ab.analyze(*case)
            self.assertAlmostEqual(r["p_value"], p, places=8)
            self.assertAlmostEqual(abs(r["z"]), z, places=5)

    def test_significance_flag_and_verdict(self):
        self.assertFalse(ab.analyze(1000, 30, 1000, 45)["significant"])
        r = ab.analyze(5000, 100, 5000, 160)
        self.assertTrue(r["significant"])
        self.assertIn("B is better", r["verdict"])

    def test_confidence_interval_contains_difference(self):
        r = ab.analyze(5000, 100, 5000, 160)
        lo, hi = r["ci_diff"]
        self.assertLess(lo, r["diff_abs"])
        self.assertGreater(hi, r["diff_abs"])
        self.assertGreater(lo, 0)

    def test_warns_on_tiny_counts(self):
        self.assertTrue(ab.analyze(100, 2, 90, 4)["warnings"])

    def test_zero_successes_does_not_crash(self):
        r = ab.analyze(100, 0, 100, 0)
        self.assertEqual(r["p_value"], 1.0)


class Plan(unittest.TestCase):
    def test_sample_size_known_values(self):
        self.assertEqual(ab.plan(0.03, 0.01)["n_per_variant"], 5301)
        self.assertEqual(ab.plan(0.03, None, 0.25)["n_per_variant"], 9100)

    def test_small_segment_is_flagged_and_mde_is_consistent(self):
        r = ab.plan(0.03, 0.01, segment_size=4000)
        self.assertFalse(r["feasible"])
        m = r["mde_abs_at_segment"]
        self.assertAlmostEqual(m, 0.017045, places=5)
        self.assertAlmostEqual(ab.n_required(0.03, 0.03 + m), 2000, delta=1)

    def test_large_segment_is_feasible(self):
        self.assertTrue(ab.plan(0.03, 0.01, segment_size=20000)["feasible"])


class Formatting(unittest.TestCase):
    def test_units_and_decimal_point(self):
        self.assertEqual(ab.fmt_pp(0.015), "+1.50 pp")
        self.assertEqual(ab.fmt_pct(0.0375), "3.75%")
        self.assertEqual(ab.num(0.05), "0.05")


if __name__ == "__main__":
    unittest.main()
