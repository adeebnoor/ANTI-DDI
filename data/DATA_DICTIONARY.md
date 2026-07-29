# Data dictionary — `antiddi_v2_dataset.csv`

797 rows × 35 columns. One row per **unordered** drug pair. Header row present,
UTF-8, comma-separated, `.` decimal separator, no thousands separator, no quoted
fields required. Booleans are written as the literal strings `True` / `False`.
Missing values are written as empty fields and read as `NaN`.

The file is an **evaluation resource**. A row's presence records that no
interaction evidence was found for that pair under the procedure described
below, together with a quantification of how much evidence there was to find.
It is not a statement that the pair is safe to co-prescribe, and no row of this
file licenses a clinical decision.

Every derived column below is reproduced exactly from the shipped raw columns by
`antiddi/evidence.py`; `validate.py` asserts this for all 797 rows.

---

## 1. Identifiers and pair members

| Column | Type | Missing | Permitted values | Provenance |
|---|---|---|---|---|
| `pair_id` | string | 0 | `ADDI2-NNNN`, zero-padded to 4 digits, `ADDI2-0001` … `ADDI2-0797`; unique | Assigned in this release. Ordered by descending `faers_coreports` within the clinically excluded block first, then the remainder; treat the numbering as an opaque key, not as a rank. |
| `drug_a` | string | 0 | Lower-case ingredient name as it appeared in the v1 file | Carried forward verbatim from the predecessor file so the audit trail is intact. **Not normalised** — see §5 and `audit_drug_normalization.csv`. Canonicalise with strip + case-fold before joining. |
| `drug_b` | string | 0 | as `drug_a` | as `drug_a` |

Pairs are unordered: the assignment of a drug to `drug_a` versus `drug_b`
carries no meaning, and a consumer must key on the sorted tuple. The v1 file's
30 duplicated rows were all order-reversals of this kind, which is why this
release deduplicates on the unordered set.

161 distinct drug names appear across the two columns.

---

## 2. FAERS evidence layer

Source: openFDA FAERS drug-event endpoint, count queries. Denominator for every
expected count: **20,328,575** total reports (`antiddi.FAERS_DENOMINATOR`).
openFDA count queries cap at `limit=500` without an API key.

| Column | Type | Units | Missing | Range in file | Definition and provenance |
|---|---|---|---|---|---|
| `faers_reports_a` | integer | reports | 0 | 965 – 786,855 | Total FAERS reports naming `drug_a`, at any role. Retrieved per ingredient for all 161 drugs. |
| `faers_reports_b` | integer | reports | 0 | 965 – 786,855 | As above for `drug_b`. |
| `faers_coreports` | float (integer-valued) | reports | 0 | 0 – 21,095 | Reports naming **both** drugs. Retrieved per pair for all 797 pairs. Stored as float only because the column shares a dtype with the derived columns; all values are whole numbers. Distribution across the 797 pairs: median 332, mean 1,150.6, SD 2,434.9. |
| `faers_expected` | float | reports | 0 | 0.672 – 7,120.1 | `faers_reports_a × faers_reports_b / 20,328,575` — the co-report count expected if the two drugs were reported independently. |
| `obs_exp_ratio` | float | dimensionless | 0 | 0.0 – 51.94 | `faers_coreports / faers_expected`. A **co-exposure** measure, not a signal: it is dominated by shared indication and co-prescribing practice. Do not read it as evidence of interaction. |

### `min_detectable_ror`

| Column | Type | Units | Missing | Range in file |
|---|---|---|---|---|
| `min_detectable_ror` | float, or `inf` | dimensionless (odds ratio) | 0 (90 rows are `inf`) | 1.30 – 28.80, plus `inf` |

The smallest reporting odds ratio the pair's co-exposure count could have
detected, had an interaction existed. Computed by
`antiddi.evidence.min_detectable_ror(n_coreports, p0=0.01, alpha=0.05,
power=0.80)`:

- two-sided normal approximation, `alpha = 0.05`, `power = 0.80`;
- assumed background adverse-event rate per report `p0 = 0.01`;
- for a candidate ROR `r`, the co-exposed rate is `p1 = r·p0 / (1 + p0·(r−1))`,
  and with `pbar = (p0 + p1)/2` the pair is detectable when

  ```
  (p1 − p0) · sqrt(n_coreports)  ≥  z(1−alpha/2)·sqrt(2·pbar·(1−pbar))
                                  + z(power)·sqrt(p0·(1−p0) + p1·(1−p1))
  ```

