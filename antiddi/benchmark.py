"""Degree-controlled evaluation of drug-drug interaction predictors.

Why this module exists
----------------------
In the release's headline experiment, a predictor with no pharmacological
content at all -- ``score = log1p(degree_a) * log1p(degree_b)``, i.e. how
often each drug appears in the positive knowledge base -- reached
AUC 0.934 (SD 0.007) against randomly drawn unlabelled negatives and
AUC 0.947 (SD 0.004) against this resource's curated negatives. Against
*degree-matched* curated negatives it reached AUC 0.498 (SD 0.004), which is
chance. Almost all of the apparent skill was attributable to degree, or
popularity, structure rather than to interaction prediction.

That result is a property of how negative sets are constructed, and it
applies to the curated set shipped here too, until degree-matching is
imposed. The contribution of this resource is not a set of negatives that
escapes the artefact; it is a set of negatives that ships the degree
metadata and the matched-sampling protocol needed to *measure* it. This
module is that protocol.

Typical use
-----------
>>> import pandas as pd
>>> from antiddi.benchmark import evaluate
>>> negatives = pd.read_csv("data/antiddi_v2_dataset.csv")
>>> positives = pd.read_csv("my_positive_reference.csv")   # drug_a, drug_b
>>> report = evaluate(my_model.score_pair, positives, negatives)
>>> print(report.to_frame())

Read the three AUC rows together, never singly. A large gap between the
``curated`` and ``degree_matched`` rows is the diagnostic: it quantifies how
much of a model's reported performance was carried by drug popularity.

Nothing in this module makes, or supports, a clinical recommendation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from .evidence import USABLE_TIERS

__all__ = [
    "evaluate",
    "degree_matched_sample",
    "compute_degrees",
    "sample_random_negatives",
    "auc_mann_whitney",
    "ArmResult",
    "EvaluationReport",
    "DEFAULT_DEGREE_BINS",
]

#: Default degree bin edges. Right-open bins on raw degree, chosen so that the
#: heavy right tail of a scale-free interaction graph is not collapsed into one
#: bucket. Passed to :func:`degree_matched_sample` as ``bins``.
DEFAULT_DEGREE_BINS: tuple[float, ...] = (
    0,
    1,
    2,
    3,
    5,
    8,
    12,
    20,
    35,
    60,
    100,
    175,
    300,
    550,
    1000,
    math.inf,
)

PairList = Sequence[tuple[str, str]]


# --------------------------------------------------------------------------
# small primitives
# --------------------------------------------------------------------------


def _norm_name(name: object) -> str:
    """Canonical drug key: stripped, case-folded. Mirrors the audit's fix for
    the 81 stray-whitespace and 37 inconsistent-case rows in the v1 file."""
    return str(name).strip().lower()


def _as_pairs(obj: pd.DataFrame | Iterable, col_a: str = "drug_a", col_b: str = "drug_b") -> list[tuple[str, str]]:
    """Coerce a DataFrame or an iterable of 2-tuples to a list of unordered
    pair keys, deduplicated, with each pair stored as a sorted tuple."""
    if isinstance(obj, pd.DataFrame):
        missing = [c for c in (col_a, col_b) if c not in obj.columns]
        if missing:
            raise KeyError(f"DataFrame is missing required column(s): {missing}")
        rows = zip(obj[col_a], obj[col_b])
    else:
        rows = obj
    seen: dict[tuple[str, str], None] = {}
    for item in rows:
        a, b = item
        ka, kb = _norm_name(a), _norm_name(b)
        if not ka or not kb or ka == kb:
            continue
        seen[tuple(sorted((ka, kb)))] = None  # type: ignore[index]
    return list(seen.keys())


def auc_mann_whitney(pos_scores: Sequence[float], neg_scores: Sequence[float]) -> float:
    """AUC as the Mann-Whitney U statistic, with ties credited one half.

    Equals the probability that a randomly chosen positive outscores a
    randomly chosen negative. Returns ``nan`` if either arm is empty.
    """
    p = np.asarray(pos_scores, dtype=float)
    n = np.asarray(neg_scores, dtype=float)
    p = p[np.isfinite(p)]
    n = n[np.isfinite(n)]
    if p.size == 0 or n.size == 0:
        return float("nan")
    combined = np.concatenate([p, n])
    ranks = pd.Series(combined).rank(method="average").to_numpy()
    r_pos = ranks[: p.size].sum()
    u = r_pos - p.size * (p.size + 1) / 2.0
    return float(u / (p.size * n.size))


def compute_degrees(positives: pd.DataFrame | PairList) -> dict[str, int]:
    """Degree of each drug in the *positive* reference graph.

    Degree is counted on positives only. This is deliberate: the artefact
    being controlled is that a drug appearing in many known interactions is
    more likely to appear in any given positive pair, irrespective of the
    partner. Counting degree on the negative set instead would not control
    it.

    Returns
    -------
    dict
        Mapping of canonicalised drug name to degree. Drugs absent from the
        positive set are simply absent from the mapping; callers should treat
        a missing key as degree 0.
    """
    pairs = _as_pairs(positives)
    deg: dict[str, int] = {}
    for a, b in pairs:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    return deg


def _pair_degree_bin(
    pair: tuple[str, str], degrees: Mapping[str, int], bins: Sequence[float]
) -> tuple[int, int]:
    """Bin index for each drug in a pair, returned sorted so that the bin
    signature of a pair is order-invariant."""
    edges = np.asarray(bins, dtype=float)
    out = []
    for drug in pair:
        d = float(degrees.get(drug, 0))
        idx = int(np.searchsorted(edges, d, side="right") - 1)
        idx = max(0, min(idx, len(edges) - 2))
        out.append(idx)
    return tuple(sorted(out))  # type: ignore[return-value]


# --------------------------------------------------------------------------
# sampling
# --------------------------------------------------------------------------


def degree_matched_sample(
    positives: pd.DataFrame | PairList,
    negatives: pd.DataFrame | PairList,
    bins: Sequence[float] = DEFAULT_DEGREE_BINS,
    degrees: Mapping[str, int] | None = None,
    random_state: int | None = None,
    replace: bool = False,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Down-sample positives so that the two arms share a degree profile.

    Each pair is assigned an order-invariant signature: the pair of degree
    bins its two drugs fall into. Positives are then retained only where a
    negative with the same signature is available, one negative consumed per
    positive retained. What survives is two arms that a degree-only
    predictor cannot separate -- so any AUC above chance on the matched arms
    is attributable to pair-specific information.

    In the release's 20-replicate experiment this retained roughly 331 of
    538 positives per replicate, and a mean of 38.4% of positives (SD 2.1%,
    range 34.2-42.6% across replicates) had no degree-matched negative
    available at all. That shortfall is itself a measurement: it is how far
    apart the degree distributions of the two classes are.

    Parameters
    ----------
    positives, negatives : DataFrame or iterable of (drug_a, drug_b)
        DataFrames must carry ``drug_a`` and ``drug_b`` columns.
    bins : sequence of float, default :data:`DEFAULT_DEGREE_BINS`
        Right-open bin edges on raw degree. Coarser bins retain more
        positives but match less tightly; report the bins you used.
    degrees : mapping, optional
        Precomputed drug degrees. Defaults to
        ``compute_degrees(positives)``.
    random_state : int, optional
        Seed for the negative draw within each bin signature.
    replace : bool, default False
        If True, a negative may be matched to more than one positive. False
        is the conservative default and the setting used for the published
        figures.

    Returns
    -------
    (matched_positives, matched_negatives) : tuple of two lists
        Equal-length lists of pair tuples, aligned by degree signature but
        not element-wise paired.
    """
    pos = _as_pairs(positives)
    neg = _as_pairs(negatives)
    deg = dict(degrees) if degrees is not None else compute_degrees(pos)
    rng = np.random.default_rng(random_state)

    pools: dict[tuple[int, int], list[tuple[str, str]]] = {}
    for pair in neg:
        pools.setdefault(_pair_degree_bin(pair, deg, bins), []).append(pair)
    for sig in pools:
        order = rng.permutation(len(pools[sig]))
        pools[sig] = [pools[sig][i] for i in order]

    used: dict[tuple[int, int], int] = {}
    keep_pos: list[tuple[str, str]] = []
    keep_neg: list[tuple[str, str]] = []
    for pair in rng.permutation(len(pos)):
        p = pos[int(pair)]
        sig = _pair_degree_bin(p, deg, bins)
        pool = pools.get(sig)
        if not pool:
            continue
        if replace:
            keep_pos.append(p)
            keep_neg.append(pool[int(rng.integers(len(pool)))])
        else:
            i = used.get(sig, 0)
            if i >= len(pool):
                continue
            used[sig] = i + 1
            keep_pos.append(p)
            keep_neg.append(pool[i])
    return keep_pos, keep_neg


