# Forensic audit of the 827-pair Anti-DDI negative-control dataset

Source file: `AntiDDI-dataset3.xlsx` (single sheet; columns `#`, `Pair 1`, `Pair 2`; 827 rows, no missing values).
Reference: Assiri & Noor, *J Healthc Eng* 2022;2022:8904342 (retracted 2023 in Hindawi's mass retraction of
compromised special issues; the notice cites concerns about the peer-review process, not adjudicated data
fabrication). All counts below were computed directly from the file; drug names were resolved against RxNorm
(RxNav REST, exact `search=0` and normalised `search=2` lookups), ATC classes against RxClass and ChEMBL, and
DrugBank identifiers against UniChem.

Throughout, defects are labelled **[error]** where the file contradicts the published method or contains an
objectively wrong value, and **[design]** where the value is internally consistent but the construction
procedure makes it uninformative for the dataset's stated purpose.

---

## 1. Summary of findings

| Defect class | Instances | Distinct rows affected | % of 827 rows |
|---|---:|---:|---:|
| `hub_pair` | 693 | 693 | 83.8% |
| `name_ambiguous` | 54 | 53 | 6.4% |
| `name_truncated` | 53 | 52 | 6.3% |
| `duplicate_unordered` | 30 | 30 | 3.6% |
| `implausible_coprescription` | 21 | 21 | 2.5% |
| `name_unresolvable` | 17 | 17 | 2.1% |
| `name_brand` | 15 | 15 | 1.8% |
| `same_class` | 11 | 11 | 1.3% |
| `name_nomenclature_inconsistent` | 8 | 8 | 1.0% |
| `same_ingredient` | 0 | 0 | 0.0% |
| **Any defect** | **902** | **782** | **94.6%** |

45 of 827 rows (5.4%) carry no flagged defect of any class.

Headline structural numbers: 827 rows contain **797 distinct unordered pairs** over **161 distinct drug names**.
The 797 pairs occupy 6.19% of the C(161,2) = 12,880 possible pairs.

---

## 2. Duplicate pairs [error]

**30 rows (3.63%) are unordered duplicates**, reducing 827 rows to 797 distinct pairs.

- There are **zero exact ordered duplicates**: no (Pair 1, Pair 2) string tuple occurs twice.
- **All 30** duplicates are order-reversals — the pair appears once as (A, B) and once as (B, A). This is
  diagnostic: the deduplication step compared ordered string tuples rather than unordered sets, so every
  reversed instance survived. Table 1 of the paper reports 52 duplications removed by expert review and zero
  further issues found by the checkers; the residual 30 are the reversals that an ordered comparison cannot see.
- The repeats are widely separated in the file (median index gap 232 rows, range 32–708), so they are not a
  contiguous copy-paste block.
- The duplicates are concentrated in a few drugs: **17 of 30 (57%) involve citalopram** and 6 involve
  amoxicillin. Citalopram appears in 47 rows total, so 36% of citalopram's rows are its own duplicates.

Enumeration (first occurrence → repeated row):

| First row | Repeat row | Drug A | Drug B |
|---:|---:|---|---|
| 14 | 197 | citalopram | isosorbide |
| 34 | 199 | allopurinol | citalopram |
| 48 | 200 | amoxicillin | citalopram |
| 50 | 252 | amoxicillin | dextromethorph |
| 52 | 466 | amoxicillin | levetiracetam |
| 53 | 518 | amoxicillin | liraglutide |
| 54 | 687 | amoxicillin | sevelamer |
| 55 | 763 | amoxicillin | ustekinumab |
| 95 | 357 | atenolol | heparin |
| 107 | 613 | atenolol | omeprazole |
| 153 | 201 | cefdinir | citalopram |
| 171 | 203 | chlorhexidine | citalopram |
| 209 | 285 | citalopram | dicyclomine |
| 210 | 302 | citalopram | dutasteride |
| 211 | 311 | citalopram | enalapril |
| 213 | 528 | citalopram | lisinopril |
| 214 | 558 | citalopram | methotrexate |
| 215 | 581 | citalopram | montelukast |
| 216 | 591 | citalopram | mupirocin |
| 217 | 597 | citalopram | nitrofurantoin |
| 218 | 622 | citalopram | oseltamivir |
| 219 | 636 | citalopram | penicillin |
| 221 | 664 | citalopram | ramipril |
| 224 | 805 | citalopram | valganciclovir |
| 265 | 366 | dextromethorph | heparin |
| 266 | 388 | dextromethorph | hydrochlorothiazide |
| 390 | 492 | hydrochlorothiazide | levetiracetam |
| 500 | 614 | levetiracetam | omeprazole |
| 615 | 725 | omeprazole | sevelamer |
| 616 | 797 | omeprazole | ustekinumab |

