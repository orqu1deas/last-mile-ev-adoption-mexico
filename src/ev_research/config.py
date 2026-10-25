''' src/ev_research/config.py

Centralized project paths, pre-specified study design, and plot colors.
'''

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / 'data' / 'raw' / 'survey_source.csv'
PROCESSED = ROOT / 'data' / 'processed'
OUTPUTS = ROOT / 'project_management' / 'reports'
TABLES = ROOT / OUTPUTS / 'tables'
FIGURES = ROOT / OUTPUTS / 'figures'

# Column indices refer to the original 34-column questionnaire.
SOURCE_INDEX = {
    'eligibility' : 2, 'firm_size' : 3, 'fleet_size' : 4,
    'vehicle_type' : 5, 'daily_distance' : 7, 'acquisition_type' : 8,
    'route_planning' : 21, 'ev_consideration' : 22, 'ev_benefits' : 23,
    'ev_barriers' : 24, 'sector' : 26, 'ev_use' : 27
}

# Scenario names describe predictor sets.
FEATURE_SETS = {
    'fleet_baseline' : ['firm_size', 'fleet_size', 'vehicle_type'],
    'operational_extended' : ['firm_size', 'fleet_size', 'vehicle_type',
                              'daily_distance', 'acquisition_type',
                              'route_planning', 'sector']}
TARGETS = ('ev_use', 'ev_consideration')
DEFAULT_SEEDS = (17, 42, 123)

PALETTE = {
    'navy': '#123B63', 'blue': '#2367A0', 'medium': '#438ECD',
    'light': '#A9D0EF', 'pale': '#EAF3FA', 'ink': '#192B3A',
    'gray': '#697B8C', 'grid': '#DCE6EF', 'white': '#FFFFFF'}

def ensure_directories():
    for path in (PROCESSED, TABLES, FIGURES):
        path.mkdir(parents=True, exist_ok=True)