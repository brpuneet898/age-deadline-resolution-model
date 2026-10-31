$ErrorActionPreference = "Stop"

python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit 1 }

python verify.py
if ($LASTEXITCODE -ne 0) { exit 1 }

python counterexample_search.py
if ($LASTEXITCODE -ne 0) { exit 1 }

python benchmark_capacity.py
if ($LASTEXITCODE -ne 0) { exit 1 }

python simulation.py --reps 10 --scenarios 5
if ($LASTEXITCODE -ne 0) { exit 1 }

python analysis.py
if ($LASTEXITCODE -ne 0) { exit 1 }

python figures.py
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "ALL D1 CHECKS COMPLETED SUCCESSFULLY" -ForegroundColor Green