import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pytest

from src.refactored_code import summarize_transactions

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
    content = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return content["cases"]


@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["name"])
def test_summarize_transactions(case: Dict[str, Any]):
    case_input = case["input"]
    expected = case["expected"]
    transactions = _generate_transactions(case_input)
    kwargs = {}
    if "high_value_threshold" in case_input:
        kwargs["high_value_threshold"] = case_input["high_value_threshold"]

    if case.get("expect_exception"):
        with pytest.raises(eval(case["expect_exception"])):
            summarize_transactions(transactions, **kwargs)
        return

    result = summarize_transactions(transactions, **kwargs)

    assert result["transaction_count"] == expected["transaction_count"]
    assert result["high_value_ids"] == expected["high_value_ids"]
    assert result["invalid_entries"] == expected["invalid_entries"]

    assert result["category_totals"] == pytest.approx(expected["category_totals"])
    assert result["currency_totals"] == pytest.approx(expected["currency_totals"])
    assert result["total_amount"] == pytest.approx(expected["total_amount"])


@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["name"])
def test_summary_is_idempotent(case: Dict[str, Any]):
    case_input = case["input"]
    transactions = _generate_transactions(case_input)
    kwargs = {}
    if "high_value_threshold" in case_input:
        kwargs["high_value_threshold"] = case_input["high_value_threshold"]

    if case.get("expect_exception"):
        with pytest.raises(eval(case["expect_exception"])):
            summarize_transactions(transactions, **kwargs)
        return

    first = summarize_transactions(transactions, **kwargs)
    second = summarize_transactions(transactions, **kwargs)

    assert first == second


def test_rejects_none_input():
    with pytest.raises(ValueError):
        summarize_transactions(None)  # type: ignore[arg-type]
