# Science send decision — evidence matrix

**Target:** Science (AAAS flagship)  
**Rule:** this file is a decision gate, not a claim that publication is likely or guaranteed. A SEND decision requires that the scientific story survives the tests below without broadening claims beyond the evidence.

## Editorial thesis

> Benchmark construction can alter which biomedical AI model is selected, which biological hypotheses are prioritized, and which later or independent evidence those priorities recover.

The paper is not sold as a new degree-bias method. Its Science-level contribution is the experimentally linked decision-consequence chain:

**structural opportunity → model selection → hypothesis identity → later/independent evidence**.

## Gate matrix

| Gate | Requirement | Current evidence | Status |
|---|---|---|---|
| G1 General mechanism | Structural-only signal must inflate conventional evaluation across independent biomedical relation families | DTI, HuRI PPI, compound–disease and disease–gene all reproduce the effect; 4/4 external relation families | **PASS** |
| G2 Learned-model consequence | Learned model families must respond unequally enough to affect substantive conclusions | NeuralMF, SVD and LightGCN show heterogeneous sensitivity; winner reversals in DTI and disease–gene; non-reversal CtD control | **PASS for consequence; heterogeneous by design** |
| G3 Scientific-decision identity | Winner changes must redirect fixed-universe Top-K hypotheses beyond training noise in at least two relation settings | DTI HT@100=1.000 with much smaller within-family instability; PPI HT@100=0.990 with much smaller within-family instability | **PASS** |
| G4 Non-circular temporal consequence | Model chosen before future evidence must differ in later evidence recovery on the same complete candidate universe | Historical BioGRID: SVD 522 vs NeuralMF 181 later-supported relations in top 50,000; paired bootstrap difference remains positive at every prespecified K | **PASS** |
| G5 Independent non-PPI consequence | External evidence source outside PPI must test the predeclared DTI contrast without participating in model selection | ChEMBL 37: SVD recovers 3/5/6 supported pairs at top 100/500/1000 vs NeuralMF 0/0/2; boundary reverses at wide K and is retained | **PASS with high-priority-frontier boundary** |
| G6 Contemporary architecture | A current stronger architecture must be evaluated under the same frozen, leakage-free dual-regime protocol, regardless of direction | GraphBAN mapping gate passes at 99.7% positive-edge feature coverage; leakage-free TargetDecagon challenge is executing under frozen protocol | **PENDING RESULT** |
| G7 Evidence-state robustness | Anti-DDI should test whether random unknown and curated counter-evidence are interchangeable without overclaiming causal isolation | Overlap weighting leaves residual model-dependent differences, but strict balance gate passes only 5/10 seeds | **PASS as boundary/sensitivity only** |
| G8 Related-paper separation | Science manuscript must be substantively distinct from Anti-DDI and RIDI/Nature work | Explicit related-paper boundary; Science uses new broad question, external datasets, learned-model experiments, H5 identity, temporal and ChEMBL consequences | **PASS subject to final disclosure package** |
| G9 Reproducibility | Headline results must have frozen protocol, provenance/checksums and executable analyses | Core gates, BioGRID snapshots, ChEMBL protocol, GraphBAN protocol amendment and result files are frozen; final release/DOI still needed | **PASS for analysis; release packaging pending** |
| G10 Science-shaped presentation | Title, abstract, figures and cover letter must foreground broad scientific consequence, not benchmark mechanics | v0.5 follows consequence-first narrative and Science playbook | **PASS for draft; final editorial polish pending** |

## Hard SEND rule

### SEND to Science if

1. G6 completes successfully as a valid leakage-free contemporary-model evaluation, **even if GraphBAN is less sensitive than simpler models**;
2. the GraphBAN result is reported without cherry-picking or post-outcome tuning;
3. the final abstract preserves the ChEMBL wide-K boundary and the Anti-DDI balance limitation;
4. the final related-paper disclosure clearly separates Anti-DDI and RIDI/Nature materials;
5. all headline figure source data and frozen code are bundled in a permanent release/DOI;
6. a final adversarial editorial read concludes that the first-page message is a broad scientific-decision result rather than a specialist benchmarking paper.

### HOLD / redesign before Science if

- the contemporary-model analysis cannot be completed reproducibly under a leakage-free protocol;
- any headline result depends on changing a threshold, split, matching rule or model after inspecting its outcome;
- the manuscript claims that structure-neutralized selection is universally superior rather than showing a decision consequence with boundaries;
- the Science and Anti-DDI/RIDI manuscripts cannot be cleanly distinguished in question, evidence and principal conclusions;
- the external-consequence story collapses after provenance or leakage auditing.

## What a favorable GraphBAN result would mean

If GraphBAN also shows a material random-to-structure-neutralized change, the paper can state that benchmark sensitivity extends to a contemporary feature-rich graph architecture.

## What an unfavorable GraphBAN result would mean

If GraphBAN is comparatively stable, retain it prominently. The defensible conclusion becomes stronger, not weaker:

> Structural benchmark dependence is model-specific; some contemporary architectures are more robust, but conventional evaluation can still select substantially different scientific priorities among plausible model families.

That result would bound the mechanism and prevent a universal claim.

## Current decision

**HOLD only for G6 completion and final submission packaging.**

The core conceptual case for a Science submission is already supported by cross-domain mechanism, two stability-controlled hypothesis-identity replications, a non-circular temporal consequence, and an independent ChEMBL DTI consequence. The remaining scientific send gate is the frozen leakage-free contemporary-model challenge; the remaining non-scientific work is final release, figures, disclosure, cover letter and adversarial editorial polish.