def sample_random_negatives(
    positives: pd.DataFrame | PairList,
    n: int,
    exclude: Iterable[tuple[str, str]] = (),
    vocabulary: Sequence[str] | None = None,
    random_state: int | None = None,
    max_tries_factor: int = 200,
) -> list[tuple[str, str]]:
    """Draw unlabelled pairs uniformly at random, the conventional baseline.

    This is the negative-set construction that most published DDI models
    use: sample non-edges of the positive graph and label them negative.
    It is reproduced here so that a user can see, for their own model, the
    size of the gap between this arm and the degree-matched arm.

    Parameters
    ----------
    positives : DataFrame or iterable of pairs
        Positive reference set; supplies the sampling vocabulary and the
        pairs to avoid.
    n : int
        Number of negatives to draw.
    exclude : iterable of pairs, optional
        Additional pairs to avoid, e.g. the curated negatives, so the arms
        stay disjoint.
    vocabulary : sequence of str, optional
        Drug names to sample from. Defaults to the drugs appearing in
        ``positives``.
    random_state : int, optional
        Seed.
    max_tries_factor : int, default 200
        Rejection-sampling budget, as a multiple of ``n``. If the budget is
        exhausted, fewer than ``n`` pairs are returned rather than looping.
    """
    pos = set(_as_pairs(positives))
    blocked = pos | set(_as_pairs(list(exclude))) if exclude else set(pos)
    vocab = list(dict.fromkeys(vocabulary)) if vocabulary is not None else sorted(
        {d for pair in pos for d in pair}
    )
    if len(vocab) < 2:
        raise ValueError("need at least two drugs in the sampling vocabulary")
    vocab = [_norm_name(v) for v in vocab]
    rng = np.random.default_rng(random_state)

    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    budget = max(1, int(n * max_tries_factor))
    for _ in range(budget):
        if len(out) >= n:
            break
        i, j = rng.integers(len(vocab), size=2)
        if i == j:
            continue
        key = tuple(sorted((vocab[int(i)], vocab[int(j)])))
        if key in blocked or key in seen:
            continue
        seen.add(key)  # type: ignore[arg-type]
        out.append(key)  # type: ignore[arg-type]
    return out


