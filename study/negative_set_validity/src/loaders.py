"""External benchmark loaders with explicit schemas and CRESCENDDI pair aggregation."""
from __future__ import annotations
import os,glob
import pandas as pd
DATA=os.environ.get('DDI_DATA_DIR','data')
def _p(*x): return os.path.join(DATA,*x)
def _exists(pattern):
    hits=sorted(glob.glob(_p(pattern))); return hits[0] if hits else None

def _drug_pair_cols(df):
    norm={c.lower().strip():c for c in df.columns}
    for a,b in [('drug_1_concept_name','drug_2_concept_name'),('drug1','drug2'),('drug_1','drug_2'),('drug_a','drug_b')]:
        if a in norm and b in norm: return norm[a],norm[b]
    drugcols=[c for c in df.columns if 'drug' in c.lower() and ('concept' in c.lower() or 'name' in c.lower())]
    if len(drugcols)>=2: return drugcols[0],drugcols[1]
    raise ValueError(f'Could not identify two drug columns: {list(df.columns)}')

def _pairs_df(df):
    a,b=_drug_pair_cols(df); out=set()
    for x,y in zip(df[a],df[b]):
        if pd.isna(x) or pd.isna(y): continue
        x=str(x).strip().lower(); y=str(y).strip().lower()
        if x and y and x!=y: out.add(tuple(sorted((x,y))))
    return out

def load_crescenddi():
    pos=_exists('crescenddi/*Positive*Controls*.xlsx'); neg=_exists('crescenddi/*Negative*Controls*.xlsx')
    if not pos: return None
    P=_pairs_df(pd.read_excel(pos)); N=_pairs_df(pd.read_excel(neg)) if neg else set()
    N=N-P
    return sorted(P),sorted(N),'CRESCENDDI_pairlevel'

def load_biosnap():
    f=_exists('biosnap/*.tsv') or _exists('biosnap/*.txt') or _exists('biosnap/*.csv')
    if not f: return None
    d=pd.read_csv(f,sep=',' if f.lower().endswith('.csv') else '\t',header=None,dtype=str)
    E=[]
    for x,y in zip(d.iloc[:,0],d.iloc[:,1]):
        x=str(x).strip(); y=str(y).strip()
        if x and y and x!=y: E.append(tuple(sorted((x,y))))
    return sorted(set(E)),None,'BioSNAP_ChCh'

BENCHMARKS={'CRESCENDDI_pairlevel':load_crescenddi,'BioSNAP_ChCh':load_biosnap}
def available(only=None):
    wanted=set(only) if only else set(BENCHMARKS); out={}
    for k,fn in BENCHMARKS.items():
        if k not in wanted: continue
        try: r=fn()
        except Exception as e: print(f'  [skip] {k}: {type(e).__name__}: {e}'); r=None
        if r and len(r[0])>=50:
            out[k]=r; print(f'  [ok] {k}: {len(r[0])} positive pairs'+(f', {len(r[1])} curated negative pairs' if r[1] else ''))
        else: print(f'  [--] {k}: unavailable/too small')
    return out
