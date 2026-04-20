#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch standardize paper-notes output directories."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
MAINTENANCE_SCRIPTS = ROOT / "scripts" / "maintenance"
PRODUCTION_SCRIPTS = ROOT / "scripts" / "production"
OUTPUTS = ROOT / "outputs"
RELEVANT_FILES = {
    "ARCHIVE_ONLY.md",
    "cover_235.png",
    "info_card.png",
    "score_card.png",
    "article_editor_ready.html",
    "note.md",
    "publish_pack.md",
    "data.json",
    "generate_data.json",
    "card_data.json",
}


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    completed = subprocess.run(cmd, capture_output=True, text=True)
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def has_relevant_files(path: Path) -> bool:
    return any((path / name).exists() for name in RELEVANT_FILES)


def find_candidate_dirs(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_dir():
            continue
        if path.is_symlink():
            continue
        if path.name.startswith("_"):
            continue
        if has_relevant_files(path):
            candidates.append(path)
    return candidates


def classify_before_backfill(path: Path) -> dict:
    files = {p.name for p in path.iterdir() if p.is_file()}
    return {
        "is_archive_only": "ARCHIVE_ONLY.md" in files,
        "has_article_html": "article_editor_ready.html" in files,
        "has_note": "note.md" in files,
        "has_publish_pack": "publish_pack.md" in files,
        "has_images": all(name in files for name in ("cover_235.png", "info_card.png", "score_card.png")),
    }


def read_preflight(path: Path) -> dict | None:
    report = path / "preflight_report.json"
    if not report.exists():
        return None
    try:
        return json.loads(report.read_text(encoding="utf-8"))
    except Exception:
        return None


def standardize_dir(path: Path) -> dict:
    before = classify_before_backfill(path)
    actions: list[str] = []
    notes: list[str] = []

    if before["is_archive_only"]:
        return {
            "dir": str(path),
            "status": "archive_only",
            "actions": actions,
            "notes": ["directory explicitly marked archive-only"],
            "before": before,
            "after": before,
            "preflight_mode": None,
            "preflight_report": None,
        }

    if before["has_article_html"] and (not before["has_note"] or not before["has_publish_pack"]):
        rc, output = run_cmd(
            [
                sys.executable,
                str(MAINTENANCE_SCRIPTS / "backfill_output_dir.py"),
                "--out-dir",
                str(path),
            ]
        )
        actions.append("backfill")
        if rc != 0:
            notes.append(f"backfill_failed: {output}")

    after = classify_before_backfill(path)

    preflight_mode = None
    preflight_passed = False
    preflight_report = None
    if after["has_article_html"] and after["has_note"] and after["has_publish_pack"]:
        preflight_mode = "publish"
    elif after["has_article_html"]:
        preflight_mode = "article"

    if preflight_mode:
        rc, output = run_cmd(
            [
                sys.executable,
                str(PRODUCTION_SCRIPTS / "preflight_check.py"),
                "--out-dir",
                str(path),
                "--mode",
                preflight_mode,
            ]
        )
        actions.append(f"preflight:{preflight_mode}")
        preflight_report = read_preflight(path)
        preflight_passed = rc == 0 and bool(preflight_report and preflight_report.get("passed"))
        if preflight_report and not preflight_report.get("passed"):
            for issue in (preflight_report.get("issues") or [])[:3]:
                notes.append(f"{issue.get('code')}: {issue.get('message')}")
        elif rc != 0 and output:
            notes.append(output.splitlines()[-1] if output.splitlines() else output)

    if preflight_mode == "publish" and preflight_passed:
        status = "publish_ready"
    elif preflight_mode == "article" and preflight_passed:
        status = "article_ready_only"
    elif not after["has_article_html"]:
        status = "blocked_missing_article_html"
    elif not after["has_images"]:
        status = "blocked_missing_images"
    else:
        status = "blocked_other"

    return {
        "dir": str(path),
        "status": status,
        "actions": actions,
        "notes": notes,
        "before": before,
        "after": after,
        "preflight_mode": preflight_mode,
        "preflight_report": preflight_report,
    }


def build_summary(results: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for item in results:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    return {
        "root": str(OUTPUTS),
        "total_dirs": len(results),
        "counts": counts,
        "results": results,
    }


def write_reports(summary: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "paper_notes_output_standardization.json"
    md_path = out_dir / "paper_notes_output_standardization.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Paper Notes Output Standardization",
        "",
        f"- root: `{summary['root']}`",
        f"- total_dirs: `{summary['total_dirs']}`",
        "",
        "## Counts",
    ]
    for status, count in sorted(summary["counts"].items()):
        lines.append(f"- `{status}`: {count}")
    lines.append("")
    lines.append("## Directories")
    for item in summary["results"]:
        actions = ", ".join(item["actions"]) if item["actions"] else "none"
        lines.append(f"- `{item['status']}` {item['dir']}")
        lines.append(f"  actions: {actions}")
        if item["notes"]:
            for note in item["notes"]:
                lines.append(f"  note: {note}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def write_ready_index(summary: dict, outputs_root: Path) -> Path:
    ready_items = [item for item in summary["results"] if item["status"] == "publish_ready"]
    archive_items = [item for item in summary["results"] if item["status"] == "archive_only"]
    path = outputs_root / "READY_INDEX.md"

    lines = [
        "# Paper Notes Ready Index",
        "",
        "当前正式可直接参考/复用的发布目录如下。",
        "",
        f"- publish_ready: `{len(ready_items)}`",
        f"- archive_only: `{len(archive_items)}`",
        "",
        "## Publish-Ready",
    ]

    if not ready_items:
        lines.append("- none")
    else:
        for item in ready_items:
            dir_path = Path(item["dir"])
            rel_dir = dir_path.relative_to(outputs_root)
            preflight = item.get("preflight_report") or {}
            warnings = preflight.get("warning_count", 0)
            lines.append(f"- `{rel_dir}`")
            lines.append(f"  preflight: PASS, warnings={warnings}")
            lines.append("  files: `cover_235.png`, `info_card.png`, `score_card.png`, `article_editor_ready.html`, `note.md`, `publish_pack.md`")

    lines.extend(
        [
            "",
            "## Notes",
            "- 全量状态见 `_reports/paper_notes_output_standardization.md`",
            "- 物理目录现按 `outputs/ready/` 与 `outputs/archive/` 分层；旧路径若仍存在，多为兼容 symlink",
            "- 被标记为 `archive_only` 的目录仅作历史参考，不再默认升格为正式发布资产",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-root", default=str(OUTPUTS))
    ap.add_argument("--report-dir", default=str(OUTPUTS / "_reports"))
    args = ap.parse_args()

    outputs_root = Path(args.outputs_root).expanduser().resolve()
    candidates = find_candidate_dirs(outputs_root)
    results = [standardize_dir(path) for path in candidates]
    summary = build_summary(results)
    report_dir = Path(args.report_dir).expanduser().resolve()
    json_path, md_path = write_reports(summary, report_dir)
    ready_index_path = write_ready_index(summary, outputs_root)
    print(str(json_path))
    print(str(md_path))
    print(str(ready_index_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
