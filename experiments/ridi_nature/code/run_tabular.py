import os, urllib.request, hashlib, json, math, platform, sys
import numpy as np, pandas as pd
from scipy import sparse
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from common import ridi_from_scores, rank_spearman, sha_seed, write_json

OUT=os.environ.get('OUTDIR','results/tabular'); os.makedirs(OUT,exist_ok=True)
DATA=os.path.join(OUT,'data'); os.makedirs(DATA,exist_ok=True)
URLS={
 'adult.data':'https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data',
 'adult.test':'https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test'
}
for fn,url in URLS.items():
    p=os.path.join(DATA,fn)
    if not os.path.exists(p): urllib.request.urlretrieve(url,p)

cols=['age','workclass','fnlwgt','education','education-num','marital-status','occupation','relationship','race','sex','capital-gain','capital-loss','hours-per-week','native-country','income']
train=pd.read_csv(os.path.join(DATA,'adult.data'),names=cols,skipinitialspace=True,na_filter=False)
test=pd.read_csv(os.path.join(DATA,'adult.test'),names=cols,skipinitialspace=True,skiprows=1,na_filter=False)
train['income']=train.income.str.strip().str.rstrip('.')
test['income']=test.income.str.strip().str.rstrip('.')
ytr=(train.income=='>50K').astype(int).to_numpy(); yte=(test.income=='>50K').astype(int).to_numpy()
Xtr=train.drop(columns='income').copy(); Xte=test.drop(columns='income').copy()
num=['age','fnlwgt','education-num','capital-gain','capital-loss','hours-per-week']
cat=[c for c in Xtr.columns if c not in num]
sc=StandardScaler(); Ntr=sc.fit_transform(Xtr[num].astype(float)); Nte=sc.transform(Xte[num].astype(float))

# Categories fixed from training; unknown is explicit.
cat_levels={c:sorted(set(Xtr[c].astype(str)))+['__UNK__'] for c in cat}

def map_vals(series, levels):
    known=set(levels[:-1]); return np.array([v if v in known else '__UNK__' for v in series.astype(str)],dtype=object)

# R0 one-hot sparse
blocks_tr=[]; blocks_te=[]; onehot_names=[]
for c in cat:
    levels=cat_levels[c]; idx={v:i for i,v in enumerate(levels)}
    trv=map_vals(Xtr[c],levels); tev=map_vals(Xte[c],levels)
    r=np.arange(len(trv)); cc=np.array([idx[v] for v in trv]); data=np.ones(len(trv))
    blocks_tr.append(sparse.csr_matrix((data,(r,cc)),shape=(len(trv),len(levels))))
    r=np.arange(len(tev)); cc=np.array([idx[v] for v in tev]); data=np.ones(len(tev))
    blocks_te.append(sparse.csr_matrix((data,(r,cc)),shape=(len(tev),len(levels))))
    onehot_names += [f'{c}={v}' for v in levels]
R0tr=sparse.hstack([sparse.csr_matrix(Ntr)]+blocks_tr,format='csr')
R0te=sparse.hstack([sparse.csr_matrix(Nte)]+blocks_te,format='csr')

# R1 collision-free binary coding
Btr=[Ntr]; Bte=[Nte]; binary_names=[]
for c in cat:
    levels=cat_levels[c]; known=levels[:-1]; idx={v:i+1 for i,v in enumerate(known)}
    width=math.ceil(math.log2(len(known)+1))
    def encode(series):
        vals=np.array([idx.get(v,0) for v in series.astype(str)],dtype=np.int64)
        return np.column_stack([((vals>>bit)&1).astype(float) for bit in range(width)])
    Btr.append(encode(Xtr[c])); Bte.append(encode(Xte[c])); binary_names += [f'{c}.bit{bit}' for bit in range(width)]
R1tr=np.column_stack(Btr); R1te=np.column_stack(Bte)

ids=np.array([f'test_{i:05d}' for i in range(len(test))])
ks=[100,500,1000]

def eval_model(name, model0, model1):
    model0.fit(R0tr,ytr); p0=model0.predict_proba(R0te)[:,1]
    model1.fit(R1tr,ytr); p1=model1.predict_proba(R1te)[:,1]
    out={'model':name,'auc_r0':float(roc_auc_score(yte,p0)),'auc_r1':float(roc_auc_score(yte,p1)),
         'ap_r0':float(average_precision_score(yte,p0)),'ap_r1':float(average_precision_score(yte,p1)),
         'spearman':rank_spearman(p0,p1)}
    out['auc_abs_diff']=abs(out['auc_r0']-out['auc_r1']); out['ap_abs_diff']=abs(out['ap_r0']-out['ap_r1'])
    for k in ks: out[f'ridi_{k}']=ridi_from_scores(p0,p1,ids,k)
    pd.DataFrame({'id':ids,'y':yte,'score_r0':p0,'score_r1':p1}).to_csv(os.path.join(OUT,f'{name}_scores.csv.gz'),index=False,compression='gzip')
    return out,p0,p1

lr0=LogisticRegression(C=1.0,solver='lbfgs',max_iter=5000,tol=1e-10)
lr1=LogisticRegression(C=1.0,solver='lbfgs',max_iter=5000,tol=1e-10)
res_lr,p0,p1=eval_model('logistic',lr0,lr1)
rf0=RandomForestClassifier(n_estimators=500,max_features='sqrt',min_samples_leaf=1,random_state=20260823,n_jobs=-1)
rf1=RandomForestClassifier(n_estimators=500,max_features='sqrt',min_samples_leaf=1,random_state=20260823,n_jobs=-1)
res_rf,_,_=eval_model('random_forest',rf0,rf1)

# Pure coordinate relabeling control for logistic model.
rng=np.random.default_rng(sha_seed('RIDI-NATURE-TABULAR-ONEHOT-PERM-v1'))
perm=rng.permutation(R0tr.shape[1])
lrc=LogisticRegression(C=1.0,solver='lbfgs',max_iter=5000,tol=1e-10)
lrc.fit(R0tr[:,perm],ytr); pc=lrc.predict_proba(R0te[:,perm])[:,1]
control={'max_abs_prediction_difference':float(np.max(np.abs(p0-pc))), 'spearman':rank_spearman(p0,pc)}
for k in ks: control[f'ridi_{k}']=ridi_from_scores(p0,pc,ids,k)
control['pass']=bool(control['max_abs_prediction_difference']<1e-8 and all(control[f'ridi_{k}']==0 for k in ks))

hashes={}
for fn in URLS:
    b=open(os.path.join(DATA,fn),'rb').read(); hashes[fn]=hashlib.sha256(b).hexdigest()
result={'experiment':'E-TABULAR','dataset':'UCI Adult','n_train':len(train),'n_test':len(test),'r0_features':int(R0tr.shape[1]),'r1_features':int(R1tr.shape[1]),
        'primary':res_lr,'secondary':res_rf,'invariance_control':control,'source_sha256':hashes,
        'versions':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__}}
write_json(os.path.join(OUT,'tabular_result.json'),result)
pd.DataFrame([res_lr,res_rf]).to_csv(os.path.join(OUT,'tabular_summary.csv'),index=False)
print(json.dumps(result,indent=2))