# --------------------------------------------------------------------------
# results containers
# --------------------------------------------------------------------------


@dataclass
class ArmResult:
    """Metrics for one negative-set arm of an evaluation.

    Attributes
    ----------
    arm : str
        ``'random'``, ``'curated'`` or ``'degree_matched'``.
    auc : float
        Mann-Whitney AUC of positives against this arm's negatives.
    specificity : float
        Fraction of this arm's negatives scored below the decision
        threshold, i.e. correctly not called an interaction.
    false_positive_rate : float
        ``1 - specificity``.
    sensitivity : float
        Fraction of positives at or above the threshold.
    threshold : float
        The score threshold at which specificity and FPR were measured.
    n_positives, n_negatives : int
        Arm sizes actually used.
    """

    arm: str
    auc: float
    specificity: float
    false_positive_rate: float
    sensitivity: float
    threshold: float
    n_positives: int
    n_negatives: int

    def as_dict(self) -> dict[str, float | str | int]:
        return {
            "arm": self.arm,
            "auc": self.auc,
            "specificity": self.specificity,
            "false_positive_rate": self.false_positive_rate,
            "sensitivity": self.sensitivity,
            "threshold": self.threshold,
            "n_positives": self.n_positives,
            "n_negatives": self.n_negatives,
        }


