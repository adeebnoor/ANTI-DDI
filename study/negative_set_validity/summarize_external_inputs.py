from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from loaders import load_crescenddi,load_biosnap
root=Path(__file__).resolve().parent
P,N,_=load_crescenddi(); B,_,_=load_biosnap()
out={'CRESCENDDI_pairlevel':{'positive_pairs':len(P),'curated_negative_pairs':len(N)},'BioSNAP_ChCh':{'positive_edges':len(B),'nodes':len({x for e in B for x in e})}}
(root/'external_input_summary.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
assert len(P)>=100 and len(N)>=100 and len(B)>=1000
