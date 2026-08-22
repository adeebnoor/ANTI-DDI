#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

SALT='RTXKG2-20260818-GraphSAGE-v1'; KS=(100,500,1000)
SEEDS=[355092268,1972696080,1590711264,1745982372,1113956884,734518037,1017280056,54477576,202245501,871610103,1739075335,404365195,1603643707,1173720350,1263375671,1531572456]
A=SEEDS[:8];B=SEEDS[8:];MS=(1,2,4,8);LOCK_LABEL='RIDI-NATURE-GRAPHSAGE-ATTRIBUTION-v1'
BOOT_SEED=int(hashlib.sha256((LOCK_LABEL+'|bootstrap').encode()).hexdigest()[:16],16)%(2**32)
EXPECTED_QUERY_STRUCTURE_SHA='1291fa56e9074cbf41589b3e74f4fbc40687419ed44a7bb9800e9340e83e400e'

def hval(s):return hashlib.sha256(s.encode()).hexdigest()
def sha256_file(p,chunk=8*1024*1024):
 h=hashlib.sha256();f=open(p,'rb')
 while True:
  b=f.read(chunk)
  if not b:break
  h.update(b)
 f.close();return h.hexdigest()

def read_queries(path):
 q=defaultdict(list)
 with gzip.open(path,'rt',encoding='utf-8',newline='') as f:
  r=csv.DictReader(f,delimiter='\t')
  for row in r:q[row['query_raw_chem']].append(row['candidate_raw_chem'])
 return dict(q)
def read_raw_to_r1(path,relevant):
 d={}
 with gzip.open(path,'rt',encoding='utf-8',newline='') as f:
  r=csv.DictReader(f,delimiter='\t')
  for row in r:
   if row['raw_chem'] in relevant:d[row['raw_chem']]=row['primary_chem']
 return d

def universe_offsets(freeze):
 queries=read_queries(freeze/'chem_disease_query_candidates.tsv.gz');relevant={x for q,cs in queries.items() for x in ([q]+cs)};m=read_raw_to_r1(freeze/'chem_disease_frozen_edges.tsv.gz',relevant);meta=[];off=0;uh=hashlib.sha256()
 for q,cands in sorted(queries.items()):
  qg=m.get(q,q);groups=sorted({m.get(c,c) for c in cands if m.get(c,c)!=qg});n=len(groups)
  for g in groups:uh.update(q.encode()+b'\t'+g.encode()+b'\n')
  meta.append((q,off,n,groups));off+=n
 return meta,off,uh.hexdigest()

def topk_from_mean(meanvec,meta,k):
 out=[]
 for q,off,n,groups in meta:
  vals=meanvec[off:off+n]
  order=sorted(range(n),key=lambda i:(-float(vals[i]),hval(f'{SALT}|tie|{groups[i]}')))
  out.append(set(groups[i] for i in order[:k]) if n>=k else None)
 return out

def ridi_sets(a,b):return 1.0-len(a&b)/len(a|b)
def mean_vec(store,seeds,arm):return np.mean(np.stack([store[s][arm] for s in seeds],axis=0),axis=0)

