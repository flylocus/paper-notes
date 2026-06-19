# DeepSeek API Layer for paper-notes

This layer is opt-in. It drafts structured JSON artifacts for the existing local production flow; it does not replace metadata verification, PDF evidence checks, rendering, QA, or `make standardize`.

## Models

- `deepseek-v4-flash`: default for high-volume draft work.
- `deepseek-v4-pro`: default for final review and high-risk judgment.

Use the current V4 model names. Do not add new automation on legacy names such as `deepseek-chat` or `deepseek-reasoner`.

## Secret Handling

Set the API key in the environment:

```bash
export DEEPSEEK_API_KEY='...'
```

Optional overrides:

```bash
export DEEPSEEK_BASE_URL='https://api.deepseek.com'
export DEEPSEEK_TIMEOUT_SECONDS=120
```

Do not write API keys to repo files, task cards, output bundles, or memory files.

## Stage Split

### 1. Candidate Enrichment

Run after `make phase1`:

```bash
make deepseek-candidates DATE=20260620
```

Equivalent:

```bash
python3 scripts/production/deepseek_paper_notes.py enrich-candidates --date 20260620
```

Output:

```text
fused/deepseek_candidate_notes_20260620.json
```

Use this to speed up Top 3 discussion. It is advisory only; still check `outputs/READY_INDEX.md` and verify the selected paper manually.

### 2. Payload Patch Draft

Run after metadata and score files exist:

```bash
make deepseek-payload DATE=20260620 ARXIV_ID=2606.xxxxx
```

Equivalent:

```bash
python3 scripts/production/deepseek_paper_notes.py draft-payload \
  --date 20260620 \
  --arxiv-id 2606.xxxxx \
  --metadata fused/2606.xxxxx_metadata.json \
  --score fused/2606.xxxxx_score.json
```

Optional full text excerpt:

```bash
python3 scripts/production/deepseek_paper_notes.py draft-payload \
  --date 20260620 \
  --arxiv-id 2606.xxxxx \
  --metadata fused/2606.xxxxx_metadata.json \
  --score fused/2606.xxxxx_score.json \
  --full-text /path/to/pdf_text.txt
```

Output:

```text
fused/2606.xxxxx_deepseek_payload_patch_20260620.json
```

Expected use: manually merge useful fields into `outputs/ready/YYYYMMDD/<id>/generate_data.json`, then rerender and run QA.

### 3. Final Reviewer

Run after a publish bundle exists:

```bash
make deepseek-review DATE=20260620 OUT_DIR=/Users/shenfei/clawd/paper-notes/outputs/ready/20260620/2606.xxxxx
```

Equivalent:

```bash
python3 scripts/production/deepseek_paper_notes.py review-output \
  --date 20260620 \
  --out-dir outputs/ready/20260620/2606.xxxxx
```

Output:

```text
fused/2606.xxxxx_deepseek_review_20260620.json
```

Treat `P0` and `P1` review findings as editorial blockers until resolved or explicitly rejected.

## Dry Runs

Print the API request without calling DeepSeek:

```bash
python3 scripts/production/deepseek_paper_notes.py enrich-candidates --date 20260620 --print-prompt
```

Test parsing/writing with a local response:

```bash
python3 scripts/production/deepseek_paper_notes.py review-output \
  --date 20260620 \
  --out-dir outputs/ready/20260619/2606.19319 \
  --mock-response /path/to/mock_review.json
```

## Guardrails

- Missing same-day ChatGPT/Grok inputs still stop `phase1`.
- DeepSeek output must not overwrite `generate_data.json` automatically.
- Strong claims still need `evidence_ledger.json` / `claim_evidence`.
- Final publish readiness still requires `make qa OUT_DIR=... MODE=publish`.
