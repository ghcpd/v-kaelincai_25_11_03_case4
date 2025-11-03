# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Feature & Improvement (Refactor)

## 🎯 Experiment Purpose
This workspace benchmarks Refactor capability across AI coding assistants by comparing a pre-refactor analytics helper (Project A) with an improved, production-ready variant (Project B). The shared objective is to streamline quality metric aggregation for software modules, eliminate code duplication, and improve resilience to malformed inputs.

## 🧪 Scenario Under Test
- **Context**: CI pipelines emit per-module metrics (`module`, `loc`, `complexity`, `coverage`, `last_updated`, optional `tags`).
- **Goal**: Produce repository-level summaries (module counts, coverage statistics, weighted risk scores) and highlight modules that violate configurable thresholds for coverage, complexity, or size.
- **Baseline Pain Points**: Redundant loops, immediate failures on bad records, duplicate-heavy breach reports.
- **Refactor Objectives**: Single-pass aggregation, structured diagnostics, deterministic breach reporting, and graceful handling of invalid payloads.

### Expected Input (JSON/Python dict)
```json
{
  "modules": [
    {
      "module": "payments.gateway",
      "loc": 4200,
      "complexity": 32,
      "coverage": 78.5,
      "last_updated": "2025-10-01T12:45:00Z",
      "tags": ["critical", "backend"]
    }
  ],
  "quality_thresholds": {
    "coverage_min": 80.0,
    "complexity_max": 25,
    "loc_max": 5000
  }
}
```

### Expected Output (Refactored)
```json
{
  "summary": {
    "module_count": 3,
    "avg_coverage": 86.233,
    "median_coverage": 88.2,
    "weighted_risk": 0.424813
  },
  "breaches": [
    {
      "module": "payments.gateway",
      "issues": ["coverage"]
    }
  ],
  "diagnostics": {
    "invalid_records": 0,
    "errors": []
  }
}
```

## 📂 Repository Layout
```
project_a/            # Pre-refactor implementation
  src/original_code.py
  tests/test_original.py
  data/test_data.json
  logs/
  performance/
  requirements.txt
  setup.sh
  run_tests.sh
project_b/            # Post-refactor implementation
  src/refactored_code.py
  tests/test_refactored.py
  data/test_data.json
  logs/
  performance/
  requirements_optimized.txt
  setup_optimized.sh
  run_tests.sh
test_data.json        # Shared dataset with expected outcomes per case
scripts/generate_report.py
run_all.sh            # One-click orchestrator for both projects and the comparison report
compare_report.md     # Generated after running the suites
README.md             # You are here
```

## 🛠️ Environment Setup
All dependencies are intentionally lightweight (`pytest`). Use the provided scripts for reproducibility:

```bash
# Project A (baseline)
bash project_a/setup.sh

# Project B (refactored)
bash project_b/setup_optimized.sh
```

Both scripts create isolated virtual environments (`.venv_pre` / `.venv_post`) and install requirements.

## ▶️ Running the Tests
To execute all suites and build the comparison artifacts:

```bash
bash run_all.sh
```

This orchestrator performs the following:
1. Ensures each project environment is ready.
2. Runs `pytest` for Project A and Project B.
3. Aggregates metrics and performance data via `scripts/generate_report.py`.
4. Updates `compare_report.md` with quantitative deltas (accuracy, edge-case coverage, invalid-input handling, runtime).

Need to run projects individually?
```bash
bash project_a/run_tests.sh
bash project_b/run_tests.sh
```

## 🧾 Test Data & Coverage
- `test_data.json` contains five curated cases spanning normal, edge, and invalid scenarios.
- Each case records expected baseline vs refactored outcomes, including structured diagnostics.
- Tests automatically persist logs (`logs/`) and timing data (`performance/`) to support benchmarking.

## 📈 Evaluation Metrics
The automated report captures:
- Overall accuracy of assertions (all suites must pass before completion).
- Edge-case success ratio (coverage of empty sets, duplicates, large inputs).
- Invalid-input containment rate (percentage of malformed records surfaced without halting execution).
- Runtime comparison based on wall-clock measurements captured during `pytest` execution.

## ⚠️ Pitfalls & Limitations
- Weighted risk computation is intentionally preserved across versions to keep deltas focused on resilience and structure rather than algorithmic change.
- The baseline implementation raises `ValueError` on malformed input; tests document this behaviour for historical reference.
- Runtime measurements are coarse wall-clock values from the current environment; reproduce them using the same hardware for apples-to-apples comparisons.

## ✅ Deliverables Recap
- **Project A**: Faulty baseline with environment automation, logs, and performance traces.
- **Project B**: Refactored implementation with modular validators, structured diagnostics, and improved reporting.
- **Shared Assets**: `test_data.json`, `run_all.sh`, auto-generated `compare_report.md`, and this README.

Run `bash run_all.sh` to validate everything end-to-end.
