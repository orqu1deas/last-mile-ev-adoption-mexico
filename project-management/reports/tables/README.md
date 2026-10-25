# Model tables

The initial model tables in this delivery are a **smoke-test demonstration** (seed 42; 3 outer folds, 2 inner folds, and two random-search iterations). They demonstrate working held-out ROC generation but are **not** the earlier 3-seed comprehensive model estimates.

For full multi-seed evaluations, open notebooks 04 and 05, set `RUN_EVALUATION = True`, then re-run. This will overwrite each target-specific table with a 3-seed nested CV run. Standard deviations for a single seed are undefined and should not be interpreted as zero.
