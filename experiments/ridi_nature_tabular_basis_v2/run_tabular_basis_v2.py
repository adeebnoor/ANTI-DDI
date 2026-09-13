#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy, sklearn
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

LOCK='RIDI-NATURE-TABULAR-BASIS-v2'
QSEED=3979731779
KS=(100,500,1000)
TRAIN_BLOB='e3cf049c46ef54b8b69dd9b2fa4d8d01376cc8e4'
TEST_BLOB='d23e54711c5c744fbf5572d5bdd379e1b54e703c'
COMMIT='d20fcb6402ae34e653d4513b00f39257bb37ed7f'
COLS=['age','workclass','fnlwgt','education','education-num','marital-status','occupation','relationship','race','sex','capital-gain','capital-loss','hours-per-week','native-country','income']
NUM=['age','fnlwgt','education-num','capital-gain','capital-loss','hours-per-week']
CAT=['workclass','education','marital-status','occupation','relationship','race','sex','native-country']

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def blob_sha1(p):
    d=Path(p).read_bytes(); h=hashlib.sha1(); h.update(f'blob {len(d)}\0'.encode()); h.update(d); return h.hexdigest()

def load(p,test=False):
    df=pd.read_csv(p,header=None,names=COLS,skipinitialspace=True,na_filter=False,dtype={c:str for c in CAT+['income']})
    for c in NUM: df[c]=pd.to_numeric(df[c],errors='raise')
    df['income']=df['income'].astype(str).str.strip()
    if test: df['income']=df['income'].str.rstrip('.')
    if set(df['income'].unique())-{'<=50K','>50K'}: raise RuntimeError('unexpected target')
    return df

def qmatrix(d):
    rng=np.random.default_rng(QSEED); a=rng.standard_normal((d,d),dtype=np.float64); q,r=np.linalg.qr(a)
    s=np.where(np.diag(r)>=0,1.0,-1.0); q=q*s[np.newaxis,:]
    if np.linalg.det(q)<0: q[:,0]*=-1
    return q

def tie(row): return hashlib.sha256(f'{LOCK}|tie|{row}'.encode()).hexdigest()
def topk(scores,ids,k): return [ids[i] for i in sorted(range(len(scores)),key=lambda i:(-float(scores[i]),tie(ids[i])))[:k]]
def ridi(a,b):
    A,B=set(a),set(b); inter=len(A&B); return 1-inter/len(A|B),len(A)-inter,inter

def perf(y,p): return {'auroc':float(roc_auc_score(y,p)),'average_precision':float(average_precision_score(y,p)),'brier':float(brier_score_loss(y,p))}

