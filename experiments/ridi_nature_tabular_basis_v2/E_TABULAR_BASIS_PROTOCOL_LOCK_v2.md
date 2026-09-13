# E-Tabular basis — prospective mechanistic follow-up (LOCK v2)

**Lock date:** 2026-08-23, Asia/Riyadh  
**Status:** frozen before any outcome from this v2 orthogonal-basis experiment is computed.  
**Lineage:** this is a new mechanistic follow-up to the already executed `NATURE_CROSSMODAL_PROTOCOL_LOCK_v1`. It does **not** replace, relabel, or rescue the v1 tabular analysis. The v1 outputs and its numerical-control failure remain archived and reportable. No v1 result is used to choose a v2 model, cutoff, threshold, seed or dimensionality.

## Question
Can an exactly information-preserving change of feature basis alter the identities of top-ranked decisions while conventional predictive performance remains similar, and does that effect depend on whether the learning family is equivariant to the basis change?

The experiment holds source rows, labels, train/test split, candidate population, fitting rule and evaluation rule fixed. The intervention changes only the operational coordinate representation supplied to the learner.

## Data and frozen universe
UCI Adult/Census Income, fixed public train/test partition, acquired byte-stably from `jbrownlee/Datasets` commit `d20fcb6402ae34e653d4513b00f39257bb37ed7f`:

- `adult-train.csv`, Git blob SHA-1 `e3cf049c46ef54b8b69dd9b2fa4d8d01376cc8e4`
- `adult-test.csv`, Git blob SHA-1 `d23e54711c5c744fbf5572d5bdd379e1b54e703c`

`?` remains an observed categorical level; no row is removed. Official train rows define fitting; every official test row defines the decision universe `C` and receives identity `adult-test:<line>` before scoring.

## Shared base preprocessing
Training-data-only preprocessing: `StandardScaler` for the six numeric predictors and `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` for the eight categorical predictors. This defines a finite-dimensional base matrix `X0`.

## Representation intervention
**R0:** `R0(X)=X0`.

**R1:** construct a deterministic square orthogonal matrix `Q` from NumPy RNG seed **3979731779**, QR decomposition, deterministic QR sign fixing and positive determinant; then `R1(X)=X0 Q`.

R1 is invertible and contains exactly the same row information as R0. Before fitting, the run aborts unless:

1. `max_abs(Q.T @ Q-I) < 1e-10`;
2. `max_abs((X0 Q)Q.T-X0) < 1e-9` on the first 256 test rows;
3. row identities and labels are identical across arms.

## Frozen inference families
**F1, equivariance control:** `LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=5000, tol=1e-10, fit_intercept=True)`. The L2 objective is orthogonally invariant, so near-zero decision divergence is predicted before execution.

**F2, representation-sensitive family:** `HistGradientBoostingClassifier(loss='log_loss', learning_rate=0.05, max_iter=300, max_leaf_nodes=31, max_depth=None, min_samples_leaf=20, l2_regularization=1.0, early_stopping=False, random_state=20260823)`. Axis-aligned partitions are not rotation-equivariant.

No hyperparameter tuning is allowed after this lock.

## Outcomes
For test probability of `income >50K`, report AUROC, average precision, Brier score, full-universe Spearman, and RIDI at `k={100,500,1000}`. Ties are broken identically by SHA-256 of `RIDI-NATURE-TABULAR-BASIS-v2|tie|<row_id>`.

`RIDI@k = 1 - |T_k(R0)∩T_k(R1)| / |T_k(R0)∪T_k(R1)|`.

## Locked interpretation
For F2:
- **performance-stable decision instability:** `|ΔAUROC| <= 0.005` and `RIDI@100 >= 0.10`;
- **representation sensitivity with performance shift:** `RIDI@100 >= 0.10` and `|ΔAUROC| > 0.005`;
- **weak decision sensitivity:** `0 < RIDI@100 < 0.10`;
- **decision invariant:** `RIDI@100 = 0`.

For F1, the mechanistic control is near-invariant only if `RIDI@100=0` and maximum absolute score difference is `<1e-6`; otherwise implementation review is required before v2 interpretation.

All outcomes, including adverse or null outcomes, remain archived. The v2 experiment is a separately timed mechanistic follow-up and cannot be described as prospectively locked before cross-modal v1 existed. Raw row scores, software versions, source hashes, transform checks and output SHA-256 manifests are mandatory.