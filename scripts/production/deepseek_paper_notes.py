#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opt-in DeepSeek draft helpers for paper-notes.

The outputs from this script are draft artifacts. Existing metadata checks,
payload editing, rendering, QA, and standardization remain authoritative.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from deepseek_client import chat_completion, completion_text, parse_json_object
except ImportError:  # pragma: no cover - supports direct module execution variants.
    from scripts.production.deepseek_client import chat_completion, completion_text, parse_json_object


ROOT = Path(__file__).resolve().parents[2]
FUSED = ROOT / "fused"

FLASH = "deepseek-v4-flash"
PRO = "deepseek-v4-pro"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path, max_chars: int | None = None) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n\n[TRUNCATED]"
    return text


def compact_json(data: Any, max_chars: int = 60000) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if len(text) > max_chars:
        return text[:max_chars] + "\n... [TRUNCATED]"
    return text


def default_candidate_input(date: str) -> Path:
    top_ranked = FUSED / f"top_ranked_{date}.json"
    if top_ranked.exists():
        return top_ranked
    return FUSED / f"candidates_{date}.json"


def infer_arxiv_id_from_out_dir(out_dir: Path) -> str:
    name = out_dir.resolve().name
    return name if name.count(".") == 1 else "unknown"


def build_messages(task: str, payload: dict[str, Any]) -> list[dict[str, str]]:
    system = (
        "你是 paper-notes 的 DeepSeek 辅助层。只输出 JSON 对象，不要 Markdown。"
        "你只能基于输入材料生成候选建议，不得伪造论文数据、benchmark、作者单位或实验数字。"
        "强判断必须保留 evidence_required 或 evidence 字段，方便本地 QA 和人工核验。"
    )
    user = f"任务：{task}\n\n输入 JSON：\n{compact_json(payload)}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def call_or_mock(args: argparse.Namespace, messages: list[dict[str, str]], model: str, *, pro: bool = False) -> dict[str, Any]:
    if args.mock_response:
        return parse_json_object(read_text(Path(args.mock_response)))
    if args.print_prompt:
        print(json.dumps({"model": model, "messages": messages}, ensure_ascii=False, indent=2))
        return {"prompt_only": True}
    response = chat_completion(
        messages=messages,
        model=model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        thinking="enabled" if pro and getattr(args, "thinking", False) else "disabled",
        reasoning_effort=args.reasoning_effort if pro and getattr(args, "thinking", False) else None,
        retries=args.retries,
    )
    return parse_json_object(completion_text(response))


def enrich_candidates(args: argparse.Namespace) -> int:
    input_path = Path(args.input) if args.input else default_candidate_input(args.date)
    candidates = load_json(input_path)
    if not isinstance(candidates, list):
        raise SystemExit(f"candidate input must be a JSON array: {input_path}")
    selected = candidates[: args.limit]
    payload = {
        "date": args.date,
        "source_file": str(input_path),
        "expected_output": {
            "candidate_notes": [
                {
                    "arxiv_id": "string",
                    "fit_summary": "为什么适合 paper-notes 的一句话判断",
                    "tags": ["ToB", "Agent", "Workflow"],
                    "risk_flags": ["可能不适合的原因"],
                    "recommended_next_step": "select|skip|verify_pdf",
                }
            ]
        },
        "candidates": selected,
    }
    messages = build_messages(
        "为候选论文补充 ToB/Agent/Workflow 适配理由、风险标记和下一步建议。",
        payload,
    )
    result = call_or_mock(args, messages, args.model)
    if result.get("prompt_only"):
        return 0
    result.setdefault("schema_version", 1)
    result.setdefault("source_file", str(input_path))
    result.setdefault("model", args.model)
    out = Path(args.out) if args.out else FUSED / f"deepseek_candidate_notes_{args.date}.json"
    write_json(out, result)
    print(out)
    return 0


