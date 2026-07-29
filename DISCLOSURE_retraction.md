# Standalone disclosure: the retracted predecessor of this work

Prepared by Adeeb Noor (sole author of the present release) for the editors and reviewers of
*Drug Safety*, to be supplied on request. It states the facts of the retraction,
what our audit of the retracted data file found, what is different in the
present work, and — equally important — what the present work does not claim.

---

## 1. The article and its retraction

**The article.** Assiri A, Noor A. *Anti-DDI Resource: A Dataset for Potential
Negative Reported Interaction Combinations to Improve Medical Research and
Decision-Making.* Journal of Healthcare Engineering 2022;2022:8904342.
doi:10.1155/2022/8904342 · PMID 35437468.

**The retraction.** Retraction notice doi:10.1155/2023/9892301 · PMID 37266234,
issued in 2023.

**The grounds.** The article was retracted as part of Hindawi's mass retraction
of compromised special issues. That action was a publisher-level response to
peer-review integrity failures in the special-issue process; it was not an
adjudicated finding of data fabrication or falsification concerning our article
in particular. We state this distinction because it is factually the case, not
because it reduces what follows from the retraction. A retracted article cannot
be cited as a source, and the data file attached to it cannot be treated as a
usable resource. We have not done either.

**Companion methods work is unaffected.** The prediction engine our earlier work
used is described in Noor A, et al. *J Am Med Inform Assoc*
2017;24(3):556–564, doi:10.1093/jamia/ocw128, which carries an erratum but no
retraction, and in Noor A, Assiri A, *Comput Math Methods Med* 2022,
doi:10.1155/2022/9093262, which is not retracted. We note the latter is a
Hindawi title and cite it with that context stated.

**Downstream use of the retracted resource.** Europe PMC records three citations
of the retracted article: the retraction notice itself, one self-citation, and
one independent scientific citation — a *GigaScience* paper
(doi:10.1093/gigascience/giad011) which, under a section on building a negative
dataset of non-interacting drug pairs, argues that negative DDI information is
scarce and that tools for predicting non-interacting pairs would be highly
beneficial. We draw a narrow conclusion from that: the scientific need our
earlier work addressed was independently recognised. It says nothing about the
adequacy of the retracted file, and we do not present it as support for the data.

---

## 2. Timeline

| Date | Event |
|---|---|
| 2022 | The Anti-DDI resource article is published in *Journal of Healthcare Engineering* (a Hindawi title), reporting a final set of 827 drug pairs labelled potential negative interaction combinations. |
| 2023 | The article is retracted as part of Hindawi's mass retraction of compromised special issues (notice doi:10.1155/2023/9892301). The retraction is a peer-review integrity action at the publisher level. |
| — | We stop citing and stop distributing the resource. |
| This work | We return to the 827-row file **as an object of audit**, not as a data source: enumerate its defects, resolve its drug names, characterise its graph structure, and determine which of its pairs can be supported by evidence independent of the original pipeline. |
| This work | We construct and release version 2: 797 unordered pairs, each carrying a FAERS co-exposure denominator, a minimum detectable reporting odds ratio, and an evidence tier, with 30 pairs excluded on clinical grounds and shipped flagged. |

---

## 3. What the audit of the 827-row file found

Every figure below is derived in code from the retracted file and is shipped in
`data/audit_defects.csv` (902 rows, one per defect instance) and
`data/audit_drug_normalization.csv` (161 rows, one per drug name).

**Overall defect burden.** 902 defect instances across 782 of the 827 rows
(94.6%). Only 45 rows (5.4%) carry no flagged defect. By class:

| Defect class | Instances |
|---|---:|
| `hub_pair` | 693 |
| `name_ambiguous` | 54 |
| `name_truncated` | 53 |
| `duplicate_unordered` | 30 |
| `implausible_coprescription` | 21 |
| `name_unresolvable` | 17 |
| `name_brand` | 15 |
| `same_class` | 11 |
| `name_nomenclature_inconsistent` | 8 |
| `same_ingredient` | **0** — this hypothesised defect was tested for and is absent |

