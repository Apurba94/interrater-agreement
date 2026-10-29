"""Percent agreement, Cohen's kappa (with SE/CI), weighted kappa and Fleiss' kappa."""
import math
import statistics
from collections import Counter

_Z = statistics.NormalDist().inv_cdf(0.975)


def _pairs(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x not in (None, "") and y not in (None, "")]
    if not pairs:
        raise ValueError("no items rated by both raters")
    return pairs


def percent_agreement(a, b):
    p = _pairs(a, b)
    return sum(1 for x, y in p if x == y) / len(p)


def cohens_kappa(a, b):
    """Cohen's kappa for two raters (nominal categories). SE from Fleiss, Cohen & Everitt (1969) simple form."""
    p = _pairs(a, b)
    n = len(p)
    cats = sorted({x for x, _ in p} | {y for _, y in p}, key=str)
    ca, cb = Counter(x for x, _ in p), Counter(y for _, y in p)
    po = sum(1 for x, y in p if x == y) / n
    pe = sum(ca[c] * cb[c] for c in cats) / (n * n)
    if pe == 1:
        return {"kappa": 1.0, "po": po, "pe": pe, "n": n, "se": 0.0, "ci": (1.0, 1.0)}
    k = (po - pe) / (1 - pe)
    se = math.sqrt(po * (1 - po) / (n * (1 - pe) ** 2))
    return {"kappa": k, "po": po, "pe": pe, "n": n, "se": se, "ci": (k - _Z * se, k + _Z * se)}


def weighted_kappa(a, b, categories=None, weights="quadratic"):
    """Weighted kappa for ordinal ratings. categories: ordered list (default: sorted numeric/str values)."""
    p = _pairs(a, b)
    cats = list(categories) if categories else sorted({x for x, _ in p} | {y for _, y in p},
                                                     key=lambda v: (float(v) if str(v).replace(".", "", 1).lstrip("-").isdigit() else math.inf, str(v)))
    idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    if k < 2:
        return 1.0
    n = len(p)
    obs = [[0.0] * k for _ in range(k)]
    for x, y in p:
        obs[idx[x]][idx[y]] += 1 / n
    ra = [sum(row) for row in obs]
    rb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    w = [[(abs(i - j) / (k - 1)) ** (2 if weights == "quadratic" else 1) for j in range(k)] for i in range(k)]
    do = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    de = sum(w[i][j] * ra[i] * rb[j] for i in range(k) for j in range(k))
    return 1 - do / de if de else 1.0


def counts_from_ratings(ratings):
    """ratings: list of per-item lists of category labels (one per rater). Returns (categories, count matrix)."""
    cats = sorted({c for item in ratings for c in item if c not in (None, "")}, key=str)
    return cats, [[sum(1 for c in item if c == cat) for cat in cats] for item in ratings]


def fleiss_kappa(counts):
    """Fleiss' kappa from an items x categories matrix of rater counts (same number of raters per item)."""
    N = len(counts)
    n = sum(counts[0])
    if any(sum(r) != n for r in counts):
        raise ValueError("every item must be rated by the same number of raters")
    if n < 2:
        raise ValueError("need at least two raters")
    k = len(counts[0])
    pj = [sum(r[j] for r in counts) / (N * n) for j in range(k)]
    Pi = [(sum(c * c for c in r) - n) / (n * (n - 1)) for r in counts]
    Pbar = statistics.fmean(Pi)
    Pe = sum(p * p for p in pj)
    kappa = (Pbar - Pe) / (1 - Pe) if Pe != 1 else 1.0
    return {"kappa": kappa, "P_observed": Pbar, "P_expected": Pe, "items": N, "raters": n,
            "category_kappa": [((sum(r[j] * r[j] for r in counts) - N * n * pj[j] * (1 + (n - 1) * pj[j])) /
                                (N * n * (n - 1) * pj[j] * (1 - pj[j]))) if 0 < pj[j] < 1 else float("nan")
                               for j in range(k)]}


def interpret(k):
    """Landis & Koch (1977) benchmarks."""
    for lim, lab in ((0.81, "almost perfect"), (0.61, "substantial"), (0.41, "moderate"), (0.21, "fair"),
                     (0.0, "slight")):
        if k >= lim:
            return lab
    return "poor"
