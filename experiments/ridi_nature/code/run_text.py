import os, hashlib, json, sys, unicodedata
import numpy as np, pandas as pd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from scipy.stats import spearmanr
from common import stable_order, bootstrap_mean_ci, ndcg_at_k, recall_at_k, sha_seed, write_json

OUT=os.environ.get('OUTDIR','results/text'); os.makedirs(OUT,exist_ok=True)
data=fetch_20newsgroups(subset='all',remove=('headers','footers','quotes'),shuffle=False)
records=[]
for i,(txt,y) in enumerate(zip(data.data,data.target)):
    t=unicodedata.normalize('NFC',txt).strip()
    if not t: continue
    h=hashlib.sha256((t+'|'+str(i)).encode('utf-8')).hexdigest()
    records.append((h,i,t,int(y)))
records.sort(key=lambda x:x[0])
if len(records)<5200: raise RuntimeError('not enough non-empty documents')
cand=records[:5000]; queries=records[5000:5200]
c_text=[x[2] for x in cand]; q_text=[x[2] for x in queries]
c_lab=np.array([x[3] for x in cand]); q_lab=np.array([x[3] for x in queries])
c_ids=np.array([f'doc_{x[1]}' for x in cand])
q_ids=np.array([f'doc_{x[1]}' for x in queries])

vec=TfidfVectorizer(lowercase=True,ngram_range=(1,2),min_df=2,max_df=0.95,max_features=50000,norm='l2')
C0=vec.fit_transform(c_text); Q0=vec.transform(q_text)
svd=TruncatedSVD(n_components=256,random_state=20260823)
C1=normalize(svd.fit_transform(C0)); Q1=normalize(svd.transform(Q0))
# Cosine because R0 tfidf is already l2-normalized.
S0=(Q0 @ C0.T).toarray(); S1=Q1 @ C1.T
# coordinate permutation invariance
rng=np.random.default_rng(sha_seed('RIDI-NATURE-TEXT-TFIDF-PERM-v1')); perm=rng.permutation(C0.shape[1])
Sc=(Q0[:,perm] @ C0[:,perm].T).toarray()
maxdiff=float(np.max(np.abs(S0-Sc)))

ks=[10,50,100]
rows=[]; ridis={k:[] for k in ks}; nd0=[]; nd1=[]; rc0=[]; rc1=[]; rhos=[]; ctr={k:[] for k in ks}
for qi in range(len(queries)):
    rel=(c_lab==q_lab[qi]).astype(int)
    o0=stable_order(S0[qi],c_ids); o1=stable_order(S1[qi],c_ids); oc=stable_order(Sc[qi],c_ids)
    rhos.append(float(spearmanr(S0[qi],S1[qi]).statistic))
    nd0.append(ndcg_at_k(rel,o0,10)); nd1.append(ndcg_at_k(rel,o1,10)); rc0.append(recall_at_k(rel,o0,100)); rc1.append(recall_at_k(rel,o1,100))
    row={'query_id':q_ids[qi],'label':int(q_lab[qi]),'spearman':rhos[-1],'ndcg10_r0':nd0[-1],'ndcg10_r1':nd1[-1],'recall100_r0':rc0[-1],'recall100_r1':rc1[-1]}
    for k in ks:
        a=set(c_ids[o0[:k]]); b=set(c_ids[o1[:k]]); c=set(c_ids[oc[:k]])
        rv=1-len(a&b)/len(a|b); cv=1-len(a&c)/len(a|c)
        ridis[k].append(rv); ctr[k].append(cv); row[f'ridi_{k}']=rv
    rows.append(row)
pd.DataFrame(rows).to_csv(os.path.join(OUT,'text_query_results.csv.gz'),index=False,compression='gzip')
res={'experiment':'E-TEXT','dataset':'20 Newsgroups','n_candidates':5000,'n_queries':200,'r0_features':int(C0.shape[1]),'r1_features':256,
     'ndcg10_r0':float(np.nanmean(nd0)),'ndcg10_r1':float(np.nanmean(nd1)),'ndcg10_abs_diff':float(abs(np.nanmean(nd0)-np.nanmean(nd1))),
     'recall100_r0':float(np.nanmean(rc0)),'recall100_r1':float(np.nanmean(rc1)),'recall100_abs_diff':float(abs(np.nanmean(rc0)-np.nanmean(rc1))),
     'mean_spearman':float(np.nanmean(rhos)),
     'invariance_control':{'max_abs_similarity_difference':maxdiff,'pass':bool(maxdiff<1e-12 and all(max(ctr[k])==0 for k in ks))}}
for k in ks:
    res[f'mean_ridi_{k}']=float(np.mean(ridis[k])); res[f'ridi_{k}_ci95']=bootstrap_mean_ci(ridis[k],10000,sha_seed(f'RIDI-TEXT-BOOT-{k}'))
    res['invariance_control'][f'max_ridi_{k}']=float(max(ctr[k]))
write_json(os.path.join(OUT,'text_result.json'),res)
print(json.dumps(res,indent=2))
