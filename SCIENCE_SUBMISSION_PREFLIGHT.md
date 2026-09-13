# Science flagship submission preflight

**Target:** Science (AAAS flagship)  
**Submission system:** Science Content Tracking System (CTS)  
**Status:** living preflight; exact current formatting limits/template must be pulled from the live Science author template at final submission because the public Information for Authors page is not reliably machine-readable in the present environment.

## Editorial objective before formatting

The first submission screen and cover letter must make the case that the paper belongs in a broad general-science journal rather than a specialist ML/biomedical-informatics journal.

The submission pitch is therefore not:

> We introduce a structure-neutralized evaluation method.

It is:

> Biomedical AI benchmarks can determine which model scientists choose, which biological hypotheses they pursue, and where independent or later biological evidence is concentrated among the hypotheses tested first.

## Current CTS submission path verified

The current AAAS Science Content Tracking System is the manuscript-management portal for the Science journals and supports new submissions, manuscript tracking, review and advisor functions.

The submission tutorial linked through the system indicates that an initial Science submission should have the following information ready:

- all authors' names, addresses and email addresses;
- manuscript title and abstract in text form for entry into the portal;
- critical cover-letter information, including the main point of the paper, its relationship to prior work, and colleagues who have reviewed the manuscript;
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
5. **Decision replication:** DTI and PPI show very large hypothesis-identity changes beyond within-model training noise; disease–gene provides supportive ensemble evidence with an explicit instability boundary.
6. **Temporal consequence:** on the identical 70,041,100-pair historical PPI universe, the neutralized-selected SVD recovered 522 later-added BioGRID relations at Top-50,000 versus 181 for the conventional winner; paired-bootstrap SVD-minus-NeuralMF recall differences were positive at every prespecified cutoff.
7. **Independent non-PPI replication:** in frozen ChEMBL 37 validation, SVD recovered 3/5/6 supported unknown DTI relations at Top-100/500/1,000 versus 0/0/2 for NeuralMF, with the important boundary that the advantage did not persist at broad cutoffs.
8. **Modern-model challenge:** GraphBAN is the frozen contemporary architecture challenge and remains the major unresolved empirical send gate.

## Cover-letter architecture

### Paragraph 1 — why Science

State one broad scientific consequence in plain language. No AUC, no degree bins, no Anti-DDI details.

### Paragraph 2 — what we show

Compress the decision chain:

**structure-only signal → model-rank reversal → hypothesis-identity change → later/independent evidence consequence.**

Use only 2–3 decisive numbers. Favor one hypothesis-identity number and one external-evidence number over a metric catalogue.

### Paragraph 3 — novelty versus closest prior work

Explicitly acknowledge that rich-node/degree bias, target-prior bias and temporal biomedical evaluation have precedents. State that the advance is linking benchmark design to **scientific decision identity and downstream evidence** across relation families.

### Paragraph 4 — rigor

Mention predeclared gates, frozen historical snapshots, identical candidate universes, ensemble stability controls, negative/non-reversal controls, external-source validation, paired uncertainty, and reproducible code/data checksums.

### Paragraph 5 — broad readership

Explain why the finding matters to researchers using AI to select experiments, not only to link-prediction specialists: drug discovery, systems biology, genetics, knowledge graphs and scientific AI evaluation.

### Closing

State related manuscripts/resources transparently, especially Anti-DDI, and explain the non-overlapping scientific scope. List colleagues who critically reviewed the manuscript when that review has actually occurred; do not invent names merely to populate the field.

## Main-manuscript presentation rules

- Title should state the scientific consequence, not the method.
- Abstract opens with the broad scientific decision problem and uses a concise “Here we show” pivot.
- Main text tells one escalating story rather than cataloguing benchmarks.
- Keep the negative CtD non-reversal, DaG instability boundary and ChEMBL broad-K reversal visible.
- AUC establishes the mechanism; Top-K identity and later/independent evidence establish the consequence.
- Treat the **experimental frontier** (small Top-K lists) as scientifically important without claiming that one model is globally superior.
- Later database support and curated ChEMBL support are evidence, not an unbiased census of biological truth.
- Unknown pairs are never called true negatives without evidence.

## Completed send-gate evidence

- [x] Cross-domain structural-null replication: 4/4 relation families.
- [x] Model-rank reversals under frozen evaluation rules.
- [x] Stability-controlled hypothesis identity in DTI.
- [x] Independent PPI hypothesis-identity replication.
- [x] Non-circular BioGRID future-evidence ranking on a shared complete universe.
- [x] Paired uncertainty for BioGRID future evidence (20,000 bootstrap resamples; positive SVD-minus-NeuralMF difference at every prespecified K).
- [x] Independent non-PPI external consequence in ChEMBL 37, with the high-priority-frontier effect and broad-K boundary both retained.

## Remaining hard send gates

- [ ] Complete the frozen GraphBAN contemporary-model challenge on the full planned five-seed set.
- [ ] Finalize the Anti-DDI evidence-state robustness analysis without conflating evidence state and structural exposure.
- [ ] Complete the related-paper/duplicate-publication audit using `RELATED_PAPER_BOUNDARY.md` against the actual final manuscripts.
- [ ] Freeze final figures, code/data provenance and repository release/DOI.
- [ ] Verify exact then-current Science formatting, file and policy requirements immediately before upload.

## Files to prepare when the remaining gates are passed

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

- the full contemporary-model challenge is absent or technically non-comparable;
- headline is broader than the cross-domain and cutoff-dependent evidence;
- unresolved duplicate-publication/related-paper overlap with Anti-DDI;
- evidence-state analysis claims a causal evidence effect while structural imbalance remains uncontrolled;
- unreproducible result or missing input provenance/checksum;
- cover letter reads as a benchmarking/methods contribution rather than a general scientific-decision result.

## Editorial test

Before upload, every component should answer the same question:

> If this result is correct, does it change how scientists should interpret AI systems that choose what biology to investigate next?

If the answer is obvious from the title, abstract, Figure 1 and cover-letter first paragraph without specialist knowledge, the package is shaped for Science. If not, revise before submission.