**Residual duplication, and what it reveals.** The 827 rows contain 797 distinct
unordered pairs over 161 drug names. All 30 duplicated rows are order-reversals,
(A,B) paired with (B,A); there are zero exact ordered duplicates. That signature
is diagnostic of deduplication performed on ordered tuples rather than on
unordered sets. Seventeen of the 30 (57%) involve citalopram. The published
Table 1 of the retracted article stated that 52 duplications had been removed
and that none remained.

**Name integrity.** 152 of the 161 names (94.4%) resolve exactly to an RxNorm
ingredient. The nine that do not include `glyceryl trini.` (truncated; the
intended ingredient is nitroglycerin), `penicillin` (a class term that does not
distinguish penicillin G from penicillin V), `dextromethorph` (truncated),
`humalog` and `lantus` (brand names rather than ingredients), and `paracetamol`
and `salbutamol` (INN forms, inconsistent with the USAN-based top-200 source
list the article cited). Eighty-one rows carry stray whitespace and 37
inconsistent case.

The most consequential single defect is `isosorbide`. It resolves
*successfully* — but to the osmotic diuretic, not to the intended antianginal
nitrate. An automated pipeline receives a confident wrong answer rather than a
failure, which is a worse failure mode than an unresolvable string.

**Graph structure — the decisive finding.** Treating the 797 distinct pairs as a
graph on 161 nodes: density 0.0619, mean degree 10.27, median 5, SD 20.54. That
standard deviation is 6.5 times the SD ≈ 3.1 expected under uniform sampling of
797 pairs from the 12,880 possible; Gini coefficient 0.582; maximum degree 152.

A greedy **vertex cover of just 13 drugs** touches all 797 pairs: sevelamer,
ustekinumab, dalteparin, atenolol, levetiracetam, liraglutide, heparin,
hydrocodone, dextromethorphan, citalopram, conjugated estrogens,
chlorpheniramine, lactulose. The remaining 148 drugs (91.9%) form an
**independent set**: none of the 10,878 possible pairs among them appears. The
797 edges decompose as 49 anchor–anchor, 748 anchor–other, 0 other–other.
Sevelamer alone appears in 152 of the 827 rows (18.4%) and ustekinumab in 140
(16.9%); together they account for 291 rows (35.2%). The top five drugs occupy
32.0% of the 1,654 drug slots, the top ten touch 94.1% of rows, and the top
twenty touch 100%.

The consequence is stark: **a 13-feature identity lookup reproduces every
negative label in the file.** Any model evaluated against it can score highly
without representing pharmacology at all.

**The mechanism behind the structure.** The filter used in the original pipeline
removed 11,130 of 12,255 pairs (90.8%) on the basis of a posited
pharmacokinetic mechanism. Drugs for which such a mechanism cannot in principle
be posited therefore survive against *every* partner: sevelamer is a
non-absorbed polyallylamine phosphate binder (ATC V03AE02, RxCUI 214824), and
ustekinumab is an IgG1κ monoclonal antibody (ATC L04AC05, RxCUI 847083) cleared
by proteolytic catabolism. 602 of the 827 rows (72.8%) contain at least one such
pharmacokinetically isolated drug. The pipeline was a sieve for pharmacological
inertness, not a measurement of safety.

**Safety-critical labelling errors.** Eleven same-class or mechanistically
redundant pairs survived a review that the article stated had considered drug
class. The reason is structural: the engine models pharmacokinetic interaction
and is blind to pharmacodynamic additivity. Two of the eleven are unambiguous:

- **hydrocodone × zopiclone** (row 394) and **hydrocodone × zaleplon** (row 406)
  — opioid plus Z-drug, carrying an **FDA boxed warning** for respiratory
  depression and death.

