# Literature gap and novelty boundary

## Why this file exists

The Science project must not claim that degree bias, rich-node bias, prior bias, or negative-sampling bias are new. Several strong papers already establish parts of that story. The project is viable only if it moves from isolated-domain observations to a general, causally tested statement about biomedical AI evaluation and external validity.

## Closest prior art identified at project start (13 September 2026)

### 1. Generic graph link prediction

**Aiyappa et al., ICML 2025 — “Implicit degree bias in the link prediction task.”**

Core result: conventional edge-vs-random-nonedge sampling favors high-degree nodes; a degree-only null can approach optimal performance; the authors propose degree-corrected link prediction and show improved alignment with recommendation-task performance.

Implication for us: we cannot claim invention of degree-corrected link prediction. Our contribution must be biomedical, cross-domain, and tied to substantive biological/external-validation consequences.

Source: https://proceedings.mlr.press/v267/aiyappa25a.html

### 2. Network biology

**Kojaku/Ahn and colleagues, PNAS 2025 — bias-aware training and evaluation of link prediction algorithms in network biology.**

Core result: uniform random edge-based evaluation favors rich/high-degree nodes, including across network snapshots; the paper proposes AWARE strategies emphasizing low-degree nodes.

Implication for us: PPI/network-biology degree bias is established. We need to test whether the same structural failure systematically contaminates heterogeneous biomedical relation claims and whether correction changes model conclusions.

Source: https://pubmed.ncbi.nlm.nih.gov/40493194/

### 3. Drug–target interaction prediction

**Lin et al., Nature Communications 2025 — TAPB.**

Core result: target prior tendency can act as a confounder in DTI datasets; models can exploit target-specific label priors rather than genuine interaction mechanisms; the authors introduce an interventional debiasing framework.

Implication for us: DTI prior bias is established. A DTI-only paper will not be novel enough. DTI should be one relation family in a broader test.

Source: https://www.nature.com/articles/s41467-025-66915-1

### 4. Biomedical knowledge-graph link prediction

**Bioinformatics 2026 — benchmarking data leakage in biomedical KGE.**

Core result: evaluates redundancy, degree-related illegitimate features, and sampling/distribution shift in biomedical link prediction. Degree-preserving permutation did not explain all model performance, especially for decoder-only models, while external/cold-start evaluation exposed important reliability issues.

Implication for us: “biomedical KG models may use degree” is not enough. We need a stronger decomposition and a cross-task claim that survives comparison with multiple interventions, not a single degree-preserving permutation.

Source: https://academic.oup.com/bioinformatics/article/42/8/btag608/8767164

### 5. Modern biomedical relational GNNs

**BioPathNet, Nature Biomedical Engineering 2026.**

The paper explicitly analyzes high-degree bias and uses stringent negative sampling while reporting strong performance across several biomedical relation tasks.

Implication for us: strong modern models are already bias-aware. The Science project must show either (a) residual benchmark shortcut effects even in strong contemporary models, (b) model-rank reversals under standardized structural controls, or (c) that corrected evaluation better predicts genuinely independent/temporal performance.

Source: https://www.nature.com/articles/s41551-025-01598-z

## The defensible novelty target

The project should aim to establish all three levels below.

### Level A — cross-domain prevalence

Use the same prespecified model-free structural audit across independent relation families (DDI, DTI, PPI, drug–disease, heterogeneous KG relations). This yields a comparable atlas rather than a collection of anecdotes.

### Level B — scientific consequence

Demonstrate that structural correction changes conclusions about learned models: absolute performance, confidence, or rank ordering. Merely showing that a degree-only null performs well is not enough after ICML 2025.

### Level C — external validity

The strongest target is to show that structure-neutralized evaluation is a better predictor of performance on genuinely novel relationships: temporal holdout, independent source, endpoint-disjoint/cold-start set, or prospective curation.

If Level C succeeds across multiple domains, the result is substantially stronger than the current prior art because it connects benchmark design to the scientific validity of biomedical predictions.

## Anti-DDI’s role

Anti-DDI remains valuable because it contains a particularly clean motivating contradiction:

- a popularity-only score with no pair-specific pharmacology gives ~0.90 AUC under conventional/curated ATC5 evaluation;
- after degree matching, the same score is ~0.50;
- the dataset explicitly distinguishes evidence states rather than equating missing edges with negative biology.

But Anti-DDI should be Figure 1 / seed observation, not the scope of the paper.

## Claims we must avoid

Do **not** claim:

- “we discovered degree bias in link prediction”;
- “biomedical AI generally learns no biology”;
- “all reported biomedical link-prediction performance is invalid”;
- “degree matching is the uniquely correct evaluation design”;
- “Anti-DDI candidates are safe drug combinations.”

Any final claim must be proportional to the cross-domain and external-validation evidence actually obtained.
