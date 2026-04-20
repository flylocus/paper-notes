#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch arXiv candidates for paper-notes phase1.

Currently supports direct arXiv API fetching for a category.
Future extension: ingest RSS/OPML feeds from news-daily.
"""

import argparse
import json
import os
import urllib.request
import xml.etree.ElementTree as ET

NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_arxiv(category: str, max_results: int):
    url = (
        f"https://export.arxiv.org/api/query?search_query=cat:{category}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    root = ET.fromstring(urllib.request.urlopen(url, timeout=30).read())
    out = []
    for entry in root.findall("atom:entry", NS):
        abs_url = entry.find("atom:id", NS).text.strip()
        arxiv_id = abs_url.rsplit("/", 1)[-1].replace("v1", "").replace("v2", "")
        title = entry.find("atom:title", NS).text.strip().replace("\n", " ")
        published = entry.find("atom:published", NS).text.strip()
        summary = entry.find("atom:summary", NS).text.strip().replace("\n", " ")
        categories = [c.attrib.get("term") for c in entry.findall("atom:category", NS)]
        authors = [a.find("atom:name", NS).text.strip() for a in entry.findall("atom:author", NS)]
        out.append({
            "source": "arxiv",
            "arxiv_id": arxiv_id,
            "title": title,
            "arxiv_url": abs_url.replace("http://", "https://"),
            "published": published,
            "summary": summary,
            "categories": categories,
            "authors": authors,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--category', default='cs.AI')
    ap.add_argument('--max-results', type=int, default=30)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    rows = fetch_arxiv(args.category, args.max_results)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(args.out)
    print(f"fetched={len(rows)}")


if __name__ == '__main__':
    main()
