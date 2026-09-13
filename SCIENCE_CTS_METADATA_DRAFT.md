# Science CTS metadata draft

**Internal working file — verify all live CTS labels at upload.**

## Journal and article type

- **Journal:** Science
- **Article type:** Research Article
- **Resubmission:** No, unless CTS is later used for a formally returned version of this same Science manuscript.

## Working title

**Benchmark design redirects biomedical discovery**

## Short abstract for portal / manuscript

Biomedical AI increasingly determines which molecular relations are prioritized for experiments, yet models are often selected on benchmarks that contrast known relations with sampled unknown pairs. Across four relation families, structural observability alone produced strong discrimination and affected learned models unequally, reversing the selected model in drug–target and protein-interaction analyses. These reversals changed 100% and 99% of top-100 hypotheses, respectively, far beyond within-model instability. In a frozen historical BioGRID network, the model selected after structural neutralization recovered 522 of 5,635 later-added interactions among its top 50,000 predictions versus 181 for the conventional winner. Independent ChEMBL evidence was also more concentrated at the earliest drug–target cutoffs, although the advantage did not persist at broad cutoffs. Thus benchmark design can redirect biomedical discovery by changing which model wins and which biology is tested first.

## Authors

**Adeeb Noor** — corresponding author and first author  
Department of Information Technology, Faculty of Computing and Information Technology, King Abdulaziz University, Jeddah, Saudi Arabia.

**Action before submission:** verify exact author list and order after all scientific contributions are frozen. Do not add honorary authors. If additional contributors satisfy authorship criteria, add them consistently to manuscript, CTS, CRediT statement and repository release.

## Funding

Populate only from verified funding/support records relevant to this specific study. Do not infer funding from other Adeeb Noor projects or manuscripts.

If there was no study-specific external funding, use the portal's no-funding route and state this consistently in the manuscript.

## Subject areas

**Do not pre-invent CTS taxonomy labels.** At final submission, select the closest live CTS categories to:
- artificial intelligence / machine learning;
- computational biology / bioinformatics;
- systems/network biology;
- drug discovery / molecular interactions, where available.

Primary editorial positioning should remain **AI for scientific discovery**, not a narrow DTI or pharmacology category.

## Suggested reviewers — selection strategy

CTS currently allows up to five suggested reviewers and marks the step optional. Suggested reviewers should collectively cover:
1. AI/ML evaluation and scientific discovery;
2. biomedical network/link prediction and topology bias;
3. drug–target prediction / molecular ML;
4. protein-interaction networks and temporal validation;
5. reproducible computational biology / benchmark design.

### Independence rules for our shortlist

Do not suggest:
- current or recent collaborators;
- coauthors from recent years;
- colleagues with direct institutional conflicts;
- anyone materially involved in Anti-DDI, RIDI, manuscript review, or development of the current analysis;
- researchers for whom a reasonable editor could perceive a strong personal or competitive conflict.

**Reviewer names will be frozen only after conflict checks against publication/coauthor history.**

## Excluded reviewers

CTS permits excluded-reviewer requests and asks for a brief reason. Use this sparingly and only for concrete scientific or conflict reasons. Do not exclude researchers merely because they may be critical of the work.

## Related manuscripts / overlap disclosure

The cover letter and any CTS related-work field should disclose the separate manuscripts/projects transparently:

- **Anti-DDI:** focuses on evidence-aware reference construction for candidate non-interacting drug pairs and pharmacovigilance/statistical-power tiers.
- **RIDI/Nature manuscript:** focuses on allocation/representation identity under constrained decision systems using distinct tasks and datasets.
- **Current Science manuscript:** asks whether biomedical AI benchmark construction changes model selection, hypothesis identity and later/independent discovery evidence across DTI, PPI and other relation families.

Suggested disclosure language:

> The authors have related ongoing manuscripts that address distinct questions: Anti-DDI concerns evidence-aware construction of candidate non-interacting drug-pair references, whereas separate RIDI work concerns allocation/representation identity in constrained decision systems. Neither manuscript reports the cross-domain benchmark-to-model-to-hypothesis-to-later-evidence chain tested here. Relevant materials can be supplied to the editors on request.

Re-check this statement against the exact submission status and contents of those manuscripts on the day of submission.

## Data and code availability

Final statement must point to:
- frozen GitHub release/commit for the Science project;
- permanent archive/DOI (preferably Zenodo) corresponding exactly to the submitted version;
- source data for all main and supplementary figures;
- release/version identifiers and checksums for BioSNAP, HuRI, Hetionet, BioGRID and ChEMBL-derived evidence;
- executable scripts for every headline result;
- GraphBAN protocol amendment explaining why test-edge-informed message passing is not used as clean evidence.

Do not claim a DOI or archival release until it actually exists.

## Competing interests

Use only verified declarations. Current working assumption is no competing interests specific to this study, but this must be reconfirmed at submission, especially for any patents, consulting, commercial relationships or related intellectual property relevant to biomedical AI benchmarking or discovery prioritization.

## CRediT

Prepare a role-level contribution statement after authorship is frozen. For a single-author version, likely roles include Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Visualization, Writing – original draft, Writing – review & editing, and Project administration, but only declare roles actually performed.

## Upload package mapped to current CTS

### Required manuscript upload
- One complete manuscript file in **DOCX or PDF** with embedded figures/tables for initial editorial reading.

### Cover letter
- `manuscript/SCIENCE_COVER_LETTER_DRAFT_v0.1.md` will be converted to final DOCX/PDF after S6 and release freeze.

### Supplementary/supporting files
Prepare:
- Supplementary Materials PDF/DOCX;
- source-data archive(s) or files as allowed by the live system;
- related-manuscript files if the editors request them;
- reproducibility/readme materials where appropriate.

The CTS tutorial indicates auxiliary supporting files can be uploaded separately. Re-check file-number/size limits in the live portal immediately before upload.

## Final CTS preflight

Before clicking Submit:
- journal = **Science**, not another Science-family journal;
- article type = **Research Article**;
- title matches manuscript exactly;
- author names, order, email and affiliation match exactly;
- abstract matches final manuscript;
- funding is verified;
- subject areas are broad enough for the paper's scientific-discovery framing;
- suggested/excluded reviewer entries have documented conflict checks;
- related-work disclosure is complete;
- manuscript and cover letter are final, not internal drafts;
- all citations and figure numbers resolve;
- repository release/DOI is frozen and public as claimed;
- final generated/previewed submission PDF is inspected page by page.
