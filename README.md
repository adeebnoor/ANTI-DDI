# Anti-DDI v3 — an evidence framework and benchmark resource for drug non-interaction

**Version 3.0.0 · 797 audited pair records · 538 default benchmark Anti-DDI records · 8 human clinical anchors**

Anti-DDI treats **evidence against a clinically meaningful drug–drug interaction as an explicit knowledge state**. It is not the same as a pair being absent from a DDI database, and it is not a universal safety label.

> **DDI-supported ≠ unresolved ≠ Anti-DDI**

The repository provides an auditable dataset, evidence tiers, degree-bias controls, a prospective Paper 5 benchmark split, human clinical-pharmacology anchors, and reproducibility tools.

## The construct

An **Anti-DDI** is an evidence-supported representation that a specified drug pair lacks a clinically meaningful interaction with respect to the evidence context evaluated. It is distinct from:

- **documented DDI:** evidence supports a clinically meaningful interaction;
- **unresolved:** evidence is absent, insufficient, conflicting, or underpowered;
- **Anti-DDI:** affirmative counter-evidence supports non-interaction under a defined evidence context.

Anti-DDI does **not** mean "safe in every patient", and the resource does not authorize prescribing decisions.

## What changed from v2

v2 was released primarily as a tiered negative-control resource. v3 preserves every original v2 column and row, but makes the evidence-state interpretation explicit and adds:

1. `knowledge_state` — separates supported Anti-DDI, limited candidates, unresolved records, structural controls, and excluded positive-concern pairs;
2. `recommended_use` — machine-readable guidance for benchmarking;
3. `paper5_role` — identifies the frozen development/confirmatory Anti-DDI records used in the prospective RIDI study;
4. human clinical-anchor metadata for 8 T1/T2 pairs;
5. a 538-row ready-to-use default benchmark export;
6. the Paper 5 split manifest and clinical-anchor table.

The original `data/antiddi_v2_dataset.csv` should remain in the repository unchanged for historical reproducibility.

## Data products

| File | Rows | Intended use |
|---|---:|---|
| `data/antiddi_v3_dataset.csv` | 797 | Complete evidence-state resource; includes excluded and unresolved states for auditability |
| `data/antiddi_v3_benchmark.csv` | 538 | Default machine-learning benchmark: T1 + T2 only |
| `data/paper5_split_manifest.csv` | 214 | Frozen 40-development / 174-confirmatory Anti-DDI split used in Paper 5 |
| `data/clinical_anchor_pairs.csv` | 8 | Post-confirmatory human clinical-pharmacology anchors |
| `data/antiddi_v2_dataset.csv` | 797 | Immutable v2 historical dataset; retained for reproducibility |

## Evidence-state semantics

| `knowledge_state` | Source tier(s) | Interpretation | Default use |
|---|---|---|---|
| `ANTI_DDI_SUPPORTED` | T1, T2 | Evidence supports a non-interaction state at the stated evidence strength | Default benchmark |
| `ANTI_DDI_CANDIDATE_LIMITED` | T3 limited | Evidence is too weak for the default benchmark | Sensitivity analyses only |
| `STRUCTURAL_CONTROL_ONLY` | T3 trivial/inert | Useful as a structural control, not as clinical evidence | Exclude from default benchmark |
| `UNRESOLVED` | T4 | Too little co-exposure to make a negative claim | Do not label negative |
| `POSITIVE_CONCERN_EXCLUDED` | clinical/label exclusions | Positive clinical or regulatory concern was identified | Never use as Anti-DDI |

The key rule is:

> **Absence of DDI evidence is not evidence of non-interaction.**

## Human clinical anchoring

Paper 5 added a post-confirmatory, supportive clinical-anchor analysis. Eight retained T1/T2 Anti-DDIs had explicit named-pair human DDI evidence reporting no clinically meaningful interaction, no meaningful PK/PD change, or no clinically relevant effect. All 8 were concordant with the Anti-DDI state.

