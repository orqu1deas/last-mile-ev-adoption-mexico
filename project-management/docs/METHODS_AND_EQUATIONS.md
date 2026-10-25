# Statistical methods and mathematical definitions

## Research questions and estimands

**RQ1:** Among eligible responding small-cargo operators, which operational attributes are associated with self-reported current EV use?

**RQ2:** Which attributes are associated with self-reported EV consideration or already-included EVs?

**RQ3:** Can predictive classifiers discriminate responses on held-out folds more accurately than a majority-class benchmark, and how sensitive are their scores to random partitions?

Only RQ3 is primarily predictive. RQ1/RQ2 concern *within-sample associations* and do not identify causal effects.

For eligible survey response \(i\):

\[
Y_i^{\mathrm{use}}=\mathbb{1}(\text{current EV use reported}),\qquad
Y_i^{\mathrm{consider}}=\mathbb{1}(\text{yes or fleet already includes EVs}).
\]

The observed descriptive rate for a target is \(\hat p = n^{-1}\sum_{i=1}^n Y_i\), with its own target-specific denominator after missing responses are removed. The Wilson score interval is

\[
\frac{\hat p+\frac{z^2}{2n}\;\pm\;z\sqrt{\frac{\hat p(1-\hat p)}n+\frac{z^2}{4n^2}}}{1+\frac{z^2}{n}},\qquad z=1.96.
\]

The Wilson interval is an idealized independent-Bernoulli uncertainty interval, **not a correction for non-probability sampling or repeated respondents**.

## Target integrity and transformation

Source columns are accessed by documented zero-based indices because the original Spanish question text is lengthy and sometimes inconsistent. Source column 2 is the small-cargo screener. Column 27 measures EV use, while column 22 measures consideration; neither is ever used as a feature. Input spreadsheet strings are canonicalized through fixed rules and quality flags. Importantly, expressions measured in km per trip/route are not silently converted to km/day; the interval crossing 120 km/day remains missing and flagged.

Missing category imputation and low-frequency one-hot category grouping are **learned on the training fold only**, using `SimpleImputer` and `OneHotEncoder` in one `Pipeline`.

## Pre-specified scenarios

Let \(\mathbf X_i^B\) include firm size, fleet size, and vehicle type; let \(\mathbf X_i^E\) include \(\mathbf X_i^B\), daily-distance category, acquisition arrangement, route planning, and operating sector. The same eight classification families are evaluated on both \(\mathbf X^B\) and \(\mathbf X^E\), separately for \(Y^{\mathrm{use}}\) and \(Y^{\mathrm{consider}}\).

## Models and loss functions

### Penalized logistic regression

\[
p_i=\sigma(\beta_0+\mathbf x_i^T\boldsymbol\beta),\quad
\sigma(t)=\frac1{1+e^{-t}},
\]

\[
\widehat{\boldsymbol\beta}=\arg\min_{\boldsymbol\beta}
\left[-\sum_i w_i\left(y_i\log p_i+(1-y_i)\log(1-p_i)\right)
+\lambda\|\boldsymbol\beta\|_q^q\right],\qquad q\in\{1,2\}.
\]

The actual library's `C` controls inverse regularization strength; the expression is schematic and implementation-specific scale conventions differ. L1 selection is not causal variable selection. The intercept may be penalized depending on the chosen solver (`liblinear`).

### Linear support-vector classifier

\[
\min_{\mathbf w,b}\;\frac12\|\mathbf w\|_2^2+C\sum_i\max\bigl(0,1-y_i^*(\mathbf w^T\mathbf x_i+b)\bigr),\quad y_i^*=2y_i-1.
\]

LinearSVC outputs signed decision margins rather than calibrated probabilities; the Brier score is intentionally undefined for it in this study.

### Trees and forests

Binary Gini impurity at a node is

\[
G(t)=1-\sum_{k\in\{0,1\}}p(k\mid t)^2.
\]

Random Forest averages the predictions of trees trained on bootstrap samples and feature subsamples; depth and minimum leaf size regularize complexity. LightGBM sequentially fits gradient-boosted trees to optimize binary logistic loss and must also be constrained in such a small dataset.

### Dummy comparator

The reference model predicts the training-fold class distribution (`strategy='prior'`). Its balanced accuracy is generally near 0.5 for both observed classes, though individual fold behavior can vary.

## Honest repeated nested cross-validation

The implementation uses repeated **stratified 3-fold outer CV**, seeded with 17, 42, and 123 by default, and **stratified 3-fold inner CV** within each outer training split. Hyperparameters are selected by balanced accuracy:

