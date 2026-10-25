import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.contingency_tables import Table2x2
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint
from .config import TARGETS, FEATURE_SETS
from .preprocessing import normalized


def prevalence_table(eligible):
    rows = []
    for target in TARGETS:
        y = eligible[target].dropna().astype(int)
        n, positives = len(y), int(y.sum())
        low, high = proportion_confint(positives, n, method = 'wilson', alpha = 0.05)
        rows.append({'outcome': target, 'positive': positives, 'negative': n - positives,
                     'n': n, 'rate': positives / n, 'wilson_95_low': low, 'wilson_95_high': high})
    return pd.DataFrame(rows)


def assumptions_audit(eligible):
    rows = []
    for target in TARGETS:
        frame = eligible[eligible[target].notna()]
        y = frame[target].astype(int)
        for scenario, features in FEATURE_SETS.items():
            for variable in features:
                counts = pd.crosstab(frame[variable].fillna('Missing'), y).reindex(columns = [0, 1], fill_value = 0)
                for category, row in counts.iterrows():
                    rows.append({'outcome': target, 'scenario': scenario, 'feature': variable,
                                 'category': str(category), 'n': int(row.sum()), 'negative': int(row[0]),
                                 'positive': int(row[1]), 'rare_under_3': bool(row.sum() < 3),
                                 'single_class': bool((row == 0).any())})
    return pd.DataFrame(rows)


def binary_exposures(eligible):
    df = pd.DataFrame(index = eligible.index)
    comparisons = {
        'large_firm': ('firm_size', lambda v: v == 'Large'),
        'fleet_over_ten': ('fleet_size', lambda v: v != '1-10'),
        'distance_over_sixty_km': ('daily_distance', lambda v: v in {'61-120 km/day', '>120 km/day'}),
        'preplanned_routes': ('route_planning', lambda v: v == 'Preplanned'),
        'logistics_sector': ('sector', lambda v: v == 'Logistics and parcel delivery')}
    for name, (feature, predicate) in comparisons.items():
        df[name] = eligible[feature].map(lambda v: np.nan if pd.isna(v) else int(predicate(v)))
    barrier_raw = eligible.iloc[:, 24].map(normalized)
    for name, token in {
        'barrier_acquisition_cost': 'alto costo de adquisicion',
        'barrier_charging_infrastructure': 'falta de infraestructura de recarga',
        'barrier_range': 'autonomia limitada'}.items():
        df[name] = barrier_raw.map(lambda v: np.nan if not v else int(token in v))
    return df


def fisher_associations(eligible):
    exposures = binary_exposures(eligible)
    rows = []
    for target in TARGETS:
        for name in exposures:
            paired = pd.DataFrame({'exposure': exposures[name], 'outcome': eligible[target]}).dropna()
            tab = pd.crosstab(paired.exposure.astype(int), paired.outcome.astype(int)).reindex(
                index = [0, 1], columns = [0, 1], fill_value = 0).to_numpy(dtype=int)
            if (tab.sum(axis=0) == 0).any() or (tab.sum(axis=1) == 0).any():
                continue
            odds_ratio, pvalue = fisher_exact(tab)
            ci = Table2x2(tab, shift_zeros=True).oddsratio_confint()
            rows.append({'outcome': target, 'exposure': name, 'n': int(tab.sum()),
                         'exposed_positives': int(tab[1,1]), 'exposed_n': int(tab[1].sum()),
                         'unexposed_positives': int(tab[0,1]), 'unexposed_n': int(tab[0].sum()),
                         'odds_ratio': odds_ratio, 'or_95_low_approx': ci[0],
                         'or_95_high_approx': ci[1], 'fisher_p': pvalue})
    result = pd.DataFrame(rows)
    if not result.empty:
        result['fdr_bh_q'] = result.groupby('outcome')['fisher_p'].transform(
            lambda series: multipletests(series, method = 'fdr_bh')[1])
        result = result.sort_values(['outcome', 'fisher_p']).reset_index(drop = True)
    return result


def sensitivity_table(original, eligible, source_indices):
    from .preprocessing import apply_cleaners
    raw_eligible = original.loc[original.iloc[:, source_indices['eligibility']].map(normalized).eq('si')].copy()
    raw_eligible = apply_cleaners(raw_eligible, source_indices)
    result = []
    for label, frame in (('deduplicated_main', eligible),
                         ('exact_duplicates_retained', raw_eligible)):
        for outcome in TARGETS:
            valid = frame[outcome].dropna()
            result.append({'analysis': label, 'outcome': outcome,
                           'n': len(valid), 'positive': int(valid.sum()),
                           'rate': float(valid.mean())})
    frame = eligible.loc[(eligible.ev_use == 0) & eligible.ev_consideration.notna()]
    valid = frame.ev_consideration
    result.append({'analysis': 'current_nonadopters_only',
                   'outcome': 'ev_consideration', 'n': len(valid),
                   'positive': int(valid.sum()), 'rate': float(valid.mean())})
    return pd.DataFrame(result)
