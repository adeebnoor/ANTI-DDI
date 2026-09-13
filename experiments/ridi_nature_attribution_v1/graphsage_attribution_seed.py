#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score
import torch, torch.nn as nn
import torch.nn.functional as F
from scipy.sparse import csr_matrix

torch.set_num_threads(max(1,min(4,(__import__('os').cpu_count() or 4))))
try: torch.set_num_interop_threads(1)
except RuntimeError: pass

SALT='RTXKG2-20260818-GraphSAGE-v1'; KS=(100,500,1000)
MAX_TRAIN_POS=100_000; MAX_VAL_POS=20_000; NEG_PER_TEST=100
MAX_EPOCHS=60; PATIENCE=8; HIDDEN=64; OUTDIM=64; DROPOUT=.10; LR=.01; WEIGHT_DECAY=1e-5
LOCK_SEEDS=[355092268,1972696080,1590711264,1745982372,1113956884,734518037,1017280056,54477576,202245501,871610103,1739075335,404365195,1603643707,1173720350,1263375671,1531572456]
LEGACY_SEEDS=[20260818,20260819,20260820]

def hval(s):return hashlib.sha256(s.encode()).hexdigest()
def sha256_file(p,chunk=8*1024*1024):
 h=hashlib.sha256();f=open(p,'rb')
 while True:
  b=f.read(chunk)
  if not b:break
  h.update(b)
 f.close();return h.hexdigest()

def read_queries(path):
 q=defaultdict(list);relevant=set()
 with gzip.open(path,'rt',encoding='utf-8',newline='') as f:
  r=csv.DictReader(f,delimiter='\t')
  for row in r:
   a=row['query_raw_chem'];b=row['candidate_raw_chem'];q[a].append(b);relevant.add(a);relevant.add(b)
 return dict(q),relevant

def read_edges(path,relevant):
 rows=[];raw_to_r1={};all_raw_pos=defaultdict(set)
 with gzip.open(path,'rt',encoding='utf-8',newline='') as f:
  r=csv.DictReader(f,delimiter='\t')
  for row in r:
   c=row['raw_chem']
   if c not in relevant:continue
   p=row['raw_partner'];pc=row['primary_chem'];pp=row['primary_partner']
   rows.append((c,p,pc,pp));raw_to_r1[c]=pc;all_raw_pos[c].add(p)
 if not rows:raise RuntimeError('No edges found')
 return rows,raw_to_r1,all_raw_pos

def split_of(pc,pp):
 x=int(hval(f'{SALT}|split|{pc}|{pp}')[:12],16)%10000
 return 'train' if x<8000 else ('val' if x<9000 else 'test')
def split_rows(rows):
 out={'train':[],'val':[],'test':[]}
 for x in rows:out[split_of(x[2],x[3])].append(x)
 return out
def represented_pairs(rows,arm):return {(c,p) for c,p,pc,pp in rows} if arm=='R0' else {(pc,pp) for c,p,pc,pp in rows}
def select_by_hash(items,n,key):
 items=list(items);return items if len(items)<=n else sorted(items,key=lambda x:hval(f'{SALT}|{key}|{x[0]}|{x[1]}'))[:n]
def raw_partner_universe(rows):return sorted({p for c,p,pc,pp in rows})
def partner_r1_map(rows):return {p:pp for c,p,pc,pp in rows}

def build_fixed_raw_negatives(pos_rows,all_raw_pos,partners,max_n,tag):
 selected=select_by_hash([(c,p) for c,p,pc,pp in pos_rows],max_n,tag+'pos');neg=[];m=len(partners)
 for c,p in selected:
  start=int(hval(f'{SALT}|{tag}|neg|{c}|{p}')[:16],16)%m;found=None
  for j in range(min(m,10000)):
   q=partners[(start+j)%m]
   if q not in all_raw_pos[c]:found=(c,q);break
  if found is not None:neg.append(found)
 return selected,neg

def map_raw_pairs(rawpairs,arm,raw_to_r1,pmap,allrep):
 out=[];seen=set()
 for c,p in rawpairs:
  a=c if arm=='R0' else raw_to_r1.get(c,c);b=p if arm=='R0' else pmap.get(p,p);pair=(a,b)
  if pair in allrep:continue
  if pair not in seen:seen.add(pair);out.append(pair)
 return out

