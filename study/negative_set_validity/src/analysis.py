from __future__ import annotations
import itertools,os,sys
import numpy as np,pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0,os.path.dirname(__file__))
from models import NULL_MODELS
import protocols as PR
OUT=os.environ.get('DDI_OUT_DIR','results_external'); BOOT=5000; PERM=20000

def boot_ci(x,seed=0):
    x=np.asarray(x,float); rng=np.random.default_rng(seed); b=rng.choice(x,(BOOT,len(x)),replace=True).mean(1)
    return float(x.mean()),float(np.quantile(b,.025)),float(np.quantile(b,.975))
def signflip_p(x,seed=0):
    x=np.asarray(x,float); obs=abs(x.mean()); rng=np.random.default_rng(seed); signs=rng.choice([-1.,1.],(PERM,len(x))); vals=np.abs((signs*x).mean(1))
    return float((1+(vals>=obs).sum())/(PERM+1))
def holm(pvals):
    p=np.asarray(pvals,float); m=len(p); order=np.argsort(p); adj=np.empty(m); running=0
    for rank,ix in enumerate(order):
        val=(m-rank)*p[ix]; running=max(running,val); adj[ix]=min(1.,running)
    return adj
def valid(df): return df[(df.model!='__PROTOCOL__') & (df.status=='OK')].copy()

def inflation(df):
    out=[]
    for (bm,m),g in valid(df).groupby(['benchmark','model']):
        w=g.pivot(index='seed',columns='protocol',values='auc')
        if PR.STANDARD_PRACTICE not in w or 'P3_degree_matched' not in w: continue
        d=(w[PR.STANDARD_PRACTICE]-w['P3_degree_matched']).dropna()
        if len(d)<5: continue
        mu,lo,hi=boot_ci(d,abs(hash((bm,m)))%2**32); p=signflip_p(d,abs(hash(('p',bm,m)))%2**32)
        out.append(dict(benchmark=bm,model=m,auc_standard=w[PR.STANDARD_PRACTICE].mean(),auc_degree_matched=w['P3_degree_matched'].mean(),inflation=mu,ci_lo=lo,ci_hi=hi,p_raw=p,n_seeds=len(d)))
    res=pd.DataFrame(out)
    if len(res):
        res['p_holm']=np.nan
        for bm,idx in res.groupby('benchmark').groups.items(): res.loc[idx,'p_holm']=holm(res.loc[idx,'p_raw'].values)
    return res

def null_share(df):
    rows=[]
    for (bm,p),g in valid(df).groupby(['benchmark','protocol']):
        real=g[~g.model.isin(NULL_MODELS)]
        if real.empty: continue
        best=real.groupby('model').auc.mean().idxmax(); vals=[]
        for s,gs in g.groupby('seed'):
            a=gs.loc[gs.model=='M0_popularity','auc']; b=gs.loc[gs.model==best,'auc']
            if len(a) and len(b) and float(b.iloc[0])>0.5: vals.append((float(a.iloc[0])-.5)/(float(b.iloc[0])-.5))
        if vals:
            mu,lo,hi=boot_ci(vals,abs(hash((bm,p)))%2**32); rows.append(dict(benchmark=bm,protocol=p,best_model=best,null_share=mu,ci_lo=lo,ci_hi=hi,n_seeds=len(vals)))
    return pd.DataFrame(rows)

def ranking(df):
    rows=[]
    for bm,g in valid(df).groupby('benchmark'):
        tab=g.groupby(['protocol','model']).auc.mean().unstack(0)
        if PR.STANDARD_PRACTICE not in tab.columns: continue
        for corr in [p for p in PR.CORRECTIVE if p in tab.columns]:
            tau,pv=kendalltau(tab[PR.STANDARD_PRACTICE].rank(),tab[corr].rank()); rows.append(dict(benchmark=bm,protocol_a=PR.STANDARD_PRACTICE,protocol_b=corr,kendall_tau=tau,p_value=pv,n_models=len(tab.index)))
    return pd.DataFrame(rows)

def inversions(df):
    rows=[]
    for bm,g in valid(df).groupby('benchmark'):
        w=g.pivot_table(index='seed',columns=['protocol','model'],values='auc'); models=sorted(g.model.unique())
        for corr in sorted(PR.CORRECTIVE):
            if not all((corr,m) in w for m in models) or not all((PR.STANDARD_PRACTICE,m) in w for m in models): continue
            tmp=[]
            for m1,m2 in itertools.combinations(models,2):
                ds=(w[(PR.STANDARD_PRACTICE,m1)]-w[(PR.STANDARD_PRACTICE,m2)]).dropna(); dc=(w[(corr,m1)]-w[(corr,m2)]).dropna()
                if len(ds)<5 or len(dc)<5: continue
                ms,ls,hs=boot_ci(ds,1); mc,lc,hc=boot_ci(dc,2); ps=signflip_p(ds,3); pc=signflip_p(dc,4)
                tmp.append(dict(benchmark=bm,corrective=corr,model_a=m1,model_b=m2,delta_standard=ms,std_lo=ls,std_hi=hs,p_standard_raw=ps,delta_corrective=mc,corr_lo=lc,corr_hi=hc,p_corrective_raw=pc,order_reverses=bool(ms*mc<0)))
            if tmp:
                psadj=holm([x['p_standard_raw'] for x in tmp]); pcadj=holm([x['p_corrective_raw'] for x in tmp])
                for x,a,b in zip(tmp,psadj,pcadj): x['p_standard_holm']=a; x['p_corrective_holm']=b; x['significant_inversion_holm']=bool(x['order_reverses'] and a<.05 and b<.05); rows.append(x)
    return pd.DataFrame(rows)

def main():
    df=pd.read_csv(f'{OUT}/E2_auc.csv'); inf=inflation(df); inf.to_csv(f'{OUT}/A1_inflation.csv',index=False); ns=null_share(df); ns.to_csv(f'{OUT}/A2_null_share.csv',index=False); rk=ranking(df); rk.to_csv(f'{OUT}/A3_ranking_agreement.csv',index=False); inv=inversions(df); inv.to_csv(f'{OUT}/A4_rank_inversions_holm.csv',index=False)
    raw=pd.read_csv(f'{OUT}/E2_auc.csv'); raw.groupby(['benchmark','protocol','seed'],as_index=False).first()[['benchmark','protocol','seed','n_pos','n_neg','status']].to_csv(f'{OUT}/A5_protocol_diagnostics.csv',index=False)
    print('=== INFLATION (Holm within benchmark) ==='); print(inf.to_string(index=False)); print('\n=== NULL SHARE ==='); print(ns.to_string(index=False)); print('\n=== RANKING AGREEMENT ==='); print(rk.to_string(index=False))
    if len(inv):
        sig=inv[inv.significant_inversion_holm]; print(f'\n=== HOLM-SIGNIFICANT INVERSIONS: {len(sig)}/{len(inv)} ==='); print(sig[['benchmark','corrective','model_a','model_b','delta_standard','delta_corrective','p_standard_holm','p_corrective_holm']].to_string(index=False))
if __name__=='__main__': main()
