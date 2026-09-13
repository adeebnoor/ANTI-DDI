# Leakage-free contemporary GraphBAN challenge — TargetDecagon DTI

Mapping edge coverage: **99.7%**. Held-out positives in message passing: **no**.

| Metric | Conventional | Structure-neutralized | Difference |
|---|---:|---:|---:|
| AUROC | 0.997 ± 0.000 | 0.942 ± 0.006 | +0.056 conventional-minus-neutralized |
| AUPRC | 0.998 | 0.956 | +0.042 |

Mean matching coverage: **0.588** across seeds [0, 1, 2].

This is the primary S6 contemporary-model challenge defined before outcome inspection. The public GraphBAN transductive test-graph construction is not used here because held-out positive edges must not enter message passing.