Their presence in a set labelled a potential safe combination is a substantive
labelling error, not a technicality, and we describe it as such. The remaining
nine are sitagliptin × liraglutide (DPP-4 inhibitor plus GLP-1 receptor agonist,
mechanistically redundant), cinacalcet × sevelamer, dextromethorphan ×
zolmitriptan, humalog × liraglutide, hydrocodone × aspirin, hydroxychloroquine ×
ustekinumab, metformin × liraglutide, methotrexate × ustekinumab, and
ustekinumab × pemetrexed.

A further 21 pairs are implausible as co-prescriptions: 8 renal-population
conflicts (sevelamer indicates dialysis-dependent CKD, while the partner drugs
metformin, nitrofurantoin, methotrexate, pemetrexed, hydrochlorothiazide,
triamterene, spironolactone and glimepiride are contraindicated or ineffective
at that level of renal function), 12 route-precluded pairs (a systemic drug
paired with topical or non-absorbed mupirocin, chlorhexidine or clotrimazole),
and one age/sex-exclusive pair (conjugated estrogens × methylphenidate). We
also tested systematically for three further defect types and found none:
sex-exclusive pairs, acute-course × acute-course pairs, and same-ingredient
pairs.

**Funnel irreproducibility.** The article's pair-count arithmetic does not close.
The reported starting figure of 14,365 pairs equals C(170,2), not the
C(200,2) = 19,900 implied by the stated 200-drug list. Following the reported
removals, 14,365 − 2,110 − 11,130 − 208 = 917, and 917 − 52 = 865, whereas the
published final count is 827 — leaving 38 pairs removed by a step that is not
quantified anywhere in the article.

---

## 4. What is different in version 2

1. **The prior file is an object of audit, not a data source.** Nothing is
   inherited on trust. Every defect above is enumerated in machine-readable
   form and shipped with the release, so a reader can verify the audit rather
   than accept our summary of it.
2. **The negative claim is re-derived from an independent evidence layer.** For
   all 797 pairs we retrieved FAERS co-report counts against a denominator of
   20,328,575 reports, and for each pair computed the minimum reporting odds
   ratio its co-exposure count could have detected at α = 0.05 and 80% power.
   A pair's status now rests on measured co-exposure and stated statistical
   resolution, not on the output of the original filter.
3. **Evidence is graded, and the resource declines to claim where it cannot.**
   Six tiers, assigned by a published rule implemented in code: T1 well-powered
   217 pairs (median 2,020 co-reports, median minimum detectable ROR 2.15), T2
   moderate 321 (291; 5.15), T3 limited 106 (59; 17.15), T3 trivial-inert 44
   (623; 3.40), T4 uninformative 76 (11.5; minimum detectable ROR infinite —
   no interaction of any plausible size could have been detected), 30
   clinically excluded and 3 excluded on FDA-label evidence. The **usable set is
   T1 + T2 = 538 pairs**. The 76 T4
   pairs are shipped as a documented absence of evidence, explicitly not as
   negative claims.
4. **Thirty pairs are excluded on clinical grounds and shipped flagged.** The 11
   same-class and 21 implausible-co-prescription pairs above — including both
   opioid × Z-drug pairs — are removed from the usable set and retained in the
   file with `excluded_clinical = True` so that the exclusion is auditable
   rather than invisible. The evaluation package drops them under every tier
   selector.
5. **The structural artefact is disclosed and made measurable.** The 13-drug
   anchor set is shipped as a package constant and the per-pair anchor count as
   a column, so any evaluation can stratify on it. The trivially inert pairs are
   tiered separately so they cannot inflate a benchmark.
6. **The degree artefact is quantified, and it is the paper's headline.** A
   popularity-only heuristic reaches AUC 0.934 (SD 0.007) against random
   negatives and 0.947 (SD 0.004) against our curated negatives, but 0.498
   (SD 0.004) — chance — against degree-matched negatives. The release ships
   the matched-sampling protocol that produces the third number.
7. **An independent cross-check post-dating the original by two to three
   years.** 588 of the 797 pairs have both drugs present in DDInter 2.0
   (doi:10.1093/nar/gkae726; 302,516 DDI records over 2,310 drugs). Zero are
   flagged as interactions there. The drugs are individually
   interaction-active; these specific pairs are not.
