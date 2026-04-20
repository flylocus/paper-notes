#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preflight checker for paper-notes final output directories."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


REQUIRED_BY_MODE = {
    "article": [
        "cover_235.png",
        "info_card.png",
        "score_card.png",
        "article_editor_ready.html",
    ],
    "publish": [
        "cover_235.png",
        "info_card.png",
        "score_card.png",
        "article_editor_ready.html",
        "note.md",
        "publish_pack.md",
    ],
}


BLOCKING_PATTERNS = [
    "待补充",
    "TBD",
    "Not specified",
    "Unknown Institution",
    "Unknown (Wait for ArXiv matching)",
    "Community Verified",
    "Simulated",
    "placeholder",
    "manual enrichment",
]


WARNING_PATTERNS = [
    "默认标题",
    "前沿研究论文速记",
    "Unknown",
]


TEXT_FILES_ALWAYS_SCAN = [
    "note.md",
    "article_editor_ready.html",
    "publish_pack.md",
]


DATA_FILE_PRIORITY = [
    "generate_data.json",
    "data.json",
    "card_data.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_issue(issues: list[dict], severity: str, code: str, message: str, path: str | None = None) -> None:
    issues.append(
        {
            "severity": severity,
            "code": code,
            "message": message,
            "path": path,
        }
    )


def scan_placeholders(out_dir: Path, issues: list[dict]) -> None:
    scan_targets: list[str] = list(TEXT_FILES_ALWAYS_SCAN)
    for name in DATA_FILE_PRIORITY:
        if (out_dir / name).exists():
            scan_targets.append(name)
            break

    for name in scan_targets:
        path = out_dir / name
        if not path.exists():
            continue
        text = read_text(path)
        lower_text = text.lower()
        for pattern in BLOCKING_PATTERNS:
            if pattern.lower() in lower_text:
                add_issue(
                    issues,
                    "blocking",
                    "placeholder_blocking",
                    f"found blocking placeholder pattern: {pattern}",
                    str(path),
                )
        for pattern in WARNING_PATTERNS:
            if pattern.lower() in lower_text:
                add_issue(
                    issues,
                    "warning",
                    "placeholder_warning",
                    f"found warning placeholder pattern: {pattern}",
                    str(path),
                )


def check_required_files(out_dir: Path, mode: str, issues: list[dict]) -> None:
    for name in REQUIRED_BY_MODE[mode]:
        path = out_dir / name
        if not path.exists():
            add_issue(
                issues,
                "blocking",
                "missing_required_file",
                f"missing required file for {mode}: {name}",
                str(path),
            )


def check_article_consistency(out_dir: Path, issues: list[dict]) -> None:
    article_path = out_dir / "article_editor_ready.html"
    if not article_path.exists():
        return

    text = read_text(article_path)
    for image_name in ("score_card.png", "info_card.png"):
        if image_name not in text:
            add_issue(
                issues,
                "blocking",
                "article_missing_image_reference",
                f"article_editor_ready.html does not reference {image_name}",
                str(article_path),
            )


def check_metadata_presence(out_dir: Path, issues: list[dict]) -> None:
    if not any((out_dir / name).exists() for name in DATA_FILE_PRIORITY):
        add_issue(
            issues,
            "warning",
            "metadata_not_found",
            "no data.json / generate_data.json / card_data.json found in output dir",
            str(out_dir),
        )


def build_report(out_dir: Path, mode: str, issues: list[dict]) -> dict:
    blocking = [x for x in issues if x["severity"] == "blocking"]
    warnings = [x for x in issues if x["severity"] == "warning"]
    return {
        "out_dir": str(out_dir),
        "mode": mode,
        "passed": len(blocking) == 0,
        "blocking_count": len(blocking),
        "warning_count": len(warnings),
        "issues": issues,
    }


def write_report_files(out_dir: Path, report: dict) -> tuple[Path, Path]:
    json_path = out_dir / "preflight_report.json"
    md_path = out_dir / "preflight_report.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Preflight Report",
        "",
        f"- 模式：`{report['mode']}`",
        f"- 结果：`{'PASS' if report['passed'] else 'FAIL'}`",
        f"- blocking：`{report['blocking_count']}`",
        f"- warning：`{report['warning_count']}`",
        "",
        "## Issues",
    ]
    if not report["issues"]:
        lines.append("- none")
    else:
        for issue in report["issues"]:
            path = f" ({issue['path']})" if issue.get("path") else ""
            lines.append(f"- [{issue['severity']}] {issue['code']}: {issue['message']}{path}")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def run_preflight(out_dir: Path, mode: str) -> dict:
    issues: list[dict] = []
    check_required_files(out_dir, mode, issues)
    check_article_consistency(out_dir, issues)
    check_metadata_presence(out_dir, issues)
    scan_placeholders(out_dir, issues)
    return build_report(out_dir, mode, issues)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mode", choices=("article", "publish"), default="publish")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    report = run_preflight(out_dir, args.mode)
    json_path, md_path = write_report_files(out_dir, report)
    print(str(json_path))
    print(str(md_path))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
