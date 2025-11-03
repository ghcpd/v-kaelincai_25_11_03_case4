from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .original_code import summarize_transactions

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

        transactions: List[Dict[str, Any]] = []
        for index in range(count):
            if seed_amounts:
                amount = seed_amounts[index % len(seed_amounts)]
            else:
                amount = ((index % modulus) + offset) * factor + base
            transactions.append(
                {
                    "id": f"{id_prefix}-{index}",
                    "amount": amount,
                    "category": categories[index % len(categories)],
                    "currency": currencies[index % len(currencies)],
                }
            )
        return transactions
    if "raw" in payload:
        return payload["raw"]
    raise ValueError("Unsupported payload in test data")


def load_cases() -> List[Dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))["cases"]


def measure_performance() -> Dict[str, Any]:
    rows = []
    for case in load_cases():
        if case.get("expect_exception"):
            continue
        payload = case["input"]
        kwargs = {}
        if "high_value_threshold" in payload:
            kwargs["high_value_threshold"] = payload["high_value_threshold"]
        dataset = list(_generate_transactions(payload))

        timings: List[float] = []
        for _ in range(15):
            start = time.perf_counter()
            summarize_transactions(list(dataset), **kwargs)
            summarize_transactions(list(dataset), **kwargs)
            timings.append(time.perf_counter() - start)

        avg = statistics.mean(timings)
        rows.append(
            {
                "case": case["name"],
                "avg_ms": avg * 1000.0,
                "min_ms": min(timings) * 1000.0,
                "max_ms": max(timings) * 1000.0,
            }
        )

    overall = {
        "cases": rows,
        "mean_of_avgs_ms": statistics.mean(row["avg_ms"] for row in rows),
    }
    return overall


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark original implementation")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "performance" / "time_original.json",
        help="Destination file for JSON statistics.",
    )
    args = parser.parse_args()
    results = measure_performance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
