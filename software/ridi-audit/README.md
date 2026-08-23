# ridi-audit

`ridi-audit` implements a minimal representation-aware decision reproducibility audit.

The audit does **not** replace task performance metrics. It asks a different question: when source evidence and the candidate universe are fixed, do two operational representations surface the same decision identities?

## Install locally

```bash
pip install .
```

## Minimal use

Prepare two CSV files containing the same candidate IDs and one score per candidate, then run:

```bash
ridi-audit compare --r0 r0.csv --r1 r1.csv --id-col id --score-col score --k 10 100 1000 --out audit.json
```

The output reports global Spearman agreement, RIDI, changed decision slots, top-k overlap and the score-margin stability certificate.

## Minimum reporting standard

A representation-aware audit should report: (1) frozen source evidence, (2) explicit R0/R1 intervention, (3) frozen inference procedure and candidate universe, (4) aggregate task performance, (5) decision identity at pre-specified cutoffs, and (6) an interpretable null/control. Learned systems additionally require calibration against same-representation retraining variability.

This source tree is the public release candidate prepared for the RIDI manuscript. An immutable archival identifier should be minted before journal submission.
