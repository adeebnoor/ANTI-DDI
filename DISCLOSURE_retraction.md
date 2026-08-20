# Retraction disclosure and provenance boundary

## Relationship to the predecessor article

Adeeb Noor, the sole author of the present Anti-DDI resource/framework study, was a co-author and corresponding author of the retracted predecessor article:

Assiri A, Noor A. *Anti-DDI Resource: A Dataset for Potential Negative Reported Interaction Combinations to Improve Medical Research and Decision-Making.* Journal of Healthcare Engineering. 2022;2022:8904342. doi:10.1155/2022/8904342. Retracted in 2023; notice doi:10.1155/2023/9892301.

This relationship is disclosed explicitly because the historical 827-row file is the lineage object audited in the current work. The retracted article and its negative labels are **not** treated as validated evidence for the current resource.

## What the publisher notice states

The publisher reported that its investigation uncovered evidence of one or more indicators of systematic manipulation of the publication process. The notice lists: discrepancies in scope; discrepancies in the description of the research; discrepancies between data availability and the research described; inappropriate citations; incoherent, meaningless and/or irrelevant content; and peer-review manipulation. The publisher stated that it could not vouch for the reliability or integrity of the article. The notice also states that the publisher did not investigate whether the authors were aware of or involved in the systematic manipulation.

Accordingly, this repository does not narrow the retraction to peer-review concerns and does not speculate beyond the notice. This disclosure follows the COPE principle that retraction information should remain linked to the affected work and that the reasons for retraction should be reported objectively and factually (COPE Retraction Guidelines, Version 2, doi:10.24318/cope.2019.1.4).

## How the historical file is used

The predecessor file is retained only for **lineage and forensic audit**. It is used to:

1. identify the historical candidate-pair universe that motivated the re-audit;
2. enumerate duplication, naming defects, structural concentration and clinically problematic pairs; and
3. demonstrate why database absence or inherited negative labels cannot be treated as evidence of non-interaction.

The current evidence state attached to a pair is not inherited from the predecessor label. Current records carry newly computed observation-opportunity fields, explicit evidence tiers, clinical/label exclusions and provenance. Unsupported records are separated as unresolved or excluded rather than forced into a negative class.

## Current corrective status

Anti-DDI v3.0.1 also records a separate correction to an internal four-arm classifier/RIDI validation experiment that had briefly been documented in v3.0.0. A post-analysis adversarial audit found class-label leakage and an invalid safety comparison; the associated efficacy and safety claims are withdrawn. See `VALIDATION_NOTICE_20260820.md`. This correction does not alter the underlying audit table but reinforces the rule that an Anti-DDI evidence state must never be encoded as a surrogate safety label.

## Clinical boundary

Anti-DDI is an evidence framework and research benchmark resource. It is not a list of universally safe drug combinations and does not authorize prescribing, de-prescribing or alert suppression. Direct clinical use requires current drug-information sources, patient context and professional judgment.

## Citation practice

When discussing provenance, cite both the retracted predecessor article and its retraction notice and identify the predecessor as retracted. Do not cite the retracted article as validation of Anti-DDI v3.0.1. Cite the archived corrective dataset release and the accompanying current article when available.
