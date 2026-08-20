# Anti-DDI v3.0.1 data dictionary — added fields

`antiddi_v3_dataset.csv` contains the 35 columns from v2 unchanged, followed by nine v3 fields. The v3.0.1 corrective release does not change the 797-row data table; it clarifies how the semantic fields should be interpreted after withdrawal of the superseded classifier experiment.

## New v3 fields

| Column | Type | Values / format | Meaning |
|---|---|---|---|
| `knowledge_state` | categorical | `ANTI_DDI_SUPPORTED`, `ANTI_DDI_CANDIDATE_LIMITED`, `STRUCTURAL_CONTROL_ONLY`, `UNRESOLVED`, `POSITIVE_CONCERN_EXCLUDED` | Resource-level epistemic category derived from the evidence tier; **not a clinical safety certification** |
| `recommended_use` | categorical | `DEFAULT_BENCHMARK`, `SENSITIVITY_ONLY`, `EXCLUDE_FROM_BENCHMARK`, `DO_NOT_LABEL_NEGATIVE`, `EXCLUDE_POSITIVE_CONCERN` | Machine-readable research/benchmarking guidance |
| `paper5_role` | categorical | `development`, `confirmatory`, `not_used_in_paper5` | Historical role in the now-superseded classifier experiment; retained for provenance only |
| `clinical_anchor_status` | categorical | `HUMAN_NONINTERACTION_ANCHOR`, `NOT_ANCHORED` | Whether the pair was included in the targeted supportive human clinical-anchor analysis |
| `clinical_anchor_type` | string | e.g. `human_crossover_pk`, `regulatory_clinical_pharmacology` | Type of independent human/regulatory evidence |
| `clinical_anchor_source` | string | citation text | Human/regulatory source used for the supportive anchor |
| `clinical_anchor_locator` | string | DOI or official regulatory URL | Persistent or official source locator |
| `clinical_anchor_summary` | string | free text | Bounded summary of the human evidence |
| `clinical_anchor_concordance` | categorical | `CONCORDANT` or blank | Concordance with the resource state in the targeted anchor analysis |

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

`ANTI_DDI_SUPPORTED` means **supported relative to the resource's observation-opportunity and exclusion rules**. It should be read as a higher-support research candidate, not as a statement that co-prescription is safe in every patient. Direct named-pair human evidence exists only for the targeted clinical-anchor subset. T1/T2 membership by itself is not human clinical validation.

The full 797-row file intentionally retains limited evidence, unresolved cases, structural controls and exclusions so that uncertainty and contradictions remain visible. The default 538-row benchmark is therefore a research benchmark candidate set, not a clinical whitelist.

## Historical experimental fields

`paper5_split_manifest.csv` and `paper5_role` are retained solely for provenance. The four-arm classifier/RIDI experiment to which they refer was invalidated by a post-analysis adversarial audit because the evidence payload leaked class information and the intervention was not applied to the original safety controls. See `../VALIDATION_NOTICE_20260820.md`. Those fields must not be interpreted as validation status.

## Clinical-anchor table

`clinical_anchor_pairs.csv` contains eight targeted T1/T2 pairs with explicit named-pair human clinical-pharmacology or regulatory evidence consistent with no clinically meaningful interaction. The analysis is supportive and targeted; it is not an unbiased diagnostic-accuracy cohort and must not be used to claim 100% population accuracy.
