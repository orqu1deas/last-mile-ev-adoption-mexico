import pandas as pd
from .config import RAW_CSV, SOURCE_INDEX
from .preprocessing import normalized, apply_cleaners


def load_survey(path = RAW_CSV):
    original = pd.read_csv(path, dtype = str, keep_default_na = False, encoding = 'utf-8-sig')
    if original.shape[1] != 34:
        raise ValueError(f'Expected 34 source questionnaire columns, found {original.shape[1]}')
    unique = original.drop_duplicates().copy()
    eligible = unique.loc[
        unique.iloc[:, SOURCE_INDEX['eligibility']].map(normalized).eq('si')
    ].copy()
    eligible = apply_cleaners(eligible, SOURCE_INDEX)
    return original, unique, eligible


def sample_audit(raw, unique, eligible):
    records = [
        ('Original records', len(raw)),
        ('Exact duplicates', len(raw) - len(unique)),
        ('Unique response rows', len(unique)),
        ('Eligible unique responses', len(eligible)),
    ]
    for target in ('ev_use', 'ev_consideration'):
        valid = eligible[target].dropna()
        records.extend([
            (f'Valid {target} responses', len(valid)),
            (f'Positive {target} responses', int(valid.sum())),
        ])
    return pd.DataFrame(records, columns=['stage', 'n'])


def cleaning_audit(eligible):
    quality_cols = [c for c in eligible if c.endswith('_quality')]
    return (eligible[quality_cols].melt(var_name = 'variable', value_name = 'quality')
            .groupby(['variable', 'quality'], dropna=False).size()
            .rename('n').reset_index().sort_values(['variable', 'quality']))
