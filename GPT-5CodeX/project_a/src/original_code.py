"""Original, pre-refactor implementation for transaction analytics.

This module intentionally keeps duplicated loops and defensive checks to
simulate a less maintainable baseline that still produces correct results.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

RISK_TAGS = {"fraud", "chargeback", "dispute"}


def _as_list(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def analyze_transactions(payload: Any) -> Dict[str, Any]:
    """Analyze raw transaction payload with redundant computations.

    The function validates the payload, normalises transaction entries,
    and aggregates summary statistics. It is deliberately repetitive so that
    the refactored version can demonstrate structural improvements.
    """
    if not isinstance(payload, dict):
        raise ValueError("Input must be a dictionary with a 'transactions' key.")
    if "transactions" not in payload:
        raise ValueError("Input dictionary must contain 'transactions'.")

    transactions = payload["transactions"]
    if not isinstance(transactions, list):
        raise ValueError("'transactions' must be provided as a list.")

    threshold = float(payload.get("threshold", 1000.0))
    base_currency = payload.get("base_currency", "USD")
    home_country = payload.get("home_country")

    normalized: List[Dict[str, Any]] = []
    invalid_entries: List[Dict[str, Any]] = []

    # First pass: perform validation and keep large intermediate structure.
    for index in range(len(transactions)):
        entry = transactions[index]
        if not isinstance(entry, dict):
            invalid_entries.append({"index": index, "reason": "not_a_dict"})
            continue

        if "amount" not in entry:
            invalid_entries.append({"index": index, "reason": "missing_amount"})
            continue

        amount_raw = entry.get("amount")
        try:
            amount_value = float(amount_raw)
        except (TypeError, ValueError):
            invalid_entries.append({"index": index, "reason": "invalid_amount"})
            continue

        category_value = entry.get("category")
        if not isinstance(category_value, str) or not category_value.strip():
            category_value = "uncategorized"
        currency_value = entry.get("currency")
        tags_value = _as_list(entry.get("tags"))
        country_value = entry.get("country")

        normalized.append(
            {
                "index": index,
                "id": entry.get("id"),
                "amount": amount_value,
                "category": category_value,
                "currency": currency_value if currency_value else base_currency,
                "raw_currency": currency_value,
                "tags": [t for t in tags_value if isinstance(t, str)],
                "country": country_value,
            }
        )

    # Second pass: compute total amount (redundant but kept for baseline).
    total_amount = 0.0
    for item in normalized:
        total_amount += float(item["amount"])

    # Third pass: build category totals with repeated lookups.
    category_totals: Dict[str, float] = {}
    for item in normalized:
        category_name = item["category"] if isinstance(item["category"], str) else "uncategorized"
        if not category_name.strip():  # defensive strip
            category_name = "uncategorized"
        if category_name not in category_totals:
            category_totals[category_name] = 0.0
        category_totals[category_name] += float(item["amount"])

    # Fourth pass: compute currency mismatches using stored raw values.
    currency_mismatch_count = 0
    for item in normalized:
        raw_currency = item.get("raw_currency")
        if raw_currency and raw_currency != base_currency:
            currency_mismatch_count += 1

    # Fifth pass: detect high-risk transactions with verbose logic.
    high_risk_transactions: List[Dict[str, Any]] = []
    for item in normalized:
        reasons: List[str] = []
        amount_value = float(item["amount"])
        if amount_value > threshold:
            reasons.append("amount_exceeds_threshold")
        for tag in item.get("tags", []):
            if isinstance(tag, str) and tag.lower() in RISK_TAGS:
                reasons.append("high_risk_tag")
                break
        country_value = item.get("country")
        if country_value and home_country and country_value != home_country:
            reasons.append("foreign_transaction")
        if reasons:
            deduped = sorted(set(reasons))
            high_risk_transactions.append(
                {
                    "id": item.get("id"),
                    "amount": amount_value,
                    "reason": ";".join(deduped),
                }
            )

    # Sixth pass: gather valid amounts again for average calculation.
    valid_amounts = []
    for item in normalized:
        valid_amounts.append(float(item["amount"]))
    transaction_count = len(valid_amounts)
    average_amount = float(total_amount / transaction_count) if transaction_count else 0.0

    return {
        "total_amount": float(total_amount),
        "average_amount": average_amount,
        "transaction_count": transaction_count,
        "category_totals": category_totals,
        "high_risk_transactions": high_risk_transactions,
        "currency_mismatch_count": currency_mismatch_count,
        "invalid_entries": invalid_entries,
    }


__all__ = ["analyze_transactions"]


if __name__ == "__main__":
    import json
    import pathlib

    sample_path = pathlib.Path(__file__).resolve().parents[1] / "data" / "test_data.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    example = data["cases"][0]["input"]
    print(json.dumps(analyze_transactions(example), indent=2))
```