@dataclass
class EvaluationReport:
    """Result of :func:`evaluate`: one :class:`ArmResult` per negative arm.

    ``degree_attributable_auc`` is the headline diagnostic: the drop in AUC
    from the curated arm to the degree-matched arm. In the release's own
    experiment, using a popularity-only heuristic, that drop was
    0.947 -> 0.498.
    """

    arms: dict[str, ArmResult]
    target_sensitivity: float
    bins: tuple[float, ...]
    replicates: int
    notes: list[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> ArmResult:
        return self.arms[key]

    @property
    def degree_attributable_auc(self) -> float:
        """``auc(curated) - auc(degree_matched)``; ``nan`` if either is absent."""
        try:
            return self.arms["curated"].auc - self.arms["degree_matched"].auc
        except KeyError:
            return float("nan")

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([a.as_dict() for a in self.arms.values()]).set_index("arm")

    def __str__(self) -> str:  # pragma: no cover - presentational
        lines = [self.to_frame().to_string(float_format=lambda v: f"{v:.4f}")]
        lines.append(f"degree-attributable AUC (curated - matched): {self.degree_attributable_auc:.4f}")
        lines.extend(self.notes)
        return "\n".join(lines)


# --------------------------------------------------------------------------
# the entry point
# --------------------------------------------------------------------------


def evaluate(
    predict_fn: Callable[[str, str], float],
    positives: pd.DataFrame | PairList,
    negatives: pd.DataFrame | str = "T1+T2",
    matching: str | None = "degree",
    bins: Sequence[float] = DEFAULT_DEGREE_BINS,
    target_sensitivity: float = 0.95,
    threshold: float | None = None,
    replicates: int = 20,
    random_state: int | None = 0,
    dataset_path: str | None = None,
) -> EvaluationReport:
    """Score a predictor against three negative sets and report the gap.

    The point of the function is the comparison, not any single number.
    A predictor is evaluated three times against the same positives:

    ``random``
        unlabelled pairs drawn uniformly from the positive vocabulary --
        the conventional baseline;
    ``curated``
        this resource's negatives at the requested tier;
    ``degree_matched``
        the same curated negatives after :func:`degree_matched_sample`
        equalises the degree profile of the two arms.

    Read the three AUCs together. The ``curated`` minus ``degree_matched``
    difference (:attr:`EvaluationReport.degree_attributable_auc`) is the
    portion of apparent performance attributable to drug popularity rather
    than to pair-specific pharmacology.

    Parameters
    ----------
    predict_fn : callable
        ``predict_fn(drug_a, drug_b) -> float``, a higher score meaning
        "more likely to interact". Called with canonicalised (stripped,
        lower-cased) names. It need not be symmetric, but an asymmetric
        function will be called with an arbitrary argument order.
    positives : DataFrame or iterable of pairs
        Known-interacting reference pairs, with ``drug_a`` / ``drug_b``
        columns if a DataFrame. Required: this resource ships negatives
        only, and the degree structure being controlled is a property of
        the positive set.
    negatives : DataFrame or str, default ``'T1+T2'``
        Either a DataFrame of negatives (``drug_a``, ``drug_b``, and
        ``evidence_tier`` if filtering is wanted), or a tier selector
        string resolved against ``dataset_path``. Recognised selectors:
        ``'T1+T2'`` (the 538-pair usable benchmark set, the default and the
        recommended choice), ``'T1'``, ``'T2'``, ``'all'`` (every non-excluded
        tier), or a ``'+'``-joined list of literal tier names. Pairs flagged
        ``excluded_clinical`` are dropped by every selector, including
        ``'all'``; the 30 clinically excluded pairs are shipped for
        auditability and are never part of a usable negative set.
    matching : {'degree', None}, default ``'degree'``
        ``'degree'`` computes the third arm. ``None`` skips it -- which
        forgoes the only arm that controls the artefact, and should be done
        only when a matched arm is genuinely unavailable.
    bins : sequence of float, default :data:`DEFAULT_DEGREE_BINS`
        Degree bin edges for matching.
    target_sensitivity : float, default 0.95
        Specificity and FPR require a decision threshold. Unless
        ``threshold`` is given, the threshold is set to the score quantile
        of the positives that achieves this sensitivity, so that the arms
        are compared at equal sensitivity. Report the value you used.
    threshold : float, optional
        Fixed decision threshold; overrides ``target_sensitivity``.
    replicates : int, default 20
        Number of random draws for the ``random`` and ``degree_matched``
        arms; reported metrics are means over replicates. The ``curated``
        arm is deterministic and computed once.
    random_state : int, optional
        Base seed; replicate *i* uses ``random_state + i``.
    dataset_path : str, optional
        Path to ``antiddi_v2_dataset.csv``, required when ``negatives`` is a
        selector string. Defaults to ``data/antiddi_v2_dataset.csv``
        relative to the working directory.

    Returns
    -------
    EvaluationReport

    Raises
    ------
    ValueError
        If ``matching`` is not ``'degree'`` or ``None``, if a tier selector
        is unrecognised, or if either arm ends up empty.

    Examples
    --------
    A popularity-only heuristic, which is the release's own headline
    experiment::

        import numpy as np
        from antiddi.benchmark import evaluate, compute_degrees

        deg = compute_degrees(positives)
        def popularity(a, b):
            return np.log1p(deg.get(a, 0)) * np.log1p(deg.get(b, 0))

        report = evaluate(popularity, positives, negatives_df)
        report["random"].auc           # ~0.93
        report["curated"].auc          # ~0.94
        report["degree_matched"].auc   # ~0.50, i.e. chance
    """
    if matching not in ("degree", None):
        raise ValueError("matching must be 'degree' or None")

    neg_df = _resolve_negatives(negatives, dataset_path)
    neg_pairs = _as_pairs(neg_df)
    pos_pairs = _as_pairs(positives)
    if not pos_pairs:
        raise ValueError("positives is empty")
    if not neg_pairs:
        raise ValueError("negatives resolved to an empty set")

    overlap = set(pos_pairs) & set(neg_pairs)
    notes: list[str] = []
    if overlap:
        notes.append(
            f"note: {len(overlap)} pair(s) appear in both arms and were dropped from the negatives"
        )
        neg_pairs = [p for p in neg_pairs if p not in overlap]

    degrees = compute_degrees(pos_pairs)
    score = _memo_scorer(predict_fn)

    pos_scores = np.array([score(a, b) for a, b in pos_pairs], dtype=float)
    thr = (
        float(threshold)
        if threshold is not None
        else float(np.nanquantile(pos_scores, 1.0 - target_sensitivity))
    )
    sens_all = float(np.mean(pos_scores >= thr))

    arms: dict[str, ArmResult] = {}

    # --- arm 1: random unlabelled negatives (mean over replicates) --------
    aucs, specs, sizes = [], [], []
    for i in range(max(1, replicates)):
        seed = None if random_state is None else random_state + i
        rnd = sample_random_negatives(
            pos_pairs, n=len(neg_pairs), exclude=neg_pairs, random_state=seed
        )
        s = np.array([score(a, b) for a, b in rnd], dtype=float)
        aucs.append(auc_mann_whitney(pos_scores, s))
        specs.append(float(np.mean(s < thr)) if s.size else float("nan"))
        sizes.append(len(rnd))
    arms["random"] = ArmResult(
        "random",
        float(np.nanmean(aucs)),
        float(np.nanmean(specs)),
        1.0 - float(np.nanmean(specs)),
        sens_all,
        thr,
        len(pos_pairs),
        int(round(float(np.mean(sizes)))),
    )

    # --- arm 2: curated negatives (deterministic) -------------------------
    cur = np.array([score(a, b) for a, b in neg_pairs], dtype=float)
    cur_spec = float(np.mean(cur < thr))
    arms["curated"] = ArmResult(
        "curated",
        auc_mann_whitney(pos_scores, cur),
        cur_spec,
        1.0 - cur_spec,
        sens_all,
        thr,
        len(pos_pairs),
        len(neg_pairs),
    )

    # --- arm 3: degree-matched curated negatives --------------------------
    if matching == "degree":
        aucs, specs, senss, npos, nneg = [], [], [], [], []
        for i in range(max(1, replicates)):
            seed = None if random_state is None else random_state + i
            mp, mn = degree_matched_sample(
                pos_pairs, neg_pairs, bins=bins, degrees=degrees, random_state=seed
            )
            if not mp or not mn:
                continue
            ps = np.array([score(a, b) for a, b in mp], dtype=float)
            ns = np.array([score(a, b) for a, b in mn], dtype=float)
            aucs.append(auc_mann_whitney(ps, ns))
            specs.append(float(np.mean(ns < thr)))
            senss.append(float(np.mean(ps >= thr)))
            npos.append(len(mp))
            nneg.append(len(mn))
        if not aucs:
            raise ValueError(
                "degree matching retained no pairs; widen `bins` or supply a larger negative set"
            )
        mean_spec = float(np.nanmean(specs))
        arms["degree_matched"] = ArmResult(
            "degree_matched",
            float(np.nanmean(aucs)),
            mean_spec,
            1.0 - mean_spec,
            float(np.nanmean(senss)),
            thr,
            int(round(float(np.mean(npos)))),
            int(round(float(np.mean(nneg)))),
        )
        retained = float(np.mean(npos)) / len(pos_pairs)
        notes.append(
            f"degree matching retained {retained:.1%} of positives "
            f"({int(round(float(np.mean(npos))))} of {len(pos_pairs)}) per replicate"
        )
    else:
        notes.append(
            "matching=None: the degree-matched arm was not computed, so no part of the "
            "reported AUC has been shown to be independent of drug popularity"
        )

    return EvaluationReport(
        arms=arms,
        target_sensitivity=target_sensitivity,
        bins=tuple(bins),
        replicates=int(max(1, replicates)),
        notes=notes,
    )


def _memo_scorer(predict_fn: Callable[[str, str], float]) -> Callable[[str, str], float]:
    cache: dict[tuple[str, str], float] = {}

    def score(a: str, b: str) -> float:
        key = (a, b)
        if key not in cache:
            try:
                cache[key] = float(predict_fn(a, b))
            except Exception:
                cache[key] = float("nan")
        return cache[key]

    return score


def _resolve_negatives(negatives: pd.DataFrame | str, dataset_path: str | None) -> pd.DataFrame:
    """Apply a tier selector, dropping clinically excluded pairs always."""
    if isinstance(negatives, pd.DataFrame):
        df = negatives.copy()
        selector = "all"
    else:
        path = dataset_path or "data/antiddi_v2_dataset.csv"
        df = pd.read_csv(path)
        selector = str(negatives)

    if "excluded_clinical" in df.columns:
        df = df[~df["excluded_clinical"].map(_bool)]

    if selector == "all" or "evidence_tier" not in df.columns:
        return df.reset_index(drop=True)

    aliases = {
        "T1+T2": list(USABLE_TIERS),
        "T1": ["T1_wellpowered"],
        "T2": ["T2_moderate"],
        "T3": ["T3_limited", "T3_trivial_inert"],
        "T4": ["T4_uninformative"],
    }
    if selector in aliases:
        wanted = aliases[selector]
    else:
        wanted = []
        for token in selector.split("+"):
            token = token.strip()
            wanted.extend(aliases.get(token, [token]))
        known = set(df["evidence_tier"].unique())
        unknown = [w for w in wanted if w not in known and w not in set().union(*aliases.values())]
        if unknown:
            raise ValueError(
                f"unrecognised tier selector token(s): {unknown}; "
                f"known tiers: {sorted(known)}"
            )
    out = df[df["evidence_tier"].isin(wanted)].reset_index(drop=True)
    if out.empty:
        raise ValueError(f"tier selector {selector!r} matched no rows")
    return out


def _bool(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"true", "t", "yes", "y", "1"}
    return bool(value)
