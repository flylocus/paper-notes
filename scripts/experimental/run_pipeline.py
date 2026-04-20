#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main Coordinator for Paper Notes Pipeline"""

import os
import sys
import json
import argparse
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
FUSED_DIR = os.path.join(ROOT, "fused")
RENDERED_DIR = os.path.join(ROOT, "rendered")

def fetch_arxiv_data(arxiv_id):
    """Fetch accurate metadata from arXiv API."""
    print(f"[*] Fetching arXiv data for {arxiv_id}...")
    url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    try:
        response = urllib.request.urlopen(url)
        root = ET.fromstring(response.read())
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entry = root.find('atom:entry', ns)
        if not entry:
            return None
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        return {"title": title, "summary": summary, "authors": authors}
    except Exception as e:
        print(f"[-] ArXiv fetch failed: {e}")
        return None

def merge_and_rank(candidates):
    """Merge entries with same arxiv_id and rank by likes."""
    merged = {}
    for c in candidates:
        aid = c["arxiv_id"]
        if aid not in merged:
            merged[aid] = c
        else:
            # Merge logic: keep highest likes, combine text if needed
            existing = merged[aid]
            if c["x_signal"]["likes"] > existing["x_signal"]["likes"]:
                existing["x_signal"] = c["x_signal"]
            if not existing["why_value"] and c["why_value"]:
                existing["why_value"] = c["why_value"]
            if not existing["keywords"] and c["keywords"]:
                existing["keywords"] = c["keywords"]
    
    # Sort by likes descending
    ranked = list(merged.values())
    ranked.sort(key=lambda x: x.get("x_signal", {}).get("likes", 0), reverse=True)
    return ranked

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chatgpt", required=True, help="Path to raw ChatGPT input")
    ap.add_argument("--grok", required=True, help="Path to raw Grok input")
    args = ap.parse_args()

    os.makedirs(FUSED_DIR, exist_ok=True)
    os.makedirs(RENDERED_DIR, exist_ok=True)

    norm_json = os.path.join(FUSED_DIR, "normalized_candidates.json")

    # 1. Normalize
    print("[1] Running normalization...")
    subprocess.run([
        sys.executable, os.path.join(SCRIPTS_DIR, "normalize_input.py"),
        "--chatgpt", args.chatgpt,
        "--grok", args.grok,
        "--out", norm_json
    ], check=True)

    with open(norm_json, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    
    if not candidates:
        print("[-] No candidates found.")
        return

    # 2. Rank
    ranked = merge_and_rank(candidates)
    top_paper = ranked[0]
    print(f"[2] Top paper selected: {top_paper['title']} (Likes: {top_paper['x_signal']['likes']})")

    # 3. Fetch Truth from ArXiv
    arxiv_data = fetch_arxiv_data(top_paper["arxiv_id"])
    if arxiv_data:
        real_title = arxiv_data["title"]
        real_authors = arxiv_data["authors"]
        abstract = arxiv_data["summary"]
    else:
        real_title = top_paper["title"]
        real_authors = top_paper.get("authors", ["Unknown"])
        abstract = ""

    # 4. Construct Payloads
    print("[3] Constructing payloads...")
    # Generate a dummy short title and chinese title for demonstration (should be from LLM in future)
    short_title = real_title.split(":")[0] if ":" in real_title else real_title[:30]
    
    # Static scores for automation demo
    total_score = 9.0
    
    card_payload = {
        "paper_title": short_title,
        "score": {
            "total": total_score,
            "dimensions": [
                {"label": "重要性 Impact", "value": 2.0},
                {"label": "创新性 Novelty", "value": 1.8},
                {"label": "可验证性 Evidence", "value": 1.7},
                {"label": "产业可用性 Applicability", "value": 1.9},
                {"label": "可复用性 Reusability", "value": 1.6}
            ]
        },
        "info": {
            "title": real_title,
            "title_cn": "前沿研究论文速记", # Placeholder for Chinese translation
            "link": top_paper["arxiv_url"],
            "authors": real_authors,
            "affiliations": ["Community Verified"]
        }
    }
    
    article_payload = {
        **card_payload,
        "A_research_problem": abstract[:200] + "..." if abstract else top_paper.get("why_value", ""),
        "B_core_contributions": [top_paper.get("why_value", "No explicit contribution parsed.")],
        "C_method_framework": "Refer to the original paper methodology.",
        "D_key_results": ["Significant improvements reported."],
        "E_industry_implications": ["High relevance to current production challenges."],
        "F_one_line_judgement": "值得深入阅读，具备落地潜力。",
        "discussion_notes": [f"X.com metrics: {top_paper['x_signal']['likes']} likes, {top_paper['x_signal']['views']} views."]
    }

    card_path = os.path.join(FUSED_DIR, "card_payload.json")
    article_path = os.path.join(FUSED_DIR, "article_payload.json")
    
    with open(card_path, "w", encoding="utf-8") as f:
        json.dump(card_payload, f, ensure_ascii=False, indent=2)
    with open(article_path, "w", encoding="utf-8") as f:
        json.dump(article_payload, f, ensure_ascii=False, indent=2)

    # 5. Render Everything
    print("[4] Generating assets...")
    subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "generate_cards.py"), "--data", card_path, "--out", RENDERED_DIR], check=True)
    subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "generate_cover.py"), "--data", card_path, "--out", os.path.join(RENDERED_DIR, "cover_235.png")], check=True)
    subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "generate_article.py")], check=True)

    print("\n[✔] Pipeline Complete! Assets generated in:", RENDERED_DIR)
    print("  - article.md")
    print("  - cover_235.png")
    print("  - info_card.png")
    print("  - score_card.png")

if __name__ == "__main__":
    main()