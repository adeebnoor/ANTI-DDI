# Validation notice — 20 August 2026

## Status

The four-arm text-classifier/RIDI experiment that was documented in Anti-DDI v3.0.0 is **withdrawn as validation evidence**. It must not be used to support efficacy, safety-preservation, or downstream decision-stability claims for Anti-DDI.

The dataset audit, evidence tiers, clinical/label exclusions, structural analyses, and targeted human clinical-anchor table are separate from that experiment and are not changed by this notice.

## Why the experiment was withdrawn

A post-analysis adversarial audit identified a design error that made the Anti-DDI evidence payload act as a surrogate class label. In the frozen training construction, positive examples were represented only in arms without the Anti-DDI payload, whereas negative examples were represented in arms both with and without the payload. Consequently, the marker `ANTIDDI=YES` and associated evidence fields were perfectly associated with the negative class whenever present.

A direct payload-only stress test confirmed the effect. For an artificial pair (`DRUGX + DRUGY`) with no pair-specific pharmacology, the primary TF-IDF/logistic-regression model changed from P(interaction)=0.8090 without the payload to 0.00469 with the payload. The frozen Complement Naive Bayes model changed from 0.99991 to approximately zero.

A second design error affected the reported safety comparison: the Anti-DDI intervention was not actually applied to the held-out confirmed-interaction safety controls in the original C/D safety arms. When the generic payload was applied adversarially to established interaction controls, their scores could be suppressed to the no-interaction decision region. The prior safety-preservation statement therefore does not provide evidence of pipeline safety.

The replication backend also reached an all-tied score floor in one arm, making a zero RIDI value a property of deterministic tie-breaking rather than evidence of decision stability.

## Corrective action

1. The efficacy and safety claims from the four-arm classifier experiment are withdrawn.
2. `paper5/PAPER5_RIDI_VALIDATION.md` is retained only as a provenance notice identifying the superseded analysis.
3. The repository now foregrounds the resource/framework contribution and a reproducible structural-bias diagnostic that does not use the invalid payload experiment.
4. `data/paper5_split_manifest.csv` is retained only for provenance; it is not a validation asset.
5. Any future downstream-decision experiment must use class-symmetric evidence representations, apply the intervention to safety controls, include explicit leakage stress tests, and treat collapsed/tied score distributions as invalid endpoints rather than as stability.

## Scope of the correction

This notice does **not** establish clinical safety for any Anti-DDI pair. The released T1/T2 set remains a research benchmark candidate set defined by observation opportunity, exclusion rules, and evidence provenance. The eight human clinical anchors are a targeted supportive subset, not an unbiased diagnostic-accuracy sample.
