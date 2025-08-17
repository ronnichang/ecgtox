def build_subject_drug_map(annotation_csv, placebo_tpt=3.0):
    """
    Returns mapping {(subject, drug): {'baseline': [egrefids], 'post': [egrefids], 'fs': <Hz>?, 'meta': {…}}}
    Note: fs is read per-file later; stored here for convenience if needed.
    Placebo: use TPT == 3.0 (3 hours). Non-placebo: use max PCSTRESN timepoint.
    """
    import pandas as pd

    annot = pd.read_csv(annotation_csv)
    cols_kept = [ 'RANDID','EGREFID','EXTRT','BASELINE','TPT','PCSTRESN',
                  'SEX','AGE','HGHT','WGHT','SYSBP','DIABP','RACE','ETHNIC',]
    annot = annot[cols_kept].dropna(subset=['EGREFID','EXTRT'])
    annot['EXTRT'] = annot['EXTRT'].str.capitalize()

    mapping = {}
    for (subj, drug), group in annot.groupby(['RANDID','EXTRT']):
        meta = group.iloc[0][['SEX','AGE','HGHT','WGHT','SYSBP','DIABP','RACE','ETHNIC']].to_dict()
        base_ids = group[group['BASELINE']=='Y']['EGREFID'].tolist()
        nonbase = group[group['BASELINE']!='Y']

        if drug != 'Placebo':
            nonbase = nonbase.dropna(subset=['PCSTRESN'])
            if nonbase.empty:
                continue
            max_conc = nonbase['PCSTRESN'].max()
            max_group = nonbase[nonbase['PCSTRESN']==max_conc]
            max_tpt  = max_group['TPT'].iloc[0]
            post_ids = max_group[max_group['TPT']==max_tpt]['EGREFID'].tolist()
        else:
            max_conc = None
            max_tpt = placebo_tpt
            post_ids = nonbase[nonbase['TPT']==placebo_tpt]['EGREFID'].tolist()

        mapping[(int(subj), str(drug))] = {
            'meta': meta,
            'baseline': base_ids,
            'post': post_ids,
            'max_conc': max_conc,
            'tpt': max_tpt,
        }
    return mapping