"""Graph construction and structural diagnostics."""
from __future__ import annotations
import numpy as np
from collections import defaultdict
class Graph:
    def __init__(self,edges,name='graph'):
        self.name=name; self.edges=sorted({tuple(sorted(e)) for e in edges if e[0]!=e[1]})
        self.nodes=sorted({x for e in self.edges for x in e}); self.idx={n:i for i,n in enumerate(self.nodes)}; self.N=len(self.nodes); self.eset=set(self.edges)
        d=defaultdict(int)
        for a,b in self.edges: d[a]+=1; d[b]+=1
        self.deg={n:d[n] for n in self.nodes}
    def adjacency(self,edge_subset=None):
        E=self.edges if edge_subset is None else edge_subset; M=np.zeros((self.N,self.N),dtype=np.float32)
        for a,b in E:
            i,j=self.idx[a],self.idx[b]; M[i,j]=M[j,i]=1.0
        return M

def gini(x):
    x=np.sort(np.asarray(x,dtype=float)); n=len(x)
    return 0.0 if x.sum()==0 else float((2*np.arange(1,n+1)-n-1).dot(x)/(n*x.sum()))

def greedy_vertex_cover(edges):
    E={tuple(sorted(e)) for e in edges}; cover=[]
    while E:
        c=defaultdict(int)
        for a,b in E: c[a]+=1; c[b]+=1
        v=max(c,key=c.get); cover.append(v); E={e for e in E if v not in e}
    return cover

def structural_report(g):
    degs=[g.deg[n] for n in g.nodes]; cover=greedy_vertex_cover(g.edges); rest=set(g.nodes)-set(cover)
    return dict(benchmark=g.name,n_edges=len(g.edges),n_nodes=g.N,density=2*len(g.edges)/(g.N*(g.N-1)) if g.N>1 else 0.0,mean_degree=float(np.mean(degs)),median_degree=float(np.median(degs)),max_degree=int(np.max(degs)),gini_degree=gini(degs),greedy_vertex_cover_size=len(cover),greedy_vertex_cover_fraction=len(cover)/g.N,complement_is_independent_set=not any(a in rest and b in rest for a,b in g.edges),top13_degree_share=float(sum(sorted(degs,reverse=True)[:13])/(2*len(g.edges))))
