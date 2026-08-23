import hashlib, json, math, os
import numpy as np
from scipy.stats import spearmanr


def sha_seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode('utf-8')).digest()[:8], 'big') % (2**32 - 1)


def stable_order(scores, ids):
    scores=np.asarray(scores, dtype=float)
    ids=np.asarray(ids)
    # primary: descending score, secondary: stable string id
    return np.lexsort((ids.astype(str), -scores))


def ridi_from_scores(a, b, ids, k):
    oa=stable_order(a, ids)[:k]
    ob=stable_order(b, ids)[:k]
    sa=set(np.asarray(ids)[oa].astype(str)); sb=set(np.asarray(ids)[ob].astype(str))
    return 1.0 - len(sa & sb)/len(sa | sb)


def rank_spearman(a,b):
    return float(spearmanr(a,b).statistic)


def bootstrap_mean_ci(values, n_boot=10000, seed=20260823):
    x=np.asarray(values, dtype=float)
    rng=np.random.default_rng(seed)
    n=len(x)
    means=np.empty(n_boot, dtype=float)
    # chunk to avoid large allocations
    for start in range(0,n_boot,1000):
        end=min(start+1000,n_boot)
        idx=rng.integers(0,n,size=(end-start,n))
        means[start:end]=x[idx].mean(axis=1)
    return [float(np.quantile(means,0.025)), float(np.quantile(means,0.975))]


def ndcg_at_k(relevance, order, k):
    rel=np.asarray(relevance, dtype=int)[order[:k]]
    gains=rel/np.log2(np.arange(2,k+2))
    dcg=float(gains.sum())
    ideal_n=min(int(np.asarray(relevance).sum()),k)
    if ideal_n==0: return float('nan')
    idcg=float((np.ones(ideal_n)/np.log2(np.arange(2,ideal_n+2))).sum())
    return dcg/idcg


def recall_at_k(relevance, order, k):
    rel=np.asarray(relevance, dtype=int)
    denom=int(rel.sum())
    if denom==0: return float('nan')
    return float(rel[order[:k]].sum()/denom)


def write_json(path, obj):
    with open(path,'w',encoding='utf-8') as f: json.dump(obj,f,indent=2,sort_keys=True)