def f2_label(da,r100):
    if r100==0:return 'decision invariant at k=100'
    if r100>=.10 and abs(da)<=.005:return 'performance-stable decision instability'
    if r100>=.10:return 'representation sensitivity with performance shift'
    return 'weak decision sensitivity'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--train',type=Path,required=True); ap.add_argument('--test',type=Path,required=True); ap.add_argument('--out-dir',type=Path,required=True); a=ap.parse_args(); out=a.out_dir; out.mkdir(parents=True,exist_ok=True)
    if blob_sha1(a.train)!=TRAIN_BLOB: raise RuntimeError('ABORT train blob mismatch')
    if blob_sha1(a.test)!=TEST_BLOB: raise RuntimeError('ABORT test blob mismatch')
    tr,te=load(a.train),load(a.test,True); ytr=(tr.income.to_numpy()=='>50K').astype(int); yte=(te.income.to_numpy()=='>50K').astype(int); ids=[f'adult-test:{i+1}' for i in range(len(te))]
    pre=ColumnTransformer([('num',StandardScaler(),NUM),('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False,dtype=np.float64),CAT)],sparse_threshold=0.0)
    X0tr=np.asarray(pre.fit_transform(tr[NUM+CAT]),dtype=np.float64); X0te=np.asarray(pre.transform(te[NUM+CAT]),dtype=np.float64)
    q=qmatrix(X0tr.shape[1]); orth=float(np.max(np.abs(q.T@q-np.eye(q.shape[0])))); rt=float(np.max(np.abs((X0te[:256]@q)@q.T-X0te[:256])))
    if orth>=1e-10 or rt>=1e-9: raise RuntimeError(f'ABORT transform integrity orth={orth} roundtrip={rt}')
    X1tr,X1te=X0tr@q,X0te@q
    factories={
      'logistic_l2':lambda:LogisticRegression(penalty='l2',C=1.0,solver='lbfgs',max_iter=5000,tol=1e-10,fit_intercept=True),
      'hist_gradient_boosting':lambda:HistGradientBoostingClassifier(loss='log_loss',learning_rate=.05,max_iter=300,max_leaf_nodes=31,max_depth=None,min_samples_leaf=20,l2_regularization=1.0,early_stopping=False,random_state=20260823)}
    rows=[]; decisions=[]; scoreframes=[]
    for fam,fac in factories.items():
        scores={}; pp={}
        for arm,Xtr,Xte in [('R0',X0tr,X0te),('R1',X1tr,X1te)]:
            m=fac(); m.fit(Xtr,ytr); p=np.asarray(m.predict_proba(Xte)[:,1],dtype=np.float64); scores[arm]=p; pp[arm]=perf(yte,p)
            scoreframes.append(pd.DataFrame({'row_id':ids,'y':yte,'model_family':fam,'arm':arm,'score':p}))
        rec={'model_family':fam,'n_train':len(tr),'n_test':len(te),'n_features':X0tr.shape[1],'spearman_r0_r1':float(spearmanr(scores['R0'],scores['R1']).statistic)}
        for met in ['auroc','average_precision','brier']:
            rec[f'r0_{met}']=pp['R0'][met]; rec[f'r1_{met}']=pp['R1'][met]; rec[f'delta_{met}_r1_minus_r0']=pp['R1'][met]-pp['R0'][met]
        rr={}
        for k in KS:
            rk,repl,inter=ridi(topk(scores['R0'],ids,k),topk(scores['R1'],ids,k)); rr[k]=rk; rec[f'ridi_{k}']=rk; rec[f'replacements_{k}']=repl; decisions.append({'model_family':fam,'k':k,'ridi':rk,'intersection':inter,'replacements_each_arm':repl})
        if fam=='hist_gradient_boosting': rec['locked_interpretation']=f2_label(rec['delta_auroc_r1_minus_r0'],rr[100])
        else:
            md=float(np.max(np.abs(scores['R0']-scores['R1']))); rec['max_abs_score_delta']=md; rec['locked_interpretation']='mechanistic equivariance control near-invariant' if rr[100]==0 and md<1e-6 else 'mechanistic control requires implementation review'
        rows.append(rec)
    S=pd.DataFrame(rows); pd.concat(scoreframes).to_csv(out/'per_row_scores.csv.gz',index=False,compression='gzip'); S.to_csv(out/'summary.csv',index=False); pd.DataFrame(decisions).to_csv(out/'decision_identity.csv',index=False)
    man={'lock_label':LOCK,'lineage':'separate mechanistic follow-up to executed cross-modal v1; not a replacement','source':{'dataset':'UCI Adult/Census Income','mirror_commit':COMMIT,'train_git_blob_sha1':TRAIN_BLOB,'test_git_blob_sha1':TEST_BLOB,'train_sha256':sha256(a.train),'test_sha256':sha256(a.test)},'counts':{'n_train':len(tr),'n_test':len(te),'positive_train':int(ytr.sum()),'positive_test':int(yte.sum()),'base_dimension':int(X0tr.shape[1]),'categorical_levels':{c:int(tr[c].nunique(dropna=False)) for c in CAT}},'representation':{'orthogonal_seed':QSEED,'orthogonality_max_abs_error':orth,'roundtrip_max_abs_error':rt,'det_Q':float(np.linalg.det(q))},'software':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'scikit_learn':sklearn.__version__}}
    (out/'run_manifest.json').write_text(json.dumps(man,indent=2,sort_keys=True))
    f2=S[S.model_family=='hist_gradient_boosting'].iloc[0]; f1=S[S.model_family=='logistic_l2'].iloc[0]
    text=f'''# E-Tabular basis v2 locked verdict\n\nGradient boosting: **{f2.locked_interpretation}**.\n- AUROC R0={f2.r0_auroc:.6f}, R1={f2.r1_auroc:.6f}, delta={f2.delta_auroc_r1_minus_r0:+.6f}\n- Spearman={f2.spearman_r0_r1:.6f}\n- RIDI@100={f2.ridi_100:.6f}; RIDI@500={f2.ridi_500:.6f}; RIDI@1000={f2.ridi_1000:.6f}\n\nLogistic equivariance control: **{f1.locked_interpretation}**.\n- AUROC R0={f1.r0_auroc:.6f}, R1={f1.r1_auroc:.6f}, delta={f1.delta_auroc_r1_minus_r0:+.6f}\n- Spearman={f1.spearman_r0_r1:.6f}\n- RIDI@100={f1.ridi_100:.6f}; max |score delta|={f1.max_abs_score_delta:.3e}\n\nThis v2 analysis is a separately timed mechanistic follow-up; it does not replace cross-modal v1.\n'''
    (out/'VERDICT.md').write_text(text); print(text)
    manifests=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!='RESULT_SHA256.csv': manifests.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha256(p)})
    pd.DataFrame(manifests).to_csv(out/'RESULT_SHA256.csv',index=False)
if __name__=='__main__': main()