**Effect of correction.** After deduplication the set is 797 pairs; sevelamer's degree falls from 152 to 150,
ustekinumab's from 140 to 138, and the fraction of pairs containing at least one of the two goes from 35.2% to
36.0%. Deduplication therefore corrects the reported dataset size by 3.6% but does not change the structural
diagnosis in §4.

---

## 3. Drug-name integrity [error]

The 827 rows contain 165 distinct raw strings, reducing to **161** after stripping leading/trailing whitespace
and case-folding. Two pre-normalisation defects exist in the file itself:

- **81 rows (9.8%)** have a leading or trailing space in a drug field.
- **37 rows (4.5%)** use inconsistent capitalisation of the same ingredient (e.g. `Allopurinol` vs
  `allopurinol`, `Lantus`, `Humalog`, `Methocarbamol `).

Neither changes the pair content, but both mean the published file cannot be joined to any terminology without
prior cleaning, and both indicate the file was assembled by manual transcription rather than by export from a
normalised store.

Of the 161 normalised names, **152 (94.4%) resolve exactly** to an RxNorm ingredient concept (TTY = IN) on the
first exact-match call. Nine do not:

| Name | Rows affected | Status | Finding |
|---|---:|---|---|
| `dextromethorph` | 52 | truncated | Exact lookup fails. Normalised lookup returns four concepts (PIN 236146 polistirex, PIN 259262 tannate, PIN 267251 hydrochloride, IN 3289 base). Resolvable only by fuzzy matching. |
| `glyceryl trini.` | 6 | **unresolvable** | Fails both exact and normalised lookup. Approximate matching returns `glyceryl` (RxCUI 2531034), a different chemical entity. The intended concept is nitroglycerin (IN 4917; INN glyceryl trinitrate). |
| `penicillin` | 11 | **unresolvable** | Fails both lookups. A class/stem term, not a dispensable ingredient: it does not distinguish penicillin G (IN 7980) from penicillin V (IN 7984), nor intravenous from oral route. The two differ materially in pharmacokinetics and interaction profile. |
| `isosorbide` | 11 | ambiguous | Resolves *successfully but incorrectly* to IN 6057 `isosorbide`, the osmotic diuretic oral solution — not the intended antianginal nitrate. The correct concepts are isosorbide mononitrate (PIN 28004) or isosorbide dinitrate (IN 6058). This is the most dangerous name defect in the set, because automated resolution returns a confident wrong answer rather than a failure. |
| `humalog` | 8 | brand | RxNorm BN 135805. Ingredient is insulin lispro (IN 86009). |
| `lantus` | 7 | brand | RxNorm BN 261551. Ingredient is insulin glargine (IN 274783). |
| `conjugated estrogens` | 32 | multi-ingredient | IN 4099 `estrogens, conjugated (USP)` is a defined mixture of conjugated equine estrogens, not a single molecular entity. No InChIKey and no DrugBank cross-reference exist for it. |
| `paracetamol` | 4 | nomenclature | INN form; RxNorm/USAN preferred term is acetaminophen (IN 161). |
| `salbutamol` | 4 | nomenclature | INN form; RxNorm/USAN preferred term is albuterol (IN 435). |

`paracetamol` and `salbutamol` are internally inconsistent with the source list: the paper's input was the
top-200 *US* prescribed drugs, for which the USAN terms acetaminophen and albuterol are the correct labels.
Their presence indicates the drug list was assembled from at least two nomenclature sources.

**Rows affected by at least one name defect: 123 of 827 (14.9%).**
Only two names (`glyceryl trini.`, `penicillin`) are strictly unresolvable against RxNorm.

