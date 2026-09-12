# Science flagship submission preflight

**Target:** Science (AAAS flagship)  
**Submission system:** Science Content Tracking System (CTS)  
**Status:** living preflight; exact current formatting limits/template must be pulled from the live Science author template at final submission because the public Information for Authors page is not reliably machine-readable in the present environment.

## Editorial objective before formatting

The first submission screen and cover letter must make the case that the paper belongs in a broad general-science journal rather than a specialist ML/biomedical-informatics journal.

The submission pitch is therefore not:

> We introduce a structure-neutralized evaluation method.

It is:

> Biomedical AI benchmarks can determine which model scientists choose, which biological hypotheses they pursue, and which later-supported relationships those choices recover.

## Current CTS submission path verified

The current AAAS Science Content Tracking System is the manuscript-management portal for the Science journals and supports new submissions, manuscript tracking, review and advisor functions.

The submission tutorial linked through the system indicates that an initial Science submission should have the following information ready:

- all authors' names, addresses and email addresses;
- manuscript title and abstract in text form for entry into the portal;
- critical cover-letter information, including:
  - the main point of the paper;
  - its relationship to prior work;
  - colleagues who have reviewed the manuscript;
- a cover-letter file;
- manuscript text/references with figures and captions embedded, with Word preferred by the tutorial and PDF also supported there;
- a combined PDF containing the main manuscript and supplementary materials;
- optional separate supplementary files where appropriate.

Because portal requirements can change, this checklist does **not** freeze old word/figure/reference limits. Those will be rechecked against the live Science template immediately before upload.

## What the editor must understand in the first 30 seconds

1. **Broad problem:** AI increasingly prioritizes what biology investigates next.
2. **Conceptual failure:** benchmark construction is not passive; structural opportunity can influence which model is declared best.
3. **Scientific consequence:** changing the benchmark changes the model and therefore the identity of experimental hypotheses.
4. **Cross-domain generality:** the structural mechanism is reproduced across DTI, PPI, compound–disease and disease–gene relations.
5. **Decision replication:** DTI and PPI show very large hypothesis-identity changes beyond within-model training noise.
6. **External consequence:** a frozen BioGRID historical test links benchmark selection to later-evidence recovery on the same complete candidate universe.
7. **Independent replication:** ChEMBL DTI is the predeclared non-PPI external test and must be resolved before submission.
8. **Modern-model challenge:** GraphBAN is the predeclared contemporary architecture challenge.

## Cover-letter architecture

### Paragraph 1 — why Science

State one broad scientific consequence in plain language. No AUC, no degree bins, no Anti-DDI details.

### Paragraph 2 — what we show

Compress the causal chain:

**structure-only signal → model-rank reversal → hypothesis-identity change → later/independent evidence consequence.**

Use only 2–3 decisive numbers.

### Paragraph 3 — novelty versus closest prior work

Explicitly acknowledge that rich-node/degree bias, target-prior bias and temporal biomedical evaluation have precedents. State that the advance is linking benchmark design to **scientific decision identity and downstream evidence** across relation families.

### Paragraph 4 — rigor

Mention predeclared gates, frozen historical snapshots, identical candidate universes, ensemble stability controls, negative/non-reversal controls, external-source validation, and reproducible code/data checksums.

### Paragraph 5 — broad readership

Explain why the finding matters to researchers using AI to select experiments, not only to link-prediction specialists: drug discovery, systems biology, genetics, knowledge graphs and scientific AI evaluation.

### Closing

State related manuscripts/resources transparently, especially Anti-DDI, and explain the non-overlapping scientific scope. List colleagues who critically reviewed the manuscript when that review has actually occurred; do not invent names merely to populate the field.

## Main-manuscript presentation rules

- Title should state the scientific consequence, not the method.
- Abstract opens with the broad scientific decision problem and uses a concise “Here we show” pivot.
- Main text should tell one escalating story rather than catalogue benchmarks.
- Keep the negative CtD non-reversal and DaG instability boundary visible.
- Prefer five conceptual main figures; push resource/mapping/implementation details to Supplementary Materials.
- AUC establishes the mechanism; Top-K identity and later/independent evidence establish the consequence.
- Later database support is not called biological truth.
- Unknown pairs are never called true negatives without evidence.

## Files to prepare when Science send gates are passed

- final main manuscript using the then-current Science template;
- publication-quality main figures;
- Supplementary Materials with full methods, robustness analyses, mapping audits and extended figures/tables;
- combined submission PDF;
- cover letter;
- data/code availability statements with permanent release/DOI where possible;
- frozen repository release and checksums;
- related-paper disclosure package, including any overlapping Anti-DDI manuscript/material;
- suggested reviewers spanning biomedical AI, network science, evaluation/statistics and biological validation;
- conflict-of-interest, funding, author-contribution and ethics statements as applicable;
- any AI-use disclosure required by the current Science policy at the time of submission.

## Hard no-send conditions

Do not submit to Science if any of these remain unresolved:

- independent non-PPI evidence consequence not completed or conclusively mapping-limited without a defensible alternative;
- no contemporary-model challenge;
- prospective-yield uncertainty omitted;
- headline broader than the actual cross-domain evidence;
- unresolved duplicate-publication/related-paper overlap with Anti-DDI;
- unreproducible result or missing input provenance/checksum;
- cover letter reads as a benchmarking/methods contribution rather than a general scientific-decision result.

## Editorial test

Before upload, every component should answer the same question:

> If this result is correct, does it change how scientists should interpret AI systems that choose what biology to investigate next?

If the answer is obvious from the title, abstract, Figure 1 and cover-letter first paragraph without specialist knowledge, the package is shaped for Science. If not, we revise before submission.
