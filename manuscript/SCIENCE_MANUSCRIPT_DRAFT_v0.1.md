# Benchmark structure redirects biomedical AI model selection and discovery priorities

**Draft status:** v0.1 — results-driven skeleton, not submission-ready  
**Target:** Science (flagship)  
**Scope rule:** only results frozen in the `science-structural-shortcuts` branch may enter the main Results. Pending analyses remain explicitly marked.

## Abstract — working draft

Biomedical relation-prediction models are commonly ranked on benchmarks constructed from observed links and sampled non-links, yet those benchmarks can encode structural opportunity independently of pair-specific biology. Across drug–target, protein–protein, drug–disease and disease–gene networks, a degree-only predictor achieved high discrimination under conventional evaluation but approached chance after structural matching. The effect extended unevenly to learned models and changed which model appeared best. Those reversals had large downstream consequences: models selected by conventional versus structure-neutralized evaluation disagreed on 94–100% of their top 100 prioritized hypotheses in two independent relation families. In a frozen BioGRID analysis, conventional evaluation selected NeuralMF whereas structure-neutralized evaluation selected SVD. Both models were then trained on the same historical network and ranked the same 70,041,100 previously unobserved human protein pairs. Of 5,635 relations added in a later BioGRID release, SVD recovered 7 versus 0 within the top 100 and 522 versus 181 within the top 50,000. Benchmark construction can therefore alter not only apparent predictive performance but model selection, scientific prioritization and recovery of later-supported biological relations.

## One-sentence claim

**Benchmark construction can change not only estimated predictive performance, but which biomedical AI model is selected and therefore which biological hypotheses science chooses to pursue.**

## Introduction — argument spine

Biomedical AI increasingly prioritizes drug targets, molecular interactions, disease genes and therapeutic hypotheses. Model comparison therefore has a downstream scientific consequence: benchmark winners can determine which relations receive experimental attention.

However, biological knowledge networks are not exchangeable collections of pairs. Their nodes have highly unequal observation, degree and study histories. Randomly sampled non-links can therefore make structural opportunity predictive even when a score contains no pair-specific biological information. Rich-node and prior biases have been documented in network biology and drug–target prediction, temporal biomedical hypothesis benchmarks already exist, and recent biomedical-KG work has highlighted leakage and failure of random test sets to represent deployment. The unresolved question is broader and more consequential: **does benchmark structure systematically alter model selection across biomedical relation families, and can that change propagate into different scientific hypotheses and different recovery of later evidence?**

We address this question through a sequence of increasingly consequential tests. First, we measure structural inflation with a degree/popularity-only null across heterogeneous biomedical relations. Second, we compare learned model families under conventional and structure-neutralized evaluation. Third, where the winning model changes, we hold the biological candidate universe fixed and quantify downstream hypothesis-selection turnover. Finally, we freeze a historical network, select models using each evaluation regime, rank the complete identical historical unknown-pair universe, and open a later database release to measure which prioritized relations subsequently acquire support.

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

Hypothesis turnover does not identify which list is biologically correct. It establishes the downstream decision consequence: changing only the evaluation rule used to select a model can redirect most of the highest-priority experimental hypotheses. A within-model stability control is required before interpreting the magnitude of cross-model turnover as surprising beyond ordinary training variability.

**Figure 4:** Hypothesis-selection identity and turnover.

### 5. Historical benchmark choice predicts different recovery of later BioGRID relations

To test external validity, we froze BioGRID MV-Physical release 5.0.250 as the historical state and used release 5.0.261 as a later evidence state. The historical human network contained 93,146 unique interactions among 11,844 proteins. We identified 5,635 interactions absent historically but present later whose two endpoints were already represented in the historical network.

Within the historical snapshot, conventional random-negative evaluation selected NeuralMF (mean AUC 0.931) over LightGCN (0.908) and SVD (0.877). Degree-matched evaluation reversed the result: SVD scored 0.766, LightGCN 0.595 and NeuralMF 0.552. In an initial temporal comparison using degree-matched persistent-unobserved controls, SVD achieved 0.703 AUC, compared with 0.589 for LightGCN and 0.549 for NeuralMF.

