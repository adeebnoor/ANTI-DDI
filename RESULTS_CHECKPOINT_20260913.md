# Science structural-shortcuts project — results checkpoint

**Freeze date:** 2026-09-13

This file records outcomes separately from `SCIENCE_PROJECT.md`. The original hypotheses and go/no-go gates are intentionally left unchanged after outcome inspection.

## H1 / Gate 1 — cross-domain structural inflation

Status: **PASS (4/4 external relation families)**.

Degree/popularity-only structural null under conventional versus degree-matched evaluation:

| Relation family | Conventional AUC | Degree-matched AUC | Difference | Matching coverage |
|---|---:|---:|---:|---:|
| BioSNAP DTI | 0.983 | 0.620 | 0.364 | 0.599 |
| HuRI PPI | 0.928 | 0.513 | 0.415 | 1.000 |
| Hetionet Compound–treats–Disease | 0.871 | 0.519 | 0.352 | 1.000 |
| Hetionet Disease–associates–Gene | 0.876 | 0.513 | 0.363 | 1.000 |

Anti-DDI remains the motivating/seed observation and is not counted among these four external families.

## H2 / Gate 2 — learned-model sensitivity

Status: **SUPPORTED, BUT ORIGINAL STRICT GATE NOT YET DECLARED PASS**.

Across the current controlled model ladder, NeuralMF is strongly sensitive in DTI, CtD and DaG. LightGCN shows larger sensitivity in DTI and DaG but only a small change in CtD; SVD is comparatively stable. This model-by-task heterogeneity is retained rather than collapsed into a universal claim.

Selected mean AUC changes:

- DTI: NeuralMF 0.997 → 0.908; LightGCN 0.989 → 0.883; SVD 0.950 → 0.914.
- CtD: NeuralMF 0.879 → 0.560; LightGCN 0.902 → 0.882; SVD 0.717 → 0.705.
- DaG: NeuralMF 0.863 → 0.640; LightGCN 0.794 → 0.721; SVD 0.620 → 0.604.

The prespecified Gate-2 wording required at least two learned model families with meaningful sensitivity in at least three relation families. We do **not** retroactively weaken that wording.

## H3 / Gate 3a — model-rank instability

Status: **PASS as pilot**.

- DTI conventional winner: NeuralMF; degree-matched winner: SVD.
- Disease–gene conventional winner: NeuralMF; degree-matched winner: LightGCN.
- Compound–disease: LightGCN remains winner under both evaluations and serves as a useful non-reversal control.

## H5 — RIDI-inspired hypothesis-selection identity

Status: **STRONGLY SUPPORTED as pilot**.

The same frozen candidate universe is ranked by the model selected under conventional evaluation and the model selected under structure-neutralized evaluation.

| Family | Candidate pairs | Score Spearman | HT@100 | HT@500 | HT@1000 |
|---|---:|---:|---:|---:|---:|
| DTI | ~817,292 | 0.091 | 1.000 | 0.9996 | 0.9406 |
| Disease–gene | ~614,361 | 0.258 | 0.942 | 0.8988 | 0.8760 |

DTI Top-100 overlap was zero in every one of five frozen split seeds. Disease–gene HT@100 bootstrap 95% interval was 0.924–0.960.

Interpretation: benchmark design can alter model selection and thereby alter the identity of prioritized biological hypotheses. This does **not** establish which hypothesis list is biologically correct.

## H4 — temporal external-validity pilot

Status: **PASS as pilot; requires independent replication and stronger uncertainty analysis**.

Frozen BioGRID comparison:

- historical snapshot: 5.0.250,
- later snapshot: 5.0.261,
- historical human multi-validated physical network: 93,146 unique edges / 11,844 nodes,
- later-added edges with both endpoints already present historically: 5,635.

Internal historical evaluation:

| Model | Random AUC | Degree-matched AUC | Future AUC against degree-matched persistent-unobserved controls |
|---|---:|---:|---:|
| NeuralMF | 0.931 | 0.552 | 0.549 |
| LightGCN | 0.908 | 0.595 | 0.589 |
| SVD | 0.877 | 0.766 | 0.703 |

Conventional evaluation selected NeuralMF. Structure-neutralized evaluation selected SVD. On later-added edges versus degree-matched persistent-unobserved controls, the neutralized-selected model exceeded the conventional-selected model by **0.154 AUC**.

Important caveat: this first H4 test uses a degree-matched future comparison and can therefore be criticized as sharing an evaluation principle with the neutralized selection rule. A stricter non-circular test has been launched: rank the complete historical non-edge candidate universe without degree-matched control sampling and measure actual later-added edge yield at fixed top-k.

## Evidence-aware Anti-DDI axis

Status: **NEXT HARDENING STEP**.

The frozen supplementary archive contains:

- 8,094 GoldD2-derived ATC5 positive class pairs,
- 538 higher-support Anti-DDI candidate records,
- explicit evidence tiers and contradiction safeguards.

The final Science analysis will distinguish random unobserved pairs, curated counter-evidence, and degree-matched/evidence-aware comparisons. Preliminary learned-model signals are not promoted to final results until reproduced by a dedicated frozen workflow.

## Prior-art boundary

The project does not claim discovery of degree/rich-node/prior bias. Closely related prior work already includes:

- bias-aware PPI evaluation showing rich-node bias and temporal BioGRID effects;
- target-prior bias and causal debiasing in DTI;
- biomedical-KG leakage/evaluation studies comparing random/cold-start tests with independent evidence.

The intended new contribution is the joint chain:

**cross-domain structural inflation → model-rank reversal → hypothesis-selection turnover → temporal/independent scientific consequence**, with evidence-state-aware negative controls where available.

## Current claim ceiling

The current evidence supports a strong biomedical-AI evaluation paper and justifies continued testing for a Science-level contribution. It does not yet justify a final claim of universal correction or a claim that structure-neutralization always improves prospective discovery. The non-circular future-yield analysis and at least one independent temporal/real-world replication remain decisive.