# interrater-agreement

**Quantify how consistently coders, raters or annotators agree: percent agreement, Cohen's
kappa with CI, weighted kappa for ordinal scales, and Fleiss' kappa for three or more raters.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Qualitative coding, systematic-review screening, image annotation, clinical scoring and
machine-learning labelling all need evidence that the ratings are reliable. Percent agreement alone
overstates reliability because raters agree by chance; kappa statistics correct for that and are
expected by reviewers.

## Features

- Percent agreement and Cohen's kappa (nominal) with standard error and 95% CI
- Weighted kappa (linear or quadratic weights) with optional explicit category order
- Fleiss' kappa for any number of raters, plus per-category kappa
- Items with missing ratings are skipped for pairwise statistics
- Landis & Koch interpretation labels; CSV input (one column per rater); JSON output
- Validated against published worked examples (kappa = .40; Fleiss kappa = .210)

## Usage

```bash
pip install .
interrater-agreement screening.csv -r reviewer1,reviewer2
interrater-agreement severity.csv -r r1,r2 --weighted quadratic --order none,mild,moderate,severe
interrater-agreement labels.csv -r ann1,ann2,ann3,ann4
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
