# Benchmark structure redirects biomedical AI model selection and discovery priorities

**Draft status:** v0.2 — results-driven working manuscript, not submission-ready  
**Target:** Science (flagship)  
**Scope rule:** only frozen results from the `science-structural-shortcuts` branch enter the main Results. The original prespecified gates in `SCIENCE_PROJECT.md` remain unchanged.

## Abstract — working draft

Biomedical relation-prediction models are commonly ranked on benchmarks built from observed links and sampled non-links, but those benchmarks can encode structural opportunity independently of pair-specific biology. Across drug–target, protein–protein, drug–disease and disease–gene networks, a degree-only predictor achieved high discrimination under conventional evaluation and lost most of that discrimination after endpoint-degree matching. Learned models were affected unevenly, changing which model appeared best. In drug–target prediction, conventional evaluation selected NeuralMF whereas structure-neutralized evaluation selected SVD; on the same frozen candidate universe their top-100 prioritized hypotheses had zero overlap across five split seeds. A fixed-split stability control showed that this cross-model turnover (HT@100 = 1.000) greatly exceeded within-model initialization turnover (0.307 for NeuralMF; 0.138 for SVD). In an independent frozen BioGRID analysis, conventional evaluation again selected NeuralMF whereas structure-neutralized evaluation selected SVD. Both models then ranked the same 70,041,100 historically unobserved human protein pairs. Of 5,635 relations added in a later BioGRID release, SVD recovered 7 versus 0 within the top 100 and 522 versus 181 within the top 50,000. Benchmark construction can therefore alter not only apparent predictive performance but model selection, scientific prioritization and recovery of later-supported biological relations.

## One-sentence claim

**Benchmark construction can change which biomedical AI model appears best and, through that selection decision, redirect the biological hypotheses prioritized for discovery.**

## Introduction — argument spine

Biomedical AI increasingly prioritizes drug targets, molecular interactions, disease genes and therapeutic hypotheses. Benchmarking is therefore not merely descriptive: the model declared best can determine which unknown relations receive experimental attention.

Biological knowledge networks, however, are not exchangeable collections of pairs. Nodes differ greatly in observation history, degree and scientific attention. Randomly sampled non-links can consequently make structural opportunity predictive even when a score contains no pair-specific biological information. Rich-node bias in network biology, target-prior bias in drug–target prediction, temporal biomedical hypothesis benchmarking and leakage failures in biomedical knowledge graphs are already established. The unresolved question tested here is different: **can benchmark structure propagate through model selection into the identity of prioritized biological hypotheses and into later-supported discovery yield?**

We test that chain in stages. First, we measure structural inflation with a degree/popularity-only null across heterogeneous biomedical relations. Second, we compare learned model families under conventional and structure-neutralized evaluation. Third, where evaluation changes the winning model, we hold the candidate universe fixed and measure downstream hypothesis-selection identity, explicitly benchmarking this effect against within-model training instability. Finally, we freeze a historical interaction network, select models using each evaluation regime, rank the same complete historical unknown-pair universe, and open a later database release to measure which prioritized relations subsequently acquire support.

Anti-DDI provides the motivating evidence-state case but is not the scope of the paper. The central unit of analysis is the biomedical relation-prediction benchmark and the scientific decision induced by model selection.

## Results

### 1. Structural opportunity alone appears predictive across biomedical relation families

A degree/popularity-only score contained no pair-specific molecular or clinical features. Nevertheless, under conventional negative sampling it achieved AUCs of 0.983 in BioSNAP drug–target interactions, 0.928 in HuRI protein–protein interactions, 0.871 in Hetionet compound–treats–disease relations and 0.876 in Hetionet disease–associates–gene relations. After endpoint-degree matching, the corresponding AUCs were 0.620, 0.513, 0.519 and 0.513. Matching coverage was complete in HuRI and both Hetionet relations and 0.599 in BioSNAP DTI.

This establishes a benchmark-level vulnerability rather than a universal claim about learned models: structural opportunity alone can separate observed positives from sampled non-links across distinct biomedical relation families.

**Figure 1:** Cross-domain structural-null atlas.

### 2. Learned models differ in sensitivity to benchmark structure

We compared truncated-SVD latent factors, neural matrix factorization and LightGCN-style message passing under the same frozen relation splits. Sensitivity was model- and task-dependent.

