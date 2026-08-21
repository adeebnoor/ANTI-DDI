# OpenKG operational correction addendum — before outcome availability
Date: 2026-08-21
Parent: OPENKG_IMPLEMENTATION_ADDENDUM_20260821.md

## Trigger
The first GitHub Actions execution downloaded the official ReVerb45K files and completed score computation, but terminated inside the bijective negative-control routine before writing `openkg_ridi_metrics.csv`, `negative_control.csv`, `manifest.json`, or `gate_summary.json`.

The traceback was a `KeyError` for a surface alias that existed in the full candidate alias universe but was absent from the R0 training adjacency after held-out identity-pair removal. No final RIDI outcome table or gate result existed at the time of this correction.

## Correction
1. Define the negative-control bijection over the **full operational alias universe**: all R0 training nodes plus every surface alias attached to any gold identity in the frozen candidate universe. Isolated aliases therefore receive a relabeled identity even if they have no training adjacency.
2. Relabel only existing graph edges; isolated aliases remain isolated under the bijection.
3. Keep the same candidate universe, split, seeds, scoring methods, aggregation rule, k values, tie protocol, bootstrap protocol, and success gate.
4. Add `set -o pipefail` to the GitHub Actions execution step so any future Python failure propagates through `tee` and fails the step immediately.

## Scientific impact
None intended. This correction changes only the implementation of the exact invariance control and CI error propagation. It does not alter any scientific endpoint or representation comparison.

Locked SHA-256: d0c0ca7ae50ae0223385c507463bffa1cc54b41f6d6e39b47e1dd4b4c168beab
