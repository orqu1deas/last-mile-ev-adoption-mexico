from .plotting_style import apply_style,axis_style as polish_axis,make_panel,export
from .descriptive_plots import (plot_eligibility_and_coverage,
    plot_operator_and_fleet,plot_observed_ev_outcomes,plot_distance_and_cost,
    plot_barriers_benefits_and_operations,plot_segment_rates,
    plot_cleaning_quality,plot_sample_sensitivity)
from .model_plots import (plot_model_dashboard,plot_roc_dashboard,
    plot_precision_recall_and_confusion,plot_seed_stability)
from .statistical_plots import plot_association_overview

def plot_survey_story(audit, prevalence):
    from .data import load_survey
    raw,unique,eligible = load_survey()
    plot_eligibility_and_coverage(raw, unique, eligible)
    return plot_observed_ev_outcomes(eligible)

def plot_fleet_profile(df):
    return plot_operator_and_fleet(df)

def plot_outcome_groups(df, outcome):
    return plot_segment_rates(df, outcome)