8. **A reproducibility harness ships with the data.** `validate.py` re-derives
   97 reported quantities from the shipped files, prints a PASS/FAIL line for
   each, and exits non-zero on any mismatch. It runs in continuous integration
   on every push.
9. **No text is reused from the retracted article.** The manuscript, the data
   dictionary, and the documentation are written from the current analysis.

---

## 5. What we deliberately do **not** claim

- **We do not claim any pair is safe to co-prescribe.** The resource is for
  evaluation and benchmarking. It licenses no clinical decision, and it is not a
  drug-interaction information source for prescribing. Presence in the file
  records that no interaction evidence was found under a documented procedure,
  together with how much evidence there was to find.
- **We do not claim priority.** CRESCENDDI
  (doi:10.1038/s41597-022-01159-y) precedes this work with 10,286 positive and
  4,544 negative drug–drug–event controls. Our differences are that we work at
  the pair rather than the triplet level and that we attach a quantified
  co-exposure denominator. We are not first to build DDI negative controls.
- **We do not claim our negatives are free of degree bias.** They are not, and
  no negative set can be. Our curated negatives score 0.947 against a
  popularity-only heuristic, essentially as high as random negatives do. The
  contribution is that the bias is measurable with the metadata and protocol we
  ship.
- **We do not claim compendium adjudication.** Lexicomp and Micromedex
  re-screening was **not** performed for this release; we had no institutional
  access during its preparation. The predecessor's screening stands as
  historical provenance only. This is stated as a limitation in the manuscript
  and named as required future work. It also matters because single-compendium
  absence is not evidence of non-interaction: across BNF (51,481 pairs),
  Drug Interactions Thesaurus (38,037) and Micromedex (65,446), only 6,970 pairs
  are common to all three — 13.54%, 18.32% and 10.65% respectively
  (doi:10.1111/bcp.15341).
- **We do not claim that disproportionality validates our negatives.** It does
  not, and we report the failure. Omega shrinkage disproportionality flagged at
  least one signal for 12 of 12 established positive-control interacting pairs
  **and** for 246 of 246 candidate negatives (100%). Discrimination between the
  groups was AUC 0.577 (p = 0.367) on strongest signal per pair and AUC 0.632
  (p = 0.124) on fraction of adverse-event terms flagged — the latter pair
  previously reported as 0.633 (p = 0.120), which is not reproducible from the
  shipped file; the recomputed values stand and the non-significant conclusion
  is unchanged. Median strongest
  signal 3.465 for positives versus 2.812 for negatives. Confounding by
  indication, co-medication and reporting artefacts dominates. Pair-level
  spontaneous-report disproportionality therefore cannot adjudicate a negative
  control set; in this resource it supplies the co-exposure denominator only.
- **We record a methods error found and corrected during this work.** An initial
  disproportionality run used top-100 truncated adverse-event profiles and
  non-disjoint marginals, and produced 100% signal rates with apparently large
  effect sizes. The corrected computation uses disjoint strata (A-not-B,
  B-not-A, A-and-B) with `g11 = n_AB × max(p_A, p_B)`, and is the one reported.
  We note it here rather than only in a code comment because the erroneous
  version would have supported a stronger and false conclusion.

---

## 6. Availability

The complete release — dataset, data dictionary, installable evaluation package,
audit tables, and the validation harness — is archived at
the archived GitHub release at https://github.com/adeebnoor/ANTI-DDI. We will supply any
part of the audit, any intermediate file, or the full analysis history at
whatever point in review the editors consider useful.

**Adeeb Noor** (sole author, corresponding), Department of Information
Technology, Faculty of Computing and Information Technology, King Abdulaziz
University, Jeddah, Saudi Arabia · arnoor@kau.edu.sa · ORCID https://orcid.org/0000-0002-8251-1853

**Abdullah Assiri**, Department of Clinical Pharmacy, King Khalid University, is
a co-author of the retracted 2022 predecessor audited here and is acknowledged;
he is not an author of the present release.
