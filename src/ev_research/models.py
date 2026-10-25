import json
import warnings
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score,
    confusion_matrix, f1_score, precision_score, recall_score,
    roc_auc_score, brier_score_loss)
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.naive_bayes import BernoulliNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from lightgbm import LGBMClassifier
from .config import DEFAULT_SEEDS, FEATURE_SETS, TARGETS

ALL_MODELS = ('dummy', 'logistic_l2', 'logistic_l1', 'linear_svm',
              'decision_tree', 'bernoulli_nb', 'random_forest', 'lightgbm')


def estimator_specs(seed):
    return {
        'dummy': (DummyClassifier(strategy = 'prior'), {}),
        'logistic_l2': (LogisticRegression(l1_ratio = 0.0, solver = 'liblinear', class_weight = 'balanced',
                                            max_iter = 3000, random_state = seed), {'model__C': [0.1, 0.5, 2.0]}),
        'logistic_l1': (LogisticRegression(l1_ratio = 1.0, solver = 'liblinear', class_weight = 'balanced',
                                            max_iter = 3000, random_state = seed), {'model__C': [0.1, 0.5, 2.0]}),
        'linear_svm': (LinearSVC(class_weight = 'balanced', dual = False, max_iter = 10000,
                                  random_state = seed), {'model__C': [0.1, 0.5, 2.0]}),
        'decision_tree': (DecisionTreeClassifier(class_weight = 'balanced', random_state = seed),
                          {'model__max_depth': [1, 2, 3], 'model__min_samples_leaf': [3, 5, 8]}),
        'bernoulli_nb': (BernoulliNB(), {'model__alpha': [0.5, 1.0, 2.0]}),
        'random_forest': (RandomForestClassifier(class_weight = 'balanced', n_jobs = 1,
                                                  random_state = seed),
                          {'model__n_estimators': [100, 200], 'model__max_depth': [2, 3],
                           'model__min_samples_leaf': [3, 5, 8],
                           'model__max_features': ['sqrt', 0.7]}),
        'lightgbm': (LGBMClassifier(objective = 'binary', class_weight = 'balanced', n_jobs = 1,
                                    verbose = -1, random_state = seed, max_depth = 3),
                     {'model__n_estimators': [40, 80], 'model__num_leaves': [2, 3, 5],
                      'model__min_child_samples': [3, 6], 'model__learning_rate': [0.03, 0.1],
                      'model__reg_lambda': [1.0, 5.0]})}


def make_pipeline(features, estimator):
    categorical = Pipeline([
        ('imputer', SimpleImputer(strategy = 'constant', fill_value = 'Missing')),
        ('one_hot', OneHotEncoder(handle_unknown = 'infrequent_if_exist', min_frequency = 2))])
    transformer = ColumnTransformer([('categorical', categorical, features)], remainder = 'drop')
    return Pipeline([('preprocess', transformer), ('model', estimator)])


def probability_or_margin(fitted, X):
    if hasattr(fitted, 'predict_proba'):
        scores = np.asarray(fitted.predict_proba(X))[:, 1]
        return scores, True
    return np.asarray(fitted.decision_function(X), dtype = float), False


def calculate_metrics(y, predicted, score, is_probability):
    y = np.asarray(y, dtype=int)
    predicted = np.asarray(predicted, dtype = int)
    score = np.asarray(score, dtype = float)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels = [0, 1]).ravel()
    has_both = len(np.unique(y)) == 2
    return {
        'n': len(y), 'positives': int(y.sum()), 'accuracy': accuracy_score(y, predicted),
        'balanced_accuracy': balanced_accuracy_score(y, predicted), 'recall': recall_score(y, predicted, zero_division = 0),
        'specificity': tn / (tn + fp) if tn + fp else np.nan, 'precision': precision_score(y, predicted, zero_division = 0),
        'f1': f1_score(y, predicted, zero_division = 0), 'roc_auc': roc_auc_score(y, score) if has_both else np.nan,
        'average_precision': average_precision_score(y, score) if y.sum() else np.nan,
        'brier_score': brier_score_loss(y, score) if is_probability else np.nan,
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)}


def outer_splits(eligible, outcome, seed, n_outer=3):
    subset = eligible.loc[eligible[outcome].notna()].copy().reset_index(drop=False)
    subset = subset.rename(columns = {'index': 'source_record_index'})
    y = subset[outcome].astype(int).to_numpy()
    if np.bincount(y, minlength = 2).min() < n_outer:
        raise ValueError(f'Not enough cases of each class for {n_outer} outer folds: {outcome}')
    splitter = StratifiedKFold(n_splits = n_outer, shuffle = True, random_state = seed)
    return subset, y, list(splitter.split(subset, y))


