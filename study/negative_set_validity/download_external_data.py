from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; (DATA/'crescenddi').mkdir(parents=True,exist_ok=True); (DATA/'biosnap').mkdir(parents=True,exist_ok=True)
SOURCES={
'crescenddi_positive':('https://raw.githubusercontent.com/elpidakon/CRESCENDDI/main/data_records/Data%20Record%201%20-%20Positive%20Controls.xlsx',DATA/'crescenddi'/'Data Record 1 - Positive Controls.xlsx'),
'crescenddi_negative':('https://raw.githubusercontent.com/elpidakon/CRESCENDDI/main/data_records/Data%20Record%202%20-%20Negative%20Controls.xlsx',DATA/'crescenddi'/'Data Record 2 - Negative Controls.xlsx'),
'biosnap_chch':('https://raw.githubusercontent.com/kexinhuang12345/SkipGNN/master/data/DDI/ChCh-Miner_durgbank-chem-chem.tsv',DATA/'biosnap'/'ChCh-Miner_durgbank-chem-chem.tsv')}
rows={}
for name,(url,path) in SOURCES.items():
    print('Downloading',name,url,flush=True); urllib.request.urlretrieve(url,path); b=path.read_bytes(); rows[name]={'url':url,'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
(ROOT/'external_source_manifest.json').write_text(json.dumps(rows,indent=2)+'\n'); print(json.dumps(rows,indent=2))
