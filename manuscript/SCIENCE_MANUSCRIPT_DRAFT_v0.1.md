# Benchmark structure redirects biomedical AI model selection and discovery priorities

**Draft status:** v0.1 — results-driven skeleton, not submission-ready  
**Target:** Science (flagship)  
**Scope rule:** only results frozen in the `science-structural-shortcuts` branch may enter the main Results. Pending analyses remain explicitly marked.

## Abstract — working draft

Biomedical relation-prediction models are commonly ranked on benchmarks constructed from observed links and sampled non-links, yet those benchmarks can encode structural opportunity independently of pair-specific biology. Across drug–target, protein–protein, drug–disease and disease–gene networks, a degree-only predictor achieved high discrimination under conventional evaluation but approached chance after structural matching. The effect extended unevenly to learned models and changed which model appeared best. Those reversals had large downstream consequences: models selected by conventional versus structure-neutralized evaluation disagreed on 94–100% of their top 100 prioritized hypotheses in two independent relation families. In a frozen BioGRID experiment, conventional evaluation selected NeuralMF whereas structure-neutralized evaluation selected SVD; against 5,635 physical interactions added in a later release, SVD achieved 0.703 AUC versus 0.549 for NeuralMF under degree-matched persistent-unobserved controls. These results suggest that benchmark design can redirect model selection and scientific prioritization, motivating evaluation standards that distinguish biological signal from structural opportunity.

## One-sentence claim

**Benchmark construction can change not only estimated predictive performance, but which biomedical AI model is selected and therefore which biological hypotheses science chooses to pursue.**

## Introduction — argument spine

Biomedical AI increasingly prioritizes drug targets, molecular interactions, disease genes and therapeutic hypotheses. Model comparison therefore has a downstream scientific consequence: benchmark winners can determine which relations receive experimental attention.

However, biological knowledge networks are not exchangeable collections of pairs. Their nodes have highly unequal observation, degree and study histories. Randomly sampled non-links can therefore make structural opportunity predictive even when a score contains no pair-specific biological information. Rich-node and prior biases have been documented in network biology and drug–target prediction, and recent biomedical-KG work has highlighted leakage and failure of random test sets to represent deployment. The unresolved question is broader and more consequential: **does benchmark structure systematically alter model selection across biomedical relation families, and can that change propagate into different scientific hypotheses and future discovery performance?**

We address this question through a sequence of increasingly consequential tests. First, we measure structural inflation with a degree/popularity-only null across heterogeneous biomedical relations. Second, we compare learned model families under conventional and structure-neutralized evaluation. Third, where the winning model changes, we hold the biological candidate universe fixed and quantify downstream hypothesis-selection turnover. Finally, we freeze a historical network and ask whether the model favored by each evaluation regime better discriminates relations appearing only in a later database release.

Anti-DDI provides the motivating evidence-state case but is not the scope of the paper. The central unit of analysis is the biomedical relation-prediction benchmark.

## Results

### 1. Structural opportunity alone appears predictive across biomedical relation families

A degree/popularity-only score contained no pair-specific molecular or clinical features. Nevertheless, under conventional negative sampling it achieved AUCs of 0.983 in BioSNAP drug–target interactions, 0.928 in HuRI protein–protein interactions, 0.871 in Hetionet compound–treats–disease relations and 0.876 in Hetionet disease–associates–gene relations. After endpoint-degree matching, the corresponding AUCs were 0.620, 0.513, 0.519 and 0.513. Matching coverage was complete in HuRI and both Hetionet relations and 0.599 in BioSNAP DTI.

This experiment does not establish that learned models use degree alone. It establishes a benchmark-level vulnerability: structural opportunity can separate positives from sampled negatives with little or no relation-specific biology.

**Figure 1:** Cross-domain structural-null atlas.

### 2. Learned models differ in their sensitivity to benchmark structure

We next compared truncated-SVD latent factors, a neural matrix-factorization model and LightGCN-style message passing using the same frozen relation splits. Sensitivity was strongly model- and task-dependent rather than universal.

In DTI, NeuralMF fell from 0.997 to 0.908 AUC and LightGCN from 0.989 to 0.883 after structural matching, whereas SVD changed from 0.950 to 0.914. In compound–disease prediction, NeuralMF fell from 0.879 to 0.560 while LightGCN remained comparatively stable (0.902 to 0.882) and SVD changed from 0.717 to 0.705. In disease–gene prediction, NeuralMF fell from 0.863 to 0.640, LightGCN from 0.794 to 0.721 and SVD from 0.620 to 0.604.

Thus structural correction did not merely lower every score by a common factor; it exposed different dependence on benchmark structure across model families.

**Figure 2:** Model-by-task sensitivity matrix.

### 3. Structural correction reverses which model appears best

The heterogeneous sensitivity changed model selection. In DTI, conventional evaluation ranked NeuralMF first, whereas degree-matched evaluation ranked SVD first. In disease–gene prediction, conventional evaluation favored NeuralMF whereas degree-matched evaluation favored LightGCN. Compound–disease prediction provided a non-reversal control: LightGCN remained first under both regimes.

These reversals motivate a distinction between **performance inflation** and **selection instability**. The latter is scientifically consequential because model selection determines the scoring function subsequently applied to unknown biological relations.

**Figure 3:** Rank trajectories from conventional to structure-neutralized evaluation.

### 4. Benchmark-induced model selection redirects prioritized biological hypotheses

