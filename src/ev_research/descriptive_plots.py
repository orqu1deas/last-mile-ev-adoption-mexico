import textwrap
import numpy as np
import pandas as pd
from .plotting_style import (PRIMARY, GOLD, CREAM, LIGHT_BLUE, MID_BLUE,
                             PALE_BLUE, MUTED, INK, make_panel, axis_style,
                             title_axis, export, set_percent)
from .config import SOURCE_INDEX
from .preprocessing import normalized


def _label_bars(ax, bars, values, suffix='', total = None, horizontal = False, fontsize = 10.5):
    for bar, value in zip(bars, values):
        label = f'{int(value)}' + (f' ({100 * value / total:.1f}%)' if total else suffix)
        if horizontal:
            ax.text(bar.get_width() + ax.get_xlim()[1] * .012,bar.get_y() + bar.get_height() / 2,
                    label, ha = 'left', va = 'center', fontsize = fontsize, color = INK)
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + ax.get_ylim()[1] * .01,
                    label, ha = 'center', va = 'bottom', fontsize = fontsize, color=INK)


def _bars_h(ax, labels, values, colors = None, total = None):
    values = list(values); labels = list(labels)
    if colors is None: colors = [PRIMARY] * len(values)
    upper = max(values + [1]) * 1.22
    ax.set_xlim(0, upper)
    bars = ax.barh(labels, values, color = colors, height = .58)
    ax.invert_yaxis()
    _label_bars(ax, bars, values, total = total, horizontal = True)
    axis_style(ax, 'x')
    return bars


def _counts(df, col, labels = None, top = None):
    counts = df[col].fillna('Missing').value_counts(dropna = False)
    if labels: counts = counts.reindex(labels, fill_value = 0)
    if top: counts = counts.head(top)
    return counts


def plot_eligibility_and_coverage(raw, unique, eligible):
    fig, axes = make_panel(2, 'Survey eligibility and respondent coverage',
        'Exact-row duplicates are excluded from the primary analytical sample.')
    fig.subplots_adjust(left = .145, right = .96, wspace = .38)
    first = [('Submitted', len(raw)), ('Unique rows', len(unique)), ('Eligible', len(eligible)),
           ('Not eligible', len(unique)-len(eligible))]
    _bars_h(axes[0], [r[0] for r in first], [r[1] for r in first], [PALE_BLUE, LIGHT_BLUE, MID_BLUE, PRIMARY])
    title_axis(axes[0],'Screening status')
    fields = [('Eligible',len(eligible)),('Firm size',eligible.firm_size.notna().sum()),
              ('Fleet size',eligible.fleet_size.notna().sum()),
              ('Daily distance',eligible.daily_distance.notna().sum())]
    labels = [r[0] for r in fields]; values = [r[1] for r in fields]
    bars = _bars_h(axes[1], labels, values,[PALE_BLUE, LIGHT_BLUE, MID_BLUE, PRIMARY])
    for item, bar in zip(fields, bars):
        for text in list(axes[1].texts):
            if abs(text.get_position()[1] - (bar.get_y() + bar.get_height() / 2)) < .02:
                text.set_text(f'{item[1]} / {len(eligible)}')
    title_axis(axes[1],'Field completeness (eligible respondents)')
    return export(fig,'01_data_quality','01_survey_eligibility_and_coverage')


