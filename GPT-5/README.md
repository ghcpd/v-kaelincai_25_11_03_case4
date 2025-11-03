# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Feature & Improvement for Refactor

## Overview
This workspace contains two Python projects used to evaluate refactoring capability:
- **ProjectA**: Pre-refactor implementation (`original_code.py`) with intentional inefficiencies and correctness issues.
- **ProjectB**: Post-refactor implementation (`refactored_code.py`) optimizing readability, maintainability, and performance.

A shared test dataset (`test_data.json`) defines 5 scenarios:
1. `normal` – Standard small dataset
2. `nested` – Deeply nested subtasks
3. `negative` – Negative duration exclusion logic
4. `invalid` – Non-list malformed input
5. `large` – Generated high-volume dataset (performance)

## Refactor Scenario
The refactor targets elimination of anti-patterns:
- Duplicate loops for category counting
- Recomputing depth recursively for each record
- Inefficient list concatenation in recursion
- Broad exception swallowing
- Inclusion of negative durations in totals

Refactored changes:
- Single-pass accumulation with iterative stack for nesting
- Proper exclusion/tracking of negative durations
- Accurate category counts
- Dataclass `Task` improves clarity & structure
- Optional fast JSON parsing with `orjson`

## Input / Output Contract
`compute_statistics(data)` returns a dictionary:
```
{
  total_tasks: int,
  total_duration: float,        # sum of non-negative durations
  avg_duration: float | None,   # average over valid (non-negative) tasks
  categories: { str: int },     # frequency per category including nested
  invalid_records: int,         # top-level invalid records
  negative_duration_tasks: int, # count with duration < 0
  nested_subtask_count: int,    # total nested tasks (excludes top-level)
  max_depth: int,               # deepest nesting level
  errors: [str]                 # parsing/validation errors
}
```
Input may be a list of dicts or a JSON string. Non-list input yields zero metrics and an error entry.

## Environment Setup
Each project has an isolated virtual environment.

### Project A
```
ProjectA/
  requirements.txt (standard library only)
  setup.sh
  run_tests.sh
```
### Project B
```
ProjectB/
  requirements_optimized.txt (includes orjson)
  setup_optimized.sh
  run_tests.sh
```

## Running Tests (Windows PowerShell Friendly)
Preferred (cross-platform Python orchestration):
```
python run_all.py
```
This will:
1. Create virtual environments for both projects
2. Install dependencies
3. Execute both test suites
4. Generate `compare_report.md`

If you have a Bash environment (Git Bash / WSL):
```
bash run_all.sh
```

To run a single project manually:
```
python -m venv ProjectA/.venv
ProjectA/.venv/Scripts/activate
python ProjectA/tests/test_original.py
```
(Adjust to `ProjectB` for refactored.)

## Test Execution & Metrics
Each test harness:
- Loads `test_data.json`
- Generates large dataset if required
- Captures execution time per case
- Measures memory usage via `tracemalloc`
- Compares selected keys against expected values (float tolerance 1e-6)
- Writes summary logs:
  - `logs/log_original.txt` / `logs/log_refactored.txt`
  - `performance/time_original.txt` / `performance/time_refactored.txt`

`compare_report.md` aggregates:
- Accuracy (overall pass ratio)
- Edge accuracy (nested, negative, invalid, large cases)
- Average elapsed time
- Large dataset execution time
- Peak memory usage
- Narrative of refactor improvements & pitfalls

## Edge Cases Covered
- Negative durations excluded from aggregates
- Deep nesting depth & count
- Malformed non-list input handled gracefully
- Large performance stress test (20k records)

## Potential Pitfalls
- Extremely deep nesting could still consume memory (stack of Task objects)
- Optional dependency `orjson` may not install in restricted environments (tests still pass without acceleration)
- Validation overhead can be bypassed (future improvement: toggle for nested validation)

## Limitations
- Memory measurement uses peak from `tracemalloc`; does not differentiate categories cache overhead
- Large dataset generation is synthetic; real-world distributions may differ
- No parallel processing; single-thread performance only

## Next Steps / Enhancements
- Add median and p95 duration metrics per category
- Add streaming input for huge datasets
- Include property-based tests for fuzzing malformed records
- Expand error classification

## One-Click Summary
After `python run_all.py` completes, view `compare_report.md` for quantitative comparison.

## License / Attribution
All code generated for experimental evaluation purposes.