In DTI, NeuralMF fell from 0.997 to 0.908 AUC and LightGCN from 0.989 to 0.883 after structural matching, whereas SVD changed from 0.950 to 0.914. In compound–disease prediction, NeuralMF fell from 0.879 to 0.560 while LightGCN remained comparatively stable (0.902 to 0.882) and SVD changed from 0.717 to 0.705. In disease–gene prediction, NeuralMF fell from 0.863 to 0.640, LightGCN from 0.794 to 0.721 and SVD from 0.620 to 0.604.

Structural correction therefore did not subtract a common amount from all models; it exposed different dependence on benchmark structure.

**Figure 2:** Model-by-task evaluation sensitivity.

### 3. Structural correction can reverse model selection

The heterogeneous sensitivity changed which model appeared best. In DTI, conventional evaluation ranked NeuralMF first whereas degree-matched evaluation ranked SVD first. In disease–gene prediction, conventional evaluation favored NeuralMF whereas degree-matched evaluation favored LightGCN. Compound–disease prediction provided a useful non-reversal control: LightGCN remained first under both evaluation regimes.

This separates performance inflation from **selection instability**. Selection instability is the more consequential object because it changes the scoring function subsequently applied to unknown biological relations.

**Figure 3:** Model-rank trajectories across evaluation regimes.

### 4. In DTI, benchmark-induced model selection changes hypothesis identity beyond training noise

We next held the biological candidate universe fixed and compared the hypotheses prioritized by the DTI model selected under conventional evaluation with those prioritized by the model selected under structure-neutralized evaluation. Approximately 817,000 candidate drug–target relations were eligible per frozen split. Candidate-level score agreement between NeuralMF and SVD was low (mean Spearman 0.091). Their top-100 lists had zero overlap in all five split seeds (HT@100 = 1.000); HT@500 was 0.9996 and HT@1000 was 0.9406.

A fixed-split stability control then varied only training/initialization randomness. Mean pairwise HT@100 was 0.307 for NeuralMF and 0.138 for SVD, compared with 1.000 between the conventionally selected and structure-neutralized-selected models. At HT@500, within-model turnover was 0.036 for NeuralMF and 0.136 for SVD versus 0.999 across selected models. The benchmark-induced model-selection change therefore redirected DTI hypotheses far more strongly than ordinary initialization variability under this controlled design.

Disease–gene prediction provided an important boundary case. Although conventional versus neutralized winners initially showed HT@100 = 0.942, NeuralMF itself showed within-model HT@100 = 0.934 on a fixed split. We therefore do **not** attribute the disease–gene turnover primarily to benchmark-induced model selection and do not count it as a second robust H5 replication.

**Figure 4:** DTI hypothesis-selection turnover with within-model stability controls; disease–gene boundary result in Extended Data.

### 5. Historical benchmark choice predicts different recovery of later BioGRID relations

We froze BioGRID MV-Physical release 5.0.250 as the historical state and used release 5.0.261 as a later evidence state. The historical human network contained 93,146 unique interactions among 11,844 proteins. We identified 5,635 interactions absent historically but present later whose two endpoints were already represented in the historical network.

Within the historical snapshot, conventional random-negative evaluation selected NeuralMF (mean AUC 0.931) over LightGCN (0.908) and SVD (0.877). Degree-matched evaluation reversed the result: SVD scored 0.766, LightGCN 0.595 and NeuralMF 0.552. In an initial temporal comparison using degree-matched persistent-unobserved controls, SVD achieved 0.703 AUC, compared with 0.589 for LightGCN and 0.549 for NeuralMF.

We then removed the shared matching principle from the temporal endpoint. Each model was trained on the complete historical network and ranked the same **70,041,100** unordered protein pairs that were unobserved at the historical freeze. No degree matching, negative sampling or future-control construction was used. Opening the later release revealed 5,635 subsequently supported relations within this fixed universe. The structure-neutralized winner, SVD, recovered **7, 26, 159 and 522** later-added relations within its top 100, 1,000, 10,000 and 50,000 candidates, respectively. The conventional winner, NeuralMF, recovered **0, 5, 42 and 181**; LightGCN recovered **0, 5, 66 and 241**. At top 50,000, SVD recovered 9.26% of all later-added closed-world relations versus 3.21% for NeuralMF and 4.28% for LightGCN. Relative to uniform sampling from the complete historical candidate universe, SVD’s later-evidence enrichment was 870-fold at top 100 and 130-fold at top 50,000.

