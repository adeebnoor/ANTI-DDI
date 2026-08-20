# Paper 5 validation assets

This directory documents the validation study that operationalizes Anti-DDI as an evidence state in a computational medication-screening pipeline.

## Prospective component

The candidate cohort was frozen before confirmatory inference:
- 214 T1/T2 pairs
- 40 development
- 174 confirmatory
- five representation families

The intervention arms were:
- A: raw
- B: canonicalized
- C: Anti-DDI evidence
- D: canonicalized + Anti-DDI evidence

The primary endpoint was the incremental `B - D` change in RIDI@20.

## Primary result

Primary backend:
- A RIDI@20 = 0.746
- B RIDI@20 = 0.308
- D RIDI@20 = 0.243
- B-D = 0.065, a 21.1% relative point-estimate reduction
- 95% paired-bootstrap interval crossed no improvement

This is a non-confirmed primary incremental effect and must remain described as such.

## Safety controls

- 200/200 held-out confirmed interactions remained detected
- 0/3 regulatory overrides were suppressed

These are computational benchmark safety controls, not proof of patient-level clinical safety.

## Human clinical anchoring

A post-confirmatory supportive analysis identified 8 retained T1/T2 Anti-DDI pairs with explicit named-pair human clinical-pharmacology or regulatory evidence of no clinically meaningful interaction. All eight were concordant with the Anti-DDI state.

Because the anchor set was targeted, small, and post-confirmatory, it is a clinical anchor rather than a population diagnostic-accuracy estimate.

See:
- `../data/paper5_split_manifest.csv`
- `../data/clinical_anchor_pairs.csv`
