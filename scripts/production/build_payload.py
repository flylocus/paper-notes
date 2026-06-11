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


def build_evidence_ledger(meta, score, metadata_path, score_path):
    source_basis = score.get('source_basis', [])
    ledger = {
        'schema_version': 1,
        'paper': {
            'arxiv_id': meta.get('arxiv_id'),
            'title': meta.get('title'),
            'link': meta.get('abs_url'),
        },
        'source_files': {
            'metadata': os.path.basename(metadata_path),
            'score': os.path.basename(score_path),
        },
        'source_basis': source_basis,
        'score_rationale': score.get('reason') or score.get('rationale') or '',
        'claim_evidence': [],
    }
    return ledger


def score_dimensions(score):
    nested = score.get('score', {})
    if isinstance(nested, dict) and isinstance(nested.get('dimensions'), list):
        return nested.get('dimensions', [])
    if isinstance(score.get('dimensions'), list):
        return score.get('dimensions', [])
    return []


def build_score_rationale_detail(score):
    dimensions = score_dimensions(score)
    rationale = score.get('reason') or score.get('rationale') or ''
    if not dimensions:
        return {}
    values = [float(d.get('value', 0) or 0) for d in dimensions]
    high = max(values)
    low = min(values)
    dimension_rationales = []
    for dim in dimensions:
        value = dim.get('value', 0)
        label = dim.get('label', '')
        if value == high:
            role = 'highest'
            role_note = '最高维，说明这篇论文最强的判断依据集中在该维度。'
        elif value == low:
            role = 'lowest'
            role_note = '最低维，说明这里是评分上限的主要约束，后续复用或外推需要额外验证。'
        else:
            role = 'middle'
            role_note = '中间维，说明该维度有明确支撑，但不是本篇最突出的差异点。'
        dimension_rationales.append({
            'label': label,
            'value': value,
            'role': role,
            'rationale': f"{role_note} 总体依据：{rationale}" if rationale else role_note,
        })
    return {
        'schema_version': 1,
        'score_range': round(high - low, 2),
        'highest_dimensions': [d.get('label', '') for d in dimensions if d.get('value', 0) == high],
        'lowest_dimensions': [d.get('label', '') for d in dimensions if d.get('value', 0) == low],
        'dimension_rationales': dimension_rationales,
    }


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
            'total': round(score['score']['total_score'], 1),
            'dimensions': score['score']['dimensions']
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
    score_rationale = score.get('reason') or score.get('rationale')
    if score_rationale:
        article_payload['score_rationale'] = score_rationale
    score_rationale_detail = build_score_rationale_detail(score)
    if score_rationale_detail:
        article_payload['score_rationale_detail'] = score_rationale_detail
    evidence_ledger = build_evidence_ledger(meta, score, args.metadata, args.score)
    if score.get('source_basis') or score.get('reason'):
        article_payload['evidence_ledger'] = evidence_ledger

    os.makedirs(args.out_dir, exist_ok=True)
    card_out = os.path.join(args.out_dir, f"{args.paper_key}_card_payload_{args.date}.json")
    article_out = os.path.join(args.out_dir, f"{args.paper_key}_article_payload_{args.date}.json")
    evidence_out = os.path.join(args.out_dir, f"{args.paper_key}_evidence_ledger_{args.date}.json")

    with open(card_out, 'w', encoding='utf-8') as f:
        json.dump(card_payload, f, ensure_ascii=False, indent=2)
    with open(article_out, 'w', encoding='utf-8') as f:
        json.dump(article_payload, f, ensure_ascii=False, indent=2)
    with open(evidence_out, 'w', encoding='utf-8') as f:
        json.dump(evidence_ledger, f, ensure_ascii=False, indent=2)

    print(card_out)
    print(article_out)
    print(evidence_out)


if __name__ == '__main__':
    main()