def percentile_ci(x,rng,B=10000):
 x=np.asarray(x,float);means=np.empty(B,float);n=len(x)
 for i in range(B):means[i]=x[rng.integers(0,n,n)].mean()
 return [float(np.quantile(means,.025)),float(np.quantile(means,.5)),float(np.quantile(means,.975))]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--freeze-dir',required=True);ap.add_argument('--shards-root',required=True);ap.add_argument('--out-dir',required=True);a=ap.parse_args();freeze=Path(a.freeze_dir);root=Path(a.shards_root);out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
 if sha256_file(freeze/'chem_disease_query_structure.json')!=EXPECTED_QUERY_STRUCTURE_SHA:raise RuntimeError('query structure SHA mismatch')
 meta,N,universe_sha=universe_offsets(freeze);store={};perf=[]
 for p in root.rglob('ranks_*.npz'):
  s=int(p.stem.split('_')[1]);z=np.load(p);store[s]={'R0':z['R0'],'R1':z['R1']}
 for p in root.rglob('seed_performance.csv'):perf.append(pd.read_csv(p))
 if set(store)!=set(SEEDS):raise RuntimeError(f'missing seeds {sorted(set(SEEDS)-set(store))}, extras {sorted(set(store)-set(SEEDS))}')
 for s,v in store.items():
  if len(v['R0'])!=N or len(v['R1'])!=N:raise RuntimeError(f'length mismatch seed {s}')
 manifests=[json.loads(p.read_text()) for p in root.rglob('shard_manifest.json')]
 if any(m['universe_sha256']!=universe_sha or int(m['n_universe_rows'])!=N for m in manifests):raise RuntimeError('shard universe mismatch')
 rows=[];qdetail=[]
 for m in MS:
  Am=A[:m];Bm=B[:m]
  means={name:mean_vec(store,seeds,arm) for name,seeds,arm in [('R0A',Am,'R0'),('R1A',Am,'R1'),('R0B',Bm,'R0'),('R1B',Bm,'R1')]}
  tops={name:{k:topk_from_mean(v,meta,k) for k in KS} for name,v in means.items()}
  perq=[]
  for qi,(q,off,n,groups) in enumerate(meta):
   rec={'m':m,'query':q};repvals=[];stvals=[]
   for k in KS:
    a0=tops['R0A'][k][qi];a1=tops['R1A'][k][qi];b0=tops['R0B'][k][qi];b1=tops['R1B'][k][qi]
    if any(x is None for x in (a0,a1,b0,b1)):continue
    rA=ridi_sets(a0,a1);rB=ridi_sets(b0,b1);s0=ridi_sets(a0,b0);s1=ridi_sets(a1,b1);rep=.5*(rA+rB);st=.5*(s0+s1);delta=rep-st
    rec[f'rep_{k}']=rep;rec[f'stoch_{k}']=st;rec[f'delta_{k}']=delta;repvals.append(rep);stvals.append(st)
   rec['rep_AURIDI']=float(np.mean(repvals));rec['stoch_AURIDI']=float(np.mean(stvals));rec['delta_AURIDI']=rec['rep_AURIDI']-rec['stoch_AURIDI'];perq.append(rec);qdetail.append(rec)
  df=pd.DataFrame(perq);r={'m':m,'n_queries':len(df),'mean_rep_AURIDI':df.rep_AURIDI.mean(),'mean_stoch_AURIDI':df.stoch_AURIDI.mean(),'mean_delta_AURIDI':df.delta_AURIDI.mean()}
  for k in KS:
   r[f'mean_rep_{k}']=df[f'rep_{k}'].mean();r[f'mean_stoch_{k}']=df[f'stoch_{k}'].mean();r[f'mean_delta_{k}']=df[f'delta_{k}'].mean()
  rows.append(r)
 summary=pd.DataFrame(rows);detail=pd.DataFrame(qdetail);summary.to_csv(out/'convergence_summary.csv',index=False);detail.to_csv(out/'query_level_attribution.csv',index=False)
 d8=detail[detail.m==8].copy();rng=np.random.default_rng(BOOT_SEED);ci=percentile_ci(d8.delta_AURIDI.to_numpy(),rng,10000);mean_delta=float(d8.delta_AURIDI.mean());success=bool(ci[0]>0)
 secondary={}
 for k in KS:
  rngk=np.random.default_rng((BOOT_SEED+k)%(2**32));secondary[str(k)]={'mean_delta':float(d8[f'delta_{k}'].mean()),'ci95':percentile_ci(d8[f'delta_{k}'].to_numpy(),rngk,10000)}
 perfdf=pd.concat(perf,ignore_index=True).sort_values('seed') if perf else pd.DataFrame();perfdf.to_csv(out/'seed_performance_all.csv',index=False)
 verdict={'lock_label':LOCK_LABEL,'bootstrap_seed':BOOT_SEED,'primary_stratum':'chemical-disease','primary_m':8,'primary_metric':'AURIDI mean across k=100,500,1000','mean_delta_rep_minus_stochasticity':mean_delta,'bootstrap_95_percentile_CI':ci,'primary_success':success,'interpretation':('G3 learned-family attribution criterion supported on this frozen GraphSAGE task.' if success else ('G3 remains unmet because the 95% CI includes zero.' if ci[0]<=0<=ci[2] else 'Retraining stochasticity dominates on the primary endpoint; G3 remains unmet.')),'secondary_by_k':secondary,'all_16_seeds_reported':True,'query_structure_sha256':EXPECTED_QUERY_STRUCTURE_SHA,'universe_sha256':universe_sha}
 (out/'PRIMARY_VERDICT.json').write_text(json.dumps(verdict,indent=2));(out/'VERDICT.md').write_text('# Nature GraphSAGE attribution — locked primary verdict\n\n'+f"**Primary success:** {'PASS' if success else 'NOT MET'}\n\nMean Δ (representation AURIDI − stochasticity AURIDI): **{mean_delta:.6f}**\n\n95% query-bootstrap CI: **[{ci[0]:.6f}, {ci[2]:.6f}]**\n\n{verdict['interpretation']}\n")
 manifest=[]
 for p in sorted(out.iterdir()):
  if p.is_file():manifest.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha256_file(p)})
 (out/'RESULT_SHA256.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(verdict,indent=2))
if __name__=='__main__':main()
