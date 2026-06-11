#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render note.md and article_editor_ready.html from article payload."""

import argparse
import json
import os


STYLE = """<section id="nice">
<style>
:root{
  --primary:#0B1430;
  --accent:#4CC3FF;
  --accent-2:#2F6BFF;
  --bg-soft:#E6F2FF;
  --text:#1F2A37;
  --muted:#6B7280;
}
#nice, #write{color:var(--text);font-size:16px;line-height:1.8;}
#nice h1, #write h1{color:var(--primary);font-size:22px;font-weight:800;border-left:5px solid var(--accent);padding-left:12px;margin:22px 0 14px;}
#nice h2, #write h2{color:var(--primary);font-size:18px;font-weight:700;margin:18px 0 10px;}
#nice h3, #write h3,#nice h3.blue-accent,#write h3.blue-accent{color:var(--accent-2);font-size:16px;font-weight:700;margin:14px 0 8px;}
#nice hr, #write hr{border:0;border-top:1px solid #D9E6FF;margin:18px 0;}
#nice blockquote, #write blockquote{margin:14px 0;padding:10px 14px;background:#F6FAFF;border-left:4px solid var(--accent);color:#0F172A;}
#nice strong, #write strong{color:var(--primary);}
#nice ul, #nice ol, #write ul, #write ol{padding-left:22px;}
#nice li, #write li{margin:6px 0;}
#nice table, #write table{width:100%;border-collapse:collapse;margin:12px 0 10px;font-size:14px;}
#nice th, #nice td, #write th, #write td{border:1px solid #D9E6FF;padding:8px 10px;vertical-align:top;}
#nice th, #write th{background:#EEF6FF;color:var(--primary);font-weight:700;}
#nice .term-box, #write .term-box{margin:12px 0;padding:10px 14px;background:#F6FAFF;border-left:4px solid var(--accent);}
#nice .insight-box, #write .insight-box{margin:16px 0;padding:14px 16px;background:#F6FAFF;border-left:5px solid var(--accent);}
</style>
"""


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def item_text(item):
    if isinstance(item, dict):
        title = item.get('title') or item.get('term') or item.get('label') or ''
        body = item.get('body') or item.get('definition') or item.get('text') or item.get('value') or ''
        if title and body:
            return f"**{title}**：{body}"
        return title or body
    return str(item)


def html_item_text(item):
    return item_text(item).replace("**", "<strong>", 1).replace("**", "</strong>", 1)


