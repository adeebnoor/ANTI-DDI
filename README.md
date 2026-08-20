# Anti-DDI v3.0.1 — evidence states for drug non-interaction

**797 audited pair records · 538 T1/T2 higher-support benchmark candidates · 8 targeted human/regulatory illustrations**

Anti-DDI starts from one design principle: **a missing edge is an observation about a database; an Anti-DDI state is a claim about evidence.** Drug–drug interaction (DDI) informatics represents reasons for concern explicitly, but evidence against a clinically meaningful interaction is often collapsed with sparse evidence, incomplete coverage, or simple absence. Anti-DDI keeps those states separate.

> **DDI-supported ≠ unresolved ≠ Anti-DDI candidate**

The resource is for research and decision-support assurance. It is **not** a universal safety list.

## Validation notice

A post-analysis adversarial audit on 20 August 2026 identified label leakage in an experimental four-arm text-classifier/RIDI demonstration that had briefly been documented in v3.0.0. The associated efficacy and safety claims are withdrawn and are **not evidence for this resource**. See [`VALIDATION_NOTICE_20260820.md`](VALIDATION_NOTICE_20260820.md). The audited dataset, evidence tiers, graph audit, label exclusions and clinical-anchor source table are unaffected.

## What this resource provides

| File | Rows | Intended use |
|---|---:|---|
| `data/antiddi_v3_dataset.csv` | 797 | Complete audit/evidence-state table, including excluded and unresolved records |
| `data/antiddi_v3_benchmark.csv` | 538 | Default research benchmark candidates: T1 + T2 only |
| `data/degree_bias_atc5_replicates.csv` | 20 | Reproducible ATC5 structural-bias output |
| `data/degree_bias_atc5_summary.json` | — | Frozen summary of the ATC5 structural-bias analysis |
| `data/figure2_vertex_cover_degrees.csv` | 13 | Source data for the 13-drug vertex-cover figure |
| `data/FROZEN_REFERENCE_MANIFEST.md` | — | Row count, derivation and SHA-256 of the frozen 8,094-pair ATC5 positive reference |
| `data/clinical_anchor_pairs.csv` | 8 | Targeted illustrative human/regulatory source anchors; not a validation cohort |
| `data/antiddi_v2_dataset.csv` | 797 | Immutable v2 audit table retained for historical reproducibility |

The exact frozen `goldd2_atc5_positive_reference.csv` is included in the manuscript Supplementary Code and Data archive; its SHA-256 is recorded in `data/FROZEN_REFERENCE_MANIFEST.md`. The original `data/paper5_split_manifest.csv` is retained only as provenance for the superseded classifier experiment; it is not a validation asset.

## Evidence-state semantics

| State | Interpretation | Default use |
|---|---|---|
| `ANTI_DDI_CANDIDATE_HIGHER_SUPPORT` | T1/T2 candidate with greater observation opportunity under the resource rules | Default research benchmark candidate |
| `ANTI_DDI_CANDIDATE_LIMITED` | T3 candidate with limited observation opportunity | Sensitivity analysis only |
| `STRUCTURAL_CONTROL_ONLY` | Trivial/inert structural control | Exclude from default benchmark |
| `UNRESOLVED` | Too little co-exposure to support a negative claim | Do not label negative |
| `POSITIVE_CONCERN_EXCLUDED` | Clinical or regulatory concern identified | Never use as Anti-DDI |

**T1/T2 does not mean clinically proven non-interacting or safe.** It encodes greater observation opportunity under the stated statistical setting. Direct named-pair human or regulatory evidence is carried separately. A T1/T2 row should therefore be described as a **higher-support Anti-DDI candidate**, not as a clinically validated negative.

This framing yields three operational rules:

1. database absence is not a negative label;
2. unresolved evidence remains explicit rather than being forced into the negative class; and
3. credible positive clinical/regulatory evidence overrides any de-escalating interpretation.

## Audit and structure

The retracted predecessor file contained 827 rows. The current audit identified 902 defect instances affecting 782 rows and reduced the file to 797 distinct unordered pairs over 161 drug names. A 13-drug greedy vertex cover touches all 797 pairs; the remaining 148 drugs form an independent set. This structure is a major benchmark confounder and is disclosed rather than hidden.

