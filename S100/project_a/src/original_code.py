"""Pre-refactor analytics helper for module quality metrics.

The implementation intentionally intertwines validation, aggregation, and diagnostics
logic. It performs multiple passes over the data, raises errors for malformed
records, and uses ad-hoc calculations that will later be improved in the
refactored version.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def _expect_mapping(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError("Expected mapping payload")
    return payload


def process_module_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process module metrics and return aggregate insights.

    Parameters
    ----------
    payload: Dict[str, Any]
        Mapping containing ``modules`` and optional ``quality_thresholds``.

    Returns
    -------
    Dict[str, Any]
        Summary dictionary with module count, coverage statistics, weighted
        risk, and modules that breach supplied thresholds.

    Notes
    -----
    This baseline implementation raises ``ValueError`` when it encounters
    malformed records instead of collecting diagnostics. It also executes
    multiple passes over the same data, which will be addressed in the
    refactored version.
    """

    data = _expect_mapping(payload)
    modules = data.get("modules", [])
    if not isinstance(modules, list):
        raise ValueError("'modules' must be a list")

    thresholds = data.get("quality_thresholds") or {}
    if not isinstance(thresholds, dict):
        raise ValueError("'quality_thresholds' must be a mapping if provided")

    coverage_min = thresholds.get("coverage_min", 0.0)
    complexity_max = thresholds.get("complexity_max", float("inf"))
    loc_max = thresholds.get("loc_max", float("inf"))

    cleaned_modules: List[Dict[str, Any]] = []
    coverage_values: List[float] = []
    complexities: List[int] = []
    locs: List[int] = []
    names: List[str] = []

    for idx in range(len(modules)):
        module_info = modules[idx]
        if not isinstance(module_info, dict):
            raise ValueError(f"Module entry at index {idx} is not a mapping")

        if "module" not in module_info:
            raise ValueError(f"Module entry at index {idx} is missing 'module'")

        module_name = module_info.get("module")
        loc_value = module_info.get("loc")
        complexity_value = module_info.get("complexity")
        coverage_value = module_info.get("coverage")
        last_updated = module_info.get("last_updated")
        tags = module_info.get("tags") or []

        try:
            loc_value = int(loc_value)
            complexity_value = int(complexity_value)
            coverage_value = float(coverage_value)
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Invalid metric types for module '{module_name}'"
            ) from exc

        if coverage_value < 0 or coverage_value > 100:
            raise ValueError(
                f"Coverage for module '{module_name}' must be between 0 and 100"
            )

        cleaned_modules.append(
            {
                "module": module_name,
                "loc": loc_value,
                "complexity": complexity_value,
                "coverage": coverage_value,
                "last_updated": last_updated,
                "tags": tags,
            }
        )

        coverage_values.append(coverage_value)
        complexities.append(complexity_value)
        locs.append(loc_value)
        names.append(module_name)

    module_count = len(cleaned_modules)

    if module_count == 0:
        return {
            "module_count": 0,
            "avg_coverage": 0.0,
            "median_coverage": 0.0,
            "weighted_risk": 0.0,
            "breaches": [],
        }

    # First pass for averages
    average_coverage = sum(coverage_values) / float(len(coverage_values))

    # Second pass for median (inefficiently recompute)
    sorted_cov = sorted(coverage_values)
    mid = len(sorted_cov) // 2
    if len(sorted_cov) % 2:
        median_coverage = sorted_cov[mid]
    else:
        median_coverage = (sorted_cov[mid - 1] + sorted_cov[mid]) / 2.0

    # Third pass for weighted risk
    weighted_risk = 0.0
    for idx in range(len(cleaned_modules)):
        weighted_risk += locs[idx] * complexities[idx]
    total_loc = sum(locs) if locs else 1
    total_complexity = sum(complexities) if complexities else 1
    if not total_loc or not total_complexity:
        weighted_risk = 0.0
    else:
        weighted_risk = weighted_risk / (total_loc * total_complexity)

    breaches: List[str] = []
    for idx in range(len(cleaned_modules)):
        module_snapshot = cleaned_modules[idx]
        if module_snapshot["coverage"] < coverage_min:
            breaches.append(module_snapshot["module"])
        elif module_snapshot["complexity"] > complexity_max:
            breaches.append(module_snapshot["module"])
        elif module_snapshot["loc"] > loc_max:
            breaches.append(module_snapshot["module"])

    # Redundant duplicate detection (introduces duplicates into the breaches list)
    duplicates: List[str] = []
    seen = set()
    for name in names:
        if name in seen and name not in duplicates:
            duplicates.append(name)
        else:
            seen.add(name)
    if duplicates:
        breaches.extend(duplicates)

    return {
        "module_count": module_count,
        "avg_coverage": round(average_coverage, 3),
        "median_coverage": round(median_coverage, 3),
        "weighted_risk": round(weighted_risk, 6),
        "breaches": breaches,
    }


__all__ = ["process_module_metrics"]
