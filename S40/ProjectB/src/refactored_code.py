"""Refactored transaction summarisation implementation.

Key improvements over the original baseline:

* Single pass over the input iterable (no materialisation).
* Shared helper functions for parsing, normalisation, and deduplication.
* Dataclass-driven data flow that simplifies code review and maintenance.
* Deterministic output ordering with minimal post-processing.
* Clear error handling describing invalid entries without repeating logic.

The external contract remains identical to the baseline implementation so the
same test-suite can validate both versions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping

_VALID_STATUS = {"pending", "confirmed", "settled", "cancelled", None}


@dataclass
class NormalisedTransaction:
    identifier: str
    amount: float
    category: str
    currency: str
    index: int

    @property
    def amount_float(self) -> float:
        return self.amount


def _iter_records(records: Iterable[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    if records is None:
        raise ValueError("records cannot be None")
    try:
        iterator = iter(records)
    except TypeError as exc:  # pragma: no cover - defensive
        raise ValueError("records must be iterable") from exc
    for payload in iterator:
        yield payload


def _coerce_identifier(raw_id: Any, index: int) -> str:
    if raw_id is None:
        return f"_generated_{index}"
    return str(raw_id)


def _parse_amount(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("empty_amount")
        try:
            return float(stripped)
        except ValueError as exc:
            raise ValueError("non_numeric_amount") from exc
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("non_numeric_amount") from exc


def _normalise_category(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip().lower()
    return "uncategorized"


def _normalise_currency(value: Any) -> str:
    if isinstance(value, str) and value:
        return value.upper()
    return "USD"


def _validate_status(value: Any) -> str | None:
    return value if value in _VALID_STATUS else None


def _build_summary(
    deduped: MutableMapping[str, NormalisedTransaction],
    invalid_entries: List[Dict[str, Any]],
    high_value_threshold: float,
) -> Dict[str, Any]:
    total_amount = 0.0
    category_totals: Dict[str, float] = {}
    currency_totals: Dict[str, float] = {}
    high_value_ids: List[str] = []
    threshold = float(high_value_threshold)

    for identifier, item in deduped.items():
        total_amount += item.amount

        category_totals[item.category] = category_totals.get(item.category, 0.0) + item.amount
        currency_totals[item.currency] = currency_totals.get(item.currency, 0.0) + item.amount

        if item.amount >= threshold:
            high_value_ids.append(identifier)

    def _ordered(source: Mapping[str, float]) -> Dict[str, float]:
        return {key: source[key] for key in sorted(source)}

    high_value_ids.sort()
    invalid_entries.sort(key=lambda row: row["index"])

    return {
        "total_amount": total_amount,
        "category_totals": _ordered(category_totals),
        "currency_totals": _ordered(currency_totals),
        "invalid_entries": invalid_entries,
        "transaction_count": len(deduped),
        "high_value_ids": high_value_ids,
    }


def summarize_transactions(
    records: Iterable[Mapping[str, Any]],
    *,
    high_value_threshold: float = 1000.0,
) -> Dict[str, Any]:
    deduped: Dict[str, NormalisedTransaction] = {}
    invalid_entries: List[Dict[str, Any]] = []

    for index, raw in enumerate(_iter_records(records)):
        if not isinstance(raw, Mapping):
            invalid_entries.append({"index": index, "id": None, "error": "not_mapping"})
            continue

        identifier = _coerce_identifier(raw.get("id"), index)

        try:
            amount = _parse_amount(raw.get("amount", 0))
        except ValueError as exc:
            invalid_entries.append({"index": index, "id": identifier, "error": str(exc)})
            continue

        category = _normalise_category(raw.get("category"))
        currency = _normalise_currency(raw.get("currency"))
        status = _validate_status(raw.get("status"))

        payload: Dict[str, Any] = dict(raw)
        payload.update(
            {
                "id": identifier,
                "amount": amount,
                "category": category,
                "currency": currency,
                "status": status,
            }
        )

        deduped[identifier] = NormalisedTransaction(
            identifier=identifier,
            amount=amount,
            category=payload["category"],
            currency=payload["currency"],
            index=index,
        )

    return _build_summary(deduped, invalid_entries, high_value_threshold)


__all__ = ["summarize_transactions"]
