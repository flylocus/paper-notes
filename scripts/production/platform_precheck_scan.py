#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Advisory platform content scan via yuwen-publish-precheck scan.py.

Runs lexical pre-check on note.md (or --text-file). Does not block QA;
semantic review still requires agent pass per yuwen SKILL.md + 双号备忘录.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_NOTES_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_SKILL_ROOTS = [
    Path(os.environ.get("YUWEN_PRECHECK_ROOT", "")),
    PAPER_NOTES_ROOT.parent / "wechat-reports/tools/yuwen-publish-precheck",
    Path.home() / ".cursor/skills/yuwen-publish-precheck",
]


def resolve_skill_root() -> Path | None:
    for root in DEFAULT_SKILL_ROOTS:
        if not root or not str(root).strip():
            continue
        scan = root / "scripts" / "scan.py"
        if scan.is_file():
            return root
    return None


def pick_text_file(out_dir: Path, explicit: Path | None) -> Path:
    if explicit:
        p = explicit.expanduser().resolve()
        if not p.is_file():
            raise SystemExit(f"text file not found: {p}")
        return p
    for name in ("note.md", "article_editor_ready.html"):
        candidate = out_dir / name
        if candidate.is_file():
            return candidate
    raise SystemExit(f"no note.md or article in {out_dir}; pass --text-file")


def run_scan(skill_root: Path, text_file: Path, commercial: bool, industry: str) -> dict:
    cmd = [
        sys.executable,
        str(skill_root / "scripts" / "scan.py"),
        "--file",
        str(text_file),
        "--json",
    ]
    if commercial:
        cmd.append("--commercial")
    if industry:
        cmd.extend(["--industry", industry])

    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)

    start = proc.stdout.find("{")
    if start < 0:
        raise SystemExit("scan.py did not return JSON")
    return json.loads(proc.stdout[start:])


def write_reports(out_dir: Path, payload: dict, skill_root: Path, text_file: Path) -> tuple[Path, Path]:
    json_path = out_dir / "platform_precheck_scan.json"
    md_path = out_dir / "platform_precheck_scan.md"

    candidates = payload.get("candidates", [])
    personal_hits = payload.get("personal_hits", [])
    myth_advisories = payload.get("myth_advisories", [])
    char_count = payload.get("characters", "?")
    commercial = payload.get("commercial", False)

    json_path.write_text(
        json.dumps(
            {
                "tool": "yuwen-publish-precheck",
                "skill_root": str(skill_root),
                "text_file": str(text_file),
                "platform_scope": "通用层(G01-G14)+广告法；目标平台为抖音/小红书/视频号规则包，公众号图文需人工语义复核",
                "characters": char_count,
                "commercial": commercial,
                "industries": payload.get("industries", []),
                "candidate_count": len(candidates),
                "personal_hits_count": len(personal_hits),
                "myth_advisories_count": len(myth_advisories),
                "candidates": candidates,
                "personal_hits": personal_hits,
                "myth_advisories": myth_advisories,
                "advisory_only": True,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# Platform Precheck Scan (advisory)",
        "",
        f"- Skill：`yuwen-publish-precheck` @ `{skill_root}`",
        f"- 扫描文件：`{text_file.name}`",
        f"- 字数：{char_count}｜商业属性：{'有' if commercial else '无/未声明'}",
        f"- 风险候选：**{len(candidates)}**｜个人规则：**{len(personal_hits)}**｜辟谣提示：**{len(myth_advisories)}**",
        "",
        "> 词面命中只是复核线索，不是违规结论。零命中仍需语义判定（见 skill `references/judgment.md`）+ `/Users/shenfei/公众号双号内容发布前备忘录.md`。",
        "> 本工具 V1.0 未覆盖微信公众号图文专用规则包；与现有 preflight/validate/双号 memo 互补，不替代。",
        "",
    ]

    if not candidates and not personal_hits and not myth_advisories:
        lines.extend(["## 结果", "", "未发现词面候选。"])
    else:
        if candidates:
            lines.extend(["## 风险候选", ""])
            for i, item in enumerate(candidates, 1):
                lines.append(
                    f"{i}. `{item.get('match', '?')}` L{item.get('line', '?')} "
                    f"→ {item.get('rule', '?')} ({item.get('severity', '?')})"
                )
            lines.append("")
        if personal_hits:
            lines.extend(["## 个人规则命中", ""])
            for item in personal_hits:
                lines.append(
                    f"- `{item.get('match', '?')}` L{item.get('line', '?')} → {item.get('reason', '')}"
                )
            lines.append("")
        if myth_advisories:
            lines.extend(["## 辟谣提示", ""])
            for item in myth_advisories:
                lines.append(f"- L{item.get('line', '?')} `{item.get('match', '?')}`：{item.get('note', '')}")
            lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Run yuwen-publish-precheck lexical scan (advisory)")
    ap.add_argument("--out-dir", required=True, help="paper-notes ready output directory")
    ap.add_argument("--text-file", type=Path, default=None, help="override text source (default note.md)")
    ap.add_argument("--commercial", action="store_true", help="content has commercial intent")
    ap.add_argument("--industry", default="", help="medical,finance comma-separated")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    if not out_dir.is_dir():
        print(f"ERROR: directory not found: {out_dir}", file=sys.stderr)
        return 2

    skill_root = resolve_skill_root()
    if skill_root is None:
        print(
            "ERROR: yuwen-publish-precheck not found. "
            "Clone to wechat-reports/tools/yuwen-publish-precheck or set YUWEN_PRECHECK_ROOT.",
            file=sys.stderr,
        )
        return 2

    text_file = pick_text_file(out_dir, args.text_file)
    payload = run_scan(skill_root, text_file, args.commercial, args.industry)
    json_path, md_path = write_reports(out_dir, payload, skill_root, text_file)

    if args.json:
        print(json_path.read_text(encoding="utf-8"))
    else:
        print(str(json_path))
        print(str(md_path))
        n = len(payload.get("candidates", [])) + len(payload.get("personal_hits", []))
        print(f"SCAN_OK candidates={n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
