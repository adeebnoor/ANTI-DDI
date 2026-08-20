# Anti-DDI v3 data dictionary — added fields

`antiddi_v3_dataset.csv` contains the 35 columns from v2 unchanged, followed by nine v3 fields.

## New v3 fields

| Column | Type | Values / format | Meaning |
|---|---|---|---|
| `knowledge_state` | categorical | `ANTI_DDI_SUPPORTED`, `ANTI_DDI_CANDIDATE_LIMITED`, `STRUCTURAL_CONTROL_ONLY`, `UNRESOLVED`, `POSITIVE_CONCERN_EXCLUDED` | Epistemic state implied by the evidence tier |
| `recommended_use` | categorical | `DEFAULT_BENCHMARK`, `SENSITIVITY_ONLY`, `EXCLUDE_FROM_BENCHMARK`, `DO_NOT_LABEL_NEGATIVE`, `EXCLUDE_POSITIVE_CONCERN` | Machine-readable default use |
| `paper5_role` | categorical | `development`, `confirmatory`, `not_used_in_paper5` | Role in the frozen Paper 5 candidate cohort |
| `clinical_anchor_status` | categorical | `HUMAN_NONINTERACTION_ANCHOR`, `NOT_ANCHORED` | Whether the pair was included in the post-confirmatory human clinical-anchor analysis |
| `clinical_anchor_type` | string | e.g. `human_crossover_pk`, `regulatory_clinical_pharmacology` | Type of independent human/regulatory evidence |
| `clinical_anchor_source` | string | citation text | Human/regulatory source used for the supportive anchor |
| `clinical_anchor_locator` | string | DOI or official regulatory URL | Persistent or official source locator |
| `clinical_anchor_summary` | string | free text | Bounded summary of the human evidence |
| `clinical_anchor_concordance` | categorical | `CONCORDANT` or blank | Concordance with the Anti-DDI state in the targeted anchor analysis |

## Mapping from v2 evidence tiers

| v2 tier | v3 `knowledge_state` | v3 `recommended_use` |
|---|---|---|
| `T1_wellpowered` | `ANTI_DDI_SUPPORTED` | `DEFAULT_BENCHMARK` |
| `T2_moderate` | `ANTI_DDI_SUPPORTED` | `DEFAULT_BENCHMARK` |
| `T3_limited` | `ANTI_DDI_CANDIDATE_LIMITED` | `SENSITIVITY_ONLY` |
| `T3_trivial_inert` | `STRUCTURAL_CONTROL_ONLY` | `EXCLUDE_FROM_BENCHMARK` |
| `T4_uninformative` | `UNRESOLVED` | `DO_NOT_LABEL_NEGATIVE` |
| `EXCLUDED_clinical` | `POSITIVE_CONCERN_EXCLUDED` | `EXCLUDE_POSITIVE_CONCERN` |
| `EXCLUDED_label` | `POSITIVE_CONCERN_EXCLUDED` | `EXCLUDE_POSITIVE_CONCERN` |

## Important semantic rule

A row in the 797-record full file is **not automatically an Anti-DDI**. Only records classified as `ANTI_DDI_SUPPORTED` are included in the default 538-row benchmark. The remaining records are retained because auditability requires showing limited evidence, unresolved cases, structural controls, and exclusions rather than silently deleting them.

## Paper 5 files

`paper5_split_manifest.csv` is a separate manifest because the development/confirmatory assignment is a study-design property, not a pharmacological property of a pair.

`clinical_anchor_pairs.csv` is separate because the clinical anchor analysis was post-confirmatory and supportive. It should not be merged into the prospective primary endpoint or represented as pre-registered validation.
