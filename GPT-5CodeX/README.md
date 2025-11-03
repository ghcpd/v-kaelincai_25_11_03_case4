# Feature & Improvement Refactor Evaluation

This workspace compares two implementations of a transaction analytics routine:

- **Project A – Pre-Refactor**: A defensive but repetitive baseline that performs six passes over the data to compute metrics.
- **Project B – Post-Refactor**: A streamlined refactor that centralises validation, normalises data once, and aggregates in a single pass.

Both projects analyse the same JSON payload structure:

```json
{
  "threshold": 1000.0,
  "base_currency": "USD",
  "home_country": "US",
  "transactions": [
    {
      "id": "t1",
      "amount": 120.5,
      "category": "groceries",
      "currency": "USD",
      "tags": ["weekly"],
      "country": "US"
    }
  ]
}
```

The analytics pipeline returns a Python dictionary with:

- `total_amount`, `average_amount`, and `transaction_count`
- `category_totals` keyed by category (default `uncategorized`)
- `high_risk_transactions` flagged by threshold, risk tags, or foreign country
- `currency_mismatch_count`
- `invalid_entries` describing any malformed records

## Repository Layout

```
project_a/            # Baseline implementation
project_b/            # Refactored implementation
test_data.json        # Shared scenarios (normal, edge, invalid, performance)
run_all.sh            # One-click execution for both projects
compare_report.md     # Generated comparison summary
```

Each project contains:

- `src/` with the implementation (`original_code.py` / `refactored_code.py`)
- `tests/runner.py` custom harness and JSON logging
- `data/test_data.json` copy of the shared dataset
- `logs/` and `performance/` outputs (populated after running tests)
- `setup*.sh` to create a virtual environment
- `run_tests.sh` to execute the harness and capture metrics

## Test Scenarios

`test_data.json` describes five scenarios that exercise correctness and robustness:

1. **baseline_normal** – mixed categories and a high-risk transaction.
2. **empty_transactions** – ensures zero-handling with no data.
3. **mixed_quality_entries** – validates malformed entries, currency mismatch, and foreign transactions.
4. **large_dataset** – twenty synthetic transactions to highlight performance differences.
5. **non_dict_input** – guards against invalid payload types.

Expected outputs (including totals, risk flags, and invalid-entry reporting) are embedded alongside each case so the harness can compute pass/fail, accuracy, and edge-case success rates.

## Setup & Execution

> **Windows note**: The `.sh` scripts assume a POSIX shell. Use Git Bash, WSL, or a similar environment and ensure `python` is available on the `PATH`.

### Project A

```bash
cd project_a
./setup.sh          # creates .venv and installs requirements
./run_tests.sh      # executes tests, writes logs/log_original.txt and performance/time_original.txt
```

### Project B

```bash
cd project_b
./setup_optimized.sh
./run_tests.sh
```

### Full Comparison

```bash
./run_all.sh
```

The master script runs both project pipelines, then calls `tools/generate_compare_report.py` to regenerate `compare_report.md`. Logs and performance JSON are overwritten on each run to keep the report current.

## Output & Metrics

- **Functional metrics**: accuracy, edge-case success, and invalid-input handling.
- **Performance metrics**: total runtime, average runtime per case, peak memory (via `tracemalloc`).
- **Artifacts**: JSON logs under `logs/`, performance details under `performance/`, consolidated comparison in `compare_report.md`.

## Extending the Experiment

- Add new scenarios to `test_data.json` and rerun the harnesses.
- Modify the refactor to explore additional optimisations (e.g., concurrency, memoisation) and observe the impact in the comparison report.
- Integrate the harness into CI pipelines by invoking `run_all.sh` as part of verification.