def node_index(all_pairs):
 chems=sorted({c for c,p in all_pairs});parts=sorted({p for c,p in all_pairs})
 if set(chems)&set(parts):raise RuntimeError('semantic family collision')
 ids=chems+parts;return ids,{x:i for i,x in enumerate(ids)},set(chems),set(parts)
def sparse_mean_adj(train_pairs,idx,n):
 src=[];dst=[]
 for c,p in train_pairs:
  i=idx[c];j=idx[p];src.extend([i,j]);dst.extend([j,i])
 src=np.asarray(src,dtype=np.int64);dst=np.asarray(dst,dtype=np.int64);deg=np.bincount(src,minlength=n).astype(np.float32)
 vals=np.where(deg[src]>0,1.0/deg[src],0).astype(np.float32);M=csr_matrix((vals,(src,dst)),shape=(n,n),dtype=np.float32);M.sum_duplicates();M.sort_indices()
 return torch.sparse_csr_tensor(torch.tensor(M.indptr,dtype=torch.int64),torch.tensor(M.indices,dtype=torch.int64),torch.tensor(M.data,dtype=torch.float32),size=(n,n)),deg
def features(ids,chems,parts,deg):
 x=np.zeros((len(ids),3),dtype=np.float32)
 for i,node in enumerate(ids):x[i,0 if node in chems else 1]=1.0
 ld=np.log1p(deg);mx=float(ld.max()) if len(ld) and ld.max()>0 else 1.;x[:,2]=ld/mx;return torch.tensor(x,dtype=torch.float32)
class GraphSAGE(nn.Module):
 def __init__(self):super().__init__();self.l1=nn.Linear(6,HIDDEN);self.l2=nn.Linear(2*HIDDEN,OUTDIM)
 def forward(self,x,A):
  m0=torch.sparse.mm(A,x);h=F.relu(self.l1(torch.cat([x,m0],1)));h=F.dropout(h,p=DROPOUT,training=self.training);m1=torch.sparse.mm(A,h);return self.l2(torch.cat([h,m1],1))
def pair_tensor(pairs,idx,device):return (torch.tensor([idx[x] for x,y in pairs],dtype=torch.long,device=device),torch.tensor([idx[y] for x,y in pairs],dtype=torch.long,device=device))
def logits(z,pairidx):a,b=pairidx;return (z[a]*z[b]).sum(1)/math.sqrt(z.shape[1])

