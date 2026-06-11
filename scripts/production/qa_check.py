#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified QA gate for paper-notes output directories."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run_json(cmd: list[str]) -> tuple[int, dict | None, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    data = None
    if proc.stdout.strip():
        start = proc.stdout.find("{")
        if start >= 0:
            try:
                data = json.loads(proc.stdout[start:])
            except json.JSONDecodeError:
                data = None
    return proc.returncode, data, proc.stdout, proc.stderr


def run_preflight(out_dir: Path, mode: str) -> tuple[int, dict | None, str, str]:
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "preflight_check.py"),
        "--out-dir",
        str(out_dir),
        "--mode",
        mode,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    report_path = out_dir / "preflight_report.json"
    report = None
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    return proc.returncode, report, proc.stdout, proc.stderr


def run_validation(out_dir: Path) -> tuple[int, dict | None, str, str]:
    return run_json([
        sys.executable,
        str(SCRIPT_DIR / "validate_output.py"),
        "--out-dir",
        str(out_dir),
        "--json",
        "--write-report",
    ])


def build_qa_report(out_dir: Path, mode: str, preflight: dict | None, validation: dict | None) -> dict:
    preflight_blocking = int((preflight or {}).get("blocking_count", 999))
    validation_p0 = int((validation or {}).get("p0_count", 999))
    validation_p1 = int((validation or {}).get("p1_count", 0))
    validation_p2 = int((validation or {}).get("p2_count", 0))
    passed = preflight_blocking == 0 and validation_p0 == 0

    return {
        "out_dir": str(out_dir),
        "mode": mode,
        "passed": passed,
        "preflight": {
            "passed": bool((preflight or {}).get("passed", False)),
            "blocking_count": preflight_blocking,
            "warning_count": int((preflight or {}).get("warning_count", 999)),
        },
        "validation": {
            "grade": (validation or {}).get("grade"),
            "p0_count": validation_p0,
            "p1_count": validation_p1,
            "p2_count": validation_p2,
            "failed_checks": int((validation or {}).get("failed_checks", 999)),
        },
        "evidence": {
            "ledger_file_present": (out_dir / "evidence_ledger.json").exists(),
        },
        "issues": {
            "preflight": (preflight or {}).get("issues", []),
            "validation": (validation or {}).get("issues", []),
        },
    }


def write_report(out_dir: Path, report: dict) -> tuple[Path, Path]:
    json_path = out_dir / "qa_report.json"
    md_path = out_dir / "qa_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# QA Report",
        "",
        f"- 结果：`{'PASS' if report['passed'] else 'FAIL'}`",
        f"- preflight blocking：`{report['preflight']['blocking_count']}`",
        f"- preflight warning：`{report['preflight']['warning_count']}`",
        f"- validation P0：`{report['validation']['p0_count']}`",
        f"- validation P1：`{report['validation']['p1_count']}`",
        f"- validation P2：`{report['validation']['p2_count']}`",
        f"- validation grade：`{report['validation']['grade']}`",
        f"- evidence ledger：`{'present' if report['evidence']['ledger_file_present'] else 'missing'}`",
        "",
        "## Blocking Policy",
        "- QA fails when preflight has blocking issues or validation has P0 issues.",
        "- P1/P2 validation issues are written as quality warnings for editorial follow-up.",
        "",
        "## Validation Issues",
    ]
    validation_issues = report["issues"]["validation"]
    if not validation_issues:
        lines.append("- none")
    else:
        for issue in validation_issues:
            lines.append(f"- [{issue['severity']}] {issue['check_id']}: {issue['detail']}")

    lines.extend(["", "## Preflight Issues"])
    preflight_issues = report["issues"]["preflight"]
    if not preflight_issues:
        lines.append("- none")
    else:
        for issue in preflight_issues:
            lines.append(f"- [{issue['severity']}] {issue['code']}: {issue['message']}")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Run paper-notes preflight + validation QA")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mode", choices=("article", "publish"), default="publish")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    if not out_dir.exists():
        print(f"ERROR: directory not found: {out_dir}", file=sys.stderr)
        return 2

    _, preflight, preflight_stdout, preflight_stderr = run_preflight(out_dir, args.mode)
    _, validation, validation_stdout, validation_stderr = run_validation(out_dir)

    if preflight is None:
        print(preflight_stdout, file=sys.stderr)
        print(preflight_stderr, file=sys.stderr)
        print("ERROR: preflight report was not generated", file=sys.stderr)
        return 2
    if validation is None:
        print(validation_stdout, file=sys.stderr)
        print(validation_stderr, file=sys.stderr)
        print("ERROR: validation report was not generated", file=sys.stderr)
        return 2

    report = build_qa_report(out_dir, args.mode, preflight, validation)
    json_path, md_path = write_report(out_dir, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(str(json_path))
        print(str(md_path))
        print("PASS" if report["passed"] else "FAIL")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
