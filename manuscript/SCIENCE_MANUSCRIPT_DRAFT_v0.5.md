# Benchmark design redirects biological hypotheses in biomedical AI

**Draft status:** v0.5 — Science-style narrative draft; not submission-ready  
**Target:** Science (AAAS flagship)  
**Submission rule:** do not send until the contemporary-model challenge is complete and the evidence-state/related-paper boundary is finalized.  
**Evidence rule:** only frozen results from `science-structural-shortcuts` enter the main Results; original prespecified gates remain unchanged.

## Abstract

Biomedical artificial intelligence increasingly prioritizes molecular interactions, disease mechanisms and therapeutic hypotheses for experimental follow-up, making model selection a scientific decision rather than a purely computational one. Yet models are commonly selected using benchmarks in which observed relations are contrasted with sampled unknown pairs, a design that can encode structural opportunity independently of pair-specific biology. **Here we show that benchmark design can redirect which biomedical AI model is selected and, consequently, which biological hypotheses are prioritized.** Across drug–target, protein–protein, drug–disease and disease–gene relations, a degree-only predictor showed strong discrimination under conventional evaluation and lost most of it after structural matching. Learned models were affected unequally, reversing the apparent winner in drug–target and disease–gene prediction while leaving a compound–disease control unchanged. In drug–target prediction, five-fit ensembles selected under conventional versus structure-neutralized evaluation disagreed on every top-100 hypothesis, whereas leave-one-initialization-out ensemble turnover was only 0.085 and 0.042. In an independent frozen protein-interaction network, selected-model ensembles disagreed on 99.0% of top-100 hypotheses, compared with within-family turnover of 0.137 and 0.050. The structure-neutralized-selected model subsequently recovered 522 of 5,635 relations added to a later BioGRID release within its top 50,000 candidates versus 181 for the conventionally selected model; paired bootstrap differences were positive at every prespecified cutoff. Finally, in a separately curated ChEMBL 37 drug–target evidence set opened after the evaluation protocol was frozen, the structure-neutralized-selected model recovered 3, 5 and 6 supported unknown relations within its top 100, 500 and 1,000 candidates versus 0, 0 and 2 for the conventional winner, although this advantage did not persist at broad cutoffs. Benchmark construction can therefore alter model identity, hypothesis identity and the evidence concentrated at the experimental frontier.

## Central claim

**The benchmark used to choose a biomedical AI model can change the model, the biological hypotheses it prioritizes, and the evidence concentrated among the hypotheses tested first.**

## Introduction

Biomedical AI is increasingly used to decide which drug targets, molecular interactions, disease genes and therapeutic hypotheses deserve experimental attention. The consequences of model comparison therefore extend beyond predictive metrics. A benchmark winner can become the scoring function that determines which unknown relationships are investigated next.

Biological knowledge networks are not exchangeable collections of pairs. Proteins, drugs and diseases differ markedly in observation history, scientific attention and network degree. As a result, random unknown pairs can be structurally easier to distinguish from observed relations even when a score contains no pair-specific biological information. Rich-node bias in network biology, target-prior bias in drug–target interaction prediction, leakage in biomedical knowledge graphs and temporal hypothesis-generation benchmarks have each exposed parts of this problem. What remains unresolved is the downstream scientific consequence: **can benchmark structure alter the identity of the model selected for discovery, redirect the hypotheses that model prioritizes, and change the evidence concentrated among those priorities?**

We test this question as a sequence of increasingly consequential experiments. We first ask whether structural opportunity alone can appear predictive across distinct biomedical relation families. We then ask whether learned model families respond differently enough to change the benchmark winner. Where the winner changes, we hold the biological candidate universe fixed and quantify whether the resulting hypothesis lists differ beyond ordinary training instability. We then freeze a historical interaction network, allow competing evaluation regimes to select different models, require those models to rank the identical complete candidate universe, and open a later database release to measure which prioritized relations subsequently acquire support. Finally, we test the drug–target result against an independently curated ChEMBL evidence source that is never used for model selection.

Anti-DDI supplies the motivating evidence-state observation but is not the scope of this study. The scientific object is the chain from **benchmark construction to scientific decision identity and consequence**.

## Results

### Structural opportunity alone appears predictive across biomedical relation families

We first constructed a predictor containing no pair-specific molecular or clinical information. Its score depended only on endpoint degree/popularity measured from training relations. Under conventional sampled-unknown evaluation, this structural-only predictor achieved AUCs of 0.983 in BioSNAP drug–target interactions, 0.928 in HuRI protein–protein interactions, 0.871 in Hetionet compound–treats–disease relations and 0.876 in Hetionet disease–associates–gene relations. After endpoint-degree matching, the corresponding AUCs fell to 0.620, 0.513, 0.519 and 0.513. Matching coverage was complete in HuRI and both Hetionet relations and 0.599 in BioSNAP DTI.