- both arms are taken to have `n_coreports` reports — the co-exposed stratum is
  the binding constraint, which is the conservative reading of available power;
- the smallest `r` on a **0.05 grid** starting at 1.05 that satisfies the
  inequality is reported. The grid step is part of the definition: changing it
  changes the values;
- search ceiling **30.0**. A pair whose smallest detectable effect exceeds 30 is
  reported as `inf` rather than carrying an implausibly precise large number.
  `n_coreports ≤ 0` also returns `inf`.

`inf` means *no interaction of any plausible size could have been detected at
this co-exposure count*. It is the column's most important value: it marks where
the resource declines to make a negative claim.

---

## 3. Structural and exclusion flags

| Column | Type | Missing | Permitted values | Definition and provenance |
|---|---|---|---|---|
| `n_anchor_drugs` | integer | 0 | `1`, `2` (748 rows are 1; 49 rows are 2; **no row is 0**) | Number of the pair's two drugs that belong to the 13-drug anchor set `antiddi.ANCHOR_DRUGS`: sevelamer, ustekinumab, dalteparin, atenolol, levetiracetam, liraglutide, heparin, hydrocodone, dextromethorphan, citalopram, conjugated estrogens, chlorpheniramine, lactulose. That set is a greedy vertex cover of the 797-pair graph, so every pair contains at least one anchor and the other 148 drugs form an independent set. Shipped because it is the structural artefact a consumer most needs to guard against: a 13-feature identity lookup reproduces every negative label in the file. |
| `both_pk_inert` | boolean | 0 | `True` (51 rows), `False` | Both drugs belong to a class for which a pharmacokinetic interaction mechanism cannot in principle be posited — a non-absorbed binder or a monoclonal antibody cleared by proteolytic catabolism. Such pairs are negative by construction rather than by evidence, and are tiered `T3_trivial_inert` so they cannot inflate a benchmark. |
| `excluded_clinical` | boolean | 0 | `True` (30 rows), `False` | The pair was excluded on clinical grounds during this release's review: 11 same-pharmacological-class or mechanistically redundant pairs and 21 implausible-co-prescription pairs (8 renal-population conflicts, 12 route-precluded, 1 age/sex-exclusive). Two of the 11 — hydrocodone × zopiclone and hydrocodone × zaleplon — are opioid plus Z-drug combinations carrying an **FDA boxed warning** for respiratory depression and death. **These 30 rows are shipped so that the exclusion is auditable. They are never part of a usable negative set,** and `antiddi.benchmark` drops them under every tier selector, including `all`. |
| `name_defect_v1` | boolean | 0 | `True` (110 rows), `False` | At least one drug name in the row carried a name-integrity defect in the predecessor file — truncation, brand name, class term, ambiguity, or nomenclature inconsistent with the stated source list. Per-name detail is in `audit_drug_normalization.csv`; per-row detail in `audit_defects.csv`. |

---

## 4. Cross-references

| Column | Type | Missing | Format | Provenance |
|---|---|---|---|---|
| `rxcui_a`, `rxcui_b` | float (integer-valued) | 5 each | RxNorm concept identifier, 161 – 847,083 | RxNorm. Float dtype is an artefact of the missing values; values are integers. Missing where the v1 name does not resolve to a single RxNorm concept. |
| `atc_a`, `atc_b` | string | 0 | One or more ATC codes, **semicolon-delimited**, e.g. `N02AJ;R05DA`. 352 rows carry a multi-code `atc_a` | ATC via RxClass / ChEMBL. Split on `;` before use; a single string is not a single classification. |
| `drugbank_a` | string | 151 | `DBNNNNN` | DrugBank identifier where a unique mapping exists. |
| `drugbank_b` | string | 431 | `DBNNNNN` | As above. The high missingness is a property of the mapping, not of the pair. |
| `chembl_a`, `chembl_b` | string | 0 | `CHEMBLNNNN…` | ChEMBL identifier. |

