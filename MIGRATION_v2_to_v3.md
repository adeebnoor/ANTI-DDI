# Migration from Anti-DDI v2 to v3

## Do not delete v2

Keep `data/antiddi_v2_dataset.csv` unchanged. v3 is additive and preserves the v2 audit trail.

## What is backward compatible

All 797 pair IDs and all 35 v2 columns remain unchanged in `antiddi_v3_dataset.csv`.

## What is new

v3 appends semantic fields that distinguish:
- supported Anti-DDI evidence,
- limited candidates,
- unresolved records,
- structural controls,
- positive-concern exclusions.

It also publishes the frozen Paper 5 split and the post-confirmatory human clinical anchors.

## Code migration

Old:
```python
negatives = pd.read_csv("data/antiddi_v2_dataset.csv")
```

Recommended v3:
```python
negatives = pd.read_csv("data/antiddi_v3_benchmark.csv")
```

If you need the complete audit trail:
```python
all_states = pd.read_csv("data/antiddi_v3_dataset.csv")
```

## Semantics migration

Do not call all 797 rows "negative drug pairs". In v3, 538 are default supported Anti-DDI benchmark records; the other states are explicitly retained as limited, unresolved, structural, or excluded records.
