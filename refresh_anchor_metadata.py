from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'

ANCHORS=[
 dict(pair_id='ADDI2-0457',drug_a='sevelamer',drug_b='enalapril',antiddi_tier='T2_moderate',anchor_type='human_crossover_pk',external_human_evidence='Human crossover PK study; no meaningful change in enalapril/enalaprilat exposure',source_citation='Burke SK et al. J Clin Pharmacol 2001;41:199-205',source_locator='https://doi.org/10.1177/00912700122009881',manuscript_reference=28,label_screen_context='label_explicit_NONinteraction',vertex_cover_drug='yes',anchor_role='illustrative_example'),
 dict(pair_id='ADDI2-0142',drug_a='sevelamer',drug_b='metoprolol',antiddi_tier='T1_wellpowered',anchor_type='human_crossover_pk',external_human_evidence='Human crossover PK study; exposure ratios approximately bioequivalent',source_citation='Burke SK et al. J Clin Pharmacol 2001;41:199-205',source_locator='https://doi.org/10.1177/00912700122009881',manuscript_reference=28,label_screen_context='label_explicit_NONinteraction',vertex_cover_drug='yes',anchor_role='illustrative_example'),
 dict(pair_id='ADDI2-0279',drug_a='sevelamer',drug_b='warfarin',antiddi_tier='T2_moderate',anchor_type='human_crossover_pk',external_human_evidence='Human crossover PK study; warfarin exposure unchanged',source_citation='Burke S et al. J Clin Pharmacol 2001;41:193-198',source_locator='https://doi.org/10.1177/00912700122009872',manuscript_reference=27,label_screen_context='label_explicit_NONinteraction',vertex_cover_drug='yes',anchor_role='illustrative_example'),
 dict(pair_id='ADDI2-0202',drug_a='levetiracetam',drug_b='warfarin',antiddi_tier='T1_wellpowered',anchor_type='human_crossover_pk',external_human_evidence='Human repeated-dose study; R/S-warfarin PK and INR unchanged',source_citation='Ragueneau-Majlessi I et al. Epilepsy Res 2001;47:55-63',source_locator='https://doi.org/10.1016/S0920-1211(01)00293-5',manuscript_reference=29,label_screen_context='no_label_signal',vertex_cover_drug='yes',anchor_role='illustrative_example'),
 dict(pair_id='ADDI2-0171',drug_a='ustekinumab',drug_b='omeprazole',antiddi_tier='T1_wellpowered',anchor_type='regulatory_clinical_pharmacology',external_human_evidence="Regulatory clinical pharmacology in subjects with Crohn's disease; no clinically significant exposure change",source_citation='DailyMed STELARA (ustekinumab) prescribing information',source_locator='https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c77a9664-e3bb-4023-b400-127aa53bca2b',manuscript_reference=30,label_screen_context='no_label_signal',vertex_cover_drug='yes',anchor_role='illustrative_example'),
 dict(pair_id='ADDI2-0325',drug_a='ustekinumab',drug_b='dextromethorphan',antiddi_tier='T2_moderate',anchor_type='regulatory_clinical_pharmacology',external_human_evidence="Regulatory clinical pharmacology in subjects with Crohn's disease; no clinically significant exposure change",source_citation='DailyMed STELARA (ustekinumab) prescribing information',source_locator='https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c77a9664-e3bb-4023-b400-127aa53bca2b',manuscript_reference=30,label_screen_context='no_label_signal',vertex_cover_drug='yes',anchor_role='illustrative_example'),
 dict(pair_id='ADDI2-0151',drug_a='liraglutide',drug_b='acetaminophen',antiddi_tier='T1_wellpowered',anchor_type='regulatory_clinical_pharmacology',external_human_evidence='Regulatory clinical pharmacology; overall acetaminophen exposure (AUC) unchanged',source_citation='DailyMed liraglutide injection prescribing information',source_locator='https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4253be3b-bda6-4efd-8118-9c9538168a88',manuscript_reference=31,label_screen_context='no_label_signal',vertex_cover_drug='yes',anchor_role='illustrative_example')]
EXCLUDED=[dict(pair_id='ADDI2-0110',drug_a='liraglutide',drug_b='lisinopril',antiddi_tier='T1_wellpowered',source_citation='DailyMed liraglutide injection prescribing information',source_locator='https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4253be3b-bda6-4efd-8118-9c9538168a88',manuscript_reference=31,reported_finding='Lisinopril AUC -15%, Cmax -27%, Tmax delayed 6->8 h; change judged not clinically relevant',exclusion_reason='excluded_by_anchor_criterion: label documents a measured exposure change (lisinopril AUC -15%, Cmax -27%, Tmax 6->8 h) judged not clinically relevant, rather than an absence of meaningful change',anchor_role='assessed_and_excluded')]

def main():
    anchors=pd.DataFrame(ANCHORS); excluded=pd.DataFrame(EXCLUDED)
    anchors.to_csv(DATA/'clinical_anchor_pairs.csv',index=False); excluded.to_csv(DATA/'excluded_candidate_anchors.csv',index=False)
    amap=anchors.set_index('pair_id').to_dict('index'); exmap=excluded.set_index('pair_id').to_dict('index')
    for fn in ['antiddi_v3_dataset.csv','antiddi_v3_benchmark.csv']:
        p=DATA/fn; df=pd.read_csv(p)
        if 'clinical_anchor_exclusion_reason' not in df.columns: df['clinical_anchor_exclusion_reason']=''
        df['clinical_anchor_status']='NOT_ANCHORED'
        for c in ['clinical_anchor_type','clinical_anchor_source','clinical_anchor_locator','clinical_anchor_summary','clinical_anchor_concordance']:
            df[c]=''
        df['clinical_anchor_exclusion_reason']=''
        for i,pid in df['pair_id'].astype(str).items():
            a=amap.get(pid)
            if a:
                df.at[i,'clinical_anchor_status']='HUMAN_NONINTERACTION_ANCHOR'; df.at[i,'clinical_anchor_type']=a['anchor_type']; df.at[i,'clinical_anchor_source']=a['source_citation']; df.at[i,'clinical_anchor_locator']=a['source_locator']; df.at[i,'clinical_anchor_summary']=a['external_human_evidence']; df.at[i,'clinical_anchor_concordance']='CONCORDANT'
            e=exmap.get(pid)
            if e: df.at[i,'clinical_anchor_exclusion_reason']=e['exclusion_reason']
        df.to_csv(p,index=False)
    print('Refreshed seven illustrative anchors and one assessed-and-excluded anchor candidate.')
if __name__=='__main__': main()