def draft_payload(args: argparse.Namespace) -> int:
    metadata = load_json(Path(args.metadata))
    score = load_json(Path(args.score))
    full_text = read_text(Path(args.full_text), args.max_source_chars) if args.full_text else ""
    payload = {
        "date": args.date,
        "arxiv_id": args.arxiv_id,
        "metadata": metadata,
        "score": score,
        "full_text_excerpt": full_text,
        "expected_output": {
            "title_cn": "中文标题建议",
            "one_line": "F 段一句话判断，必须包含限制面",
            "payload_patch": {
                "glossary": [{"term": "string", "explanation": "string"}],
                "method_subsections": [{"title": "string", "body": "string"}],
                "result_table": {"columns": ["维度"], "rows": [{"维度": "结果"}]},
                "source_notes": ["数据来源说明"],
                "so_what": "D 段结果的 So What",
                "feige_view": "ToB/销售视角",
                "limitations": [{"title": "限制", "body": "解释"}],
            },
            "score_revision_notes": ["评分是否需要调整及证据"],
            "evidence_required": ["每个强判断需要回查的 PDF 位置"],
        },
    }
    messages = build_messages(
        "基于已核验 metadata/score 和可选全文摘录，生成 generate_data.json 的结构化补丁草稿。",
        payload,
    )
    result = call_or_mock(args, messages, args.model)
    if result.get("prompt_only"):
        return 0
    result.setdefault("schema_version", 1)
    result.setdefault("arxiv_id", args.arxiv_id)
    result.setdefault("model", args.model)
    out = Path(args.out) if args.out else FUSED / f"{args.arxiv_id}_deepseek_payload_patch_{args.date}.json"
    write_json(out, result)
    print(out)
    return 0


def review_output(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir).resolve()
    data: dict[str, Any] = {"out_dir": str(out_dir)}
    for name in ["generate_data.json", "evidence_ledger.json", "qa_report.json", "preflight_report.json"]:
        path = out_dir / name
        if path.exists():
            data[name] = load_json(path)
    for name in ["note.md", "publish_pack.md"]:
        path = out_dir / name
        if path.exists():
            data[name] = read_text(path, args.max_source_chars)
    payload = {
        "arxiv_id": args.arxiv_id or infer_arxiv_id_from_out_dir(out_dir),
        "review_target": data,
        "expected_output": {
            "verdict": "pass|needs_fix|block",
            "issues": [
                {
                    "severity": "P0|P1|P2",
                    "field": "generate_data.json path or article section",
                    "problem": "问题描述",
                    "fix": "建议修复",
                    "evidence_check": "需要回查的 PDF/table/section",
                }
            ],
            "ready_to_publish": False,
        },
    }
    messages = build_messages(
        "做发布前 reviewer：只找虚构、过度外推、术语未解释、So What 空泛、F 段缺限制面、claim-evidence 不足等问题。",
        payload,
    )
    result = call_or_mock(args, messages, args.model, pro=True)
    if result.get("prompt_only"):
        return 0
    result.setdefault("schema_version", 1)
    result.setdefault("model", args.model)
    result.setdefault("out_dir", str(out_dir))
    arxiv_id = args.arxiv_id or infer_arxiv_id_from_out_dir(out_dir)
    out = Path(args.out) if args.out else FUSED / f"{arxiv_id}_deepseek_review_{args.date}.json"
    write_json(out, result)
    print(out)
    return 0


def add_common(ap: argparse.ArgumentParser, *, default_model: str) -> None:
    ap.add_argument("--model", default=default_model)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--mock-response", help="Read a local JSON response instead of calling the API")
    ap.add_argument("--print-prompt", action="store_true", help="Print request payload without calling the API")


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepSeek draft helpers for paper-notes")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("enrich-candidates", help="Draft candidate fit notes from top_ranked/candidates JSON")
    p.add_argument("--date", required=True)
    p.add_argument("--input")
    p.add_argument("--out")
    p.add_argument("--limit", type=int, default=10)
    add_common(p, default_model=FLASH)
    p.set_defaults(func=enrich_candidates)

    p = sub.add_parser("draft-payload", help="Draft structured generate_data.json patch fields")
    p.add_argument("--date", required=True)
    p.add_argument("--arxiv-id", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--score", required=True)
    p.add_argument("--full-text")
    p.add_argument("--max-source-chars", type=int, default=60000)
    p.add_argument("--out")
    add_common(p, default_model=FLASH)
    p.set_defaults(func=draft_payload)

    p = sub.add_parser("review-output", help="Review an output directory for publish-risk issues")
    p.add_argument("--date", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--arxiv-id")
    p.add_argument("--max-source-chars", type=int, default=60000)
    p.add_argument("--out")
    p.add_argument("--no-thinking", action="store_false", dest="thinking", default=True)
    p.add_argument("--reasoning-effort", default="high")
    add_common(p, default_model=PRO)
    p.set_defaults(func=review_output)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
