import json
import time
from pathlib import Path
from typing import Any, Dict

import pytest

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from original_code import process_module_metrics

DATA_PATH = PROJECT_ROOT / "data" / "test_data.json"
LOG_PATH = PROJECT_ROOT / "logs" / "log_original.txt"
PERF_PATH = PROJECT_ROOT / "performance" / "time_original.txt"
METRICS_PATH = PROJECT_ROOT / "logs" / "results_original.json"


def load_cases():
    with DATA_PATH.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload["cases"]


CASES = load_cases()


@pytest.fixture(scope="module")
def metrics_recorder():
    results: Dict[str, Any] = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "invalid_expected": 0,
        "invalid_success": 0,
        "edge_total": 0,
        "edge_success": 0,
        "start": time.perf_counter(),
        "cases": [],
    }
    yield results
    duration = time.perf_counter() - results["start"]
    results["duration_seconds"] = duration
    results["accuracy"] = (
        results["passed"] / results["total"] if results["total"] else 0.0
    )
    results["edge_case_success_rate"] = (
        results["edge_success"] / results["edge_total"]
        if results["edge_total"]
        else 0.0
    )
    results["invalid_handling_rate"] = (
        results["invalid_success"] / results["invalid_expected"]
        if results["invalid_expected"]
        else 0.0
    )

    LOG_PATH.write_text(
        "Pre-Refactor Execution\n"
        f"Total cases: {results['total']}\n"
        f"Passed: {results['passed']}\n"
        f"Failed: {results['failed']}\n"
        f"Accuracy: {results['accuracy']:.3f}\n"
        f"Edge coverage: {results['edge_case_success_rate']:.3f}\n"
        f"Invalid handling: {results['invalid_handling_rate']:.3f}\n",
        encoding="utf-8",
    )

    PERF_PATH.write_text(
        f"elapsed_seconds={duration:.6f}\n",
        encoding="utf-8",
    )

    METRICS_PATH.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_process_module_metrics(case, metrics_recorder):
    metrics_recorder["total"] += 1

    case_result: Dict[str, Any] = {
        "id": case["id"],
        "type": case["type"],
    }

    if case["type"] == "edge":
        metrics_recorder["edge_total"] += 1
    if case["type"] == "invalid":
        metrics_recorder["invalid_expected"] += 1

    expected = case["expected_pre"]
    start = time.perf_counter()

    try:
        if "error" in expected:
            with pytest.raises(ValueError):
                process_module_metrics(case["input"])
            elapsed = time.perf_counter() - start
            case_result.update({
                "status": "passed",
                "expectation": "ValueError",
                "elapsed": elapsed,
            })
            if case["type"] == "invalid":
                metrics_recorder["invalid_success"] += 1
        else:
            result = process_module_metrics(case["input"])
            elapsed = time.perf_counter() - start
            case_result.update({
                "status": "passed",
                "elapsed": elapsed,
                "output": result,
            })

            summary = result
            expected_summary = expected["summary"]

            assert summary["module_count"] == expected_summary["module_count"]
            assert summary["breaches"] == expected["breaches"]
            assert summary["avg_coverage"] == pytest.approx(
                expected_summary["avg_coverage"], rel=1e-3, abs=1e-3
            )
            assert summary["median_coverage"] == pytest.approx(
                expected_summary["median_coverage"], rel=1e-3, abs=1e-3
            )
            assert summary["weighted_risk"] == pytest.approx(
                expected_summary["weighted_risk"], rel=1e-3, abs=1e-6
            )

            if case["type"] == "edge":
                metrics_recorder["edge_success"] += 1
    except AssertionError:
        metrics_recorder["failed"] += 1
        case_result["status"] = "failed"
        raise
    else:
        metrics_recorder["passed"] += 1
    finally:
        if "elapsed" not in case_result:
            case_result["elapsed"] = time.perf_counter() - start
        metrics_recorder["cases"].append(case_result)
