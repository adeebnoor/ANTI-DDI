# Anti-DDI v3.0.1 data dictionary — added fields

`antiddi_v3_dataset.csv` contains the 35 columns from v2 unchanged, followed by nine v3 fields.

## New v3 fields

| Column | Type | Values / format | Meaning |
|---|---|---|---|
| `knowledge_state` | categorical | `ANTI_DDI_CANDIDATE_HIGHER_SUPPORT`, `ANTI_DDI_CANDIDATE_LIMITED`, `STRUCTURAL_CONTROL_ONLY`, `UNRESOLVED`, `POSITIVE_CONCERN_EXCLUDED` | Conservative evidence state used for research benchmarking |
| `recommended_use` | categorical | `DEFAULT_BENCHMARK_CANDIDATE`, `SENSITIVITY_ONLY`, `EXCLUDE_FROM_BENCHMARK`, `DO_NOT_LABEL_NEGATIVE`, `EXCLUDE_POSITIVE_CONCERN` | Machine-readable default research use |
| `paper5_role` | categorical | `development`, `confirmatory`, `not_used_in_paper5` | Provenance from the superseded classifier experiment; not a current validation role |
| `clinical_anchor_status` | categorical | `HUMAN_NONINTERACTION_ANCHOR`, `NOT_ANCHORED` | Whether the pair belongs to the targeted human/regulatory clinical-anchor subset |
| `clinical_anchor_type` | string | e.g. `human_crossover_pk`, `regulatory_clinical_pharmacology` | Type of independent human/regulatory evidence |
| `clinical_anchor_source` | string | citation text | Human/regulatory source used for the supportive anchor |
| `clinical_anchor_locator` | string | DOI or official regulatory URL | Persistent or official source locator |
| `clinical_anchor_summary` | string | free text | Bounded summary of the human evidence |
| `clinical_anchor_concordance` | categorical | `CONCORDANT` or blank | Concordance in the targeted anchor subset |

## Mapping from v2 evidence tiers

| v2 tier | v3 `knowledge_state` | v3 `recommended_use` |
|---|---|---|
| `T1_wellpowered` | `ANTI_DDI_CANDIDATE_HIGHER_SUPPORT` | `DEFAULT_BENCHMARK_CANDIDATE` |
| `T2_moderate` | `ANTI_DDI_CANDIDATE_HIGHER_SUPPORT` | `DEFAULT_BENCHMARK_CANDIDATE` |
| `T3_limited` | `ANTI_DDI_CANDIDATE_LIMITED` | `SENSITIVITY_ONLY` |
| `T3_trivial_inert` | `STRUCTURAL_CONTROL_ONLY` | `EXCLUDE_FROM_BENCHMARK` |
| `T4_uninformative` | `UNRESOLVED` | `DO_NOT_LABEL_NEGATIVE` |
| `EXCLUDED_clinical` | `POSITIVE_CONCERN_EXCLUDED` | `EXCLUDE_POSITIVE_CONCERN` |
| `EXCLUDED_label` | `POSITIVE_CONCERN_EXCLUDED` | `EXCLUDE_POSITIVE_CONCERN` |

## Critical semantic boundary

T1/T2 status is **not direct clinical proof of non-interaction**. It indicates comparatively greater observation opportunity under the resource's prespecified co-report/power rules and makes a row eligible as a research benchmark candidate. Only pairs carrying a separate human/regulatory anchor should be described as clinically anchored. Database absence, low disproportionality, or T1/T2 membership alone must never be translated into a prescribing-safety claim.

A row in the 797-record full file is therefore not automatically an Anti-DDI. The default 538-row file contains `ANTI_DDI_CANDIDATE_HIGHER_SUPPORT` records intended for research benchmarking with the stated limitations. The remaining records are retained for auditability rather than silently deleted.

## Provenance of the superseded classifier experiment

`paper5_split_manifest.csv` and `paper5_role` are retained only to preserve the provenance of a classifier/RIDI experiment withdrawn after a post-analysis adversarial audit identified label leakage and an invalid safety comparison. They are not current validation assets. See `../VALIDATION_NOTICE_20260820.md`.

## Clinical anchors

`clinical_anchor_pairs.csv` is a targeted supportive subset with named-pair human clinical-pharmacology or regulatory evidence. It is not an unbiased diagnostic-accuracy sample and should not be used to estimate the sensitivity or specificity of the 538-pair candidate benchmark.