The experiment does not imply that learned biomedical models use degree alone. It establishes a reproducible benchmark vulnerability: across several relation families, structural opportunity can discriminate observed relations from sampled unknown pairs in the absence of pair-specific biology.

**Figure 1 — Structural opportunity masquerades as relation signal across biomedical networks.**

### Benchmark structure affects learned models unequally

We next compared truncated-SVD latent factors, neural matrix factorization and LightGCN-style message passing under identical frozen splits. The response to structural matching was neither uniform across models nor uniform across tasks.

In DTI, NeuralMF changed from 0.997 to 0.908 AUC and LightGCN from 0.989 to 0.883, whereas SVD changed from 0.950 to 0.914. In compound–disease prediction, NeuralMF changed from 0.879 to 0.560, LightGCN from 0.902 to 0.882 and SVD from 0.717 to 0.705. In disease–gene prediction, NeuralMF changed from 0.863 to 0.640, LightGCN from 0.794 to 0.721 and SVD from 0.620 to 0.604.

Thus structural neutralization did not merely lower all scores by a common amount. It changed the relative evidence supporting competing model families.

**Figure 2 — Model-specific sensitivity to benchmark structure.**

### Changing the evaluation can change the selected model

The unequal sensitivity was sufficient to reverse model selection. In DTI, conventional evaluation ranked NeuralMF first, whereas degree-matched evaluation ranked SVD first. In disease–gene prediction, conventional evaluation favored NeuralMF whereas degree-matched evaluation favored LightGCN. Compound–disease prediction served as a non-reversal control: LightGCN remained first under both regimes.

A separate historical BioGRID PPI analysis produced the same NeuralMF-to-SVD selection reversal: conventional random-unknown evaluation selected NeuralMF whereas degree-matched evaluation selected SVD.

This distinction is central. Performance inflation changes a number; **selection instability changes the model that will subsequently prioritize biology**.

**Figure 3 — Evaluation regime changes model identity.**

### Model-selection reversals redirect biological hypotheses beyond training noise

We held each biological candidate universe fixed and compared the hypotheses produced by the model selected under conventional evaluation with those produced by the model selected under structure-neutralized evaluation.

In DTI, approximately 817,000 candidate drug–target relations were eligible per frozen split. Across the original five split seeds, NeuralMF and SVD had low score agreement (mean Spearman 0.091); their top-100 lists had zero overlap in every split, with HT@100 = 1.000, HT@500 = 0.9996 and HT@1000 = 0.9406.

We then separated benchmark-induced model identity from ordinary training variability. On one fixed DTI split, five independently initialized fits of each model family were averaged into score ensembles. The conventional-winner versus neutralized-winner ensembles again had HT@100 = 1.000 and HT@500 = 1.000. By contrast, leave-one-initialization-out ensemble perturbations produced mean HT@100 of 0.085 for NeuralMF and 0.042 for SVD, and mean HT@500 of 0.005 and 0.033. The difference therefore persisted after suppressing initialization noise.

We next repeated the scientific-decision identity test in the historical BioGRID PPI network using the complete 70,041,100-pair historical non-edge universe. Three independently initialized fits were averaged within each selected model family. NeuralMF and SVD ensemble rankings differed in 99.0% of their top 100 hypotheses, 98.6% of their top 500 and 97.6% of their top 1,000. In contrast, leave-one-initialization-out turnover was 13.7%, 13.9% and 13.0% for NeuralMF and 5.0%, 3.5% and 3.8% for SVD at the same cutoffs. Thus the benchmark-induced model-selection reversal changed PPI hypothesis identity far beyond within-family ranking instability.

Disease–gene prediction provided a more difficult stability boundary. Single NeuralMF fits were highly unstable, so we retained that result and repeated the analysis using five-fit ensembles. Cross-selected-model ensemble turnover remained HT@100 = 0.800, HT@500 = 0.740 and HT@1000 = 0.717. Corresponding leave-one-initialization-out turnover was lower: 0.378, 0.353 and 0.325 for the conventional winner and 0.219, 0.177 and 0.191 for the neutralized winner. Ensembling reduced the ambiguity but did not erase the original single-fit instability boundary.

Together, DTI and PPI provide independent, stability-controlled demonstrations that benchmark-induced model selection can redirect scientific hypothesis identity by substantially more than training randomness alone, while disease–gene prediction illustrates a domain in which intrinsic model instability must itself be reported.

