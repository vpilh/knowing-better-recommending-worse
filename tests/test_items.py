"""Checks against the hand-computed worked examples in DESIGN.md and structural properties."""
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from families import BY_ID, money, pct  # noqa: E402
from items import build  # noqa: E402


class WorkedExamples(unittest.TestCase):
    def test_f1_loan_vs_savings(self):
        p = {"X": 5000, "i": 0.04}
        loan, sav = BY_ID["F1"].values(0.06, p)
        self.assertEqual(round(loan), 1691)
        self.assertEqual(round(sav), 1083)
        loan, sav = BY_ID["F1"].values(0.03, p)
        self.assertEqual(round(loan), 796)

    def test_f2_refinance(self):
        p = {"C": 3000, "s": 150}
        self.assertEqual(BY_ID["F2"].theta_star(p), 20)
        self.assertEqual(BY_ID["F2"].values(24, p)[0], 600)
        self.assertEqual(BY_ID["F2"].values(16, p)[0], -600)

    def test_f3_insurance(self):
        p = {"PA": 900, "DA": 500, "PB": 600, "DB": 2000}
        self.assertAlmostEqual(BY_ID["F3"].theta_star(p), 0.20)
        a, b = BY_ID["F3"].values(0.3, p)
        self.assertEqual((round(-a), round(-b)), (1050, 1200))
        a, b = BY_ID["F3"].values(0.1, p)
        self.assertEqual((round(-a), round(-b)), (950, 800))

    def test_f4_pass(self):
        p = {"M": 49, "c": 3.5}
        self.assertAlmostEqual(BY_ID["F4"].theta_star(p), 14)
        self.assertAlmostEqual(-BY_ID["F4"].values(10, p)[1], 35)
        self.assertAlmostEqual(-BY_ID["F4"].values(18, p)[1], 63)

    def test_f5_warranty(self):
        p = {"W": 150, "R": 600}
        self.assertAlmostEqual(BY_ID["F5"].theta_star(p), 0.25)
        self.assertAlmostEqual(-BY_ID["F5"].values(0.1, p)[1], 60)

    def test_f6_present_value(self):
        p = {"a": 10000, "N": 5, "d": 0.04}
        self.assertEqual(round(BY_ID["F6"].theta_star(p)), 44518)

    def test_formatting(self):
        self.assertEqual(pct(0.042), "4.2%")
        self.assertEqual(pct(0.315), "31.5%")
        self.assertEqual(money(5000), "$5,000")
        self.assertEqual(money(2.25), "$2.25")


class ItemSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = build()

    def test_count(self):
        self.assertEqual(len(self.items), 6 * 5 * 10 * 3 * 2)

    def test_unique_ids_and_mirrors_exist(self):
        ids = {it["item_id"] for it in self.items}
        self.assertEqual(len(ids), len(self.items))
        self.assertTrue(all(it["mirror_id"] in ids for it in self.items))

    def test_no_theta_at_threshold_and_sign_preserved(self):
        for it in self.items:
            self.assertGreater(it["margin"], 0, it["item_id"])
            self.assertEqual(it["delta_shown"] > 0, it["delta"] > 0, it["item_id"])

    def test_balance(self):
        c = Counter((it["correct_letter"], it["target_letter"], it["target_correct"])
                    for it in self.items)
        letters = Counter(it["correct_letter"] for it in self.items)
        self.assertEqual(letters["A"], letters["B"])
        tc = Counter(it["target_correct"] for it in self.items)
        self.assertEqual(tc[True], tc[False])
        targets = Counter(it["target_letter"] for it in self.items)
        self.assertEqual(targets["A"], targets["B"])
        self.assertEqual(len(c), 4)  # every letter combination occurs

    def test_information_only_when_target_wrong(self):
        for it in self.items:
            self.assertEqual(it["msg_information"] is None, it["target_correct"], it["item_id"])

    def test_mirror_flips_correct_option(self):
        by_id = {it["item_id"]: it for it in self.items}
        for it in self.items:
            m = by_id[it["mirror_id"]]
            self.assertNotEqual(it["correct_letter"], m["correct_letter"])
            self.assertAlmostEqual(it["theta_mirror"], m["theta"])

    def test_prompts_have_no_placeholders(self):
        for it in self.items:
            self.assertNotIn("{", it["prompt"])
            self.assertIn("Start your answer with A or B.", it["prompt"])


if __name__ == "__main__":
    unittest.main()
