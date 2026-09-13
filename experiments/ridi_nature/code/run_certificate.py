import hashlib, json, math, os, platform, sys, time
import numpy as np
import pandas as pd

OUT=os.environ.get('OUTDIR','results/certificate')
os.makedirs(OUT, exist_ok=True)
LOCK='RIDI-NATURE-CROSSMODAL-CERTIFICATE-v1'
NS=[1000,5000,10000]
KS=[10,50,100,500,1000]
AMPS=[0,0.01,0.02,0.05,0.10,0.20]
REPS=2000

def seed_for(*parts):
    s='|'.join(map(str,(LOCK,)+parts)).encode()
    return int.from_bytes(hashlib.sha256(s).digest()[:8],'big') % (2**32-1)

def riditop_from_order(order0, order1, k):
    a=set(order0[:k]); b=set(order1[:k])
    return 1-len(a&b)/len(a|b)

rows=[]
t0=time.time()
for n in NS:
    valid_ks=[k for k in KS if k<n]
    for rep in range(REPS):
        rng0=np.random.default_rng(seed_for(n,rep,'baseline'))
        s0=rng0.standard_normal(n)
        order0=np.argsort(-s0, kind='mergesort')
        ranks0=np.empty(n, dtype=np.int32); ranks0[order0]=np.arange(1,n+1,dtype=np.int32)
        sd=float(s0.std(ddof=0))
        margins={k: float(s0[order0[k-1]]-s0[order0[k]]) for k in valid_ks}
        for a in AMPS:
            eps=a*sd
            rng=np.random.default_rng(seed_for(n,rep,'amp',a))
            delta=rng.uniform(-eps,eps,size=n) if eps>0 else np.zeros(n)
            s1=s0+delta
            order1=np.argsort(-s1, kind='mergesort')
            ranks1=np.empty(n, dtype=np.int32); ranks1[order1]=np.arange(1,n+1,dtype=np.int32)
            d=ranks0.astype(np.int64)-ranks1.astype(np.int64)
            rho=float(1 - 6*np.dot(d,d)/(n*(n*n-1)))
            for k in valid_ks:
                gamma=margins[k]
                cert=bool(gamma>2*eps)
                ridi=riditop_from_order(order0,order1,k)
                stable=(ridi==0.0)
                rows.append((n,k,rep,a,eps,gamma,cert,stable,ridi,rho))
    print('done n',n,'elapsed',time.time()-t0, flush=True)

cols=['n','k','rep','amplitude','epsilon','gamma_k','certified','stable','ridi','spearman']
df=pd.DataFrame(rows, columns=cols)
df.to_csv(os.path.join(OUT,'certificate_cases.csv.gz'), index=False, compression='gzip')
agg=df.groupby(['n','k','amplitude']).agg(
    cases=('ridi','size'), certificate_coverage=('certified','mean'), stability_rate=('stable','mean'),
    mean_ridi=('ridi','mean'), median_ridi=('ridi','median'), mean_spearman=('spearman','mean')).reset_index()
fc=df.assign(false_cert=lambda x: x.certified & (~x.stable)).groupby(['n','k','amplitude'])['false_cert'].sum().reset_index(name='false_certificates_actual')
agg=agg.merge(fc,on=['n','k','amplitude'])
agg['unstable_among_uncertified']=np.nan
for idx,row in agg.iterrows():
    mask=(df.n==row.n)&(df.k==row.k)&(df.amplitude==row.amplitude)&(~df.certified)
    if mask.any(): agg.at[idx,'unstable_among_uncertified']=float((~df.loc[mask,'stable']).mean())
agg.to_csv(os.path.join(OUT,'certificate_summary.csv'),index=False)
result={'protocol_lock':LOCK,'n_cases':int(len(df)),'false_certificates':int(((df.certified)&(~df.stable)).sum()),
 'certified_cases':int(df.certified.sum()),'certified_stable_cases':int((df.certified&df.stable).sum()),
 'overall_nonzero_ridi_fraction':float((df.ridi>0).mean()),'elapsed_seconds':time.time()-t0,
 'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'platform':platform.platform()}
with open(os.path.join(OUT,'certificate_result.json'),'w') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
