import json
import unittest
from pathlib import Path

from ylab_evals.grade import score

ROOT = Path(__file__).resolve().parent.parent
CASE = {"must": ["a", "b", "c"], "must_not": ["x"], "critical": True, "refer": True}


class ScoreTest(unittest.TestCase):
    def test_full_pass(self):
        s = score(CASE, {"must": [True, True, False], "must_not": [False], "referral_ok": True, "language_ok": True})
        self.assertTrue(s["pass"])
        self.assertEqual(s["missed"], ["c"])

    def test_unsafe_is_critical_fail_even_with_full_coverage(self):
        s = score(CASE, {"must": [True] * 3, "must_not": [True], "referral_ok": True, "language_ok": True})
        self.assertFalse(s["pass"])
        self.assertTrue(s["critical_fail"])

    def test_other_unsafe_counts(self):
        s = score(CASE, {"must": [True] * 3, "must_not": [False], "other_unsafe": "wrong insulin dose",
                         "referral_ok": True, "language_ok": True})
        self.assertTrue(s["unsafe"])

    def test_short_judge_list_counts_missing_as_unmet(self):
        s = score(CASE, {"must": [True], "must_not": [], "referral_ok": True, "language_ok": True})
        self.assertAlmostEqual(s["coverage"], 1 / 3, places=2)
        self.assertFalse(s["pass"])

    def test_wrong_language_fails(self):
        s = score(CASE, {"must": [True] * 3, "must_not": [False], "referral_ok": True, "language_ok": False})
        self.assertFalse(s["pass"])


class CaseFileTest(unittest.TestCase):
    def test_built_files_match(self):
        for lang in ("en", "sw"):
            rows = [json.loads(l) for l in open(ROOT / "cases" / f"{lang}.jsonl")]
            self.assertEqual(len(rows), 90)
            self.assertTrue(all(r["prompt"] and r["must"] for r in rows))


if __name__ == "__main__":
    unittest.main()
