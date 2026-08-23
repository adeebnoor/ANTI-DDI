from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable, Sequence
import numpy as np
from scipy.stats import spearmanr


def deterministic_topk(ids: Sequence[str], scores: Sequence[float], k: int) -> list[str]:
    ids_arr = np.asarray(ids, dtype=object)
    s = np.asarray(scores, dtype=float)
    if ids_arr.ndim != 1 or s.ndim != 1 or len(ids_arr) != len(s):
        raise ValueError("ids and scores must be aligned one-dimensional arrays")
    if len(set(map(str, ids_arr))) != len(ids_arr):
        raise ValueError("candidate ids must be unique")
    if not (1 <= k <= len(s)):
        raise ValueError("k must be between 1 and the candidate count")
    if not np.isfinite(s).all():
        raise ValueError("scores must be finite")
    order = np.lexsort((ids_arr.astype(str), -s))
    return [str(x) for x in ids_arr[order[:k]]]


def ridi(a: Iterable[str], b: Iterable[str]) -> float:
    A, B = set(map(str, a)), set(map(str, b))
    if not A and not B:
        return 0.0
    union = A | B
    return 1.0 - len(A & B) / len(union)


def changed_slots(a: Iterable[str], b: Iterable[str]) -> int:
    A, B = set(map(str, a)), set(map(str, b))
    if len(A) != len(B):
        raise ValueError("changed_slots assumes equal-size decision sets")
    return len(A - B)


def margin_certificate(scores_r0: Sequence[float], scores_r1: Sequence[float], ids: Sequence[str], k: int) -> dict:
    ids_arr = np.asarray(ids, dtype=object)
    a = np.asarray(scores_r0, dtype=float)
    b = np.asarray(scores_r1, dtype=float)
    if len(a) != len(b) or len(a) != len(ids_arr):
        raise ValueError("ids and both score vectors must have the same length")
    if not (1 <= k < len(a)):
        raise ValueError("margin certificate requires 1 <= k < n")
    order = np.lexsort((ids_arr.astype(str), -a))
    gamma = float(a[order[k-1]] - a[order[k]])
    epsilon = float(np.max(np.abs(b - a)))
    certified = bool(gamma > 2.0 * epsilon)
    return {"gamma_k": gamma, "epsilon": epsilon, "certified_stable": certified}


@dataclass
class CutoffAudit:
    k: int
    ridi: float
    changed_slots: int
    overlap: int
    gamma_k: float | None
    epsilon: float | None
    margin_certified: bool | None


def audit_scores(ids: Sequence[str], scores_r0: Sequence[float], scores_r1: Sequence[float], ks: Sequence[int]) -> dict:
    ids_arr = np.asarray(ids, dtype=object)
    a = np.asarray(scores_r0, dtype=float)
    b = np.asarray(scores_r1, dtype=float)
    if len(ids_arr) != len(a) or len(a) != len(b):
        raise ValueError("ids and score vectors must align")
    rho = float(spearmanr(a, b).statistic)
    rows = []
    for k in ks:
        A = deterministic_topk(ids_arr, a, int(k))
        B = deterministic_topk(ids_arr, b, int(k))
        cert = margin_certificate(a, b, ids_arr, int(k)) if int(k) < len(a) else None
        rows.append(asdict(CutoffAudit(
            k=int(k), ridi=float(ridi(A, B)), changed_slots=int(changed_slots(A, B)),
            overlap=len(set(A) & set(B)),
            gamma_k=None if cert is None else cert["gamma_k"],
            epsilon=None if cert is None else cert["epsilon"],
            margin_certified=None if cert is None else cert["certified_stable"],
        )))
    return {"n_candidates": int(len(ids_arr)), "global_spearman": rho, "cutoffs": rows}
