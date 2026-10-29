import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from interrater_agreement.cli import main
from interrater_agreement.core import (cohens_kappa, counts_from_ratings, fleiss_kappa, interpret, percent_agreement,
                                       weighted_kappa)

# Classic example: both yes 20, A yes/B no 5, A no/B yes 10, both no 15 -> po .70, pe .50, kappa .40
A = ["y"] * 25 + ["n"] * 25
B = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15
# Fleiss (1971) style example from the literature: 10 items, 14 raters, 5 categories -> kappa 0.210
FLEISS = [[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1],
          [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]]


class KappaTests(unittest.TestCase):
    def test_cohen(self):
        r = cohens_kappa(A, B)
        self.assertAlmostEqual(r["po"], 0.7)
        self.assertAlmostEqual(r["pe"], 0.5)
        self.assertAlmostEqual(r["kappa"], 0.4)
        self.assertLess(r["ci"][0], 0.4)
        self.assertAlmostEqual(percent_agreement(A, B), 0.7)

    def test_missing_ratings_skipped(self):
        self.assertEqual(cohens_kappa(["a", "b", ""], ["a", "b", "a"])["n"], 2)
        with self.assertRaises(ValueError):
            cohens_kappa(["", ""], ["a", "b"])

    def test_fleiss_reference(self):
        self.assertAlmostEqual(fleiss_kappa(FLEISS)["kappa"], 0.210, places=3)
        with self.assertRaises(ValueError):
            fleiss_kappa([[1, 1], [2, 1]])

    def test_weighted(self):
        a = [1, 2, 3, 4, 5, 1, 2, 3]
        self.assertAlmostEqual(weighted_kappa(a, a), 1.0)
        near = weighted_kappa(a, [2, 2, 3, 4, 5, 1, 2, 4])
        far = weighted_kappa(a, [5, 2, 3, 4, 5, 1, 2, 1])
        self.assertGreater(near, far)
        self.assertGreater(weighted_kappa(a, [2, 2, 3, 4, 5, 1, 2, 4], weights="quadratic"),
                           weighted_kappa(a, [2, 2, 3, 4, 5, 1, 2, 4], weights="linear"))

    def test_counts_and_interpret(self):
        cats, counts = counts_from_ratings([["a", "a", "b"], ["b", "b", "b"]])
        self.assertEqual((cats, counts), (["a", "b"], [[2, 1], [0, 3]]))
        self.assertEqual(interpret(0.4), "fair")
        self.assertEqual(interpret(0.85), "almost perfect")

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.csv")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("item,r1,r2\n" + "".join("%d,%s,%s\n" % (i, x, y) for i, (x, y) in enumerate(zip(A, B))))
            with redirect_stdout(io.StringIO()) as buf:
                main([p, "-r", "r1,r2"])
            self.assertIn("Cohen's kappa = 0.400", buf.getvalue())
            self.assertIn("Percent agreement: 70.0%", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
