from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from .core import audit_scores
from .report import render_markdown_report


def _read(path: str, id_col: str, score_col: str):
    df = pd.read_csv(path)
    if id_col not in df or score_col not in df:
        raise SystemExit(f"Missing required columns in {path}: {id_col}, {score_col}")
    return df[[id_col, score_col]].copy()


def main() -> None:
    ap = argparse.ArgumentParser(prog="ridi-audit", description="Audit decision identity under a representation intervention")
    ap.add_argument("--version", action="version", version="ridi-audit 0.2.0")
    sp = ap.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("compare", help="Compare two aligned candidate-score tables")
    c.add_argument("--r0", required=True)
    c.add_argument("--r1", required=True)
    c.add_argument("--id-col", default="id")
    c.add_argument("--score-col", default="score")
    c.add_argument("--k", nargs="+", type=int, required=True)
    c.add_argument("--out", default="-", help="JSON output path, or - for stdout")
    c.add_argument("--report", default=None, help="Optional Markdown audit report path")
    args = ap.parse_args()

    a = _read(args.r0, args.id_col, args.score_col).rename(columns={args.score_col: "score_r0"})
    b = _read(args.r1, args.id_col, args.score_col).rename(columns={args.score_col: "score_r1"})
    m = a.merge(b, on=args.id_col, how="outer", validate="one_to_one", indicator=True)
    if not (m["_merge"] == "both").all():
        raise SystemExit("R0 and R1 must contain the same candidate identities")
    m = m.sort_values(args.id_col, kind="mergesort")

    res = audit_scores(
        m[args.id_col].astype(str).to_numpy(),
        m.score_r0.to_numpy(),
        m.score_r1.to_numpy(),
        args.k,
    )
    text = json.dumps(res, indent=2)
    if args.out == "-":
        print(text)
    else:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    if args.report:
        Path(args.report).write_text(render_markdown_report(res), encoding="utf-8")


if __name__ == "__main__":
    main()