These additions are later database evidence, not an unbiased census of biological truth. Nevertheless, the full-universe analysis avoids defining the future endpoint by the same degree-balancing intervention used for model selection.

**Figure 5:** Historical model selection → complete shared candidate universe → later BioGRID evidence.

### 6. Evidence state is distinct from structural opportunity

Anti-DDI motivates a second benchmark axis: an unobserved pair is not equivalent to a curated counter-evidence pair. Independent re-execution of the frozen Anti-DDI/GoldD2 assets shows that replacing random missing pairs with curated counter-evidence reduces learned-model performance. However, the curated ATC5 evidence pairs differ materially in endpoint-degree distribution from the positive reference. Exact structural matching covers only a minority of positive test pairs, and forced nearest-neighbor matching leaves meaningful residual imbalance.

We therefore do not present a single forced matched estimate as if it isolates evidence state. The confirmatory analysis treats evidence state and structural exposure as separate axes with explicit balance diagnostics, overlap weighting or stratification.

**Extended Data / Figure 6 candidate:** relation evidence state × structural exposure × temporal novelty.

## Discussion — working spine

The findings support a hierarchy of benchmark consequences. Structural opportunity alone can inflate apparent separability across multiple biomedical relation families. Learned model families differ in their sensitivity, and the correction can reverse model selection. In DTI, that reversal changes top-ranked hypothesis identity far beyond within-model initialization noise. In a separate historical PPI analysis, the model selected after structural neutralization recovered substantially more relations appearing in a later BioGRID release even when all models ranked the same complete historical unknown-pair universe.

The contribution is therefore not the discovery of degree bias or the invention of temporal biomedical hypothesis evaluation. Those precedents already exist. The contribution being tested is the integrated decision chain from benchmark structure to **scientific decision identity and consequence**: benchmark construction can determine which model wins; the winner can determine which hypotheses are prioritized; and, in one independent temporal domain, the neutralized-selected winner preferentially recovered later-supported relations.

The negative and boundary findings matter. LightGCN remained the winner in compound–disease prediction under both regimes. Disease–gene hypothesis lists were intrinsically unstable across model initializations, preventing clean causal attribution of their turnover to benchmark selection. Anti-DDI evidence-state and structural-exposure differences cannot be separated by naïve forced matching. These boundaries argue against a universal “all biomedical AI is structurally biased” interpretation.

Several limitations remain. Database additions reflect research and curation processes rather than an unbiased sample of biological truth. Unknown pairs are not true negatives. Degree matching addresses only one structural dimension. The current learned-model ladder is deliberately controlled rather than a comprehensive contemporary SOTA leaderboard. Most importantly, the strongest full-universe temporal result currently comes from one PPI data lineage, and the clean hypothesis-identity result currently comes from one DTI benchmark. Independent replication of each consequence remains necessary before a universal prospective-discovery claim is justified.

## Proposed reporting standard

A biomedical relation-prediction study making discovery claims should report, at minimum:

1. a structure-only null;
2. conventional and structure-aware evaluation;
3. model-rank stability across evaluation regimes;
4. within-model stability of induced top-k hypotheses;
5. hypothesis-selection identity when model winners differ;
6. temporal, independent or cold-start validation;
7. explicit distinction among random unobserved pairs, curated negatives/counter-evidence and contradicted states.

## Main claim boundary before submission

**Allowed now:** benchmark design can alter model ranking across biomedical relation families; in DTI, a winner reversal produces hypothesis turnover far beyond within-model initialization noise; in one frozen PPI temporal analysis, the structure-neutralized-selected model recovers substantially more later-supported relations from the same complete historical candidate universe.

**Not allowed yet:** structure-neutralized evaluation universally improves prospective discovery; all biomedical AI performance is structural; disease–gene turnover is caused mainly by benchmark choice; Anti-DDI pairs are clinically safe; persistent unobserved BioGRID pairs are true negatives.

## Decisive remaining experiments

- replicate temporal/external validity outside PPI, preferably in DTI;
- seek a second stable hypothesis-identity replication using ensemble/stability-controlled ranking, including PPI;
- add at least one stronger contemporary relational/GNN or task-specific architecture without changing the frozen evaluation rules;
- formalize uncertainty and sensitivity analyses for prospective discovery yield;
- harden the Anti-DDI evidence-state analysis with explicit balance diagnostics.
