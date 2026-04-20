#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, json, argparse, os
from typing import List, Dict, Any

ARXIV_ABS_RE = re.compile(r'https?://arxiv\.org/abs/(\d{4}\.\d{5})')
ARXIV_PDF_RE = re.compile(r'https?://arxiv\.org/pdf/(\d{4}\.\d{5})(?:\.pdf)?')
NOISE_PATTERNS = ["100% 对应真实存在", "无幻觉", "已工具核查", "定时提醒", "明天 1 点见", "严格核查流程已内置"]

def norm_num(s: str) -> int:
    s = s.strip().lower().replace(",", "")
    if "万" in s: return int(float(re.findall(r'[\d.]+', s)[0]) * 10000)
    if "k" in s: return int(float(re.findall(r'[\d.]+', s)[0]) * 1000)
    m = re.findall(r'[\d.]+', s)
    return int(float(m[0])) if m else 0

def extract_arxiv_id(text: str):
    m = ARXIV_ABS_RE.search(text) or ARXIV_PDF_RE.search(text)
    return m.group(1) if m else None

def split_blocks(text: str) -> List[str]:
    # split by numbered headings: "1. ..." or "**1. ..." or "1) ..."
    parts = re.split(r'(?m)^(?:\*\*)?\d+[\.\)]\s+', text)
    return [p.strip() for p in parts if p.strip()]

def clean_line(s: str) -> str:
    return re.sub(r'^[\-\*\s]+|[\s\*]+$', '', s).strip()

def parse_block(block: str, source: str) -> Dict[str, Any]:
    if any(p in block for p in NOISE_PATTERNS):
        pass  # keep block, but noise lines are implicitly skipped below by tight matching

    lines = [l.strip() for l in block.splitlines() if l.strip()]
    title = clean_line(lines[0]) if lines else ""

    # title fallback from **...**
    m_title = re.search(r'\*\*(.*?)\*\*', block)
    if m_title and len(m_title.group(1)) > 5:
        title = m_title.group(1).strip()

    arxiv_id = extract_arxiv_id(block)
    if not arxiv_id:
        return {}

    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"

    # authors
    authors_raw = ""
    m_auth = re.search(r'(?:Authors?|作者)[:：]\s*(.+)', block, re.I)
    if m_auth:
        authors_raw = m_auth.group(1).strip()
    authors = []
    if authors_raw:
        authors = [a.strip() for a in re.split(r'[,，;/；/]\s*', authors_raw) if a.strip()]

    # why value / 核心亮点
    why = ""
    m_why = re.search(r'(?:Why it[’\'`]s valuable|Why it’s valuable|核心亮点)(?:.*?)(?:[：:])\s*(.+?)(?:\n[A-Z][a-z]+:|\n[-*]\s|$)', block, re.S | re.I)
    if m_why:
        why = re.sub(r'\s+', ' ', m_why.group(1)).strip()[:240]

    # keywords
    keywords = []
    m_kw = re.search(r'Keywords?[:：]\s*(.+)', block, re.I)
    if m_kw:
        keywords = [k.strip() for k in re.split(r'[,，]\s*', m_kw.group(1)) if k.strip()][:4]

    # x signal
    likes = views = 0
    m_likes = re.search(r'([\d\.,]+(?:k|K|万)?)\s*(?:likes|赞)', block)
    if m_likes: likes = norm_num(m_likes.group(1))
    m_views = re.search(r'([\d\.,]+(?:k|K|万)?)\s*(?:views|浏览)', block)
    if m_views: views = norm_num(m_views.group(1))

    x_boosted = bool(re.search(r'Boosted by X mention[:：]\s*Yes|为什么火', block, re.I))

    return {
        "source": source,
        "title": title,
        "arxiv_id": arxiv_id,
        "arxiv_url": arxiv_url,
        "authors": authors,
        "authors_raw": authors_raw,
        "why_value": why,
        "keywords": keywords,
        "x_signal": {"likes": likes, "views": views},
        "x_boosted": x_boosted,
        "raw_confidence": "low"
    }

def parse_text(text: str, source: str) -> List[Dict[str, Any]]:
    out = []
    for b in split_blocks(text):
        item = parse_block(b, source)
        if item:
            out.append(item)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chatgpt", help="chatgpt raw text file")
    ap.add_argument("--grok", help="grok raw text file")
    ap.add_argument("--out", required=True, help="output normalized json")
    args = ap.parse_args()

    all_items = []
    if args.chatgpt and os.path.exists(args.chatgpt):
        all_items += parse_text(open(args.chatgpt, "r", encoding="utf-8").read(), "chatgpt")
    if args.grok and os.path.exists(args.grok):
        all_items += parse_text(open(args.grok, "r", encoding="utf-8").read(), "grok")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(all_items)} items -> {args.out}")

if __name__ == "__main__":
    main()