Cross-reference columns are provided for joining only. A pair's tier does not
depend on them, and a missing identifier does not weaken the row's evidence.

---

## 5. Name integrity — read before joining

Names are carried forward from the predecessor file **unmodified**, deliberately,
so that the audit is reproducible from the shipped data. 152 of the 161 names
resolve exactly to an RxNorm ingredient. The nine that do not are documented in
full in `audit_drug_normalization.csv`; the ones that will bite a naive join:

- `glyceryl trini.` — truncated; the intended ingredient is nitroglycerin.
- `penicillin` — a class term that does not distinguish penicillin G from
  penicillin V.
- `dextromethorph` — truncated.
- `humalog`, `lantus` — brand names, not ingredients.
- `paracetamol`, `salbutamol` — INN forms, inconsistent with the USAN-based
  source list the predecessor file cited.
- `isosorbide` — **resolves successfully but wrongly**, to the osmotic diuretic
  rather than the intended antianginal nitrate. This is the most dangerous
  defect in the file precisely because automated resolution returns a confident
  wrong answer rather than a failure. Any pipeline that maps these names
  automatically must special-case it.

81 v1 rows also carried stray whitespace and 37 inconsistent case. Canonicalise
with strip + case-fold (`antiddi.benchmark` does this internally).

---

## 6. `evidence_tier` — the exact decision rules

| Column | Type | Missing | Permitted values |
|---|---|---|---|
| `evidence_tier` | string | 0 | `T1_wellpowered`, `T2_moderate`, `T3_limited`, `T3_trivial_inert`, `T4_uninformative`, `EXCLUDED_clinical` |

Implemented by `antiddi.evidence.assign_tier(row)`. The rules are evaluated
**strictly in this order** and the first match wins:

1. `excluded_clinical` is `True` → **`EXCLUDED_clinical`**
2. `faers_coreports < 25` → **`T4_uninformative`**
3. `both_pk_inert` is `True` → **`T3_trivial_inert`**
4. `faers_coreports ≥ 500` **and** `min_detectable_ror ≤ 3.0` → **`T1_wellpowered`**
5. `faers_coreports ≥ 100` → **`T2_moderate`**
6. otherwise → **`T3_limited`**

Rule 1 precedes every evidence rule: a pair excluded on clinical grounds stays
excluded however well powered it is. Rule 2 precedes rule 3 so that a pair with
too little co-exposure to support any statement is reported as uninformative
rather than as trivially inert.

### Tier counts and summary statistics (all 797 rows)

| Tier | Pairs | Median co-reports | Median min. detectable ROR | What the tier means |
|---|---:|---:|---:|---|
| `T1_wellpowered` | 217 | 2,020 | 2.15 | Substantial real-world co-exposure; a moderate interaction would have been detectable and was not detected. The strongest negative evidence in the resource. |
| `T2_moderate` | 321 | 291 | 5.15 | Enough co-exposure to exclude a large effect, not a moderate one. |
| `T3_limited` | 106 | 59 | 17.15 | Only a very large effect was detectable. Use as a negative only with the limitation stated. |
| `T3_trivial_inert` | 44 | 623 | 3.40 | Both drugs pharmacokinetically inert by class: negative by construction, not by evidence. Excluding this tier from a benchmark prevents trivially separable pairs from inflating performance. |
| `T4_uninformative` | 76 | 11.5 | `inf` | Co-exposure below 25 reports; **no interaction could have been detected.** Not a negative claim — a documented absence of evidence. |
| `EXCLUDED_clinical` | 30 | — | — | Excluded on clinical grounds. Shipped for auditability only; **never** part of a usable negative set. |
| `EXCLUDED_label` | 3 | 165 | 7.50 | Excluded on FDA structured-product-label evidence (Sect. 3.3). Shipped for auditability only; **never** part of a usable negative set. |

**The usable benchmark set is `T1_wellpowered + T2_moderate` = 538 pairs**, the
default of `antiddi.benchmark.evaluate(negatives="T1+T2")`.

---

## 7. Supporting files shipped alongside

