#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit drift between generate_data.json (payload) and the shipped artifacts.

Read-only. Re-renders note.md / article HTML from the payload in memory and
compares normalized text against the actual files, reporting a similarity
ratio plus the largest divergent fragments. Used to quantify how much manual
HTML editing escapes the payload (Phase 1 of render-separation design).

Usage:
  python3 scripts/maintenance/audit_render_drift.py --out-dir outputs/ready/20260611/2606.12320
  python3 scripts/maintenance/audit_render_drift.py --month 202606   # batch summary
"""

from __future__ import annotations

import argparse
import difflib
import html as html_lib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RENDERER = ROOT / "scripts" / "production" / "render_article.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_article", RENDERER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize(text: str) -> list[str]:
    text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style\b[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html_lib.unescape(text)
    text = text.replace("**", "").replace("·", "")
    lines = []
    for ln in text.splitlines():
        ln = re.sub(r"\s+", " ", ln).strip()
        if len(ln) >= 8:  # 忽略短标签行/噪声
            lines.append(ln)
    return lines


def audit_dir(out_dir: Path, renderer) -> dict | None:
    payload_path = out_dir / "generate_data.json"
    html_path = out_dir / "article_editor_ready.html"
    if not payload_path.exists() or not html_path.exists():
        return None
    data = json.loads(payload_path.read_text(encoding="utf-8"))
    try:
        rendered = renderer.render_editor_html(data)
    except Exception as e:
        return {"out_dir": str(out_dir), "error": f"render failed: {e}"}

    want = normalize(rendered)
    have = normalize(html_path.read_text(encoding="utf-8"))
    sm = difflib.SequenceMatcher(a=want, b=have)
    ratio = sm.ratio()

    only_in_html, only_in_render = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            only_in_render.extend(want[i1:i2])
        if tag in ("replace", "insert"):
            only_in_html.extend(have[j1:j2])
    return {
        "out_dir": str(out_dir),
        "similarity": round(ratio, 3),
        "lines_rendered": len(want),
        "lines_actual": len(have),
        "manual_only_lines": len(only_in_html),
        "samples_manual_only": only_in_html[:6],
        "samples_render_only": only_in_render[:6],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out-dir")
    g.add_argument("--month", help="YYYYMM batch mode")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    renderer = load_renderer()
    targets = []
    if args.out_dir:
        targets = [Path(args.out_dir).resolve()]
    else:
        for day in sorted((ROOT / "outputs" / "ready").glob(f"{args.month}??")):
            targets.extend(sorted(p for p in day.iterdir() if p.is_dir()))

    results = [r for r in (audit_dir(t, renderer) for t in targets) if r]
    for r in results:
        if "error" in r:
            print(f"{r['out_dir']}: ERROR {r['error']}")
            continue
        print(f"{Path(r['out_dir']).parent.name}/{Path(r['out_dir']).name}: "
              f"similarity={r['similarity']} manual_only={r['manual_only_lines']} "
              f"(rendered {r['lines_rendered']} vs actual {r['lines_actual']} lines)")
        if args.verbose:
            for s in r["samples_manual_only"]:
                print(f"    [仅在实际 HTML] {s[:90]}")
            for s in r["samples_render_only"]:
                print(f"    [仅在重渲染稿] {s[:90]}")
    if results and all("error" not in r for r in results):
        avg = sum(r["similarity"] for r in results) / len(results)
        print(f"\n均值 similarity: {avg:.3f}  ({len(results)} dirs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
