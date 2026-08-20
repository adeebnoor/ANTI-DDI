#!/usr/bin/env python3
"""Deterministically rebuild Anti-DDI v3 release tables from immutable v2 plus frozen Paper 5 metadata."""
from pathlib import Path
from io import BytesIO
import base64, zlib
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SPLIT_CSV_ZLIB_B64 = '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'
ANCHOR_CSV_ZLIB_B64 = 'eNrtll+P4zQUxd/5FH4EyWns9E9aRggNDIgR7Go0i4TgJbq1b1Izjh1sp53y6blpp50ULauyQjztU+PEuT7nd+ybdmBCZTTXoW8qOP6sObhktDZVMhg4PicMDmy16VtwFW6NRqeQ06CPKpguVQFrDIebyjvlg6YCVERtfKjSvkMefR8UVsokSMa709h6BckHmgp2H02sIj3v42e3d3f3RSZm85JH3KKFdtBBk6ALxvKfi6r1GgMk5D8MopgKPka/xcAefmQx9Xp/w5xnLYIzrql7y9QGXIPMOHauk5+vIDF87nzsA/KZ5JIfrZ6rVt0T/6YPT8gwMbATVgghb9hZW/aqbZNSF7/Mc+3NxIcml2IiZVnmQqxkUdJrBb27Wi4lp/VSRrxqE9qBwp7Fvut8SGaLJwJyVowItJh8F7z1hEBWO7S28zsCrz9A4eSLhYF8ZNBRhWdDK6Lds7Xx+EdvtmCREvso6yNR/633olyNvO8g1BCMuzL80/RX/707bgHNZ+IjbJ7Xv9JkWVxnUhTc0iLJBFCYoB0ZfV/EATsk5zrTPuLJ7GP+7qxvYABOs/u3j2PLxdnyqUI1VCDbVaf5IzQ9OoQ+ewO/W4zRXGK4UPhhFEIu8ndiVYhMFlJ+LuQXQhSraTa/br+Xkvcx4ZNxJHbNfYtdgD+9xb/jeNgAAZDsYIp9++tDRptwjaPDr6xxRoGlbR5N40xNA/d60F86Ap9NCU3AprcHUdXptarbAAlVtLObPf/+7pb98t1vP92+vWVdwKHvramzUD+p/WCHmtoNGykfFM3mgiyuYxr2ajzT2u12E1CKKGtIMKk1TBq/zYfWGyHRkJJRMbewRpvT/ljk5UIWy3kUYmHXlgbTqXwZTDpdXwV2WswvwGrq6oHoJmrRZPTyWH1i+6/YSim4pdPR2J4+m0jX0Th//FK9t02/UMjGFE5wyQ0dTuYDPR9kM1hHimiAQODpUNY1qmFG8gzGOQSkUzqEoLEJSOxn17C/A2P3b6jcyMA/h2BctjVbP1JnHP05AHWQNzgwozD0ULtFPXG2nTizOUbxcvOQyT0Vn6i6/TpSe9FfFYVaLlblIlst5mU201pky7quM6Gm9bQWy+m8VNclMpcXiRwb1xDKBt2nUP7nUP4CCK+2gA=='


def state_and_use(row):
    tier = str(row["evidence_tier"])
    if tier.startswith("EXCLUDED") or bool(row["excluded_clinical"]):
        return "POSITIVE_CONCERN_EXCLUDED", "EXCLUDE_POSITIVE_CONCERN"
    if tier in {"T1_wellpowered", "T2_moderate"}:
        return "ANTI_DDI_SUPPORTED", "DEFAULT_BENCHMARK"
    if tier == "T3_limited":
        return "ANTI_DDI_CANDIDATE_LIMITED", "SENSITIVITY_ONLY"
    if tier == "T3_trivial_inert":
        return "STRUCTURAL_CONTROL_ONLY", "EXCLUDE_FROM_BENCHMARK"
    return "UNRESOLVED", "DO_NOT_LABEL_NEGATIVE"


def decode_csv(payload):
    return pd.read_csv(BytesIO(zlib.decompress(base64.b64decode(payload))))


def main():
    v2 = pd.read_csv(DATA / "antiddi_v2_dataset.csv")
    split = decode_csv(SPLIT_CSV_ZLIB_B64)
    anchors = decode_csv(ANCHOR_CSV_ZLIB_B64)

    v3 = v2.copy()
    states = v3.apply(state_and_use, axis=1, result_type="expand")
    v3["knowledge_state"] = states[0]
    v3["recommended_use"] = states[1]
    role_map = dict(zip(split["pair_id"].astype(str), split["split"].astype(str)))
    v3["paper5_role"] = v3["pair_id"].astype(str).map(role_map).fillna("not_used_in_paper5")

    v3["clinical_anchor_status"] = "NOT_ANCHORED"
    for col in ["clinical_anchor_type", "clinical_anchor_source", "clinical_anchor_locator", "clinical_anchor_summary", "clinical_anchor_concordance"]:
        v3[col] = ""

    anchor_map = {str(r["pair_id"]): r for _, r in anchors.iterrows()}
    for idx, pid in v3["pair_id"].astype(str).items():
        a = anchor_map.get(pid)
        if a is None:
            continue
        v3.at[idx, "clinical_anchor_status"] = "HUMAN_NONINTERACTION_ANCHOR"
        v3.at[idx, "clinical_anchor_type"] = a["anchor_type"]
        v3.at[idx, "clinical_anchor_source"] = a["source_citation"]
        v3.at[idx, "clinical_anchor_locator"] = a["source_locator"]
        v3.at[idx, "clinical_anchor_summary"] = a["external_human_evidence"]
        v3.at[idx, "clinical_anchor_concordance"] = "CONCORDANT" if int(a["concordant"]) == 1 else "DISCORDANT"

    v3.to_csv(DATA / "antiddi_v3_dataset.csv", index=False)
    v3[v3["recommended_use"].eq("DEFAULT_BENCHMARK")].to_csv(DATA / "antiddi_v3_benchmark.csv", index=False)
    split.to_csv(DATA / "paper5_split_manifest.csv", index=False)
    anchors.to_csv(DATA / "clinical_anchor_pairs.csv", index=False)
    print(f"Wrote {len(v3)} v3 rows; {len(split)} Paper 5 rows; {len(anchors)} clinical anchors")

if __name__ == "__main__":
    main()
