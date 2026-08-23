# RIDI Nature cross-modal replication — prospective lock v1

**Lock date:** 2026-08-23 (Asia/Riyadh)  
**Status:** design freeze before any cross-modal outcomes are computed  
**Parent claim:** decision identity is a reproducibility property distinct from aggregate performance.  
**Core intervention:** within each experiment, freeze source evidence `S`, candidate/decision universe `C`, and inference rule/family `F`; change only operational representation `R`. Training randomness `Z` is absent for deterministic pipelines and explicitly controlled when present.

## General endpoints
For fixed decision sets `T_k(R0)` and `T_k(R1)`,

`RIDI@k = 1 - |T_k(R0) ∩ T_k(R1)| / |T_k(R0) ∪ T_k(R1)|`.

Each experiment reports all pre-specified cutoffs, a global agreement metric on the common candidate universe, a task-performance metric when ground truth exists, and an invariance control that should return `RIDI=0` up to declared numerical tolerance.

No experiment is declared successful solely because RIDI is non-zero. The Nature-level pattern of interest is **material decision turnover with substantially preserved aggregate task performance**, together with a passing invariance control. Null/adverse results are retained.

---

## E-TABULAR — lossless categorical representation

### Dataset
UCI Adult / Census Income, DOI `10.24432/C5XW20`, using the official `adult.data` training file and `adult.test` test file. No outcome-driven row selection.

### Frozen source evidence and split
- `S`: the original 14 predictors and binary income label.
- Training/test split: official UCI split.
- Missing marker `?` is retained as an explicit categorical level rather than deleting rows.
- Numeric variables: standardized using training-set mean and SD in both arms.
- Candidate universe `C`: every row in the official test file, preserving original row identity.

### Representation intervention
Categorical identities are preserved without using labels.

- `R0`: ordinary one-hot encoding of each categorical variable, categories ordered lexicographically from the training data; unseen test category maps to an explicit `UNK` level.
- `R1`: deterministic collision-free binary encoding of the same categorical identity. Within each feature, lexicographically ordered training categories receive integer codes `1..n`; `0` is reserved for `UNK`; the integer is represented by `ceil(log2(n+1))` binary indicator columns. Thus category identity is injectively encoded and no target statistic is used.

### Inference families
Primary: `sklearn.linear_model.LogisticRegression`, L2 penalty, `C=1`, `solver='lbfgs'`, `max_iter=5000`, `tol=1e-10`, no class weighting.  
Secondary: `sklearn.ensemble.RandomForestClassifier`, 500 trees, `max_features='sqrt'`, `min_samples_leaf=1`, `random_state=20260823`, `n_jobs=-1`.

### Decisions and endpoints
Rank test rows by predicted probability of income `>50K`.
- k = `{100, 500, 1000}`.
- Report ROC-AUC and average precision in each arm.
- Report absolute AUC/AP difference, Spearman correlation over all test-row scores, and RIDI@k.

### Invariance control
For the primary logistic model, deterministically permute the one-hot feature columns with a SHA-256-derived permutation and refit with the same solver. Because this is a pure coordinate relabeling, the primary control requires max absolute prediction difference `<1e-8` and `RIDI=0` at all k. If numerical tolerance fails, record failure and do not reinterpret the main contrast as causal evidence.

### Interpretation
This experiment tests whether two label-free, injective encodings of the same tabular categories can alter high-priority identities under a fixed learning procedure. Target/frequency encoding is explicitly excluded because it introduces outcome- or sample-frequency information into `R`.

---

## E-TEXT — retrieval under representation compression

### Dataset
Scikit-learn 20 Newsgroups corpus, `subset='all'`, with headers, footers and quoted replies removed by the standard loader. The corpus is used as a non-biomedical text-retrieval benchmark; topic labels are used only for evaluation.

### Frozen query/candidate construction
After loading, compute SHA-256 of normalized document text plus original corpus index. Sort by hash.
- first 5,000 non-empty documents: candidate corpus;
- next 200 non-empty documents: queries.
The construction is deterministic and independent of labels.

### Representation intervention
- `R0`: word TF-IDF with lowercase=True, unigrams+bigrams, `min_df=2`, `max_df=0.95`, maximum 50,000 features; fitted on candidate texts only.
- `R1`: 256-dimensional `TruncatedSVD(random_state=20260823)` of the frozen R0 candidate matrix, followed by L2 normalization; queries are transformed through the same fitted map.

`S` is the same text. `F` is cosine similarity retrieval in both arms. R1 is a deterministic low-rank operational representation of R0; it is not described as information preserving.

### Decisions and endpoints
For each query rank all 5,000 candidates by cosine similarity.
- k = `{10, 50, 100}`.
- Relevance for task performance: same newsgroup label as the query.
- Report mean nDCG@10 and Recall@100 in each arm, their absolute differences, mean query-level Spearman correlation on candidate scores, and mean RIDI@k with 95% query bootstrap intervals (10,000 resamples; seed from lock label).

