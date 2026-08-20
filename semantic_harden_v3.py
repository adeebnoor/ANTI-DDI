#!/usr/bin/env python3
"""Apply conservative v3.0.1 knowledge-state semantics after build_v3.py.

T1/T2 encode higher observation opportunity under the resource rules; they are
benchmark candidates, not direct clinical proof of non-interaction. Direct
human/regulatory anchoring is carried separately.
"""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
FULL=DATA/'antiddi_v3_dataset.csv'
BENCH=DATA/'antiddi_v3_benchmark.csv'

for path in (FULL,BENCH):
    df=pd.read_csv(path)
    mask=df['evidence_tier'].isin(['T1_wellpowered','T2_moderate'])
    df.loc[mask,'knowledge_state']='ANTI_DDI_CANDIDATE_HIGHER_SUPPORT'
    df.loc[mask,'recommended_use']='DEFAULT_BENCHMARK_CANDIDATE'
    df.to_csv(path,index=False)

print('Applied conservative Anti-DDI v3.0.1 candidate semantics.')
