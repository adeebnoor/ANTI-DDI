"""Evaluation-invariant graph link scores.

No model is fitted on held-out positive/negative labels. Every score is a
function only of the training adjacency matrix, so changing the evaluation
negative set cannot leak labels into model fitting.
"""
from __future__ import annotations
import numpy as np
from sklearn.decomposition import TruncatedSVD

REGISTRY = {}
NULL_MODELS = {'M0_popularity','M1_pref_attach'}

def register(name):
    def deco(fn): REGISTRY[name]=fn; return fn
    return deco

def pair_features(M, deg, idx, pairs):
    ii=np.array([idx[a] for a,_ in pairs],dtype=int); jj=np.array([idx[b] for _,b in pairs],dtype=int)
    Ai,Aj=M[ii],M[jj]
    inter=Ai*Aj
    cn=inter.sum(1)
    aa=(inter*np.where(deg>1,1.0/np.log(np.maximum(deg,2)),0.0)).sum(1)
    ra=(inter*np.where(deg>0,1.0/np.maximum(deg,1),0.0)).sum(1)
    uni=((Ai+Aj)>0).sum(1)
    jc=np.where(uni>0,cn/np.maximum(uni,1),0.0)
    da,db=deg[ii],deg[jj]
    return dict(cn=cn,aa=aa,ra=ra,jc=jc,da=da,db=db,pop=np.log1p(da)*np.log1p(db),pa=da*db)

def _simple(key):
    def fn(ctx,pairs): return pair_features(ctx['M'],ctx['deg'],ctx['idx'],pairs)[key]
    return fn
for n,k in [('M0_popularity','pop'),('M1_pref_attach','pa'),('M2_common_neigh','cn'),('M3_adamic_adar','aa'),('M4_resource_alloc','ra'),('M5_jaccard','jc')]:
    REGISTRY[n]=_simple(k)

def _cos_scores(emb, idx, pairs):
    A=np.array([emb[idx[a]] for a,_ in pairs]); B=np.array([emb[idx[b]] for _,b in pairs])
    den=np.linalg.norm(A,axis=1)*np.linalg.norm(B,axis=1)
    return np.sum(A*B,axis=1)/np.maximum(den,1e-12)

@register('M6_spectral_svd')
def spectral(ctx,pairs):
    cache=ctx['cache']
    if 'svd' not in cache:
        ncomp=max(2,min(32,ctx['M'].shape[0]-1))
        cache['svd']=TruncatedSVD(n_components=ncomp,random_state=0).fit_transform(ctx['M'])
    return _cos_scores(cache['svd'],ctx['idx'],pairs)

@register('M7_diffusion_svd')
def diffusion(ctx,pairs):
    cache=ctx['cache']
    if 'diff' not in cache:
        M=ctx['M'].astype(float); P=M/np.maximum(M.sum(1,keepdims=True),1.0); D=P+0.5*(P@P)
        ncomp=max(2,min(32,M.shape[0]-1))
        cache['diff']=TruncatedSVD(n_components=ncomp,random_state=0).fit_transform(D)
    return _cos_scores(cache['diff'],ctx['idx'],pairs)