**Zero pairs are the same ingredient under two different names.** Both members of every pair map to distinct
RxCUIs. In particular `humalog`/`lantus`, `heparin`/`dalteparin`, and `paracetamol`/`salbutamol` never co-occur
as a pair with their alternate-name counterparts. Defect class `same_ingredient` has count 0 — this specific
hypothesised defect is not present.

---

## 4. Hub concentration and graph topology [design]

Treating the 797 distinct pairs as an undirected graph on 161 nodes:

| Statistic | Value |
|---|---|
| Nodes (drugs) | 161 |
| Edges (distinct pairs) | 797 |
| Graph density | 0.0619 |
| Mean degree | 10.27 |
| Median degree | 5 |
| SD of degree | 20.54 (coefficient of variation 2.00) |
| Max / min degree | 152 (sevelamer) / 1 |
| Gini coefficient of degree | 0.582 |
| Degree skewness / excess kurtosis | 4.73 / 24.65 |

Under uniform random selection of 797 pairs from C(161,2) the expected degree is 9.9 with SD ≈ 3.1. The observed
SD is 20.5 — **6.5× the value expected** under uniform sampling. The degree distribution is not a sampling
fluctuation.

Concentration:

- **sevelamer: 152 rows (18.4%); ustekinumab: 140 rows (16.9%).** Together they appear in **291 of 827 rows
  (35.2%)**.
- The top 5 drugs (sevelamer, ustekinumab, dalteparin, levetiracetam, atenolol) occupy **32.0% of all 1,654
  drug slots**.
- 11 drugs hold 50% of drug slots. The top 10 drugs touch **94.1%** of rows; the top 20 touch **100%**.

**The decisive structural finding is that the graph is a near-star, not a sampled network.** A greedy vertex
cover of size **13** — sevelamer, ustekinumab, dalteparin, atenolol, levetiracetam, liraglutide, heparin,
hydrocodone, dextromethorphan, citalopram, conjugated estrogens, chlorpheniramine, lactulose — touches **all 797
distinct pairs**. The remaining **148 drugs (91.9%) form an independent set: not one of the 10,878 possible
pairs among them appears in the dataset.**

Decomposing the 797 distinct edges: **49** join two anchor drugs, **748** join an anchor to a non-anchor, and
**0 join two non-anchor drugs** (49 + 748 + 0 = 797). Over the 827 raw rows, before deduplication, the same
decomposition is 51 / 776 / 0, the difference being the 30 duplicate rows (2 anchor–anchor, 28 anchor–other).

### Why these drugs dominate

The two largest hubs are pharmacokinetically isolated by molecular class, and this is the mechanism of their
dominance, not a coincidence:

- **Sevelamer** (RxCUI 214824, ATC V03AE02) is a non-absorbed cross-linked polyallylamine phosphate binder. It
  has essentially no systemic exposure, no CYP or transporter involvement, and no plasma protein binding. A
  pharmacokinetic interaction of the kind indexed by the D3 rule engine is *structurally impossible* for it
  (its real interaction liability — gastrointestinal chelation of co-administered oral drugs — is a
  mechanism the D3 engine does not model).
- **Ustekinumab** (RxCUI 847083, ATC L04AC05) is an IgG1κ monoclonal antibody cleared by proteolytic
  catabolism. Antibodies are not CYP substrates, inhibitors, or inducers, and are not transporter substrates.
  The same structural impossibility applies.

The next hubs follow the same pattern: dalteparin (LMWH, renal clearance, no CYP), levetiracetam (non-protein-
bound, renal/hydrolytic clearance), atenolol (hydrophilic, renally cleared, negligible CYP metabolism),
liraglutide (peptide, endopeptidase degradation), heparin (reticuloendothelial clearance).

The consequence is that the filtering pipeline behaves as a **sieve for pharmacological inertness**. The D3
mechanism filter removed 11,130 pairs — 77.5% of all candidates — on the basis of a modelled mechanism. Any
drug for which a mechanism *cannot in principle* be posited survives the filter against every partner. Its
degree is therefore approximately the number of surviving partners, not a measurement of anything. **602 of 827
rows (72.8%)** contain at least one drug from a hand-specified low-interaction-potential list (the eight hubs
above plus lactulose, insulin lispro, insulin glargine, mupirocin, chlorhexidine, gabapentin, pregabalin,
emtricitabine).