| File | Rows | Contents |
|---|---:|---|
| `benchmark_replicates.csv` | 20 | One row per random-seed replicate of the headline experiment. Columns: `random`, `curated`, `deg_matched` (AUC of a drug-popularity-only heuristic against each negative arm) and `n_matched` (positives retained by degree matching in that replicate). Means: 0.9339, 0.9447, 0.4957; SDs 0.0068, 0.0041, 0.0040. |
| `signal_detection_t1.csv` | 19,633 | Pair × adverse-event Omega shrinkage disproportionality output for the well-powered pairs and the positive-control pairs. Columns: `drug_a`, `drug_b`, `ae`, `n_obs`, `n_exp`, `omega`, `omega_025`, `co_reports`. `omega_025` is the 2.5th percentile of the gamma posterior, computed on **disjoint** strata (A-not-B, B-not-A, A-and-B) with `g11 = n_AB × max(p_A, p_B)`. Shipped because the analysis it supports is a **negative** result: disproportionality did not discriminate known-interacting pairs from candidate non-interacting pairs (see README §"What we could not do"). |
| `audit_defects.csv` | 902 | One row per defect instance found in the predecessor 827-row file. Columns: `pair_index`, `drug_1`, `drug_2`, `defect_class`, `detail`. Classes: `hub_pair` 693, `name_ambiguous` 54, `name_truncated` 53, `duplicate_unordered` 30, `implausible_coprescription` 21, `name_unresolvable` 17, `name_brand` 15, `same_class` 11, `name_nomenclature_inconsistent` 8. |
| `audit_drug_normalization.csv` | 161 | One row per distinct drug name in the predecessor file, with its RxNorm resolution, term type, ingredient, ATC, ChEMBL and DrugBank mappings, graph `degree`, `pair_share_pct`, `resolution_status` and free-text `notes`. `resolution_status` values: `resolved_exact` 152, `brand_level` 2, `unresolvable` 2, `resolved_nomenclature_variant` 2, `multi_ingredient` 1, `truncated_resolved_by_fuzzy` 1, `ambiguous` 1. |
| `audit_summary.md` | — | Narrative audit of the predecessor file. |
| `landscape_review.md` | — | Positioning against existing DDI reference and negative-control resources. |


---

## Additional columns (23–35) — submission dataset

The submission release carries 13 further columns beyond the 22 above, holding
the per-pair outputs of the equivalence analysis, the external re-screening, and
the residual-mechanism scan. They are not required for the core benchmark but
are shipped so every reported quantity is reproducible.

| # | Column | Type | Description |
|---|---|---|---|
| 23 | `n_ae_terms_tested` | integer | Adverse-event terms with ≥5 co-reports tested in the equivalence analysis (Sect. 3.5). |
| 24 | `median_upper95_ror` | float | Median across tested terms of the exact Poisson one-sided 95% upper bound on the observed/expected ratio. |
| 25 | `p95_upper95_ror` | float | 95th-percentile of that per-term upper bound. |
| 26 | `max_upper95_ror` | float | Maximum of that per-term upper bound. |
| 27 | `frac_terms_equiv_ror1.5` | float | Fraction of tested terms whose 95% upper bound falls below equivalence margin δ = 1.5. |
| 28 | `frac_terms_equiv_ror2.0` | float | Same, δ = 2.0. |
| 29 | `frac_terms_equiv_ror3.0` | float | Same, δ = 3.0. |
| 30 | `gold_d3r_testable` | boolean | Both members present in the mechanism-annotated gold standard (pair is testable there). |
| 31 | `gold_d3r_flagged` | boolean | Pair flagged as interacting in that gold standard (false for all testable pairs). |
| 32 | `label_screen` | categorical | FDA structured-product-label outcome: `no_label_signal`, `label_explicit_INTERACTION`, `label_explicit_NONinteraction`, `label_class_INTERACTION`. |
| 33 | `label_evidence` | string | Adjudicated label text supporting the `label_screen` value. |
| 34 | `d3_mechanism_hypotheses` | integer | Number of mechanism hypotheses the v1 rule engine attached to the pair (Sect. 3.6). |
| 35 | `d3_hypothesis_types` | string | Semicolon-delimited types of those hypotheses. |

The 3 pairs whose `label_screen` records a label-explicit or class-level
interaction are assigned the `EXCLUDED_label` tier and are outside the usable
set (Sect. 3.3).
