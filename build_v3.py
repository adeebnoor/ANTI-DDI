#!/usr/bin/env python3
"""Deterministically rebuild Anti-DDI v3 release tables from the immutable v2 audit table."""
from pathlib import Path
import base64, json, zlib
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
PAPER5_ROLES_ZLIB_B64='eNp9mM2KVUEMhN/lrhU6laR/3Amz8TFk5g4IzlwZBkHEd1fcOCD1rYs+pyrpVJL+efl4d/dJ78dIXT5cHq7fr19v356uz6+Xd/+g/APd354fv7w8fX69vfx4ixVg7T854dgCbAN2PFbDUinBMVBeoLyAZgHNDsB8gjo9BCy7AYMkTGA5IZoTojmB5wSek3huG5Z5LLTCQyBggYAFt33BVdkDMEjChiRs0LBBwwYNG670AQ0HeB7geYDnmTZ9Z3nIZyHGACwAS8AasAkY8fRZiPBlEhJgoEEFGOgT8EzgktblAlpGQFuIsrUeYP0B1h9tm1708hDktUEA2G2A3QbYbYDdxoS7uWyPDTDHWPC7BXkF4wwwztg+5+CbsYHmBirgf3HAPcAbA7wxjr8tGnaEEBiSxvTHFhwDJiHA/GWRrAcILEeagIEEbcBAHkzF8lOxwMYENibwKoFXqSBkBSFrW0JqSCzMmwIjExiSvOloBRyDiIFZCQxJ4B6CqUswdQkmK4F7CNxD4B7pHSJHwbEJmK+hjAFYAAYSwo72qeEhH7AEh0hwgUxQBzt1pvXbLLvSZMPfYK/MBiYTvgmbV07IOZRewiyQUHoJy1DC4pLQuPMAF79JFGwENQRYAlaATcAWYP7iFpRlQeeusN25oKlX+GgKopmEeSbp81oFwuGdqKBZVkESoFtWWxco2BYKtoWCjaCgnAvKufxLSkHFFkzvBc2yoFnWtpNVwRTew04zDQXbf4vSHPNXrKG2OmzKGxbxlm0KDTXSsGt3enFpE94Ff4Nnz4bW1fCA2TBQNrSuhgfMhg23/6+DX78BPurZZA=='
CLINICAL_ANCHORS=[{'pair_id': 'ADDI2-0457', 'clinical_anchor_type': 'human_crossover_pk', 'clinical_anchor_source': 'Burke et al. 2001; sevelamer-enalapril', 'clinical_anchor_locator': 'https://doi.org/10.1177/00912700122009881', 'clinical_anchor_summary': 'Human crossover PK study; no meaningful change in enalapril/enalaprilat exposure', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0142', 'clinical_anchor_type': 'human_crossover_pk', 'clinical_anchor_source': 'Burke et al. 2001; sevelamer-metoprolol', 'clinical_anchor_locator': 'https://doi.org/10.1177/00912700122009881', 'clinical_anchor_summary': 'Human crossover PK study; exposure ratios approximately bioequivalent', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0279', 'clinical_anchor_type': 'human_crossover_pk', 'clinical_anchor_source': 'Burke et al. 2001; sevelamer-warfarin', 'clinical_anchor_locator': 'https://doi.org/10.1177/00912700122009872', 'clinical_anchor_summary': 'Human crossover PK study; warfarin exposure unchanged', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0202', 'clinical_anchor_type': 'human_repeated_dose_pk_pd', 'clinical_anchor_source': 'Ragueneau-Majlessi et al. 2001; levetiracetam-warfarin', 'clinical_anchor_locator': 'https://doi.org/10.1016/S0920-1211(01)00293-5', 'clinical_anchor_summary': 'Human repeated-dose study; R/S-warfarin PK and INR unchanged', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0171', 'clinical_anchor_type': 'regulatory_clinical_pharmacology', 'clinical_anchor_source': 'FDA WEZLANA prescribing information; ustekinumab CYP450 substrates', 'clinical_anchor_locator': 'https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/761285s006lbl761331s006lbl.pdf', 'clinical_anchor_summary': 'Phase 1 human CYP-probe study; no clinically significant exposure change', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0325', 'clinical_anchor_type': 'regulatory_clinical_pharmacology', 'clinical_anchor_source': 'FDA WEZLANA prescribing information; ustekinumab CYP450 substrates', 'clinical_anchor_locator': 'https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/761285s006lbl761331s006lbl.pdf', 'clinical_anchor_summary': 'Phase 1 human CYP-probe study; no clinically significant exposure change', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0110', 'clinical_anchor_type': 'regulatory_clinical_pharmacology', 'clinical_anchor_source': 'DailyMed liraglutide prescribing information; in-vivo oral-drug interaction studies', 'clinical_anchor_locator': 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=22c86976-9657-4dd0-8fff-0c3f3f08357c', 'clinical_anchor_summary': 'Human clinical-pharmacology study; tested oral-drug absorption not affected to a clinically relevant degree', 'clinical_anchor_concordance': 'CONCORDANT'}, {'pair_id': 'ADDI2-0151', 'clinical_anchor_type': 'regulatory_clinical_pharmacology', 'clinical_anchor_source': 'DailyMed liraglutide prescribing information; in-vivo oral-drug interaction studies', 'clinical_anchor_locator': 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=22c86976-9657-4dd0-8fff-0c3f3f08357c', 'clinical_anchor_summary': 'Human clinical-pharmacology study; tested oral-drug absorption not affected to a clinically relevant degree', 'clinical_anchor_concordance': 'CONCORDANT'}]


def state_and_use(row):
    tier=str(row['evidence_tier'])
    if tier.startswith('EXCLUDED') or bool(row['excluded_clinical']):
        return 'POSITIVE_CONCERN_EXCLUDED','EXCLUDE_POSITIVE_CONCERN'
    if tier in {'T1_wellpowered','T2_moderate'}:
        return 'ANTI_DDI_SUPPORTED','DEFAULT_BENCHMARK'
    if tier=='T3_limited':
        return 'ANTI_DDI_CANDIDATE_LIMITED','SENSITIVITY_ONLY'
    if tier=='T3_trivial_inert':
        return 'STRUCTURAL_CONTROL_ONLY','EXCLUDE_FROM_BENCHMARK'
    return 'UNRESOLVED','DO_NOT_LABEL_NEGATIVE'


def main():
    v2=pd.read_csv(DATA/'antiddi_v2_dataset.csv')
    v3=v2.copy()
    states=v3.apply(state_and_use,axis=1,result_type='expand')
    v3['knowledge_state']=states[0]
    v3['recommended_use']=states[1]
    roles=json.loads(zlib.decompress(base64.b64decode(PAPER5_ROLES_ZLIB_B64)).decode())
    v3['paper5_role']=v3['pair_id'].astype(str).map(roles).fillna('not_used_in_paper5')
    anchor_by={x['pair_id']:x for x in CLINICAL_ANCHORS}
    v3['clinical_anchor_status']='NOT_ANCHORED'
    for col in ['clinical_anchor_type','clinical_anchor_source','clinical_anchor_locator','clinical_anchor_summary','clinical_anchor_concordance']:
        v3[col]=''
    for idx,pid in v3['pair_id'].astype(str).items():
        a=anchor_by.get(pid)
        if a:
            v3.at[idx,'clinical_anchor_status']='HUMAN_NONINTERACTION_ANCHOR'
            for col in ['clinical_anchor_type','clinical_anchor_source','clinical_anchor_locator','clinical_anchor_summary','clinical_anchor_concordance']:
                v3.at[idx,col]=a[col]
    v3.to_csv(DATA/'antiddi_v3_dataset.csv',index=False)
    v3[v3['recommended_use'].eq('DEFAULT_BENCHMARK')].to_csv(DATA/'antiddi_v3_benchmark.csv',index=False)
    manifest=v3.loc[v3['paper5_role'].ne('not_used_in_paper5'),['pair_id','drug_a','drug_b','evidence_tier','paper5_role']].copy()
    manifest=manifest.rename(columns={'paper5_role':'split'})
    manifest['split_seed']=20260819
    manifest.to_csv(DATA/'paper5_split_manifest_compact.csv',index=False)
    anchors=v3.loc[v3['clinical_anchor_status'].eq('HUMAN_NONINTERACTION_ANCHOR'),[
      'pair_id','drug_a','drug_b','evidence_tier','clinical_anchor_status','clinical_anchor_type','clinical_anchor_source',
      'clinical_anchor_locator','clinical_anchor_summary','clinical_anchor_concordance']].copy()
    anchors.to_csv(DATA/'clinical_anchor_pairs_compact.csv',index=False)
    print(f"Wrote {len(v3)} v3 rows; {len(manifest)} Paper 5 rows; {len(anchors)} clinical anchors")

if __name__=='__main__':
    main()
