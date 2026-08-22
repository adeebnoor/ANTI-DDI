# Nature GraphSAGE attribution — execution addendum v1

**Date:** 2026-08-23 (Asia/Riyadh)  
**Status:** locked before any of the 16 new-seed outcomes are computed.  
**Parent lock:** `NATURE_GRAPHSAGE_ATTRIBUTION_LOCK_v1.md`.

## Purpose of this addendum
The prospectively frozen scientific design is unchanged. This addendum fixes execution details needed to reproduce the original RTX chemical–disease cache and to construct seed ensembles without post-outcome discretion.

## Rebuilding the frozen cache
The compact RTX cache files were not redistributed in the manuscript package. They are rebuilt from the exact official RTX-KG2 2.7.3pre Git-LFS objects used previously. Execution must verify before parsing:

- `nodes.tar.xz` SHA-256 = `35bb9deaeeeaef029f18a5a21c4dd3af0c55712f20f4bc985443ce1efe2ee231`
- `edges.tar.xz` SHA-256 = `26b8b95035519412566c0bd74d0bbd9f4180636a4ab7ea3327938b1c60cf7ed3`

The original outcome-blind freeze algorithm and constants are reused. Because gzip headers include non-scientific timestamp metadata, a fresh byte-for-byte gzip SHA is not required. Instead, before any model run, the rebuild must reproduce all of the following frozen census facts exactly: 10,238,961 node rows; 54,041,267 edge rows; 564,240 non-negated `same_as` rows; 213,924 non-singleton same-as components; 915,794 unique chemical–disease raw binary edges; 69,510 primary-representation-exposed chemical–disease edges; 200 frozen queries; and SHA-256 `1291fa56e9074cbf41589b3e74f4fbc40687419ed44a7bb9800e9340e83e400e` for the deterministic `chem_disease_query_structure.json`. Any mismatch aborts before training.

Fresh gzip outputs use `mtime=0` only to make the newly generated execution artifact byte-stable. This does not alter decompressed rows or any scientific endpoint.

## Percentile-rank definition
For each query, candidate decision groups are ordered by descending score. Exact score ties use the already locked SHA-256 identity tie-break. With `n` decision groups and zero-based rank `r`, the stored percentile rank is

`p = 1 - r/(n-1)` for `n>1`, and `p=1` for `n=1`.

Thus 1.0 is the highest-ranked candidate and 0.0 the lowest. Ensemble scores are arithmetic means of these within-query percentile ranks. No score calibration across queries is performed.

## Parallel execution
The 16 locked seeds may be executed in computational shards. Sharding is solely an execution optimization. Every shard uses the same rebuilt cache, model, optimizer, split, feature construction and decision universe. The final aggregator requires all 16 seeds and identical decision-universe fingerprints before calculating the primary endpoint.

## Bootstrap seed
The 10,000-resample primary query bootstrap uses the first 64 bits of SHA-256(`RIDI-NATURE-GRAPHSAGE-ATTRIBUTION-v1|bootstrap`), reduced modulo 2^32. Secondary per-k bootstrap seeds are deterministically offset by k. No bootstrap seed is chosen from results.

## Software environment
The execution environment is frozen before outcomes to Python 3.11 with `torch==2.10.0` (CPU build), `numpy==2.3.5`, `pandas==2.2.3`, `scipy==1.17.0`, and `scikit-learn==1.8.0`. These versions match the validated local rebuild environment used to prepare the runner.

## Reporting
All model runs, convergence summaries, query-level deltas, performance metrics, final verdict and SHA-256 manifests are retained whether the primary endpoint passes or fails. Chemical–gene is not run in this execution because the locked primary endpoint is chemical–disease and the parent protocol explicitly forbids a secondary stratum from rescuing primary failure.
