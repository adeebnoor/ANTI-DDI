"""Outcome-neutral negative-sampling protocols."""
from __future__ import annotations
import numpy as np
from collections import defaultdict

def _bin_map(nodes, deg, nbins=10):
    vals=np.array([deg[n] for n in nodes],dtype=float)
    qs=np.unique(np.quantile(vals,np.linspace(0,1,nbins+1)))
    if len(qs)<=2: return {n:0 for n in nodes}
    cuts=qs[1:-1]
    return {n:int(np.digitize(deg[n],cuts,right=True)) for n in nodes}

def p1_uniform_random(g,train_deg,test_pos,rng,k):
    out,guard=set(),0
    while len(out)<k and guard<max(10000,500*k):
        guard+=1; i,j=rng.integers(0,g.N,2)
        if i==j: continue
        p=tuple(sorted((g.nodes[i],g.nodes[j])))
        if p not in g.eset: out.add(p)
    return sorted(out)

def p2_degree_proportional(g,train_deg,test_pos,rng,k):
    w=np.array([train_deg[n] for n in g.nodes],dtype=float)+1e-6; w/=w.sum()
    out,guard=set(),0
    while len(out)<k and guard<max(10000,500*k):
        guard+=1; i,j=rng.choice(g.N,2,replace=True,p=w)
        if i==j: continue
        p=tuple(sorted((g.nodes[i],g.nodes[j])))
        if p not in g.eset: out.add(p)
    return sorted(out)

def p3_degree_matched(g,train_deg,test_pos,rng,k):
    """Match each held-out positive's unordered endpoint training-degree bins."""
    bmap=_bin_map(g.nodes,train_deg); bybin=defaultdict(list)
    for n in g.nodes: bybin[bmap[n]].append(n)
    out,used=[],set()
    for ix in rng.permutation(len(test_pos)):
        a,b=test_pos[ix]; A,B=bybin[bmap[a]],bybin[bmap[b]]; found=None
        for _ in range(400):
            x=A[int(rng.integers(0,len(A)))]; y=B[int(rng.integers(0,len(B)))]
            if x==y: continue
            p=tuple(sorted((x,y)))
            if p in g.eset or p in used: continue
            found=p; break
        if found is not None: used.add(found); out.append(found)
        if len(out)>=k: break
    return out

def p5_config_rewire(g,train_deg,test_pos,rng,k):
    """Degree-preserving rewiring of held-out positives, rejecting known positives."""
    cur=[tuple(sorted(p)) for p in test_pos]
    for _ in range(30*len(cur)):
        i,j=rng.integers(0,len(cur),2)
        if i==j: continue
        a,b=cur[i]; c,d=cur[j]
        if len({a,b,c,d})<4: continue
        n1,n2=(tuple(sorted((a,d))),tuple(sorted((c,b)))) if rng.random()<0.5 else (tuple(sorted((a,c))),tuple(sorted((b,d))))
        if n1 in g.eset or n2 in g.eset or n1==n2: continue
        cur[i],cur[j]=n1,n2
    out=[]; used=set()
    for p in cur:
        if p not in g.eset and p not in used: used.add(p); out.append(p)
        if len(out)>=k: break
    return out

def make_p4_curated(curated_pairs):
    C=sorted({tuple(sorted(p)) for p in curated_pairs})
    def p4_curated(g,train_deg,test_pos,rng,k):
        pool=[p for p in C if p[0] in g.idx and p[1] in g.idx and p not in g.eset]
        if not pool: return []
        idx=rng.permutation(len(pool))[:min(k,len(pool))]
        return [pool[int(i)] for i in idx]
    return p4_curated

BASE_PROTOCOLS={'P1_uniform_random':p1_uniform_random,'P2_degree_proportional':p2_degree_proportional,'P3_degree_matched':p3_degree_matched,'P5_config_rewire':p5_config_rewire}
CORRECTIVE={'P3_degree_matched','P5_config_rewire'}
STANDARD_PRACTICE='P1_uniform_random'
