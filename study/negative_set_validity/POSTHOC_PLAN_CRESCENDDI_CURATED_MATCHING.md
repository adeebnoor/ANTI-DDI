# Post-hoc mechanism analysis — CRESCENDDI curated negatives after structural matching

**Status:** explicitly post hoc. This plan was written only after the confirmatory external results had been frozen in `CONFIRMATORY_RESULTS.md` from GitHub Actions run `32529326608`.

**Execution rule:** run the committed script unchanged against the same checksum-recorded CRESCENDDI source records; archive every output regardless of direction.

## Why this analysis is being added

The locked external study showed two simultaneous facts in CRESCENDDI:

1. clinically curated pair-level negatives remained highly distinguishable by endpoint popularity (mean popularity AUC 0.866); and
2. arbitrary degree-matched non-edges reduced popularity AUC to 0.517.

Those results suggest that **evidential validity** (why an example is accepted as a negative/control) and **structural comparability** (whether positive and negative endpoints are balanced enough to prevent identity/degree shortcuts) are different design properties.

## Fixed post-hoc question

When the *curated CRESCENDDI negative pool itself* is matched to held-out positives on the same unordered training-degree-bin signature, how much curated-negative coverage remains and what happens to graph-only AUC?

## Method fixed before execution

- Re-download and checksum the same CRESCENDDI positive and negative Data Records used by the confirmatory run.
- Collapse DDEs to pair level exactly as in the locked external protocol; exclude every negative pair that also appears in the positive-pair set.
- Reuse the same 20 positive-edge train/test seeds (`100000 + seed`).
- Compute training degrees from the positive training graph.
- Bin nodes by the same quantile-bin rule used in P3.
- Group curated negative pairs by the **unordered pair of endpoint degree bins**.
- For each held-out positive, sample without replacement a curated negative from the identical bin signature. Keep the matched positive together with its selected negative; unmatched positives are dropped rather than replaced from another bin.
- Require at least 100 matched pairs to report a seed.
- Apply the same eight graph-only training-adjacency scores. No model is trained on evaluation labels.

## Outputs

This is a mechanism analysis, not a new confirmatory hypothesis. Report descriptively:

- matched-pair count and coverage per seed;
- popularity AUC before (P4 curated) and after curated-degree matching;
- AUC for the eight graph-only scores on the matched curated subset;
- mean and sample SD across seeds.

No new confirmatory p-value will be used to rescue or redefine the locked external study.

## Interpretation

A drop toward chance for endpoint popularity would support the proposed **dual-validity** distinction: clinical/evidential curation and structural balancing solve different problems and can be combined. Failure to obtain adequate matched coverage, or persistence of high popularity AUC after matching, is equally reportable.