**Figure 4 — Benchmark choice redirects hypothesis identity after stability control in DTI and PPI.**

### Historical benchmark choice predicts different recovery of later-supported protein interactions

We next asked whether different benchmark-selected models differ only in ranking identity or also in the later evidence recovered by those rankings. BioGRID MV-Physical release 5.0.250 was frozen as the historical state and release 5.0.261 as a later evidence state. The historical human network contained 93,146 unique interactions among 11,844 proteins. We identified 5,635 interactions absent historically but present later whose two endpoints were already represented in the historical network.

Within the historical snapshot, conventional random-unknown evaluation selected NeuralMF (mean AUC 0.931) over LightGCN (0.908) and SVD (0.877). Degree-matched evaluation reversed the ranking: SVD scored 0.766, LightGCN 0.595 and NeuralMF 0.552.

To avoid constructing the future endpoint using the same matching rule that selected SVD, each model was then trained on the complete historical network and required to rank the identical **70,041,100** unordered protein pairs unobserved at the historical freeze. No future negative sampling, degree matching or matched-control construction was used. Opening the later release revealed 5,635 subsequently supported relations within this fixed universe.

The structure-neutralized winner, SVD, recovered 7 later-supported relations within its top 100, 26 within its top 1,000, 159 within its top 10,000 and 522 within its top 50,000. The conventional winner, NeuralMF, recovered 0, 5, 42 and 181 at the same cutoffs; LightGCN recovered 0, 5, 66 and 241. At 50,000 hypotheses, SVD recovered 9.26% of all later-added closed-world relations compared with 3.21% for NeuralMF and 4.28% for LightGCN. Relative to uniform sampling from the complete historical candidate universe, SVD's enrichment was 870-fold at top 100 and 130-fold at top 50,000.

We quantified uncertainty by paired bootstrap resampling the 5,635 later-added relations 20,000 times. The SVD-minus-NeuralMF recall difference remained positive at every prespecified cutoff. At top 100 it was 0.0012 (95% CI 0.0004 to 0.0023), at top 1,000 it was 0.0037 (0.0020 to 0.0057), at top 10,000 it was 0.0208 (0.0163 to 0.0252), and at top 50,000 it was 0.0605 (0.0531 to 0.0680).

Database additions are not an unbiased census of biological truth; they reflect both biology and research/curation processes. The result is therefore interpreted as **later evidence recovery**, not proof that persistent unknown pairs are negative or that SVD is universally superior. Its importance is that the evaluation regime used before the future evidence existed selected models with markedly different subsequent evidence yield on the same complete candidate universe.

**Figure 5 — Benchmark-selected models recover different later evidence from the same historical universe.**

### Independent ChEMBL evidence concentrates differently at the drug–target discovery frontier

The BioGRID experiment provides a temporal consequence within one database lineage. We therefore prespecified an external drug–target validation using ChEMBL 37 before opening its outcome. Models were fitted on BioSNAP only. ChEMBL was not used for model selection, fitting or threshold tuning. The primary evidence definition required Homo sapiens, a direct single-protein target, a binding assay with confidence score 9 and pChEMBL ≥ 6. A stricter pChEMBL ≥ 7 threshold was frozen as a sensitivity analysis.

Mapping covered 264 of 284 BioSNAP drugs (93.0%) and 1,897 of 3,648 genes (52.0%). Within the mapped BioSNAP unknown-pair universe, 66 candidate drug–target relations met the primary ChEMBL evidence definition and 26 met the stricter threshold.

At the highest-priority cutoffs, the model selected after structural neutralization concentrated more external support. SVD recovered **3, 5 and 6** ChEMBL-supported relations within its top 100, 500 and 1,000 candidates, compared with **0, 0 and 2** for NeuralMF, the conventional benchmark winner. The pattern persisted under the stricter pChEMBL ≥ 7 criterion: SVD recovered **2, 3 and 3** supported relations at the same cutoffs versus **0, 0 and 2** for NeuralMF. LightGCN recovered 0, 2 and 5 primary-threshold relations within top 100, 500 and 1,000.

The result was cutoff-dependent rather than universal. At top 5,000 SVD and NeuralMF recovered 13 and 12 primary-threshold relations, respectively; by top 10,000 NeuralMF recovered 19 compared with 15 for SVD, and at top 50,000 the counts were 35 and 23. Thus the external replication does not establish that SVD is globally superior. Instead, it shows that benchmark choice can substantially alter the **experimental frontier**—the small set of hypotheses a discovery program would plausibly test first—even when large candidate lists later converge or reverse.

