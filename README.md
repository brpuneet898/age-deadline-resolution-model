# D1 early start — Transportation Science M0

**Date:** 18 October 2026. **Nature:** research prototype, synthetic and analytical only.

The D0 charter is frozen. This package starts the D1 mathematical and computational track early, without declaring the November D1 acceptance gate satisfied.

## File manifest
- `M0_model_note.tex`: mathematical model, Bellman equation, three elementary proved structural statements under **explicit sufficient assumptions**, subsidy/activation-charge distinction, next research obligations.
- `m0.py`: pure-Python finite-horizon DP, deterministic passive ties, exhaustive oracle, Monte Carlo simulator, and grid diagnostics.
- `test_m0.py`: eight reproducibility checks.
- `experiment.py`: fixed-seed synthetic smoke experiment.
- `smoke_results.json`: output from the smoke experiment.

## Reproduce
```sh
python -m unittest -v test_m0
python experiment.py
pdflatex -interaction=nonstopmode -halt-on-error M0_model_note.tex
```
Only standard-library Python dependencies are required.

## Model and proof scope
States `(a, ell)` represent integer dwell age and remaining deadline intervals. The action controls the *current problematic stage's* resolution before its deadline; it does **not** assert end-to-end shipment delivery. Resolving within the last interval is timely. `ell=0` unresolved costs `K`. Charge `lambda` is paid on activation; an unresolved-only passive subsidy is a separate mathematical object and is **not** treated as a capacity-equivalent Whittle relaxation.

Theorems in the accompanying working note concern value ordering and activity-region shape under explicit probability monotonicity assumptions; **indexability has not been proved**. Numerical grid absence of passive-set reversals is not theoretical evidence of general indexability. No FedEx or open-data results are claimed, and no causal intervention effect has been estimated.

## Handoff priorities
1. Analytical audit of the activation-charge formulation, passive-set nesting and terminal convention.
2. Counterexample search that saves failing parameter grids rather than suppressing them.
3. Small multi-shipment exact capacity benchmark, then heterogeneous deadlines and interventions.
4. Frozen scenario grid and replication-level paired statistical comparisons.

**Planned D1 gate:** 30 November 2026. **D2 theory gate:** 31 December 2026. **Target venue:** Transportation Science.