def fit_inner_search(pipe, parameters, X_train, y_train, seed, n_inner = 3, n_iter = 4):
    if not parameters:
        return clone(pipe).fit(X_train, y_train), {}, np.nan
    inner_folds = min(n_inner, int(np.bincount(y_train, minlength = 2).min()))
    if inner_folds < 2:
        raise ValueError('Not enough minority-class observations for inner cross-validation')
    inner = StratifiedKFold(n_splits = inner_folds, shuffle = True, random_state = seed)
    available = int(np.prod([len(values) for values in parameters.values()]))
    search = RandomizedSearchCV(
        estimator = pipe, param_distributions = parameters, n_iter = min(n_iter, available),
        scoring = 'balanced_accuracy', cv = inner, refit = True, n_jobs = 1,
        random_state = seed, error_score = 'raise', return_train_score = False)
    search.fit(X_train, y_train)
    return search.best_estimator_, search.best_params_, float(search.best_score_)


def evaluate(eligible, seeds = DEFAULT_SEEDS, n_outer = 3, n_inner = 3, n_iter = 4,
             model_names = ALL_MODELS, scenarios = None, targets = None):
    chosen_scenarios = {k: FEATURE_SETS[k] for k in (scenarios or FEATURE_SETS)}
    chosen_targets = targets or TARGETS
    selected_models = tuple(model_names)
    invalid = set(selected_models) - set(ALL_MODELS)
    if invalid:
        raise ValueError(f'Unknown models: {sorted(invalid)}')
    folds, predictions, searches = [], [], []
    for target in chosen_targets:
        for seed in seeds:
            sample, y, splits = outer_splits(eligible, target, seed, n_outer)
            for scenario, features in chosen_scenarios.items():
                X = sample[features].copy()
                for fold_number, (train, test) in enumerate(splits, start = 1):
                    inner_seed = seed * 100 + fold_number
                    for name in selected_models:
                        estimator, parameters = estimator_specs(inner_seed)[name]
                        pipe = make_pipeline(features, estimator)
                        with warnings.catch_warnings():
                            warnings.filterwarnings('ignore', category = UserWarning,
                                                    message = '.*does not have valid feature names.*')
                            fitted, best_params, inner_score = fit_inner_search(
                                pipe, parameters, X.iloc[train], y[train], inner_seed,
                                n_inner = n_inner, n_iter = n_iter)
                        predicted = fitted.predict(X.iloc[test]).astype(int)
                        scores, proba = probability_or_margin(fitted, X.iloc[test])
                        meta = {'outcome': target, 'scenario': scenario, 'seed': seed,
                                'outer_fold': fold_number, 'model': name}
                        folds.append({**meta, **calculate_metrics(y[test], predicted, scores, proba)})
                        searches.append({**meta, 'inner_balanced_accuracy': inner_score,
                                         'best_parameters': json.dumps(best_params, sort_keys = True)})
                        for pos, actual, guess, score in zip(test, y[test], predicted, scores):
                            predictions.append({**meta, 'source_record_index': int(sample.iloc[pos]['source_record_index']),
                                                'y_true': int(actual), 'y_pred': int(guess),
                                                'score': float(score), 'is_probability': bool(proba)})
    fold_table = pd.DataFrame(folds)
    pred_table = pd.DataFrame(predictions)
    search_table = pd.DataFrame(searches)
    seed_scores = []
    group_columns = ['outcome', 'scenario', 'seed', 'model']
    for keys, group in pred_table.groupby(group_columns, sort = False):
        if group.source_record_index.duplicated().any():
            raise AssertionError(f'OOF duplication for {keys}')
        seed_scores.append({**dict(zip(group_columns, keys)),
                            **calculate_metrics(group.y_true, group.y_pred, group.score,
                                                bool(group.is_probability.iloc[0]))})
    seed_table = pd.DataFrame(seed_scores)
    metric_names = ['balanced_accuracy', 'roc_auc', 'average_precision', 'f1',
                    'recall', 'specificity', 'brier_score']
    aggregate = seed_table.groupby(['outcome', 'scenario', 'model'], as_index = False).agg(
        n=('n', 'first'), seeds = ('seed', 'nunique'),
        **{f'{name}_mean': (name, 'mean') for name in metric_names},
        **{f'{name}_sd': (name, 'std') for name in metric_names})
    return fold_table, seed_table, pred_table, search_table, aggregate


def ranking_table(summary):
    return (summary.sort_values(['outcome', 'scenario', 'balanced_accuracy_mean', 'average_precision_mean'],
                                ascending = [True, True, False, False])
            .assign(rank = lambda frame: frame.groupby(['outcome', 'scenario']).cumcount() + 1))
