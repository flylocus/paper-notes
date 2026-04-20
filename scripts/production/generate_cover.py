#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 2.35:1 cover image strictly adhering to the requested minimal style."""
import os, math
from PIL import Image, ImageDraw, ImageFont

W, H = 2350, 1000  # 2.35:1
PRIMARY = "#0B1430"
ACCENT = "#4CC3FF"  # Bright cyan for vertical line
ACCENT2 = "#2F6BFF" # Bright blue for horizontal line
TEXT = "#EAF4FF"
MUTED = "#B7C7E6"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
ROOT = os.path.dirname(SCRIPTS_ROOT)
FONT_REG = os.path.join(ROOT, "SourceHanSansCN-Regular.otf")
FONT_BOLD = os.path.join(ROOT, "SourceHanSansCN-Bold.otf")
LOGO_PATH = os.path.join(SCRIPTS_ROOT, "assets", "logo.jpg")

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_bg(draw):
    draw.rectangle([0, 0, W, H], fill=PRIMARY)

def extract_domain_from_title(title):
    domains = []
    title_lower = title.lower()
    domain_keywords = {
        "AI Agents": ["agent", "multi-agent", "llm agent", "autonomous agent"],
        "Computer Vision": ["vision", "image", "video", "detection", "segmentation"],
        "NLP": ["nlp", "language", "text", "translation", "summarization", "llm"],
        "Security": ["security", "privacy", "attack", "malicious", "supply chain"],
    }
    for domain, keywords in domain_keywords.items():
        if any(kw in title_lower for kw in keywords):
            domains.append(domain)
        if len(domains) >= 2:
            break
    if not domains:
        domains = ["AI Research"]
    return domains

def extract_keywords_from_title(title):
    words = title.replace("-", " ").replace(":", " ").split()
    stop_words = {"a", "an", "the", "and", "or", "in", "on", "to", "for", "of", "with", "is", "your"}
    keywords = [word for word in words if word.lower() not in stop_words and len(word) > 4]
    return keywords[:3]

def wrap_text(text, font, max_width, draw):
    lines = []
    cur = ""
    for word in text.split():
        test = cur + " " + word if cur else word
        w = draw.textlength(test, font=font)
        if w <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines

def main():
    import argparse
    import json
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="JSON data file")
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "cover_235.png"), help="output path")
    args = ap.parse_args()
    
    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "score": {"total": 9.1},
            "info": {"title": "Function Calling for Agentic Querying in NLP"}
        }

    img = Image.new("RGB", (W, H), PRIMARY)
    draw = ImageDraw.Draw(img)
    draw_bg(draw)
    
    # Text Setup
    f_header = load_font(FONT_BOLD, 54)
    f_label = load_font(FONT_REG, 30)
    f_score_val = load_font(FONT_BOLD, 64)
    f_value = load_font(FONT_REG, 40)
    
    # 调小了主标题字号 (85 -> 60)，副标题字号 (48 -> 42)
    f_main = load_font(FONT_BOLD, 60)
    f_sub = load_font(FONT_REG, 42)

    # Base coordinates
    left_x = 200
    right_x = 750
    start_y = 150

    # 1. Left Vertical Line (Cyan)
    line_top = start_y + 10
    line_bot = H - 200
    draw.rectangle([left_x - 40, line_top, left_x - 25, line_bot], fill=ACCENT)

    # 2. Left Sidebar Content
    y = start_y
    draw.text((left_x, y), "论文速记", fill=TEXT, font=f_header)
    
    y += 150
    draw.text((left_x, y), "领域", fill=MUTED, font=f_label)
    y += 50
    title = data.get("info", {}).get("title", "Untitled")
    for d in extract_domain_from_title(title):
        draw.text((left_x, y), d, fill=TEXT, font=f_value)
        y += 50
        
    y += 80
    draw.text((left_x, y), "评分", fill=MUTED, font=f_label)
    y += 50
    total_score = data.get("score", {}).get("total", 8.0)
    draw.text((left_x, y), f"{total_score:.1f} / 10", fill=ACCENT, font=f_score_val)
    
    y += 120
    draw.text((left_x, y), "关键词", fill=MUTED, font=f_label)
    y += 50
    for kw in extract_keywords_from_title(title):
        draw.text((left_x, y), kw, fill=TEXT, font=f_value)
        y += 50
        
    # Update vertical line bottom
    line_bot = y - 10
    draw.rectangle([left_x - 40, line_top, left_x - 25, line_bot], fill=ACCENT)

    # 3. Right Main Area (Strictly English Title + Chinese Subtitle)
    y = start_y + 40
    # Main Title with wrapping
    title_lines = wrap_text(title, f_main, 1400, draw)
    for line in title_lines[:3]: # limit to 3 lines max
        draw.text((right_x, y), line, fill=TEXT, font=f_main)
        # 调小了换行行距 (110 -> 85)
        y += 85
        
    y += 50
    # Subtitle (Chinese)
    # 取自定义的中文标题，如果没有则使用默认占位
    subtitle = data.get("info", {}).get("title_cn", "前沿研究论文速记")
    draw.text((right_x, y), subtitle, fill=ACCENT2, font=f_sub)
    
    y += 100
    # Horizontal line
    draw.rectangle([right_x, y, right_x + 900, y + 10], fill=ACCENT2)

    # Save
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    img.save(args.out)
    print(f"✅ Generated minimal cover: {args.out}")

if __name__ == "__main__":
    main()
