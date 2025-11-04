"""Generate the comparative report between the original and refactored projects."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
A_LOG = ROOT / "project_a" / "logs" / "log_original.txt"
A_PERF = ROOT / "project_a" / "performance" / "time_original.txt"
B_LOG = ROOT / "project_b" / "logs" / "log_refactored.txt"
B_PERF = ROOT / "project_b" / "performance" / "time_refactored.txt"
REPORT_PATH = ROOT / "compare_report.md"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Expected JSON content in {path}: {exc}") from exc


def _format_percentage(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def _format_seconds(value: float) -> str:
    return f"{value:.6f}s"


def _format_ms(value: float) -> str:
    return f"{value:.3f}ms"


def _format_kib(value: float) -> str:
    return f"{value:.2f} KiB"


def _metric_delta(a: float, b: float) -> str:
    diff = b - a
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.2f}"


def _runtime_delta(a: float, b: float) -> str:
    diff = a - b
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.6f}s"


def build_report() -> str:
    a_log = _load_json(A_LOG)
    b_log = _load_json(B_LOG)
    a_perf = _load_json(A_PERF)
    b_perf = _load_json(B_PERF)

    a_metrics = a_log.get("metrics", {})
    b_metrics = b_log.get("metrics", {})

    lines = [
        "# Refactor Comparison Report",
        "",
        "## Accuracy & Coverage",
        "| Metric | Project A (Original) | Project B (Refactored) | Delta |",
        "| --- | --- | --- | --- |",
        f"| Accuracy | {_format_percentage(a_metrics.get('accuracy'))} | {_format_percentage(b_metrics.get('accuracy'))} | {_metric_delta(a_metrics.get('accuracy', 0.0)*100, b_metrics.get('accuracy', 0.0)*100)} percentage points |",
        f"| Edge Case Success | {_format_percentage(a_metrics.get('edge_case_success_rate'))} | {_format_percentage(b_metrics.get('edge_case_success_rate'))} | {_metric_delta((a_metrics.get('edge_case_success_rate') or 0.0)*100, (b_metrics.get('edge_case_success_rate') or 0.0)*100)} percentage points |",
        f"| Invalid Case Handling | {_format_percentage(a_metrics.get('invalid_case_success_rate'))} | {_format_percentage(b_metrics.get('invalid_case_success_rate'))} | {_metric_delta((a_metrics.get('invalid_case_success_rate') or 0.0)*100, (b_metrics.get('invalid_case_success_rate') or 0.0)*100)} percentage points |",
        "",
        "## Performance",
        "| Metric | Project A | Project B | Improvement |",
        "| --- | --- | --- | --- |",
        f"| Total Runtime | {_format_seconds(a_perf.get('total_runtime_seconds', 0.0))} | {_format_seconds(b_perf.get('total_runtime_seconds', 0.0))} | {_runtime_delta(a_perf.get('total_runtime_seconds', 0.0), b_perf.get('total_runtime_seconds', 0.0))} |",
        f"| Avg Runtime per Case | {_format_ms(a_perf.get('avg_case_runtime_ms', 0.0))} | {_format_ms(b_perf.get('avg_case_runtime_ms', 0.0))} | {_metric_delta(a_perf.get('avg_case_runtime_ms', 0.0), b_perf.get('avg_case_runtime_ms', 0.0))} ms |",
        f"| Peak Memory | {_format_kib(a_perf.get('peak_memory_kib', 0.0))} | {_format_kib(b_perf.get('peak_memory_kib', 0.0))} | {_metric_delta(a_perf.get('peak_memory_kib', 0.0), b_perf.get('peak_memory_kib', 0.0))} KiB |",
        "",
        "## Highlights",
        "- Refactor performs a single aggregation pass instead of six sequential loops, reducing CPU time.",
        "- Input normalisation is centralised which improves resilience to malformed entries.",
        "- High-risk detection shares reusable helpers, simplifying maintenance and future feature work.",
        "",
        "## Data Sources",
        f"- Original logs: `{A_LOG.relative_to(ROOT)}`",
        f"- Refactored logs: `{B_LOG.relative_to(ROOT)}`",
        f"- Original performance: `{A_PERF.relative_to(ROOT)}`",
        f"- Refactored performance: `{B_PERF.relative_to(ROOT)}`",
    ]

    return "\n".join(lines)


def main() -> None:
    report = build_report()
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Comparison report written to {REPORT_PATH}")


if __name__ == "__main__":  # pragma: no cover
    main()
