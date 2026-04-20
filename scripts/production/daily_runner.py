#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paper-notes daily runner (orchestrator skeleton).

This runner standardizes the end-to-end flow but intentionally keeps
human approval in the middle after Top-3 recommendation.

Modes:
  1) phase1   -> build candidates / recommend top picks
  2) produce  -> for a selected paper, verify metadata -> build payload -> render article -> build publish pack

Examples:
  python3 daily_runner.py phase1 --date 20260415
  python3 daily_runner.py produce \
    --date 20260415 \
    --arxiv-id 2604.09285 \
    --paper-key sage \
    --title-cn "SAGE：面向服务型 Agent 的图引导评测基准" \
    --score-json fused/2604.09285_score.json \
    --out-dir outputs/20260415/2604.09285 \
    --html-title "【论文速记】企业里的 Agent，为什么不能只测会不会答，还要测会不会按流程做？" \
    --html-conclusion "真正能进入企业服务流程的 Agent，关键不只是会不会回答，而是能不能沿着正确 SOP 做出正确动作。" \
    --one-line "这篇论文真正重要的地方，不是又做了一个 benchmark，而是把 Agent 评测从会不会回答推进到了会不会沿着流程正确执行。"
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS_ROOT = os.path.join(ROOT, "scripts")
PRODUCTION_SCRIPTS = os.path.join(SCRIPTS_ROOT, "production")
INPUTS = os.path.join(ROOT, "inputs")
FUSED = os.path.join(ROOT, "fused")
OUTPUTS = os.path.join(ROOT, "outputs")


def production_script(name: str) -> str:
    return os.path.join(PRODUCTION_SCRIPTS, name)


def run(cmd):
    print("[RUN]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def phase1(date: str):
    print("[Phase1] Build candidate pool")
    run([sys.executable, production_script("run_phase1.py"), "--date", date])
    print("\n[Next Required Human Step]")
    print("1. Review fused/candidates_<date>.json")
    print("2. Cross-check with RSS/arXiv candidate window")
    print("3. Confirm Top 3 with reasons")
    print("4. User selects one paper before entering produce mode")


def produce(args):
    os.makedirs(args.out_dir, exist_ok=True)
    metadata_out = os.path.join(FUSED, f"{args.arxiv_id}_metadata.json")

    print("[Produce/1] Verify metadata")
    run([
        sys.executable, production_script("verify_metadata.py"),
        "--arxiv-id", args.arxiv_id,
        "--out", metadata_out,
        "--keep-pdf"
    ])

    print("[Produce/2] Build payloads")
    build_cmd = [
        sys.executable, production_script("build_payload.py"),
        "--metadata", metadata_out,
        "--score", args.score_json,
        "--paper-key", args.paper_key,
        "--date", args.date,
        "--title-cn", args.title_cn,
        "--out-dir", FUSED,
        "--one-line", args.one_line,
        "--research-problem", args.research_problem,
        "--method-framework", args.method_framework,
    ]
    for x in args.core_contributions:
        build_cmd.extend(["--core-contributions", x])
    for x in args.key_results:
        build_cmd.extend(["--key-results", x])
    for x in args.industry_implications:
        build_cmd.extend(["--industry-implications", x])
    run(build_cmd)

    article_payload = os.path.join(FUSED, f"{args.paper_key}_article_payload_{args.date}.json")
    card_payload = os.path.join(FUSED, f"{args.paper_key}_card_payload_{args.date}.json")

    print("[Produce/3] Render article files")
    run([
        sys.executable, production_script("render_article.py"),
        "--article-payload", article_payload,
        "--out-dir", args.out_dir,
        "--html-title", args.html_title,
        "--html-conclusion", args.html_conclusion,
    ])

    print("[Produce/4] Render images")
    run([
        sys.executable, production_script("generate_cards.py"),
        "--data", card_payload,
        "--out", args.out_dir,
    ])
    run([
        sys.executable, production_script("generate_cover.py"),
        "--data", card_payload,
        "--out", os.path.join(args.out_dir, "cover_235.png"),
    ])

    print("[Produce/5] Build publish pack")
    pub_out = os.path.join(args.out_dir, "publish_pack.md")
    pub_cmd = [
        sys.executable, production_script("build_publish_pack.py"),
        "--out", pub_out,
        "--intro", args.publish_intro,
        "--summary", args.publish_summary,
    ]
    for t in args.publish_titles:
        pub_cmd.extend(["--title", t])
    run(pub_cmd)

    print("[Produce/6] Run preflight guard")
    run([
        sys.executable, production_script("preflight_check.py"),
        "--out-dir", args.out_dir,
        "--mode", "publish",
    ])

    print("\n[Done] Final output dir:")
    print(args.out_dir)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    p1 = sub.add_parser("phase1")
    p1.add_argument("--date", required=True)

    p2 = sub.add_parser("produce")
    p2.add_argument("--date", required=True)
    p2.add_argument("--arxiv-id", required=True)
    p2.add_argument("--paper-key", required=True)
    p2.add_argument("--title-cn", required=True)
    p2.add_argument("--score-json", required=True)
    p2.add_argument("--out-dir", required=True)
    p2.add_argument("--html-title", default="")
    p2.add_argument("--html-conclusion", default="")
    p2.add_argument("--one-line", default="这是一篇值得关注的论文。")
    p2.add_argument("--research-problem", default="待补充")
    p2.add_argument("--method-framework", default="待补充")
    p2.add_argument("--core-contributions", action='append', default=[])
    p2.add_argument("--key-results", action='append', default=[])
    p2.add_argument("--industry-implications", action='append', default=[])
    p2.add_argument("--publish-title", dest="publish_titles", action='append', default=[])
    p2.add_argument("--publish-intro", default="待补充")
    p2.add_argument("--publish-summary", default="待补充")

    args = ap.parse_args()
    if args.mode == "phase1":
        phase1(args.date)
    elif args.mode == "produce":
        produce(args)


if __name__ == "__main__":
    main()