This is **supportive clinical anchoring, not an unbiased diagnostic-accuracy cohort**. The targeted sample is small and was added after the prospective computational confirmation; it must not be used to claim 100% population accuracy.

## Paper 5: prospective RIDI validation

Paper 5 prospectively evaluated Anti-DDI in a frozen four-arm screening experiment:

- **A:** raw representation
- **B:** canonicalization
- **C:** Anti-DDI evidence without forced canonicalization
- **D:** canonicalization + Anti-DDI evidence

Representation-induced decision instability (RIDI) was measured as:

`RIDI@k = 1 - Jaccard(top-k decisions under representation x, top-k decisions under representation y)`

In the primary backend, RIDI@20 was 0.746 in A, 0.308 in B, and 0.243 in D. The prespecified incremental B−D effect was 0.065 (21.1% relative point-estimate reduction), but the 95% paired-bootstrap interval crossed no improvement. A second frozen backend reproduced the positive direction but reached a floor.

The safety controls were preserved in the computational benchmark: all 200 confirmed interactions remained detected and none of three regulatory overrides was suppressed.

The correct conclusion is therefore **not** that Anti-DDI uniformly improves every screening model. Anti-DDI improves the epistemic quality of the input; downstream decision effects remain backend-dependent and must be validated at the complete-pipeline level.

## Quickstart

```python
import pandas as pd

# Recommended default benchmark: supported Anti-DDI states only
anti = pd.read_csv("data/antiddi_v3_benchmark.csv")

print(anti.shape)                 # (538, 44)
print(anti["knowledge_state"].unique())
# ['ANTI_DDI_SUPPORTED']
```

For a full audit:

```python
full = pd.read_csv("data/antiddi_v3_dataset.csv")
print(full["knowledge_state"].value_counts())
```

For exact Paper 5 replication:

```python
split = pd.read_csv("data/paper5_split_manifest.csv")
development = split.query("split == 'development'")
confirmatory = split.query("split == 'confirmatory'")
```

## Recommended evaluation practice

If Anti-DDI is used as a negative class:

1. use `antiddi_v3_benchmark.csv` by default;
2. preserve evidence tiers in analysis;
3. report drug-degree or popularity structure;
4. perform degree-matched or otherwise structure-aware negative sampling;
5. never convert `UNRESOLVED` records into negatives;
6. never use `POSITIVE_CONCERN_EXCLUDED` records as negatives;
7. report the exact Anti-DDI release version and checksum;
8. do not describe the dataset as a prescribing safety list.

## Dataset structure

v3 retains all 35 v2 columns and appends nine semantic/reproducibility fields:

- `knowledge_state`
- `recommended_use`
- `paper5_role`
- `clinical_anchor_status`
- `clinical_anchor_type`
- `clinical_anchor_source`
- `clinical_anchor_locator`
- `clinical_anchor_summary`
- `clinical_anchor_concordance`

See `data/DATA_DICTIONARY_v3.md`.

## Reproducibility

Run the original v2 validation harness and the v3 semantic checks:

```bash
python validate.py
python validate_v3.py
```

The GitHub Actions workflow should run both.

## Provenance and retraction disclosure

This repository supersedes a retracted predecessor publication. The predecessor file is retained only for historical lineage and audit. The candidate-pair lineage is disclosed, but current v2/v3 evidence states are not inherited from the predecessor labels; they are re-evaluated under the current evidence rules. `DISCLOSURE_retraction.md` states the retraction notice accurately and defines this provenance boundary.

## License

- Code: MIT
- Data and documentation: CC BY 4.0
- Third-party identifiers and source material remain subject to their original terms.

## Citation

Use `CITATION.cff`. After creating the v3.0.0 GitHub release, archive the release in Zenodo and add the minted DOI to this README and `CITATION.cff`.

## Clinical boundary

Anti-DDI is a research evidence framework. It is **not** a clinical safety list and does not substitute for a current drug-information source, pharmacist/physician judgment, patient context, dose, route, timing, or monitoring.
