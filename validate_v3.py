from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
errors = []

def check(cond, msg):
    if cond:
        print(f"PASS: {msg}")
    else:
        print(f"FAIL: {msg}")
        errors.append(msg)

v2 = pd.read_csv(DATA / "antiddi_v2_dataset.csv")
v3 = pd.read_csv(DATA / "antiddi_v3_dataset.csv")
bench = pd.read_csv(DATA / "antiddi_v3_benchmark.csv")
split = pd.read_csv(DATA / "paper5_split_manifest.csv")
anchors = pd.read_csv(DATA / "clinical_anchor_pairs.csv")
original_cols = list(v2.columns)

check(len(v3) == 797, "v3 has 797 audit records")
check(v3["pair_id"].is_unique, "pair_id is unique")
check(list(v3.columns[:len(original_cols)]) == original_cols,
      "the original 35 v2 columns are preserved in order")
same = True
for col in original_cols:
    a, b = v2[col], v3[col]
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
        import numpy as np
        if not np.allclose(a.to_numpy(dtype=float), b.to_numpy(dtype=float), equal_nan=True, rtol=0, atol=1e-12):
            same = False; break
    else:
        eq = (a.astype("string") == b.astype("string")) | (a.isna() & b.isna())
        if not bool(eq.fillna(False).all()):
            same = False; break
check(same, "all original v2 values are unchanged (within CSV float precision)")

state_counts = v3["knowledge_state"].value_counts().to_dict()
check(state_counts.get("ANTI_DDI_CANDIDATE_HIGHER_SUPPORT", 0) == 538,
      "538 records are higher-support Anti-DDI benchmark candidates")
check(state_counts.get("ANTI_DDI_CANDIDATE_LIMITED", 0) == 106,
      "106 records are limited Anti-DDI candidates")
check(state_counts.get("STRUCTURAL_CONTROL_ONLY", 0) == 44, "44 records are structural controls")
check(state_counts.get("UNRESOLVED", 0) == 76, "76 records are unresolved")
check(state_counts.get("POSITIVE_CONCERN_EXCLUDED", 0) == 33, "33 records are excluded for positive concern")

check(len(bench) == 538, "default benchmark has 538 rows")
check(set(bench["knowledge_state"]) == {"ANTI_DDI_CANDIDATE_HIGHER_SUPPORT"},
      "default benchmark contains only higher-support candidate records")
check(set(bench["recommended_use"]) == {"DEFAULT_BENCHMARK_CANDIDATE"},
      "default benchmark is explicitly marked candidate use")
check(set(bench["evidence_tier"]).issubset({"T1_wellpowered", "T2_moderate"}),
      "default benchmark contains only T1/T2 tiers")

split_counts = split["split"].value_counts().to_dict()
check(len(split) == 214, "legacy classifier manifest has 214 provenance pairs")
check(split_counts.get("development", 0) == 40, "legacy development split has 40 pairs")
check(split_counts.get("confirmatory", 0) == 174, "legacy confirmatory split has 174 pairs")
check(set(split["pair_id"]).issubset(set(v3["pair_id"])), "all legacy split pairs exist in the v3 dataset")

check(len(anchors) == 8, "clinical anchor table has 8 pairs")
check(set(anchors["pair_id"]).issubset(set(bench["pair_id"])),
      "all clinical anchors belong to the T1/T2 candidate benchmark")
check((anchors["concordant"] == 1).all(), "all eight targeted clinical anchors are concordant")
check((anchors["analysis_status"] == "post-confirmatory supportive").all(),
      "clinical anchors are explicitly marked targeted/supportive")

check(not (v3.loc[v3["knowledge_state"] == "UNRESOLVED", "recommended_use"] == "DEFAULT_BENCHMARK_CANDIDATE").any(),
      "UNRESOLVED records are never default benchmark candidates")
check(not (v3.loc[v3["knowledge_state"] == "POSITIVE_CONCERN_EXCLUDED", "recommended_use"] == "DEFAULT_BENCHMARK_CANDIDATE").any(),
      "positive-concern exclusions are never default benchmark candidates")

if errors:
    print(f"\n{len(errors)} v3 validation check(s) failed.")
    sys.exit(1)
print("\nAll Anti-DDI v3.0.1 semantic and release checks passed.")
