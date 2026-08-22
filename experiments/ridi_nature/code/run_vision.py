import os, hashlib, json, sys
import numpy as np, pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision.datasets import CIFAR10
from torchvision.models import resnet18, ResNet18_Weights
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
from scipy.stats import spearmanr
from common import stable_order, bootstrap_mean_ci, ndcg_at_k, recall_at_k, sha_seed, write_json

OUT=os.environ.get('OUTDIR','results/vision'); os.makedirs(OUT,exist_ok=True)
DATA=os.path.join(OUT,'data')
weights=ResNet18_Weights.DEFAULT; tfm=weights.transforms()
ds=CIFAR10(root=DATA,train=False,download=True,transform=tfm)
# query ids are 200 lowest SHA256 hashes of official test index
order=sorted(range(len(ds)),key=lambda i: hashlib.sha256(f'CIFAR10-test-{i}'.encode()).hexdigest())
q_idx=np.array(order[:200]); c_idx=np.array(order[200:]);
model=resnet18(weights=weights); model.fc=nn.Identity(); model.eval()
device=torch.device('cpu'); model.to(device)

def extract(indices):
    loader=DataLoader(Subset(ds,indices.tolist()),batch_size=128,shuffle=False,num_workers=2)
    feats=[]; labs=[]
    with torch.inference_mode():
        for x,y in loader:
            z=model(x.to(device)).cpu().numpy(); feats.append(z); labs.append(np.asarray(y))
    return np.vstack(feats), np.concatenate(labs)
Qraw,qlab=extract(q_idx); Craw,clab=extract(c_idx)
Q0=normalize(Qraw); C0=normalize(Craw)
pca=PCA(n_components=128,svd_solver='randomized',random_state=20260823)
C1=normalize(pca.fit_transform(Craw)); Q1=normalize(pca.transform(Qraw))
S0=Q0@C0.T; S1=Q1@C1.T
# orthogonal invariance control on normalized R0 coordinates
rng=np.random.default_rng(sha_seed('RIDI-NATURE-VISION-ORTHOGONAL-v1'))
G=rng.standard_normal((512,512)); Qmat,_=np.linalg.qr(G)
Qrot=Q0@Qmat; Crot=C0@Qmat; Sc=Qrot@Crot.T
maxdiff=float(np.max(np.abs(S0-Sc)))
cids=np.array([f'cifar10_{i}' for i in c_idx]); qids=np.array([f'cifar10_{i}' for i in q_idx])
ks=[10,50,100]; ridis={k:[] for k in ks}; ctr={k:[] for k in ks}; nd0=[]; nd1=[]; rc0=[]; rc1=[]; rhos=[]; rows=[]
for qi in range(200):
    rel=(clab==qlab[qi]).astype(int); o0=stable_order(S0[qi],cids); o1=stable_order(S1[qi],cids); oc=stable_order(Sc[qi],cids)
    rhos.append(float(spearmanr(S0[qi],S1[qi]).statistic)); nd0.append(ndcg_at_k(rel,o0,10)); nd1.append(ndcg_at_k(rel,o1,10)); rc0.append(recall_at_k(rel,o0,100)); rc1.append(recall_at_k(rel,o1,100))
    row={'query_id':qids[qi],'label':int(qlab[qi]),'spearman':rhos[-1],'ndcg10_r0':nd0[-1],'ndcg10_r1':nd1[-1],'recall100_r0':rc0[-1],'recall100_r1':rc1[-1]}
    for k in ks:
        a=set(cids[o0[:k]]); b=set(cids[o1[:k]]); c=set(cids[oc[:k]])
        rv=1-len(a&b)/len(a|b); cv=1-len(a&c)/len(a|c); ridis[k].append(rv); ctr[k].append(cv); row[f'ridi_{k}']=rv
    rows.append(row)
pd.DataFrame(rows).to_csv(os.path.join(OUT,'vision_query_results.csv.gz'),index=False,compression='gzip')
res={'experiment':'E-VISION','dataset':'CIFAR-10 test','n_candidates':len(c_idx),'n_queries':len(q_idx),'feature_extractor':'torchvision ResNet18 DEFAULT','r0_dim':512,'r1_dim':128,
     'pca_explained_variance':float(pca.explained_variance_ratio_.sum()),'ndcg10_r0':float(np.mean(nd0)),'ndcg10_r1':float(np.mean(nd1)),'ndcg10_abs_diff':float(abs(np.mean(nd0)-np.mean(nd1))),
     'recall100_r0':float(np.mean(rc0)),'recall100_r1':float(np.mean(rc1)),'recall100_abs_diff':float(abs(np.mean(rc0)-np.mean(rc1))), 'mean_spearman':float(np.mean(rhos)),
     'invariance_control':{'max_abs_similarity_difference':maxdiff,'pass':bool(maxdiff<1e-10 and all(max(ctr[k])==0 for k in ks))}}
for k in ks:
    res[f'mean_ridi_{k}']=float(np.mean(ridis[k])); res[f'ridi_{k}_ci95']=bootstrap_mean_ci(ridis[k],10000,sha_seed(f'RIDI-VISION-BOOT-{k}'))
    res['invariance_control'][f'max_ridi_{k}']=float(max(ctr[k]))
write_json(os.path.join(OUT,'vision_result.json'),res)
np.savez_compressed(os.path.join(OUT,'vision_features_and_indices.npz'),q_idx=q_idx,c_idx=c_idx,Qraw=Qraw,Craw=Craw,qlab=qlab,clab=clab)
print(json.dumps(res,indent=2))
