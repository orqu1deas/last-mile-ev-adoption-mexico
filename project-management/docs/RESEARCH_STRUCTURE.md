# Research article, poster, and presentation structure

## Paper outline

1. **Title and abstract.** Electric-Vehicle Use and Consideration Among Small-Cargo Operators in Mexico: An Exploratory Survey and Nested Cross-Validation Study.
2. **Introduction and motivation.** Last-mile logistics, decarbonization, operating constraints, and lack of representative operator-level adoption evidence.
3. **Related work.** EV fleet-adoption barriers, adoption intention versus revealed operation, and the Mexican regulatory environment. The 2026 legal manuscript is context, not an adoption dataset.
4. **Data and research design.** Questionnaire provenance, eligibility, exact duplicates, target definition, feature scenarios, selection bias, non-probability design.
5. **Methods.** Cleaning protocol, Wilson intervals, exploratory Fisher/FDR, repeated nested CV, model families, scoring, split stability.
6. **Results.** Eligibility flow; current use and consideration rates; operational profile; pre-specified associations; per-target scenario-by-model benchmark; robustness to seed.
7. **Discussion.** Observed relationships versus hypotheses, role of charging/funding/route constraints, legal uncertainty, alternatives for micro-operators versus depot fleets.
8. **Limitations.** Cross-sectional/small/possibly non-independent sample, sparse minority class, lack of real charger and route data, non-causal modeling and selection uncertainty.
9. **Conclusions and policy implications.** Conservative, evidence-bound recommendations and data collection priorities.
10. **Reproducibility appendix.** Data dictionary, exact mapping flags, dependency file, model grids, seeds, model audit tables and selective withheld respondent-level artifacts.

## Figures and poster positioning

| Place | Figure/summary | Source |
|---|---|---|
| Paper Fig. 1 / Methods poster panel | Screening and deduplication flow, including separate target-specific n | `outputs/tables/sample_flow.csv` |
| Paper Fig. 2 / Poster top-center | Self-reported EV use vs. consideration with Wilson intervals | `outputs/figures/01_ev_outcomes.svg` |
| Paper Table 1 / Poster left panel | Sample operational profile by canonical categories | `eligible_canonical.csv` aggregated to counts; no respondent IDs |
| Paper Table 2 / Supplement | Pre-specified exposure vs. target Fisher test, odds ratio, FDR | `exploratory_associations.csv` |
| Paper Fig. 3 / Poster center-right | Nested-CV balanced accuracy by target and scenario | `02_models_*.svg` |
| Paper Table 3 / Supplement | Seed-level score dispersion, best hyperparameters | `model_summary.csv`, `inner_search_audit.csv` |
| Discussion figure / Poster bottom | Operational–regulatory pathway: vehicle class → route duty cycle → depot electricity connection → permitting → fiscal applicability | Conceptual flow synthesized from the supplied legal manuscript, **not** inferred statistically |

No standalone poster file was supplied in the materials reviewed. The 47-page supplied `main(4).pdf` is a **legal research article**; the five-page `EI-AD26-085.pdf` is a **research project brief**, not an empirical results poster. Once a poster exists, store source files separately under `docs/poster/`, and export final SVG figures or a print-quality PDF to a public dissemination folder only after privacy review.

## Domain-specific caveats from the legal manuscript

The supplied manuscript (reviewed through **August 6, 2026**) discusses Mexican electricity-sector electromobility provisions (notably Electricity Sector Law articles 86–87), electrical connection and charging design, fleet-vehicle tax categories, potential demand-based electricity expenses, and the non-uniformity of local circulation regimes. These constrain whether a fleet electrification *scenario* is feasible but are **not measured variables in the current survey**. Separate any prospective regulatory scenarios from predictive analyses, document legal source dates, and verify applicable regulations again before operational use.

Do not apply an assumed universal 30% charger credit to private depots or assume all light-cargo vehicles qualify as "automobiles" for tax relief. Do not assert that self-reported charging barriers measure charger density. Do not infer a TCO break-even from the survey's category-binned price/cost responses.