For benchmark use this is disqualifying rather than merely unbalanced. A classifier can achieve high apparent
accuracy on this negative set by learning to recognise 13 drug identities; the vertex-cover result means a
13-feature lookup table reproduces every negative label. The set contains far less discriminative information
than 797 pairs implies.

**This is a design limitation, not a data error.** Every hub pair is individually defensible; the defect is in
what the aggregate can support.

---

## 5. Clinically implausible co-prescription [design]

21 rows (2.5%) join drugs whose labelled indications make co-prescription in a single patient negligible. For
these, "no reported interaction" measures the absence of co-exposure, not the safety of the combination.

| Row | Drug 1 | Drug 2 | Basis |
|---:|---|---|---|
| 22 | spironolactone | sevelamer | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but spironolactone is contraindicated in anuria/severe renal impairment (hyperkalaemia) — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 66 | atenolol | chlorhexidine | chlorhexidine is a topical/oral-rinse antiseptic with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 69 | atenolol | clotrimazole | clotrimazole here is topical/troche formulation with minimal systemic exposure; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 105 | atenolol | mupirocin | mupirocin is a topical-only antibacterial with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 171 | chlorhexidine | citalopram | chlorhexidine is a topical/oral-rinse antiseptic with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 203 | citalopram | chlorhexidine | chlorhexidine is a topical/oral-rinse antiseptic with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 216 | citalopram | mupirocin | mupirocin is a topical-only antibacterial with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 242 | conjugated estrogens | methylphenidate | labelled indications are age/sex-exclusive (childhood-onset ADHD vs menopausal HRT / postmenopausal osteoporosis); shared patient population is negligible |
| 270 | dextromethorph | mupirocin | mupirocin is a topical-only antibacterial with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 391 | hydrochlorothiazide | sevelamer | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but thiazides are ineffective at eGFR<30 mL/min — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 401 | hydrocodone | chlorhexidine | chlorhexidine is a topical/oral-rinse antiseptic with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 430 | hydrocodone | mupirocin | mupirocin is a topical-only antibacterial with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 546 | metformin | sevelamer | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but metformin is contraindicated at eGFR<30 mL/min/1.73m2 (lactic acidosis) — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 562 | methotrexate | sevelamer | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but methotrexate is contraindicated in severe renal impairment (renal elimination, myelosuppression) — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 591 | mupirocin | citalopram | mupirocin is a topical-only antibacterial with negligible systemic absorption; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 603 | nitrofurantoin | sevelamer | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but nitrofurantoin is contraindicated at CrCl<30-45 mL/min (inadequate urinary concentration, neurotoxicity) — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 695 | sevelamer | clotrimazole | clotrimazole here is topical/troche formulation with minimal systemic exposure; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |
| 699 | sevelamer | glimepiride | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but sulfonylureas are avoided in severe renal impairment (prolonged hypoglycaemia) — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 717 | sevelamer | pemetrexed | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but pemetrexed is contraindicated at CrCl<45 mL/min — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 761 | triamterene | sevelamer | sevelamer indicates dialysis-dependent CKD (hyperphosphataemia of ESRD), but triamterene is contraindicated in significant renal impairment (hyperkalaemia) — the two drugs are not co-prescribable in the same patient, so 'no reported interaction' reflects absent co-exposure |
| 770 | ustekinumab | clotrimazole | clotrimazole here is topical/troche formulation with minimal systemic exposure; a systemic pharmacokinetic interaction is precluded by route, so the negative label is uninformative |

Two mechanisms account for these:

1. **Renal-population conflict (8 rows).** Sevelamer's licensed indication is hyperphosphataemia in
   dialysis-dependent chronic kidney disease. Eight of its partners are contraindicated or ineffective at that
   level of renal function (metformin, nitrofurantoin, methotrexate, pemetrexed, hydrochlorothiazide,
   triamterene, spironolactone, glimepiride). The two drugs in each such pair are not concurrently
   prescribable, so the negative label is structurally guaranteed. A ninth partner, valganciclovir, is
   dose-restricted rather than contraindicated in dialysis and is not flagged.
