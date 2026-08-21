#!/usr/bin/env bash
set -euo pipefail
SEEDS="${SEEDS:-20}"
export DDI_DATA_DIR="${DDI_DATA_DIR:-data}"
export DDI_OUT_DIR="${DDI_OUT_DIR:-results_external}"
mkdir -p "$DDI_OUT_DIR"
python src/experiment.py --seeds "$SEEDS" --benchmarks CRESCENDDI_pairlevel,BioSNAP_ChCh
python src/analysis.py | tee "$DDI_OUT_DIR/ANALYSIS_LOG.txt"