We next asked whether selecting a different model changes scientific prioritization even when the candidate universe is held exactly constant. For each relation family with a winner reversal, the conventional winner and structure-neutralized winner ranked the same frozen set of currently unobserved candidate relations.

In DTI, approximately 817,000 candidates were eligible per split. Candidate-level score agreement between the two selected models was low (mean Spearman 0.091). The top-100 lists had zero overlap in all five frozen seeds (HT@100 = 1.000), HT@500 was 0.9996, and HT@1000 was 0.9406. In disease–gene prediction, approximately 614,000 candidates were eligible; mean score Spearman was 0.258, HT@100 was 0.942 (bootstrap 95% interval 0.924–0.960), HT@500 was 0.899 and HT@1000 was 0.876.

Hypothesis turnover does not identify which list is biologically correct. It establishes the downstream decision consequence: changing only the evaluation rule used to select a model can redirect most of the highest-priority experimental hypotheses.

**Figure 4:** Hypothesis-selection identity and turnover.

### 5. A historical BioGRID freeze links benchmark choice to later evidence

To test external validity, we froze BioGRID MV-Physical release 5.0.250 as the historical state and used release 5.0.261 as a later evidence state. The historical human network contained 93,146 unique interactions among 11,844 proteins. We identified 5,635 interactions absent historically but present later whose two endpoints were already represented in the historical network.

Within the historical snapshot, conventional random-negative evaluation selected NeuralMF (mean AUC 0.931) over LightGCN (0.908) and SVD (0.877). Degree-matched evaluation reversed the result: SVD scored 0.766, LightGCN 0.595 and NeuralMF 0.552. After retraining on the complete historical graph, the same models were evaluated on later-added interactions against degree-matched pairs that remained unobserved. SVD achieved 0.703 AUC, compared with 0.589 for LightGCN and 0.549 for NeuralMF. Thus the model selected by structure-neutralized evaluation exceeded the conventional winner by 0.154 AUC on this temporal test.

This analysis treats later-added interactions as future evidence and persistent-unobserved pairs as controls, not as proven biological negatives. Because the future comparison also uses degree balancing, a stricter full-candidate prospective ranking analysis is treated as a separate confirmatory test rather than inferred from this result.

**Figure 5:** Historical benchmark selection and later BioGRID evidence.

### 6. Evidence state is distinct from structural opportunity — pending confirmatory analysis

Anti-DDI motivates a second axis of benchmark validity: an unobserved pair is not equivalent to a curated counter-evidence pair. Initial frozen-resource analyses show that moving from random unobserved pairs to curated Anti-DDI evidence changes learned-model performance, but the curated ATC5 set has a substantially different endpoint-degree distribution from the positive reference. We therefore do not report a single forced matched estimate as a final result.

The confirmatory analysis will report the evidence-state effect and structural-exposure effect separately, with overlap weighting/stratification or another prespecified balance diagnostic rather than presenting poor matching as if it removed confounding.

**Extended Data / Figure 6 candidate:** Evaluation cube: relation evidence state × structural exposure × temporal novelty.

## Discussion — working spine

The findings support a hierarchy of benchmark consequences. First, structural opportunity can inflate apparent separability even without pair-specific biology. Second, learned model families differ markedly in their susceptibility. Third, correcting the evaluation can reverse model selection. Fourth, those reversals can change nearly all top-ranked biological hypotheses. Fifth, in one historical PPI experiment, the model selected after structural neutralization better discriminated later-added relations under a matched temporal test.

The work should not be framed as the discovery of degree bias. Prior studies have established rich-node bias in PPI link prediction, target-prior bias in DTI and generalization failures in biomedical-KG evaluation. The contribution tested here is the cross-domain causal chain from benchmark structure to **scientific decision identity**: the benchmark can determine which model wins, which hypotheses are prioritized and, potentially, which later-supported relations are recovered.

Several limits are central. Database additions reflect curation and study processes rather than an unbiased sample of biological truth. Unknown pairs are not true negatives. Degree matching addresses only one structural dimension. The current learned-model ladder is deliberately controlled rather than a comprehensive SOTA leaderboard. The temporal result requires replication in at least one independent relation family before a general prospective-discovery claim is justified.

## Proposed reporting standard

A biomedical relation-prediction study making discovery claims should report, at minimum:

1. a structure-only null;
2. conventional and structure-aware evaluation;
3. model-rank stability across evaluation regimes;
4. stability of the induced top-k scientific hypotheses;
5. temporal, independent or cold-start validation;
6. explicit distinction among random unobserved pairs, curated negatives/counter-evidence and contradicted states.

## Main claim boundary before submission

**Allowed now:** benchmark design can alter model ranking and biomedical hypothesis prioritization across multiple relation families; a BioGRID temporal pilot supports external consequences.

**Not allowed yet:** structure-neutralized evaluation universally improves prospective discovery; all biomedical AI performance is structural; Anti-DDI pairs are clinically safe; persistent unobserved BioGRID pairs are true negatives.

## Decisive remaining experiments

- complete the non-circular full-candidate BioGRID future-yield test;
- independently replicate temporal/external validity outside PPI;
- harden the evidence-aware Anti-DDI analysis with explicit balance diagnostics;
- add at least one stronger relational/GNN or task-specific architecture without changing the frozen evaluation rules;
- add paired uncertainty tests and sensitivity analyses for the future-discovery comparison.
