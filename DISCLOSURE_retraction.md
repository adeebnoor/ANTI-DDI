# Retraction disclosure and provenance boundary

## Purpose

This file documents the relationship between Anti-DDI v3 and the retracted predecessor article:

Assiri A, Noor A. *Anti-DDI Resource: A Dataset for Potential Negative Reported Interaction Combinations to Improve Medical Research and Decision-Making.* Journal of Healthcare Engineering. 2022;2022:8904342. doi:10.1155/2022/8904342. Retracted in 2023; retraction notice doi:10.1155/2023/9892301.

Anti-DDI v3 does **not** treat the retracted article or its labels as validated evidence.

## What the retraction notice states

The publisher's retraction notice reports that an investigation identified evidence of one or more indicators of systematic manipulation of the publication process. The notice lists indicators including discrepancies in scope, discrepancies in the description of the research, discrepancies between the availability of data and the research described, inappropriate citations, incoherent or irrelevant content, and peer-review manipulation. The publisher therefore states that it cannot vouch for the reliability or integrity of the article. The notice does not determine whether the authors were aware of or involved in any manipulation.

Accordingly, this repository does not characterize the retraction as being limited to peer-review concerns, and it does not use the retracted article as evidence for any current Anti-DDI claim.

## How the historical file is used

The 827-row predecessor file is retained only for **lineage and audit**. It serves two bounded purposes:

1. to identify the historical candidate-pair universe that motivated the re-audit; and
2. to quantify defects, naming problems, duplication, structural concentration, and clinically problematic pairs in that historical artifact.

The current evidence state attached to a pair is **not inherited** from the predecessor label. It is re-evaluated using the current release's independent evidence layer and explicit tiering rules. Therefore:

- historical pair provenance is retained;
- historical negative labels are not trusted;
- current Anti-DDI evidence states must be justified by current evidence fields;
- unresolved and positive-concern records are explicitly separated from the supported benchmark.

## Audit findings retained from v2

The v2 audit found 797 distinct unordered pairs among 827 historical rows and documented substantial defects and structural concentration. The complete machine-readable audit remains in the repository. The usable default benchmark is restricted to the current T1/T2 evidence-supported records; T4 records are explicitly unresolved, and clinical/regulatory positive-concern pairs are excluded from Anti-DDI use.

## Clinical boundary

Anti-DDI is an evidence framework and research benchmark. It is not a list of universally safe drug combinations and does not authorize prescribing, de-prescribing, or alert suppression. Patient-specific decisions require current clinical drug information and professional judgment.

## v3 extension

Version 3 adds explicit knowledge-state semantics, a frozen Paper 5 development/confirmatory split, and a small post-confirmatory set of named-pair human clinical-pharmacology anchors. These additions do not retroactively validate the historical predecessor file. They provide new, auditable evidence layers for the current resource.

## Recommended citation practice

Do not cite the retracted article as validation of Anti-DDI v3. Cite the archived v3 dataset release and, once available, the accompanying Anti-DDI article. The retracted article and notice may be cited only when discussing provenance and the retraction history.
