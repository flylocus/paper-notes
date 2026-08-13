#!/usr/bin/env python3
"""Render a WeChat-safe paper-notes article from generate_data.json.

This renderer is intentionally separate from render_article.py. It avoids style tags,
classes, and divs so the output survives WeChat editor paste/cleanup more reliably.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

THEME = {
    "root": "font-size:16px;line-height:1.78;color:#172033;letter-spacing:0;",
    "container": "max-width:680px;margin:0 auto;",
    "hero": "margin:0 0 18px;padding:16px 16px 14px;border-left:6px solid #0f4c81;border-top:1px solid #dbe7f5;border-bottom:1px solid #dbe7f5;background-color:#f8fbff;color:#0b1430;",
    "hero_p": "font-size:16px;line-height:1.75;margin:0 0 12px;color:#172033;",
    "meta": "display:inline-block;font-size:12px;color:#2563eb;background-color:#eef6ff;border:1px solid #dbeafe;border-radius:999px;padding:3px 10px;margin:0 8px 6px 0;",
    "quote": "margin:14px 0 18px;padding:13px 15px;background-color:#f8fafc;border-left:5px solid #2f6bff;color:#0f172a;font-size:17px;font-weight:700;",
    "image": "margin:14px 0;text-align:center;",
    "img": "width:100%;display:block;border:0;",
    "h2": "font-size:18px;line-height:1.4;color:#0b1430;font-weight:800;margin:26px 0 14px;padding-left:10px;border-left:5px solid #2f6bff;",
    "h2_orange": "font-size:18px;line-height:1.4;color:#0b1430;font-weight:800;margin:26px 0 14px;padding-left:10px;border-left:5px solid #f97316;",
    "h3": "font-size:16px;line-height:1.5;color:#0f172a;font-weight:800;margin:16px 0 8px;",
    "p": "margin:9px 0;color:#334155;font-size:15.5px;line-height:1.82;",
    # 术语框：去掉底部边框，只保留顶部淡分割线，降低前四屏的卡片密度感
    "soft": "margin:14px 0 18px;padding:12px 14px 0;background-color:#fbfdff;border-left:0;border-top:1px solid #e6f0fc;",
    "term": "margin:7px 0;color:#334155;font-size:15px;line-height:1.75;",
    "li": "margin:7px 0;color:#334155;font-size:15.5px;line-height:1.78;",
    "table": "width:100%;border-collapse:collapse;margin:12px 0 10px;font-size:14px;",
    "th": "border:1px solid #d9e6ff;padding:8px 10px;vertical-align:top;background-color:#eef6ff;color:#0b1430;font-weight:700;",
    "td": "border:1px solid #d9e6ff;padding:8px 10px;vertical-align:top;color:#334155;",
    # insight-box：增加顶部2px深蓝线，强化"数据→解读"的阅读序列
    "insight": "margin:16px 0;padding:14px 16px;background-color:#f8fafc;border-left:5px solid #0b1430;border-top:2px solid #2f6bff;color:#0f172a;",
    "d_card": "margin:10px 0;padding:12px 14px;background-color:#fffbf8;border-left:4px solid #f97316;border-top:1px solid #fed7aa;",
    "d_badge": "display:inline-block;min-width:48px;text-align:center;margin-right:8px;padding:2px 7px;border-radius:999px;background-color:#ffedd5;color:#c2410c;font-size:12px;font-weight:800;",
    "d_title": "display:inline;color:#0b1430;font-size:15.5px;font-weight:800;line-height:1.78;",
    "d_data": "margin:8px 0 4px;color:#0f172a;font-size:16px;line-height:1.75;font-weight:700;",
    "d_note": "margin:0;color:#64748b;font-size:14.5px;line-height:1.7;",
    # E段产业启示：浅灰蓝卡片底色 + 圆角数字徽章，强化视觉锚点
    "e_card": "margin:12px 0;padding:14px 15px;background-color:#f1f5f9;border-left:4px solid #94a3b8;border-radius:6px;",
    "e_badge": "display:inline-block;min-width:30px;text-align:center;margin-right:10px;padding:3px 8px;border-radius:999px;background-color:#bae6fd;color:#0369a1;font-size:13px;font-weight:800;",
    "e_body": "display:inline;color:#334155;font-size:15.5px;line-height:1.78;",
    "feige": "margin:16px 0;padding:14px 16px;background-color:#0b1430;color:#ffffff;border-left:5px solid #4cc3ff;",
    # F段限制面：保持蓝边条标题，只在卡片本身用橙色，与D段形成"数据-后果"呼应
    "limit": "margin:14px 0;padding:12px 14px;background-color:#fff7ed;border-left:4px solid #f97316;border-radius:6px;color:#334155;",
    "source": "margin:8px 0;padding:10px 12px;background-color:#f8fafc;border-top:1px solid #e2e8f0;font-size:13px;color:#475569;word-break:break-all;",
    "divider": "height:1px;background-color:#e2e8f0;margin:22px 0;",
    # info_card HTML版：作者、机构、链接信息块
    "info_meta": "margin:10px 0 16px;padding:12px 14px;background-color:#fafbfc;border-left:3px solid #cbd5e1;border-radius:4px;",
    "info_row": "margin:5px 0;font-size:13px;color:#475569;line-height:1.65;",
    "info_label": "display:inline-block;min-width:50px;color:#64748b;font-weight:700;",
    "info_link": "color:#2563eb;text-decoration:none;word-break:break-all;",
    # 导读过渡：评分卡后衔接正文的引导语
    "intro_lead": "margin:10px 0 18px;padding:10px 14px;background-color:#f0f9ff;border-left:3px solid #7dd3fc;border-radius:4px;color:#0c4a6e;font-size:14px;line-height:1.7;",
    # footer文字版（公众号原生账号卡模式的兜底）
    "footer_text": "margin:16px 0;padding:12px 14px;background-color:#f8fafc;border-top:1px solid #e2e8f0;color:#64748b;font-size:13px;line-height:1.7;",
    "footer_title": "font-weight:800;color:#475569;margin:0 0 6px;font-size:14px;",
    "footer_ul": "margin:6px 0;padding-left:20px;",
    "footer_li": "margin:3px 0;color:#64748b;font-size:13px;",
}


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def as_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def item_parts(item: object) -> tuple[str, str]:
    if isinstance(item, dict):
        title = item.get("title") or item.get("term") or item.get("label") or ""
        body = item.get("body") or item.get("explanation") or item.get("definition") or item.get("text") or item.get("value") or ""
        return str(title), str(body)
    return "", str(item)


def render_paragraphs(text: str) -> list[str]:
    chunks = [x.strip() for x in (text or "").split("\n") if x.strip()]
    return [f'<p style="{THEME["p"]}">{esc(x)}</p>' for x in chunks]


def render_bullets(items: list) -> str:
    out = ["<ul style=\"padding-left:22px;margin:8px 0 14px;\">"]
    for item in items:
        title, body = item_parts(item)
        if title and body:
            text = f'<span style="color:#0b1430;font-weight:700;">{esc(title)}</span>：{esc(body)}'
        else:
            text = esc(title or body)
        out.append(f'<li style="{THEME["li"]}">{text}</li>')
    out.append("</ul>")
    return "\n".join(out)


def render_table(table: dict | None) -> str:
    if not isinstance(table, dict):
        return ""
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    if not columns or not rows:
        return ""
    out = [f'<table style="{THEME["table"]}">', "<thead><tr>"]
    for col in columns:
        out.append(f'<th style="{THEME["th"]}">{esc(col)}</th>')
    out.append("</tr></thead><tbody>")
    for row in rows:
        values = [row.get(c, "") for c in columns] if isinstance(row, dict) else list(row)
        out.append("<tr>")
        for value in values:
            out.append(f'<td style="{THEME["td"]}">{esc(value)}</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def render_result_cards(table: dict | None) -> str:
    if not isinstance(table, dict):
        return ""
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    if len(columns) < 3 or not rows:
        return ""
    out = []
    for idx, row in enumerate(rows, 1):
        values = [row.get(c, "") for c in columns] if isinstance(row, dict) else list(row)
        title = values[0] if len(values) > 0 else ""
        data = values[1] if len(values) > 1 else ""
        note = values[2] if len(values) > 2 else ""
        out.append(f'<section style="{THEME["d_card"]}">')
        out.append(f'<p style="margin:0 0 6px;"><span style="{THEME["d_badge"]}">证据 {idx:02d}</span><span style="{THEME["d_title"]}">{esc(title)}</span></p>')
        if data:
            out.append(f'<p style="{THEME["d_data"]}">{esc(data)}</p>')
        if note:
            out.append(f'<p style="{THEME["d_note"]}">{esc(note)}</p>')
        out.append('</section>')
    return "\n".join(out)


# ── 作者签名（直接插图版；默认推荐安全卡，无加微/个人码）────────────────────
AUTHOR_SIGNATURE_FILE = "author-signature-card.png"
DEFAULT_SAFE_SIGNATURE = Path(__file__).resolve().parents[2] / "assets" / "author_signature_image_safe.png"
AUTHOR_SIGNATURE = f'''<section style="margin:24px 0 8px;text-align:center;border-radius:8px;overflow:hidden;">
  <img src="{AUTHOR_SIGNATURE_FILE}" alt="申飞" style="width:100%;display:block;border:0;border-radius:8px;" />
</section>'''


def render_footer(out_dir: Path, mode: str = "auto") -> str:
    """footer双版本策略
    - mode="image": 强制用图片footer（本地HTML/其他平台/兜底）
    - mode="text": 强制用文字版（公众号发布，配合微信原生账号卡）
    - mode="auto": 优先图片，不存在则用文字

    2026-07-16+: 公众号公域推荐场景优先 text（避免双号二维码互推被判导流）。
    """
    if mode in ["image", "auto"]:
        candidates = [
            out_dir / "wechat-footer-guide.jpg",
            out_dir / "wechat-footer-guide.png",
            ROOT / "outputs" / "assets" / "wechat-footer-guide.jpg",
        ]
        for path in candidates:
            if path.exists():
                rel = path.name if path.parent == out_dir else str(path)
                return f'<section style="margin:20px 0 0;"><img src="{esc(rel)}" alt="更多 AI 与 ToB 深度内容" style="{THEME["img"]}" /></section>'

    # 文字版footer：公众号发布模式，配合微信原生账号卡片
    if mode in ["text", "auto"]:
        return f'''<section style="{THEME["footer_text"]}">
    <p style="{THEME["footer_title"]}">📚 关于 paper-notes</p>
    <p style="{THEME["info_row"]}">每天一篇 AI 顶会论文速读，聚焦：可落地的技术信号、产业转化机会、真实落地边界。</p>
    <ul style="{THEME["footer_ul"]}">
    <li style="{THEME["footer_li"]}"><strong>AI 系统笔记</strong>：技术架构与工程落地</li>
    <li style="{THEME["footer_li"]}"><strong>Dare to B2B</strong>：商业化与产业观察</li>
    </ul>
    </section>'''
    return ""


def strip_label(text: str, label: str) -> str:
    text = text or ""
    return text[len(label):].lstrip("：: ") if text.startswith(label) else text


def render(d: dict, out_dir: Path, *, title: str = "", conclusion: str = "", footer_mode: str = "auto") -> str:
    info = d.get("info") or {}
    score = d.get("score") or {}
    title = title or f"【论文速记】{info.get('title_cn') or d.get('paper_title') or ''}"
    conclusion = conclusion or d.get("F_one_line_judgement") or ""
    total = score.get("total")
    total_text = f"{float(total):.1f}" if isinstance(total, (int, float)) else esc(total)

    out = [
        '<section id="nice" data-theme="wechat_safe_paper_v1" style="{}">'.format(THEME["root"]),
        f'<section style="{THEME["container"]}">',
    ]

    out.append(f'<section style="{THEME["hero"]}">')
    out.append(f'<p style="{THEME["hero_p"]}">{esc(info.get("title"))}</p>')
    source_label = info.get("source_label") or "arXiv"
    out.append(f'<span style="{THEME["meta"]}">{esc(source_label)}：{esc(info.get("link"))}</span>')
    out.append(f'<span style="{THEME["meta"]}">评分：{total_text} / 10</span>')
    if info.get("title_cn"):
        out.append(f'<span style="{THEME["meta"]}">{esc(info.get("title_cn"))}</span>')
    out.append("</section>")

    out.append(f'<blockquote style="{THEME["quote"]}">{esc(conclusion)}</blockquote>')

    # 头部图片：优先用 9:16 竖版 header_card（手机原生适配，单列不挤）
    # 回退方案：双图模式 + HTML元信息
    header_img = out_dir / "header_card.png"
    score_img = out_dir / "score_card.png"
    info_img = out_dir / "info_card.png"

    def _append_intro_lead() -> None:
        # One Fact, One Place：intro_lead 不得默认复读 so_what。
        # - 显式提供 intro_lead 且非空 → 渲染
        # - 显式提供空串 / null → 跳过（避免与 So What 重复）
        # - 未提供字段 → 兼容旧稿，回退 so_what / feige_view
        if "intro_lead" in d:
            lead = str(d.get("intro_lead") or "").strip()
            if not lead:
                return
        else:
            lead = str(d.get("so_what") or d.get("feige_view") or "").strip()
            if not lead:
                lead = "快速了解这篇论文的核心价值与产业意义。"
        out.append(f'<section style="{THEME["intro_lead"]}">💡 {esc(lead)}</section>')

    if header_img.exists():
        # 9:16 竖版模式：居中显示，左右留白，适配手机窄屏
        out.append(f'<section style="margin:10px 0;text-align:center;"><img src="header_card.png" alt="论文评分与信息" style="max-width:100%;width:360px;display:inline-block;border:0;border-radius:8px;" /></section>')
        _append_intro_lead()
    elif score_img.exists() and info_img.exists():
        # 双图模式：两张图 + HTML元信息（向后兼容）
        out.append(f'<section style="{THEME["image"]}"><img src="score_card.png" alt="评分卡" style="{THEME["img"]}" /></section>')
        _append_intro_lead()

        authors = ", ".join(info.get("authors", [])[:5])
        if len(info.get("authors", [])) > 5:
            authors += f" 等 {len(info['authors'])} 人"
        affiliations = info.get("affiliations") or ""
        if isinstance(affiliations, list):
            affiliations = "；".join(affiliations[:2])
        link = info.get("link", "")

        out.append(f'<section style="{THEME["info_meta"]}">')
        if authors:
            out.append(f'<p style="{THEME["info_row"]}"><span style="{THEME["info_label"]}">作者：</span>{esc(authors)}</p>')
        if affiliations:
            out.append(f'<p style="{THEME["info_row"]}"><span style="{THEME["info_label"]}">机构：</span>{esc(str(affiliations))}</p>')
        if link:
            out.append(f'<p style="{THEME["info_row"]}"><span style="{THEME["info_label"]}">链接：</span><span style="{THEME["info_link"]}">{esc(link)}</span></p>')
        out.append(f'<p style="{THEME["info_row"]}"><span style="{THEME["info_label"]}">评分：</span>{total_text} / 10</p>')
        out.append('</section>')

    glossary = as_list(d.get("glossary") or d.get("terminology_notes"))
    if glossary:
        out.append(f'<section style="{THEME["soft"]}">')
        out.append(f'<p style="{THEME["p"]}"><span style="color:#0b1430;font-weight:800;">术语说明</span></p>')
        for item in glossary:
            term, definition = item_parts(item)
            if term and definition:
                out.append(f'<p style="{THEME["term"]}"><span style="color:#0b1430;font-weight:700;">{esc(term)}</span>：{esc(definition)}</p>')
            else:
                out.append(f'<p style="{THEME["term"]}">{esc(term or definition)}</p>')
        out.append("</section>")

    out.append(f'<h2 style="{THEME["h2"]}">A. 研究问题</h2>')
    out.extend(render_paragraphs(d.get("A_research_problem") or ""))

    out.append(f'<h2 style="{THEME["h2"]}">B. 核心贡献</h2>')
    out.append(render_bullets(as_list(d.get("B_core_contributions"))))

    out.append(f'<h2 style="{THEME["h2"]}">C. 方法 / 框架</h2>')
    out.extend(render_paragraphs(d.get("C_method_framework") or ""))
    for section in as_list(d.get("method_subsections")):
        title_text, body = item_parts(section)
        if title_text:
            out.append(f'<h3 style="{THEME["h3"]}">{esc(title_text)}</h3>')
        if body:
            out.extend(render_paragraphs(body))

    out.append(f'<h2 style="{THEME["h2_orange"]}">D. 关键结果</h2>')
    # 兼容新旧字段名：table (旧) / result_table (新)
    table_data = d.get("result_table") or d.get("table")
    result_cards = render_result_cards(table_data)
    if result_cards:
        out.append(result_cards)
    elif table_data:
        out.append(render_table(table_data))
    else:
        out.append(render_bullets(as_list(d.get("D_key_results"))))

    # Optional: concentrated failure-mode list (One Fact — list once in D)
    failure_modes = d.get("failure_modes")
    if isinstance(failure_modes, dict) and failure_modes.get("items"):
        fm_title = str(failure_modes.get("title") or "反复失败模式").strip()
        fm_intro = str(failure_modes.get("intro") or "").strip()
        out.append(f'<h3 style="{THEME["h3"]}">{esc(fm_title)}</h3>')
        if fm_intro:
            out.extend(render_paragraphs(fm_intro))
        out.append(render_bullets(as_list(failure_modes.get("items"))))

    source_notes = as_list(d.get("source_notes"))
    so_what = d.get("so_what") or ""
    if source_notes or so_what:
        out.append(f'<blockquote style="{THEME["insight"]}">')
        for note in source_notes:
            out.append(f'<p style="margin:0 0 8px;"><span style="color:#0b1430;font-weight:800;">数据来源：</span>{esc(note)}</p>')
        if so_what:
            out.append(f'<p style="margin:0;"><span style="color:#0b1430;font-weight:800;">So What：</span>{esc(so_what)}</p>')
        out.append("</blockquote>")


    out.append(f'<h2 style="{THEME["h2"]}">E. 产业启示</h2>')
    implications = as_list(d.get("E_industry_implications"))
    if implications and all(isinstance(x, dict) for x in implications):
        for idx, item in enumerate(implications, 1):
            title_text, body = item_parts(item)
            out.append(f'<section style="{THEME["e_card"]}"><span style="{THEME["e_badge"]}">{idx:02d}</span><span style="{THEME["e_body"]}">{esc(title_text)}</span></section>')
            out.extend(render_paragraphs(body))
    else:
        for idx, item in enumerate(implications, 1):
            _, body = item_parts(item)
            text = body.strip()
            prefix = f"{idx:02d}"
            if text[:2].isdigit():
                prefix = text[:2]
                text = text[2:].lstrip(" .。")
            out.append(f'<section style="{THEME["e_card"]}"><span style="{THEME["e_badge"]}">{esc(prefix)}</span><span style="{THEME["e_body"]}">{esc(text)}</span></section>')
    if d.get("feige_view"):
        feige_text = strip_label(str(d.get("feige_view")), "飞哥视角")
        out.append(f'<blockquote style="{THEME["feige"]}"><span style="font-weight:800;color:#93c5fd;">飞哥视角：</span>{esc(feige_text)}</blockquote>')

    out.append(f'<h2 style="{THEME["h2"]}">{esc(d.get("F_section_title") or "F. 一句话判断")}</h2>')
    out.extend(render_paragraphs(d.get("F_one_line_judgement") or ""))
    limitations = as_list(d.get("limitations"))
    if limitations:
        # 「结论与边界」仍保留「限制面」小标题，满足 QA 完整性检查，同时不再单开一层主章节。
        out.append(f'<section style="{THEME["limit"]}">')
        out.append(f'<p style="margin:0 0 8px;color:#9a3412;font-weight:800;">限制面</p>')
        out.append(render_bullets(limitations))
        out.append("</section>")


    # 业务落地指引（销售导向 · Battlecard 格式）
    # 借鉴 pm-skills/pm-go-to-market 的 competitive-battlecard 框架
    target_audience = as_list(d.get("target_audience"))
    sales_use_cases = as_list(d.get("sales_use_cases"))
    objection_handling = as_list(d.get("objection_handling"))
    copy_paste_lines = as_list(d.get("copy_paste_lines"))
    key_quotes = as_list(d.get("key_quotes"))

    if target_audience or sales_use_cases or objection_handling or copy_paste_lines or key_quotes:
        out.append(f'<section style="{THEME["soft"]}">')
        out.append(f'<p style="{THEME["p"]}"><span style="color:#0b1430;font-weight:800;">🎯 销售战斗卡</span></p>')

        if target_audience:
            out.append(f'<p style="margin:12px 0 4px;"><span style="color:#0b1430;font-weight:700;">👥 对谁有用</span></p>')
            out.append(render_bullets(target_audience))

        if sales_use_cases:
            out.append(f'<p style="margin:12px 0 4px;"><span style="color:#0b1430;font-weight:700;">💼 可以用在什么场景</span></p>')
            out.append(render_bullets(sales_use_cases))

        if objection_handling:
            out.append(f'<p style="margin:12px 0 4px;"><span style="color:#0b1430;font-weight:700;">🛡️ 常见反对意见回应</span></p>')
            out.append(render_bullets(objection_handling))

        if copy_paste_lines:
            out.append(f'<p style="margin:12px 0 4px;"><span style="color:#0b1430;font-weight:700;">📋 可以直接复制的话术</span></p>')
            for line in copy_paste_lines:
                out.append(f'<blockquote style="{THEME.get("quote", THEME["soft"])}">{esc(str(line))}</blockquote>')

        if key_quotes:
            quote_label = "报告金句" if d.get("content_label") == "技术报告速记" else "论文金句"
            out.append(f'<p style="margin:12px 0 4px;"><span style="color:#0b1430;font-weight:700;">💬 {esc(quote_label)}</span></p>')
            out.append(render_bullets(key_quotes))

        out.append("</section>")

    source_urls = []
    link = info.get("link")
    if link:
        source_label = info.get("source_label") or "arXiv 摘要"
        source_urls.append((source_label, link))
    for key in ["code", "code_url", "dataset", "dataset_url", "project_url"]:
        value = d.get(key) or info.get(key)
        if value:
            source_urls.append((key, value))
    if source_urls:
        out.append(f'<h2 style="{THEME["h2"]}">来源链接</h2>')
        for label, url in source_urls:
            out.append(f'<section style="{THEME["source"]}"><span style="color:#0b1430;font-weight:800;">{esc(label)}</span><br/><span style="color:#2563eb;text-decoration:none;">{esc(url)}</span></section>')

    # 同题精选：放在来源链接之后、footer/签名之前（对齐 Beyond Leaderboard 样式）
    related = d.get("related_theme_picks") or {}
    related_items = related.get("items") if isinstance(related, dict) else None
    if isinstance(related_items, list) and related_items:
        theme = str(related.get("theme") or "").strip() or "同题"
        intro = str(related.get("intro") or "").strip()
        n = len(related_items)
        out.append(f'<section style="{THEME["divider"]}"></section>')
        out.append(
            f'<h2 style="{THEME["h2"]}">同题精选（{n}）'
            + (f'· {esc(theme)}' if theme else '')
            + '</h2>'
        )
        if intro:
            out.append(
                f'<p style="margin:9px 0;color:#334155;font-size:15px;line-height:1.75;">{esc(intro)}</p>'
            )
        out.append('<ol style="padding-left:22px;margin:8px 0 14px;">')
        for item in related_items:
            if not isinstance(item, dict):
                continue
            title_cn = str(item.get("title_cn") or "").strip()
            one_liner = str(item.get("one_liner") or "").strip()
            link = str(item.get("link") or "").strip()
            arxiv_id = str(item.get("arxiv_id") or "").strip()
            account = str(item.get("account") or "").strip()
            id_bit = f'（{esc(arxiv_id)}）' if arxiv_id else (f'（{esc(account)}）' if account else '')
            dash = f'—— {esc(one_liner)}' if one_liner else ''
            out.append(
                f'<li style="margin:8px 0;color:#334155;font-size:15px;line-height:1.75;">'
                f'<strong>{esc(title_cn)}</strong>{id_bit}{dash}'
            )
            if link:
                out.append(
                    f'<br/><span style="color:#2563eb;font-size:13px;">{esc(link)}</span>'
                )
            out.append('</li>')
        out.append('</ol>')

    footer = render_footer(out_dir, mode=footer_mode)
    if footer:
        out.append(f'<section style="{THEME["divider"]}"></section>')
        out.append(footer)

    # 作者签名块：条件输出（用于公众号场景，同 footer_text 模式）
    out.append(AUTHOR_SIGNATURE)

    out.append("</section></section>")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-payload", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--out", default="article_wechat_safe.html")
    parser.add_argument("--html-title", default="")
    parser.add_argument("--html-conclusion", default="")
    parser.add_argument("--footer-mode", default="text", choices=["auto", "image", "text"],
                        help="footer模式: text=公众号推荐安全(默认), auto=优先图片否则文字, image=强制图片")
    parser.add_argument("--author-qr", default="",
                        help="作者签名卡图片路径；默认用 assets/author_signature_image_safe.png（无加微/个人码）。传旧版加微卡会限推荐。")
    args = parser.parse_args()

    payload_path = Path(args.article_payload)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 作者签名：默认推荐安全卡；显式 --author-qr 可覆盖
    global AUTHOR_SIGNATURE
    import shutil
    qr_src = Path(args.author_qr) if args.author_qr else DEFAULT_SAFE_SIGNATURE
    if qr_src.exists():
        shutil.copy2(qr_src, out_dir / AUTHOR_SIGNATURE_FILE)
        if qr_src.name == "author_signature_image.png":
            print("⚠ 警告: 旧版加微/个人码签名卡，公域推荐风险高；请改用 author_signature_image_safe.png")
    else:
        print(f"⚠ 签名卡图片未找到: {qr_src}，跳过作者签名")
        AUTHOR_SIGNATURE = ""

    data = json.loads(payload_path.read_text(encoding="utf-8"))
    html_text = render(data, out_dir, title=args.html_title, conclusion=args.html_conclusion, footer_mode=args.footer_mode)
    out_path = out_dir / args.out
    out_path.write_text(html_text, encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
