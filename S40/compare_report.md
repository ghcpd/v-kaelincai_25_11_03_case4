# Feature & Improvement · Refactor Comparison

This report was generated automatically by `scripts/generate_report.py` after running `run_all.sh`.

## 📂 Scenario Overview
- **Focus**: Deduplicate transaction feeds, normalise malformed records, and surface metrics for downstream analytics.
- **Input**: Iterable of transaction mappings (`id`, `amount`, `category`, optional `currency`, optional `status`).
- **Output**: Aggregate totals, category & currency breakdowns, invalid entry diagnostics, high-value identifiers.

## ✅ Test Coverage
| Case | Description | Expects Exception? |
| --- | --- | --- |
| basic_valid | Happy path with mixed currencies and categories. | No |
| with_duplicates_and_invalid | Deduplicates on id, records invalid amounts, and identifies high value ids. | No |
| iterator_with_non_mapping | Ensures non-mapping entries are rejected and whitespace amounts are caught. | No |
| large_batch_generated | Synthetic 1000 record feed for performance measurement. | No |
| invalid_input_type | Non-iterable input should raise ValueError. | Yes |

### Project A (Pre-Refactor)
- **Tests**: 11 passed / 0 failed / 0 skipped
- **Duration**: 0.030s

### Project B (Post-Refactor)
- **Tests**: 11 passed / 0 failed / 0 skipped
- **Duration**: 0.030s

## ⚙️ Performance Snapshot
| Metric | Project A | Project B | Δ |
| --- | --- | --- | --- |
| Mean of average latencies (ms) | 0.5878 | 0.5726 | 2.59% faster |
| Mean p95 latency (ms) | n/a | 0.774174986872822 | n/a |

## 🧪 Edge Case Handling
- Invalid-entry scenarios covered: `with_duplicates_and_invalid, iterator_with_non_mapping`
- High-value detection threshold maintained at 1000.0 by default.
- Generators and duplicate identifiers validated against deterministic summaries.

## 📝 Observations
- Project B eliminates redundant passes over the dataset, bringing average latency down while maintaining parity with the baseline tests.
- Shared fixtures and synthetic data ensure identical coverage pre- and post-refactor.
- Performance results are stored in JSON for reproducibility and downstream analysis.

## ⚠️ Known Limitations
- Both versions use floating-point outputs, so financial-grade precision may require adopting `Decimal` end-to-end.
- Performance probes run in-process and do not capture GC or peak memory usage.