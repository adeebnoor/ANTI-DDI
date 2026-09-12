#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


def auc_mw(pos_scores, neg_scores):
    p = np.asarray(pos_scores, float)
    n = np.asarray(neg_scores, float)
    if len(p) == 0 or len(n) == 0:
        return float("nan")
    ranks = pd.Series(np.concatenate([p, n])).rank(method="average").to_numpy()
    u = ranks[: len(p)].sum() - len(p) * (len(p) + 1) / 2
    return float(u / (len(p) * len(n)))


def d_bin(d: int) -> int:
    if d <= 0:
        return 0
    return int(math.floor(math.log2(d))) + 1


def score(edge, dl, dr):
    a, b = edge
    return float(np.log1p(dl.get(a, 0)) * np.log1p(dr.get(b, 0)))


def parse_edges(path: str):
    # Canonical SNAP file has a tab-delimited comment/header line but comma-delimited
    # data rows. Treat '#' as comment and parse the actual edge rows as CSV.
    d = pd.read_csv(
        path,
        compression="infer",
        comment="#",
        header=None,
        names=["drug", "gene"],
        sep=",",
        skip_blank_lines=True,
    )
    d = d.dropna(subset=["drug", "gene"])
    edges = sorted({
        (str(a).strip().replace("\r", ""), str(b).strip().replace("\r", ""))
        for a, b in zip(d["drug"], d["gene"])
    })
    edges = [e for e in edges if e[0] and e[1] and e[0] != "nan" and e[1] != "nan"]
    if len(edges) < 100:
        raise ValueError(f"Parsed only {len(edges)} edges; expected a large DTI edge list.")
    return edges


def sample_nonedges(rng, n, left, right, blocked):
    out = set()
    max_attempts = max(200000, n * 100)
    attempts = 0
    while len(out) < n and attempts < max_attempts:
        attempts += 1
        e = (left[int(rng.integers(len(left)))], right[int(rng.integers(len(right)))])
        if e in blocked or e in out:
            continue
        out.add(e)
    if len(out) < n:
        raise RuntimeError(f"sampled only {len(out)} of requested {n} nonedges")
    return list(out)


def match_by_degree(rng, positives, candidate_negatives, dl, dr):
    pools = defaultdict(list)
    for e in candidate_negatives:
        pools[(d_bin(dl.get(e[0], 0)), d_bin(dr.get(e[1], 0)))].append(e)
    for p in pools.values():
        rng.shuffle(p)
    used = Counter()
    mp, mn = [], []
    for i in rng.permutation(len(positives)):
        e = positives[int(i)]
        sig = (d_bin(dl.get(e[0], 0)), d_bin(dr.get(e[1], 0)))
        pool = pools.get(sig, [])
        j = used[sig]
        if j < len(pool):
            mp.append(e)
            mn.append(pool[j])
            used[sig] += 1
    return mp, mn


