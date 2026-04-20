#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paper-Notes Phase 1: Parse ChatGPT/Grok inputs, fetch arXiv candidates, merge, dedupe, and rank.

Ranking principle:
- curated human/LLM picks (ChatGPT/Grok) should outrank raw arXiv-only papers
- ToB / Agent / workflow / benchmark / reasoning fit should outrank freshness
- raw arXiv recency is auxiliary, not dominant
"""

import os
import json
import re
import argparse
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUTS_DIR = os.path.join(ROOT, "inputs")
FUSED_DIR = os.path.join(ROOT, "fused")
SCRIPTS_DIR = os.path.join(ROOT, "scripts", "production")


FIT_TERMS = [
    'agent', 'service', 'workflow', 'benchmark', 'evaluation', 'reasoning',
    'tool', 'sop', 'graph', 'reliability', 'human-in-the-loop', 'process',
    'enterprise', 'customer support', 'ticketing', 'process navigation'
]
NEGATIVE_TERMS = [
    'vehicle routing', 'quantum', 'medical imaging', 'ct', 'vision-language modeling'
]


def parse_chatgpt_input(text):
    papers = []
    entries = re.split(r'\n(?=\d+\))', text)
    for entry in entries:
        if not entry.strip() or not re.match(r'\d+\)', entry.strip()):
            continue
        lines = entry.strip().split('\n')
        title_match = re.match(r'\d+\)\s+(.+)', lines[0])
        if not title_match:
            continue
        title = title_match.group(1).strip()
        arxiv_id = None
        why_valuable = ""
        keywords = []
        for line in lines:
            m = re.search(r'arXiv:\s*(\d{4}\.\d+)', line)
            if m:
                arxiv_id = m.group(1)
            if 'Why valuable' in line or '为什么' in line:
                why_valuable = line.split(':', 1)[-1].strip() if ':' in line else ""
            if 'Keywords' in line or '关键词' in line:
                kw_text = line.split(':', 1)[-1].strip() if ':' in line else ""
                keywords = [k.strip() for k in kw_text.split(',') if k.strip()]
        if arxiv_id:
            papers.append({
                'source': 'chatgpt',
                'title': title,
                'arxiv_id': arxiv_id,
                'arxiv_url': f'https://arxiv.org/abs/{arxiv_id}',
                'why_value': why_valuable,
                'keywords': keywords,
            })
    return papers


def parse_grok_input(text):
    papers = []
    blocks = re.split(r'\n(?=\*\*\d+\.)|\n(?=\d+\.)', text)
    for entry in blocks:
        m_id = re.search(r'https?://arxiv.org/abs/(\d{4}\.\d+)|arXiv[:：]\s*(\d{4}\.\d+)', entry)
        if not m_id:
            continue
        arxiv_id = m_id.group(1) or m_id.group(2)
        lines = [x.strip('* ').strip() for x in entry.splitlines() if x.strip()]
        title = lines[0] if lines else arxiv_id
        title = re.sub(r'^\d+\.?\s*', '', title).strip()
        why_value = ''
        m_why = re.search(r'为什么火[^:：]*[:：]\s*(.+)', entry)
        if m_why:
            why_value = m_why.group(1).strip()
        keywords = []
        m_kw = re.search(r'Keywords[:：]\s*(.+)', entry)
        if m_kw:
            keywords = [k.strip() for k in m_kw.group(1).split(',') if k.strip()]
        papers.append({
            'source': 'grok',
            'title': title,
            'arxiv_id': arxiv_id,
            'arxiv_url': f'https://arxiv.org/abs/{arxiv_id}',
            'why_value': why_value,
            'keywords': keywords,
        })
    return papers


def merge_rows(rows):
    merged = {}
    for r in rows:
        aid = r['arxiv_id']
        if aid not in merged:
            merged[aid] = r.copy()
            merged[aid]['sources'] = [r['source']]
        else:
            merged[aid]['sources'].append(r['source'])
            for k in ['why_value', 'summary']:
                if not merged[aid].get(k) and r.get(k):
                    merged[aid][k] = r[k]
            if not merged[aid].get('keywords') and r.get('keywords'):
                merged[aid]['keywords'] = r['keywords']
            for k in ['published', 'categories', 'authors']:
                if r.get(k):
                    merged[aid][k] = r[k]
    for v in merged.values():
        v['sources'] = sorted(list(set(v['sources'])))
    return list(merged.values())


def candidate_score(x):
    text = ' '.join([
        x.get('title', ''), x.get('why_value', ''), ' '.join(x.get('keywords', [])), x.get('summary', '')
    ]).lower()
    cats = x.get('categories', [])
    sources = x.get('sources', [])

    score = 0

    # strongest signal: curated picks
    if 'chatgpt' in sources:
        score += 5
    if 'grok' in sources:
        score += 4
    if 'chatgpt' in sources and 'grok' in sources:
        score += 4

    # arxiv is verification / pool source, not a main ranking boost
    if 'arxiv' in sources:
        score += 1

    # fit to project
    if 'cs.AI' in cats:
        score += 2
    if any(term in text for term in FIT_TERMS):
        score += 4
    if any(term in text for term in ['service', 'workflow', 'sop', 'graph', 'reliability', 'enterprise', 'customer support', 'ticketing', 'process navigation']):
        score += 4
    if any(term in text for term in ['service agent', 'customer service', 'graph-guided', 'dynamic dialogue graph', 'sop compliance', 'industrial scenario']):
        score += 4
    if any(term in text for term in ['benchmark', 'evaluation']):
        score += 2
    if any(term in text for term in ['agent', 'reasoning', 'tool']):
        score += 2

    # penalties for poor fit
    if any(term in text for term in NEGATIVE_TERMS):
        score -= 4

    # slight preference for richer human explanation
    if x.get('why_value'):
        score += 1
    if x.get('keywords'):
        score += 1

    # tiny freshness signal only
    if x.get('published', '').startswith('2026-04'):
        score += 0.5

    return score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default=datetime.now().strftime('%Y%m%d'))
    ap.add_argument('--category', default='cs.AI')
    ap.add_argument('--max-results', type=int, default=30)
    args = ap.parse_args()

    os.makedirs(FUSED_DIR, exist_ok=True)

    chatgpt_file = os.path.join(INPUTS_DIR, 'chatgpt', f'{args.date}.txt')
    grok_file = os.path.join(INPUTS_DIR, 'grok', f'{args.date}.txt')
    arxiv_file = os.path.join(FUSED_DIR, f'arxiv_candidates_{args.date}.json')

    subprocess.run([
        sys.executable, os.path.join(SCRIPTS_DIR, 'fetch_candidates.py'),
        '--category', args.category,
        '--max-results', str(args.max_results),
        '--out', arxiv_file,
    ], check=True)

    with open(chatgpt_file, 'r', encoding='utf-8') as f:
        chatgpt_text = f.read()
    with open(grok_file, 'r', encoding='utf-8') as f:
        grok_text = f.read()
    with open(arxiv_file, 'r', encoding='utf-8') as f:
        arxiv_rows = json.load(f)

    rows = parse_chatgpt_input(chatgpt_text) + parse_grok_input(grok_text) + arxiv_rows
    merged = merge_rows(rows)

    for x in merged:
        x['candidate_score'] = candidate_score(x)

    merged.sort(key=lambda z: (z['candidate_score'], len(z.get('sources', []))), reverse=True)

    out1 = os.path.join(FUSED_DIR, f'candidates_{args.date}.json')
    out2 = os.path.join(FUSED_DIR, f'top_ranked_{args.date}.json')
    with open(out1, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    with open(out2, 'w', encoding='utf-8') as f:
        json.dump(merged[:10], f, ensure_ascii=False, indent=2)

    print(out1)
    print(out2)
    print('\n[Top 3 Recommended]')
    for i, x in enumerate(merged[:3], 1):
        print(f"{i}. {x['arxiv_id']} | score={x['candidate_score']} | {x['title']}")
        print(f"   sources={','.join(x.get('sources', []))}")


if __name__ == '__main__':
    main()