We then removed the shared matching principle from the temporal endpoint. Each model was trained on the complete historical network and ranked the same **70,041,100** unordered protein pairs that were unobserved at the historical freeze. No degree matching, negative sampling or future-control construction was used. Opening the later release revealed 5,635 subsequently supported relations within this fixed universe. The structure-neutralized winner, SVD, recovered **7, 26, 159 and 522** of these later-added relations within its top 100, 1,000, 10,000 and 50,000 candidates, respectively. The conventional winner, NeuralMF, recovered **0, 5, 42 and 181**; LightGCN recovered **0, 5, 66 and 241**. At top 50,000, SVD therefore recovered 9.26% of all later-added closed-world relations, compared with 3.21% for NeuralMF and 4.28% for LightGCN. Relative to uniform sampling from the complete historical candidate universe, SVD’s later-evidence enrichment was 870-fold at top 100 and 130-fold at top 50,000.

These database additions are later evidence, not an unbiased census of biological truth. Nevertheless, this full-universe analysis avoids constructing the future test with the same degree-balancing rule that selected SVD and directly links historical benchmark choice to different later-supported hypothesis yield.

**Figure 5:** Historical benchmark selection → fixed full candidate universe → later BioGRID evidence.

### 6. Evidence state is distinct from structural opportunity — pending confirmatory analysis

Anti-DDI motivates a second axis of benchmark validity: an unobserved pair is not equivalent to a curated counter-evidence pair. Independent re-execution of the frozen Anti-DDI/GoldD2 assets shows that replacing random missing pairs with curated counter-evidence reduces learned-model performance, but the curated ATC5 pairs have a materially different degree distribution from the positive reference. Exact structural matching covers only a minority of positive test pairs, and forced nearest-neighbor matching leaves meaningful residual imbalance.

We therefore do not present a single matched number as if it isolates evidence state. The confirmatory analysis will model evidence state and structural exposure as distinct axes with explicit balance diagnostics or overlap weighting/stratification.

**Extended Data / Figure 6 candidate:** Evaluation cube: relation evidence state × structural exposure × temporal novelty.

## Discussion — working spine

The findings support a hierarchy of benchmark consequences. First, structural opportunity can inflate apparent separability even without pair-specific biology. Second, learned model families differ markedly in their susceptibility. Third, correcting the evaluation can reverse model selection. Fourth, those reversals can change nearly all top-ranked biological hypotheses. Fifth, in a historical PPI experiment, the model selected after structural neutralization recovered substantially more relations appearing in a later database release even when all models ranked the same complete historical unknown-pair universe.

The work should not be framed as the discovery of degree bias or the invention of temporal biomedical hypothesis benchmarking. Prior studies have established rich-node bias in PPI link prediction, target-prior bias in DTI, temporal evaluation of biomedical hypothesis generation and generalization failures in biomedical-KG evaluation. The contribution tested here is the integrated causal chain from benchmark structure to **scientific decision identity**: the benchmark can determine which model wins, which hypotheses are prioritized and which later-supported relations are preferentially recovered.

Several limits are central. Database additions reflect curation and study processes rather than an unbiased sample of biological truth. Unknown pairs are not true negatives. Degree matching addresses only one structural dimension. The current learned-model ladder is deliberately controlled rather than a comprehensive SOTA leaderboard. Most importantly, the strongest full-universe temporal result currently comes from one PPI data lineage and therefore requires an independent relation family before a universal prospective-discovery claim is justified.

## Proposed reporting standard

A biomedical relation-prediction study making discovery claims should report, at minimum:

1. a structure-only null;
2. conventional and structure-aware evaluation;
3. model-rank stability across evaluation regimes;
4. stability of the induced top-k scientific hypotheses;
5. temporal, independent or cold-start validation;
6. explicit distinction among random unobserved pairs, curated negatives/counter-evidence and contradicted states.

## Main claim boundary before submission

**Allowed now:** benchmark design can alter model ranking and biomedical hypothesis prioritization across multiple relation families; in one frozen PPI temporal analysis, the structure-neutralized-selected model recovered substantially more later-supported relations from the same complete historical candidate universe.

**Not allowed yet:** structure-neutralized evaluation universally improves prospective discovery; all biomedical AI performance is structural; Anti-DDI pairs are clinically safe; persistent unobserved BioGRID pairs are true negatives.

## Decisive remaining experiments

- independently replicate temporal/external validity outside PPI;
- add within-model initialization/split stability controls for H5;
- harden the evidence-aware Anti-DDI analysis with explicit balance diagnostics;
- add at least one stronger relational/GNN or task-specific architecture without changing the frozen evaluation rules;
- add paired uncertainty and sensitivity analyses for future-discovery yield.
