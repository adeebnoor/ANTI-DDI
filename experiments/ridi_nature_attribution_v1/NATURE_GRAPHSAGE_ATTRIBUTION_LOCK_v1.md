# Nature learned-model attribution experiment — prospective lock v1

**Lock date:** 2026-08-23 (Asia/Riyadh)  
**Status:** design freeze before any new-seed outcomes are computed  
**Parent evidence:** frozen RTX-KG2 GraphSAGE experiment already reported in the candidate manuscript  
**Purpose:** test whether the previously observed representation-associated GraphSAGE decision turnover contains a structural component that exceeds same-representation retraining stochasticity. This experiment tests attribution, not whether turnover exists.

## Why this experiment
The existing three-seed GraphSAGE result shows high global agreement and nearly unchanged held-out recovery while top-k decisions differ. However, three seeds are insufficient to calibrate that contrast against retraining randomness. ReVerb45K DistMult demonstrates why this control is necessary: raw representation turnover can be almost indistinguishable from seed-to-seed turnover.

## Frozen data and task
Use the exact RTX-KG2 2.7.3 frozen chemical–disease files, mappings, candidate universe, group-safe split and GraphSAGE architecture from `PHASE8_GRAPHSAGE_PROTOCOL_LOCKED.md`.

**Primary stratum:** chemical–disease.  
Rationale fixed before new outcomes: this stratum has the cleanest existing high-global-agreement signal and non-degenerate local tie structure. Chemical–gene remains a secondary transport analysis only if compute permits.

No source assertion, query, candidate, mapping, split, architecture, optimizer, early-stopping rule, feature set or decision cutoff may be changed after this lock.

## Model
Reuse the exact prior GraphSAGE specification:
- two full-neighbourhood mean-aggregation layers;
- hidden/output dimensions 64/64;
- type plus normalized log-degree node features;
- dropout 0.10;
- dot-product link decoder;
- Adam, learning rate 0.01, weight decay 1e-5;
- maximum 60 epochs;
- early-stopping patience 8;
- same deterministic negative construction and edge caps.

## New seed set
Seeds are the first 16 31-bit integers obtained from SHA-256(`RIDI-NATURE-GRAPHSAGE-ATTRIBUTION-v1|i`) for i=0..15. They were generated mechanically, not selected from outcomes:

`[355092268, 1972696080, 1590711264, 1745982372, 1113956884, 734518037, 1017280056, 54477576, 202245501, 871610103, 1739075335, 404365195, 1603643707, 1173720350, 1263375671, 1531572456]`

Split them in generation order into two disjoint sets:
- A = first 8 seeds
- B = last 8 seeds

## Ensemble decision construction
For every query and seed, convert candidate scores to within-query percentile ranks to remove arbitrary cross-seed score-scale differences. Ties use the existing deterministic SHA-256 identity tie-break. For an ensemble of m seeds, average percentile ranks candidate-wise and rank by that mean.

Use nested ensemble sizes m ∈ {1,2,4,8} from the prefixes of A and B.

## Contrasts
At each m and k ∈ {100,500,1000} compute query-level RIDI for:

**Representation contrasts**
1. R0(A_m) vs R1(A_m)
2. R0(B_m) vs R1(B_m)

**Same-representation stochasticity contrasts**
3. R0(A_m) vs R0(B_m)
4. R1(A_m) vs R1(B_m)

The representation summary is the mean of contrasts 1–2 for each query. The stochasticity summary is the mean of contrasts 3–4 for the same query.

## Primary endpoint
For m=8, define query-level AURIDI as the simple mean of RIDI@100, RIDI@500 and RIDI@1000. Define

`Δ = AURIDI_representation − AURIDI_stochasticity`.

Use a two-sided 95% percentile bootstrap over the 200 frozen queries (10,000 resamples, seed derived from the same lock label).

**Primary attribution success criterion:** lower bound of the 95% bootstrap CI for mean Δ is > 0.

This single primary endpoint avoids declaring success from whichever cutoff is most favourable.

## Secondary endpoints
- Δ separately at k=100,500,1000 for m=8;
- convergence curves for representation and stochasticity AURIDI across m=1,2,4,8;
- held-out MRR/AUROC/AP averaged across the same ensembles, reported descriptively;
- the B-versus-A swapped construction as a symmetry check (already inherent in the two representation contrasts);
- chemical–gene replication, if run, is secondary and cannot rescue failure of the primary chemical–disease endpoint.

## Interpretation fixed before outcomes
- **If primary CI > 0:** the learned-family result supports a representation-associated component beyond retraining stochasticity on this frozen task. Do not claim universal dominance across models or cutoffs.
- **If CI includes 0:** G3 remains unmet. Retain the result and frame learned models as a boundary where representation attribution remains unresolved.
- **If mean Δ < 0:** treat retraining stochasticity as the dominant source for this model/task; do not search alternative seeds, cutoffs, architectures or strata for a confirmatory rescue. Any later work must be labelled exploratory or separately prospectively locked.

## Reporting discipline
Report all 16 seeds, all m values and all three k values. Do not exclude failed runs unless a pre-defined implementation/integrity check fails; all exclusions require a dated correction addendum before inspecting replacement outcomes.
