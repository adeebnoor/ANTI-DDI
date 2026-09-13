# Benchmark design redirects biomedical discovery

**Pre-submission research branch for a planned _Science_ Research Article**  
**Status:** core results frozen; one contemporary-model robustness gate (leakage-free GraphBAN challenge) is still running.  
**This branch is not a statement of acceptance, peer review, or publication.**

> **Central result:** the benchmark used to select a biomedical AI model can change which model wins, which biological hypotheses reach the front of the experimental queue, and which later or independent evidence is concentrated among those priorities.

## Why this branch exists

The repository default branch (`main`) remains the independent **Anti-DDI v3.0.1** resource. This branch (`science-structural-shortcuts`) contains a separate research program on **benchmark-induced scientific decision changes in biomedical AI**. The separation is intentional for provenance, related-work disclosure, and reproducibility.

The paper is not presented as a new discovery of degree bias. Prior work has established degree/rich-node bias, target-prior bias, data leakage, and other benchmark artifacts. The contribution tested here is the downstream decision chain:

**benchmark construction → model identity → hypothesis identity → later / independent evidence**

## Main evidence

| Layer | Frozen result | Interpretation |
|---|---|---|
| Structural-only signal | Degree-only AUC falls from 0.983→0.620 (DTI), 0.928→0.513 (HuRI PPI), 0.871→0.519 (compound–disease), 0.876→0.513 (disease–gene) after structural matching | conventional sampled-unknown evaluation can reward structural observability |
| Model selection | DTI and historical PPI switch from NeuralMF under conventional evaluation to SVD after structural neutralization; compound–disease is a non-reversal control | benchmark choice can change the winning model |
| Hypothesis identity | selected-model ensembles disagree on 100% of DTI top-100 and 99% of PPI top-100 hypotheses, far above within-family instability | model-selection reversals change what biology is prioritized |
| Later evidence | on the same 70,041,100 historical BioGRID candidate pairs, SVD recovers 522 later-added relations in top-50k vs 181 for NeuralMF | benchmark-selected models differ in later evidence recovery |
| Independent evidence | in unopened ChEMBL 37 evidence, SVD recovers 3/5/6 supported DTI candidates at top 100/500/1000 vs 0/0/2 for NeuralMF | the experimental frontier changes outside the selection dataset |

The ChEMBL advantage does **not** persist at broad cutoffs; that boundary is retained in the paper. Later BioGRID additions are treated as later evidence, not unbiased biological truth.

## Paper architecture

The planned main paper is intentionally compressed to four figures:

1. **A benchmark can reward structural observability.**
2. **Benchmark choice changes model identity and hypothesis identity.**
3. **Historical benchmark choice changes later evidence recovery.**
4. **Independent evidence differs at the drug–target experimental frontier.**

Specialist diagnostics, negative controls, the disease–gene instability boundary, Anti-DDI evidence-state sensitivity, and the contemporary GraphBAN challenge are placed in Supplementary / Extended Data rather than allowed to dilute the central general-science story.

## Reproduce the evidence

Start here:

- [`SCIENCE_PROJECT.md`](SCIENCE_PROJECT.md) — original prespecified hypotheses and gates; intentionally not rewritten after outcomes.
- [`RESULTS_CHECKPOINT_20260913.md`](RESULTS_CHECKPOINT_20260913.md) — canonical outcome checkpoint.
- [`SCIENCE_SEND_DECISION.md`](SCIENCE_SEND_DECISION.md) — send / hold gate matrix.
- [`SCIENCE_SUBMISSION_STRATEGY_20260913.md`](SCIENCE_SUBMISSION_STRATEGY_20260913.md) — _Science_-specific editorial strategy.
- [`LITERATURE_GAP.md`](LITERATURE_GAP.md) — novelty boundary and closest prior art.
- [`BENCHMARK_MANIFEST.md`](BENCHMARK_MANIFEST.md) and [`CHECKSUMS.sha256`](CHECKSUMS.sha256) — provenance and hashes.
- [`results/`](results/) — frozen seed-level and summary outputs.
- [`analysis/`](analysis/) — executable analyses.
- [`submission/`](submission/) — cover letter, CTS metadata, supplementary draft, file manifest, and generated package workflow.
- [`figures/`](figures/) — main-figure source data and reproducible plotting code.

## Main manuscript

Current editorial-fit manuscript source:

- [`manuscript/SCIENCE_MANUSCRIPT_v0.7_PRE_SUBMISSION.md`](manuscript/SCIENCE_MANUSCRIPT_v0.7_PRE_SUBMISSION.md)

The generated DOCX is built from the same source by GitHub Actions and is deliberately labeled **PRE-SUBMISSION** until the final GraphBAN robustness result is frozen and inserted without changing its predeclared criterion.

## Contemporary-model gate

A leakage-free GraphBAN-style challenge is being run on frozen BioSNAP TargetDecagon. Feature mapping passed the prespecified gate at **18,631/18,690 positive edges (99.7%)**. Held-out positive edges are excluded from message passing. The direction of the result does not determine whether it is reported:

- sensitivity extends the architectural evidence;
- robustness becomes an explicit model-specific boundary;
- technical non-executability is reported rather than replaced by a test-edge-informed protocol.

See [`CONTEMPORARY_MODEL_CHALLENGE.md`](CONTEMPORARY_MODEL_CHALLENGE.md) and [`GRAPHBAN_PROTOCOL_AMENDMENT_20260913.md`](GRAPHBAN_PROTOCOL_AMENDMENT_20260913.md).

## Boundaries we will not cross

This project does **not** claim that:

- degree bias is newly discovered;
- biomedical AI generally learns no biology;
- structural neutralization is universally optimal;
- SVD is the universally best biological model;
- persistent unknown relations are true negatives;
- later BioGRID additions are an unbiased truth set;
- ChEMBL favors the neutralized-selected model at every cutoff;
- Anti-DDI evidence state has been causally isolated;
- the upstream GraphBAN transductive evaluation is leakage-free.

## Related projects

- `main` branch: **Anti-DDI v3.0.1**, an evidence-state resource for drug non-interaction research.
- The separate RIDI / allocation-identity manuscript is not part of this paper's evidence base. Its EPSS/COMPAS analyses, theorem, and primary examples are not reused here.

## Citation and release status

This branch is a **pre-submission reproducibility package**, not a published article. Until a persistent archival release is minted, cite the exact branch/commit used. [`CITATION.cff`](CITATION.cff) and [`.zenodo.json`](.zenodo.json) on this branch describe the Science-paper reproducibility package rather than the Anti-DDI dataset release.

## License

Code remains under the repository software license; dataset/source-material terms remain governed by their original licenses. External datasets (BioSNAP, HuRI, Hetionet, BioGRID, ChEMBL and others) are not relicensed here.