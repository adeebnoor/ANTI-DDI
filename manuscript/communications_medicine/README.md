# Communications Medicine submission map

## Central idea

**A missing DDI edge is an observation about a database; an Anti-DDI state is a claim about evidence.**

Drug–drug interaction informatics has an epistemic asymmetry: reasons for interaction concern are represented explicitly, while evidence against clinically meaningful interaction is often conflated with database absence, sparse evidence, or incomplete coverage. Anti-DDI makes that counter-evidence explicit and graded.

Submitted Article title:

**Anti-DDI: treating drug non-interaction as an evidence state in medication decision support**

## What the Article contributes

1. A conservative evidence-state vocabulary for counter-evidence in DDI informatics.
2. A forensic reconstruction of the historical candidate set with defects and provenance retained rather than hidden.
3. A structural-bias diagnostic showing that a popularity-only score reaches AUC about 0.90 before degree matching and about 0.50 after matching.
4. A public 797-record audit resource and 538-row higher-support benchmark-candidate table.
5. Targeted human/regulatory illustrations that show how direct source anchoring can be represented without treating the selected examples as a validation-rate sample.

## What the Article does not claim

- Dataset membership is not a declaration that a drug pair is clinically safe.
- Database absence is not a negative label.
- The eight clinical anchors are not an unbiased validation cohort.
- The withdrawn classifier/RIDI experiment is not evidence for this resource.

## Frozen resource state

The submission is tied to Anti-DDI v3.0.1 commit:

`95186b7d7d70db78741b6d788bdaf1883f961921`

## Reader-facing evidence map

- Full evidence-state resource: `data/antiddi_v3_dataset.csv`
- Higher-support benchmark candidates: `data/antiddi_v3_benchmark.csv`
- Clinical/regulatory illustrative anchors: `data/clinical_anchor_pairs.csv`
- Instance-level forensic audit: `data/audit_defects.csv`
- Drug-name normalization audit: `data/audit_drug_normalization.csv`
- Audit narrative: `data/audit_summary.md`
- Vertex-cover source data: `data/figure2_vertex_cover_degrees.csv`
- Structural-bias replicate source data: `data/degree_bias_atc5_replicates.csv`
- Structural-bias summary: `data/degree_bias_atc5_summary.json`
- Validation correction record: `VALIDATION_NOTICE_20260820.md`

The exact frozen GoldD2-derived ATC5 positive-reference CSV used in the structural-bias diagnostic is supplied with the journal Supplementary Code and Data archive and is identified by checksum in `data/FROZEN_REFERENCE_MANIFEST.md`.

The full submitted manuscript is intentionally not duplicated here before journal submission; this directory is a reader-facing evidence and concept map rather than a parallel preprint.
