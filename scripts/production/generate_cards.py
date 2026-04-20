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
    print("OK", args.out)


if __name__ == "__main__":
    main()