2. **Route-precluded interaction (12 rows).** Twelve rows pair a systemic drug with a topical or non-absorbed
   agent (mupirocin, chlorhexidine, clotrimazole). A systemic pharmacokinetic interaction is precluded by route
   of administration.

One further row (242, conjugated estrogens × methylphenidate) pairs drugs with age- and sex-exclusive labelled
indications.

Sex-exclusive pairs were tested systematically and **none were found**: no pair joins a male-only drug
(dutasteride, finasteride, alfuzosin, vardenafil) with a female-only drug (conjugated estrogens, raloxifene).
Acute-course × acute-course pairs (two short-course anti-infectives) were also tested and **none were found**.
These two hypothesised defect classes are absent.

---

## 6. Same-class and same-indication pairs [error, against the paper's stated method]

The paper states that expert review considered pharmacological class. Using ATC codes resolved independently
from RxClass and ChEMBL (which agreed on the 4th-level class for all 161 drugs, zero disagreements), **one pair
shares an ATC 4th level and five share an ATC 3rd level**. Adding pharmacodynamic classes that ATC does not
capture, 11 rows (1.3%) pair drugs with a recognised additive or redundant pharmacology:

| Row | Drug 1 | Drug 2 | Basis |
|---:|---|---|---|
| 195 | cinacalcet | sevelamer | both CKD-mineral-and-bone-disorder agents co-prescribed for the same indication; sevelamer alters gastrointestinal pH/binding environment |
| 279 | dextromethorph | zolmitriptan | both serotonergic (dextromethorphan SERT/sigma-1, zolmitriptan 5-HT1B/1D); theoretical serotonin-syndrome additive class |
| 381 | humalog | liraglutide | both ATC A10A/A10B antidiabetics (insulin lispro + GLP-1 RA); additive hypoglycaemia is a recognised pharmacodynamic interaction, not a null pair |
| 394 | hydrocodone | zopiclone | both CNS depressants (opioid + Z-drug); additive sedation/respiratory depression is an FDA boxed-warning combination |
| 396 | hydrocodone | aspirin | share ATC 4th level N02AJ (opioid + non-opioid analgesic combinations); co-formulated products exist |
| 406 | hydrocodone | zaleplon | both CNS depressants (opioid + Z-drug); additive sedation/respiratory depression is an FDA boxed-warning combination |
| 447 | hydroxychloroquine | ustekinumab | both immunomodulators used in overlapping autoimmune indications; additive immunosuppression |
| 545 | metformin | liraglutide | both ATC A10B oral/injectable antihyperglycaemics; additive hypoglycaemia risk |
| 563 | methotrexate | ustekinumab | both ATC L04A immunosuppressants; additive immunosuppression / infection risk |
| 739 | sitagliptin | liraglutide | both incretin-pathway agents (DPP-4 inhibitor + GLP-1 receptor agonist, ATC A10B); mechanistically redundant and not recommended for combination |
| 789 | ustekinumab | pemetrexed | biologic immunosuppressant + antifolate cytotoxic; additive myelosuppression/immunosuppression |

Rows 394 and 406 are the most serious of these: hydrocodone × zopiclone and hydrocodone × zaleplon pair an
opioid with a non-benzodiazepine hypnotic. Concurrent opioid and sedative-hypnotic use carries an FDA boxed
warning for respiratory depression and death. Their presence in a set labelled "potential safe combination" is
a substantive labelling error, not a technicality. Row 739 (sitagliptin × liraglutide) pairs a DPP-4 inhibitor
with a GLP-1 receptor agonist — mechanistically redundant agents acting on the same incretin pathway, whose
combination is not recommended.

The mechanism of these escapes is the same one described in §4: the D3 rule engine models pharmacokinetic
interaction mechanisms. Pharmacodynamic additivity — additive CNS depression, additive hypoglycaemia, additive
immunosuppression — is invisible to it, so pairs whose only interaction is pharmacodynamic pass the filter and
then must be caught by expert review, which did not catch them.

---

## 7. Reconciliation of the published funnel

The published derivation is: 200 drugs → 14,365 candidate pairs → remove 2,110 Ayvaz PDDI pairs → remove 11,130
D3-mechanism pairs → expert review and post-2018-approval cutoff → remove 208 Lexicomp/Drugs.com pairs → 827.

