# Executable research narrative

Run notebooks **01 → 02 → 03 → 04 → 05 → 06** from the repository root after installing `requirements.txt`.

- 01 provenance, screening, 34-field original survey, data quality and both outcome definitions.
- **02 EDA:** the three user-supplied reference layouts, plus grouped operating-cost, distance, barriers/benefits, segment and sensitivity panels.
- 03 Fisher tests, odds ratios, BH-FDR correction and statistical assumptions.
- 04 **current EV use**: five-family nested CV evaluation, ROC, precision–recall, confusion and seed stability.
- 05 **EV consideration**: same design on a separately defined valid-response set.
- 06 integrated evidence, duplicate sensitivity, contextual interpretation and research limitations.

All six notebooks were executed and saved with their visible chart outputs. The reusable work is in `src/ev_research/`: a single centralized plot style and target-aware modeling routines. The model notebooks read precomputed tables by default; set `RUN_EVALUATION=True` for a repeat of the included three-seed model comparison. Raw inputs and per-respondent scores must be handled as private research data.