def plot_operator_and_fleet(eligible):
    fig, axes = make_panel(2,'Normalized operator and fleet composition',
        'Equivalent answers are harmonized before counting; ambiguous and missing fleet-size responses remain explicit.')
    fig.subplots_adjust(left = .19, right = .96, wspace = .42)
    firms = _counts(eligible, 'firm_size', labels = ['Small', 'Medium', 'Large'])
    _bars_h(axes[0], ['Small (1–50 employees)', 'Medium (51–250 employees)', 'Large (>250 employees)'],
            firms.to_numpy())
    title_axis(axes[0], 'Firm size by employees')
    sizes = _counts(eligible, 'fleet_size', labels = ['1-10', '11-50', '51-200', '200-400', '>400', 'Missing'])
    unclassified = (eligible. fleet_size_quality == 'unclassified').sum()
    missing = (eligible.fleet_size_quality == 'missing').sum()
    counts = [*(sizes.iloc[:5].tolist()), int(unclassified), int(missing)]
    _bars_h(axes[1], ['1–10', '11–50', '51–200', '200–400', '>400', 'Unclassifiable', 'Missing'], counts)
    title_axis(axes[1], 'Small-cargo fleet size')
    return export(fig, '02_eda', '01_operator_and_fleet_composition')


def plot_observed_ev_outcomes(eligible):
    fig, axes = make_panel(2,'Observed EV use and consideration',
        'Question-specific denominators; percentages describe responding eligible operators.')
    for ax, col, title in zip(axes, ['ev_use','ev_consideration'], ['Current EV operation','Considered EV inclusion']):
        valid = eligible[col].dropna().astype(int)
        counts = [int(valid.sum()), int((1-valid).sum())]
        ax.set_ylim(0, max(counts) * 1.27)
        bars = ax.bar(['Yes','No'], counts, color = [PRIMARY, PALE_BLUE], width = .62)
        _label_bars(ax, bars, counts, total = len(valid), fontsize=12)
        axis_style(ax, 'y')
        title_axis(ax, f'{title} (n={len(valid)})')
    return export(fig,'01_data_quality', '02_observed_ev_use_and_consideration')


def plot_distance_and_cost(eligible):
    fig, axes = make_panel(2,'Operating distance and vehicle acquisition cost',
        'Original questionnaire bands are retained; unclassifiable distances are not treated as observed kilometers.')
    fig.subplots_adjust(left = .18, right = .96, wspace = .42)
    vals = _counts(eligible, 'daily_distance', labels=['<20 km/day', '31-60 km/day', '61-120 km/day', '>120 km/day', 'Missing'])
    unit_mismatch = int((eligible.daily_distance_quality == 'incompatible_unit').sum())
    cross = int((eligible.daily_distance_quality == 'crosses_120km_threshold').sum())
    not_class = int(eligible.daily_distance.isna().sum() - unit_mismatch - cross - int((eligible.daily_distance_quality == 'missing').sum()))
    labels = ['<20 km/day', '31–60 km/day', '61–120 km/day', '>120 km/day', 'Incompatible unit', 'Crosses bands', 'Other missing/unclear']
    values = [*vals.iloc[:4].tolist(), unit_mismatch,cross, max(0, not_class + int((eligible.daily_distance_quality == 'missing').sum()))]
    _bars_h(axes[0], labels, values)
    title_axis(axes[0], 'Reported daily travel distance')
    cost = eligible.iloc[:,10].astype(str).replace('', 'Missing').value_counts()
    labels = [textwrap.shorten(str(x).replace(' – ', '–'), width = 30,placeholder = '…') for x in cost.index[:7]]
    _bars_h(axes[1], labels,cost.values[:7], [PRIMARY] + [MID_BLUE] * (min(6, len(cost) - 1)))
    title_axis(axes[1], 'Reported acquisition-cost bands (MXN)')
    return export(fig, '02_eda', '02_distance_and_acquisition_cost',
                  'Daily-distance and cost categories are ordinal; no reliable EV payback estimate is implied.')


def _multi_choice_counts(eligible, index, map_labels):
    raw = eligible.iloc[:, index].map(normalized)
    valid = raw[raw != '']
    counts = {label:int(valid.map(lambda response: any(term in response for term in (tokens if isinstance(tokens, tuple) else (tokens,)))).sum())
              for label, tokens in map_labels.items()}
    return pd.Series(counts).sort_values(ascending=False),len(valid)