Two arithmetic observations:

- 14,365 = C(170,2), not C(200,2) = 19,900. The stated starting point of 200 drugs does not produce 14,365
  pairs; 170 drugs does. The paper's own mapping loss (30 of 200 drugs lost in the UMLS-to-STITCH step) accounts
  for this, but the funnel as printed does not state it.
- 14,365 − 2,110 − 11,130 − 208 = 917, and 917 − 52 (the duplications removed in Table 1) = 865. The published
  final count is 827, leaving **38 pairs removed by a step that is not quantified in the funnel**. This is
  presumably the expert review and post-2018-approval cutoff, but no count is given for it, so the derivation
  is not reproducible from the paper.

The final file contains 161 distinct drugs — 9 fewer than the 170 that entered pair generation, and 39 fewer
than the 200 claimed. 38 drugs appear only in the `Pair 1` column and 39 only in `Pair 2`; 84 appear in both.

---

## 8. The inferential flaw

The dataset's central claim is that its 827 pairs are "negative reported" and therefore represent potential
safe combinations. This inference does not hold, for three reasons that compound.

**(i) Absence of co-exposure.** A curated interaction knowledge base records interactions that have been
observed or predicted for drug pairs that are actually co-prescribed. For a pair that is rarely or never
co-administered, the base is silent because nobody has looked, not because anyone looked and found nothing.
Section 5 quantifies the clear-cut cases (21 rows, 2.5%), but the effect is not confined to them: the
probability that a pair has been studied scales with its co-prescription frequency, which is not uniform across
the 797 pairs and is not reported anywhere in the dataset. The negative label conflates "studied and found
safe" with "never studied".

**(ii) Reporting and publication bias.** Even among co-prescribed pairs, interaction detection is driven by
spontaneous reporting, case series, and targeted pharmacokinetic studies — all of which are biased toward
severe, acute, and mechanistically expected effects. Interactions that are mild, delayed, or affect a narrow
subpopulation are systematically under-recorded. A negative label inherits this bias in full. The dataset
provides no measure of the evidence density behind any negative call: a pair co-prescribed to millions with no
signal and a pair co-prescribed to nobody receive the same label.

**(iii) The filtering procedure selects for pharmacological inertness by construction.** This is the decisive
problem and it is specific to how this dataset was built. The D3 rule engine removed 11,130 of 12,255 remaining
pairs (90.8%) on the basis of a posited mechanism. Removal on mechanism means the residual set is, definitionally,
the set of pairs for which no mechanism could be posited. Drugs whose molecular class precludes a
pharmacokinetic mechanism — non-absorbed polymers, monoclonal antibodies, peptides, renally cleared
non-CYP substrates — survive against *every* partner. The topology in §4 is the direct fingerprint of this:
13 drugs cover all 797 pairs, and 148 drugs never pair with each other, because the surviving pairs are almost
entirely "one inert drug × one anything". The set therefore does not sample the space of safe combinations; it
samples the space of pharmacokinetically isolated molecules.

The consequences are concrete:

- **The negative label is not a measurement.** For the 291 rows containing sevelamer or ustekinumab (35.2%),
  the absence of a reported pharmacokinetic interaction is predictable from the molecule's class before any
  database is consulted. No evidence was gathered; a structural impossibility was restated.
- **The set is not a valid negative control for a DDI predictor.** A model trained or evaluated on it can
  separate positives from negatives by learning drug identity rather than pair pharmacology. The vertex-cover
  result bounds this precisely: 13 drug identities suffice to reproduce every negative label.
- **Pharmacodynamic interactions are not excluded at all.** Because the removal filter was pharmacokinetic,
  the negative set retains pairs with recognised additive pharmacodynamics, including two opioid ×
  sedative-hypnotic pairs carrying an FDA boxed warning (§6). The label "potential safe combination" is
  therefore not merely weakly supported for these rows — it is contradicted.

The correct framing is that absence of a reported interaction is a statement about the *knowledge base*, not
about the *drug pair*. A rebuilt resource must therefore record, per pair, the basis on which the negative call
is made — measured co-exposure with active surveillance, a targeted negative pharmacokinetic study, expert
adjudication, or mere database silence — and must not present these as a single label. Graded evidence tiers
are not a refinement of the original design; they are the minimum required for the negative claim to carry any
information at all.

