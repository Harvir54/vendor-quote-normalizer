"""Measure deterministic extraction accuracy against curated expectations."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, TypedDict

from app.normalizer import normalize_estimate_text


class Score(TypedDict):
    passed: int
    total: int
    accuracy: float


class Failure(TypedDict):
    case_id: str
    trade: str
    field: str
    expected: Any
    actual: Any


class EvaluationReport(TypedDict):
    cases: int
    overall: Score
    by_trade: dict[str, Score]
    by_field: dict[str, Score]
    failures: list[Failure]


def _score(passed: int, total: int) -> Score:
    return {
        "passed": passed,
        "total": total,
        "accuracy": round(passed / total * 100, 2) if total else 0.0,
    }


def evaluate_cases(cases_dir: Path) -> EvaluationReport:
    """Evaluate every expected leaf value in the JSON case files."""
    paths = sorted(cases_dir.glob("*-cases.json"))
    cases = [case for path in paths for case in json.loads(path.read_text())]
    trade_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    field_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    failures: list[Failure] = []
    passed = 0
    total = 0

    for case in cases:
        actual = normalize_estimate_text(case["text"], trade=case["trade"])
        for field, expected in case["expected"].items():
            checks = expected.items() if isinstance(expected, dict) else (("value", expected),)
            for attribute, expected_value in checks:
                field_name = field if attribute == "value" else f"{field}.{attribute}"
                actual_value = actual[field] if attribute == "value" else actual[field][attribute]
                matched = actual_value == expected_value
                total += 1
                trade_counts[case["trade"]][1] += 1
                field_counts[field_name][1] += 1
                if matched:
                    passed += 1
                    trade_counts[case["trade"]][0] += 1
                    field_counts[field_name][0] += 1
                else:
                    failures.append({
                        "case_id": case["id"],
                        "trade": case["trade"],
                        "field": field_name,
                        "expected": expected_value,
                        "actual": actual_value,
                    })

    return {
        "cases": len(cases),
        "overall": _score(passed, total),
        "by_trade": {
            trade: _score(*counts) for trade, counts in sorted(trade_counts.items())
        },
        "by_field": {
            field: _score(*counts) for field, counts in sorted(field_counts.items())
        },
        "failures": failures,
    }
