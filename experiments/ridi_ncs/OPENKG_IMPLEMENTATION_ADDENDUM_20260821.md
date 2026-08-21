# OpenKG implementation addendum — locked before outcome computation
Date: 2026-08-21
Parent protocol: OPENKG_PROSPECTIVE_LOCK_20260821.md
Status: prospective implementation detail; written before any ReVerb45K RIDI outcome is computed.

## Frozen split and candidate construction
- Union CESI ReVerb45K validation and test JSONL files; source rows are not edited.
- Gold identity pair = unordered pair of Freebase `true_link` subject/object IDs.
- Deterministic 20% identity-pair holdout using SHA-256 of `20260821|u|v`.
- If a held-out identity is absent from the training identity graph, that held-out pair is excluded before scoring because neither representation can support an inductive structural score.
- All source-form edges belonging to a held-out gold identity pair are removed from R0 training; the corresponding canonical edge is removed from R1 training.
- Fixed negative universe: 5 negatives per held-out positive, sampled with seed 20260821 from non-edge gold identity pairs, capped at 100,000 negatives.

## Alignment between representations
- R0 is scored on surface-form nodes. A gold identity-pair score equals the maximum score across all observed surface-alias pairs for those two identities.
- R1 is scored directly on gold Freebase identity nodes.
- Thus both representations rank exactly the same gold identity-pair candidate universe; aliases cannot appear as duplicate decisions.

## Inference families
- Local family: Jaccard, Adamic–Adar, Resource Allocation.
- Spectral family: rank-64 truncated SVD adjacency reconstruction, fixed random seed 20260821.
- Jaccard/AA/RA count as one independent family for the NCS generality gate; SVD is the second.
- Learned KG-native models are a later extension and do not alter the deterministic primary gate.

## Tie robustness and uncertainty
- 200 deterministic tie-break replicates per method/k using the same identity-specific hash ordering in R0 and R1.
- 200 candidate bootstrap replicates per method/k; report 2.5%, median and 97.5% RIDI quantiles.
- Pre-specified k: 10, 50, 100, 500, 1000 where feasible.

## Negative control
- Bijective SHA-256 relabeling of all R0 surface nodes.
- Gate requires exact RIDI=0 and maximum absolute score difference <1e-12 for Jaccard, AA and RA.

## Cross-domain success gate
A deterministic cross-domain replication passes only if:
1. the bijective negative control is exact;
2. at least one local method has bootstrap RIDI lower quantile >0 at a pre-specified k;
3. SVD has bootstrap RIDI lower quantile >0 at a pre-specified k;
4. the same findings survive tie-robust lower quantiles >0 where boundary ties are material.

Performance changes are reported rather than filtered. A strong NCS dissociation is claimed only if aggregate held-out quality remains comparatively stable while decision identity turnover is material.

Locked SHA-256 (local source): e5405164ec9de6cb7b39344bdca770ba89604df3188ae6573272ce6b19979839
