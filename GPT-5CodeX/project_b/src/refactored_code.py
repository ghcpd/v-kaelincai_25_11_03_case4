"""Refactored transaction analytics implementation.

This version focuses on maintainability by centralising validation logic,
reducing repeated passes, and providing clearer domain abstractions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RISK_TAGS = frozenset({"fraud", "chargeback", "dispute"})


@dataclass(frozen=True)
class NormalizedTransaction:
    index: int
    identifier: Any
    amount: float
    category: str
    currency: str
    mismatched_currency: bool
    tags: Tuple[str, ...]
    country: str | None


def analyze_transactions(payload: Any) -> Dict[str, Any]:
    """Produce summary metrics for a transaction payload."""
    transactions, threshold, base_currency, home_country = _validate_payload(payload)

    invalid_entries: List[Dict[str, Any]] = []
    normalized, currency_mismatch_count = _normalize_transactions(
        transactions, base_currency, invalid_entries
    )

    summary = _aggregate(normalized, threshold, home_country)
    summary["currency_mismatch_count"] = currency_mismatch_count
    summary["invalid_entries"] = invalid_entries
    return summary


def _validate_payload(payload: Any) -> Tuple[List[Any], float, str, str | None]:
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
    return transactions, threshold, base_currency, home_country


def _normalize_transactions(
    transactions: Iterable[Any],
    base_currency: str,
    invalid_entries: List[Dict[str, Any]],
) -> Tuple[List[NormalizedTransaction], int]:
    normalized: List[NormalizedTransaction] = []
    mismatch_count = 0

    for index, entry in enumerate(transactions):
        maybe_tx = _normalize_single(entry, index, base_currency, invalid_entries)
        if maybe_tx is None:
            continue
        normalized.append(maybe_tx)
        if maybe_tx.mismatched_currency:
            mismatch_count += 1
    return normalized, mismatch_count


def _normalize_single(
    entry: Any,
    index: int,
    base_currency: str,
    invalid_entries: List[Dict[str, Any]],
) -> NormalizedTransaction | None:
    if not isinstance(entry, dict):
        invalid_entries.append({"index": index, "reason": "not_a_dict"})
        return None

    if "amount" not in entry:
        invalid_entries.append({"index": index, "reason": "missing_amount"})
        return None

    amount = _parse_amount(entry.get("amount"))
    if amount is None:
        invalid_entries.append({"index": index, "reason": "invalid_amount"})
        return None

    category_raw = entry.get("category")
    if isinstance(category_raw, str) and category_raw.strip():
        category = category_raw.strip()
    else:
        category = "uncategorized"

    currency_raw = entry.get("currency") if isinstance(entry.get("currency"), str) else None
    mismatched_currency = bool(currency_raw and currency_raw != base_currency)
    currency = currency_raw or base_currency

    tags = _normalize_tags(entry.get("tags"))
    country = entry.get("country") if isinstance(entry.get("country"), str) else entry.get("country")

    return NormalizedTransaction(
        index=index,
        identifier=entry.get("id"),
        amount=amount,
        category=category,
        currency=currency,
        mismatched_currency=mismatched_currency,
        tags=tags,
        country=country,
    )


def _parse_amount(value: Any) -> float | None:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(amount):
        return None
    return amount


def _normalize_tags(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        filtered = [str(tag).strip() for tag in value if isinstance(tag, str) and tag.strip()]
        return tuple(filtered)
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()


def _aggregate(
    normalized: Sequence[NormalizedTransaction],
    threshold: float,
    home_country: str | None,
) -> Dict[str, Any]:
    total_amount = 0.0
    category_totals: Dict[str, float] = {}
    high_risk_transactions: List[Dict[str, Any]] = []

    for tx in normalized:
        total_amount += tx.amount
        category_totals[tx.category] = category_totals.get(tx.category, 0.0) + tx.amount
        risk_reason = _detect_risk(tx, threshold, home_country)
        if risk_reason:
            high_risk_transactions.append(
                {
                    "id": tx.identifier,
                    "amount": tx.amount,
                    "reason": risk_reason,
                }
            )

    transaction_count = len(normalized)
    average_amount = total_amount / transaction_count if transaction_count else 0.0

    return {
        "total_amount": float(total_amount),
        "average_amount": float(average_amount),
        "transaction_count": transaction_count,
        "category_totals": {k: float(v) for k, v in category_totals.items()},
        "high_risk_transactions": high_risk_transactions,
    }


def _detect_risk(tx: NormalizedTransaction, threshold: float, home_country: str | None) -> str | None:
    reasons: List[str] = []
    if tx.amount > threshold:
        reasons.append("amount_exceeds_threshold")

    for tag in tx.tags:
        if tag.lower() in RISK_TAGS:
            reasons.append("high_risk_tag")
            break

    if tx.country and home_country and tx.country != home_country:
        reasons.append("foreign_transaction")

    if not reasons:
        return None
    return ";".join(sorted(set(reasons)))


__all__ = ["analyze_transactions"]


if __name__ == "__main__":
    import json
    import pathlib

    sample_path = pathlib.Path(__file__).resolve().parents[1] / "data" / "test_data.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    example = data["cases"][0]["input"]
    print(json.dumps(analyze_transactions(example), indent=2))
