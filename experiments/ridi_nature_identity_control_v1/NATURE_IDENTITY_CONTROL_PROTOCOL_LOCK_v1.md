# Nature main identity-control extension — prospective protocol lock v1

**Lock date:** 2026-08-23 (Asia/Riyadh)  
**Status:** frozen before identity-control outcomes are computed  
**Parent branch:** `ridi-nature-attribution-v1` at commit `304f977946b49120acbde300e8975284ac9db3b7`  
**New branch:** `ridi-nature-main-v11`  
**Purpose:** test whether representation-associated top-k turnover can be controlled, rather than only measured, by an exact identity-constrained selection rule that maximizes updated score utility under a decision-change budget.

## Scientific question

The parent study shows that aggregate performance and global rank agreement do not certify top-k identity, derives a sufficient zero-turnover margin certificate, and measures representation-associated turnover against invariance and retraining controls. The present extension asks a different question:

> When a representation update changes a finite decision set, how much of that turnover is required to preserve the utility of the updated ranking, and how much can be avoided by an explicit identity constraint?

This extension is a control intervention. It does not determine whether the old or new representation is more correct, and it does not convert score utility into clinical utility.

## Identity-constrained selection

For a query, let `C` be the fixed candidate universe, `A0` the deterministic baseline top-k set under scores `s0`, and `s1` the updated score vector. Scores are converted to deterministic within-query percentile ranks before control so that utility is non-negative and comparable across seeds and model arms.

For exactly `j` changed slots, define

`T*j = argmax_T sum_{i in T} s1(i)`

subject to `|T| = k` and `|T \ A0| = j`.

The candidate set is constructed by retaining the `k-j` members of `A0` with the highest updated scores and adding the `j` highest-updated-score candidates outside `A0`. Deterministic identity ordering resolves ties.

Let `Uj` be the updated-score utility of `T*j`, and let `U*` be the utility of the unconstrained updated top-k set. Define normalized utility regret

`Lj = (U* - Uj) / U*`.

For tolerance `eta`, the minimum necessary turnover is

`j_eta = min {j : Lj <= eta}`.

For an unconstrained update with `Delta > 0` changed slots, define the avoidable-turnover fraction

`ATF_eta = 1 - j_eta / Delta`.

Cases with `Delta = 0` are reported separately and are not assigned an ATF value. The controlled decision set has

`RIDI_control = 2 j_eta / (k + j_eta)`.

## Formal result fixed before experiments

**Identity-constrained selection theorem.** For every integer `j` in `0..k`, the construction above maximizes additive updated-score utility among all size-k sets that change exactly `j` baseline slots. Consequently, the sequence `(j, Uj)` is the exact identity-utility frontier, and `j_eta` is the smallest number of identity changes capable of attaining the declared utility tolerance. The proof is an exchange argument: any feasible set omitting a higher-scored eligible baseline member or outsider can be improved without changing its identity budget.

The frontier is computable in `O(n log n)` time after paired score vectors are stored and requires no retraining or additional model inference.

## Locked tolerances and cutoffs

- Primary utility tolerance: `eta = 0.001` (0.1% normalized updated-score regret).
- Complete tolerance ladder: `{0, 0.0001, 0.001, 0.005, 0.01}`.
- All parent-study cutoffs are retained; no cutoff is selected after outcome inspection.

## Primary confirmatory experiment: RTX-KG2 GraphSAGE

Use the immutable artifacts from GitHub Actions run `32643350756`, generated from parent commit `304f977946b49120acbde300e8975284ac9db3b7`:

- frozen chemical-disease universe artifact `rtx-chem-disease-freeze`;
- all 16 locked seed rank artifacts `seed-shard-s0` through `seed-shard-s7`;
- parent locked ensemble construction with A and B seed halves;
- ensemble size `m = 8`;
- cutoffs `k = {100, 500, 1000}`.

For each query, cutoff and seed half, apply identity-constrained selection to the representation contrast `R0 -> R1`. Compute `Delta`, `j_eta`, unconstrained RIDI, controlled RIDI, normalized utility regret and `ATF_eta`.

The primary endpoint is the query-level mean `ATF_0.001`, first averaged over the A and B representation contrasts and then over the three locked cutoffs. A 95% percentile bootstrap interval uses 10,000 query resamples and a seed derived mechanically from `RIDI-NATURE-IDENTITY-CONTROL-v1|graphsage|bootstrap`.

**Material-control criterion fixed before outcomes:** the lower bound of the 95% bootstrap interval for mean `ATF_0.001` must exceed 0.25. Failure is retained and reported; no alternate tolerance, cutoff, ensemble size or seed subset can rescue the primary criterion.

Same-representation contrasts `R0(A) vs R0(B)` and `R1(A) vs R1(B)` are processed with the identical frontier as stochastic-control analyses. They do not replace the primary representation contrast.

## Cross-domain transport experiment: 20 Newsgroups

Re-run the locked E-TEXT construction without changing document selection, TF-IDF settings, SVD dimension, query set, candidate set, labels, similarity rule, cutoffs or invariance control. Apply the identity-control frontier to each query for `R0 -> R1` at `k = {10, 50, 100}`.

Report, for every tolerance and cutoff:

- mean and 95% query-bootstrap interval for ATF;
- mean unconstrained and controlled RIDI;
- actual changed slots;
- updated-score utility regret;
- label-based nDCG at the matching cutoff and Recall at the matching cutoff for the unconstrained R1 and controlled set, ordered internally by R1 score.

The feature-permutation invariance control must return `Delta = 0`; the control algorithm must not create turnover when scores and identities are invariant.

The text experiment is a transport analysis and cannot rescue failure of the GraphSAGE primary criterion.

## Integrity and reporting rules

- All tolerance values, cutoffs, queries, seed halves and adverse outcomes are retained.
- No tuning of `eta`, representation dimension, model, seeds or candidate universe after outcomes.
- Source artifacts are verified by recorded GitHub artifact digest, parent commit and internal manifests before analysis.
- The analysis writes query-level frontiers, aggregate summaries, exact environment versions, execution provenance and SHA-256 checksums.
- Utility refers only to additive within-query percentile-rank score under the updated arm. It is not labelled clinical utility, patient benefit or correctness.
- The theorem and algorithm may be reported regardless of empirical magnitude; a claim of material avoidable turnover requires the locked primary criterion.

