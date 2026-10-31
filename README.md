# D1 M0 Age–Deadline Resolution: synthetic research implementation

**No FedEx/proprietary data.** Full coding package for single-shipment M0, negative-charge counterexample, restricted positive-cost critical score, exact joint at-most-B capacity control, heuristics, independent DP enumeration, paired synthetic experiments, and evidence logs. Not a claim of operational improvement or optimality of index ranking.

## One-command quick start (Python 3.10+)

From this extracted folder in PowerShell:

```powershell
python -m unittest discover -s tests -v
python verify.py
python counterexample_search.py
python benchmark_capacity.py --n 3 --capacity 1
python simulation.py --scenarios 2 --reps 10 --n 3 --output results/pilot.csv
python analysis.py results/pilot.csv --output results/pilot_analysis.json
python figures.py
```

All scripts use the Python standard library (no pip install needed). On Windows, use `py` instead of `python` if appropriate.

**Illustrative full grid, only after approving factors and a pilot:**

```powershell
python simulation.py --scenarios 432 --reps 500 --n 3 --seed 20261031 --output results/full_432.csv
python analysis.py results/full_432.csv --output results/full_432_analysis.json
```

Caution: The supplied email specifies **432 scenarios** but not the frozen D0 factor levels. `scenario_grid.py` is deliberately marked **illustrative**; its 432 combinations are NOT an audited match to the charter. Do **not** present an unapproved run as the charter experiment. Running 432 x 500 x five policies may take substantial time, depending on hardware; execute pilot first.

## Source directory

- `m0.py`: validated backwards Bellman DP, action values, exhaustive oracle, critical cost (restricted domain), negative-charge example.
- `capacity_dp.py`: small-N exact joint DP with independent Bernoulli resolutions and at-most-B feasible action subsets; exact policy evaluation and sample paths.
- `policies.py`: critical-cost, failure-risk, earliest-deadline, myopic-benefit and never-active.
- `benchmark_capacity.py`: expected policy costs and **exact small-N optimality gaps**.
- `scenario_grid.py`: synthetic grid and configurable misspecified decision model.
- `simulation.py`: paired simulation, common random numbers, CSV+manifest.
- `analysis.py`: paired mean cost differences with normal-approximation 95% confidence intervals.
- `counterexample_search.py`: analytic action values and finite structural violation search.
- `verify.py`: DP vs independent exhaustive enumeration, 576 cases.
- `figures.py`: dependency-free SVG counterexample and optimality-gap plots.
- `tests/`: targeted unit, integration, and replication tests.
- `theory/`: proof-scope summary and correction ledger.
- `evidence/`: output from validation, including environment/version after run.

## Critical distinctions

1. Counterexample with `k=c+lambda`: passive for `k<=-100`, active for `-100<k<100`, passive for `k>=100`, with passive ties at exactly +/-100. Refutes **global real-charge nesting** only.
2. When `k>0`, restricted passive-set nesting holds for arbitrary valid hazards. The `k=0` endpoint can be included by direct monotonicity argument; see `theory/proof_scope.md`.
3. A critical activation-cost score is **not** a classical unrestricted Whittle index and ranking by score is **not** proved optimal for the joint capacity constraint.
4. The subsidy model is distinct from a capacity-consistent activation charge; `m0.py` does not mix them.
5. `exact()` returns a finite Bellman action-enumeration certificate for the implemented small model, not a MILP solver certificate or an independent theorem proof.

## Reproducibility and publication

Log your own `git rev-parse HEAD`, `python --version`, commands and stdout in `evidence/`. The dates of actual execution must be used; do not backdate an October 30 checkpoint. `evidence/checkpoint_template.md` is a template, not a completed proof audit. No confidential FedEx material is included.