def one_seed(edges, seed, test_fraction=0.2):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(edges))
    n_test = max(1, int(round(len(edges) * test_fraction)))
    test = [edges[i] for i in idx[:n_test]]
    train = [edges[i] for i in idx[n_test:]]
    all_set = set(edges)

    dl = Counter(a for a, _ in train)
    dr = Counter(b for _, b in train)
    left = sorted({a for a, _ in edges})
    right = sorted({b for _, b in edges})

    test_seen = [e for e in test if dl.get(e[0], 0) > 0 and dr.get(e[1], 0) > 0]
    if len(test_seen) < 10:
        raise ValueError(f"Only {len(test_seen)} test edges have both endpoints observed in training.")

    random_neg = sample_nonedges(rng, len(test_seen), left, right, all_set)
    universe_nonedges = len(left) * len(right) - len(all_set)
    match_n = min(max(len(test_seen) * 20, 50000), universe_nonedges)
    match_pool = sample_nonedges(rng, match_n, left, right, all_set)
    mp, mn = match_by_degree(rng, test_seen, match_pool, dl, dr)

    auc_random = auc_mw([score(e, dl, dr) for e in test_seen], [score(e, dl, dr) for e in random_neg])
    auc_matched = auc_mw([score(e, dl, dr) for e in mp], [score(e, dl, dr) for e in mn]) if mp else float("nan")
    collapse = (auc_random - auc_matched) / (auc_random - 0.5) if auc_random > 0.55 and np.isfinite(auc_matched) else float("nan")

    return {
        "seed": seed,
        "n_train": len(train),
        "n_test": len(test),
        "n_test_seen_endpoints": len(test_seen),
        "seen_test_fraction": len(test_seen) / len(test),
        "n_degree_matched": len(mp),
        "matched_fraction": len(mp) / len(test_seen),
        "auc_random": auc_random,
        "auc_degree_matched": auc_matched,
        "inflation_auc": auc_random - auc_matched,
        "collapse_fraction": collapse,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--replicates", type=int, default=20)
    args = ap.parse_args()

    edges = parse_edges(args.input)
    rows = [one_seed(edges, s) for s in range(args.replicates)]
    out = pd.DataFrame(rows)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_csv, index=False)

    summary = {
        "benchmark": "BioSNAP TargetDecagon drug-target interactions",
        "source_url": "https://snap.stanford.edu/biodata/datasets/10015/files/ChG-TargetDecagon_targets.csv.gz",
        "edge_count": len(edges),
        "left_nodes": len({a for a, _ in edges}),
        "right_nodes": len({b for _, b in edges}),
        "replicates": args.replicates,
        "auc_random_mean": float(out.auc_random.mean()),
        "auc_random_sd": float(out.auc_random.std(ddof=1)),
        "auc_degree_matched_mean": float(out.auc_degree_matched.mean()),
        "auc_degree_matched_sd": float(out.auc_degree_matched.std(ddof=1)),
        "inflation_auc_mean": float(out.inflation_auc.mean()),
        "inflation_auc_sd": float(out.inflation_auc.std(ddof=1)),
        "collapse_fraction_mean": float(out.collapse_fraction.mean()),
        "matched_fraction_mean": float(out.matched_fraction.mean()),
        "seen_test_fraction_mean": float(out.seen_test_fraction.mean()),
        "interpretation_boundary": "Model-free structural diagnostic; no claim about biological truth or clinical validity.",
    }
    Path(args.out_json).write_text(json.dumps(summary, indent=2) + "\n")

    gate = summary["auc_random_mean"] >= 0.60 and summary["inflation_auc_mean"] >= 0.08 and summary["matched_fraction_mean"] >= 0.50
    md = f"""# Gate 1 — BioSNAP DTI result\n\n- Edges: **{summary['edge_count']:,}**\n- Drugs: **{summary['left_nodes']:,}**\n- Targets: **{summary['right_nodes']:,}**\n- Degree-only AUC, conventional random negatives: **{summary['auc_random_mean']:.3f} ± {summary['auc_random_sd']:.3f}**\n- Degree-only AUC, degree-matched negatives: **{summary['auc_degree_matched_mean']:.3f} ± {summary['auc_degree_matched_sd']:.3f}**\n- Mean AUC inflation: **{summary['inflation_auc_mean']:.3f}**\n- Mean matched fraction: **{summary['matched_fraction_mean']:.3f}**\n- Gate-1 DTI structural-inflation signal: **{'PASS' if gate else 'FAIL / INCONCLUSIVE'}**\n\nPrespecified operational pass rule for this first external audit: conventional degree-only AUC >= 0.60, AUC inflation >= 0.08, and >= 50% of evaluable test positives degree matched. This rule is an internal project gate, not a universal scientific threshold.\n"""
    Path(args.out_md).write_text(md)
    print(json.dumps(summary, indent=2))
    print(md)


if __name__ == "__main__":
    main()
