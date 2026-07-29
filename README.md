# Anti-DDI v2 — a tiered negative-control resource for drug–drug interaction research

Version 2.0.0 · 797 drug pairs · 161 drugs · code MIT, data CC-BY-4.0

---

## Provenance note — please read first

This release supersedes a **retracted** predecessor.

> Assiri A, Noor A. *Anti-DDI Resource: A Dataset for Potential Negative Reported
> Interaction Combinations to Improve Medical Research and Decision-Making.*
> Journal of Healthcare Engineering 2022;2022:8904342.
> doi [10.1155/2022/8904342](https://doi.org/10.1155/2022/8904342) · PMID 35437468.
> **Retracted 2023**; retraction notice doi
> [10.1155/2023/9892301](https://doi.org/10.1155/2023/9892301), PMID 37266234.

The retraction was part of Hindawi's mass retraction of compromised special
issues — a publisher-level peer-review integrity action, not an adjudicated
finding of data fabrication. The distinction does not lessen the obligation:
a retracted file cannot be treated as a usable resource, and this release does
not treat it as one.

In this release **the predecessor's 827-row file is used solely as an object of
audit.** Its defects are enumerated in `data/audit_defects.csv` — 902 defect
instances across 782 of its 827 rows (94.6%) — and its drug names are resolved
one by one in `data/audit_drug_normalization.csv`. The negative claim attached
to each surviving pair is re-derived here from an independent evidence layer
(FAERS co-exposure and statistical power), not inherited. Thirty pairs are
excluded on clinical grounds, including two opioid × Z-drug pairs that carry an
FDA boxed warning. No text is reused from the retracted article.

`DISCLOSURE_retraction.md` (distributed with this release) states the full
timeline, what the audit found, and what this release does and does not claim.

---

## What this resource is

Models that predict drug–drug interactions are trained and evaluated against
**negative** examples — pairs asserted not to interact. Those negatives are
almost always constructed by taking pairs absent from an interaction database
and labelling them negative. Absence from a database is not evidence of
non-interaction, and it is not distributed at random: it tracks how much
attention a drug has received.

This resource supplies 797 candidate non-interacting pairs in which each pair
carries:

1. **a quantified co-exposure denominator** — how often the two drugs actually
   appeared together in FAERS, so a reader can see whether an interaction had
   any chance of being observed;
2. **a minimum detectable reporting odds ratio** — the smallest interaction
   effect that co-exposure count could have detected, so the strength of the
   negative claim is stated rather than assumed;
3. **an evidence tier** derived from those two quantities by a rule that is
   published, implemented, and machine-checked;
4. **the degree metadata and matched-sampling protocol** needed to measure how
   much of a model's apparent performance comes from drug popularity rather
   than from pharmacology.

The last item is the reason to prefer this resource over a list of pairs.

## What this resource is **not**

- **It is not a safety list, and it licenses no clinical decision.** A pair's
  presence records that no interaction evidence was found under the procedure
  documented here, together with how much evidence there was to find. It does
  not state that the pair is safe to co-prescribe in any patient. Prescribing
  decisions require a clinician with the full patient context and a current
  drug-information source; nothing in these files substitutes for either.
- **It is not a compendium re-screening.** Lexicomp and Micromedex
  re-screening was **not** performed for this release (no institutional access);
  the predecessor's screening stands as historical provenance only. This is a
  stated limitation and required future work, not an oversight.
- **It is not the first DDI negative-control set.** CRESCENDDI
  (doi [10.1038/s41597-022-01159-y](https://doi.org/10.1038/s41597-022-01159-y))
  precedes it, with 4,544 negative drug–drug–event controls. The contribution
  here is pair-level rather than triplet-level, plus the quantified co-exposure
  denominator and the degree-control protocol.
- **It is not free of degree bias.** It is not possible to construct a
  negative set that is. What is possible — and what this release does — is to
  ship the metadata and the protocol that make the bias measurable.

---

## The headline result

A deliberately trivial "predictor" — `score = log1p(degree_a) × log1p(degree_b)`,
i.e. how *popular* each drug is in the positive knowledge base, containing no
pair-specific pharmacology whatsoever — was scored against three negative sets
over 20 random-seed replicates:

| Negative set | AUC | SD |
|---|---:|---:|
| Random unlabelled negatives | **0.934** | 0.007 |
| This resource's curated negatives | **0.947** | 0.004 |
| Degree-matched curated negatives | **0.498** | 0.004 |

A model with zero pharmacological content reaches AUC 0.93 against conventional
negative sets. Almost all of that apparent skill is attributable to
degree/popularity structure, not to interaction prediction.

This is a property of how negatives are constructed, and **it applies to the
curated set here too**, until degree-matching is imposed — which is precisely
why the resource ships the degree metadata and the matched-sampling protocol
rather than only the pair list. The claim is not that these negatives are
immune to the artefact; it is that they make it measurable. The direct
precedent for the finding is
doi [10.1186/s12915-025-02231-w](https://doi.org/10.1186/s12915-025-02231-w),
on negative-sampling bias in scale-free biomolecular networks.

Degree matching retained roughly 331 of 538 positives per replicate; a mean of
38.4% of positives (SD 2.1%, range 34.2-42.6% across the 20 replicates) had no
degree-matched negative available at all. That shortfall is
itself a measurement of how far apart the two classes' degree distributions are.

## What we could not do

Two findings are reported because they are findings, not because they are
convenient.

**Pair-level FAERS disproportionality does not adjudicate a negative control.**
Omega shrinkage disproportionality was run on the well-powered pairs and on 12
established positive-control interacting pairs. All 12 positive controls flagged
at least one signal — **and so did 246 of 246 candidate negatives (100%)**.
Discrimination between the two groups was AUC 0.577 (p = 0.367) on strongest
signal per pair and AUC 0.632 (p = 0.124) on fraction of adverse-event terms
flagged. (The second pair of figures was previously reported as AUC 0.633,
p = 0.120; those values are not reproducible from the shipped
`signal_detection_t1.csv` and the recomputed 0.632 / 0.124 are the ones
`validate.py` asserts. See the note at check (c) in `validate.py` for the
evidence. The conclusion is unchanged — both comparisons are
non-significant.) Confounding by indication, co-medication and reporting artefacts
dominates at this granularity. Spontaneous-report disproportionality therefore
**cannot** serve as the adjudication criterion for a negative control set; in
this resource it supplies the co-exposure *denominator* only. See
`data/signal_detection_t1.csv`.

**One methods bug is on the record.** An initial run used top-100 truncated
adverse-event profiles and non-disjoint marginals, and produced 100% signal
rates with apparently large effect sizes. The corrected computation — disjoint
strata (A-not-B, B-not-A, A-and-B), with `g11 = n_AB × max(p_A, p_B)` — is the
one reported. Also note that openFDA count queries cap at `limit=500` without
an API key (`limit=1000` returns `403 API_KEY_MISSING`).

## Independent cross-check

588 of the 797 pairs have both drugs present in DDInter 2.0
(doi [10.1093/nar/gkae726](https://doi.org/10.1093/nar/gkae726); 302,516 DDI
records over 2,310 drugs, released two to three years after the predecessor
file). **Zero** of those 588 pairs is flagged as an interaction there. The
drugs are individually interaction-active; these specific pairs are not. There
is also zero contamination between the 538-pair usable set and an 11,786-pair
positive reference. DDInter is third-party and is not redistributed here, so
`validate.py` records this check as a documented `SKIP` rather than asserting it.

---

## Evidence tiers

Assigned by `antiddi.evidence.assign_tier`. Rules are evaluated **in this
order** and the first match wins:

1. `excluded_clinical` is true → **`EXCLUDED_clinical`**
2. `faers_coreports < 25` → **`T4_uninformative`**
3. `both_pk_inert` is true → **`T3_trivial_inert`**
4. `faers_coreports ≥ 500` **and** `min_detectable_ror ≤ 3.0` → **`T1_wellpowered`**
5. `faers_coreports ≥ 100` → **`T2_moderate`**
6. otherwise → **`T3_limited`**

| Tier | Pairs | Median co-reports | Median min. detectable ROR | Use |
|---|---:|---:|---:|---|
| `T1_wellpowered` | 217 | 2,020 | 2.15 | Strongest negative evidence: a moderate interaction would have been detectable and was not detected. |
| `T2_moderate` | 321 | 291 | 5.15 | Excludes a large effect, not a moderate one. |
| `T3_limited` | 106 | 59 | 17.15 | Only a very large effect was detectable. Use with the limitation stated. |
| `T3_trivial_inert` | 44 | 623 | 3.40 | Both drugs pharmacokinetically inert by class — negative by construction, not by evidence. Exclude from benchmarks. |
| `T4_uninformative` | 76 | 11.5 | ∞ | Under 25 co-reports: **no interaction could have been detected.** A documented absence of evidence, not a negative claim. |
| `EXCLUDED_clinical` | 30 | — | — | Excluded on clinical grounds. Shipped for auditability only; **never** a usable negative. |
| `EXCLUDED_label` | 3 | 165 | 7.50 | Excluded on FDA structured-product-label evidence (Sect. 3.3). Shipped for auditability only; **never** a usable negative. |

**The usable benchmark set is `T1_wellpowered + T2_moderate` = 538 pairs**, the
default of `evaluate(negatives="T1+T2")`. The 30 `EXCLUDED_clinical` and 3
`EXCLUDED_label` pairs are dropped by every tier selector, including `"all"`.

### The structural warning

Treated as a graph, the 797 pairs are covered by a **greedy vertex cover of just
13 drugs** (`antiddi.ANCHOR_DRUGS`: sevelamer, ustekinumab, dalteparin,
atenolol, levetiracetam, liraglutide, heparin, hydrocodone, dextromethorphan,
citalopram, conjugated estrogens, chlorpheniramine, lactulose). Every pair
contains at least one; the other 148 drugs form an independent set — none of the
10,878 possible pairs among them appears. A 13-feature identity lookup
therefore reproduces every negative label in the file.

This is inherited from the predecessor's construction, and it is disclosed
rather than hidden: `n_anchor_drugs` is shipped as a column so that any
evaluation can stratify on it. The mechanism is documented in
`data/audit_summary.md` — the underlying filter removed pairs on the basis of a
posited pharmacokinetic mechanism, so drugs for which no such mechanism can in
principle be posited (a non-absorbed phosphate binder, a monoclonal antibody
cleared by proteolytic catabolism) survive against every partner. That pipeline
is a sieve for pharmacological inertness, not a measurement of safety.

---

## Quickstart

```python
# pip install -e .                          # from the release root
import pandas as pd, numpy as np
from antiddi.benchmark import evaluate, compute_degrees

negatives = pd.read_csv("data/antiddi_v2_dataset.csv")          # 797 pairs, 35 columns
positives = pd.read_csv("my_positive_reference.csv")            # your drug_a, drug_b
degrees   = compute_degrees(positives)                          # degree in the positive graph
popularity = lambda a, b: np.log1p(degrees.get(a, 0)) * np.log1p(degrees.get(b, 0))

report = evaluate(popularity, positives, negatives)             # T1+T2 and degree matching by default
print(report)                                                   # three arms: random / curated / degree_matched
print(report.degree_attributable_auc)                           # AUC carried by popularity alone
```

Then `python validate.py` re-derives every published quantity from the shipped
files and prints a PASS/FAIL line for each.

## Package contents

```
antiddi-v2/
├── README.md                         this file
├── LICENSE                           MIT (code) + CC-BY-4.0 (data) — the split is stated inside
├── CITATION.cff
├── pyproject.toml                    installable; pandas, numpy, scipy only
├── validate.py                       reproducibility harness (116 quantities; exits non-zero on failure)
├── CHECKSUMS.sha256                  SHA-256 of every shipped file
├── antiddi/
│   ├── __init__.py                   __version__ = "2.0.0"
│   ├── evidence.py                   min_detectable_ror(), assign_tier()
│   └── benchmark.py                  evaluate(), degree_matched_sample()
├── data/
│   ├── antiddi_v2_dataset.csv        797 × 35 — the resource
│   ├── DATA_DICTIONARY.md            all 35 columns: type, units, permitted values, provenance
│   ├── benchmark_replicates.csv      20 replicates of the headline experiment
│   ├── signal_detection_t1.csv       88,679 pair × adverse-event disproportionality rows
│   ├── audit_defects.csv             902 defect instances in the predecessor file
│   ├── audit_drug_normalization.csv  161 drug names, resolved individually
│   ├── audit_summary.md              narrative audit of the predecessor file
│   ├── label_screening.csv           FDA label screen per pair, with the evidence text
│   ├── equivalence_analysis.csv      per-pair equivalence bounds (645 pairs with ≥10 testable terms)
│   ├── citation_strategy.csv         verified reference map for the accompanying article
│   ├── citation_verification.csv     provenance of every bibliographic claim, incl. one withdrawn
│   └── landscape_review.md           positioning against existing resources
├── figures/
│   ├── fig1_framework.png            four-stage study framework, audit through benchmark
│   ├── fig2_structure_tiers.png      predecessor structure and the six evidential states
│   ├── fig3_benchmark.png            tiers, the AUC collapse, and Ω non-discrimination
│   └── fig4_equivalence.png          equivalence testing tracks data volume, not interaction status
└── .github/workflows/ci.yml          runs validate.py on push (Python 3.12)
```

Before joining on drug names, read **§5 of `data/DATA_DICTIONARY.md`**. Names
are carried forward from the predecessor file unmodified so the audit stays
reproducible; nine of the 161 do not resolve cleanly, and `isosorbide` resolves
*successfully but wrongly* to the osmotic diuretic rather than the intended
antianginal nitrate. Automated resolution returns a confident wrong answer
there rather than a failure.

## Licence

- **Code** (`antiddi/`, `validate.py`, `pyproject.toml`, CI configuration): MIT.
- **Data and documentation** (`data/`, `figures/`, `README.md`): Creative
  Commons Attribution 4.0 International (CC-BY-4.0).

Both texts are in `LICENSE`. Third-party identifiers appearing in the data
(RxNorm, ATC, DrugBank, ChEMBL) remain subject to their own source terms; FAERS
counts are derived from openFDA, a public United States federal data source.

## Citation

Cite the article and the archived release together. The dataset DOI is minted
as an archived GitHub release (tag v2.0.0) at https://github.com/adeebnoor/ANTI-DDI.

```
Noor A. A Graded Reference Set of Non-Interacting Drug Pairs for Benchmarking Drug–Drug Interaction Prediction: Negative-Control Selection Determines Measured Performance. Drug Safety. [AUTHOR: year;volume:pages].
doi:[AUTHOR: article DOI once assigned]

Noor A. Anti-DDI v2: a tiered negative-control resource for
drug-drug interaction research (Version 2.0.0) [Data set]. GitHub. https://github.com/adeebnoor/ANTI-DDI
```

`CITATION.cff` carries the machine-readable form.

## Contact

Adeeb Noor (sole author, corresponding) — Department of Information Technology,
Faculty of Computing and Information Technology, King Abdulaziz University,
Jeddah, Saudi Arabia · arnoor@kau.edu.sa

Abdullah Assiri (Department of Clinical Pharmacy, King Khalid University) is a
co-author of the **retracted 2022 predecessor** audited here and is
acknowledged; he is not an author of the present release.

Source repository: https://github.com/adeebnoor/ANTI-DDI
