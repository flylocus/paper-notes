#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import os
import re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True, help="Path to normalized_candidates.json")
    ap.add_argument("--daily", required=True, help="Path to daily-YYYYMMDD.json from RSS")
    ap.add_argument("--out-matched", required=True, help="Output path for matched papers")
    ap.add_argument("--out-unmatched", required=True, help="Output path for unmatched papers")
    args = ap.parse_args()

    with open(args.candidates, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    
    with open(args.daily, "r", encoding="utf-8") as f:
        daily_data = json.load(f)
        
    # The daily file format has "items" list, where each item has "url" and "title"
    items = daily_data.get("items", [])
    
    # Extract arxiv IDs from daily items
    daily_arxiv_ids = set()
    daily_map = {}
    for item in items:
        url = item.get("url", "")
        # Try to extract ID from URL
        m = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{5})', url)
        if m:
            arxiv_id = m.group(1)
            daily_arxiv_ids.add(arxiv_id)
            daily_map[arxiv_id] = item
            
    matched = []
    unmatched = []
    
    for cand in candidates:
        arxiv_id = cand.get("arxiv_id")
        if arxiv_id in daily_arxiv_ids:
            # Enrich candidate with truth from daily feed
            daily_item = daily_map[arxiv_id]
            cand["truth"] = {
                "title": daily_item.get("title", ""),
                "summary": daily_item.get("summary", ""),
                "category": daily_item.get("category", "")
            }
            matched.append(cand)
        else:
            unmatched.append(cand)
            
    # Write outputs
    os.makedirs(os.path.dirname(args.out_matched), exist_ok=True)
    
    with open(args.out_matched, "w", encoding="utf-8") as f:
        json.dump(matched, f, ensure_ascii=False, indent=2)
        
    with open(args.out_unmatched, "w", encoding="utf-8") as f:
        json.dump(unmatched, f, ensure_ascii=False, indent=2)
        
    print(f"Matched: {len(matched)}, Unmatched: {len(unmatched)}")
    
if __name__ == "__main__":
    main()