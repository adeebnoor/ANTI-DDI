#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import platform
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from identity_control import (
    binary_ndcg,
    binary_recall,
    bootstrap_mean_ci,
    identity_utility_frontier,
    select_identity_control,
    stable_order,
)


LOCK_LABEL = "RIDI-NATURE-IDENTITY-CONTROL-v1"
KS = (10, 50, 100)
ETAS = (0.0, 0.0001, 0.001, 0.005, 0.01)
PRIMARY_ETA = 0.001


def sha_seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16) % (2**32)


def bootstrap_summary(frame: pd.DataFrame) -> list[dict]:
    rows = []
    for (k, eta), group in frame.groupby(["k", "eta"]):
        atf = group["avoidable_turnover_fraction"].to_numpy(dtype=float)
        seed = sha_seed(f"{LOCK_LABEL}|text|k={int(k)}|eta={eta}|bootstrap")
        rows.append(
            {
                "k": int(k),
                "eta": float(eta),
                "n_queries": int(len(group)),
                "n_queries_with_turnover": int((group["delta_unconstrained"] > 0).sum()),
                "mean_delta_unconstrained": float(group["delta_unconstrained"].mean()),
                "mean_j_eta": float(group["j_eta"].mean()),
                "mean_atf": float(np.nanmean(atf)),
                "atf_ci95": bootstrap_mean_ci(atf, seed, 10_000),
                "mean_utility_regret": float(group["utility_regret"].mean()),
                "mean_ridi_unconstrained": float(group["ridi_unconstrained"].mean()),
                "mean_ridi_controlled": float(group["ridi_controlled"].mean()),
                "mean_ndcg_r1": float(group["ndcg_r1"].mean()),
                "mean_ndcg_controlled": float(group["ndcg_controlled"].mean()),
                "mean_recall_r1": float(group["recall_r1"].mean()),
                "mean_recall_controlled": float(group["recall_controlled"].mean()),
            }
        )
    return rows


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def main():
    out = Path(os.environ.get("OUTDIR", "results/identity_control_text"))
    out.mkdir(parents=True, exist_ok=True)

    data_home = os.environ.get("SCIKIT_LEARN_DATA")
    data = fetch_20newsgroups(
        subset="all",
        remove=("headers", "footers", "quotes"),
        shuffle=False,
        data_home=data_home,
    )
    records = []
    for i, (text, label) in enumerate(zip(data.data, data.target)):
        normalized = unicodedata.normalize("NFC", text).strip()
        if not normalized:
            continue
        digest = hashlib.sha256((normalized + "|" + str(i)).encode()).hexdigest()
        records.append((digest, i, normalized, int(label)))
    records.sort(key=lambda x: x[0])
    if len(records) < 5200:
        raise RuntimeError("not enough non-empty documents")
    candidates, queries = records[:5000], records[5000:5200]
    candidate_text = [x[2] for x in candidates]
    query_text = [x[2] for x in queries]
    candidate_labels = np.asarray([x[3] for x in candidates])
    query_labels = np.asarray([x[3] for x in queries])
    candidate_ids = np.asarray([f"doc_{x[1]}" for x in candidates], dtype=object)
    query_ids = np.asarray([f"doc_{x[1]}" for x in queries], dtype=object)

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        max_features=50000,
        norm="l2",
    )
    c0 = vectorizer.fit_transform(candidate_text)
    q0 = vectorizer.transform(query_text)
    svd = TruncatedSVD(n_components=256, random_state=20260823)
    c1 = normalize(svd.fit_transform(c0))
    q1 = normalize(svd.transform(q0))
    s0 = (q0 @ c0.T).toarray()
    s1 = q1 @ c1.T

    rng = np.random.default_rng(sha_seed("RIDI-NATURE-TEXT-TFIDF-PERM-v1"))
    permutation = rng.permutation(c0.shape[1])
    sc = (q0[:, permutation] @ c0[:, permutation].T).toarray()
    if float(np.max(np.abs(s0 - sc))) >= 1e-12:
        raise RuntimeError("locked feature-permutation score control failed")

    rows = []
    control_checks = []
    frontier_path = out / "text_frontier_points.csv.gz"
    with gzip.open(frontier_path, "wt", encoding="utf-8", newline="", compresslevel=6) as gz:
        writer = csv.DictWriter(
            gz,
            fieldnames=["query_id", "k", "j", "utility", "utility_regret"],
        )
        writer.writeheader()
        for qi, query_id in enumerate(query_ids):
            relevance = (candidate_labels == query_labels[qi]).astype(int)
            updated_order = stable_order(s1[qi], candidate_ids)
            for k in KS:
                frontier = identity_utility_frontier(candidate_ids, s0[qi], s1[qi], k)
                for j, utility, regret in zip(frontier.j, frontier.utility, frontier.regret):
                    writer.writerow(
                        {
                            "query_id": query_id,
                            "k": k,
                            "j": int(j),
                            "utility": float(utility),
                            "utility_regret": float(regret),
                        }
                    )

                control_frontier = identity_utility_frontier(candidate_ids, s0[qi], sc[qi], k)
                control = select_identity_control(control_frontier, PRIMARY_ETA)
                control_checks.append(
                    control_frontier.delta_unconstrained == 0 and control["j_eta"] == 0
                )

                ndcg_r1 = binary_ndcg(relevance, updated_order[:k], k)
                recall_r1 = binary_recall(relevance, updated_order[:k])
                for eta in ETAS:
                    selected = select_identity_control(frontier, eta)
                    chosen = np.asarray(selected.pop("selected_indices"), dtype=int)
                    local = stable_order(s1[qi][chosen], candidate_ids[chosen])
                    controlled_order = chosen[local]
                    rows.append(
                        {
                            "query_id": query_id,
                            "query_label": int(query_labels[qi]),
                            "k": k,
                            **selected,
                            "ndcg_r1": ndcg_r1,
                            "ndcg_controlled": binary_ndcg(relevance, controlled_order, k),
                            "recall_r1": recall_r1,
                            "recall_controlled": binary_recall(relevance, controlled_order),
                        }
                    )

    if not all(control_checks):
        raise RuntimeError("identity-control invariance check failed")
    detail = pd.DataFrame(rows)
    detail.to_csv(out / "text_identity_control_query_level.csv.gz", index=False, compression="gzip")
    summary_rows = bootstrap_summary(detail)
    pd.DataFrame(
        [
            {
                **{key: value for key, value in row.items() if key != "atf_ci95"},
                "atf_ci95_low": row["atf_ci95"][0],
                "atf_ci95_median": row["atf_ci95"][1],
                "atf_ci95_high": row["atf_ci95"][2],
            }
            for row in summary_rows
        ]
    ).to_csv(out / "text_identity_control_summary.csv", index=False)

    primary = next(
        row for row in summary_rows if row["k"] == 100 and np.isclose(row["eta"], PRIMARY_ETA)
    )
    result = {
        "lock_label": LOCK_LABEL,
        "dataset": "20 Newsgroups",
        "n_queries": 200,
        "n_candidates": 5000,
        "primary_transport_cutoff": 100,
        "primary_eta": PRIMARY_ETA,
        "primary_transport_result": primary,
        "all_summaries": summary_rows,
        "invariance_control": {
            "max_abs_similarity_difference": float(np.max(np.abs(s0 - sc))),
            "n_checks": len(control_checks),
            "all_delta_zero_and_j_zero": bool(all(control_checks)),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    (out / "TEXT_IDENTITY_CONTROL_RESULT.json").write_text(json.dumps(result, indent=2))
    manifest = []
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name != "RESULT_SHA256.json":
            manifest.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    (out / "RESULT_SHA256.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(primary, indent=2))


if __name__ == "__main__":
    main()
