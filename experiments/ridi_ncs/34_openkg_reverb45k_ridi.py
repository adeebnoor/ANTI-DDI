#!/usr/bin/env python3
"""Prospectively locked non-biomedical RIDI replication on ReVerb45K.

R0: normalized surface-form noun phrases as operational nodes.
R1: gold Freebase IDs for subject/object noun phrases; relation phrases unchanged.
Source assertions are frozen; canonicalization only changes operational node identity.

Primary deterministic families: Jaccard, Adamic-Adar, Resource Allocation.
Secondary spectral family: truncated SVD adjacency reconstruction.

The common decision universe is defined on gold identity pairs. For R0, an identity-pair
score is the maximum score across its observed surface aliases, preventing duplicate alias
candidates from inflating top-k turnover.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, random, sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Set

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy.stats import spearmanr

LOCK_SEED = 20260821
SPLIT_FRACTION = 0.20
NEGATIVE_RATIO = 5
SVD_RANK = 64
K_VALUES = (10, 50, 100, 500, 1000)
TIE_REPS = 200
BOOT_REPS = 200


def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()


def norm_np(x: str) -> str:
    return ' '.join(str(x).strip().lower().split())


def load_jsonl(paths: List[Path]):
    triples=[]
    bad=0
    for p in paths:
        with p.open('r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try: o=json.loads(line)
                except Exception:
                    bad += 1; continue
                try:
                    raw=o.get('triple_norm') or o['triple']
                    s=norm_np(raw[0]); r=norm_np(raw[1]); t=norm_np(raw[2])
                    gl=o.get('true_link',{}) or {}
                    gs=str(gl.get('subject') or '').strip(); gt=str(gl.get('object') or '').strip()
                    if not s or not t or not gs or not gt: continue
                    triples.append((s,r,t,gs,gt,int(o.get('_id',len(triples)))))
                except Exception:
                    bad += 1
    return triples,bad


def canon_pair(a,b):
    return (a,b) if a < b else (b,a)


def hashed_holdout(pair):
    s=f'{LOCK_SEED}|{pair[0]}|{pair[1]}'.encode()
    u=int(hashlib.sha256(s).hexdigest()[:16],16)/2**64
    return u < SPLIT_FRACTION


def build_data(triples):
    aliases=defaultdict(set); all_pairs=set(); pair_rows=defaultdict(list)
    for s,r,t,gs,gt,tid in triples:
        if gs==gt: continue
        aliases[gs].add(s); aliases[gt].add(t)
        p=canon_pair(gs,gt)
        all_pairs.add(p); pair_rows[p].append((s,t,r,tid))
    train_pairs={p for p in all_pairs if not hashed_holdout(p)}
    test_pairs={p for p in all_pairs if hashed_holdout(p)}
    train_ids=set(x for p in train_pairs for x in p)
    test_pairs={p for p in test_pairs if p[0] in train_ids and p[1] in train_ids}
    return aliases, pair_rows, train_pairs, test_pairs, all_pairs


def sample_negatives(entities: List[str], all_pairs: Set[Tuple[str,str]], n: int):
    rng=random.Random(LOCK_SEED)
    out=set(); attempts=0; cap=max(100000, n*100)
    while len(out)<n and attempts<cap:
        a,b=rng.sample(entities,2); p=canon_pair(a,b); attempts+=1
        if p in all_pairs or p in out: continue
        out.add(p)
    if len(out)<n: raise RuntimeError(f'Could only sample {len(out)} / {n} negatives')
    return out


def build_graphs(pair_rows, train_pairs):
    adj0=defaultdict(set); adj1=defaultdict(set)
    for p in train_pairs:
        a,b=p; adj1[a].add(b); adj1[b].add(a)
        for s,t,r,tid in pair_rows[p]:
            if s==t: continue
            adj0[s].add(t); adj0[t].add(s)
    return adj0,adj1


def local_score(adj, u, v, method):
    nu=adj.get(u,set()); nv=adj.get(v,set())
    inter=nu & nv
    if method=='jaccard':
        den=len(nu|nv); return len(inter)/den if den else 0.0
    if method=='aa':
        z=0.0
        for w in inter:
            d=len(adj.get(w,set()))
            if d>1: z += 1.0/math.log(d)
        return z
    if method=='ra':
        return sum(1.0/len(adj.get(w,set())) for w in inter if len(adj.get(w,set()))>0)
    raise ValueError(method)


def score_identity_pair_local(adj0, adj1, aliases, p, method):
    a,b=p
    s1=local_score(adj1,a,b,method)
    vals=[local_score(adj0,x,y,method) for x in aliases[a] for y in aliases[b]]
    s0=max(vals) if vals else 0.0
    return s0,s1


def svd_embeddings(adj, rank, seed):
    nodes=sorted(adj)
    idx={n:i for i,n in enumerate(nodes)}
    rows=[]; cols=[]
    for u,vs in adj.items():
        i=idx[u]
        for v in vs:
            j=idx.get(v)
            if j is not None:
                rows.append(i); cols.append(j)
    A=sparse.csr_matrix((np.ones(len(rows),dtype=np.float32),(rows,cols)),shape=(len(nodes),len(nodes)))
    k=max(2,min(rank, max(2, min(A.shape)-2)))
    svd=TruncatedSVD(n_components=k, random_state=seed, algorithm='randomized', n_iter=7)
    X=svd.fit_transform(A)
    C=svd.components_
    return idx,X,C


def svd_pair_score(idx,X,C,u,v):
    if u not in idx or v not in idx: return 0.0
    iu,iv=idx[u],idx[v]
    return float(0.5*(np.dot(X[iu],C[:,iv]) + np.dot(X[iv],C[:,iu])))


def score_identity_pair_svd(idx0,X0,C0,idx1,X1,C1,aliases,p):
    a,b=p
    s1=svd_pair_score(idx1,X1,C1,a,b)
    vals=[svd_pair_score(idx0,X0,C0,x,y) for x in aliases[a] for y in aliases[b]]
    return (max(vals) if vals else 0.0), s1


def topk_set(keys, scores, k):
    k=min(k,len(keys)); order=np.argsort(-np.asarray(scores), kind='mergesort')[:k]
    return {keys[i] for i in order}


def ridi(a,b):
    u=a|b
    return 0.0 if not u else 1.0-len(a&b)/len(u)


def tie_robust_bounds(keys,s0,s1,k):
    out={}
    for label,s in [('r0',np.asarray(s0)),('r1',np.asarray(s1))]:
        kk=min(k,len(s)); order=np.argsort(-s, kind='mergesort'); cutoff=s[order[kk-1]]
        strict=int(np.sum(s>cutoff)); tied=int(np.sum(s==cutoff))
        out[f'{label}_strict_above']=strict; out[f'{label}_boundary_ties']=tied; out[f'{label}_cutoff_score']=float(cutoff)
    return out


def _top_indices(scores, maxk, tie=None):
    scores=np.asarray(scores)
    n=len(scores); maxk=min(maxk,n)
    if tie is None:
        if maxk==n:
            cand=np.arange(n)
        else:
            cand=np.argpartition(scores,-maxk)[-maxk:]
        return cand[np.lexsort((cand,-scores[cand]))]
    return np.lexsort((tie,-scores))[:maxk]


def eval_method(name,keys,labels,s0,s1):
    rows=[]; s0=np.asarray(s0,dtype=float); s1=np.asarray(s1,dtype=float)
    rho=float(spearmanr(s0,s1).statistic) if len(set(s0))>1 and len(set(s1))>1 else float('nan')
    auc0=roc_auc_score(labels,s0); auc1=roc_auc_score(labels,s1); ap0=average_precision_score(labels,s0); ap1=average_precision_score(labels,s1)
    feasible=[k for k in K_VALUES if k<=len(keys)]; maxk=max(feasible)
    base0=_top_indices(s0,maxk); base1=_top_indices(s1,maxk)
    tie_vals={k:[] for k in feasible}; rng=np.random.default_rng(LOCK_SEED+101)
    for rep in range(TIE_REPS):
        tie=rng.random(len(keys))
        o0=_top_indices(s0,maxk,tie); o1=_top_indices(s1,maxk,tie)
        for k in feasible:
            tie_vals[k].append(ridi({keys[i] for i in o0[:k]},{keys[i] for i in o1[:k]}))
    boot_vals={k:[] for k in feasible}; rng=np.random.default_rng(LOCK_SEED+202)
    n=len(keys)
    for rep in range(BOOT_REPS):
        ix=rng.integers(0,n,n)
        b0=s0[ix]; b1=s1[ix]; mk=min(maxk,len(ix))
        if mk==len(ix):
            r0=np.argsort(-b0,kind='mergesort'); r1=np.argsort(-b1,kind='mergesort')
        else:
            c0=np.argpartition(b0,-mk)[-mk:]; c1=np.argpartition(b1,-mk)[-mk:]
            r0=c0[np.argsort(-b0[c0],kind='mergesort')]; r1=c1[np.argsort(-b1[c1],kind='mergesort')]
        o0=ix[r0]; o1=ix[r1]
        for k in feasible:
            boot_vals[k].append(ridi({keys[i] for i in o0[:k]},{keys[i] for i in o1[:k]}))
    for k in feasible:
        t0={keys[i] for i in base0[:k]}; t1={keys[i] for i in base1[:k]}
        tq=np.quantile(tie_vals[k],[0.025,0.5,0.975]); bq=np.quantile(boot_vals[k],[0.025,0.5,0.975])
        x={'method':name,'k':k,'ridi':ridi(t0,t1),'spearman':rho,'auroc_r0':auc0,'auroc_r1':auc1,'ap_r0':ap0,'ap_r1':ap1,'topk_intersection':len(t0&t1),
           'tie_ridi_q025':float(tq[0]),'tie_ridi_median':float(tq[1]),'tie_ridi_q975':float(tq[2]),
           'boot_ridi_q025':float(bq[0]),'boot_ridi_median':float(bq[1]),'boot_ridi_q975':float(bq[2])}
        x.update(tie_robust_bounds(keys,s0,s1,k)); rows.append(x)
    return rows


def negative_control(adj0, aliases, keys):
    # Fixed bijection over the full operational alias universe, including aliases
    # that become isolated after held-out identity-pair removal.
    old=sorted(set(adj0) | {x for vs in aliases.values() for x in vs})
    perm=sorted(old,key=lambda x:hashlib.sha256(f'perm|{LOCK_SEED}|{x}'.encode()).hexdigest())
    mp={o:f'P{j:08d}' for j,o in enumerate(perm)}
    adp=defaultdict(set)
    for u,vs in adj0.items():
        pu=mp[u]
        for v in vs: adp[pu].add(mp[v])
    result=[]
    for method in ('jaccard','aa','ra'):
        base=[]; rel=[]
        for a,b in keys:
            vals=[local_score(adj0,x,y,method) for x in aliases[a] for y in aliases[b]]
            vals2=[local_score(adp,mp[x],mp[y],method) for x in aliases[a] for y in aliases[b]]
            base.append(max(vals) if vals else 0.0); rel.append(max(vals2) if vals2 else 0.0)
        maxdiff=float(np.max(np.abs(np.asarray(base)-np.asarray(rel)))) if base else 0.0
        for k in K_VALUES:
            if k<=len(keys): result.append({'method':method,'k':k,'ridi':ridi(topk_set(keys,base,k),topk_set(keys,rel,k)),'max_abs_score_diff':maxdiff})
    return result


def exposure_features(aliases, keys, s0, s1):
    rows=[]
    for p,a,b in zip(keys,s0,s1):
        e=(len(aliases[p[0]])-1)+(len(aliases[p[1]])-1)
        rows.append({'u':p[0],'v':p[1],'alias_exposure':e,'alias_product':len(aliases[p[0]])*len(aliases[p[1]]),'abs_score_delta':abs(a-b)})
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--valid',required=True); ap.add_argument('--test',required=True); ap.add_argument('--out',required=True)
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    paths=[Path(args.valid),Path(args.test)]
    triples,bad=load_jsonl(paths)
    aliases,pair_rows,train_pairs,test_pairs,all_pairs=build_data(triples)
    entities=sorted({x for p in train_pairs for x in p})
    neg=sample_negatives(entities,all_pairs,min(len(test_pairs)*NEGATIVE_RATIO,100000))
    keys=sorted(test_pairs)+sorted(neg); labels=np.array([1]*len(test_pairs)+[0]*len(neg),dtype=np.int8)
    adj0,adj1=build_graphs(pair_rows,train_pairs)
    metrics=[]
    for method in ('jaccard','aa','ra'):
        s0=[];s1=[]
        for p in keys:
            a,b=score_identity_pair_local(adj0,adj1,aliases,p,method);s0.append(a);s1.append(b)
        metrics.extend(eval_method(method,keys,labels,s0,s1))
        pd.DataFrame(exposure_features(aliases,keys,s0,s1)).to_csv(out/f'exposure_{method}.csv',index=False)
    idx0,X0,C0=svd_embeddings(adj0,SVD_RANK,LOCK_SEED); idx1,X1,C1=svd_embeddings(adj1,SVD_RANK,LOCK_SEED)
    s0=[];s1=[]
    for p in keys:
        a,b=score_identity_pair_svd(idx0,X0,C0,idx1,X1,C1,aliases,p);s0.append(a);s1.append(b)
    metrics.extend(eval_method('svd64',keys,labels,s0,s1))
    pd.DataFrame(exposure_features(aliases,keys,s0,s1)).to_csv(out/'exposure_svd64.csv',index=False)
    negctl=negative_control(adj0,aliases,keys)
    pd.DataFrame(metrics).to_csv(out/'openkg_ridi_metrics.csv',index=False)
    pd.DataFrame(negctl).to_csv(out/'negative_control.csv',index=False)
    pd.DataFrame([{'u':a,'v':b,'label':int(y)} for (a,b),y in zip(keys,labels)]).to_csv(out/'candidate_universe.csv',index=False)
    manifest={
      'protocol':'OPENKG_PROSPECTIVE_LOCK_20260821','seed':LOCK_SEED,'split_fraction':SPLIT_FRACTION,
      'negative_ratio':NEGATIVE_RATIO,'svd_rank':SVD_RANK,'n_input_triples':len(triples),'n_bad_lines':bad,
      'n_gold_identities':len(aliases),'n_train_identity_pairs':len(train_pairs),'n_test_identity_pairs':len(test_pairs),
      'n_negative_pairs':len(neg),'n_candidate_pairs':len(keys),'n_r0_alias_nodes':len(adj0),'n_r1_nodes':len(adj1),
      'input_sha256':{p.name:sha256_file(p) for p in paths},
      'methods':['jaccard','aa','ra','svd64'],'families':{'local':['jaccard','aa','ra'],'spectral':['svd64']},'k_values':list(K_VALUES),
      'tie_reps':TIE_REPS,'bootstrap_reps':BOOT_REPS,
      'r0_aggregation':'max score across aliases for each gold identity pair','r1':'gold Freebase identity graph',
    }
    with (out/'manifest.json').open('w') as f: json.dump(manifest,f,indent=2)
    m=pd.DataFrame(metrics)
    nc=pd.DataFrame(negctl)
    positive_ci=set(m.loc[m.boot_ridi_q025>0,'method'].unique())
    local_positive=bool(positive_ci & {'jaccard','aa','ra'})
    spectral_positive='svd64' in positive_ci
    tie_survives=set(m.loc[m.tie_ridi_q025>0,'method'].unique())
    gate={
      'negative_control_exact_zero': bool((nc['ridi']==0).all() and (nc['max_abs_score_diff']<1e-12).all()),
      'methods_with_bootstrap_ci_above_zero': sorted(positive_ci),
      'methods_with_tie_robust_q025_above_zero': sorted(tie_survives),
      'independent_family_gate_local_plus_spectral': bool(local_positive and spectral_positive),
      'max_ridi_by_method': {x:float(g.ridi.max()) for x,g in m.groupby('method')},
      'performance_delta_auroc_by_method': {x:float((g.auroc_r1-g.auroc_r0).iloc[0]) for x,g in m.groupby('method')},
    }
    with (out/'gate_summary.json').open('w') as f: json.dump(gate,f,indent=2)
    print(json.dumps({'manifest':manifest,'gate':gate},indent=2))

if __name__=='__main__': main()