def plot_barriers_benefits_and_operations(eligible):
    barriers = {
        'Charging infrastructure': ('infraestructura de recarga', 'infraestructura de carga',
                                    'instalar centros de carga', 'instalaciones de carga',
                                    'adecuar instalaciones de carga'),
        'Driving range': ('autonomia limitada', 'autonomia suficiente', 'baja de autonomia',
                          'sin bateria', 'autonomia de la bateria'),
        'Acquisition price': 'alto costo de adquisicion',
        'Specialized maintenance': 'mantenimiento especializado',
        'Long charging times': ('tiempos de recarga prolongados', 'tiempo de carga',
                                'tiempos de carga')}
    benefits = {
        'Emission reductions': ('reduccion de emisiones', 'reduce las emisiones',
                                'cero emisiones', 'huella de carbono'),
        'Operating-cost savings': ('menores costos de operacion', 'ahorro en',
                                   'reduce costos'),
        'Sustainable image': ('imagen sostenible', 'magen de empresa'),
        'Lower urban noise': 'menor ruido',
        'Incentives': 'incentivos'}
    b, n_b = _multi_choice_counts(eligible, 24, barriers)
    a, n_a = _multi_choice_counts(eligible, 23, benefits)
    fig, axes = make_panel(3, 'Perceived EV barriers, advantages and route planning',
        'Respondents could select multiple benefits and barriers; each panel has its own denominator.',
        height = 7.3, width_per_panel = 5.6)
    fig.subplots_adjust(left = .19, right = .97, wspace = .64)
    _bars_h(axes[0], b.index.tolist(), b.values.tolist(), [PRIMARY] * len(b))
    title_axis(axes[0], f'Perceived barriers (n={n_b})')
    _bars_h(axes[1], a.index.tolist(), a.values.tolist(), [MID_BLUE] * len(a))
    title_axis(axes[1],f'Perceived benefits (n={n_a})')
    planned = _counts(eligible,'route_planning',labels = ['Mixed','Dynamic','Preplanned','Missing'])
    _bars_h(axes[2], planned.index.tolist(),planned.values.tolist(), [PRIMARY, MID_BLUE, LIGHT_BLUE, PALE_BLUE])
    title_axis(axes[2], 'Route planning approach')
    return export(fig, '02_eda', '03_barriers_benefits_and_route_planning',
                  'Multi-select counts can sum to more than the number of respondents.')


def plot_segment_rates(eligible,outcome):
    valid = eligible.loc[eligible[outcome].notna()].copy()
    heading = 'Current EV use' if outcome == 'ev_use' else 'EV consideration'
    fig, axes = make_panel(3, f'{heading} by operating segment',
        'Within-segment sample percentages; small denominators may produce unstable rates.',
        height = 7.1, width_per_panel = 5.5)
    configs = [('firm_size', ['Small', 'Medium', 'Large'], 'Firm size'),
               ('fleet_size', ['1-10', '11-50', '51-200', '200-400', '>400'], 'Fleet size'),
               ('daily_distance', ['<20 km/day', '31-60 km/day', '61-120 km/day', '>120 km/day'], 'Daily distance')]
    fig.subplots_adjust(left = .18, right = .97, wspace = .62)
    for ax,(col, levels, heading_axis) in zip(axes, configs):
        stats = valid.groupby(col, dropna = True)[outcome].agg(['sum', 'count']).reindex(levels).dropna(subset = ['count'])
        stats = stats[stats['count']>0]
        values = (stats['sum'] / stats['count']).to_numpy()
        labels = [s.replace(' km/day', ' km/d') for s in stats.index]
        bars = ax.barh(labels, values, color = [PRIMARY if n >= 5 else GOLD for n in stats['count']], height = .58)
        ax.invert_yaxis(); ax.set_xlim(0, 1.22); ax.xaxis.set_major_formatter(__import__('matplotlib').ticker.PercentFormatter(1))
        axis_style(ax,'x'); title_axis(ax,heading_axis)
        for bar, score, count in zip(bars, values, stats['count']):
            ax.text(score + .012, bar.get_y() + bar.get_height() / 2, f'{score:.0%} (n = {int(count)})',
                    va = 'center', fontsize = 9.7, color = INK)
    section = '03_ev_use' if outcome == 'ev_use' else '04_ev_consideration'
    return export(fig, section, '01_operator_segment_rates',
                  'Gold flags n<5; subgroup comparisons are exploratory and not causal.')


