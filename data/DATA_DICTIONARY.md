# Source questionnaire and canonical analytic variables

The original 34 Spanish questionnaire labels are preserved in the source workbook and CSV (and reproduced below only by index where necessary). Indices are **zero-based**, making the source mapping stable even when labels contain line breaks and whitespace. All English canonical variables below are derived, not original survey names.

| Source index | Canonical variable | Statistical role | Cleaning / interpretation |
|---:|---|---|---|
| 2 | `eligibility` | Screening | Accept accent/case-insensitive 'Sí'; excludes responses not confirming small-cargo vehicles |
| 3 | `firm_size` | Categorical predictor | Small / Medium / Large |
| 4 | `fleet_size` | Categorical predictor | `1-10`, `11-50`, `51-200`, `200-400`, `>400`; numbers mapped to intervals, nonnumeric mixed reports flagged |
| 5 | `vehicle_type` | Categorical predictor | Motorcycle/tricycle / Van / Medium-duty truck / Mixed motorcycles and vans / Other |
| 7 | `daily_distance` | Categorical predictor | `<20`, `31-60`, `61-120`, `>120` km/day; unconvertible trip/route measures missing and flagged |
| 8 | `acquisition_type` | Categorical predictor | New purchase / Used purchase / Leasing / Outsourcing |
| 21 | `route_planning` | Categorical predictor | Preplanned / Dynamic / Mixed |
| 22 | `ev_consideration` | Binary outcome | Yes or 'my fleet includes EVs' = 1; No = 0; unanswered or unknown = missing |
| 23 | `ev_benefits` | Exploratory descriptions only | Multi-select category strings; not baseline ML predictors |
| 24 | `ev_barriers` | Exploratory association only | Multi-select category strings; not baseline ML predictors |
| 26 | `sector` | Categorical predictor | Logistics and parcel delivery / Retail / Services / Food and distribution / Other |
| 27 | `ev_use` | Binary outcome | Starts with Yes = 1, starts with No = 0; missing/unknown = missing |

The other source questionnaire fields remain retained in `eligible_canonical.csv` as original Spanish-named columns and may be inspected only for authorized, narrowly justified follow-up research. Original source timestamps are not treated as statistical predictors. `*_quality` fields classify mapping decisions as `mapped`, `numeric_to_band`, `unit_inferred_from_question`, `incompatible_unit`, `crosses_120km_threshold`, `unclassified`, `missing`, etc. Missing values do not mean zero; categorical `Missing` is imputed **inside the training-fold pipeline**. The source's distance units and financial fields cannot be converted reliably to continuous cost or daily-driving values without additional validation.

**Granularity:** one response row from the questionnaire. **Provenance:** unmodified workbook; artifact_tool CSV export; deterministic `preprocessing.py`. **Quality:** response-level, not externally validated or necessarily independent. **Geographic interpretation:** reported state of the respondent's operating base, not necessarily a verified route geography.
