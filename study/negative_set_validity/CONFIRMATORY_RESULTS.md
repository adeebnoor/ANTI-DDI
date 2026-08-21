# Confirmatory external replication results

**Protocol-lock commit:** `add54b8ce2c312d5245e7f00af27623306e449c4`  
**GitHub Actions run:** `32529326608`  
**Artifact:** `commsmed-external-validity-results` (artifact id `9463385523`)  
**Artifact digest:** `sha256:497bb0066c6a03b3a6ef9cd88ffb2cbdc2d3df8098b725c6454c0e64619cdfc8`

The external outcomes below were generated after the public protocol lock. GoldD2/ATC5 results are not included here because they were observed before the lock and are treated as pilot evidence.

## External inputs

- **BioSNAP ChCh-Miner:** 48,514 unique positive edges over 1,514 drug nodes.
- **CRESCENDDI pair-level aggregation:** 4,971 unique positive drug pairs and 4,062 curated negative drug pairs after excluding every negative pair that appeared in the positive-pair set.
- All downloaded third-party source files were hashed before analysis; see `external_source_manifest.json` in the immutable workflow artifact.

## H1 primary endpoint — negative-set structural inflation

The locked primary criterion required at least 6/8 graph-only models to show positive `AUC(P1 uniform) - AUC(P3 degree-matched)` with Holm-adjusted p<0.05 within the same external benchmark.

**Result: criterion met in both external benchmarks (8/8 models in each).**

### BioSNAP

- P1 AUC range across the eight models: **0.820–0.910**.
- P3 degree-matched AUC range: **0.516–0.798**.
- Inflation range: **0.084–0.362 AUC**.
- All 8/8 model-specific paired sign-flip tests: **Holm-adjusted p=0.000400**.
- Endpoint-popularity AUC: **0.878 → 0.516** after degree matching.

### CRESCENDDI

- P1 AUC range: **0.873–0.948**.
- P3 degree-matched AUC range: **0.517–0.905**.
- Inflation range: **0.040–0.358 AUC**.
- All 8/8 model-specific paired sign-flip tests: **Holm-adjusted p=0.000400**.
- Endpoint-popularity AUC: **0.875 → 0.517** after degree matching.

## H2 descriptive endpoint — popularity share

Popularity accounted for most of the apparent above-chance performance under uniform non-edges but little after structure-aware correction:

| Benchmark | P1 uniform | P3 degree matched | P5 configuration rewire |
|---|---:|---:|---:|
| BioSNAP | 0.921 | 0.053 | 0.030 |
| CRESCENDDI | 0.837 | 0.042 | 0.093 |

The ratio is descriptive by protocol and was not assigned a confirmatory p-value.

## H3 secondary endpoint — model-order instability

After Holm correction of protocol-specific paired model differences:

- BioSNAP: **9/28** model pairs significantly reversed order under P3 and **9/28** under P5.
- CRESCENDDI: **9/28** significantly reversed under P3 and **7/28** under P5.
- Kendall tau between P1 and corrective rankings was 0.357 for BioSNAP (P3 and P5), 0.357 for CRESCENDDI P3 and 0.500 for CRESCENDDI P5. With only eight models these tau p-values are descriptive and were not used as the inferential gate.

## Curated-negative contrast

CRESCENDDI provides a useful contrast because its negative controls were curated rather than generated as arbitrary missing graph edges. Against the locked pair-level curated-negative pool, endpoint-popularity AUC remained **0.866** and its descriptive null-model share was **0.798**. This does **not** invalidate clinical curation. Instead it shows that two validity questions are distinct:

1. **Evidential validity:** is there a defensible reason to treat an example as a negative/control rather than an unknown?
2. **Structural comparability:** can a model separate positive and negative examples using endpoint identity/degree alone?

A negative-control resource can be strong on the first dimension without being degree-balanced on the second. Conversely, degree-matched missing edges improve structural comparability but do not become clinically validated negatives. The ideal evaluation design addresses both dimensions.

## Protocol diagnostics

No P1, P2, P3 or curated CRESCENDDI seed was dropped. BioSNAP P3 retained all 9,702 requested negative examples in every seed; CRESCENDDI P3 retained all 994. The independent P5 corrective retained a mean 9,450.35 BioSNAP examples (range 9,424–9,478) and 959.25 CRESCENDDI examples (range 941–966), with no seed below the prespecified minimum of 100.

## Interpretation boundary

These results evaluate benchmark/evaluation validity. They do not estimate clinical DDI accuracy, do not establish clinical safety for Anti-DDI pairs, and do not revive the withdrawn classifier/RIDI experiment.
