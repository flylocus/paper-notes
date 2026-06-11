#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backfill score_rationale and evidence_ledger.json for ready outputs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
FUSED = ROOT / "fused"
PRODUCTION_SCRIPTS = ROOT / "scripts" / "production"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def arxiv_id_from_out_dir(out_dir: Path) -> str:
    return out_dir.name


def normalize_score_payload(score: dict) -> tuple[str, list[str]]:
    reason = str(score.get("reason") or score.get("rationale") or "").strip()
    source_basis = score.get("source_basis") or []
    if isinstance(source_basis, str):
        source_basis = [source_basis]
    return reason, [str(x) for x in source_basis]


def build_evidence_ledger(arxiv_id: str, metadata: dict, score: dict) -> dict:
    reason, source_basis = normalize_score_payload(score)
    return {
        "schema_version": 1,
        "paper": {
            "arxiv_id": metadata.get("arxiv_id") or arxiv_id,
            "title": metadata.get("title"),
            "link": metadata.get("abs_url") or f"https://arxiv.org/abs/{arxiv_id}",
        },
        "source_files": {
            "metadata": f"{arxiv_id}_metadata.json",
            "score": f"{arxiv_id}_score.json",
        },
        "source_basis": source_basis,
        "score_rationale": reason,
        "claim_evidence": [],
    }


def score_dimensions(score: dict) -> list[dict]:
    nested = score.get("score", {})
    if isinstance(nested, dict) and isinstance(nested.get("dimensions"), list):
        return nested.get("dimensions", [])
    if isinstance(score.get("dimensions"), list):
        return score.get("dimensions", [])
    return []


def build_score_rationale_detail(score: dict) -> dict:
    dimensions = score_dimensions(score)
    reason, _ = normalize_score_payload(score)
    if not dimensions:
        return {}
    values = []
    for dim in dimensions:
        try:
            values.append(float(dim.get("value", 0)))
        except (TypeError, ValueError):
            values.append(0.0)
    high = max(values)
    low = min(values)
    detail = []
    for dim, value in zip(dimensions, values):
        if value == high:
            role = "highest"
            role_note = "最高维，说明这篇论文最强的判断依据集中在该维度。"
        elif value == low:
            role = "lowest"
            role_note = "最低维，说明这里是评分上限的主要约束，后续复用或外推需要额外验证。"
        else:
            role = "middle"
            role_note = "中间维，说明该维度有明确支撑，但不是本篇最突出的差异点。"
        detail.append({
            "label": dim.get("label", ""),
            "value": value,
            "role": role,
            "rationale": f"{role_note} 总体依据：{reason}" if reason else role_note,
        })
    return {
        "schema_version": 1,
        "score_range": round(high - low, 2),
        "highest_dimensions": [d.get("label", "") for d, v in zip(dimensions, values) if v == high],
        "lowest_dimensions": [d.get("label", "") for d, v in zip(dimensions, values) if v == low],
        "dimension_rationales": detail,
    }


def backfill_one(out_dir: Path) -> dict:
    out_dir = out_dir.expanduser().resolve()
    arxiv_id = arxiv_id_from_out_dir(out_dir)
    metadata_path = FUSED / f"{arxiv_id}_metadata.json"
    score_path = FUSED / f"{arxiv_id}_score.json"
    generate_path = out_dir / "generate_data.json"

    actions = []
    warnings = []

    if not out_dir.exists():
        return {"out_dir": str(out_dir), "status": "missing_out_dir", "actions": [], "warnings": []}
    if not metadata_path.exists():
        warnings.append(f"missing metadata: {metadata_path}")
    if warnings:
        return {"out_dir": str(out_dir), "status": "skipped", "actions": actions, "warnings": warnings}

    metadata = load_json(metadata_path)
    generated_data = load_json(generate_path) if generate_path.exists() else {}
    if score_path.exists():
        score = load_json(score_path)
    elif generated_data.get("score"):
        score = {
            "arxiv_id": arxiv_id,
            "score": generated_data.get("score"),
            "reason": generated_data.get("score_rationale", ""),
            "source_basis": [
                f"Fallback score reconstructed from {generate_path.name}",
                f"Missing fused score file: {score_path.name}",
            ] + [str(x) for x in generated_data.get("discussion_notes", []) if isinstance(generated_data.get("discussion_notes"), list)],
        }
        warnings.append(f"missing score, used generate_data.json fallback: {score_path}")
    else:
        warnings.append(f"missing score: {score_path}")
        return {"out_dir": str(out_dir), "status": "skipped", "actions": actions, "warnings": warnings}
    reason, source_basis = normalize_score_payload(score)
    ledger = build_evidence_ledger(arxiv_id, metadata, score)
    score_detail = build_score_rationale_detail(score)

    write_json(out_dir / "evidence_ledger.json", ledger)
    actions.append("write:evidence_ledger.json")

    if generate_path.exists():
        data = generated_data
        changed = False
        if reason and not str(data.get("score_rationale", "")).strip():
            data["score_rationale"] = reason
            changed = True
        if score_detail and data.get("score_rationale_detail") != score_detail:
            data["score_rationale_detail"] = score_detail
            changed = True
        if source_basis and not data.get("evidence_ledger"):
            data["evidence_ledger"] = ledger
            changed = True
        if changed:
            write_json(generate_path, data)
            actions.append("update:generate_data.json")
    else:
        warnings.append(f"missing generate_data.json: {generate_path}")

    return {"out_dir": str(out_dir), "status": "updated", "actions": actions, "warnings": warnings}


def discover_outputs(date_from: str | None, date_to: str | None) -> list[Path]:
    ready = ROOT / "outputs" / "ready"
    paths = []
    for date_dir in sorted(ready.iterdir()):
        if not date_dir.is_dir() or not date_dir.name.isdigit():
            continue
        if date_from and date_dir.name < date_from:
            continue
        if date_to and date_dir.name > date_to:
            continue
        for out_dir in sorted(p for p in date_dir.iterdir() if p.is_dir()):
            paths.append(out_dir)
    return paths


def run_qa(out_dir: Path) -> int:
    return subprocess.run(
        [
            sys.executable,
            str(PRODUCTION_SCRIPTS / "qa_check.py"),
            "--out-dir",
            str(out_dir),
            "--mode",
            "publish",
        ],
        check=False,
    ).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill evidence ledger and score rationale")
    ap.add_argument("--out-dir", action="append", default=[])
    ap.add_argument("--date-from")
    ap.add_argument("--date-to")
    ap.add_argument("--run-qa", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    targets = [Path(p) for p in args.out_dir]
    if not targets:
        targets = discover_outputs(args.date_from, args.date_to)
    if not targets:
        print("no output directories selected", file=sys.stderr)
        return 2

    results = []
    exit_code = 0
    for out_dir in targets:
        result = backfill_one(out_dir)
        if args.run_qa and result["status"] == "updated":
            result["qa_exit_code"] = run_qa(Path(result["out_dir"]))
            if result["qa_exit_code"] != 0:
                exit_code = 1
        results.append(result)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['status']}: {result['out_dir']}")
            for action in result["actions"]:
                print(f"  - {action}")
            for warning in result["warnings"]:
                print(f"  ! {warning}")
            if "qa_exit_code" in result:
                print(f"  qa_exit_code={result['qa_exit_code']}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
