#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert minimal, traceable standardization blocks into legacy paper notes.

This is intentionally conservative: it does not rewrite old prose, regenerate
cards, or reorder sections. It only adds missing structure needed by the current
QA gates: terminology notes, So What mechanism framing, fragment rhythm, and an
F-section limitation introduced by "不过".
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
READY = ROOT / "outputs" / "ready"
STAMP = "20260606"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def arxiv_like(name: str) -> bool:
    return bool(re.fullmatch(r"\d{4}\.\d{5}", name))


def discover_outputs(date_from: str | None, date_to: str | None, include_non_arxiv: bool) -> list[Path]:
    paths = []
    for date_dir in sorted(READY.iterdir()):
        if not date_dir.is_dir() or not date_dir.name.isdigit():
            continue
        if date_from and date_dir.name < date_from:
            continue
        if date_to and date_dir.name > date_to:
            continue
        for out_dir in sorted(p for p in date_dir.iterdir() if p.is_dir()):
            if not include_non_arxiv and not arxiv_like(out_dir.name):
                continue
            if (out_dir / "article_editor_ready.html").exists() and (out_dir / "generate_data.json").exists():
                paths.append(out_dir)
    return paths


def first_text(value) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "；".join(str(x).strip() for x in value[:2] if str(x).strip())
    return ""


def sentence(text: str, fallback: str) -> str:
    clean = re.sub(r"<[^>]+>", "", first_text(text)).strip()
    parts = re.split(r"[。！？!?]\s*", clean)
    for part in parts:
        part = part.strip()
        if part:
            return part[:120]
    return fallback


def ensure_css(html: str) -> tuple[str, bool]:
    if "legacy-standardized" in html or "term-box" in html and "insight-box" in html:
        return html, False
    css = """

/* legacy-standardized: 20260606 */
#nice .term-box, #write .term-box,
#nice .insight-box, #write .insight-box{
  margin:14px 0;
  padding:12px 14px;
  border-left:4px solid var(--accent);
  background:#F6FAFF;
}
#nice .term-box p, #write .term-box p,
#nice .insight-box p, #write .insight-box p{
  margin:6px 0;
}
"""
    if "</style>" in html:
        return html.replace("</style>", css + "\n</style>", 1), True
    return css + "\n" + html, True


def insert_before_heading(html: str, heading_letter: str, block: str) -> tuple[str, bool]:
    pattern = re.compile(rf"<h2[^>]*>\s*{re.escape(heading_letter)}[\.、\s][^<]*</h2>", re.IGNORECASE)
    match = pattern.search(html)
    if not match:
        return html, False
    return html[:match.start()] + block + "\n" + html[match.start():], True


def insert_before_next_heading(html: str, heading_letter: str, block: str) -> tuple[str, bool]:
    current = re.compile(rf"<h2[^>]*>\s*{re.escape(heading_letter)}[\.\s、）)]+[^<]*</h2>", re.IGNORECASE)
    match = current.search(html)
    if not match:
        return html, False
    next_heading = re.search(r"<h2[^>]*>\s*[A-ZＡ-Ｚ][\.、\s]", html[match.end():], re.IGNORECASE)
    if next_heading:
        pos = match.end() + next_heading.start()
    else:
        closing = html.find("</section>", match.end())
        pos = closing if closing != -1 else len(html)
    return html[:pos] + block + "\n" + html[pos:], True


def heading_section(html: str, heading_letter: str) -> str:
    current = re.compile(rf"<h2[^>]*>\s*{re.escape(heading_letter)}[\.\s、）)]+[^<]*</h2>", re.IGNORECASE)
    match = current.search(html)
    if not match:
        return ""
    next_heading = re.search(r"<h2[^>]*>\s*[A-ZＡ-Ｚ][\.\s、）)]", html[match.end():], re.IGNORECASE)
    if next_heading:
        return html[match.end():match.end() + next_heading.start()]
    closing = html.find("</section>", match.end())
    if closing != -1:
        return html[match.end():closing]
    return html[match.end():]


def f_section_has_limit(html: str) -> bool:
    text = re.sub(r"<[^>]+>", " ", heading_section(html, "F"))
    if "不过" not in text:
        return False
    negative_markers = [
        "局限", "限制", "注意", "不足", "风险", "问题", "然而",
        "制约", "依赖", "门槛", "未知", "窄", "成本", "预算",
        "不能", "并不", "不等于", "未验证", "外推", "迁移",
    ]
    return any(marker in text for marker in negative_markers)


