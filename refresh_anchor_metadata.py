from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

ROWS = [
    dict(pair_id='ADDI2-0457',drug_a='sevelamer',drug_b='enalapril',antiddi_tier='T2_moderate',external_human_evidence='Human crossover PK study; no meaningful change in enalapril/enalaprilat exposure',manuscript_reference=28,concordant=1,anchor_type='human_crossover_pk',source_citation='Burke et al. 2001; sevelamer-enalapril',source_locator='https://doi.org/10.1177/00912700122009881',analysis_status='targeted illustrative',label_screen_context='label_explicit_NONinteraction'),
    dict(pair_id='ADDI2-0142',drug_a='sevelamer',drug_b='metoprolol',antiddi_tier='T1_wellpowered',external_human_evidence='Human crossover PK study; exposure ratios approximately bioequivalent',manuscript_reference=28,concordant=1,anchor_type='human_crossover_pk',source_citation='Burke et al. 2001; sevelamer-metoprolol',source_locator='https://doi.org/10.1177/00912700122009881',analysis_status='targeted illustrative',label_screen_context='label_explicit_NONinteraction'),
    dict(pair_id='ADDI2-0279',drug_a='sevelamer',drug_b='warfarin',antiddi_tier='T2_moderate',external_human_evidence='Human crossover PK study; warfarin exposure unchanged',manuscript_reference=27,concordant=1,anchor_type='human_crossover_pk',source_citation='Burke et al. 2001; sevelamer-warfarin',source_locator='https://doi.org/10.1177/00912700122009872',analysis_status='targeted illustrative',label_screen_context='label_explicit_NONinteraction'),
    dict(pair_id='ADDI2-0202',drug_a='levetiracetam',drug_b='warfarin',antiddi_tier='T1_wellpowered',external_human_evidence='Human repeated-dose study; R/S-warfarin PK and INR unchanged',manuscript_reference=29,concordant=1,anchor_type='human_repeated_dose_pk_pd',source_citation='Ragueneau-Majlessi et al. 2001; levetiracetam-warfarin',source_locator='https://doi.org/10.1016/S0920-1211(01)00293-5',analysis_status='targeted illustrative',label_screen_context='no_label_signal'),
    dict(pair_id='ADDI2-0171',drug_a='ustekinumab',drug_b='omeprazole',antiddi_tier='T1_wellpowered',external_human_evidence="Regulatory clinical pharmacology in subjects with Crohn's disease; no clinically significant exposure change for named CYP-probe substrate",manuscript_reference=30,concordant=1,anchor_type='regulatory_clinical_pharmacology',source_citation="DailyMed STELARA prescribing information; CYP450 substrates in subjects with Crohn's disease",source_locator='https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c77a9664-e3bb-4023-b400-127aa53bca2b',analysis_status='targeted illustrative',label_screen_context='no_label_signal'),
    dict(pair_id='ADDI2-0325',drug_a='ustekinumab',drug_b='dextromethorphan',antiddi_tier='T2_moderate',external_human_evidence="Regulatory clinical pharmacology in subjects with Crohn's disease; no clinically significant exposure change for named CYP-probe substrate",manuscript_reference=30,concordant=1,anchor_type='regulatory_clinical_pharmacology',source_citation="DailyMed STELARA prescribing information; CYP450 substrates in subjects with Crohn's disease",source_locator='https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c77a9664-e3bb-4023-b400-127aa53bca2b',analysis_status='targeted illustrative',label_screen_context='no_label_signal'),
    dict(pair_id='ADDI2-0110',drug_a='liraglutide',drug_b='lisinopril',antiddi_tier='T1_wellpowered',external_human_evidence='Human clinical-pharmacology study; tested oral-drug absorption not affected to a clinically relevant degree',manuscript_reference=31,concordant=1,anchor_type='regulatory_clinical_pharmacology',source_citation='DailyMed liraglutide prescribing information; oral-drug interaction studies',source_locator='https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4253be3b-bda6-4efd-8118-9c9538168a88',analysis_status='targeted illustrative',label_screen_context='no_label_signal'),
    dict(pair_id='ADDI2-0151',drug_a='liraglutide',drug_b='acetaminophen',antiddi_tier='T1_wellpowered',external_human_evidence='Human clinical-pharmacology study; overall acetaminophen exposure unchanged',manuscript_reference=31,concordant=1,anchor_type='regulatory_clinical_pharmacology',source_citation='DailyMed liraglutide prescribing information; oral-drug interaction studies',source_locator='https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4253be3b-bda6-4efd-8118-9c9538168a88',analysis_status='targeted illustrative',label_screen_context='no_label_signal'),
]


def main():
    anchors = pd.DataFrame(ROWS)
    anchors['anchor_role'] = 'targeted illustrative example; concordant is descriptive only and not a validation-rate observation'
    anchors.to_csv(DATA / 'clinical_anchor_pairs.csv', index=False)

    amap = anchors.set_index('pair_id').to_dict('index')
    for name in ['antiddi_v3_dataset.csv', 'antiddi_v3_benchmark.csv']:
        path = DATA / name
        df = pd.read_csv(path)
        for idx, pid in df['pair_id'].astype(str).items():
            a = amap.get(pid)
            if not a:
                continue
            df.at[idx, 'clinical_anchor_status'] = 'HUMAN_NONINTERACTION_ANCHOR'
            df.at[idx, 'clinical_anchor_type'] = a['anchor_type']
            df.at[idx, 'clinical_anchor_source'] = a['source_citation']
            df.at[idx, 'clinical_anchor_locator'] = a['source_locator']
            df.at[idx, 'clinical_anchor_summary'] = a['external_human_evidence']
            # Kept for backwards compatibility only; selection conditioned on supportive outcome.
            df.at[idx, 'clinical_anchor_concordance'] = 'CONCORDANT'
        df.to_csv(path, index=False)
    print('Refreshed 8 targeted illustrative clinical anchors and v3 provenance fields.')

if __name__ == '__main__':
    main()
