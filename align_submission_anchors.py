from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
anchors=pd.read_csv(DATA/'clinical_anchor_pairs.csv')
excluded=pd.read_csv(DATA/'excluded_candidate_anchors.csv')
amap=anchors.set_index('pair_id').to_dict('index')
exmap=excluded.set_index('pair_id').to_dict('index')

for fn in ['antiddi_v3_dataset.csv','antiddi_v3_benchmark.csv']:
    p=DATA/fn
    df=pd.read_csv(p)
    if 'clinical_anchor_exclusion_reason' not in df.columns:
        df['clinical_anchor_exclusion_reason']=''
    # Clear all previous anchor metadata, then reapply the tightened seven-example set.
    df['clinical_anchor_status']='NOT_ANCHORED'
    for c in ['clinical_anchor_type','clinical_anchor_source','clinical_anchor_locator','clinical_anchor_summary','clinical_anchor_concordance']:
        if c not in df.columns: df[c]=''
        else: df[c]=''
    df['clinical_anchor_exclusion_reason']=''
    for i,pid in df['pair_id'].astype(str).items():
        a=amap.get(pid)
        if a is not None:
            df.at[i,'clinical_anchor_status']='HUMAN_NONINTERACTION_ANCHOR'
            df.at[i,'clinical_anchor_type']=a['anchor_type']
            df.at[i,'clinical_anchor_source']=a['source_citation']
            df.at[i,'clinical_anchor_locator']=a['source_locator']
            df.at[i,'clinical_anchor_summary']=a['external_human_evidence']
            # Legacy field retained for schema compatibility; never aggregate as a validation rate.
            df.at[i,'clinical_anchor_concordance']='CONCORDANT'
        e=exmap.get(pid)
        if e is not None:
            df.at[i,'clinical_anchor_exclusion_reason']=e['exclusion_reason']
    df.to_csv(p,index=False)

full=pd.read_csv(DATA/'antiddi_v3_dataset.csv')
bench=pd.read_csv(DATA/'antiddi_v3_benchmark.csv')
assert len(full)==797 and len(bench)==538
assert (full.clinical_anchor_status=='HUMAN_NONINTERACTION_ANCHOR').sum()==7
assert (bench.clinical_anchor_status=='HUMAN_NONINTERACTION_ANCHOR').sum()==7
assert full.loc[full.pair_id.eq('ADDI2-0110'),'clinical_anchor_status'].iloc[0]=='NOT_ANCHORED'
assert full.loc[full.pair_id.eq('ADDI2-0110'),'clinical_anchor_exclusion_reason'].astype(str).str.len().iloc[0]>20
print('PASS: submission data aligned to seven illustrative anchors; ADDI2-0110 retained as assessed-and-excluded.')
