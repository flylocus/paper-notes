#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a monthly theme index from outputs/ready/ article payloads.

Scans outputs/ready/<YYYYMMDD>/<paper_id>/generate_data.json for the given
month, tags each article against a fixed theme taxonomy, and writes
outputs/THEME_INDEX_<YYYYMM>.md for monthly review.

Usage:
  python3 scripts/maintenance/build_theme_index.py --month 202606
  python3 scripts/maintenance/build_theme_index.py --month 202606 --stdout
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READY = ROOT / "outputs" / "ready"

# 主题分类:按命中关键词打标签,一篇可属多主题;全不命中归"其他"。
THEME_TAXONOMY = [
    ("Agent 评测与基准", ["评测", "benchmark", "基准", "评估", "eval"]),
    ("多智能体与委派", ["多 agent", "多智能体", "委派", "委托", "协作", "swarm", "delegation"]),
    ("治理·安全·审计", ["治理", "安全", "审计", "权限", "合规", "风险", "governance"]),
    ("Deep Research", ["deep research", "深度研究", "检索", "搜索", "research agent"]),
    ("训练与对齐", ["训练", "微调", "强化学习", "rl", "对齐", "reward"]),
    ("记忆与上下文", ["记忆", "memory", "上下文", "context", "rag"]),
    ("工具使用与执行", ["工具调用", "tool use", "执行", "工作流", "workflow", "skill"]),
]


def article_text_for_tagging(data: dict) -> str:
    parts = [
        str(data.get("info", {}).get("title", "")),
        str(data.get("info", {}).get("title_cn", "")),
        str(data.get("A_research_problem", "")),
        str(data.get("F_one_line_judgement", "")),
    ]
    for x in data.get("B_core_contributions", []) or []:
        parts.append(str(x))
    return " ".join(parts).lower()


def tag_themes(text: str) -> list[str]:
    themes = []
    for name, keywords in THEME_TAXONOMY:
        if any(k.lower() in text for k in keywords):
            themes.append(name)
    return themes or ["其他"]


def collect_month(month: str) -> list[dict]:
    entries = []
    for day_dir in sorted(READY.glob(f"{month}??")):
        for paper_dir in sorted(day_dir.iterdir()):
            payload = paper_dir / "generate_data.json"
            if not payload.exists():
                continue
            try:
                data = json.loads(payload.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            info = data.get("info", {})
            score = data.get("score", {})
            try:
                total = float(score.get("total"))
            except (TypeError, ValueError):
                total = None
            entries.append({
                "date": day_dir.name,
                "paper_id": paper_dir.name,
                "title_cn": info.get("title_cn") or info.get("title", ""),
                "title": info.get("title", ""),
                "link": info.get("link", ""),
                "score": total,
                "one_line": str(data.get("F_one_line_judgement", "")).strip(),
                "themes": tag_themes(article_text_for_tagging(data)),
                "rel_path": f"ready/{day_dir.name}/{paper_dir.name}",
            })
    return entries


def render_index(month: str, entries: list[dict]) -> str:
    lines = [f"# 论文速记主题索引 {month[:4]}-{month[4:]}", ""]
    lines.append(f"- 收录:{len(entries)} 篇(来源 `outputs/ready/`,按 `generate_data.json` 自动生成)")
    scored = [e["score"] for e in entries if e["score"] is not None]
    if scored:
        lines.append(f"- 评分:均值 {sum(scored)/len(scored):.2f},最高 {max(scored):.1f},最低 {min(scored):.1f}")
    lines.append("")

    theme_map: dict[str, list[dict]] = {}
    for e in entries:
        for t in e["themes"]:
            theme_map.setdefault(t, []).append(e)

    lines.append("## 主题分布")
    lines.append("")
    for t, es in sorted(theme_map.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"- **{t}**:{len(es)} 篇")
    lines.append("")

    for t, es in sorted(theme_map.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"## {t}")
        lines.append("")
        for e in sorted(es, key=lambda x: x["date"]):
            score = f"{e['score']:.1f}" if e["score"] is not None else "—"
            lines.append(f"### {e['date']} · [{e['title_cn']}]({e['rel_path']}) · {score}/10")
            if e["one_line"]:
                one = re.sub(r"\s+", " ", e["one_line"])
                lines.append(f"> {one}")
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True, help="YYYYMM, e.g. 202606")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing file")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{6}", args.month):
        ap.error("--month must be YYYYMM")

    entries = collect_month(args.month)
    if not entries:
        print(f"No payloads found under outputs/ready/{args.month}??/")
        return 1
    content = render_index(args.month, entries)
    if args.stdout:
        print(content)
        return 0
    out_path = ROOT / "outputs" / f"THEME_INDEX_{args.month}.md"
    out_path.write_text(content, encoding="utf-8")
    print(out_path)
    print(f"{len(entries)} articles indexed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
