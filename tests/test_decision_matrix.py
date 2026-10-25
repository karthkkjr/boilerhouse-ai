#!/usr/bin/env python3
"""Run: python3 -m unittest tests/test_decision_matrix.py -v   (or pytest)"""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "skills", "decision-matrix-calculator", "scripts")


def run(script, *args):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args],
                       capture_output=True, text=True, timeout=20)
    return p.returncode, json.loads(p.stdout), p.stderr  # stdout must ALWAYS be pure JSON


class TestRank(unittest.TestCase):
    def test_default_ranks_all_15(self):
        code, out, err = run("rank_apartments.py", "--top", "15")
        self.assertEqual(code, 0)
        self.assertEqual(out["candidate_count"], 15)
        self.assertEqual([r["rank"] for r in out["results"]], list(range(1, 16)))
        self.assertIn("[decision-matrix]", err)  # logs on stderr, not stdout
        scores = [r["score"] for r in out["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(0 <= s <= 100 for s in scores))

    def test_weights_normalized(self):
        _, out, _ = run("rank_apartments.py", "--weights", "price=5,distance=3,rating=2")
        self.assertAlmostEqual(sum(out["weights"].values()), 1.0, places=3)

    def test_price_only_picks_cheapest(self):
        _, out, _ = run("rank_apartments.py", "--weights", "price=1")
        self.assertEqual(out["results"][0]["id"], "fairway")

    def test_distance_only_picks_closest(self):
        _, out, _ = run("rank_apartments.py", "--weights", "distance=1")
        self.assertEqual(out["results"][0]["id"], "hub-on-campus")

    def test_filters_and_excluded(self):
        _, out, _ = run("rank_apartments.py", "--budget", "900", "--max-distance", "1.5")
        for r in out["results"]:
            self.assertLessEqual(r["raw"]["price_per_bed"], 900)
            self.assertLessEqual(r["raw"]["distance_mi"], 1.5)
        self.assertEqual(out["candidate_count"] + len(out["excluded"]), 15)

    def test_json_mode(self):
        code, out, _ = run("rank_apartments.py", "--json",
                           '{"budget": "1000", "weights": {"rating": 1}, "amenities": ["gym"], "top": 2}')
        self.assertEqual(code, 0)
        self.assertEqual(len(out["results"]), 2)
        self.assertTrue(all("gym" in r["raw"]["amenities"] for r in out["results"]))

    def test_no_match_is_json_error(self):
        code, out, _ = run("rank_apartments.py", "--budget", "100")
        self.assertEqual(code, 2)
        self.assertEqual(out["status"], "error")

    def test_bad_weight_is_json_error(self):
        code, out, _ = run("rank_apartments.py", "--weights", "vibes=1")
        self.assertEqual(code, 2)
        self.assertIn("Unknown criteria", out["error"])


class TestLookup(unittest.TestCase):
    def test_list(self):
        _, out, _ = run("lookup_apartments.py", "--list")
        self.assertEqual(out["count"], 15)

    def test_compare(self):
        code, out, _ = run("lookup_apartments.py", "--compare", "hub,rise,muinzer")
        self.assertEqual(code, 0)
        self.assertEqual(out["best_by"]["price"], "Muinzer Apartments")

    def test_not_found(self):
        code, out, _ = run("lookup_apartments.py", "--name", "zzz")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
