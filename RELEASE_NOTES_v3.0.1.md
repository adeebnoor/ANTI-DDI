# Anti-DDI v3.0.1 — corrective resource release

Released 20 August 2026.

## Correction

A post-analysis adversarial audit invalidated the four-arm text-classifier/RIDI demonstration previously documented in v3.0.0. The evidence payload leaked the negative class and was not applied to the original confirmed-interaction safety controls. Those efficacy and safety claims are withdrawn as validation evidence. See `VALIDATION_NOTICE_20260820.md`.

## Resource status

The core audited data are unchanged:
- 797 deduplicated pair records;
- 538 T1/T2 higher-support research benchmark candidates;
- 902 legacy defect instances across 782/827 rows;
- 30 clinical exclusions and 3 label exclusions;
- 8 targeted human clinical-pharmacology anchors.

T1/T2 membership remains a resource-level observation-opportunity category, not a clinical safety certification.

## New reproducible analysis

v3.0.1 adds an ATC level-5 degree/popularity-bias diagnostic independent of the invalid classifier experiment. Across 20 seeds, a popularity-only score produced AUC 0.908 ± 0.006 against random unlabelled negatives and 0.900 ± 0.005 against curated Anti-DDI class pairs; after degree matching AUC fell to 0.501 ± 0.004.

The diagnostic is structural and does not adjudicate pair-level clinical non-interaction.

## Transparency

The superseded experimental files/metadata are retained where useful for provenance but are explicitly marked as non-validation evidence. The revised Communications Medicine manuscript is a resource/framework Article and does not use the invalid four-arm experiment in its inferential argument.
