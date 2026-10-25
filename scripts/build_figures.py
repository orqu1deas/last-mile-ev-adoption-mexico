"""Regenerate publication-style figures from respondent survey and saved OOF tables.

Run from repository root: python scripts/build_figures.py
Sensitive source and respondent-level results must remain private.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
from src.ev_research.data import load_survey
from src.ev_research.statistics import fisher_associations
from src.ev_research.config import SOURCE_INDEX,TABLES,FIGURES
from src.ev_research.figures import (plot_eligibility_and_coverage,plot_operator_and_fleet,
    plot_observed_ev_outcomes,plot_distance_and_cost,plot_barriers_benefits_and_operations,
    plot_cleaning_quality,plot_sample_sensitivity,plot_segment_rates,
    plot_association_overview,plot_model_dashboard,plot_roc_dashboard,
    plot_precision_recall_and_confusion,plot_seed_stability)


def main():
    original,unique,eligible=load_survey()
    plot_eligibility_and_coverage(original,unique,eligible)
    plot_operator_and_fleet(eligible)
    plot_observed_ev_outcomes(eligible)
    plot_distance_and_cost(eligible)
    plot_barriers_benefits_and_operations(eligible)
    plot_cleaning_quality(eligible)
    plot_sample_sensitivity(eligible,original,SOURCE_INDEX)
    for target in ('ev_use','ev_consideration'):
        plot_segment_rates(eligible,target)
    plot_association_overview(fisher_associations(eligible))
    summary=pd.concat([pd.read_csv(TABLES/f'{x}_summary.csv') for x in ('ev_use','ev_consideration')])
    predictions=pd.concat([pd.read_csv(TABLES/f'{x}_predictions.csv') for x in ('ev_use','ev_consideration')])
    for target in ('ev_use','ev_consideration'):
        for scenario in ('fleet_baseline','operational_extended'):
            plot_model_dashboard(summary,target,scenario)
            plot_roc_dashboard(predictions,target,scenario,seed=42)
            plot_precision_recall_and_confusion(predictions,summary,target,scenario,seed=42)
        plot_seed_stability(summary,target)
    png=list(FIGURES.rglob('*.png'))
    svg=list(FIGURES.rglob('*.svg'))
    print(f'Exported {len(png)} PNG and {len(svg)} SVG figures to {FIGURES}')
    assert len(png)==24 and len(svg)==24, 'Unexpected chart inventory'

if __name__=='__main__':main()
