"""Print the curated extraction-accuracy report."""

import argparse
import json
from pathlib import Path

from app.evaluation import EvaluationReport, evaluate_cases


ROOT = Path(__file__).resolve().parents[1]


def _score_line(label: str, score: dict[str, int | float]) -> str:
    return (
        f"{label:<12} {score['accuracy']:>6.2f}%  "
        f"({score['passed']}/{score['total']} checks)"
    )


def format_report(report: EvaluationReport) -> str:
    lines = [
        "Vendor Quote Normalizer accuracy evaluation",
        f"Cases: {report['cases']}",
        _score_line("Overall", report["overall"]),
        "",
        "By trade",
    ]
    lines.extend(
        _score_line("HVAC" if trade == "hvac" else trade.title(), score)
        for trade, score in report["by_trade"].items()
    )
    perfect_fields = sum(
        score["passed"] == score["total"] for score in report["by_field"].values()
    )
    lines.extend((
        "",
        f"Field metrics: {perfect_fields}/{len(report['by_field'])} passing",
        "Failures",
    ))
    if not report["failures"]:
        lines.append("None")
    else:
        lines.extend(
            f"{failure['case_id']} · {failure['field']}: expected "
            f"{failure['expected']!r}, got {failure['actual']!r}"
            for failure in report["failures"]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases-dir",
        type=Path,
        default=ROOT / "sample-data" / "evaluation",
        help="Directory containing *-cases.json files",
    )
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()
    report = evaluate_cases(args.cases_dir)
    print(json.dumps(report, indent=2) if args.json else format_report(report), end="")
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
