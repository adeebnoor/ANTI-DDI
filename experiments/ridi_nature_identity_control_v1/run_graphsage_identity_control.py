#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import platform
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from identity_control import (
    bootstrap_mean_ci,
    identity_utility_frontier,
    select_identity_control,
)


SALT = "RTXKG2-20260818-GraphSAGE-v1"
LOCK_LABEL = "RIDI-NATURE-IDENTITY-CONTROL-v1"
PARENT_RUN_ID = 32643350756
PARENT_COMMIT = "304f977946b49120acbde300e8975284ac9db3b7"
EXPECTED_QUERY_STRUCTURE_SHA = "1291fa56e9074cbf41589b3e74f4fbc40687419ed44a7bb9800e9340e83e400e"
EXPECTED_UNIVERSE_SHA = "63f79154d270493514ee2d70971af8a4fb6d7e498be0044933a1bd1bc7ad8057"
SEEDS = [
    355092268, 1972696080, 1590711264, 1745982372,
    1113956884, 734518037, 1017280056, 54477576,
    202245501, 871610103, 1739075335, 404365195,
    1603643707, 1173720350, 1263375671, 1531572456,
]
A, B = SEEDS[:8], SEEDS[8:]
KS = (100, 500, 1000)
ETAS = (0.0, 0.0001, 0.001, 0.005, 0.01)
PRIMARY_ETA = 0.001


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def hval(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_queries(path: Path) -> dict[str, list[str]]:
    queries: dict[str, list[str]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            queries[row["query_raw_chem"]].append(row["candidate_raw_chem"])
    return dict(queries)


def read_raw_to_r1(path: Path, relevant: set[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["raw_chem"] in relevant:
                mapping[row["raw_chem"]] = row["primary_chem"]
    return mapping


def universe_offsets(freeze: Path):
    queries = read_queries(freeze / "chem_disease_query_candidates.tsv.gz")
    relevant = {item for q, cands in queries.items() for item in [q, *cands]}
    mapping = read_raw_to_r1(freeze / "chem_disease_frozen_edges.tsv.gz", relevant)
    meta, offset = [], 0
    universe_hash = hashlib.sha256()
    for query, candidates in sorted(queries.items()):
        query_group = mapping.get(query, query)
        groups = sorted({mapping.get(c, c) for c in candidates if mapping.get(c, c) != query_group})
        for group in groups:
            universe_hash.update(query.encode() + b"\t" + group.encode() + b"\n")
        meta.append((query, offset, len(groups), groups))
        offset += len(groups)
    return meta, offset, universe_hash.hexdigest()


def load_store(shards_root: Path, expected_n: int) -> dict[int, dict[str, np.ndarray]]:
    store: dict[int, dict[str, np.ndarray]] = {}
    manifests = []
    for path in shards_root.rglob("shard_manifest.json"):
        manifest = json.loads(path.read_text())
        manifests.append(manifest)
        if manifest["universe_sha256"] != EXPECTED_UNIVERSE_SHA:
            raise RuntimeError("seed-shard universe SHA mismatch")
        if int(manifest["n_universe_rows"]) != expected_n:
            raise RuntimeError("seed-shard universe length mismatch")
        for entry in manifest["files"]:
            target = path.parent / entry["name"]
            if target.exists() and sha256_file(target) != entry["sha256"]:
                raise RuntimeError(f"seed-shard file SHA mismatch: {target}")
    if len(manifests) != 8:
        raise RuntimeError(f"expected 8 shard manifests, found {len(manifests)}")
    for path in shards_root.rglob("ranks_*.npz"):
        seed = int(path.stem.split("_")[1])
        z = np.load(path)
        store[seed] = {"R0": z["R0"], "R1": z["R1"]}
    if set(store) != set(SEEDS):
        raise RuntimeError(f"seed mismatch: expected {SEEDS}, observed {sorted(store)}")
    for seed, arms in store.items():
        if len(arms["R0"]) != expected_n or len(arms["R1"]) != expected_n:
            raise RuntimeError(f"rank length mismatch for seed {seed}")
    return store


def mean_vec(store, seeds, arm):
    return np.mean(np.stack([store[s][arm] for s in seeds], axis=0), axis=0)


def bootstrap_seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16) % (2**32)


def write_manifest(out: Path):
    rows = []
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name != "RESULT_SHA256.json":
            rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    (out / "RESULT_SHA256.json").write_text(json.dumps(rows, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-dir", required=True)
    parser.add_argument("--shards-root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    freeze, shards, out = Path(args.freeze_dir), Path(args.shards_root), Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    structure_path = freeze / "chem_disease_query_structure.json"
    if sha256_file(structure_path) != EXPECTED_QUERY_STRUCTURE_SHA:
        raise RuntimeError("query structure SHA mismatch")
    meta, total_n, universe_sha = universe_offsets(freeze)
    if universe_sha != EXPECTED_UNIVERSE_SHA:
        raise RuntimeError("reconstructed universe SHA mismatch")
    store = load_store(shards, total_n)

    means = {
        "R0A": mean_vec(store, A, "R0"),
        "R1A": mean_vec(store, A, "R1"),
        "R0B": mean_vec(store, B, "R0"),
        "R1B": mean_vec(store, B, "R1"),
    }
    contrasts = (
        ("representation", "rep_A", "R0A", "R1A"),
        ("representation", "rep_B", "R0B", "R1B"),
        ("stochastic", "stoch_R0", "R0A", "R0B"),
        ("stochastic", "stoch_R1", "R1A", "R1B"),
    )

    selected_rows = []
    frontier_path = out / "graphsage_frontier_points.csv.gz"
    with gzip.open(frontier_path, "wt", encoding="utf-8", newline="", compresslevel=6) as gz:
        frontier_writer = csv.DictWriter(
            gz,
            fieldnames=["query", "contrast_type", "contrast", "k", "j", "utility", "utility_regret"],
        )
        frontier_writer.writeheader()
        for query, offset, n, groups in meta:
            ids = np.asarray(groups, dtype=object)
            for contrast_type, contrast, left, right in contrasts:
                s0 = means[left][offset : offset + n]
                s1 = means[right][offset : offset + n]
                for k in KS:
                    if n < 2 * k:
                        raise RuntimeError(f"query {query} has n={n}, below locked 2k requirement for k={k}")
                    frontier = identity_utility_frontier(ids, s0, s1, k)
                    for j, utility, regret in zip(frontier.j, frontier.utility, frontier.regret):
                        frontier_writer.writerow(
                            {
                                "query": query,
                                "contrast_type": contrast_type,
                                "contrast": contrast,
                                "k": k,
                                "j": int(j),
                                "utility": float(utility),
                                "utility_regret": float(regret),
                            }
                        )
                    for eta in ETAS:
                        control = select_identity_control(frontier, eta)
                        selected_rows.append(
                            {
                                "query": query,
                                "contrast_type": contrast_type,
                                "contrast": contrast,
                                "k": k,
                                "eta": eta,
                                "n_candidates": n,
                                "delta_unconstrained": control["delta_unconstrained"],
                                "j_eta": control["j_eta"],
                                "avoidable_turnover_fraction": control["avoidable_turnover_fraction"],
                                "utility_regret": control["utility_regret"],
                                "ridi_unconstrained": control["ridi_unconstrained"],
                                "ridi_controlled": control["ridi_controlled"],
                            }
                        )

    detail = pd.DataFrame(selected_rows)
    detail.to_csv(out / "graphsage_identity_control_query_level.csv.gz", index=False, compression="gzip")
    summary = (
        detail.groupby(["contrast_type", "contrast", "k", "eta"], dropna=False)
        .agg(
            n_queries=("query", "size"),
            n_queries_with_turnover=("delta_unconstrained", lambda x: int((x > 0).sum())),
            mean_delta_unconstrained=("delta_unconstrained", "mean"),
            mean_j_eta=("j_eta", "mean"),
            mean_atf=("avoidable_turnover_fraction", "mean"),
            mean_utility_regret=("utility_regret", "mean"),
            mean_ridi_unconstrained=("ridi_unconstrained", "mean"),
            mean_ridi_controlled=("ridi_controlled", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(out / "graphsage_identity_control_summary.csv", index=False)

    primary_cells = detail[
        (detail["contrast_type"] == "representation")
        & np.isclose(detail["eta"], PRIMARY_ETA)
    ].copy()
    primary_by_query = (
        primary_cells.groupby("query", as_index=False)
        .agg(
            mean_atf=("avoidable_turnover_fraction", "mean"),
            mean_delta_unconstrained=("delta_unconstrained", "mean"),
            mean_j_eta=("j_eta", "mean"),
            mean_ridi_unconstrained=("ridi_unconstrained", "mean"),
            mean_ridi_controlled=("ridi_controlled", "mean"),
            mean_utility_regret=("utility_regret", "mean"),
            n_nonzero_cells=("delta_unconstrained", lambda x: int((x > 0).sum())),
        )
    )
    primary_by_query.to_csv(out / "graphsage_primary_query_endpoint.csv", index=False)
    seed = bootstrap_seed(f"{LOCK_LABEL}|graphsage|bootstrap")
    ci = bootstrap_mean_ci(primary_by_query["mean_atf"].to_numpy(), seed, 10_000)
    mean_atf = float(primary_by_query["mean_atf"].mean())
    verdict = {
        "lock_label": LOCK_LABEL,
        "parent_run_id": PARENT_RUN_ID,
        "parent_commit": PARENT_COMMIT,
        "primary_eta": PRIMARY_ETA,
        "primary_cutoffs": list(KS),
        "primary_ensemble_size": 8,
        "n_queries": int(len(primary_by_query)),
        "mean_avoidable_turnover_fraction": mean_atf,
        "bootstrap_seed": seed,
        "bootstrap_95_percentile_CI": ci,
        "material_control_threshold": 0.25,
        "primary_success": bool(ci[0] > 0.25),
        "mean_delta_unconstrained": float(primary_by_query["mean_delta_unconstrained"].mean()),
        "mean_j_eta": float(primary_by_query["mean_j_eta"].mean()),
        "mean_ridi_unconstrained": float(primary_by_query["mean_ridi_unconstrained"].mean()),
        "mean_ridi_controlled": float(primary_by_query["mean_ridi_controlled"].mean()),
        "mean_utility_regret": float(primary_by_query["mean_utility_regret"].mean()),
        "query_structure_sha256": EXPECTED_QUERY_STRUCTURE_SHA,
        "universe_sha256": EXPECTED_UNIVERSE_SHA,
    }
    (out / "GRAPHSAGE_IDENTITY_CONTROL_VERDICT.json").write_text(json.dumps(verdict, indent=2))
    (out / "VERDICT.md").write_text(
        "# GraphSAGE identity-control locked verdict\n\n"
        f"**Primary success:** {'PASS' if verdict['primary_success'] else 'NOT MET'}\n\n"
        f"Mean avoidable-turnover fraction at eta=0.001: **{mean_atf:.6f}**\n\n"
        f"95% query-bootstrap CI: **[{ci[0]:.6f}, {ci[2]:.6f}]**\n\n"
        f"Mean changed slots before control: **{verdict['mean_delta_unconstrained']:.3f}**\n\n"
        f"Mean minimum necessary changed slots: **{verdict['mean_j_eta']:.3f}**\n"
    )
    environment = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "parent_run_id": PARENT_RUN_ID,
        "parent_commit": PARENT_COMMIT,
    }
    (out / "ENVIRONMENT.json").write_text(json.dumps(environment, indent=2))
    write_manifest(out)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