**Figure 6 — Independent ChEMBL evidence at the high-priority drug–target frontier.**

### Evidence state and structural exposure are distinct benchmark dimensions

Anti-DDI provides a complementary boundary. Replacing randomly unobserved DDI pairs with curated counter-evidence pairs reduced learned-model performance, but those evidence-state sets also differed materially in endpoint-degree distribution. Exact structural matching covered only a minority of positive test pairs and forced nearest-neighbor matching left meaningful residual imbalance.

We therefore do not use a single forced matched estimate to claim that evidence state has been isolated causally. Instead, evidence state and structural exposure are treated as separate benchmark dimensions, with explicit balance diagnostics. This distinction reinforces the broader point that “unknown,” “counter-evidence,” and “negative” are not interchangeable biological labels.

**Extended Data — Evidence state × structural exposure × temporal novelty.**

## Discussion

Biomedical AI benchmarks are often treated as passive measuring instruments. Our results instead show that benchmark construction can become part of the scientific decision process. Structural opportunity alone was strongly predictive under conventional evaluation across four relation families. Learned models depended on that opportunity to different extents, sometimes reversing the model selected as best. In DTI and PPI, ensemble-controlled analyses showed that selected models produced substantially different top-ranked biological hypotheses beyond ordinary training variability. In a historical PPI experiment, the model selected after structural neutralization recovered markedly more relations that acquired support in a later database release, with paired uncertainty excluding zero across every prespecified cutoff. In a separate curated DTI evidence source, the same selection principle enriched externally supported relations at the highest-priority discovery cutoffs.

This work is not a claim to have discovered degree bias. Rich-node bias, target-prior effects, sampling artifacts and temporal-evaluation failures have important precedents. The advance tested here is the **decision chain** connecting these benchmark properties to scientific consequence: benchmark structure can alter model identity; model identity can alter hypothesis identity; and those differences can be reflected in the evidence concentrated among prioritized hypotheses.

The ChEMBL result narrows rather than universalizes the claim. The structure-neutralized-selected model was favored at the experimental frontier, not across all list sizes. At broad cutoffs the conventional winner caught up and eventually exceeded it. This boundary is scientifically important: practical discovery programs rarely validate tens of thousands of candidates, so the identity of the first tens or hundreds of hypotheses can matter even when aggregate large-list recovery differs.

Other negative results define the claim. Compound–disease prediction did not show a winner reversal. Single-fit disease–gene rankings were intrinsically unstable, requiring ensemble confirmation before interpreting cross-model turnover. Anti-DDI counter-evidence could not be cleanly separated from structural exposure by naïve matching. These observations argue against a universal interpretation in which all biomedical AI performance is structural or one correction is uniquely valid.

The major remaining robustness test is architectural. The current controlled model ladder includes matrix factorization, truncated-SVD latent factors and LightGCN-style message passing. Before submission we challenge the conclusion with a stronger contemporary CPI architecture under a protocol frozen before outcome inspection. This test is designed to determine whether the structural effect survives a model developed explicitly for modern compound–protein interaction prediction, not to force a particular winner.

If that challenge preserves the decision-chain result, benchmark reporting for biomedical discovery models should extend beyond aggregate predictive accuracy. Studies should report a structure-only null, model-rank stability across evaluation regimes, within-model stability of induced Top-K hypotheses, hypothesis identity when benchmark winners differ, and temporal or independent evidence for the scientific priorities produced.

## Claim boundary

**Supported now:** benchmark structure can alter apparent performance and model ranking across multiple biomedical relation families; DTI and PPI show large, stability-controlled changes in hypothesis identity; ensemble-controlled disease–gene analysis supports the same direction while retaining an instability boundary; in a non-circular PPI historical experiment, the structure-neutralized-selected model recovered substantially more later-supported relations from the identical complete candidate universe with positive paired-bootstrap differences at every prespecified cutoff; in an independently curated ChEMBL 37 DTI validation frozen before outcome inspection, the structure-neutralized-selected model recovered more external support among the highest-priority Top-100 to Top-1,000 hypotheses, while the advantage did not persist at broad cutoffs.

**Required before Science submission:** complete the frozen GraphBAN contemporary-model challenge; finalize evidence-state robustness; complete related-paper/duplicate-publication disclosure; verify final Science submission formatting from current official guidance.

**Not supported:** all biomedical AI is structurally biased; degree matching is the uniquely correct evaluation; structure-neutralized evaluation always improves discovery; SVD is universally superior; database absence is a true biological negative; Anti-DDI candidate pairs are clinically safe.
