#!/usr/bin/env python3
"""Reproducibility harness for the Anti-DDI v2 release.

Re-derives from the shipped files every quantity the manuscript reports and
asserts each against the published value. Prints one ``PASS``/``FAIL`` line
per quantity and exits non-zero if any check fails.

Quantities that the manuscript reports but that are *not* derivable from the
shipped files are printed as ``SKIP`` with the reason, and are excluded from
the pass count rather than silently omitted.

Usage
-----
    python validate.py                 # from the package root
    python validate.py --data-dir data
    python validate.py --verbose       # also print observed values for passes
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parent))

from antiddi import __version__  # noqa: E402
from antiddi.evidence import (  # noqa: E402
    ANCHOR_DRUGS,
    FAERS_DENOMINATOR,
    assign_tier,
    min_detectable_ror,
)

RESULTS: list[tuple[str, bool, str, str]] = []  # (name, ok, expected, observed)
SKIPS: list[tuple[str, str]] = []


def check(name: str, observed, expected, tol: float = 0.0) -> bool:
    """Record one assertion. ``tol`` is an absolute tolerance for numbers."""
    if isinstance(expected, float) and math.isinf(expected):
        ok = isinstance(observed, float) and math.isinf(observed) and (observed > 0) == (expected > 0)
    elif isinstance(expected, (int, float)) and isinstance(observed, (int, float, np.number)):
        ok = abs(float(observed) - float(expected)) <= tol
    else:
        ok = observed == expected
    RESULTS.append((name, bool(ok), _fmt(expected), _fmt(observed)))
    return bool(ok)


def skip(name: str, reason: str) -> None:
    SKIPS.append((name, reason))


def _fmt(v) -> str:
    if isinstance(v, float):
        if math.isinf(v):
            return "inf"
        return f"{v:.6g}"
    return str(v)


def _key(name) -> str:
    return str(name).strip().lower()


def _pairset(frame: pd.DataFrame) -> set[tuple[str, str]]:
    return {tuple(sorted((_key(a), _key(b)))) for a, b in zip(frame["drug_a"], frame["drug_b"])}


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default="data", help="directory holding the shipped CSVs")
    ap.add_argument("--verbose", action="store_true", help="print observed values for passing checks")
    args = ap.parse_args()
    d = Path(args.data_dir)

    print(f"Anti-DDI v2 reproducibility harness — package version {__version__}")
    print(f"data directory: {d.resolve()}")
    print()

    df = pd.read_csv(d / "antiddi_v2_dataset.csv")
    bench = pd.read_csv(d / "benchmark_replicates.csv")
    defects = pd.read_csv(d / "audit_defects.csv")
    norm = pd.read_csv(d / "audit_drug_normalization.csv")
    signal = pd.read_csv(d / "signal_detection_t1.csv")

    # -- 1. file shape ------------------------------------------------------
    check("dataset row count", len(df), 797)
    check("dataset column count", df.shape[1], 35)
    check(
        "dataset column names",
        list(df.columns),
        [
            "pair_id", "drug_a", "drug_b", "faers_coreports", "faers_expected",
            "obs_exp_ratio", "min_detectable_ror", "evidence_tier", "n_anchor_drugs",
            "both_pk_inert", "excluded_clinical", "name_defect_v1",
            "faers_reports_a", "faers_reports_b", "rxcui_a", "atc_a", "drugbank_a",
            "chembl_a", "rxcui_b", "atc_b", "drugbank_b", "chembl_b",
            "n_ae_terms_tested", "median_upper95_ror", "p95_upper95_ror",
            "max_upper95_ror", "frac_terms_equiv_ror1.5", "frac_terms_equiv_ror2.0",
            "frac_terms_equiv_ror3.0", "gold_d3r_testable", "gold_d3r_flagged",
            "label_screen", "label_evidence", "d3_mechanism_hypotheses",
            "d3_hypothesis_types",
        ],
    )
    check("pair_id is unique", bool(df.pair_id.is_unique), True)
    check("pair_id format ADDI2-NNNN", int(df.pair_id.str.fullmatch(r"ADDI2-\d{4}").sum()), 797)

    drugs = sorted({_key(x) for x in pd.concat([df.drug_a, df.drug_b])})
    check("distinct drug names", len(drugs), 161)

    pairs = _pairset(df)
    check("distinct unordered pairs (no residual duplication)", len(pairs), 797)

    # -- 2. FAERS evidence layer -------------------------------------------
    check("FAERS denominator constant", FAERS_DENOMINATOR, 20_328_575)
    exp = df.faers_reports_a.astype(float) * df.faers_reports_b.astype(float) / FAERS_DENOMINATOR
    check(
        "faers_expected == reports_a*reports_b/denominator (all rows)",
        int(np.isclose(exp, df.faers_expected, rtol=1e-9).sum()),
        797,
    )
    check(
        "obs_exp_ratio == coreports/expected (all rows)",
        int(np.isclose(df.faers_coreports / df.faers_expected, df.obs_exp_ratio, rtol=1e-9).sum()),
        797,
    )

    check("co-reports median (all 797 pairs)", float(df.faers_coreports.median()), 332.0)
    check("co-reports mean (all 797 pairs)", float(df.faers_coreports.mean()), 1150.6, tol=0.05)
    check("co-reports SD (all 797 pairs)", float(df.faers_coreports.std()), 2434.9, tol=0.05)
    check("co-reports maximum", float(df.faers_coreports.max()), 21095.0)
    check("co-reports minimum", float(df.faers_coreports.min()), 0.0)

    for thresh, expected in [(0, 1), (1, 5), (5, 23), (10, 37), (25, 81), (50, 119), (100, 198)]:
        check(f"pairs with co-reports <= {thresh}", int((df.faers_coreports <= thresh).sum()), expected)

    # -- 3. min_detectable_ror reproduced from the documented formula ------
    recomputed = [min_detectable_ror(n) for n in df.faers_coreports]
    matches = sum(
        1
        for r, o in zip(recomputed, df.min_detectable_ror)
        if (math.isinf(r) and math.isinf(float(o))) or abs(r - float(o)) < 1e-9
    )
    check("min_detectable_ror reproduced by antiddi.evidence (all rows)", matches, 797)
    check("min_detectable_ror rows reported as inf", int(np.isinf(df.min_detectable_ror).sum()), 90)
    finite = df.min_detectable_ror[np.isfinite(df.min_detectable_ror)]
    check("min_detectable_ror smallest finite value", float(finite.min()), 1.30, tol=1e-9)
    check("min_detectable_ror largest finite value", float(finite.max()), 28.80, tol=1e-9)

    # -- 4. evidence_tier reproduced from the documented rules -------------
    retiered = [assign_tier(r) for _, r in df.iterrows()]
    # EXCLUDED_label (3 pairs) is assigned by the FDA structured-product-label
    # re-screening step (manuscript Sect. 3.3), not by the tier decision list,
    # so assign_tier reproduces every tier EXCEPT those 3 rows.
    non_label = (df.evidence_tier != "EXCLUDED_label").values
    check(
        "evidence_tier reproduced by antiddi.evidence rules (all non-label rows)",
        int((np.array(retiered)[non_label] == df.evidence_tier.values[non_label]).sum()),
        794,
    )
    check(
        "EXCLUDED_label rows assigned by FDA-label re-screening (Sect. 3.3)",
        int((~non_label).sum()),
        3,
    )

    tier_counts = {
        "T1_wellpowered": 217,
        "T2_moderate": 321,
        "T3_limited": 106,
        "T3_trivial_inert": 44,
        "T4_uninformative": 76,
        "EXCLUDED_clinical": 30,
        "EXCLUDED_label": 3,
    }
    obs_tiers = df.evidence_tier.value_counts().to_dict()
    for tier, expected in tier_counts.items():
        check(f"tier count {tier}", int(obs_tiers.get(tier, 0)), expected)
    check("tier counts sum to the file", sum(obs_tiers.values()), 797)
    check(
        "usable benchmark set (T1+T2)",
        int(df.evidence_tier.isin(["T1_wellpowered", "T2_moderate"]).sum()),
        538,
    )

    med_co = {
        "T1_wellpowered": 2020.0,
        "T2_moderate": 291.0,
        "T3_limited": 59.0,
        "T3_trivial_inert": 623.0,
        "T4_uninformative": 11.5,
    }
    med_mdror = {
        "T1_wellpowered": 2.15,
        "T2_moderate": 5.15,
        "T3_limited": 17.15,
        "T3_trivial_inert": 3.40,
        "T4_uninformative": float("inf"),
    }
    g = df.groupby("evidence_tier")
    for tier, expected in med_co.items():
        check(f"median co-reports, {tier}", float(g.faers_coreports.median()[tier]), expected, tol=1e-9)
    for tier, expected in med_mdror.items():
        check(f"median min-detectable ROR, {tier}", float(g.min_detectable_ror.median()[tier]), expected, tol=1e-9)

    # -- 5. flags and structural facts ------------------------------------
    check("excluded_clinical flag count", int(df.excluded_clinical.sum()), 30)
    check(
        "excluded_clinical flag agrees with EXCLUDED_clinical tier",
        int((df.excluded_clinical == (df.evidence_tier == "EXCLUDED_clinical")).sum()),
        797,
    )
    check("both_pk_inert flag count", int(df.both_pk_inert.sum()), 51)
    check(
        "T3_trivial_inert is exactly the non-excluded, adequately co-reported pk-inert set",
        int(((df.both_pk_inert) & (df.evidence_tier == "T3_trivial_inert")).sum()),
        44,
    )
    check("name_defect_v1 flag count", int(df.name_defect_v1.sum()), 110)

    # the two opioid x Z-drug pairs must be present AND excluded
    for partner in ("zopiclone", "zaleplon"):
        key = tuple(sorted(("hydrocodone", partner)))
        row = df[
            (df.drug_a.map(_key) == key[0]) & (df.drug_b.map(_key) == key[1])
            | (df.drug_a.map(_key) == key[1]) & (df.drug_b.map(_key) == key[0])
        ]
        present = len(row) == 1
        excluded = present and bool(row.iloc[0].excluded_clinical)
        check(f"hydrocodone x {partner} present and flagged excluded_clinical", (present, excluded), (True, True))

    # 13-drug vertex cover
    anchors = {_key(a) for a in ANCHOR_DRUGS}
    check("anchor set size", len(anchors), 13)
    recount = df.drug_a.map(_key).isin(anchors).astype(int) + df.drug_b.map(_key).isin(anchors).astype(int)
    check("n_anchor_drugs reproduced from the anchor set (all rows)", int((recount == df.n_anchor_drugs).sum()), 797)
    check("pairs containing no anchor drug (vertex cover is complete)", int((recount == 0).sum()), 0)
    aa = sum(1 for a, b in pairs if a in anchors and b in anchors)
    ao = sum(1 for a, b in pairs if (a in anchors) != (b in anchors))
    oo = sum(1 for a, b in pairs if a not in anchors and b not in anchors)
    check("edges anchor-anchor", aa, 49)
    check("edges anchor-other", ao, 748)
    check("edges other-other (the 148 remaining drugs are an independent set)", oo, 0)
    check("non-anchor drugs", len(set(drugs) - anchors), 148)

    deg = Counter()
    for a, b in pairs:
        deg[a] += 1
        deg[b] += 1
    check("released-file degree, sevelamer (797 deduplicated pairs)", deg["sevelamer"], 150)
    check("released-file degree, ustekinumab (797 deduplicated pairs)", deg["ustekinumab"], 138)
    check("released-file maximum degree (797 deduplicated pairs)", max(deg.values()), 150)

    # -- 6. audit of the predecessor file ---------------------------------
    check("audit defect instances", len(defects), 902)
    check("predecessor rows carrying >=1 defect", defects.pair_index.nunique(), 782)
    defect_counts = {
        "hub_pair": 693,
        "name_ambiguous": 54,
        "name_truncated": 53,
        "duplicate_unordered": 30,
        "implausible_coprescription": 21,
        "name_unresolvable": 17,
        "name_brand": 15,
        "same_class": 11,
        "name_nomenclature_inconsistent": 8,
    }
    obs_def = defects.defect_class.value_counts().to_dict()
    for cls, expected in defect_counts.items():
        check(f"defect class {cls}", int(obs_def.get(cls, 0)), expected)
    check("defect class same_ingredient absent (hypothesised defect not found)", int(obs_def.get("same_ingredient", 0)), 0)

    check("drug normalisation table rows", len(norm), 161)
    check(
        "names resolving exactly to an RxNorm ingredient",
        int((norm.resolution_status == "resolved_exact").sum()),
        152,
    )
    check(
        "predecessor-file degree, sevelamer (827 rows, pre-deduplication)",
        int(norm.loc[norm.original_name.map(_key) == "sevelamer", "degree"].iloc[0]),
        152,
    )
    check("predecessor-file degree sum == 2 x 827 rows", int(norm.degree.sum()), 1654)

    # -- 7. the headline benchmark result ---------------------------------
    check("benchmark replicates", len(bench), 20)
    check("benchmark columns", list(bench.columns), ["random", "curated", "deg_matched", "n_matched"])
    check("AUC vs random unlabelled negatives", float(bench["random"].mean()), 0.934, tol=0.0005)
    check("AUC vs curated negatives", float(bench["curated"].mean()), 0.947, tol=0.0005)
    check("AUC vs degree-matched curated negatives", float(bench["deg_matched"].mean()), 0.498, tol=0.0005)
    check("SD of AUC vs random negatives", float(bench["random"].std()), 0.007, tol=0.0005)
    check("SD of AUC vs curated negatives", float(bench["curated"].std()), 0.004, tol=0.0005)
    check("SD of AUC vs degree-matched negatives", float(bench["deg_matched"].std()), 0.004, tol=0.0005)
    check(
        "degree-matched AUC is within 0.01 of chance",
        bool(abs(float(bench["deg_matched"].mean()) - 0.5) <= 0.01),
        True,
    )
    check("positives retained per replicate by degree matching", float(bench.n_matched.mean()), 331.25, tol=0.05)
    check(
        "degree-matched retention is drawn from the 538-pair usable set",
        bool(bench.n_matched.max() <= 538),
        True,
    )
    # Fraction of the 538-pair positive pool with no degree-matched negative
    # available, across all 20 replicates.
    unmatched_frac = (538 - bench.n_matched) / 538
    check(
        "mean fraction of positives with no degree-matched negative available",
        float(unmatched_frac.mean()),
        0.384,
        tol=0.0005,
    )
    check(
        "SD of the fraction of positives with no degree-matched negative available",
        float(unmatched_frac.std()),
        0.021,
        tol=0.0005,
    )

    # -- 8. signal-detection file (the negative result) --------------------
    check("signal-detection rows", len(signal), 88679)
    check(
        "signal-detection columns",
        list(signal.columns),
        ["drug_a", "drug_b", "pair_class", "ae", "n_obs", "n_exp", "omega", "omega_025", "co_reports"],
    )
    sig_cand = signal[signal.pair_class == "candidate_negative"]
    sig_pos = signal[signal.pair_class == "positive_control"]
    check("signal-detection rows, candidate_negative arm", len(sig_cand), 84412)
    check("signal-detection rows, positive_control arm", len(sig_pos), 4267)
    sig_pairs = _pairset(signal)
    cand_pairs = _pairset(sig_cand)
    pos_pairs = _pairset(sig_pos)
    check("pairs carrying a signal-detection analysis", len(sig_pairs), 258)
    check("candidate-negative pairs analysed", len(cand_pairs), 246)
    check("positive-control pairs analysed", len(pos_pairs), 12)
    # The 12 positive controls are external established interacting pairs, not
    # members of the released candidate set, so only the candidate arm is
    # expected to be a subset of the shipped dataset.
    check(
        "every candidate-negative signal-detection pair is a pair shipped in the dataset",
        int(len(cand_pairs - _pairset(df))),
        0,
    )
    check(
        "candidate-negative signal-detection pairs analysed at T1_wellpowered",
        int(len(cand_pairs & _pairset(df[df.evidence_tier == "T1_wellpowered"]))),
        217,
    )
    check(
        "omega_025 <= omega for every row (the 2.5th percentile bounds the point estimate)",
        bool((signal.omega_025 <= signal.omega + 1e-9).all()),
        True,
    )
    # omega_025 is on a log2 scale, so a signal is omega_025 > 0.
    _sig = signal.assign(
        _p=[tuple(sorted((_key(a), _key(b)))) for a, b in zip(signal.drug_a, signal.drug_b)]
    )
    # Per-pair summaries: strongest signal, and the fraction of the pair's
    # tested adverse-event terms that flag.
    per_pair = _sig.groupby(["_p", "pair_class"]).agg(
        max_omega_025=("omega_025", "max"),
        n_terms=("ae", "size"),
        n_flagged=("omega_025", lambda s: int((s > 0).sum())),
    )
    per_pair["frac_flagged"] = per_pair.n_flagged / per_pair.n_terms
    per_pair = per_pair.reset_index()
    pos_pp = per_pair[per_pair.pair_class == "positive_control"]
    cand_pp = per_pair[per_pair.pair_class == "candidate_negative"]

    # (a) positive-control arm
    check(
        "positive controls flagged with >=1 disproportionality signal (12/12)",
        int((pos_pp.max_omega_025 > 0).sum()),
        12,
    )
    check(
        "signal rate among positive controls",
        float((pos_pp.max_omega_025 > 0).mean()),
        1.0,
        tol=1e-12,
    )
    # (b) candidate-negative arm
    check(
        "candidate negatives flagged with >=1 disproportionality signal (the negative result: 100%)",
        int((cand_pp.max_omega_025 > 0).sum()),
        246,
    )
    check(
        "signal rate among candidate negatives",
        float((cand_pp.max_omega_025 > 0).mean()),
        1.0,
        tol=1e-12,
    )

    # (c) between-group non-discrimination. AUC = U / (n_pos * n_neg).
    def _auc_p(a, b) -> tuple[float, float]:
        u, p = mannwhitneyu(a, b, alternative="two-sided")
        return float(u) / (len(a) * len(b)), float(p)

    auc_max, p_max = _auc_p(pos_pp.max_omega_025.values, cand_pp.max_omega_025.values)
    check("discrimination AUC, strongest signal per pair", auc_max, 0.577, tol=0.0005)
    check("Mann-Whitney p, strongest signal per pair", p_max, 0.367, tol=0.0005)
    check(
        "median strongest signal, positive controls",
        float(pos_pp.max_omega_025.median()),
        3.465,
        tol=0.0005,
    )
    check(
        "median strongest signal, candidate negatives",
        float(cand_pp.max_omega_025.median()),
        2.812,
        tol=0.0005,
    )

    # DEVIATION FROM THE PUBLISHED VALUES, ON THE RECORD.
    #
    # The manuscript and the prior release notes report AUC 0.633 (p = 0.120)
    # for this statistic. The corrected signal_detection_t1.csv yields
    # AUC 0.631775 (p = 0.123774), i.e. 0.632 (p = 0.124) to 3 dp. The
    # published constants are NOT reproducible from the shipped file and the
    # two checks below therefore assert the recomputed values, not 0.633/0.120.
    #
    # This is a change of asserted constant and is recorded rather than
    # absorbed. Evidence that the statistic itself is defined as intended and
    # that only the published AUC/p were off:
    #   * both MEDIANS of the same per-pair statistic reproduce exactly
    #     (positives 0.372402 -> 0.372, negatives 0.290297 -> 0.290), so the
    #     numerator (count of omega_025 > 0) and denominator (tested AE terms)
    #     match the published definition;
    #   * the companion strongest-signal statistic reproduces exactly on all
    #     four of its published constants (AUC 0.577, p 0.367, medians
    #     3.465 / 2.812);
    #   * eight alternative definitions were tested and none yields
    #     0.633/0.120 -- unique-AE denominator, `omega > 0` in place of
    #     `omega_025 > 0`, `omega_025 >= 0`, `n_obs > 0` and `n_exp >= 1`
    #     denominators, an `n_obs >= 3` filter, and restriction to AE terms
    #     shared by both arms (0.6365/0.1108, which is further from the
    #     published pair and breaks the medians) -- as were scipy's exact and
    #     asymptotic p-value methods (0.124821 exact, 0.123774 asymptotic).
    # The qualitative conclusion is unchanged: p > 0.05, so the two groups are
    # not discriminated on this statistic either.
    PUBLISHED_AUC_FRAC, PUBLISHED_P_FRAC = "0.633", "0.120"
    auc_frac, p_frac = _auc_p(pos_pp.frac_flagged.values, cand_pp.frac_flagged.values)
    check(
        "discrimination AUC, fraction of tested AE terms flagged "
        f"(recomputed; published {PUBLISHED_AUC_FRAC} not reproducible)",
        auc_frac,
        0.632,
        tol=0.0005,
    )
    check(
        "Mann-Whitney p, fraction of tested AE terms flagged "
        f"(recomputed; published {PUBLISHED_P_FRAC} not reproducible)",
        p_frac,
        0.124,
        tol=0.0005,
    )
    check(
        "fraction-flagged discrimination is still non-significant (the "
        "published conclusion survives the corrected constants)",
        bool(p_frac > 0.05),
        True,
    )
    check(
        "median fraction of terms flagged, positive controls",
        float(pos_pp.frac_flagged.median()),
        0.372,
        tol=0.0005,
    )
    check(
        "median fraction of terms flagged, candidate negatives",
        float(cand_pp.frac_flagged.median()),
        0.290,
        tol=0.0005,
    )

    # -- 9. reported but not derivable from the shipped files -------------
    skip(
        "DDInter 2.0 cross-check (588 pairs with both drugs present, 0 flagged)",
        "requires the DDInter 2.0 release, which is third-party and not redistributed here; "
        "no DDInter column is shipped in antiddi_v2_dataset.csv",
    )
    skip(
        "Lexicomp / Micromedex re-screening",
        "not performed for this release; no institutional access. v1 screening stands as "
        "historical provenance only (see README and DISCLOSURE_retraction.md)",
    )

    # -- report ------------------------------------------------------------
    width = max(len(n) for n, *_ in RESULTS) + 2
    failures = 0
    for name, ok, expected, observed in RESULTS:
        if ok:
            line = f"PASS  {name:<{width}}"
            if args.verbose:
                line += f" expected={expected}  observed={observed}"
            print(line)
        else:
            failures += 1
            print(f"FAIL  {name:<{width}} expected={expected}  observed={observed}")
    for name, reason in SKIPS:
        print(f"SKIP  {name}\n        reason: {reason}")

    print()
    print(f"{len(RESULTS)} quantities checked — {len(RESULTS) - failures} passed, {failures} failed, {len(SKIPS)} skipped")
    if failures:
        print("VALIDATION FAILED")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
