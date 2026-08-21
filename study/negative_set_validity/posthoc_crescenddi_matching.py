from pathlib import Path
import os,sys,json
from collections import defaultdict
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'src'))
from loaders import load_crescenddi
from graphs import Graph
from models import REGISTRY
from protocols import _bin_map
OUT=ROOT/'results_posthoc_crescenddi'; OUT.mkdir(exist_ok=True)

def split(g,rng,test_frac=.2):
    perm=rng.permutation(len(g.edges)); nt=max(1,int(test_frac*len(g.edges)))
    return [g.edges[i] for i in perm[nt:]],[g.edges[i] for i in perm[:nt]]

def sig(pair,bmap):
    a,b=pair; return tuple(sorted((bmap[a],bmap[b])))

def auc(sp,sn):
    y=np.r_[np.ones(len(sp)),np.zeros(len(sn))]
    return float(roc_auc_score(y,np.r_[sp,sn]))

def main(seeds=20):
    P,N,_=load_crescenddi(); g=Graph(P,'CRESCENDDI_pairlevel'); curated=[p for p in N if p[0] in g.idx and p[1] in g.idx and p not in g.eset]
    rows=[]; cover=[]
    for s in range(seeds):
        rng=np.random.default_rng(100000+s); train,test_pos=split(g,rng)
        M=g.adjacency(train); deg=M.sum(1); train_deg={n:float(deg[g.idx[n]]) for n in g.nodes}; bmap=_bin_map(g.nodes,train_deg)
        groups=defaultdict(list)
        for p in curated: groups[sig(p,bmap)].append(p)
        # Shuffle each signature pool deterministically, then consume without replacement.
        mrng=np.random.default_rng(700000+s)
        for k in list(groups):
            arr=groups[k]; order=mrng.permutation(len(arr)); groups[k]=[arr[int(i)] for i in order]
        pos_m=[]; neg_m=[]
        for p in test_pos:
            k=sig(p,bmap)
            if groups.get(k): pos_m.append(p); neg_m.append(groups[k].pop())
        n=len(pos_m); coverage=n/len(test_pos)
        if n<100:
            cover.append(dict(seed=s,n_test_pos=len(test_pos),n_matched=n,coverage=coverage,status='DROPPED_LT100')); continue
        # Equal-size random curated contrast evaluated on the identical matched positive set.
        rrng=np.random.default_rng(800000+s); ridx=rrng.permutation(len(curated))[:n]; neg_r=[curated[int(i)] for i in ridx]
        ctx=dict(M=M,deg=deg,idx=g.idx,cache={})
        for mname,mfn in REGISTRY.items():
            sp=mfn(ctx,pos_m); snm=mfn(ctx,neg_m); snr=mfn(ctx,neg_r)
            rows.append(dict(seed=s,model=mname,n=n,coverage=coverage,auc_random_curated_same_pos=auc(sp,snr),auc_curated_degree_matched=auc(sp,snm),delta_random_minus_matched=auc(sp,snr)-auc(sp,snm)))
        cover.append(dict(seed=s,n_test_pos=len(test_pos),n_matched=n,coverage=coverage,status='OK'))
    d=pd.DataFrame(rows); c=pd.DataFrame(cover); d.to_csv(OUT/'posthoc_model_auc.csv',index=False); c.to_csv(OUT/'posthoc_coverage.csv',index=False)
    summ=d.groupby('model').agg(n_seeds=('seed','nunique'),mean_n=('n','mean'),mean_coverage=('coverage','mean'),auc_random=('auc_random_curated_same_pos','mean'),sd_random=('auc_random_curated_same_pos','std'),auc_matched=('auc_curated_degree_matched','mean'),sd_matched=('auc_curated_degree_matched','std'),delta=('delta_random_minus_matched','mean')).reset_index()
    summ.to_csv(OUT/'posthoc_summary.csv',index=False)
    print(c.to_string(index=False)); print('\n',summ.to_string(index=False))
    assert (c.status=='OK').all(), 'At least one seed had <100 matched curated negatives'
if __name__=='__main__': main()
