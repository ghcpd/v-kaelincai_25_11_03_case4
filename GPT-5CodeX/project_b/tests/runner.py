"""Test harness for the refactored implementation."""
from __future__ import annotations

import argparse
import json
import math
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.refactored_code import analyze_transactions

FLOAT_TOLERANCE = 1e-6
EDGE_CASE_TYPES = {"edge", "performance"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute transaction analytics test cases (refactored).")
    default_data = Path(__file__).resolve().parents[1] / "data" / "test_data.json"
    parser.add_argument("--data-file", type=Path, default=default_data)
    parser.add_argument("--log-file", type=Path, default=Path(__file__).resolve().parents[1] / "logs" / "log_refactored.txt")
    parser.add_argument("--perf-file", type=Path, default=Path(__file__).resolve().parents[1] / "performance" / "time_refactored.txt")
    parser.add_argument("--implementation-name", default="Project B - Refactored")
    return parser.parse_args()


def load_cases(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("cases", [])


def compare(expected: Any, actual: Any, path: str = "") -> Tuple[bool, str]:
    location = path or "root"
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False, f"Type mismatch at {location}: expected dict got {type(actual).__name__}"
        for key in expected:
            if key not in actual:
                return False, f"Missing key '{key}' at {location}"
        for key in actual:
            if key not in expected:
                return False, f"Unexpected key '{key}' at {location}"
        for key in expected:
            ok, message = compare(expected[key], actual[key], f"{location}.{key}")
            if not ok:
                return ok, message
        return True, ""

    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False, f"Type mismatch at {location}: expected list got {type(actual).__name__}"
        if len(expected) != len(actual):
            return False, f"Length mismatch at {location}: expected {len(expected)} got {len(actual)}"
        for idx, (exp_item, act_item) in enumerate(zip(expected, actual)):
            ok, message = compare(exp_item, act_item, f"{location}[{idx}]")
            if not ok:
                return ok, message
        return True, ""

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if math.isclose(float(expected), float(actual), rel_tol=FLOAT_TOLERANCE, abs_tol=FLOAT_TOLERANCE):
            return True, ""
        return False, f"Numeric mismatch at {location}: expected {expected} got {actual}"

    if expected != actual:
        return False, f"Value mismatch at {location}: expected {expected!r} got {actual!r}"
    return True, ""


def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    case_input = case.get("input")
    expected = case.get("expected")
    expect_error = case.get("expect_error")
    start = time.perf_counter()
    error: Exception | None = None
    output: Any = None
    try:
        output = analyze_transactions(case_input)
    except Exception as exc:  # pragma: no cover - defensive
        error = exc
    duration = (time.perf_counter() - start) * 1000.0

    if expect_error:
        if error is None:
            return {
                "name": case.get("name"),
                "case_type": case.get("case_type", "unknown"),
                "status": "failed",
                "duration_ms": duration,
                "details": "Expected error but implementation returned successfully.",
            }
        expected_type = expect_error.get("type")
        message_contains = expect_error.get("message_contains", "")
        type_match = not expected_type or error.__class__.__name__ == expected_type
        message_match = message_contains.lower() in str(error).lower()
        status = "passed" if type_match and message_match else "failed"
        details = "" if status == "passed" else f"Unexpected error: {error}"
        return {
            "name": case.get("name"),
            "case_type": case.get("case_type", "unknown"),
            "status": status,
            "duration_ms": duration,
            "details": details,
        }

    if error is not None:
        return {
            "name": case.get("name"),
            "case_type": case.get("case_type", "unknown"),
            "status": "failed",
            "duration_ms": duration,
            "details": f"Raised unexpected error: {error}",
        }

    ok, message = compare(expected, output)
    return {
        "name": case.get("name"),
        "case_type": case.get("case_type", "unknown"),
        "status": "passed" if ok else "failed",
        "duration_ms": duration,
        "details": message,
    }


def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for item in results if item["status"] == "passed")
    edge_cases = [item for item in results if item.get("case_type") in EDGE_CASE_TYPES]
    edge_passed = sum(1 for item in edge_cases if item["status"] == "passed")
    invalid_cases = [item for item in results if item.get("case_type") == "invalid"]
    invalid_passed = sum(1 for item in invalid_cases if item["status"] == "passed")

    return {
        "total_cases": total,
        "passed_cases": passed,
        "accuracy": (passed / total) if total else 0.0,
        "edge_case_success_rate": (edge_passed / len(edge_cases)) if edge_cases else None,
        "invalid_case_success_rate": (invalid_passed / len(invalid_cases)) if invalid_cases else None,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    args = parse_args()
    cases = load_cases(args.data_file)

    if not cases:
        raise SystemExit("No test cases found.")

    results: List[Dict[str, Any]] = []
    tracemalloc.start()
    overall_start = time.perf_counter()

    for case in cases:
        results.append(run_case(case))

    total_runtime = time.perf_counter() - overall_start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    metrics = compute_metrics(results)
    perf_payload = {
        "implementation": args.implementation_name,
        "total_runtime_seconds": total_runtime,
        "avg_case_runtime_ms": (total_runtime / len(results)) * 1000.0,
        "peak_memory_kib": peak / 1024.0,
        "timestamp_utc": metrics["timestamp_utc"],
    }

    log_payload = {
        "implementation": args.implementation_name,
        "cases": results,
        "metrics": metrics,
    }

    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    args.perf_file.parent.mkdir(parents=True, exist_ok=True)
    args.log_file.write_text(json.dumps(log_payload, indent=2), encoding="utf-8")
    args.perf_file.write_text(json.dumps(perf_payload, indent=2), encoding="utf-8")

    passed = metrics["passed_cases"]
    total = metrics["total_cases"]
    accuracy = metrics["accuracy"] * 100
    print(f"[{args.implementation_name}] Passed {passed}/{total} cases (accuracy={accuracy:.1f}%).")


if __name__ == "__main__":  # pragma: no cover
    main()
