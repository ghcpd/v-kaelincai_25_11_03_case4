# Refactor Evaluation Harness

This workspace benchmarks a **Refactor** task focused on summarising transaction feeds. Two sibling projects expose the same functional contract:

- **Project A** – Intentionally verbose “pre-refactor” implementation.
- **Project B** – Optimised and maintainable “post-refactor” implementation.

Both projects consume the same structured test data and share identical automated tests so their behaviour can be compared side by side.

## 📦 Repository Layout

```text
ProjectA/
  src/original_code.py          # Baseline implementation with redundant loops
  src/performance_probe.py      # Captures latency stats for the baseline
  tests/test_original.py        # Regression suite shared with Project B
  data/test_data.json           # Transaction fixtures (copied from root)
  logs/log_original.txt         # Pytest output (created by run_tests.sh)
  performance/time_original.json# Timing metrics (created by run_tests.sh)
  requirements.txt              # Baseline dependencies
  setup.sh                      # Optional helper to create a venv & install deps
  run_tests.sh                  # Executes pytest + benchmarking for Project A
ProjectB/
  src/refactored_code.py        # Streamlined refactor using reusable helpers
  src/performance_probe.py      # Enhanced benchmark with percentile metrics
  tests/test_refactored.py      # Mirrors Project A tests with refactored import
  data/test_data.json           # Same fixtures as Project A
  logs/log_refactored.txt       # Pytest output for the refactor
  performance/time_refactored.json
  requirements_optimized.txt    # Dependencies for the refactored version
  setup_optimized.sh            # Optional helper to create & populate a venv
  run_tests.sh                  # Executes pytest + benchmarking for Project B
scripts/generate_report.py      # Aggregates logs/perf stats into compare_report.md
run_all.sh                      # Runs both projects and refreshes the comparison
compare_report.md               # Auto-generated summary (recreated by run_all.sh)
test_data.json                  # Canonical test scenarios shared by both projects
README.md                       # You are here
```

## 🧪 Test Scenarios

`test_data.json` defines five structured cases spanning:

1. **Normal operations** with mixed categories and currencies.
2. **Duplicate identifiers** plus malformed amounts that must trigger invalid-entry logs and high-value detection.
3. **Non-mapping elements** to confirm defensive handling and whitespace validation.
4. **Large synthetic batch (1,000 items)** for throughput benchmarking.
5. **Invalid input type** to verify contract enforcement.

Each case includes expected outputs (totals, breakdowns, invalid entries, high-value ids) so both code paths must return identical data structures.

## ⚙️ Environment Setup

> **Tip:** Both sub-projects work without a virtual environment, but the helper scripts keep local installs tidy.

```bash
# Baseline environment
cd ProjectA
bash setup.sh

# Refactored environment
cd ../ProjectB
bash setup_optimized.sh
```

The requirements are lightweight (`pytest` only). Any Python 3.10+ interpreter will work.

## ▶️ Running Tests & Benchmarks

From the repository root:

```bash
# Execute both projects, update logs/perf data, and rebuild compare_report.md
bash run_all.sh
```

Individual project runs are also available:

```bash
bash ProjectA/run_tests.sh
bash ProjectB/run_tests.sh
```

Each run performs:

1. `pytest` execution against the shared fixtures.
2. A micro-benchmark loop capturing average/min/max (and p95 for Project B).
3. Log and metric persistence to `logs/` and `performance/` for later inspection.

## 📊 Comparison Output

`scripts/generate_report.py` collates:

- Pass/fail/skip counts and durations from pytest.
- Latency averages (baseline vs refactor) with percentage improvement.
- Notes on edge-case coverage and behavioural guarantees.

The generated `compare_report.md` provides a quick glance at progress plus known limitations (e.g., floating-point outputs vs `Decimal` precision and missing memory metrics).

## 🧭 Extending the Harness

- Add new scenarios to `test_data.json`. Both suites pick them up automatically.
- Update performance probes to capture custom metrics (CPU, memory, etc.).
- Integrate into CI by invoking `bash run_all.sh` and archiving the resulting artefacts.

Happy benchmarking! Let me know if you need additional instrumentation or reporting hooks.