def plot_cleaning_quality(eligible):
    columns = ['firm_size', 'fleet_size', 'vehicle_type', 'daily_distance', 'acquisition_type', 'route_planning', 'sector']
    fig, axes = make_panel(2,'Survey harmonization and missingness audit',
        'Every original answer remains available; derived categories preserve normalization-quality flags.')
    fig.subplots_adjust(left = .22, right = .96, wspace = .45)
    complete = [int(eligible[col].notna().sum()) for col in columns]
    incomplete = [len(eligible) - v for v in complete]
    ys = np.arange(len(columns))
    axes[0].barh(ys, complete, color = PRIMARY, label = 'Classifiable')
    axes[0].barh(ys, incomplete, left = complete,color = PALE_BLUE, label = 'Unclassifiable / missing')
    axes[0].set_yticks(ys, [x.replace('_', ' ').title() for x in columns]); axes[0].invert_yaxis()
    axes[0].set_xlim(0, len(eligible) * 1.12); axes[0].legend(frameon = False, loc = 'lower right')
    axis_style(axes[0], 'x');title_axis(axes[0], 'Canonical predictor completeness')
    dist = eligible.daily_distance_quality.value_counts()
    _bars_h(axes[1], list(dist.index[:7]), list(dist.values[:7]))
    title_axis(axes[1], 'Daily-distance recoding decisions')
    return export(fig, '01_data_quality','03_normalization_and_missingness',
                  'Ambiguous or incompatible distance units are not silently converted to km/day.')


def plot_sample_sensitivity(eligible, raw, source_indices):
    from .statistics import sensitivity_table
    sensitivity = sensitivity_table(raw, eligible, source_indices)
    a = sensitivity[sensitivity.outcome == 'ev_use'].set_index('analysis')
    b = sensitivity[sensitivity.outcome == 'ev_consideration'].set_index('analysis')
    fig, axes = make_panel(2, 'How sample decisions change reported EV outcomes',
        'Exact-duplicate retention is a sensitivity analysis, not the primary specification.')
    fig.subplots_adjust(left = .20, right = .96, wspace = .43)
    for ax, data, name in zip(axes, [a, b],['Current EV use','Consideration of EVs']):
        keys = [k for k in ['deduplicated_main', 'exact_duplicates_retained', 'current_nonadopters_only'] if k in data.index]
        rates = [float(data.loc[k,'rate']) for k in keys]
        labels = [{'deduplicated_main' : 'Unique eligible responses',
                 'exact_duplicates_retained' : 'Duplicate rows retained',
                 'current_nonadopters_only' : 'Current non-users only'}[k] for k in keys]
        colors = [PRIMARY, MID_BLUE, GOLD][:len(keys)]
        bars = ax.barh(labels, rates, color = colors)
        ax.invert_yaxis();ax.set_xlim(0, .8)
        ax.xaxis.set_major_formatter(__import__('matplotlib').ticker.PercentFormatter(1))
        axis_style(ax, 'x');title_axis(ax, name)
        for bar, key, rate in zip(bars,keys,rates):
            row = data.loc[key]
            ax.text(rate + .015,bar.get_y()+bar.get_height() / 2,
                    f'{rate:.1%} ({int(row.positive)} / {int(row.n)})',va = 'center', fontsize = 10)
    return export(fig, '06_synthesis', '01_duplicate_and_nonadopter_sensitivity',
                  'Comparisons are descriptive; differing respondent sets do not identify a temporal adoption gap.')
