#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paper Notes card generator (score card + info card)

Usage:
  python3 generate_cards.py --data sample.json --out outputs

If --data is omitted, a built-in AgentLeak sample is used.
"""
import argparse
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 720
PRIMARY = "#0B1430"
ACCENT = "#4CC3FF"
ACCENT2 = "#2F6BFF"
TEXT = "#EAF4FF"
MUTED = "#B7C7E6"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
ROOT = os.path.dirname(SCRIPTS_ROOT)
ASSETS = os.path.join(SCRIPTS_ROOT, "assets")
FONT_REG = os.path.join(ROOT, "SourceHanSansCN-Regular.otf")
FONT_BOLD = os.path.join(ROOT, "SourceHanSansCN-Bold.otf")
LOGO_PATH = os.path.join(ASSETS, "logo.jpg")


def load_font(path, size):
    return ImageFont.truetype(path, size)


def draw_radial_bg(draw, img, inner="#10265F", outer=PRIMARY):
    # Simple radial gradient
    cx, cy = WIDTH * 0.55, HEIGHT * 0.35
    max_r = math.hypot(WIDTH, HEIGHT)
    for r in range(int(max_r), 0, -10):
        t = r / max_r
        color = _blend(inner, outer, t)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def _blend(c1, c2, t):
    def _hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    def _rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(r1 * (1 - t) + r2 * t)
    g = int(g1 * (1 - t) + g2 * t)
    b = int(b1 * (1 - t) + b2 * t)
    return _rgb_to_hex((r, g, b))


def round_rect(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def wrap_text(text, font, max_width, draw):
    if " " in text:
        lines = []
        cur = ""
        for token in text.split(" "):
            test = token if not cur else cur + " " + token
            if draw.textlength(test, font=font) <= max_width:
                cur = test
                continue
            if cur:
                lines.append(cur)
                cur = token
            else:
                lines.extend(_wrap_chars(token, font, max_width, draw))
                cur = ""
        if cur:
            lines.append(cur)
        return lines
    return _wrap_chars(text, font, max_width, draw)


def _wrap_chars(text, font, max_width, draw):
    lines = []
    cur = ""
    for ch in text:
        if ch == '\n':
            lines.append(cur)
            cur = ""
            continue
        test = cur + ch
        w = draw.textlength(test, font=font)
        if w <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def paste_logo(img):
    if not os.path.exists(LOGO_PATH):
        return
    logo = Image.open(LOGO_PATH).convert("RGBA")
    # Resize logo smaller for cleaner look
    max_w = 120
    scale = max_w / logo.width
    new_w = int(logo.width * scale)
    new_h = int(logo.height * scale)
    logo = logo.resize((new_w, new_h), Image.LANCZOS)

    # Make circular mask
    mask = Image.new("L", (new_w, new_h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((0, 0, new_w, new_h), fill=255)

    x = WIDTH - new_w - 50
    y = 26
    img.paste(logo, (x, y), mask)


def render_score_card(data, out_path):
    img = Image.new("RGB", (WIDTH, HEIGHT), PRIMARY)
    draw = ImageDraw.Draw(img)
    draw_radial_bg(draw, img)
    paste_logo(img)

    title_font = load_font(FONT_BOLD, 42)
    small_font = load_font(FONT_REG, 26)
    score_font = load_font(FONT_BOLD, 92)
    item_font = load_font(FONT_REG, 28)

    draw.text((60, 45), "评分卡", fill=TEXT, font=title_font)

    # Total score
    total = data["score"]["total"]
    draw.text((60, 160), "总分", fill=MUTED, font=small_font)
    draw.text((60, 210), f"{total:.1f} / 10", fill=ACCENT, font=score_font)

    # Dimensions list (right aligned values)
    dims = data["score"]["dimensions"]
    start_y = 360
    line_h = 55
    for i, d in enumerate(dims):
        y = start_y + i * line_h
        label = f"{d['label']}"
        value = f"{d['value']}/2"
        draw.text((60, y), label, fill=TEXT, font=item_font)
        w = draw.textlength(value, font=item_font)
        draw.text((WIDTH - 80 - w, y), value, fill=ACCENT, font=item_font)

    # Bottom bar
    draw.rectangle([60, HEIGHT - 70, WIDTH - 60, HEIGHT - 62], fill=ACCENT)

    img.save(out_path)


def render_info_card(data, out_path):
    img = Image.new("RGB", (WIDTH, HEIGHT), PRIMARY)
    draw = ImageDraw.Draw(img)
    draw_radial_bg(draw, img)
    paste_logo(img)

    title_font = load_font(FONT_BOLD, 42)
    label_font = load_font(FONT_REG, 26)
    text_font = load_font(FONT_REG, 28)

    draw.text((60, 45), "论文信息", fill=TEXT, font=title_font)

    x, y = 60, 150
    draw.text((x, y), "标题", fill=ACCENT, font=label_font)
    y += 38
    title_lines = wrap_text(data["info"]["title"], text_font, 960, draw)
    for line in title_lines[:2]:
        draw.text((x, y), line, fill=TEXT, font=text_font)
        y += 36

    y += 12
    draw.text((x, y), "链接", fill=ACCENT, font=label_font)
    y += 38
    draw.text((x, y), data["info"]["link"], fill=TEXT, font=text_font)

    y += 44
    draw.text((x, y), "作者", fill=ACCENT, font=label_font)
    y += 38
    authors = " / ".join(data["info"]["authors"])
    for line in wrap_text(authors, text_font, 960, draw)[:2]:
        draw.text((x, y), line, fill=TEXT, font=text_font)
        y += 36

    y += 12
    draw.text((x, y), "单位", fill=ACCENT, font=label_font)
    y += 38
    orgs = "; ".join(data["info"].get("affiliations", [])) or "—"
    for line in wrap_text(orgs, text_font, 960, draw)[:2]:
        draw.text((x, y), line, fill=TEXT, font=text_font)
        y += 36

    img.save(out_path)


def render_combined_card(data, out_path):
    """论文信息 + 评分卡 手机竖版 Banner (600 × 580)

    设计原则：Header Card 只是身份Banner，不是全文摘要。
    - 目标：用户在微信里扫一眼就知道「这是哪篇？打了多少分？
    - 不重复：作者/机构/链接在正文顶部，不重复占位
    - 无风险：两列布局，16px字体，保证窄屏不重叠

    详细设计规范见：docs/HEADER_CARD_DESIGN.md
    """
    CARD_W, CARD_H = 600, 580  # 高度减半，紧贴内容
    img = Image.new("RGB", (CARD_W, CARD_H), PRIMARY)
    draw = ImageDraw.Draw(img)

    # 渐变背景
    cx, cy = CARD_W * 0.5, CARD_H * 0.3
    max_r = math.hypot(CARD_W, CARD_H)
    for r in range(int(max_r), 0, -12):
        t = r / max_r
        color = _blend("#10265F", PRIMARY, t)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    PADDING = 50
    RIGHT_MARGIN = CARD_W - PADDING

    # 字体
    title_font = load_font(FONT_BOLD, 26)
    score_font = load_font(FONT_BOLD, 70)
    dim_label_font = load_font(FONT_REG, 16)
    dim_value_font = load_font(FONT_BOLD, 16)

    y = PADDING + 30

    # ===== LOGO 居中 =====
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        max_w = 80
        scale = max_w / logo.width
        new_w = int(logo.width * scale)
        new_h = int(logo.height * scale)
        logo = logo.resize((new_w, new_h), Image.LANCZOS)
        mask = Image.new("L", (new_w, new_h), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0, 0, new_w, new_h), fill=255)
        logo_x = (CARD_W - new_w) // 2
        img.paste(logo, (logo_x, y), mask)
        y += new_h + 30

    # ===== 一行标题：中文 + 英文缩写 =====
    title_text = "科学仪器 Agent 基准：LabOSBench"
    title_w = draw.textlength(title_text, font=title_font)
    draw.text(((CARD_W - title_w) // 2, y), title_text, fill=ACCENT, font=title_font)
    y += 55

    # ===== 分割线 1 =====
    draw.rectangle([PADDING, y, RIGHT_MARGIN, y + 2], fill=ACCENT2)
    y += 35

    # ===== 5维度评分：两列（左3右2），标签分数间留安全距离 =====
    dims = data["score"]["dimensions"]
    col_w = (RIGHT_MARGIN - PADDING) // 2 - 20  # 列宽减小，留更多间距
    value_gap = 40  # 标签和分数之间最少留 40px 安全距离

    for i, d in enumerate(dims):
        col = i % 2  # 0=左列, 1=右列
        row = i // 2
        xx = PADDING if col == 0 else PADDING + col_w + 40  # 列间距加大
        yy = y + row * 38

        label = d["label"]
        value = f"{d['value']}/2"

        # 左列：标签最大宽度留足给分数
        if col == 0:
            label_max_w = col_w - value_gap
            label_w = draw.textlength(label, font=dim_label_font)
            if label_w > label_max_w:
                # 超长时只显示中文部分
                label_short = label.split(" ")[0]
                draw.text((xx, yy), label_short, fill=TEXT, font=dim_label_font)
            else:
                draw.text((xx, yy), label, fill=TEXT, font=dim_label_font)
            w = draw.textlength(value, font=dim_value_font)
            draw.text((PADDING + col_w - w, yy), value, fill=ACCENT, font=dim_value_font)
        # 右列：标签最大宽度留足给分数
        else:
            label_max_w = col_w - value_gap
            label_w = draw.textlength(label, font=dim_label_font)
            if label_w > label_max_w:
                # 超长时只显示中文部分
                label_short = label.split(" ")[0]
                draw.text((xx, yy), label_short, fill=TEXT, font=dim_label_font)
            else:
                draw.text((xx, yy), label, fill=TEXT, font=dim_label_font)
            w = draw.textlength(value, font=dim_value_font)
            draw.text((RIGHT_MARGIN - w, yy), value, fill=ACCENT, font=dim_value_font)

    y += 3 * 38 + 15  # 3行高度

    # ===== 分割线 2 =====
    draw.rectangle([PADDING, y, RIGHT_MARGIN, y + 2], fill=ACCENT2)
    y += 25  # 减小间距

    # ===== 总分：居中放大，与底部条拉开安全距离 =====
    total = data["score"]["total"]
    total_text = f"{total:.1f} / 10"
    total_w = draw.textlength(total_text, font=score_font)
    draw.text(((CARD_W - total_w) // 2, y), total_text, fill=ACCENT, font=score_font)
    y += 95  # 总分高度 + 底部间距

    # ===== 底部条在总分下方，不重叠 =====
    draw.rectangle([PADDING, y, RIGHT_MARGIN, y + 3], fill=ACCENT)

    img.save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="JSON data file")
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs"), help="output dir")
    args = ap.parse_args()

    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "paper_title": "AgentLeak",
            "score": {
                "total": 8.0,
                "dimensions": [
                    {"label": "重要性 Impact", "value": 2.0},
                    {"label": "创新性 Novelty", "value": 1.5},
                    {"label": "可验证性 Evidence", "value": 1.0},
                    {"label": "产业可用性 Applicability", "value": 2.0},
                    {"label": "可复用性 Reusability", "value": 1.5},
                ],
            },
            "info": {
                "title": "AgentLeak: A Full-Stack Benchmark for Privacy Leakage in Multi-Agent LLM Systems",
                "link": "https://arxiv.org/abs/2602.11510",
                "authors": ["Faouzi El Yagoubi", "Godwin Badu-Marfo", "Ranwa Al Mallah"],
                "affiliations": ["Polytechnique Montréal (Computer and Software Engineering)"]
            }
        }

    os.makedirs(args.out, exist_ok=True)
    render_score_card(data, os.path.join(args.out, "score_card.png"))
    render_info_card(data, os.path.join(args.out, "info_card.png"))
    render_combined_card(data, os.path.join(args.out, "header_card.png"))
    print("OK", args.out)


if __name__ == "__main__":
    main()
