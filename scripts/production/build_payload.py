#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build standardized card/article payloads from verified metadata + scoring.

Usage:
  python3 build_payload.py \
    --metadata fused/2604.09285_metadata.json \
    --score fused/2604.09285_score.json \
    --paper-key sage \
    --date 20260415 \
    --title-cn "SAGE：面向服务型 Agent 的图引导评测基准" \
    --out-dir fused
"""

import argparse
import json
import os


def flatten_items(items):
    if not items:
        return []
    return [x for group in items for x in group]


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metadata', required=True)
    ap.add_argument('--score', required=True)
    ap.add_argument('--paper-key', required=True)
    ap.add_argument('--date', required=True)
    ap.add_argument('--title-cn', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--one-line', default='这是一篇值得关注的论文。')
    ap.add_argument('--research-problem', default='待补充')
    ap.add_argument('--method-framework', default='待补充')
    ap.add_argument('--industry-implications', nargs='+', action='append', default=[])
    ap.add_argument('--core-contributions', nargs='+', action='append', default=[])
    ap.add_argument('--key-results', nargs='+', action='append', default=[])
    args = ap.parse_args()

    meta = load_json(args.metadata)
    score = load_json(args.score)

    title = meta['title']
    short_title = args.paper_key.upper()

    card_payload = {
        'paper_title': short_title,
        'score': {
            'total': round(score['total_score'], 1),
            'dimensions': score['dimensions']
        },
        'info': {
            'title': title,
            'title_cn': args.title_cn,
            'link': meta['abs_url'],
            'authors': meta.get('authors', []),
            'affiliations': meta.get('affiliations', [])
        }
    }

    article_payload = {
        **card_payload,
        'A_research_problem': args.research_problem,
        'B_core_contributions': flatten_items(args.core_contributions),
        'C_method_framework': args.method_framework,
        'D_key_results': flatten_items(args.key_results),
        'E_industry_implications': flatten_items(args.industry_implications),
        'F_one_line_judgement': args.one_line,
        'discussion_notes': [
            f"Generated from verified metadata: {os.path.basename(args.metadata)}",
            f"Generated from score file: {os.path.basename(args.score)}"
        ]
    }

    os.makedirs(args.out_dir, exist_ok=True)
    card_out = os.path.join(args.out_dir, f"{args.paper_key}_card_payload_{args.date}.json")
    article_out = os.path.join(args.out_dir, f"{args.paper_key}_article_payload_{args.date}.json")

    with open(card_out, 'w', encoding='utf-8') as f:
        json.dump(card_payload, f, ensure_ascii=False, indent=2)
    with open(article_out, 'w', encoding='utf-8') as f:
        json.dump(article_payload, f, ensure_ascii=False, indent=2)

    print(card_out)
    print(article_out)


if __name__ == '__main__':
    main()
