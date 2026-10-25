import argparse
import numpy as np
import pandas as pd
from .config import TABLES, FEATURE_SETS, TARGETS
from .data import load_survey
from .models import outer_splits, calculate_metrics


def evaluate_autogluon(seeds = (17,), outer_folds = 3, seconds_per_fold = 60):
    try:
        from autogluon.tabular import TabularPredictor
    except ImportError as exc:
        raise RuntimeError('Install optional requirements-automl.txt in a compatible environment') from exc
    TABLES.mkdir(parents = True, exist_ok = True)
    _, _, eligible = load_survey()
    results, predictions = [], []
    for outcome in TARGETS:
        for seed in seeds:
            sample, y, folds = outer_splits(eligible, outcome, seed, outer_folds)
            for scenario, features in FEATURE_SETS.items():
                all_true, all_pred, all_scores = [], [], []
                for fold, (tr, te) in enumerate(folds, 1):
                    X_train = sample.iloc[tr][features].copy().fillna('Missing')
                    X_test = sample.iloc[te][features].copy().fillna('Missing')
                    train = X_train.assign(__label = y[tr])
                    predictor = TabularPredictor(
                        label = '__label', problem_type = 'binary', eval_metric = 'roc_auc',
                        path = str(TABLES / 'autogluon_artifacts' / f'{outcome}_{scenario}_{seed}_{fold}'),
                        verbosity = 0,
                    ).fit(train_data = train, presets = 'medium_quality', time_limit = seconds_per_fold,
                          num_bag_folds = 0, num_stack_levels = 0)
                    scores = np.asarray(predictor.predict_proba(X_test, as_multiclass = False), dtype = float)
                    guesses = (scores >= 0.5).astype(int)
                    all_true.extend(y[te]); all_pred.extend(guesses); all_scores.extend(scores)
                    for index, actual, predicted, score in zip(te, y[te], guesses, scores):
                        predictions.append({'outcome': outcome, 'scenario': scenario, 'seed': seed,
                                            'outer_fold': fold, 'source_record_index': int(sample.iloc[index].source_record_index),
                                            'model': 'autogluon', 'y_true': int(actual),
                                            'y_pred': int(predicted), 'score': float(score)})
                results.append({'outcome': outcome, 'scenario': scenario, 'seed': seed,
                                'model': 'autogluon', **calculate_metrics(
                                    all_true, all_pred, all_scores, True)})
    scores = pd.DataFrame(results)
    scores.to_csv(TABLES / 'autogluon_seed_metrics.csv', index = False)
    pd.DataFrame(predictions).to_csv(TABLES / 'autogluon_oof_predictions.csv', index = False)
    return scores


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', nargs = '+', type = int, default = [17])
    parser.add_argument('--outer-folds', type = int, default = 3)
    parser.add_argument('--seconds-per-fold', type = int, default = 60)
    args = parser.parse_args()
    print(evaluate_autogluon(args.seeds, args.outer_folds, args.seconds_per_fold).to_string(index = False))


if __name__ == '__main__':
    main()
