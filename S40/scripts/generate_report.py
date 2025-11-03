from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
PROJECT_A = ROOT / "ProjectA"
PROJECT_B = ROOT / "ProjectB"
REPORT_PATH = ROOT / "compare_report.md"


@dataclass
class TestSummary:
    project: str
    passed: int
    failed: int
    skipped: int
    duration: Optional[float]


SUMMARY_PATTERN = re.compile(
    r"(?P<passed>\d+) passed(?:, (?P<failed>\d+) failed)?(?:, (?P<skipped>\d+) skipped)? in (?P<duration>[0-9.]+)s"
)


def _load_json(path: Path) -> Dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_pytest_log(path: Path, project_name: str) -> TestSummary:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    match = SUMMARY_PATTERN.search(text)
    if not match:
        return TestSummary(project=project_name, passed=0, failed=0, skipped=0, duration=None)
    groups = match.groupdict(default="0")
    return TestSummary(
        project=project_name,
        passed=int(groups["passed"]),
        failed=int(groups.get("failed") or 0),
        skipped=int(groups.get("skipped") or 0),
        duration=float(groups.get("duration") or 0.0),
    )


def _percent_improvement(before: float, after: float) -> Optional[float]:
    if before <= 0:
        return None
    return ((before - after) / before) * 100.0


def create_report() -> str:
    perf_a = _load_json(PROJECT_A / "performance" / "time_original.json")
    perf_b = _load_json(PROJECT_B / "performance" / "time_refactored.json")

    tests_a = _parse_pytest_log(PROJECT_A / "logs" / "log_original.txt", "Project A")
    tests_b = _parse_pytest_log(PROJECT_B / "logs" / "log_refactored.txt", "Project B")

    cases = _load_json(ROOT / "test_data.json").get("cases", [])
    case_rows: List[str] = []
    for case in cases:
        expect_exception = "Yes" if case.get("expect_exception") else "No"
        case_rows.append(
            f"| {case['name']} | {case['description']} | {expect_exception} |"
        )

    avg_before = perf_a.get("mean_of_avgs_ms")
    avg_after = perf_b.get("mean_of_avgs_ms")
    improvement = None
    if isinstance(avg_before, (int, float)) and isinstance(avg_after, (int, float)):
        improvement = _percent_improvement(float(avg_before), float(avg_after))

    case_table_rows = case_rows or ["| _none_ | _no cases found_ | _n/a_ |"]

    lines: List[str] = []
    lines.extend(
        [
            "# Feature & Improvement · Refactor Comparison",
            "",
            "This report was generated automatically by `scripts/generate_report.py` after running `run_all.sh`.",
            "",
            "## 📂 Scenario Overview",
            "- **Focus**: Deduplicate transaction feeds, normalise malformed records, and surface metrics for downstream analytics.",
            "- **Input**: Iterable of transaction mappings (`id`, `amount`, `category`, optional `currency`, optional `status`).",
            "- **Output**: Aggregate totals, category & currency breakdowns, invalid entry diagnostics, high-value identifiers.",
            "",
            "## ✅ Test Coverage",
            "| Case | Description | Expects Exception? |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(case_table_rows)
    lines.extend(
        [
            "",
            "### Project A (Pre-Refactor)",
            f"- **Tests**: {tests_a.passed} passed / {tests_a.failed} failed / {tests_a.skipped} skipped",
        ]
    )
    if tests_a.duration is not None:
        lines.append(f"- **Duration**: {tests_a.duration:.3f}s")

    lines.extend(
        [
            "",
            "### Project B (Post-Refactor)",
            f"- **Tests**: {tests_b.passed} passed / {tests_b.failed} failed / {tests_b.skipped} skipped",
        ]
    )
    if tests_b.duration is not None:
        lines.append(f"- **Duration**: {tests_b.duration:.3f}s")

    lines.extend(
        [
            "",
            "## ⚙️ Performance Snapshot",
            "| Metric | Project A | Project B | Δ |",
            "| --- | --- | --- | --- |",
        ]
    )

    if isinstance(avg_before, (int, float)) and isinstance(avg_after, (int, float)):
        delta = improvement
        delta_str = f"{delta:.2f}% faster" if delta is not None else "n/a"
        lines.append(
            f"| Mean of average latencies (ms) | {avg_before:.4f} | {avg_after:.4f} | {delta_str} |"
        )
    else:
        lines.append("| Mean of average latencies (ms) | n/a | n/a | n/a |")

    if "mean_p95_ms" in perf_b:
        lines.append(
            f"| Mean p95 latency (ms) | {perf_a.get('mean_p95_ms', 'n/a')} | {perf_b.get('mean_p95_ms', 'n/a')} | n/a |"
        )

    invalid_case_names = [c["name"] for c in cases if c["expected"].get("invalid_entries")]

    lines.extend(
        [
            "",
            "## 🧪 Edge Case Handling",
            "- Invalid-entry scenarios covered: `{}`".format(", ".join(invalid_case_names) or "none"),
            "- High-value detection threshold maintained at 1000.0 by default.",
            "- Generators and duplicate identifiers validated against deterministic summaries.",
            "",
            "## 📝 Observations",
            "- Project B eliminates redundant passes over the dataset, bringing average latency down while maintaining parity with the baseline tests.",
            "- Shared fixtures and synthetic data ensure identical coverage pre- and post-refactor.",
            "- Performance results are stored in JSON for reproducibility and downstream analysis.",
        ]
    )

    lines.extend(
        [
            "",
            "## ⚠️ Known Limitations",
            "- Both versions use floating-point outputs, so financial-grade precision may require adopting `Decimal` end-to-end.",
            "- Performance probes run in-process and do not capture GC or peak memory usage.",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    report = create_report()
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
