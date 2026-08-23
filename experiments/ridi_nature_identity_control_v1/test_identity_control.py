from __future__ import annotations

import itertools

import numpy as np

from identity_control import (
    deterministic_percentiles,
    identity_utility_frontier,
    select_identity_control,
)


def brute_force_max(ids, s0, s1, k, j):
    u0 = deterministic_percentiles(s0, ids)
    u1 = deterministic_percentiles(s1, ids)
    base = set(np.lexsort((np.asarray(ids), -u0))[:k])
    best = -1.0
    for combo in itertools.combinations(range(len(ids)), k):
        chosen = set(combo)
        if len(chosen - base) == j:
            best = max(best, float(u1[list(combo)].sum()))
    return best


def run():
    rng = np.random.default_rng(20260823)
    cases = 0
    for n in range(4, 10):
        ids = np.asarray([f"c{i}" for i in range(n)])
        for k in range(1, min(4, n // 2) + 1):
            for _ in range(30):
                s0 = rng.normal(size=n)
                s1 = rng.normal(size=n)
                f = identity_utility_frontier(ids, s0, s1, k)
                for pos, j in enumerate(f.j):
                    brute = brute_force_max(ids, s0, s1, k, int(j))
                    assert abs(float(f.utility[pos]) - brute) < 1e-12
                for eta in (0.0, 0.001, 0.01, 0.1):
                    out = select_identity_control(f, eta)
                    assert out["utility_regret"] <= eta + 1e-12
                    assert len(set(map(int, out["selected_indices"]))) == k
                cases += 1

    ids = np.asarray([f"z{i}" for i in range(20)])
    score = rng.normal(size=20)
    invariant = identity_utility_frontier(ids, score, score.copy(), 5)
    out = select_identity_control(invariant, 0.001)
    assert invariant.delta_unconstrained == 0
    assert out["j_eta"] == 0
    assert out["avoidable_turnover_fraction"] is None
    print({"brute_force_cases": cases, "invariance_pass": True})


if __name__ == "__main__":
    run()