### Invariance control
Apply a deterministic permutation to R0 TF-IDF feature columns for candidates and queries. Cosine similarities must be identical within `1e-12` and RIDI must equal zero at all k.

### Interpretation
The confirmatory question is not whether dimensionality reduction changes retrieval in general; it is whether task-level retrieval quality can remain close while the identities of retrieved items change materially.

---

## E-VISION — retrieval under feature compression

### Dataset
CIFAR-10 official test set (10,000 images). Labels are used only to evaluate same-class retrieval.

### Frozen query/candidate construction
Compute SHA-256 from official test index. The 200 lowest hashes are queries; the remaining 9,800 images are candidates. No label enters selection.

### Base feature extractor
A fixed ImageNet-pretrained torchvision ResNet-18. Images use the model's documented weight preprocessing identically in both arms. The 512-dimensional penultimate-layer feature vector is extracted once per image and treated as the common upstream evidence representation for this experiment.

### Representation intervention
- `R0`: L2-normalized 512-dimensional frozen ResNet features.
- `R1`: PCA to 128 dimensions fitted on candidate R0 features only, then transform queries/candidates and L2-normalize.

The downstream inference rule `F` is cosine retrieval in both arms.

### Decisions and endpoints
- k = `{10, 50, 100}`.
- Relevance: same CIFAR-10 class.
- Report mean nDCG@10 and Recall@100 in each arm, their absolute differences, mean query-level Spearman correlation, and mean RIDI@k with 95% query bootstrap intervals (10,000 resamples).

### Invariance control
Multiply all R0 features by one fixed 512×512 orthogonal matrix generated from a SHA-256-derived Gaussian matrix followed by QR decomposition. Cosine similarities must be invariant within `1e-10` and RIDI must equal zero at all k.

### Interpretation
This tests a common representation operation—feature compression—without changing source images, preprocessing, feature extractor, candidate set or retrieval rule. Pixel-resize/normalization contrasts are excluded because they change the model input signal itself rather than isolating the representation layer.

---

## E-CERTIFICATE — margin-certificate coverage map

### Purpose
Map where the sufficient stability certificate `γ_k > 2ε` is informative. This is a calibration/visualization of an exact theorem, not an empirical proof of the theorem.

### Simulation
For each candidate size `n ∈ {1000, 5000, 10000}` and cutoff `k ∈ {10, 50, 100, 500, 1000}` when `k<n`, generate 2,000 baseline score vectors from i.i.d. standard normal values using SHA-256-derived seeds. For each baseline, generate bounded perturbations at relative amplitudes `a ∈ {0, 0.01, 0.02, 0.05, 0.10, 0.20}` where `ε = a × SD(s0)` and each coordinate perturbation is sampled uniformly on `[-ε, ε]`.

For every case record:
- baseline margin `γ_k`;
- certificate status `γ_k > 2ε`;
- empirical top-k stability;
- RIDI@k;
- Spearman correlation.

The primary integrity check is zero false certificates. Report certificate coverage and instability prevalence among uncertified cases as functions of `a` and `k/n`. No post-outcome adjustment of the grid is allowed.

---

## E-IMPACT — threshold-crossing consequence, not clinical harm

### Dataset
Use the already frozen DDInter primary ranking outputs only; no new clinical database is introduced.

### Analysis
For each primary DDInter method and each k in `{100,500,1000}`:
- enumerate identities entering and leaving the fixed review budget under R0→R1;
- report rank displacement for switchers;
- identify three deterministic illustrative pairs using the largest absolute rank displacement among representation-sensitive candidates, with ties broken by SHA-256 identity;
- show that the underlying frozen source assertion identity is unchanged while decision status crosses the threshold.

If a severity field is directly present in the frozen DDInter source used by the primary analysis, severity composition of switchers may be reported descriptively. No external severity annotation or patient-harm inference will be added to the confirmatory analysis.

### Interpretation
This converts set turnover into an operational consequence—who is admitted to or excluded from a fixed review budget—without claiming clinical outcome effects not supported by the data.

---

## Cross-modal synthesis
No single pooled p-value will be used across modalities. The main synthesis will report, for each experiment:
1. task-performance change;
2. global score/rank agreement;
3. RIDI at the primary cutoff;
4. invariance-control result;
5. whether training stochasticity exists and, if so, how it was calibrated.

The manuscript may state that representation sensitivity occurs across multiple computational modalities only if at least two non-KG experiments show non-zero RIDI with passing invariance controls. It may state that aggregate performance can mask decision turnover across modalities only for experiments where the aggregate performance difference is substantively small and reported transparently; no universal numerical threshold is defined post hoc.

## Reporting discipline
- All adverse and null outcomes are retained.
- No tuning of representation dimensionality, k, model hyperparameters or query selection after outcome inspection.
- Implementation corrections are permitted only for violations of the written specification, must be documented before replacement outcomes are inspected, and must preserve the locked estimand.
- Raw row/query-level outputs, environment versions and SHA-256 manifests are required for every experiment.
