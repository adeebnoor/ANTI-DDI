# ridi-audit

`ridi-audit` implements a minimal representation-aware **decision reproducibility** audit.

Performance metrics answer whether a system remains accurate on average. `ridi-audit` asks a different question: when source evidence and the candidate universe are fixed, do two operational representations surface the same decision identities?

## Install locally

```bash
pip install .
```

## One-command audit

Prepare two CSV files containing the same candidate IDs and one score per candidate, then run:

```bash
ridi-audit compare \
  --r0 r0.csv \
  --r1 r1.csv \
  --id-col id \
  --score-col score \
  --k 10 100 1000 \
  --out audit.json \
  --report audit.md
```

The JSON output is machine-readable. The Markdown report is designed for human review and records:

- global Spearman agreement;
- RIDI at every pre-specified cutoff;
- changed decision slots and overlap;
- the top-k score margin `gamma_k`;
- the maximum paired score perturbation `epsilon`; and
- whether the sufficient certificate `gamma_k > 2 epsilon` guarantees top-k stability.

## Minimum reporting standard

A representation-aware audit should report:

1. frozen source evidence `S`;
2. an explicit, scientifically justified `R0 -> R1` representation intervention;
3. frozen inference procedure `F`, candidate universe/decision rule `C`, and pre-specified cutoffs;
4. conventional task performance and global score/rank agreement;
5. decision identity using RIDI and changed slots;
6. an invariance/null control expected to return zero turnover;
7. the margin certificate when paired scores are available; and
8. for learned systems, calibration against same-representation retraining variability `Z`.

The complete checklist is in `RIDI_AUDIT_MINIMUM_REPORTING_STANDARD_v1.md`.

## Interpretation discipline

A non-zero RIDI establishes decision-identity turnover between the supplied pipeline realizations. It does **not** by itself establish that representation caused the turnover when training stochasticity or other uncontrolled changes are present. Conversely, a high AUROC, MRR or rank correlation does not certify top-k identity.

This source tree is the public release candidate accompanying the RIDI manuscript. Exact commit provenance should be reported when the package is used in a scientific analysis.