---

## 9. What is a data error and what is a design limitation

**Data errors** (the file contradicts the published method or contains objectively wrong values):
the 30 unordered duplicates against a stated duplicate-removal step (§2); 81 rows with stray whitespace and 37
with inconsistent case (§3); `glyceryl trini.` and `dextromethorph` as truncated strings, `humalog` and
`lantus` as brand names, `penicillin` as an unresolvable class term, and `isosorbide` resolving to the wrong
drug entirely (§3); the 11 same-class rows that survived a review stated to consider class, of which the two
opioid × Z-drug rows are mislabelled on clinical grounds (§6); the unexplained 38-pair gap in the published
funnel and the 200-vs-170 drug-count discrepancy (§7).

**Design limitations** (internally consistent, but the construction makes the output uninformative for its
stated purpose): the hub topology and the 13-drug vertex cover (§4); the 21 implausible-co-prescription rows,
which are correctly labelled but carry no information (§5); and the inferential flaw in §8, which is the
reason the other design limitations matter.

Correcting every data error yields 797 clean pairs over 161 correctly-normalised ingredients. It does not
address §4, §5, or §8, which require a different construction, not a cleaner version of this one.

---

## 10. Methods

Pair-level analysis: `pandas`; names normalised by whitespace strip and case-fold before any comparison.
Duplicate detection used unordered frozensets, compared against ordered-tuple detection to establish the
mechanism of the escape. Degree, Gini coefficient, and the greedy vertex cover were computed on the 797-edge
distinct-pair graph.

Name resolution: RxNav REST (`/REST/rxcui.json` with `search=0` for exact and `search=2` for normalised
matching; `/REST/approximateTerm.json` for failures; `/REST/rxcui/{id}/properties.json` for TTY;
`/REST/rxcui/{id}/allrelated.json` for brand-to-ingredient resolution). ATC classes were obtained
independently from RxClass (`/REST/rxclass/class/byRxcui.json`, `relaSource=ATC`, 4th level) and from ChEMBL
(`/chembl/api/data/molecule`, 5th level); the two sources agreed at the 4th level for all 161 names.
DrugBank identifiers were obtained from UniChem (`/unichem/api/v1/compounds`, ChEMBL and InChIKey queries).

Coverage of the normalisation: 160 of 161 names carry an ingredient-level RxCUI (penicillin does not, being a
class term); 161 of 161 carry a ChEMBL ID and an ATC code; **147 of 161 (91.3%) carry a DrugBank ID**. The 14
without one are biologics and non-structural entities for which UniChem holds no ChEMBL–DrugBank cross-reference
(ustekinumab, insulin lispro, insulin glargine, liraglutide, dalteparin, heparin, sevelamer, conjugated
estrogens) or small molecules whose cross-reference is absent from UniChem despite a DrugBank entry existing
(buprenorphine, cephalexin, doxycycline, granisetron, levofloxacin, lisinopril). These six should be mapped by
name against a DrugBank release during the rebuild.

Clinical plausibility, same-class, and route-precluded classifications were assigned by explicit rule sets
encoded in the analysis script (renal contraindication at dialysis-level function; topical/non-absorbed route;
sex- and age-exclusive labelled indication; eight pharmacodynamic additivity classes). These rule sets are
stated in full in the code and are the one part of this audit that rests on pharmacological judgement rather
than on a database lookup; each flagged row carries its justification in the `detail` column of
`audit_defects.csv`.

## 11. Files

- `audit_defects.csv` — 902 defect instances over 782 distinct rows; columns `pair_index`, `drug_1`, `drug_2`,
  `defect_class`, `detail`.
- `audit_drug_normalization.csv` — 161 rows, one per distinct drug name, with RxCUI, RxNorm name and TTY,
  ingredient-level RxCUI, ATC (RxClass 4th level and ChEMBL 5th level), ChEMBL ID, DrugBank ID, degree, and
  resolution status.
- `audit_structure.png` — degree distribution, cumulative concentration, and the anchor/non-anchor edge
  decomposition.
