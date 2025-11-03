"""Refactored implementation of compute_statistics.
Improvements:
- Single pass aggregation (O(n)) plus controlled stack traversal for subtasks
- Clear validation and error accumulation
- Excludes negative durations from total (counts them separately)
- Accurate category counts without duplication
- Efficient iterative depth & nested counting using explicit stack
- Supports JSON string input using orjson when available (falls back to json)
- Type hints and dataclass for Task representation
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json

try:  # Optional faster JSON
    import orjson  # type: ignore
    _FAST_JSON = True
except Exception:
    _FAST_JSON = False

DURATION_KEY = "duration"
SUBTASKS_KEY = "subtasks"
CATEGORY_KEY = "category"

@dataclass
class Task:
    category: str
    duration: float
    subtasks: List['Task']

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Optional['Task']:
        if not isinstance(d, dict):
            return None
        if CATEGORY_KEY not in d or DURATION_KEY not in d:
            return None
        cat = d[CATEGORY_KEY]
        dur = d[DURATION_KEY]
        if not isinstance(cat, str) or not isinstance(dur, (int, float)):
            return None
        subs_raw = d.get(SUBTASKS_KEY, [])
        subs: List[Task] = []
        if isinstance(subs_raw, list):
            for s in subs_raw:
                t = Task.from_dict(s)
                if t is not None:
                    subs.append(t)
        return Task(category=cat, duration=float(dur), subtasks=subs)


def _parse_input(data: Any, errors: List[str]) -> tuple[List[Dict[str, Any]], int]:
    if isinstance(data, str):
        try:
            if _FAST_JSON:
                data = orjson.loads(data)
            else:
                data = json.loads(data)
        except Exception as e:
            errors.append(f"JSON parse failed: {e}")
            return ([], 1)
    if not isinstance(data, list):
        errors.append("Input not a list")
        return ([], 1)
    return (data, 0)  # list of dicts (maybe invalid members)


def compute_statistics(data: Any, *, validate: bool = True) -> Dict[str, Any]:
    errors: List[str] = []
    raw_list, top_level_invalid = _parse_input(data, errors)

    total_tasks = 0
    total_duration = 0.0
    negative_duration_tasks = 0
    categories: Dict[str, int] = {}
    invalid_records = top_level_invalid

    # We'll also handle nested traversal iteratively; build Task objects optionally
    task_objs: List[Task] = []
    for item in raw_list:
        t = Task.from_dict(item) if validate else item  # type: ignore
        if not isinstance(t, Task):
            invalid_records += 1
            continue
        total_tasks += 1
        if t.duration < 0:
            negative_duration_tasks += 1
        else:
            total_duration += t.duration
        categories[t.category] = categories.get(t.category, 0) + 1
        task_objs.append(t)

    # Iterative traversal for nested subtasks
    nested_subtask_count = 0
    max_depth = 0
    stack: List[tuple[Task, int]] = [(t, 1) for t in task_objs]
    while stack:
        current, depth = stack.pop()
        if depth > max_depth:
            max_depth = depth
        # Push subtasks
        if current.subtasks:
            for st in current.subtasks:
                nested_subtask_count += 1
                stack.append((st, depth + 1))
                # Account categories and tasks for nested items
                categories[st.category] = categories.get(st.category, 0) + 1
                total_tasks += 1
                if st.duration < 0:
                    negative_duration_tasks += 1
                else:
                    total_duration += st.duration

    avg_duration = (total_duration / (total_tasks - negative_duration_tasks)) if (total_tasks - negative_duration_tasks) > 0 else None

    return {
        "total_tasks": total_tasks,
        "total_duration": int(total_duration) if total_duration.is_integer() else total_duration,
        "avg_duration": avg_duration,
        "categories": categories,
        "invalid_records": invalid_records,
        "negative_duration_tasks": negative_duration_tasks,
        "nested_subtask_count": nested_subtask_count,
        "max_depth": max_depth if total_tasks else 0,
        "errors": errors,
    }


if __name__ == "__main__":  # Quick sanity run
    sample = [{"id": 1, "category": "build", "duration": 5}]
    print(compute_statistics(sample))
