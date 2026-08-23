from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


def _aligned(ids: Sequence[str], scores: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    ids_arr = np.asarray(ids, dtype=object)
    values = np.asarray(scores, dtype=float)
    if ids_arr.ndim != 1 or values.ndim != 1 or len(ids_arr) != len(values):
        raise ValueError("ids and scores must be aligned one-dimensional arrays")
    if len(set(map(str, ids_arr))) != len(ids_arr):
        raise ValueError("candidate ids must be unique")
    if not np.isfinite(values).all():
        raise ValueError("scores must be finite")
    return ids_arr, values


def stable_order(scores: Sequence[float], ids: Sequence[str]) -> np.ndarray:
    ids_arr, values = _aligned(ids, scores)
    return np.lexsort((ids_arr.astype(str), -values))


def deterministic_percentiles(scores: Sequence[float], ids: Sequence[str]) -> np.ndarray:
    """Return rank utility in [0,1], with 1 assigned to the top candidate."""
    ids_arr, values = _aligned(ids, scores)
    n = len(values)
    order = stable_order(values, ids_arr)
    out = np.empty(n, dtype=float)
    if n == 1:
        out[order] = 1.0
    else:
        out[order] = 1.0 - np.arange(n, dtype=float) / float(n - 1)
    return out


def ridi_from_changed_slots(k: int, changed: int) -> float:
    if not (0 <= changed <= k):
        raise ValueError("changed must be between zero and k")
    return float(2.0 * changed / (k + changed))


@dataclass(frozen=True)
class Frontier:
    k: int
    delta_unconstrained: int
    utility_star: float
    j: np.ndarray
    utility: np.ndarray
    regret: np.ndarray
    baseline_order: np.ndarray
    outsider_order: np.ndarray


def identity_utility_frontier(
    ids: Sequence[str],
    scores_r0: Sequence[float],
    scores_r1: Sequence[float],
    k: int,
) -> Frontier:
    ids_arr, raw0 = _aligned(ids, scores_r0)
    _, raw1 = _aligned(ids, scores_r1)
    n = len(ids_arr)
    if not (1 <= k <= n // 2):
        raise ValueError("identity-control frontier requires 1 <= k <= n/2")

    utility0 = deterministic_percentiles(raw0, ids_arr)
    utility1 = deterministic_percentiles(raw1, ids_arr)
    base_order = stable_order(utility0, ids_arr)
    update_order = stable_order(utility1, ids_arr)
    baseline = base_order[:k]
    updated = update_order[:k]
    baseline_mask = np.zeros(n, dtype=bool)
    baseline_mask[baseline] = True
    delta = int(np.count_nonzero(~baseline_mask[updated]))

    inside = baseline[stable_order(utility1[baseline], ids_arr[baseline])]
    outside_idx = np.flatnonzero(~baseline_mask)
    outside = outside_idx[stable_order(utility1[outside_idx], ids_arr[outside_idx])]

    inside_prefix = np.concatenate(([0.0], np.cumsum(utility1[inside], dtype=float)))
    outside_prefix = np.concatenate(([0.0], np.cumsum(utility1[outside], dtype=float)))
    max_j = min(k, len(outside))
    js = np.arange(max_j + 1, dtype=int)
    utilities = np.asarray(
        [inside_prefix[k - int(j)] + outside_prefix[int(j)] for j in js],
        dtype=float,
    )
    utility_star = float(np.max(utilities))
    if utility_star <= 0:
        raise RuntimeError("updated percentile utility must be positive")
    regret = np.maximum(0.0, (utility_star - utilities) / utility_star)
    return Frontier(
        k=int(k),
        delta_unconstrained=delta,
        utility_star=utility_star,
        j=js,
        utility=utilities,
        regret=regret,
        baseline_order=inside,
        outsider_order=outside,
    )


def select_identity_control(frontier: Frontier, eta: float) -> dict:
    if eta < 0:
        raise ValueError("eta must be non-negative")
    eligible = np.flatnonzero(frontier.regret <= float(eta) + 1e-15)
    if not len(eligible):
        raise RuntimeError("no feasible frontier point meets eta")
    pos = int(eligible[0])
    changed = int(frontier.j[pos])
    k = frontier.k
    selected = np.concatenate(
        (frontier.baseline_order[: k - changed], frontier.outsider_order[:changed])
    )
    delta = frontier.delta_unconstrained
    atf = None if delta == 0 else float(1.0 - changed / delta)
    return {
        "eta": float(eta),
        "j_eta": changed,
        "delta_unconstrained": delta,
        "avoidable_turnover_fraction": atf,
        "utility": float(frontier.utility[pos]),
        "utility_star": float(frontier.utility_star),
        "utility_regret": float(frontier.regret[pos]),
        "ridi_unconstrained": ridi_from_changed_slots(k, delta),
        "ridi_controlled": ridi_from_changed_slots(k, changed),
        "selected_indices": selected,
    }


def binary_ndcg(relevance: Sequence[int], ordered_indices: Iterable[int], k: int) -> float:
    rel = np.asarray(relevance, dtype=int)
    order = np.asarray(list(ordered_indices), dtype=int)[:k]
    gains = rel[order] / np.log2(np.arange(2, len(order) + 2))
    ideal_n = min(int(rel.sum()), k)
    if ideal_n == 0:
        return float("nan")
    ideal = float((np.ones(ideal_n) / np.log2(np.arange(2, ideal_n + 2))).sum())
    return float(gains.sum() / ideal)


def binary_recall(relevance: Sequence[int], selected_indices: Iterable[int]) -> float:
    rel = np.asarray(relevance, dtype=int)
    denom = int(rel.sum())
    if denom == 0:
        return float("nan")
    idx = np.asarray(list(selected_indices), dtype=int)
    return float(rel[idx].sum() / denom)


def bootstrap_mean_ci(values: Sequence[float], seed: int, n_boot: int = 10_000) -> list[float]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return [float("nan"), float("nan"), float("nan")]
    rng = np.random.default_rng(int(seed))
    means = np.empty(n_boot, dtype=float)
    for start in range(0, n_boot, 1000):
        end = min(n_boot, start + 1000)
        draw = rng.integers(0, len(x), size=(end - start, len(x)))
        means[start:end] = x[draw].mean(axis=1)
    return [
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.5)),
        float(np.quantile(means, 0.975)),
    ]

