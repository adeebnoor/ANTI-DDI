# Validation notice — 20 August 2026

## Status

A post-analysis adversarial audit identified a design defect in the experimental four-arm RIDI demonstration previously described in this repository. Those RIDI efficacy and safety claims are **withdrawn as validation evidence** and are not used in the revised Communications Medicine resource/framework manuscript.

## What failed

The frozen classical text backends were trained with an asymmetric evidence token: `ANTIDDI=YES` and the associated evidence payload occurred only in negative-class training examples. The payload therefore acted as a surrogate class label rather than pair-specific pharmacological evidence. In addition, the Anti-DDI intervention was not applied to the held-out confirmed-interaction safety controls in the original safety comparison, so the reported A-versus-D preservation result did not test the intervention itself.

Adversarial tests confirmed that adding a generic Anti-DDI payload could strongly suppress interaction scores even for synthetic or confirmed-interaction pairs. A replication backend also reached a degenerate all-tied score floor, making RIDI=0 dependent on deterministic tie breaking rather than evidentiary stability.

## What is withdrawn

The following are not used as evidence for the Anti-DDI construct or resource:

- the four-arm RIDI efficacy contrast;
- the claim that the intervention preserved all 200 confirmed interactions;
- the regulatory-override result as an empirical safety finding;
- the replication-backend RIDI improvement;
- any inference that the evidence payload improves downstream screening reliability.

The frozen files are retained for provenance where applicable; they should not be cited as successful validation.

## What is unaffected

This defect does **not** alter the underlying audited resource or the analyses that do not use the evidence-token classifier:

- 797 deduplicated pair records and the 827-row legacy audit;
- 902 documented defect instances across 782 legacy rows;
- evidence-tier assignments and co-exposure metadata;
- the 538 T1/T2 higher-support benchmark candidates;
- structural graph findings, including the 13-drug vertex cover;
- structured-label exclusion records;
- the targeted eight-pair human clinical-pharmacology anchor table;
- the degree/popularity-bias analyses when reproduced independently of the flawed text classifier.

## Corrective action

The resource/framework manuscript has been rebuilt around the auditable resource, observation-opportunity grading, structural bias analysis, label contradiction screening, and targeted external human clinical anchoring. The invalid classifier experiment has been removed from the inferential argument.

This notice is intentionally public and permanent so that repository users can distinguish the resource from the superseded experimental demonstration.
