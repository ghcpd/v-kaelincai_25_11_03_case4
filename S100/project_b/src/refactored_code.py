"""Refactored analytics helper for module quality metrics.

Key improvements over the baseline implementation include:

* Strong separation of validation, aggregation, and diagnostics.
* Single-pass processing of the dataset using lightweight helper classes.
* Graceful handling of malformed records – they are recorded in diagnostics
  without aborting the entire job.
* Structured breach reporting that captures the concrete threshold violations
  per module while deduplicating repeated modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Sequence


class ValidationIssue(Exception):
    """Raised internally when a module payload cannot be canonicalised."""


@dataclass
class QualityThresholds:
    coverage_min: float = 0.0
    complexity_max: float = float("inf")
    loc_max: float = float("inf")

    @classmethod
    def from_mapping(cls, raw: Optional[MutableMapping[str, Any]]) -> "QualityThresholds":
        if raw is None:
            return cls()
        if not isinstance(raw, MutableMapping):
            raise TypeError("quality_thresholds must be a mapping when provided")

        kwargs: Dict[str, Any] = {}
        if "coverage_min" in raw and raw["coverage_min"] is not None:
            kwargs["coverage_min"] = float(raw["coverage_min"])
        if "complexity_max" in raw and raw["complexity_max"] is not None:
            kwargs["complexity_max"] = float(raw["complexity_max"])
        if "loc_max" in raw and raw["loc_max"] is not None:
            kwargs["loc_max"] = float(raw["loc_max"])
        return cls(**kwargs)


@dataclass
class ModuleRecord:
    module: str
    loc: int
    complexity: int
    coverage: float
    last_updated: Optional[str]
    tags: Sequence[str] = field(default_factory=tuple)


@dataclass
class AggregationState:
    thresholds: QualityThresholds
    module_count: int = 0
    coverage_values: List[float] = field(default_factory=list)
    risk_numerator: float = 0.0
    loc_sum: int = 0
    complexity_sum: int = 0
    breaches: Dict[str, set] = field(default_factory=dict)
    occurrences: Dict[str, int] = field(default_factory=dict)

    def record(self, record: ModuleRecord) -> None:
        self.module_count += 1
        self.coverage_values.append(record.coverage)
        self.risk_numerator += record.loc * record.complexity
        self.loc_sum += record.loc
        self.complexity_sum += record.complexity

        issues = self.breaches.setdefault(record.module, set())
        if record.coverage < self.thresholds.coverage_min:
            issues.add("coverage")
        if record.complexity > self.thresholds.complexity_max:
            issues.add("complexity")
        if record.loc > self.thresholds.loc_max:
            issues.add("loc")

        self.occurrences[record.module] = self.occurrences.get(record.module, 0) + 1

    def finalise(self) -> Dict[str, Any]:
        avg = sum(self.coverage_values) / self.module_count if self.module_count else 0.0
        med = median(self.coverage_values) if self.coverage_values else 0.0
        if self.loc_sum and self.complexity_sum:
            weighted = self.risk_numerator / (self.loc_sum * self.complexity_sum)
        else:
            weighted = 0.0

        breaches_payload: List[Dict[str, Any]] = []
        for module, issues in sorted(self.breaches.items()):
            issues = set(issues)
            duplicate_count = self.occurrences.get(module, 0)
            if duplicate_count > 1:
                issues.add("duplicate")
            if issues:
                breaches_payload.append(
                    {
                        "module": module,
                        "issues": sorted(issues),
                    }
                )

        return {
            "summary": {
                "module_count": self.module_count,
                "avg_coverage": round(avg, 3),
                "median_coverage": round(med, 3),
                "weighted_risk": round(weighted, 6),
            },
            "breaches": breaches_payload,
        }


def _normalise_tags(raw: Any) -> Sequence[str]:
    if raw is None:
        return ()
    if isinstance(raw, (str, bytes)):
        return (str(raw),)
    if isinstance(raw, Iterable):
        return tuple(str(item) for item in raw)
    return (str(raw),)


def _coerce_module(entry: MutableMapping[str, Any]) -> ModuleRecord:
    if "module" not in entry:
        raise ValidationIssue("Missing required field 'module'")

    module_name = str(entry["module"]).strip()
    if not module_name:
        raise ValidationIssue("Module name cannot be empty")

    try:
        loc = int(entry.get("loc"))
    except (TypeError, ValueError) as exc:
        raise ValidationIssue("Non-numeric loc") from exc

    try:
        complexity = int(entry.get("complexity"))
    except (TypeError, ValueError) as exc:
        raise ValidationIssue("Non-numeric complexity") from exc

    try:
        coverage = float(entry.get("coverage"))
    except (TypeError, ValueError) as exc:
        raise ValidationIssue("Non-numeric coverage") from exc

    if not 0 <= coverage <= 100:
        raise ValidationIssue("Coverage must be between 0 and 100")

    return ModuleRecord(
        module=module_name,
        loc=loc,
        complexity=complexity,
        coverage=coverage,
        last_updated=entry.get("last_updated"),
        tags=_normalise_tags(entry.get("tags")),
    )


def process_module_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Refactored entrypoint returning structured summary and diagnostics."""

    if not isinstance(payload, MutableMapping):
        raise TypeError("payload must be a mapping")

    modules = payload.get("modules", [])
    if not isinstance(modules, list):
        raise TypeError("modules must be provided as a list")

    thresholds = QualityThresholds.from_mapping(payload.get("quality_thresholds"))

    state = AggregationState(thresholds=thresholds)
    diagnostics_errors: List[Dict[str, Any]] = []

    for idx, entry in enumerate(modules):
        if not isinstance(entry, MutableMapping):
            diagnostics_errors.append(
                {
                    "module": f"index:{idx}",
                    "issue": "Entry is not a mapping",
                }
            )
            continue
        try:
            record = _coerce_module(entry)
        except ValidationIssue as exc:
            diagnostics_errors.append(
                {
                    "module": entry.get("module", f"index:{idx}"),
                    "issue": str(exc),
                }
            )
            continue
        state.record(record)

    result = state.finalise()
    result["diagnostics"] = {
        "invalid_records": len(diagnostics_errors),
        "errors": diagnostics_errors,
    }
    return result


__all__ = ["process_module_metrics", "QualityThresholds", "ModuleRecord"]
