# Anti-DDI v3.0.0 release notes

## Major release: from negative controls to an explicit evidence-state framework

v3.0.0 aligns the public resource with the Anti-DDI construct evaluated in Paper 5.

### Added
- `data/antiddi_v3_dataset.csv` — 797 records, 44 columns
- `data/antiddi_v3_benchmark.csv` — 538 T1/T2 default benchmark records
- `data/paper5_split_manifest.csv` — frozen 40/174 development-confirmatory split
- `data/clinical_anchor_pairs.csv` — 8 post-confirmatory human clinical anchors
- `data/DATA_DICTIONARY_v3.md`
- `build_v3.py` and `validate_v3.py`
- explicit knowledge-state semantics

### Preserved
- all v2 pair IDs and original 35 columns
- v2 dataset and audit trail
- degree-bias warning
- clinical-use boundary

### Paper 5 results represented in the release
- primary RIDI@20: A 0.746; B 0.308; D 0.243
- prespecified B−D effect: 0.065; 95% CI crossed no improvement
- confirmed-interaction controls: 200/200 retained
- regulatory overrides suppressed: 0/3
- human clinical anchors: 8/8 concordant, supportive/post-confirmatory

The 8/8 anchor result must not be described as an unbiased estimate of population accuracy.
