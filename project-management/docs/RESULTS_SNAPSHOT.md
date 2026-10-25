# Experimental results snapshot — October 24, 2026

**Exploratory results, not claims of external model performance or population-wide rates.**

## Exact analysis configuration

- Three outer partition seeds: `[17, 42, 123]`; `3` outer stratified folds; `3` inner stratified folds; up to `4` hyperparameter candidates per model.
- Model families: dummy, logistic_l2, logistic_l1, linear_svm, decision_tree, bernoulli_nb, random_forest, lightgbm.
- Baseline: 3 fleet predictors; extended: 7 operational predictors.
- Exact original duplicates removed in the primary analysis; no firm identifier is available.

## Observed outcome prevalence

| Outcome | Positive | Valid | Sample rate |
|---|---:|---:|---:|
| ev_use | 15 | 60 | 25.0% |
| ev_consideration | 34 | 59 | 57.6% |

## Highest-ranked models by scenario

| Outcome | Scenario | Best-ranked classifier | Balanced accuracy mean ± across-seed SD | ROC-AUC mean | Average precision mean |
|---|---|---|---:|---:|---:|
| ev_consideration | fleet_baseline | linear_svm | 0.577 ± 0.042 | 0.675 | 0.746 |
| ev_consideration | operational_extended | bernoulli_nb | 0.598 ± 0.038 | 0.635 | 0.768 |
| ev_use | fleet_baseline | random_forest | 0.707 ± 0.074 | 0.703 | 0.460 |
| ev_use | operational_extended | random_forest | 0.726 ± 0.061 | 0.707 | 0.529 |

**Interpretation:** for current EV use, Random Forest ranked highest under both predictor scenarios, while the best-ranked classifier for consideration depended on the scenario. The current-use extended result still reflects approximately 60 respondents, of whom only 15 report adoption. In the consideration task, scores show modest improvements over majority-class balanced accuracy of 0.5. Ranking is not an independently validated superiority test.

## Sensitivity findings

- Current EV use: 15/60 (25.0%) with exact duplicates removed versus 22/69 (31.9%) if exact copies are retained.
- EV consideration: 34/59 (57.6%) with exact duplicates removed versus 42/67 (62.7%) if exact copies are retained.
- Among current EV nonusers: 19/44 (43.2%) report consideration; this is a different denominator and estimand.

## Exploratory associations and predictive feature importance

- Eight prespecified binary exposures were screened for each outcome using Fisher tests. None attained a Benjamini–Hochberg-adjusted q-value below 0.05 in this experiment.
- Held-out permutation importance on one seed suggests some changes in balanced accuracy when operational fields are shuffled; these results are exploratory because the model was first selected on the study CV results and predictors are correlated. Negative importance values were retained.

## Required caveats before publication

- This is a non-probability observational survey, not a measured national EV market adoption rate.
- Multiple random split seeds do not create independent research samples or provide validated confidence intervals for model performance.
- Selective reporting of the best model still creates winner-selection optimism, even though inner CV makes hyperparameter tuning independent of the outer fold.
- External validation, a frozen prospective protocol, respondent independence review, and source/legal review are required for stronger claims.
- Historical archived notebooks and the legal article are source material, not newly independently verified evidence.
