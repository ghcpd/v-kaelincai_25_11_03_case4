"""
Original transaction summarization implementation.

This module intentionally contains a verbose and repetitive implementation that
serves as the "pre-refactor" baseline. The behaviour is already correct, but
several inefficiencies exist:

* Multiple loops perform similar tasks with duplicated logic.
* Helper routines are nested inside the main function rather than being reused.
* The code materialises iterables and recreates temporary structures
  unnecessarily.
* Error handling is scattered and harder to follow.

The refactored version in ProjectB streamlines these concerns while providing
identical external behaviour.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


_VALID_STATUS = {"pending", "confirmed", "settled", "cancelled", None}


def summarize_transactions(
    records: Iterable[Dict[str, Any]],
    *,
    high_value_threshold: float = 1000.0,
) -> Dict[str, Any]:
    """Aggregate transaction information.

    Parameters
    ----------
    records:
        Iterable of mappings describing transactions. Each mapping should
        provide an ``id`` (string/integer), ``amount`` (numeric or numeric
        string), ``category`` (string), optional ``currency`` (string), and
        optional ``status``.
    high_value_threshold:
        Amount used to collect ``high_value_ids``.

    Returns
    -------
    Dict[str, Any]
        Summary containing totals, category and currency breakdowns, invalid
        entry diagnostics, and deduplicated high-value transaction ids.

    Raises
    ------
    ValueError
        If ``records`` cannot be iterated or is ``None``.
    """

    if records is None:
        raise ValueError("records cannot be None")

    try:
        iterator = iter(records)
    except TypeError as exc:  # pragma: no cover - defensive
        raise ValueError("records must be iterable") from exc

    materialised: List[Dict[str, Any]] = list(iterator)

    # Stage 1: validate structure and gather the most recent version for each id
    deduped: Dict[str, Dict[str, Any]] = {}
    invalid_entries: List[Dict[str, Any]] = []

    for index, entry in enumerate(materialised):
        if not isinstance(entry, dict):
            invalid_entries.append(
                {"index": index, "id": None, "error": "not_mapping"}
            )
            continue

        record_id = entry.get("id")
        record_id = str(record_id) if record_id is not None else f"_generated_{index}"

        # Duplicate amount parsing logic (intentionally verbose)
        raw_amount = entry.get("amount", 0)
        parsed_amount = None
        conversion_error: Tuple[str, str] | None = None
        if isinstance(raw_amount, (int, float)):
            parsed_amount = float(raw_amount)
        elif isinstance(raw_amount, str):
            stripped = raw_amount.strip()
            if stripped:
                try:
                    parsed_amount = float(stripped)
                except (TypeError, ValueError):
                    conversion_error = ("non_numeric_amount", stripped)
            else:
                conversion_error = ("empty_amount", stripped)
        else:
            try:
                parsed_amount = float(raw_amount)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                conversion_error = ("non_numeric_amount", str(raw_amount))

        if parsed_amount is None:
            invalid_entries.append(
                {
                    "index": index,
                    "id": record_id,
                    "error": conversion_error[0] if conversion_error else "non_numeric_amount",
                }
            )
            continue

        category = entry.get("category")
        if not isinstance(category, str) or not category.strip():
            category = "uncategorized"
        currency = entry.get("currency")
        if not isinstance(currency, str) or not currency:
            currency = "USD"
        status = entry.get("status")
        if status not in _VALID_STATUS:
            status = None

        # Another round of copying to simulate inefficiencies
        new_entry = dict(entry)
        new_entry["_parsed_amount"] = parsed_amount
        new_entry["_normalised_category"] = category.strip().lower()
        new_entry["_normalised_currency"] = currency.upper()
        new_entry["_status"] = status
        new_entry["_source_index"] = index

        deduped[record_id] = new_entry

    # Stage 2: aggregate metrics using yet another loop
    total_amount = 0.0
    category_totals: Dict[str, float] = {}
    currency_totals: Dict[str, float] = {}
    high_value_ids: List[str] = []
    high_value_threshold = float(high_value_threshold)

    for record_id, entry in deduped.items():
        parsed_amount = entry.get("_parsed_amount", 0.0)
        category_key = entry.get("_normalised_category", "uncategorized")
        currency_key = entry.get("_normalised_currency", "USD")

        total_amount += parsed_amount

        if category_key in category_totals:
            category_totals[category_key] += parsed_amount
        else:
            category_totals[category_key] = parsed_amount

        if currency_key not in currency_totals:
            currency_totals[currency_key] = parsed_amount
        else:
            currency_totals[currency_key] += parsed_amount

        if parsed_amount >= high_value_threshold:
            # more duplicated logic for high-value calculation
            if record_id not in high_value_ids:
                high_value_ids.append(record_id)

    # Stage 3: produce deterministic ordering for readability
    category_totals = {
        key: category_totals[key]
        for key in sorted(category_totals)
    }
    currency_totals = {
        key: currency_totals[key]
        for key in sorted(currency_totals)
    }
    high_value_ids.sort()
    invalid_entries.sort(key=lambda item: item["index"])

    return {
        "total_amount": total_amount,
        "category_totals": category_totals,
        "currency_totals": currency_totals,
        "invalid_entries": invalid_entries,
        "transaction_count": len(deduped),
        "high_value_ids": high_value_ids,
    }


__all__ = ["summarize_transactions"]
