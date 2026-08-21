from __future__ import annotations
import argparse,os,sys
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score
sys.path.insert(0,os.path.dirname(__file__))
from graphs import Graph,structural_report
import protocols as PR
from models import REGISTRY
from loaders import available
OUT=os.environ.get('DDI_OUT_DIR','results_external'); os.makedirs(OUT,exist_ok=True)

def split(g,rng,test_frac=0.2):
    perm=rng.permutation(len(g.edges)); nt=max(1,int(test_frac*len(g.edges)))
    return [g.edges[i] for i in perm[nt:]],[g.edges[i] for i in perm[:nt]]

def run_e2(g,curated,seeds,test_frac=0.2,min_neg=100):
    protos=dict(PR.BASE_PROTOCOLS)
    if curated: protos['P4_curated']=PR.make_p4_curated(curated)
    rows=[]
    for s in seeds:
        split_rng=np.random.default_rng(100000+s); train,test_pos=split(g,split_rng,test_frac)
        M=g.adjacency(train); deg=M.sum(1); train_deg={n:float(deg[g.idx[n]]) for n in g.nodes}; cache={}
        for pi,(pname,fn) in enumerate(protos.items()):
            neg_rng=np.random.default_rng(200000+1000*s+pi); neg=fn(g,train_deg,test_pos,neg_rng,len(test_pos))
            if len(neg)<min_neg:
                rows.append(dict(benchmark=g.name,seed=s,protocol=pname,model='__PROTOCOL__',n_pos=len(test_pos),n_neg=len(neg),auc=np.nan,status='DROPPED_LT100')); continue
            tp=test_pos[:len(neg)] if len(neg)<len(test_pos) else test_pos
            ctx=dict(M=M,deg=deg,idx=g.idx,cache=cache)
            for mname,mfn in REGISTRY.items():
                sp=mfn(ctx,tp); sn=mfn(ctx,neg); y=np.r_[np.ones(len(sp)),np.zeros(len(sn))]
                auc=float(roc_auc_score(y,np.r_[sp,sn]))
                rows.append(dict(benchmark=g.name,seed=s,protocol=pname,model=mname,n_pos=len(sp),n_neg=len(sn),auc=auc,status='OK'))
        print(f'    seed {s} done',flush=True)
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seeds',type=int,default=20); ap.add_argument('--test-frac',type=float,default=.2); ap.add_argument('--benchmarks',default=''); a=ap.parse_args()
    only=[x for x in a.benchmarks.split(',') if x] or None; print('=== discovering benchmarks ==='); bms=available(only); reps=[]; allr=[]
    for _,(edges,cur,nm) in bms.items():
        g=Graph(edges,nm)
        if len(g.edges)<200 or g.N<20: continue
        reps.append(structural_report(g)); print('  running',nm,len(g.edges),'edges',g.N,'nodes'); allr.append(run_e2(g,cur,range(a.seeds),a.test_frac))
    if not allr: raise SystemExit('No usable benchmarks')
    pd.DataFrame(reps).to_csv(f'{OUT}/E1_structural_audit.csv',index=False); pd.concat(allr,ignore_index=True).to_csv(f'{OUT}/E2_auc.csv',index=False)
if __name__=='__main__': main()
