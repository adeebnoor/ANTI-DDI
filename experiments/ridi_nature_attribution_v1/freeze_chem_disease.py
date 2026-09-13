#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, gzip, hashlib, heapq, io, json, tarfile, sys
from collections import Counter, defaultdict
from pathlib import Path

# Scientific constants copied from the frozen RTX protocol/code.
CHEM={"biolink:Drug","biolink:ChemicalEntity","biolink:ChemicalSubstance","biolink:SmallMolecule","biolink:MolecularMixture","biolink:ChemicalMixture"}
DISEASE={"biolink:Disease","biolink:PhenotypicFeature","biolink:DiseaseOrPhenotypicFeature"}
MAINT={"biolink:same_as","biolink:subclass_of","biolink:superclass_of","biolink:exact_match","biolink:close_match"}
SAME="biolink:same_as"
SALT="RTXKG2-20260817-v1"
CAP=10; NQ=200; MINDEG=5; MINC=2000; MAXC=5000
EXPECTED={
    "nodes_sha256":"35bb9deaeeeaef029f18a5a21c4dd3af0c55712f20f4bc985443ce1efe2ee231",
    "edges_sha256":"26b8b95035519412566c0bd74d0bbd9f4180636a4ab7ea3327938b1c60cf7ed3",
    "node_rows":10238961,
    "edge_rows":54041267,
    "same_as_nonnegated":564240,
    "non_singleton_components":213924,
    "chem_disease_unique_edges":915794,
    "chem_disease_primary_exposed":69510,
    "n_queries":200,
    "query_structure_sha256":"1291fa56e9074cbf41589b3e74f4fbc40687419ed44a7bb9800e9340e83e400e",
}

def raise_csv_field_limit():
    limit=sys.maxsize
    while True:
        try: csv.field_size_limit(limit); return limit
        except OverflowError: limit//=10
raise_csv_field_limit()

def sha256_file(path: Path, chunk=8*1024*1024):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(chunk),b''): h.update(b)
    return h.hexdigest()

def hkey(s): return hashlib.sha256(s.encode()).hexdigest()
def neg(v): return str(v).strip().lower() in {"true","1","yes"}

class DSU:
    def __init__(self): self.parent={}; self.size={}; self.min_id={}
    def add(self,x):
        if x not in self.parent:
            self.parent[x]=x; self.size[x]=1; self.min_id[x]=x
    def find(self,x):
        p=self.parent.get(x)
        if p is None: return None
        while p!=self.parent[p]:
            self.parent[p]=self.parent[self.parent[p]]; p=self.parent[p]
        r=p; p=x
        while p!=r:
            n=self.parent[p]; self.parent[p]=r; p=n
        return r
    def union(self,a,b):
        self.add(a); self.add(b); ra,rb=self.find(a),self.find(b)
        if ra==rb:return
        if self.size[ra]<self.size[rb]:ra,rb=rb,ra
        self.parent[rb]=ra; self.size[ra]+=self.size[rb]
        self.min_id[ra]=min(self.min_id[ra],self.min_id[rb])
        del self.size[rb]; del self.min_id[rb]
    def cfull(self,x):
        r=self.find(x); return self.min_id[r] if r and self.size[r]>1 else x
    def cprimary(self,x):
        r=self.find(x); return self.min_id[r] if r and 2<=self.size[r]<=CAP else x

def stream(archive,member):
    tf=tarfile.open(archive,'r:xz')
    fh=tf.extractfile(tf.getmember(member))
    return tf,io.TextIOWrapper(fh,encoding='utf-8',errors='replace',newline='')

def deterministic_gzip_text(path:Path):
    raw=path.open('wb')
    gz=gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0)
    txt=io.TextIOWrapper(gz,encoding='utf-8',newline='')
    return raw,gz,txt

def scan_nodes(path):
    chems=set(); diseases=set(); n=0
    tf,f=stream(path,'nodes.tsv'); r=csv.reader(f,delimiter='\t')
    for row in r:
        n+=1
        if len(row)<17: continue
        x,cat=row[7],row[16]
        if cat in CHEM: chems.add(x)
        if cat in DISEASE: diseases.add(x)
        if n%1_000_000==0: print('nodes',f'{n:,}',flush=True)
    f.close(); tf.close(); return chems,diseases,n

def scan_same(path):
    d=DSU(); total=same=neg_same=0
    tf,f=stream(path,'edges.tsv'); r=csv.reader(f,delimiter='\t')
    for row in r:
        total+=1
        if len(row)<16: continue
        if row[13]==SAME:
            if neg(row[2]): neg_same+=1
            else: same+=1; d.union(row[14],row[15])
        if total%2_000_000==0: print('same pass',f'{total:,}',flush=True)
    f.close(); tf.close()
    hist=Counter(d.size.values())
    return d,{"edge_rows":total,"same_as_nonnegated":same,"same_as_negated_excluded":neg_same,
              "non_singleton_components":sum(hist.values()),"component_size_histogram":dict(sorted(hist.items())),
              "primary_component_size_cap":CAP}

def orient(s,o,chems,diseases):
    if s in chems and o in diseases:return s,o
    if o in chems and s in diseases:return o,s
    return None

