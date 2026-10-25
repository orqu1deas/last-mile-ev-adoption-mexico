# Source audit, corrections, and unresolved research issues

## Inspected inputs

1. `archive/original_ev_analysis.ipynb` — a 25-cell notebook containing Excel ingestion, normalizers, Wilson intervals, Fisher tests, assumption diagnostics, classifier comparisons, optional AutoGluon, and figures. Original environment-specific package installations and most reusable functions were embedded in cells.
2. `archive/audited_legacy_notebook.py` — exported from a Colab notebook, referring to a missing `src/ev_analysis.py`. Its narrative contains useful conservative cleaning protocols and notes that a historical 0.958 metric was accuracy, not OLS R². The missing module is not reconstructed by guessing its implementation. The consistent blue plotting palette is recreated explicitly rather than claimed to exactly reproduce unavailable original theme code.
3. `data/raw/survey_original.xlsx` — 105 × 34 original questionnaire table. `survey_source.csv` is an artifact_tool-exported source snapshot.
4. `references/legal_framework_2026.pdf` — legal research manuscript (47 pages), with 2026 cutoff and freight/last-mile scenarios.
5. `references/research_brief.pdf` — five-page research project brief about last-mile EVs and formal/informal urban-mobility operators. Its planned interviews/focus groups should not be misrepresented as completed survey data.

## Data quality issues that affect validity

- Exact duplicate exclusion: 13 source rows removed, including 11 duplicated eligible responses. Distinct rows cannot be guaranteed to represent distinct firms without identifiers.
- Questionnaire-specific denominator: 60 nonmissing current EV use responses and 59 consideration responses among 62 eligible unique rows.
- The alternative analysis retaining exact duplicates changes current EV use from **15/60 (25.0%) to 22/69 (31.9%)** and consideration from **34/59 (57.6%) to 42/67 (62.7%)**. This shows why deduplication is consequential.
- Among **non-adopters with a valid consideration response**, 19/44 (43.2%) report consideration; this is a conditional descriptive construct, not a transition probability.
- Consideration choice 'My fleet includes electric vehicles': counted positive (n=2 in this survey) but the label overlaps observed adoption. Report definition explicitly.
- Response heterogeneity: fleet count `1200` is treated as `>400`; textual percentage composition of motorcycles/trucks is **not** interpreted as a fleet count.
- Distance: `120` and `250` are assigned to daily-distance bands with a **unit-inferred flag**, but `12km/ruta`, `20km/ola` and other per-route values are not converted to daily km. `100-150` crosses an ordinal threshold and is missing with a dedicated flag, rather than being silently forced into the `>120` band.
- Survey prices are binned and some operating cost responses are bare numbers of ambiguous units; this version does not fit continuous TCO, revenue, or charging-cost regressions.
- The original 34-column spreadsheet contains a generically named field (`Column 31`) that is intentionally excluded.
- Some responses give a contradictory operating sector such as 'I do not operate small vehicles' despite eligibility screen. These are flagged as inconsistent rather than silently corrected.

## Model and inferential issues

- **Limited events:** 15 current EV adopters across 60 valid responses; a three-way outer split leaves small validation folds. Complex model family comparisons may be unstable despite nested CV.
- **Data leakage control:** preprocessing is fitted within every training fold, outer labels are held out, and two target fields cannot appear in the predictor sets. Barriers/benefits measured alongside adoption are reserved for exploratory associations, not predictive baselines.
- **Reproducibility:** fixed outer seeds, inner seeds, constrained hyperparameter search, exported inner hyperparameters and OOF observations, and run manifest.
- **Variable importance:** a separate exploratory held-out permutation-importance module is supplied. Its model winner was selected using the same study CV scores, correlated categories can share signal, and tiny test folds can yield negative/unstable drops. No variable ranking is asserted as causal or definitive.
- **Fairness and segment comparisons:** the project brief covers formal/informal ridesharing and last-mile delivery, but the current small-cargo survey does not establish corresponding formal/informal group labels. Do not claim validated fairness or group differences that cannot be identified.
- **Hyperparameter choice:** grid/random search inside inner CV removes within-model validation reuse, but choosing the overall best algorithm from its CV score still yields winner-selection optimism. Collect or reserve truly external data.
- **No statistical power guarantee:** Monte-Carlo split repeats of the same 60 responses are not independently replicated studies and cannot prove unbiased performance stability.

## Recommended next additions, only if supported by new data

1. External validation from new operators; firm identifiers and organization-level grouping.
2. Operational measurement: per-vehicle annual km, trip demand, payload, dwell time, available electrical capacity, charging power, tariffs, purchase quotes, battery degradation, and delivery success.
3. A genuine prospective forecasting cohort that can separate current adoption, consideration without adoption, and future switching.
4. Formal/informal operator and geography variables if coverage and consent permit; document selection mechanisms.
5. Freeze a study protocol before expanding model families or making directional hypothesis tests.
6. A dedicated feasibility/TCO module using independently verified EV/ICE operating inputs; it should remain **scenario modeling**, not a regression derived from these categorical questionnaire responses.
