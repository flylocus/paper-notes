#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render note.md and article_editor_ready.html from article payload.

Usage:
  python3 render_article.py \
    --article-payload fused/sage_article_payload_20260415.json \
    --out-dir outputs/20260415/2604.09285
"""

import argparse
import json
import os

STYLE = """<section id=\"nice\">\n<style>\n:root{\n  --primary:#0B1430;\n  --accent:#4CC3FF;\n  --accent-2:#2F6BFF;\n  --bg-soft:#E6F2FF;\n  --text:#1F2A37;\n  --muted:#6B7280;\n}\n\n#nice, #write{\n  color:var(--text);\n  font-size:16px;\n  line-height:1.8;\n}\n\n#nice h1, #write h1{\n  color:var(--primary);\n  font-size:22px;\n  font-weight:800;\n  border-left:5px solid var(--accent);\n  padding-left:12px;\n  margin:22px 0 14px;\n}\n\n#nice h2, #write h2{\n  color:var(--primary);\n  font-size:18px;\n  font-weight:700;\n  margin:18px 0 10px;\n}\n\n#nice h3, #write h3{\n  color:var(--accent-2);\n  font-size:16px;\n  font-weight:700;\n  margin:14px 0 8px;\n}\n\n#nice hr, #write hr{\n  border:0;\n  border-top:1px solid #D9E6FF;\n  margin:18px 0;\n}\n\n#nice blockquote, #write blockquote{\n  margin:14px 0;\n  padding:10px 14px;\n  background:#F6FAFF;\n  border-left:4px solid var(--accent);\n  color:#0F172A;\n}\n\n#nice strong, #write strong{\n  color:var(--primary);\n}\n\n#nice ul, #nice ol, #write ul, #write ol{\n  padding-left:22px;\n}\n\n#nice li, #write li{\n  margin:6px 0;\n}\n</style>\n"""


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def render_note_md(d):
    lines = []
    lines.append(f"# 【论文速记】{d['info']['title_cn']}\n")
    lines.append(f"> 原文标题：**{d['info']['title']}**  ")
    lines.append(f"> arXiv：{d['info']['link']}  ")
    lines.append(f"> 总评分：**{d['score']['total']:.1f} / 10**\n")
    lines.append("## 评分")
    for x in d['score']['dimensions']:
        lines.append(f"- {x['label']}：**{x['value']:.1f} / 2.0**")
    lines.append(f"\n## A. 研究问题\n{d['A_research_problem']}\n")
    lines.append("## B. 核心贡献")
    for i, item in enumerate(d['B_core_contributions'], 1):
        lines.append(f"{i}. {item}")
    lines.append(f"\n## C. 方法 / 框架\n{d['C_method_framework']}\n")
    lines.append("## D. 关键结果")
    for item in d['D_key_results']:
        lines.append(f"- {item}")
    lines.append("\n## E. 产业启示")
    for item in d['E_industry_implications']:
        lines.append(f"- {item}")
    lines.append(f"\n## F. 一句话判断\n{d['F_one_line_judgement']}\n")
    return "\n".join(lines)


def render_editor_html(d, title=None, conclusion=None):
    title = title or f"【论文速记】{d['info']['title_cn']}"
    conclusion = conclusion or d['F_one_line_judgement']
    html = [STYLE]
    html.append(f"<h1>{title}</h1>")
    html.append(f"\n<blockquote><p><strong>一句话结论：</strong>{conclusion}</p></blockquote>\n")
    html.append('<p><img src="score_card.png" alt="评分卡" /></p>')
    html.append('<p><img src="info_card.png" alt="信息卡" /></p>')
    html.append(f"\n<h2>A. 研究问题</h2>\n<p>{d['A_research_problem']}</p>")
    html.append("\n<h2>B. 核心贡献</h2>\n<ul>")
    for item in d['B_core_contributions']:
        html.append(f"<li>{item}</li>")
    html.append("</ul>")
    html.append(f"\n<h2>C. 方法/框架</h2>\n<p>{d['C_method_framework']}</p>")
    html.append("\n<h2>D. 关键结果</h2>\n<ul>")
    for item in d['D_key_results']:
        html.append(f"<li>{item}</li>")
    html.append("</ul>")
    html.append("\n<h2>E. 产业启示</h2>\n<ul>")
    for item in d['E_industry_implications']:
        html.append(f"<li>{item}</li>")
    html.append("</ul>")
    html.append(f"\n<h2>F. 一句话判断</h2>\n<p><strong>{d['F_one_line_judgement']}</strong></p>")
    html.append("\n</section>\n")
    return "\n".join(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--article-payload', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--html-title', default='')
    ap.add_argument('--html-conclusion', default='')
    args = ap.parse_args()

    d = load_json(args.article_payload)
    os.makedirs(args.out_dir, exist_ok=True)

    note_md = render_note_md(d)
    editor_html = render_editor_html(d, args.html_title or None, args.html_conclusion or None)

    note_path = os.path.join(args.out_dir, 'note.md')
    html_path = os.path.join(args.out_dir, 'article_editor_ready.html')

    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(note_md)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(editor_html)

    print(note_path)
    print(html_path)


if __name__ == '__main__':
    main()
