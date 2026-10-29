"""Command-line interface for interrater-agreement."""
import argparse
import csv
import json

from .core import cohens_kappa, counts_from_ratings, fleiss_kappa, interpret, percent_agreement, weighted_kappa


def main(argv=None):
    ap = argparse.ArgumentParser(prog="interrater-agreement",
                                 description="Agreement between raters (columns) over items (rows) in a CSV.")
    ap.add_argument("csvfile")
    ap.add_argument("-r", "--raters", required=True, help="comma-separated rater columns (2 for Cohen, 3+ for Fleiss)")
    ap.add_argument("--weighted", choices=["linear", "quadratic"], help="weighted kappa for ordinal ratings (2 raters)")
    ap.add_argument("--order", help="comma-separated category order for weighted kappa")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    raters = [r.strip() for r in args.raters.split(",")]
    with open(args.csvfile, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    cols = [[row[r].strip() for row in rows] for r in raters]
    res = {}
    if len(raters) == 2:
        res["percent_agreement"] = percent_agreement(*cols)
        res["cohen"] = cohens_kappa(*cols)
        if args.weighted:
            order = [c.strip() for c in args.order.split(",")] if args.order else None
            res["weighted_kappa"] = weighted_kappa(*cols, categories=order, weights=args.weighted)
    complete = [list(item) for item in zip(*cols) if all(item)]
    cats, counts = counts_from_ratings(complete)
    if len(raters) >= 2 and complete:
        res["fleiss"] = fleiss_kappa(counts)
        res["categories"] = cats
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    if "cohen" in res:
        c = res["cohen"]
        print("Percent agreement: %.1f%% (n = %d)" % (100 * res["percent_agreement"], c["n"]))
        print("Cohen's kappa = %.3f, 95%% CI [%.3f, %.3f] (%s)" % (c["kappa"], c["ci"][0], c["ci"][1], interpret(c["kappa"])))
        if "weighted_kappa" in res:
            print("Weighted kappa (%s) = %.3f" % (args.weighted, res["weighted_kappa"]))
    if "fleiss" in res:
        f = res["fleiss"]
        print("Fleiss' kappa = %.3f (%s), %d items x %d raters" % (f["kappa"], interpret(f["kappa"]), f["items"], f["raters"]))
        for cat, ck in zip(res["categories"], f["category_kappa"]):
            print("  category %-12s kappa = %.3f" % (cat, ck))
    return 0
