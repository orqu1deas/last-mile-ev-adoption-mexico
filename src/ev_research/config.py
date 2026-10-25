''' src/ev_research/config.py

Centralized project paths, pre-specified study design, and plot colors.
'''

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / 'data' / 'raw' / 'survey_source.csv'
PROCESSED = ROOT / 'data' / 'processed'
OUTPUTS = ROOT / 'project-management' / 'reports'
TABLES = OUTPUTS / 'tables'
FIGURES = OUTPUTS / 'figures'

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
    'navy': '#1e3453', 'blue': '#1e3453', 'medium': '#6d88a6',
    'light': '#a3b7d5', 'pale': '#dbe6f0', 'ink': '#1e3453',
    'gray': '#61748b', 'grid': '#dee6ec', 'white': '#FFFFFF',
    'accent': '#cea64d', 'warn': '#cea64d', 'neutral': '#6d88a6',
    'cream': '#f9f0e1', 'offwhite': '#fdfbf7', 'gold': '#cea64d'}

def ensure_directories():
    for path in (PROCESSED, TABLES, FIGURES):
        path.mkdir(parents = True, exist_ok = True)