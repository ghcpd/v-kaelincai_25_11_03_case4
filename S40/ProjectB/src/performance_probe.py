from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .refactored_code import summarize_transactions

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "test_data.json"


def _generate_transactions(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    if "transactions" in payload:
        return payload["transactions"]
    if "generated" in payload:
        spec = payload["generated"]
        count = int(spec["count"])
        id_prefix = spec.get("id_prefix", "generated")
        categories: List[str] = spec.get("categories", ["uncategorized"])
        currencies: List[str] = spec.get("currencies", ["USD"])
        modulus = int(spec.get("amount_modulus", 1))
        offset = float(spec.get("amount_offset", 1))
        factor = float(spec.get("amount_factor", 1))
        base = float(spec.get("amount_base", 0))
        seed_amounts: List[float] = [float(v) for v in spec.get("seed_amounts", [])]

        for index in range(count):
            if seed_amounts:
                amount = seed_amounts[index % len(seed_amounts)]
            else:
                amount = ((index % modulus) + offset) * factor + base
            yield {
                "id": f"{id_prefix}-{index}",
                "amount": amount,
                "category": categories[index % len(categories)],
                "currency": currencies[index % len(currencies)],
            }
        return
    if "raw" in payload:
        return payload["raw"]
    raise ValueError("Unsupported payload in test data")


def load_cases() -> List[Dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))["cases"]


def _p95(values: List[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(round(0.95 * (len(ordered) - 1)))
    return ordered[index]


def measure_performance() -> Dict[str, Any]:
    rows = []
    for case in load_cases():
        if case.get("expect_exception"):
            continue
        payload = case["input"]
        kwargs = {}
        if "high_value_threshold" in payload:
            kwargs["high_value_threshold"] = payload["high_value_threshold"]

        transactions = list(_generate_transactions(payload))
        timings: List[float] = []
        for _ in range(30):
            start = time.perf_counter()
            summarize_transactions(transactions, **kwargs)
            timings.append(time.perf_counter() - start)

        avg = statistics.fmean(timings)
        rows.append(
            {
                "case": case["name"],
                "avg_ms": avg * 1000.0,
                "min_ms": min(timings) * 1000.0,
                "max_ms": max(timings) * 1000.0,
                "p95_ms": _p95(timings) * 1000.0,
            }
        )

    aggregate_avg = statistics.fmean(row["avg_ms"] for row in rows)
    aggregate_p95 = statistics.fmean(row["p95_ms"] for row in rows)

    return {
        "cases": rows,
        "mean_of_avgs_ms": aggregate_avg,
        "mean_p95_ms": aggregate_p95,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark refactored implementation")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "performance" / "time_refactored.json",
        help="Destination file for JSON statistics.",
    )
    args = parser.parse_args()
    results = measure_performance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
