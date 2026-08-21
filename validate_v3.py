from pathlib import Path
import sys
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; errors=[]
def check(cond,msg):
    if bool(cond): print(f'PASS: {msg}')
    else: print(f'FAIL: {msg}'); errors.append(msg)
v2=pd.read_csv(DATA/'antiddi_v2_dataset.csv'); v3=pd.read_csv(DATA/'antiddi_v3_dataset.csv'); bench=pd.read_csv(DATA/'antiddi_v3_benchmark.csv'); split=pd.read_csv(DATA/'paper5_split_manifest.csv'); anchors=pd.read_csv(DATA/'clinical_anchor_pairs.csv'); excluded=pd.read_csv(DATA/'excluded_candidate_anchors.csv'); original_cols=list(v2.columns)
check(len(v3)==797,'v3 has 797 audit records'); check(v3.pair_id.is_unique,'pair_id is unique'); check(list(v3.columns[:len(original_cols)])==original_cols,'original 35 v2 columns are preserved in order')
same=True
for col in original_cols:
    a,b=v2[col],v3[col]
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
        if not np.allclose(a.to_numpy(dtype=float),b.to_numpy(dtype=float),equal_nan=True,rtol=0,atol=1e-12): same=False; break
    else:
        eq=(a.astype('string')==b.astype('string')) | (a.isna() & b.isna())
        if not bool(eq.fillna(False).all()): same=False; break
check(same,'all original v2 values are unchanged (within CSV float precision)')
sc=v3.knowledge_state.value_counts().to_dict(); check(sc.get('ANTI_DDI_CANDIDATE_HIGHER_SUPPORT',0)==538,'538 higher-support candidates'); check(sc.get('ANTI_DDI_CANDIDATE_LIMITED',0)==106,'106 limited candidates'); check(sc.get('STRUCTURAL_CONTROL_ONLY',0)==44,'44 structural controls'); check(sc.get('UNRESOLVED',0)==76,'76 unresolved'); check(sc.get('POSITIVE_CONCERN_EXCLUDED',0)==33,'33 positive-concern exclusions')
check(len(bench)==538,'benchmark has 538 rows'); check(set(bench.knowledge_state)=={'ANTI_DDI_CANDIDATE_HIGHER_SUPPORT'},'benchmark contains only higher-support candidates'); check(set(bench.recommended_use)=={'DEFAULT_BENCHMARK_CANDIDATE'},'benchmark is explicitly candidate use'); check(set(bench.evidence_tier).issubset({'T1_wellpowered','T2_moderate'}),'benchmark contains only T1/T2')
sp=split['split'].value_counts().to_dict(); check(len(split)==214 and sp.get('development',0)==40 and sp.get('confirmatory',0)==174,'superseded experiment manifest retained for provenance only')
check(len(anchors)==7,'seven targeted illustrative clinical/regulatory anchors retained'); check(set(anchors.pair_id).issubset(set(bench.pair_id)),'all retained anchors belong to T1/T2 benchmark'); check((anchors.anchor_role=='illustrative_example').all(),'all retained anchors are explicitly illustrative'); check((anchors.vertex_cover_drug.astype(str).str.lower()=='yes').all(),'all retained anchors disclose vertex-cover concentration'); check((anchors.label_screen_context=='label_explicit_NONinteraction').sum()==3,'three anchors were already captured by label screen'); check((anchors.label_screen_context=='no_label_signal').sum()==4,'four anchors add direct source anchoring beyond label screen'); check(set(anchors.manuscript_reference)=={27,28,29,30,31},'anchor references match manuscript numbering'); check(~anchors.source_citation.str.contains('WEZLANA',case=False,na=False).any(),'no obsolete WEZLANA citation remains'); check(anchors.source_citation.str.contains('STELARA',case=False,na=False).sum()==2,'ustekinumab anchors cite STELARA')
check(len(excluded)==1 and excluded.pair_id.iloc[0]=='ADDI2-0110','liraglutide-lisinopril is preserved as assessed-and-excluded'); check('measured exposure change' in excluded.exclusion_reason.iloc[0],'excluded anchor carries explicit criterion-based reason'); check(v3.loc[v3.pair_id.eq('ADDI2-0110'),'clinical_anchor_status'].iloc[0]=='NOT_ANCHORED','ADDI2-0110 is not a retained anchor'); check(str(v3.loc[v3.pair_id.eq('ADDI2-0110'),'clinical_anchor_exclusion_reason'].iloc[0]).startswith('excluded_by_anchor_criterion'),'v3 carries exclusion reason')
check(not (v3.loc[v3.knowledge_state.eq('UNRESOLVED'),'recommended_use']=='DEFAULT_BENCHMARK_CANDIDATE').any(),'UNRESOLVED never default candidates'); check(not (v3.loc[v3.knowledge_state.eq('POSITIVE_CONCERN_EXCLUDED'),'recommended_use']=='DEFAULT_BENCHMARK_CANDIDATE').any(),'positive-concern exclusions never default candidates')
if errors: print(f'\n{len(errors)} check(s) failed.'); sys.exit(1)
print('\nAll Anti-DDI v3 submission semantic and release checks passed.')
