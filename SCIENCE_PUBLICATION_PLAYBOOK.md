# Science flagship publication playbook

**Target:** Science (AAAS flagship), not Science Advances and not a Science Partner Journal.  
**Project:** structural shortcuts / benchmark-induced scientific decision identity.  
**Purpose:** emulate the editorial logic of recent Science research papers without copying language or overstating evidence.

## 1. What recent Science AI/biology papers actually do

Recent flagship exemplars share a consistent architecture.

### Evo — Nguyen et al., Science 2024, doi:10.1126/science.ado9336

The paper is not framed as a benchmark comparison. It starts from a broad biological problem, introduces a model spanning DNA/RNA/protein scales, then shows functional prediction, generation, and experimentally functional CRISPR/transposon systems. The ending is a biological capability claim.

### ESM3 — Hayes et al., Science 2025, doi:10.1126/science.ads0018

The title itself states the scientific consequence. The abstract starts from evolution, not architecture. The model is made credible by generating fluorescent proteins that are synthesized and shown to function. Method -> generated hypothesis/object -> external functional evidence.

### PromoterAI — Jaganathan et al., Science 2025, doi:10.1126/science.ads7373

Prediction accuracy is only the beginning. The paper connects predicted promoter variants to RNA and protein expression, population negative selection, rare-disease enrichment, and reporter assays. Multiple orthogonal evidence modalities establish scientific consequence.

### BioEmu — Lewis et al., Science 2025, doi:10.1126/science.adv9817

The paper begins with an outstanding biological challenge, then validates against long molecular-dynamics trajectories, static structures, functional motions and experimental stability/free-energy data. The model is a means to a biological capability claim.

## 2. Editorial rule for our paper

We must not sell:

> We propose a better benchmark for biomedical link prediction.

We should test and, if the evidence survives, sell:

> The benchmark used to choose a biomedical AI model can redirect which biological hypotheses are pursued and which later-supported relationships are recovered.

The scientific object is **decision identity**, not degree matching. Structural opportunity is the mechanism that exposes the problem.

## 3. Science-style narrative

### Opening problem

Biomedical AI increasingly decides which targets, interactions and disease mechanisms receive experimental attention. Yet benchmark design can choose the model that makes those decisions.

### Mechanism

Structural opportunity alone discriminates observed relations from sampled non-relations across multiple biomedical relation families.

### Consequence 1 — model identity

Changing only the evaluation regime can reverse which model appears best.

### Consequence 2 — hypothesis identity

When the winner changes, the prioritized biological hypotheses can change far beyond ordinary training noise.

### Consequence 3 — later evidence

A frozen historical experiment must ask whether those different choices recover different relationships that acquire support only later, with every model ranking the same candidate universe.

### Generality

The final flagship claim requires the consequence chain to survive outside a single database lineage and ideally across at least two biomedical relation families.

## 4. Title rule

Science titles are usually short, readable outside the technical subfield, and lead with the scientific advance rather than the method.

Current technical title:

> Benchmark structure redirects biomedical AI model selection and discovery priorities

Preferred working title after independent external replication:

> **Benchmark design redirects biomedical AI discovery**

Conservative title before that replication:

> **Benchmark design redirects biological hypotheses in biomedical AI**

Avoid title terms such as degree bias, matched negatives, link prediction, AUC, benchmark correction, or RIDI. Those belong in the mechanism/results, not the headline.

## 5. Abstract anatomy

One compact paragraph should follow this sequence:

1. broad scientific problem;
2. unresolved failure mode;
3. “Here we show” central finding;
4. cross-domain evidence;
5. model-selection consequence;
6. hypothesis-identity consequence;
7. independent/later-evidence validation;
8. one broad implication sentence.

Do not start the abstract with datasets, model names, AUC, or Anti-DDI.

## 6. Main-figure architecture

Keep the main text conceptually lean. A five-figure story is preferable if the final data support it.

**Figure 1 — The hidden decision problem.** A simple conceptual panel plus cross-domain structure-only null: conventional evaluation makes structure look predictive; neutralization removes most of it.

**Figure 2 — The benchmark changes the winner.** Learned-model sensitivity and rank trajectories across DTI, PPI/drug-disease/disease-gene as available. Include a non-reversal control.

**Figure 3 — The winner changes the science.** Same candidate universe, different selected model, large Top-K hypothesis turnover with within-model/ensemble stability controls.

**Figure 4 — The later-evidence test.** Historical freeze -> full shared candidate universe -> later release. Show cumulative future hits / enrichment rather than only AUC.

**Figure 5 — Independent external replication and reporting standard.** Prefer DTI or another non-PPI domain. Only after this figure exists should the paper make a general prospective-discovery claim.

