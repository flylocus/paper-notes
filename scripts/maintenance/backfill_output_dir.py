#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backfill legacy paper-notes output directories to the current baseline."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
PRODUCTION_SCRIPTS = ROOT / "scripts" / "production"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def choose_data_file(out_dir: Path) -> Path | None:
    for name in ("generate_data.json", "data.json", "card_data.json"):
        path = out_dir / name
        if path.exists():
            return path
    return None


def html_to_note_md(article_html: str) -> str:
    text = article_html
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    text = re.sub(r"</?(section|div)[^>]*>", "", text)
    text = re.sub(r"<h1>(.*?)</h1>", r"# \1\n", text, flags=re.S)
    text = re.sub(r"<h2>(.*?)</h2>", r"\n## \1\n", text, flags=re.S)
    text = re.sub(r"<h3>(.*?)</h3>", r"\n### \1\n", text, flags=re.S)
    text = re.sub(r"<blockquote><p><strong>一句话结论：</strong>(.*?)</p></blockquote>", r"> 一句话结论：**\1**\n", text, flags=re.S)
    text = re.sub(r'<p><img src="([^"]+)" alt="([^"]*)" ?/?></p>', r'![\2](\1)\n', text)
    text = re.sub(r"<ul>\s*", "", text)
    text = re.sub(r"\s*</ul>", "\n", text)
    text = re.sub(r"<li>(.*?)</li>", r"- \1\n", text, flags=re.S)
    text = re.sub(r"<p>(.*?)</p>", r"\1\n", text, flags=re.S)
    text = re.sub(r"</?strong>", "**", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def extract_conclusion(article_html: str) -> str:
    match = re.search(r"一句话结论：</strong>(.*?)</p></blockquote>", article_html, flags=re.S)
    if match:
        return html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
    return "这是一篇值得关注的论文。"


def build_publish_copy(data: dict, article_html: str) -> tuple[list[str], str, str]:
    if "info" in data:
        title_cn = data["info"].get("title_cn") or data["info"].get("title") or "论文速记"
        title_en = data["info"].get("title") or title_cn
        score = data.get("score", {}).get("total")
    else:
        paper = data.get("paper", {})
        title_cn = paper.get("title_cn") or paper.get("title") or "论文速记"
        title_en = paper.get("title") or title_cn
        score = data.get("scores", {}).get("total")

    conclusion = extract_conclusion(article_html)
    score_text = f"{score:.1f}/10" if isinstance(score, (int, float)) else "已完成评分"

    titles = [
        f"【论文速记】{title_cn}",
        f"{title_cn}：为什么它值得做成 Agent 能力框架参考",
        f"{title_cn} | Paper Notes",
    ]
    intro = conclusion
    summary = (
        f"这篇论文《{title_en}》已完成速记整理，当前评分 {score_text}。"
        f" 重点不在单点技巧，而在于它把记忆、技能、规则放进同一套 Agent 能力组织框架。"
    )
    return titles, intro, summary


def write_note(out_dir: Path) -> Path | None:
    article_path = out_dir / "article_editor_ready.html"
    note_path = out_dir / "note.md"
    if note_path.exists() or not article_path.exists():
        return note_path if note_path.exists() else None
    note_md = html_to_note_md(article_path.read_text(encoding="utf-8"))
    note_path.write_text(note_md, encoding="utf-8")
    return note_path


def write_publish_pack(out_dir: Path) -> Path | None:
    pack_path = out_dir / "publish_pack.md"
    article_path = out_dir / "article_editor_ready.html"
    data_path = choose_data_file(out_dir)
    if pack_path.exists() or not article_path.exists() or data_path is None:
        return pack_path if pack_path.exists() else None

    data = load_json(data_path)
    titles, intro, summary = build_publish_copy(data, article_path.read_text(encoding="utf-8"))
    cmd = [
        sys.executable,
        str(PRODUCTION_SCRIPTS / "build_publish_pack.py"),
        "--out",
        str(pack_path),
        "--intro",
        intro,
        "--summary",
        summary,
    ]
    for title in titles:
        cmd.extend(["--title", title])
    subprocess.run(cmd, check=True)
    return pack_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--run-preflight", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    note_path = write_note(out_dir)
    pack_path = write_publish_pack(out_dir)

    if note_path:
        print(str(note_path))
    if pack_path:
        print(str(pack_path))

    if args.run_preflight:
        subprocess.run(
            [
                sys.executable,
                str(PRODUCTION_SCRIPTS / "preflight_check.py"),
                "--out-dir",
                str(out_dir),
                "--mode",
                "publish",
            ],
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