def table_to_markdown(table):
    if not isinstance(table, dict):
        return []
    columns = table.get('columns') or []
    rows = table.get('rows') or []
    if not columns or not rows:
        return []
    lines = [
        "| " + " | ".join(str(c) for c in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [row.get(c, "") for c in columns] if isinstance(row, dict) else list(row)
        lines.append("| " + " | ".join(str(v) for v in values) + " |")
    return lines


def table_to_html(table):
    if not isinstance(table, dict):
        return ""
    columns = table.get('columns') or []
    rows = table.get('rows') or []
    if not columns or not rows:
        return ""
    html = ["<table>", "<thead><tr>"]
    for col in columns:
        html.append(f"<th>{col}</th>")
    html.append("</tr></thead>")
    html.append("<tbody>")
    for row in rows:
        values = [row.get(c, "") for c in columns] if isinstance(row, dict) else list(row)
        html.append("<tr>")
        for value in values:
            html.append(f"<td>{value}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    return "\n".join(html)


def render_note_md(d):
    lines = []
    lines.append(f"# 【论文速记】{d['info']['title_cn']}\n")
    lines.append(f"> 原文标题：**{d['info']['title']}**  ")
    lines.append(f"> arXiv：{d['info']['link']}  ")
    lines.append(f"> 总评分：**{d['score']['total']:.1f} / 10**\n")
    lines.append("## 评分")
    for x in d['score']['dimensions']:
        lines.append(f"- {x['label']}：**{x['value']:.1f} / 2.0**")

    glossary = as_list(d.get('glossary') or d.get('terminology_notes'))
    if glossary:
        lines.append("\n## 术语说明")
        for item in glossary:
            lines.append(f"- {item_text(item)}")

    lines.append(f"\n## A. 研究问题\n{d['A_research_problem']}\n")
    lines.append("## B. 核心贡献")
    for i, item in enumerate(d['B_core_contributions'], 1):
        lines.append(f"{i}. {item_text(item)}")

    lines.append(f"\n## C. 方法 / 框架\n{d['C_method_framework']}\n")
    for section in as_list(d.get('method_subsections')):
        if isinstance(section, dict):
            lines.append(f"### {section.get('title', '')}")
            lines.append(str(section.get('body', '')))
        else:
            lines.append(f"### {section}")

    lines.append("## D. 关键结果")
    table_lines = table_to_markdown(d.get('result_table'))
    if table_lines:
        lines.extend(table_lines)
    else:
        for item in d['D_key_results']:
            lines.append(f"- {item_text(item)}")
    for note in as_list(d.get('source_notes')):
        lines.append(f"\n**数据来源**：{note}")
    if d.get('so_what'):
        lines.append(f"\n**So What**：{d['so_what']}")

    lines.append("\n## E. 产业启示")
    for item in d['E_industry_implications']:
        lines.append(f"- {item_text(item)}")
    if d.get('feige_view'):
        lines.append(f"\n**飞哥视角**：{d['feige_view']}")

    lines.append(f"\n## F. 一句话判断\n{d['F_one_line_judgement']}\n")
    limitations = as_list(d.get('limitations'))
    if limitations:
        lines.append("### 限制面")
        for item in limitations:
            lines.append(f"- {item_text(item)}")
    return "\n".join(lines)


def render_editor_html(d, title=None, conclusion=None):
    title = title or f"【论文速记】{d['info']['title_cn']}"
    conclusion = conclusion or d['F_one_line_judgement']
    html = [STYLE]
    html.append(f"<h1>{title}</h1>")
    html.append(f"\n<blockquote><p>{conclusion}</p></blockquote>\n")
    html.append('<p><img src="score_card.png" alt="评分卡" /></p>')
    html.append('<p><img src="info_card.png" alt="信息卡" /></p>')

    glossary = as_list(d.get('glossary') or d.get('terminology_notes'))
    if glossary:
        html.append('<div class="term-box"><p><strong>术语说明：</strong></p><ul>')
        for item in glossary:
            html.append(f"<li>{html_item_text(item)}</li>")
        html.append("</ul></div>")

    html.append(f"\n<h2>A. 研究问题</h2>\n<p>{d['A_research_problem']}</p>")
    html.append("\n<h2>B. 核心贡献</h2>\n<ul>")
    for item in d['B_core_contributions']:
        html.append(f"<li>{html_item_text(item)}</li>")
    html.append("</ul>")

    html.append(f"\n<h2>C. 方法/框架</h2>\n<p>{d['C_method_framework']}</p>")
    for section in as_list(d.get('method_subsections')):
        if isinstance(section, dict):
            html.append(f"<h3 class=\"blue-accent\">{section.get('title', '')}</h3>")
            html.append(f"<p>{section.get('body', '')}</p>")
        else:
            html.append(f"<h3 class=\"blue-accent\">{section}</h3>")

    html.append("\n<h2>D. 关键结果</h2>")
    result_table_html = table_to_html(d.get('result_table'))
    if result_table_html:
        html.append(result_table_html)
    else:
        html.append("<ul>")
        for item in d['D_key_results']:
            html.append(f"<li>{html_item_text(item)}</li>")
        html.append("</ul>")

    source_notes = as_list(d.get('source_notes'))
    if source_notes or d.get('so_what'):
        html.append('<div class="insight-box">')
        for note in source_notes:
            html.append(f"<p><strong>数据来源：</strong>{note}</p>")
        if d.get('so_what'):
            html.append(f"<p><strong>So What：</strong>{d['so_what']}</p>")
        html.append("</div>")

    html.append("\n<h2>E. 产业启示</h2>")
    implications = d['E_industry_implications']
    if implications and all(isinstance(item, dict) for item in implications):
        for item in implications:
            html.append(f"<h3 class=\"blue-accent\">{item.get('title', '')}</h3>")
            html.append(f"<p>{item.get('body', '')}</p>")
    else:
        html.append("<ul>")
        for item in implications:
            html.append(f"<li>{html_item_text(item)}</li>")
        html.append("</ul>")
    if d.get('feige_view'):
        html.append(f"<p><strong>飞哥视角：</strong>{d['feige_view']}</p>")

    html.append(f"\n<h2>F. 一句话判断</h2>\n<p>{d['F_one_line_judgement']}</p>")
    limitations = as_list(d.get('limitations'))
    if limitations:
        html.append("<h3 class=\"blue-accent\">限制面</h3><ul>")
        for item in limitations:
            html.append(f"<li>{html_item_text(item)}</li>")
        html.append("</ul>")
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