def scan_pairs(path,chems,diseases,dsu,outdir):
    pairs=set(); total=negx=maintx=0
    tf,f=stream(path,'edges.tsv'); r=csv.reader(f,delimiter='\t')
    for row in r:
        total+=1
        if len(row)<16:continue
        if neg(row[2]): negx+=1; continue
        p=row[13]
        if p in MAINT: maintx+=1; continue
        x=orient(row[14],row[15],chems,diseases)
        if x:pairs.add(x)
        if total%2_000_000==0: print('task pass',f'{total:,}','CD',len(pairs),flush=True)
    f.close();tf.close()
    pth=outdir/'chem_disease_frozen_edges.tsv.gz'
    raw,gz,g=deterministic_gzip_text(pth)
    w=csv.writer(g,delimiter='\t'); w.writerow(['raw_chem','raw_partner','primary_chem','primary_partner','full_chem','full_partner'])
    for c,p in sorted(pairs): w.writerow([c,p,dsu.cprimary(c),dsu.cprimary(p),dsu.cfull(c),dsu.cfull(p)])
    g.flush(); g.close(); raw.close()
    return pairs,{"edge_rows_scanned":total,"negated_rows_excluded":negx,"maintenance_rows_excluded":maintx}

def cand_sample(q,pool):
    key=lambda c:hkey(f'{SALT}|cand|{q}|{c}')
    return sorted(pool,key=key) if len(pool)<=MAXC else heapq.nsmallest(MAXC,pool,key=key)

def freeze_queries(pairs,outdir):
    c2p=defaultdict(set); p2c=defaultdict(set)
    for c,p in pairs: c2p[c].add(p); p2c[p].add(c)
    candidates=[c for c in c2p if len(c2p[c])>=MINDEG]
    candidates.sort(key=lambda c:hkey(f'{SALT}|query|chem_disease|{c}'))
    chosen=[]; meta=[]
    qpath=outdir/'chem_disease_query_candidates.tsv.gz'
    raw,gz,g=deterministic_gzip_text(qpath)
    w=csv.writer(g,delimiter='\t'); w.writerow(['query_raw_chem','candidate_raw_chem'])
    for q in candidates:
        pool=set()
        for p in c2p[q]: pool.update(p2c[p])
        pool.discard(q)
        if len(pool)<MINC:continue
        cs=cand_sample(q,pool)
        chosen.append(q)
        meta.append({"query":q,"raw_degree":len(c2p[q]),"raw_candidate_pool":len(pool),"frozen_candidates":len(cs)})
        for c in cs:w.writerow([q,c])
        if len(chosen)>=NQ:break
    g.flush();g.close();raw.close()
    spath=outdir/'chem_disease_query_structure.json'
    spath.write_text(json.dumps(meta,indent=2),encoding='utf-8')
    return {"n_queries":len(chosen),"query_structure_sha256":sha256_file(spath),
            "query_candidate_file":qpath.name,"query_structure_file":spath.name}

def content_sha_gzip(path):
    h=hashlib.sha256()
    with gzip.open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--download-dir',required=True); ap.add_argument('--out-dir',required=True)
    a=ap.parse_args(); d=Path(a.download_dir); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    upstream={"nodes_sha256":sha256_file(d/'nodes.tar.xz'),"edges_sha256":sha256_file(d/'edges.tar.xz')}
    if upstream['nodes_sha256']!=EXPECTED['nodes_sha256'] or upstream['edges_sha256']!=EXPECTED['edges_sha256']:
        raise RuntimeError(f'ABORT upstream SHA mismatch: {upstream}')
    chems,diseases,node_rows=scan_nodes(d/'nodes.tar.xz')
    dsu,same=scan_same(d/'edges.tar.xz')
    pairs,edge_scan=scan_pairs(d/'edges.tar.xz',chems,diseases,dsu,out)
    qstats=freeze_queries(pairs,out)
    exposed=sum(dsu.cprimary(c)!=c or dsu.cprimary(p)!=p for c,p in pairs)
    census={"node_rows":node_rows,"edge_rows":same['edge_rows'],"same_as_nonnegated":same['same_as_nonnegated'],
            "non_singleton_components":same['non_singleton_components'],"chem_disease_unique_edges":len(pairs),
            "chem_disease_primary_exposed":exposed,"n_queries":qstats['n_queries'],"query_structure_sha256":qstats['query_structure_sha256']}
    checks={k:{"expected":EXPECTED[k],"observed":census[k],"pass":census[k]==EXPECTED[k]} for k in census}
    if not all(x['pass'] for x in checks.values()):
        raise RuntimeError('ABORT frozen census mismatch:\n'+json.dumps(checks,indent=2))
    manifest=[]
    for p in sorted(out.iterdir()):
        if p.is_file(): manifest.append({"file":p.name,"bytes":p.stat().st_size,"sha256":sha256_file(p),
                                         "decompressed_sha256":content_sha_gzip(p) if p.suffix=='.gz' else None})
    summary={"purpose":"Rebuild of the prospectively frozen chemical-disease cache from exact upstream artifacts; no model outcome computed.",
             "upstream":upstream,"census":census,"checks":checks,"same_as":same,"edge_scan":edge_scan,
             "deterministic_gzip_mtime":0,"files":manifest}
    (out/'NATURE_FREEZE_REBUILD_VERIFICATION.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({"census":census,"all_checks_pass":True},indent=2))
if __name__=='__main__':main()
