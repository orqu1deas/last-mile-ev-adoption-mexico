import re
import unicodedata
import numpy as np
import pandas as pd


def normalized(value):
    '''Normalize accent, punctuation spacing, and case.'''
    if value is None or pd.isna(value):
        return ''
    value = unicodedata.normalize('NFKD', str(value).strip().casefold())
    return ''.join(c for c in value if not unicodedata.combining(c))


def _dense(value):
    return re.sub(r'\s+', '', normalized(value).replace('–', '-').replace('—', '-'))


def binary_response(value, kind):
    answer = normalized(value)
    if not answer or answer in {'na', 'n/a', 'none'}:
        return np.nan
    if kind == 'ev_consideration' and 'mi flota incluye vehiculos electricos' in answer:
        return 1.0
    if answer == 'si' or answer.startswith('si,'):
        return 1.0
    if answer == 'no' or answer.startswith('no,'):
        return 0.0
    return np.nan


def firm_size(value):
    answer = normalized(value)
    for token, category in (('pequena', 'Small'), ('mediana', 'Medium'), ('grande', 'Large')):
        if token in answer:
            return category, 'mapped'
    return np.nan, 'missing' if not answer else 'unclassified'


def fleet_size(value):
    answer = _dense(value)
    if not answer:
        return np.nan, 'missing'
    known = {'1-10': '1-10', '11-50': '11-50', '51-200': '51-200',
             '200-400': '200-400', '201-400': '200-400', '>400': '>400'}
    if answer in known:
        return known[answer], 'mapped'
    if answer.isdigit():
        n = int(answer)
        if n <= 0:
            return np.nan, 'invalid'
        band = ('1-10' if n <= 10 else '11-50' if n <= 50 else
                '51-200' if n <= 200 else '200-400' if n <= 400 else '>400')
        return band, 'numeric_to_band'
    return np.nan, 'unclassified'


def vehicle_type(value):
    answer = normalized(value)
    if not answer or answer == 'no':
        return np.nan, 'missing'
    bikes = 'motocicletas' in answer or 'triciclos' in answer
    vans = 'vans' in answer or 'furgonetas' in answer
    if bikes and vans:
        return 'Mixed motorcycles and vans', 'mapped'
    if bikes:
        return 'Motorcycle/tricycle', 'mapped'
    if vans:
        return 'Van', 'mapped'
    if 'camiones' in answer:
        return 'Medium-duty truck', 'mapped'
    return 'Other', 'unclassified'


def daily_distance(value):
    answer = _dense(value)
    if not answer:
        return np.nan, 'missing'
    if any(token in answer for token in ('porviaje', '/ruta', '/ola')):
        return np.nan, 'incompatible_unit'
    bands = {
        'menosde20km': '<20 km/day', '31-60km': '31-60 km/day',
        '61-120km': '61-120 km/day', 'masde120km': '>120 km/day',
        '75-100': '61-120 km/day', '250-350': '>120 km/day',
    }
    if answer in bands:
        flag = 'mapped' if 'km' in answer else 'range_inferred_km_per_day'
        return bands[answer], flag
    if answer == '100-150':
        return np.nan, 'crosses_120km_threshold'
    if answer in {'120', '250'}:
        return ('61-120 km/day' if answer == '120' else '>120 km/day'), 'unit_inferred_from_question'
    return np.nan, 'unclassified'


def acquisition_type(value):
    answer = normalized(value)
    if not answer:
        return np.nan, 'missing'
    for token, category in (('nuevos', 'New purchase'), ('usados', 'Used purchase'),
                            ('leasing', 'Leasing'), ('arrendamiento', 'Leasing'),
                            ('subcontratacion', 'Outsourcing')):
        if token in answer:
            return category, 'mapped'
    return np.nan, 'unclassified'


def route_planning(value):
    answer = normalized(value)
    if 'preplanificadas' in answer:
        return 'Preplanned', 'mapped'
    if 'dinamicas' in answer:
        return 'Dynamic', 'mapped'
    if answer == 'mixto':
        return 'Mixed', 'mapped'
    return np.nan, 'missing' if not answer else 'unclassified'


def sector(value):
    answer = normalized(value)
    if not answer:
        return np.nan, 'missing'
    if 'no opero' in answer:
        return np.nan, 'inconsistent_with_screen'
    if any(token in answer for token in ('logistica', 'paqueteria', 'mensajeria', 'ultima milla',
                                         'reparto bajo demanda', 'transporte', 'e-commerce')):
        return 'Logistics and parcel delivery', 'mapped'
    if 'retail' in answer or 'comercio' in answer:
        return 'Retail', 'mapped'
    if 'servicio' in answer:
        return 'Services', 'mapped'
    if any(token in answer for token in ('alimentacion', 'distribucion', 'abastecimiento')):
        return 'Food and distribution', 'mapped'
    return 'Other', 'unclassified'

CLEANERS = {
    'firm_size': firm_size, 'fleet_size': fleet_size, 'vehicle_type': vehicle_type,
    'daily_distance': daily_distance, 'acquisition_type': acquisition_type,
    'route_planning': route_planning, 'sector': sector,}


def apply_cleaners(data, source_indices):
    result = data.copy()
    for key, cleaner in CLEANERS.items():
        original = result.iloc[:, source_indices[key]]
        output = [cleaner(value) for value in original]
        result[key] = [value for value, flag in output]
        result[f'{key}_quality'] = [flag for value, flag in output]
    for target in ('ev_use', 'ev_consideration'):
        result[target] = result.iloc[:, source_indices[target]].map(
            lambda value: binary_response(value, target))
    return result