Anti-DDI evidence-state analysis belongs in Extended Data / Supplementary unless it becomes a decisive orthogonal result.

## 7. What must remain in the main text

- at least one negative/non-reversal control;
- within-model stability control, not only cross-model differences;
- exact historical freeze and candidate-universe definition;
- uncertainty around prospective yield;
- explicit statement that database absence is not biological negativity;
- explicit distinction between later database support and unbiased experimental truth;
- prior-art boundary: we did not discover degree/rich-node bias.

## 8. Science send gates

We do **not** submit to Science merely because the manuscript is polished. Submission is unlocked only if the scientific package satisfies these gates.

### Gate S1 — broad mechanism: PASS

Structural-only inflation reproduced across at least four independent biomedical relation families.

### Gate S2 — model consequence: CURRENTLY SUPPORTED

Evaluation changes model ranking in more than one relation family, with a non-reversal control retained.

### Gate S3 — stable hypothesis consequence: NOW STRONGER

DTI passes strongly. Five-fit ensemble analysis also shows disease-gene cross-selected turnover remains materially larger than leave-one-initialization-out ensemble instability. Treat the original disease-gene single-fit instability transparently rather than hiding it.

### Gate S4 — non-circular later-evidence consequence: PASS IN PPI

BioGRID full-universe H4b passes: all models rank the identical historical candidate universe and the neutralized-selected model recovers more later-supported relations.

### Gate S5 — independent external consequence outside PPI: REQUIRED BEFORE SEND

Replicate the model-selection -> independent/later-evidence consequence in DTI or another non-PPI relation family. ChEMBL is the current primary route. This is the most important missing result.

### Gate S6 — contemporary-model challenge: REQUIRED

Add at least one stronger contemporary relational/GNN or task-specific architecture under the already frozen evaluation rules. The paper must survive the criticism that rank reversal is an artifact of a deliberately simple model ladder.

### Gate S7 — uncertainty and robustness: REQUIRED

Add bootstrap/paired uncertainty for future-hit curves, alternative structural controls, and sensitivity to historical freeze/model initialization without changing the primary endpoint.

### Gate S8 — orthogonal biological evidence: HIGHLY DESIRABLE

Recent Science AI/biology papers frequently validate beyond the benchmark using experiments or orthogonal measurements. A wet-lab experiment is not a formal requirement, but an independently curated or experimentally anchored audit of high-ranked predictions would materially strengthen the flagship case.

## 9. Desk-rejection risks we must eliminate

1. **“This is only a benchmarking/methods paper.”** Counter with model-selection identity, Top-K scientific decisions, and later-evidence recovery.
2. **“Degree bias is already known.”** State that directly and position degree as the instrument, not the discovery.
3. **“BioGRID temporal effects are already known.”** The novelty must be the full causal chain and cross-domain consequence, plus non-PPI replication.
4. **“Future database additions reflect popularity/curation.”** Use full-universe analysis, structural sensitivity analyses, independent source validation, and careful language: later-supported, not true.
5. **“Your candidate lists are unstable anyway.”** Report single-fit and ensemble stability; attribute only the excess cross-selected turnover beyond within-family noise.
6. **“Simple models are not representative.”** Add a strong contemporary architecture without moving the evaluation goalposts.
7. **“The claims are broader than the evidence.”** Preserve negative controls and claim boundaries in the abstract/discussion.

## 10. Writing discipline

- one conceptual claim per Results section;
- lead each section with the scientific question, not the script/dataset;
- numbers support the claim; they do not become the narrative;
- avoid model acronyms in the title and opening sentences;
- use “later-supported relations” rather than “true discoveries” unless independently validated;
- use “structure-neutralized” as an operational evaluation regime, not as the uniquely correct benchmark;
- do not claim all biomedical AI is biased;
- do not claim Anti-DDI pairs are clinically safe;
- make the negative controls visible because they increase credibility.

## 11. Submission package once gates are met

Prepare the submission as one coherent flagship package: concise main manuscript, five main figures, rigorous supplementary methods/results, frozen data/code release with checksums, reporting checklist, cover letter explaining the broad scientific consequence in the first paragraph, related-paper disclosure for Anti-DDI and any overlapping manuscripts, and a referee list spanning biomedical AI, network science, statistical evaluation, and biological validation.

## Bottom line

The paper becomes Science-shaped only when the story reads:

**benchmark structure changes the model -> the model changes the hypotheses -> the hypotheses differ in later/independent biological support.**

The first two arrows are now supported; the BioGRID experiment strongly supports the third in PPI. The decisive remaining move is to reproduce the third arrow independently outside PPI and survive a stronger-model challenge.