def train_arm(rows,split,arm,raw_to_r1,pmap,all_raw_pos,seed,device):
 torch.manual_seed(seed);np.random.seed(seed);random.seed(seed)
 if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
 tr=represented_pairs(split['train'],arm);va=represented_pairs(split['val'],arm);te=represented_pairs(split['test'],arm);allp=represented_pairs(rows,arm)
 ids,idx,chems,parts=node_index(allp);A,deg=sparse_mean_adj(tr,idx,len(ids));x=features(ids,chems,parts,deg);A=A.to(device);x=x.to(device)
 partners=raw_partner_universe(rows)
 rawtr_pos,rawtr_neg=build_fixed_raw_negatives(split['train'],all_raw_pos,partners,MAX_TRAIN_POS,f'train|{seed}')
 rawva_pos,rawva_neg=build_fixed_raw_negatives(split['val'],all_raw_pos,partners,MAX_VAL_POS,f'val|{seed}')
 def map_pos(rawpos,target):
  out=[];seen=set()
  for c,p in rawpos:
   a=c if arm=='R0' else raw_to_r1.get(c,c);b=p if arm=='R0' else pmap.get(p,p);pair=(a,b)
   if pair in target and pair not in seen:seen.add(pair);out.append(pair)
  return out
 trpos=map_pos(rawtr_pos,tr);vapos=map_pos(rawva_pos,va);trneg=map_raw_pairs(rawtr_neg,arm,raw_to_r1,pmap,allp);vaneg=map_raw_pairs(rawva_neg,arm,raw_to_r1,pmap,allp)
 trpos=[p for p in trpos if p[0] in idx and p[1] in idx];trneg=[p for p in trneg if p[0] in idx and p[1] in idx];vapos=[p for p in vapos if p[0] in idx and p[1] in idx];vaneg=[p for p in vaneg if p[0] in idx and p[1] in idx]
 model=GraphSAGE().to(device);opt=torch.optim.Adam(model.parameters(),lr=LR,weight_decay=WEIGHT_DECAY);bce=nn.BCEWithLogitsLoss();trpi=pair_tensor(trpos,idx,device);trni=pair_tensor(trneg,idx,device);vapi=pair_tensor(vapos,idx,device);vani=pair_tensor(vaneg,idx,device)
 best=None;best_loss=float('inf');wait=0;history=[]
 for ep in range(1,MAX_EPOCHS+1):
  model.train();opt.zero_grad();z=model(x,A);lp=logits(z,trpi);ln=logits(z,trni);loss=bce(torch.cat([lp,ln]),torch.cat([torch.ones_like(lp),torch.zeros_like(ln)]));loss.backward();opt.step()
  model.eval()
  with torch.no_grad():
   zv=model(x,A);vp=logits(zv,vapi);vn=logits(zv,vani);vl=torch.cat([vp,vn]);vy=torch.cat([torch.ones_like(vp),torch.zeros_like(vn)]);vloss=float(bce(vl,vy).cpu()) if len(vl) else float(loss.detach().cpu())
  history.append((ep,float(loss.detach().cpu()),vloss))
  if vloss<best_loss-1e-6:best_loss=vloss;wait=0;best={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
  else:
   wait+=1
   if wait>=PATIENCE:break
 if best is not None:model.load_state_dict(best)
 model.eval()
 with torch.no_grad():z=model(x,A).cpu()
 return {'z':z,'idx':idx,'test_pairs':te,'all_pairs':allp,'epochs':len(history),'best_val_loss':best_loss,'n_nodes':len(ids),'n_train_edges':len(tr)}

def normalized_embeddings(res):
 z=res['z'].numpy().astype(np.float32,copy=False);n=np.linalg.norm(z,axis=1,keepdims=True);n[n==0]=1.;return z/n

def build_universe(queries,raw_to_r1):
 qmeta=[];groups_all=[];offset=0
 for q,cands in sorted(queries.items()):
  qg=raw_to_r1.get(q,q);groups=defaultdict(list)
  for c in cands:
   g=raw_to_r1.get(c,c)
   if g!=qg:groups[g].append(c)
  sg=sorted(groups);qmeta.append((q,qg,offset,len(sg),groups,sg));groups_all.extend((q,g) for g in sg);offset+=len(sg)
 return qmeta,groups_all

def rank_vector(qmeta,r0_or_r1,arm,raw_to_r1):
 Z=normalized_embeddings(r0_or_r1);idx=r0_or_r1['idx'];vec=np.empty(sum(n for _,_,_,n,_,_ in qmeta),dtype=np.float32)
 for q,qg,off,n,groups,sg in qmeta:
  scores={}
  if arm=='R0':
   qi=idx.get(q);rawscore={}
   if qi is not None:
    avail=[c for ms in groups.values() for c in ms if c in idx]
    if avail:
     inds=np.asarray([idx[c] for c in avail]);vals=Z[inds]@Z[qi];rawscore=dict(zip(avail,vals.tolist()))
   for g,ms in groups.items():scores[g]=max(rawscore.get(c,0.0) for c in ms)
  else:
   qi=idx.get(qg);scores={g:0.0 for g in sg};avail=[g for g in sg if g in idx]
   if qi is not None and avail:
    inds=np.asarray([idx[g] for g in avail]);vals=Z[inds]@Z[qi]
    for g,v in zip(avail,vals.tolist()):scores[g]=float(v)
  order=sorted(sg,key=lambda g:(-scores[g],hval(f'{SALT}|tie|{g}')))
  pos={g:i for i,g in enumerate(sg)};denom=max(1,n-1)
  for rank,g in enumerate(order):vec[off+pos[g]]=1.0-rank/denom
 return vec

def test_negative_raw_candidates(c,p,partners,all_raw_pos):
 m=len(partners);start=int(hval(f'{SALT}|evalneg|{c}|{p}')[:16],16)%m;out=[]
 for j in range(m):
  q=partners[(start+j)%m]
  if q==p or q in all_raw_pos[c]:continue
  out.append(q)
  if len(out)>=NEG_PER_TEST:break
 return out

def heldout_metrics(split,rows,arm,raw_to_r1,pmap,all_raw_pos,res):
 partners=raw_partner_universe(rows);allp=res['all_pairs'];Z=normalized_embeddings(res);cases=[];y=[];scores=[];seen=set()
 for c,p,pc,pp in split['test']:
  if (c,p) in seen:continue
  seen.add((c,p));a=c if arm=='R0' else raw_to_r1.get(c,c);b=p if arm=='R0' else pmap.get(p,p);ia=res['idx'].get(a);ib=res['idx'].get(b)
  if (a,b) not in res['test_pairs'] or ia is None or ib is None:continue
  neg=[];seenp=set()
  for q in test_negative_raw_candidates(c,p,partners,all_raw_pos):
   nq=q if arm=='R0' else pmap.get(q,q);pair=(a,nq)
   if pair in allp or nq==b or pair in seenp or nq not in res['idx']:continue
   seenp.add(pair);neg.append(nq)
  if len(neg)<10:continue
  ps=float(Z[ib]@Z[ia]);inds=np.asarray([res['idx'][q] for q in neg]);ns=Z[inds]@Z[ia];rank=1+int(np.sum(ns>ps))+.5*int(np.sum(ns==ps));cases.append((1/rank,rank<=10,rank<=50,len(neg)));y.append(1);scores.append(ps);y.extend([0]*len(ns));scores.extend(ns.astype(float).tolist())
 if not cases:return {'n_test_cases':0}
 a=np.asarray(cases,float);return {'n_test_cases':len(cases),'MRR':float(a[:,0].mean()),'Hits10':float(a[:,1].mean()),'Hits50':float(a[:,2].mean()),'mean_usable_negatives':float(a[:,3].mean()),'AUROC':float(roc_auc_score(y,scores)),'average_precision':float(average_precision_score(y,scores))}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--freeze-dir',required=True);ap.add_argument('--out-dir',required=True);ap.add_argument('--seeds',nargs='+',type=int,required=True);ap.add_argument('--device',default='cpu');a=ap.parse_args();out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
 allowed=set(LOCK_SEEDS+LEGACY_SEEDS)
 if any(s not in allowed for s in a.seeds):raise RuntimeError('seed not in locked set')
 device=torch.device(a.device);queries,relevant=read_queries(Path(a.freeze_dir)/'chem_disease_query_candidates.tsv.gz');rows,raw_to_r1,all_raw_pos=read_edges(Path(a.freeze_dir)/'chem_disease_frozen_edges.tsv.gz',relevant);pmap=partner_r1_map(rows);split=split_rows(rows);qmeta,groups_all=build_universe(queries,raw_to_r1)
 uh=hashlib.sha256()
 for q,g in groups_all:uh.update(q.encode()+b'\t'+g.encode()+b'\n')
 universe_sha=uh.hexdigest();summary=[]
 for seed in a.seeds:
  print('SEED',seed,'R0',flush=True);r0=train_arm(rows,split,'R0',raw_to_r1,pmap,all_raw_pos,seed,device)
  print('SEED',seed,'R1',flush=True);r1=train_arm(rows,split,'R1',raw_to_r1,pmap,all_raw_pos,seed,device)
  v0=rank_vector(qmeta,r0,'R0',raw_to_r1);v1=rank_vector(qmeta,r1,'R1',raw_to_r1)
  np.savez_compressed(out/f'ranks_{seed}.npz',R0=v0,R1=v1)
  h0=heldout_metrics(split,rows,'R0',raw_to_r1,pmap,all_raw_pos,r0);h1=heldout_metrics(split,rows,'R1',raw_to_r1,pmap,all_raw_pos,r1)
  rec={'seed':seed,'universe_sha256':universe_sha,'n_universe_rows':len(groups_all),'R0_epochs':r0['epochs'],'R1_epochs':r1['epochs'],'R0_best_val_loss':r0['best_val_loss'],'R1_best_val_loss':r1['best_val_loss']}
  for k,v in h0.items():rec['R0_'+k]=v
  for k,v in h1.items():rec['R1_'+k]=v
  summary.append(rec)
 pd.DataFrame(summary).to_csv(out/'seed_performance.csv',index=False)
 (out/'shard_manifest.json').write_text(json.dumps({'seeds':a.seeds,'universe_sha256':universe_sha,'n_universe_rows':len(groups_all),'files':[{'name':p.name,'sha256':sha256_file(p)} for p in sorted(out.glob('*'))]},indent=2))
if __name__=='__main__':main()
