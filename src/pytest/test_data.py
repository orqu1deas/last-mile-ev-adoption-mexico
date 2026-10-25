'''Source-specific regression tests and deterministic transformation contracts.'''
from src.ev_research.data import load_survey, sample_audit
from src.ev_research.preprocessing import (
    binary_response, daily_distance, fleet_size, vehicle_type,
)
from src.ev_research.statistics import prevalence_table


def test_expected_source_shape_and_denominators():
    original, unique, eligible = load_survey()
    assert original.shape == (105, 34)
    assert len(unique) == 92
    assert len(eligible) == 62
    audit = sample_audit(original, unique, eligible).set_index('stage').n
    assert audit['Exact duplicates'] == 13
    assert audit['Valid ev_use responses'] == 60
    assert audit['Positive ev_use responses'] == 15
    assert audit['Valid ev_consideration responses'] == 59
    assert audit['Positive ev_consideration responses'] == 34


def test_canonicalization_preserves_ambiguity():
    assert fleet_size('1200') == ('>400', 'numeric_to_band')
    assert fleet_size('60% motos + 40% camiones pequenos')[0] != '>400'
    assert daily_distance('12km/ruta')[1] == 'incompatible_unit'
    assert daily_distance('100-150')[1] == 'crosses_120km_threshold'
    assert daily_distance('120')[0] == '61-120 km/day'
    assert vehicle_type('Motocicletas / triciclos Vans / pequeñas furgonetas')[0] == 'Mixed motorcycles and vans'


def test_target_encoding():
    assert binary_response('Mi flota incluye vehículos eléctricos', 'ev_consideration') == 1
    assert binary_response('No, ninguno', 'ev_use') == 0
    assert binary_response('Si, menos del 10% de la flota', 'ev_use') == 1
    assert binary_response('No', 'ev_consideration') == 0


def test_prevalence_agrees_with_verified_counts():
    _, _, eligible = load_survey()
    table = prevalence_table(eligible).set_index('outcome')
    assert table.loc['ev_use', 'rate'] == 0.25
    assert abs(table.loc['ev_consideration', 'rate'] - 34/59) < 1e-12


def test_sensitivity_examples():
    from src.ev_research.statistics import sensitivity_table
    from src.ev_research.config import SOURCE_INDEX
    original, _, eligible = load_survey()
    result = sensitivity_table(original, eligible, SOURCE_INDEX).set_index(['analysis', 'outcome'])
    assert result.loc[('exact_duplicates_retained', 'ev_use'), 'positive'] == 22
    assert result.loc[('current_nonadopters_only', 'ev_consideration'), 'positive'] == 19
    assert result.loc[('current_nonadopters_only', 'ev_consideration'), 'n'] == 44