\[
\hat\theta_{s,k} = \arg\max_{\theta\in\Theta}
\frac{1}{J}\sum_{j=1}^{J}\mathrm{BA}
\bigl(\hat f_{\theta}^{(-j)},\mathcal D_{s,k,j}^{\mathrm{inner\ val}}\bigr).
\]

The fit is retrained on the full outer training fold with \(\hat\theta_{s,k}\), and assessed on the strictly held-out outer test fold. Every response is predicted exactly once per outer seed/model/scenario/target. No preprocessing or tuning uses the outer held-out fold. Hyperparameter choice varies by fold and is retained in `inner_search_audit.csv`.

For a completed outer seed, the original out-of-fold predictions are pooled (each observation once) before computing class metrics. Across seeds, their mean and standard deviation measure **partition sensitivity**. They are *not* the error bars of independent experiments and cannot establish a formal confidence interval.

## Primary and supporting metrics

With true-positive, false-positive, true-negative and false-negative counts:

\[
\mathrm{Sensitivity}=\frac{TP}{TP+FN},\quad
\mathrm{Specificity}=\frac{TN}{TN+FP},\quad
\mathrm{Balanced\ Accuracy}=\frac12\left(\mathrm{Sensitivity}+\mathrm{Specificity}\right).
\]

\[
\mathrm{Precision}=\frac{TP}{TP+FP},\quad
F_1=\frac{2TP}{2TP+FP+FN},\quad
\mathrm{Brier}=\frac1n\sum_{i=1}^n(p_i-y_i)^2.
\]

ROC-AUC evaluates discrimination over thresholds. Average precision summarizes a precision–recall curve and should be interpreted relative to outcome prevalence. The Brier score measures squared probabilistic error for probability-producing models only. Scores are predictive metrics; neither accuracy nor balanced accuracy is ordinary regression \(R^2\).

**Ranking:** primary score = average across seeds of balanced accuracy; tie-breaker = average precision. Compare with the dummy. This produces a descriptive *candidate model*, not an unbiased generalization estimate of a model selected after exploring many alternatives. A future fully independent sample or a frozen external validation design is needed for a publication-level superiority claim.

## Fisher tests and associations

For prespecified binary exposure \(E\) and target \(Y\), calculate the contingency table \(\left[\begin{smallmatrix}n_{00}&n_{01}\\n_{10}&n_{11}\end{smallmatrix}\right]\). Report the Fisher exact two-sided p-value and descriptive odds ratio

\[
\widehat{\mathrm{OR}}=\frac{n_{11}n_{00}}{n_{10}n_{01}}.
\]

The estimated odds-ratio intervals are approximate and may disagree with the Fisher test because they are based on a different approximation. Benjamini–Hochberg FDR adjustment is performed separately per outcome across the **entire prespecified set of tested exposures**. Fisher tests do not adjust for confounding; no causal effects follow.

## Assumption checklist

| Procedure | Requirement or design check | Status with supplied data |
|---|---|---|
| Binary classifiers | Clearly specified binary target | Yes, subject to the nuanced consideration-item coding |
| Cross-validation | Each class appears in every training/test fold | Programmatically checked for the requested number of folds |
| All classifiers | Responses should be independent and from the intended target domain | **Not verifiable:** no company ID or sampling frame |
| Penalized logistic regression | Meaningful log-odds functional form; not severe unaddressed separation/sparsity | OHE yields flexible categorical effects; rare/single-class cells are audited, not proven harmless |
| Linear SVM | Appropriate regularization, comparable scaling, interpretable margins | Categorical OHE standardized to binary indicators; tuning is within training folds |
| Bernoulli Naive Bayes | Conditionally independent features is a simplifying model assumption | **Not established**; use as predictive comparator only |
| CART / RF / LightGBM | Sufficient data per leaf and constrained complexity | Controlled depth/leaves; training sample remains very small |
| Probability metrics | Predicted values must be probabilities | Brier omitted for LinearSVC decision margins |
| Fisher exact tests | Fixed sampling margins for exact conditional reference; interpretable independent observational units | Mathematical test available, but sampling/independence limitations remain |
| OLS linear regression | Continuous response, linear mean structure, residual diagnostics | **Not applicable**: both targets are binary |

For all models: inspect potential class imbalance, missingness, sparse categories, unknown categories, and per-fold metrics. The pipeline does **not** validate no unmeasured confounding, independent firms, geography, causality, or representativeness.

## Scientific reporting

A rigorous Results section should distinguish four layers: (1) response counts and prevalence; (2) descriptive association tables; (3) nested-CV discrimination and split sensitivity; (4) legal/operational interpretation with explicitly sourced constraints. Do **not** present cross-sectional associations as "drivers" in the causal sense, report impossible charging cost thresholds, or write that a positive classifier performance implies an economically feasible EV conversion.