The author of the current resource was a co-author and corresponding author of the retracted predecessor article. The predecessor is used only as an audit/lineage object; current evidence states are not inherited from its labels. See [`DISCLOSURE_retraction.md`](DISCLOSURE_retraction.md).

## Observation-opportunity tiers

For each pair the resource records FAERS co-report count and a minimum detectable reporting-odds-ratio calculation under a stated design parameter (`p0=0.01`, two-sided alpha 0.05, power 0.80). This is a **statistical opportunity measure**, not proof of non-interaction and not a clinical safety estimate. Sensitivity analysis shows that varying `p0` from 0.001 to 0.05 changes the T1/T2 split but leaves the combined T1+T2 count at 538 (`data/p0_sensitivity.csv`).

The historical FAERS query metadata preserve the denominator of 20,328,575 reports but not a source-export date. That missing timestamp is a limitation and is not reconstructed retrospectively.

## Reproducible structural-bias diagnostic

`analysis/run_degree_bias_atc5.py` asks whether a popularity-only score can distinguish positives from nominal negatives because of drug/class degree rather than pair-specific pharmacology.

Using the frozen 8,094-pair GoldD2-derived ATC level-5 positive reference and ATC5 projections of the T1/T2 Anti-DDI candidates:

- 1,080 unique curated ATC5 class pairs were generated;
- 88 class pairs overlapping the positive reference were excluded;
- 992 curated ATC5 class pairs remained;
- across 20 seeds, popularity-only AUC was **0.908 ± 0.006** against random unlabelled negatives and **0.900 ± 0.005** against curated Anti-DDI class pairs;
- after degree matching, AUC fell to **0.501 ± 0.004**.

The conceptual point is not that a better classifier was built. It is that **a benchmark can appear pharmacologically informative when it is structurally predictable**. Degree/popularity controls are therefore part of the evidence design, not merely a modeling detail.

This is a **structural-bias diagnostic at ATC5 class level**, not clinical validation of any drug pair.

Reproduce after placing the checksum-verified frozen CSV from the Supplementary Code and Data archive at `data/goldd2_atc5_positive_reference.csv`:

```bash
python analysis/run_degree_bias_atc5.py \
  --positives data/goldd2_atc5_positive_reference.csv \
  --antiddi data/antiddi_v2_dataset.csv \
  --out /tmp/degree_bias_atc5_replicates.csv \
  --summary /tmp/degree_bias_atc5_summary.json
```

The generated output should match the shipped `data/degree_bias_atc5_replicates.csv` and `data/degree_bias_atc5_summary.json`.

## Structured-label screen and clinical anchoring

The shipped structured-label screen contains five positive interaction signals: three were assigned `EXCLUDED_label` and two were already clinically excluded. Four rows contain explicit non-interaction statements. This screen is a contradiction safeguard, not a comprehensive drug-information compendium review.

Eight retained T1/T2 candidates are documented as **targeted illustrative anchors** because named-pair human clinical-pharmacology or regulatory sources reported no clinically meaningful interaction or no clinically relevant effect. They are outcome-selected and hub-concentrated, so they are **not** a diagnostic-accuracy sample or a population concordance estimate. Three were already identified by the structured-label screen; five add direct source anchoring not captured by that screen. See `data/clinical_anchor_pairs.csv`.

## Recommended use

1. Use `data/antiddi_v3_benchmark.csv` only as a research benchmark candidate set.
2. Preserve evidence tiers and report structural degree/popularity controls.
3. Never convert `UNRESOLVED` rows into negatives.
4. Never use excluded clinical/label rows as negatives.
5. Do not describe dataset membership as authorization to co-prescribe or suppress an alert.
6. Report the exact release/commit and checksum.
7. Validate any downstream decision system independently; the superseded classifier experiment is not validation evidence.

## Reproducibility

```bash
python validate.py
python build_v3.py
python semantic_harden_v3.py
python validate_v3.py
```

The ATC5 structural diagnostic additionally requires the checksum-verified frozen positive-reference CSV identified in `data/FROZEN_REFERENCE_MANIFEST.md`.

## License

- Code: MIT
- Data and documentation: CC BY 4.0
- Third-party identifiers/source material remain subject to their original terms.

## Clinical boundary

Anti-DDI is a research evidence framework. It is **not a clinical safety list** and does not substitute for current drug-information sources, clinician/pharmacist judgment, patient context, dose, route, timing, or monitoring.
