# Refactor Comparison Report

## Summary
This report compares pre-refactor (ProjectA) and post-refactor (ProjectB) implementations.

## Metrics Table

| Metric | ProjectA | ProjectB | Improvement |
|--------|----------|----------|------------|
| Accuracy | 20.0% | 100.0% | 400.0% |
| Edge Accuracy | 25.0% | 100.0% | 300.0% |
| Avg Elapsed (s) | 0.027887680009007453 | 0.031100940029136836 | -11.5% |
| Large Case Time (s) | 0.13925539993215352 | 0.1553523000329733 | -11.6% |
| Peak Memory (bytes) | 5500149 | 14368179 | -161.2% |

## Key Refactor Changes
- Removed duplicated category counting loops
- Single-pass aggregation reduces time complexity of core metrics
- Excluded negative durations from totals to ensure correctness
- Iterative stack traversal avoids deep recursion and excessive list concatenations
- Introduced dataclass for clarity and type hints for maintainability
- Optional fast JSON parsing with orjson (used when available).

## Edge Case Handling
- Negative durations counted but excluded from averages and totals
- Invalid input (non-list) reported without crashing
- Deeply nested subtasks counted accurately with depth tracking

## Potential Pitfalls
- Extremely large nested structures may still increase memory usage due to Task object creation
- orjson is optional; absence slightly reduces parsing performance
- Validation cost grows linearly; can be skipped with validate=False for trusted data

## Recommendations
- Consider streaming for very large inputs
- Add type-enforced schema validation if data sources are unreliable
- Extend metrics to include median duration and category duration distributions
