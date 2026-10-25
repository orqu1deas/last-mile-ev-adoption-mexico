import argparse
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from .config import TABLES, FEATURE_SETS
from .data import load_survey
from .models import outer_splits, estimator_specs, make_pipeline, fit_inner_search


def estimate_heldout_importance(seed = 17, n_outer = 3, n_inner = 3,
                                n_iter = 4, repeats = 15, scenarios = ('operational_extended',)):
    _, _, eligible = load_survey()
    rankings = pd.read_csv(TABLES / 'model_ranking.csv')
    rows = []
    for outcome in ('ev_use', 'ev_consideration'):
        sample, y, splits = outer_splits(eligible, outcome, seed, n_outer)
        for scenario in scenarios:
            top = rankings.query('outcome == @outcome and scenario == @scenario and rank == 1')
            if top.empty:
                raise ValueError('Missing model ranking for requested study scenario')
            model_name = str(top.iloc[0].model)
            features = FEATURE_SETS[scenario]
            X = sample[features]
            for fold, (tr, te) in enumerate(splits, 1):
                inner_seed = seed * 100 + fold
                model, parameters = estimator_specs(inner_seed)[model_name]
                pipe = make_pipeline(features, model)
                fitted, hp, inner_score = fit_inner_search(
                    pipe, parameters, X.iloc[tr], y[tr], inner_seed, n_inner, n_iter)
                permutation = permutation_importance(
                    fitted, X.iloc[te], y[te], scoring='balanced_accuracy',
                    n_repeats=repeats, random_state=inner_seed, n_jobs=1)
                for index, feature in enumerate(features):
                    for repetition, delta in enumerate(permutation.importances[index], 1):
                        rows.append({'outcome': outcome, 'scenario': scenario,
                                     'seed': seed, 'outer_fold': fold, 'model': model_name,
                                     'feature': feature, 'repetition': repetition,
                                     'balanced_accuracy_drop': float(delta)})
    result = pd.DataFrame(rows)
    result.to_csv(TABLES / 'heldout_permutation_importance_raw.csv', index = False)
    summary = (result.groupby(['outcome', 'scenario', 'model', 'feature'], as_index = False)
               .balanced_accuracy_drop.agg(['mean', 'std', 'count']))
    summary.to_csv(TABLES / 'heldout_permutation_importance_summary.csv', index = False)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type = int, default = 17)
    parser.add_argument('--repeats', type = int, default = 15)
    parser.add_argument('--search-iterations', type = int, default = 4)
    args = parser.parse_args()
    print(estimate_heldout_importance(seed = args.seed, repeats = args.repeats,
                                      n_iter = args.search_iterations).to_string(index = False))


if __name__ == '__main__':
    main()
