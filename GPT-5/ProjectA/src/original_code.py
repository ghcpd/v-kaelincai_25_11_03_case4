"""Pre-refactor implementation of compute_statistics.
Intentionally includes:
- Repetitive loops over data
- Poor error handling (broad exceptions)
- Duplicated code for category counting
- Inefficient recursion for depth per record
- Inclusion of negative durations in total (bug)
Contract (intended, but not always met here):
Input: list[dict] | JSON string | other
Output: dict with metrics
"""
from __future__ import annotations
import json
from typing import Any, Dict, List

# NOTE: Anti-pattern: global constants embedded mid-file
DURATION_KEY = "duration"


def _is_valid_record(r: Any) -> bool:
    return isinstance(r, dict) and "category" in r and DURATION_KEY in r


def _count_categories_loop_a(data: List[dict]) -> Dict[str, int]:
    cats: Dict[str, int] = {}
    for item in data:
        if not _is_valid_record(item):
            continue
        c = item.get("category")
        if c in cats:
            cats[c] += 1
        else:
            cats[c] = 1
    return cats


def _count_categories_loop_b(data: List[dict]) -> Dict[str, int]:
    # Duplicate of loop_a with tiny change (redundant) to simulate poor refactor candidate
    result: Dict[str, int] = {}
    for i in range(len(data)):
        rec = data[i]
        if not _is_valid_record(rec):
            continue
        cat = rec.get("category")
        prev = result.get(cat, 0)
        result[cat] = prev + 1
    return result


def _depth(record: dict) -> int:
    # Inefficient recursion computing depth every time from scratch
    if not isinstance(record, dict):
        return 0
    if "subtasks" not in record or not isinstance(record["subtasks"], list) or len(record["subtasks"]) == 0:
        return 1
    return 1 + max((_depth(st) for st in record["subtasks"]), default=0)


def _collect_all_tasks(record: dict) -> List[dict]:
    # Recursively expand tasks (inefficient list concatenations)
    tasks = [record]
    subs = record.get("subtasks")
    if isinstance(subs, list):
        for s in subs:
            tasks.extend(_collect_all_tasks(s))
    return tasks


def compute_statistics(data: Any) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {
        "total_tasks": 0,
        "total_duration": 0,
        "avg_duration": None,
        "categories": {},
        "invalid_records": 0,
        "negative_duration_tasks": 0,
        "nested_subtask_count": 0,
        "max_depth": 0,
        "errors": [],
    }
    try:
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, list):
            metrics["errors"].append("Input not a list")
            metrics["invalid_records"] += 1
            return metrics
    except Exception as e:  # Broad except anti-pattern
        metrics["errors"].append(f"Failed to parse: {e}")
        return metrics

    # First pass: count total and sum durations (BUG: includes negative durations)
    total_duration = 0
    total_tasks = 0
    negative_cnt = 0
    for rec in data:
        if not _is_valid_record(rec):
            metrics["invalid_records"] += 1
            continue
        total_tasks += 1
        dur = rec.get(DURATION_KEY, 0)
        if isinstance(dur, (int, float)):
            total_duration += dur
            if dur < 0:
                negative_cnt += 1
        # Depth recomputed separately later

    # Second pass: categories (two redundant loops merged poorly)
    cats_a = _count_categories_loop_a(data)
    cats_b = _count_categories_loop_b(data)
    # Merge (inefficient):
    merged: Dict[str, int] = {}
    for k, v in cats_a.items():
        merged[k] = merged.get(k, 0) + v
    for k, v in cats_b.items():
        merged[k] = merged.get(k, 0) + v

    # Third pass: depth and nested tasks
    all_subtasks_count = 0
    max_depth = 0
    for rec in data:
        if _is_valid_record(rec):
            d = _depth(rec)
            if d > max_depth:
                max_depth = d
            expanded = _collect_all_tasks(rec)
            all_subtasks_count += max(0, len(expanded) - 1)

    metrics["total_tasks"] = total_tasks
    metrics["total_duration"] = total_duration
    metrics["avg_duration"] = (total_duration / total_tasks) if total_tasks else None
    metrics["categories"] = merged  # NOTE: double counts
    metrics["negative_duration_tasks"] = negative_cnt
    metrics["nested_subtask_count"] = all_subtasks_count
    metrics["max_depth"] = max_depth
    return metrics


if __name__ == "__main__":  # Simple manual run
    sample = [{"id": 1, "category": "build", "duration": 5}]
    print(compute_statistics(sample))