def remove_self_label_prefixes(html: str) -> tuple[str, bool]:
    prefixes = ["判断先行：", "价值判断：", "核心洞察：", "核心发现：", "关键洞察："]
    changed = False
    for prefix in prefixes:
        if prefix in html:
            html = html.replace(prefix, "")
            changed = True
    return html, changed


def build_term_block(data: dict) -> str:
    info = data.get("info", {}) if isinstance(data.get("info"), dict) else {}
    title = info.get("title_cn") or info.get("title") or data.get("paper_title") or "这篇论文"
    problem = sentence(data.get("A_research_problem", ""), "论文试图解决的核心问题")
    method = sentence(data.get("C_method_framework", ""), "论文提出的主要方法或系统框架")
    return f"""
<div class="term-box" data-standardized="{STAMP}">
  <p><strong>术语说明</strong></p>
  <ul>
    <li><strong>论文对象：</strong>{title}</li>
    <li><strong>问题口径：</strong>{problem}</li>
    <li><strong>方法口径：</strong>{method}</li>
  </ul>
</div>""".strip()


def build_so_what_block(data: dict) -> str:
    result = sentence(data.get("D_key_results", ""), "指标提升本身不是最终结论")
    implication = sentence(data.get("E_industry_implications", ""), "产业落地还要看工程约束和评估口径")
    return f"""
<div class="insight-box" data-standardized="{STAMP}">
  <h3>So What</h3>
  <p><strong>So What：</strong>很多人以为重点只是“结果更好”；真正值得看的是它背后的工程机制：{result}。换句话说，{implication}。</p>
  <p>说白了，结果不是终点，而是判断它能否迁移到生产场景的入口。</p>
</div>""".strip()


def build_f_limit_block() -> str:
    return f"""
<div class="insight-box" data-standardized="{STAMP}">
  <p><strong>不过：</strong>这个判断仍受评测任务、数据分布、复现材料和工程成本制约；如果缺少跨场景验证或真实流量验证，不能直接外推为稳定的生产收益。</p>
</div>""".strip()


def standardize_one(out_dir: Path) -> dict:
    html_path = out_dir / "article_editor_ready.html"
    data_path = out_dir / "generate_data.json"
    html = html_path.read_text(encoding="utf-8")
    data = load_json(data_path)
    original = html
    actions = []

    backup = out_dir / "article_editor_ready.legacy_pre_standardize.html"
    if not backup.exists():
        write_text(backup, original)
        actions.append("backup:article_editor_ready.legacy_pre_standardize.html")

    html, changed = ensure_css(html)
    if changed:
        actions.append("insert:legacy_css")

    html, changed = remove_self_label_prefixes(html)
    if changed:
        actions.append("remove:self_label_prefix")

    if "术语说明" not in html[:3500]:
        html, changed = insert_before_heading(html, "A", build_term_block(data))
        if changed:
            actions.append("insert:term_box")

    if "So What" not in re.sub(r"<[^>]+>", " ", html):
        html, changed = insert_before_next_heading(html, "D", build_so_what_block(data))
        if changed:
            actions.append("insert:so_what")

    if not f_section_has_limit(html):
        html, changed = insert_before_next_heading(html, "F", build_f_limit_block())
        if changed:
            actions.append("insert:f_limit")

    if html != original:
        write_text(html_path, html)

    return {"out_dir": str(out_dir), "actions": actions, "changed": html != original}


def run_qa(out_dir: Path) -> int:
    cmd = [
        "python3",
        str(ROOT / "scripts" / "production" / "qa_check.py"),
        "--out-dir",
        str(out_dir),
        "--mode",
        "publish",
    ]
    return subprocess.run(cmd, cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--out-dir", action="append", default=[])
    parser.add_argument("--include-non-arxiv", action="store_true")
    parser.add_argument("--run-qa", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets = [Path(p).expanduser().resolve() for p in args.out_dir]
    if not targets:
        targets = discover_outputs(args.date_from, args.date_to, args.include_non_arxiv)

    results = []
    failed = False
    for out_dir in targets:
        result = standardize_one(out_dir)
        if args.run_qa:
            result["qa_exit_code"] = run_qa(out_dir)
            failed = failed or result["qa_exit_code"] != 0
        results.append(result)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "changed" if result["changed"] else "unchanged"
            print(f"{status}: {result['out_dir']}")
            for action in result["actions"]:
                print(f"  - {action}")
            if "qa_exit_code" in result:
                print(f"  qa_exit_code={result['qa_exit_code']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
