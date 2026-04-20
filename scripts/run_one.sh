#!/usr/bin/env bash
set -euo pipefail

# One-shot helper to generate paper-notes deliverables into a per-paper subdir.
# Usage:
#   ./scripts/run_one.sh --arxiv 2602.18456 --title "..." --authors "A;B" --aff "Org1;Org2" \
#     --score "8.2" --dims "1.9,1.4,1.6,1.8,1.5" --keywords "k1,k2,k3" --domain "Agent评测|安全与可靠性" --vol 011 --date 2026-02-25

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_BASE="$ROOT_DIR/outputs"

arxiv=""; title=""; authors=""; aff=""; score=""; dims=""; keywords=""; domain=""; vol=""; date=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arxiv) arxiv="$2"; shift 2;;
    --title) title="$2"; shift 2;;
    --authors) authors="$2"; shift 2;;
    --aff) aff="$2"; shift 2;;
    --score) score="$2"; shift 2;;
    --dims) dims="$2"; shift 2;;
    --keywords) keywords="$2"; shift 2;;
    --domain) domain="$2"; shift 2;;
    --vol) vol="$2"; shift 2;;
    --date) date="$2"; shift 2;;
    -h|--help) sed -n '1,40p' "$0"; exit 0;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

[[ -n "$arxiv" && -n "$title" && -n "$score" && -n "$dims" ]] || {
  echo "Missing required args. Need --arxiv --title --score --dims"; exit 2; }

out_dir="$OUT_BASE/$arxiv"
mkdir -p "$out_dir"

authors_json=$(python3 - <<PY
import json
s=${authors@Q}
arr=[a.strip() for a in s.split(';') if a.strip()]
print(json.dumps(arr,ensure_ascii=False))
PY
)

aff_json=$(python3 - <<PY
import json
s=${aff@Q}
arr=[a.strip() for a in s.split(';') if a.strip()]
print(json.dumps(arr,ensure_ascii=False))
PY
)

python3 - <<PY
import json
from pathlib import Path
arxiv=${arxiv@Q}
title=${title@Q}
score=float(${score@Q})
dims=${dims@Q}
authors=json.loads('''$authors_json''')
aff=json.loads('''$aff_json''')
vals=[float(x.strip()) for x in dims.split(',') if x.strip()]
if len(vals)!=5:
  raise SystemExit('dims must be 5 comma-separated numbers: importance,novelty,verifiability,industry,reusability')

out={
  'paper_title': title,
  'score': {
    'total': score,
    'dimensions': [
      {'label':'重要性 Impact','value': vals[0]},
      {'label':'创新性 Novelty','value': vals[1]},
      {'label':'可验证性 Evidence','value': vals[2]},
      {'label':'产业可用性 Applicability','value': vals[3]},
      {'label':'可复用性 Reusability','value': vals[4]},
    ]
  },
  'info': {
    'title': '论文标题',
    'link': f'https://arxiv.org/abs/{arxiv}',
    'authors': authors,
    'affiliations': aff or ['—']
  }
}
Path(r'''$out_dir/data.json''').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('WROTE',r'''$out_dir/data.json''')
PY

python3 "$ROOT_DIR/scripts/generate_cards.py" --data "$out_dir/data.json" --out "$out_dir"

python3 "$ROOT_DIR/scripts/generate_cover.py" \
  --data "$out_dir/data.json" \
  --keywords "$keywords" \
  --domain "$domain" \
  --out "$out_dir"

echo "DONE: $out_dir"
ls -la "$out_dir" | sed -n '1,120p'
