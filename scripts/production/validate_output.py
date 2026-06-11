#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate paper-notes output against the agent schema quality gates.

Checks content quality, style rules, and data consistency in a paper-notes
output directory. Reports P0/P1/P2 issues and computes an overall grade.

Usage:
  python3 validate_output.py --out-dir outputs/ready/20260530/2605.99999

Respects the quality_gates defined in:
  references/personas/persona-registry.json
  references/paper-note-agent-schema.json
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
from pathlib import Path


# ── Schema (inline defaults, overridable by --schema) ──────────────────────

DEFAULT_GRADE_CRITERIA = [
    {"grade": "A",  "min_score": 9.0, "p0_max": 0, "p1_max": 0, "p2_max": 2},
    {"grade": "A-", "min_score": 8.0, "p0_max": 0, "p1_max": 0, "p2_max": 4},
    {"grade": "B+", "min_score": 7.0, "p0_max": 2, "p1_max": 2, "p2_max": 4},
    {"grade": "B",  "min_score": 0.0, "p0_max": 999, "p1_max": 999, "p2_max": 999},
]

CHECKS_REGISTRY = []  # populated by @register_check


def register_check(check_id: str, severity: str, description: str):
    """Decorator that registers a validation function."""
    def decorator(fn):
        fn.check_id = check_id
        fn.severity = severity
        fn.description = description
        CHECKS_REGISTRY.append(fn)
        return fn
    return decorator


# ── Helpers ────────────────────────────────────────────────────────────────

def _read_html(out_dir: Path) -> str | None:
    html_path = out_dir / "article_editor_ready.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return None


def _read_json(out_dir: Path) -> dict | None:
    for name in ("generate_data.json", "data.json", "card_data.json"):
        p = out_dir / name
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
    return None


def _read_evidence_ledger(out_dir: Path) -> dict | None:
    p = out_dir / "evidence_ledger.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _grep(text: str, pattern: str) -> list[str]:
    return re.findall(pattern, text)


def _grep_count(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text))


def _strip_html(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style\b[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_heading_section(html: str, heading_pattern: str) -> str:
    heading_re = re.compile(
        rf"<h([2-4])\b[^>]*>[^<]*{heading_pattern}[^<]*</h\1>",
        re.DOTALL | re.IGNORECASE,
    )
    match = heading_re.search(html)
    if not match:
        return ""

    start = match.end()
    level = int(match.group(1))
    next_heading_re = re.compile(r"<h([2-4])\b[^>]*>", re.IGNORECASE)
    for next_match in next_heading_re.finditer(html, start):
        next_level = int(next_match.group(1))
        if next_level <= level:
            return html[start:next_match.start()]

    segment_end = re.search(r'<div[^>]*class="[^"]*segment[^"]*end', html[start:], re.IGNORECASE)
    if segment_end:
        return html[start:start + segment_end.start()]
    return html[start:]


def _extract_letter_heading_section(html: str, letter: str) -> str:
    heading_re = re.compile(
        rf"<h([2-4])\b[^>]*>\s*{re.escape(letter)}[\.\s、）)]+[^<]*</h\1>",
        re.DOTALL | re.IGNORECASE,
    )
    match = heading_re.search(html)
    if not match:
        return ""

    start = match.end()
    level = int(match.group(1))
    next_heading_re = re.compile(r"<h([2-4])\b[^>]*>", re.IGNORECASE)
    for next_match in next_heading_re.finditer(html, start):
        next_level = int(next_match.group(1))
        if next_level <= level:
            return html[start:next_match.start()]
    return html[start:]


def _score_values(data: dict | None) -> list[float]:
    if not data:
        return []
    score = data.get("score", {})
    dims = score.get("dimensions", [])
    values = []
    for dim in dims:
        try:
            values.append(float(dim.get("value")))
        except (TypeError, ValueError):
            continue
    return values


def _discussion_text(data: dict | None) -> str:
    if not data:
        return ""
    notes = data.get("discussion_notes", [])
    if isinstance(notes, list):
        return "\n".join(str(x) for x in notes)
    if isinstance(notes, str):
        return notes
    return ""


def _has_score_rationale_detail(data: dict | None) -> bool:
    if not data:
        return False
    detail = data.get("score_rationale_detail")
    if not isinstance(detail, dict):
        return False
    dimension_rationales = detail.get("dimension_rationales")
    if not isinstance(dimension_rationales, list) or len(dimension_rationales) < 3:
        return False
    roles = {str(item.get("role")) for item in dimension_rationales if isinstance(item, dict)}
    if "highest" not in roles or "lowest" not in roles:
        return False
    rationales = set()
    for item in dimension_rationales:
        if not isinstance(item, dict):
            return False
        if not str(item.get("label", "")).strip():
            return False
        rationale = str(item.get("rationale", "")).strip()
        if not rationale:
            return False
        rationales.add(rationale)
    if len(rationales) < 2:
        return False
    return True


# ── Registered Checks ──────────────────────────────────────────────────────

@register_check("f_section_requires_不过", "P0",
                "F段必须有转折词（不过/但/然而）引导的限制面/负面判断")
def check_f_section_requires_不过(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    f_section = _extract_letter_heading_section(html, "F")
    if not f_section:
        f_section = html[-5000:]  # fallback: last 5k chars
    f_text = _strip_html(f_section)

    adversative_markers = ["不过", "但是", "但", "然而"]
    found_adversative = [m for m in adversative_markers if m in f_text]
    if not found_adversative:
        return "F段未找到转折词（不过/但/然而）引导的限制面"

    negative_markers = [
        "局限", "限制", "注意", "不足", "风险", "问题", "然而",
        "制约", "依赖", "门槛", "未知", "窄", "成本", "预算",
        "不能", "并不", "不等于", "未验证", "外推", "迁移",
    ]
    found_negatives = [m for m in negative_markers if m in f_text]
    if not found_negatives:
        return f"F段包含转折词（{found_adversative[0]}）但缺乏实际的限制面/负面判断"
    return None


@register_check("symmetry_sentence_limit", "P1",
                "对称句式（不是...而是...）不得超过3次")
def check_symmetry_sentence(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    count = _grep_count(html, r"不是.*而是")
    if count > 3:
        return f"对称句式（不是...而是...）出现{count}次，超过3次限制"
    return None


@register_check("no_self_label_prefix", "P0",
                "禁止使用'判断先行：''价值判断：''核心洞察：'等自我标注前缀")
def check_self_label_prefix(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    prefixes = ["判断先行：", "价值判断：", "核心洞察：", "核心发现：", "关键洞察："]
    found = [p for p in prefixes if p in html]
    if found:
        return f"发现自我标注前缀: {', '.join(found)}"
    return None


@register_check("no_adverb_filler", "P1",
                "禁止副词型空话（系统性地、有效地、重要地）")
def check_adverb_filler(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    adverbs = ["系统性地", "有效地", "重要地", "显著地"]
    found = [a for a in adverbs if a in html]
    if found:
        return f"发现副词型空话: {', '.join(found)}"
    return None


@register_check("glossary_exists", "P2",
                "A段前应有'术语说明'列表")
def check_glossary(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    # Check for terminology section near the top
    if "术语说明" not in html[:3000]:
        return "未在文章前部找到术语说明（<strong>术语说明</strong>）"
    return None


@register_check("fragment_sentences_present", "P2",
                "应有碎句插入以避免通篇书面语")
def check_fragment_sentences(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    # Look for short standalone sentences / questions that break the rhythm
    fragment_patterns = [
        r"说白了[，,。]",
        r"问题出在[哪儿哪]？",
        r"结果[挺很]清楚[的。了]",
        r"别不信",
        r"别急",
        r"本质上[，,]",
    ]
    found_any = any(re.search(p, html) for p in fragment_patterns)
    if not found_any:
        return "未检测到明显的碎句插入（如'说白了'、'问题出在哪？'等）"
    return None


@register_check("d_section_needs_table", "P1",
                "D段涉及3+指标对比时应有表格")
def check_d_section_table(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    # Find D section
    d_match = re.search(
        r'<(?:h2|h3|h4)[^>]*>[^<]*[DdＤ][^<]*关键结果[^<]*</(?:h2|h3|h4)>'
        r'(.*?)(?=<(?:h2|h3|h4)[^>]*>[^<]*[EeEeＦ]|<div[^>]*class="[^"]*segment[^"]*end)',
        html, re.DOTALL
    )
    if d_match is None:
        # Try simpler: find content between D and E headers
        d_match = re.search(
            r'<(?:h2|h3|h4)[^>]*>[^<]*[DdＤ][^<]*</(?:h2|h3|h4)>'
            r'(.*?)(?:<h[2-4])',
            html, re.DOTALL
        )
    d_section = d_match.group(1) if d_match else ""

    if not d_section:
        return None  # can't find D section, skip

    # Count indicators mentioned (numbers with % or comparisons)
    indicators = re.findall(r'\d+\.?\d*%|\d+\.?\d*x|\d+\.?\d+\s*个(?:百分点|pp)', d_section)
    if len(indicators) >= 3:
        # Check if there's a <table> tag
        if "<table" not in d_section.lower():
            return f"D段涉及{len(indicators)}个指标但未使用表格"
    return None


@register_check("json_score_consistency", "P1",
                "JSON中score.total应与各维度分数之和一致")
def check_json_score_consistency(_html: str | None, data: dict | None) -> str | None:
    if data is None:
        return "未找到数据文件（generate_data.json / data.json / card_data.json）"
    score = data.get("score", {})
    total = score.get("total", 0)
    dims = score.get("dimensions", [])
    if not dims:
        return None
    dim_sum = sum(d.get("value", 0) for d in dims)
    if abs(dim_sum - total) > 0.3:  # tolerance for rounding
        return f"score.total={total} 与各维度之和({dim_sum})不一致（允许±0.3误差）"
    return None


@register_check("no_placeholder_text", "P0",
                "数据中不应有'待补充''TBD'等占位符")
def check_placeholder_text(html: str | None, data: dict | None) -> str | None:
    placeholders = ["待补充", "TBD", "Not specified", "Unknown Institution",
                    "placeholder", "Simulated"]
    found = []
    if html:
        for p in placeholders:
            if p in html:
                found.append(p)
    if data:
        text = json.dumps(data, ensure_ascii=False)
        for p in placeholders:
            if p in text and p not in found:
                found.append(p)
    if found:
        return f"发现占位符: {', '.join(found)}"
    return None


@register_check("flat_score_distribution", "P2",
                "五维评分过于扁平时，应补充维度级score_rationale_detail")
def check_flat_score_distribution(_html: str | None, data: dict | None) -> str | None:
    values = _score_values(data)
    if len(values) < 2:
        return None
    score_range = max(values) - min(values)
    if score_range > 0.2:
        return None

    rationale = ""
    if data:
        if _has_score_rationale_detail(data):
            return None
        if str(data.get("score_rationale", "")).strip():
            return "五维评分扁平，已有score_rationale但缺少维度级score_rationale_detail（需覆盖最高维/最低维/至少3个维度）"
        rationale = json.dumps(data.get("score_rationale", ""), ensure_ascii=False)
        rationale += "\n" + _discussion_text(data)
    rationale_markers = ["评分解释", "score_rationale", "可复用性", "Evidence", "Reusability"]
    if not any(marker in rationale for marker in rationale_markers):
        return (
            f"五维评分range={score_range:.1f}，但未找到score_rationale/评分解释；"
            "建议说明最高维和最低维为什么这样打分"
        )
    return None


@register_check("evidence_source_recorded", "P2",
                "应记录PDF/arXiv/fulltext核验证据源")
def check_evidence_source_recorded(_html: str | None, data: dict | None) -> str | None:
    if data is None:
        return None

    out_dir_value = data.get("_out_dir")
    ledger = None
    if out_dir_value:
        ledger = _read_evidence_ledger(Path(out_dir_value))
    ledger_markers = json.dumps(ledger or data.get("evidence_ledger", ""), ensure_ascii=False)
    discussion = _discussion_text(data)
    text = ledger_markers + "\n" + discussion
    source_patterns = [
        r"PDF evidence checked",
        r"fulltext\.txt",
        r"arXiv",
        r"Table\s*\d+",
        r"Figure\s*\d+",
        r"Appendix",
        r"§\s*\d",
    ]
    if not any(re.search(pattern, text, re.IGNORECASE) for pattern in source_patterns):
        return "未在generate_data.json中找到可机器识别的原文核验证据源记录"
    return None


@register_check("so_what_mechanism_judgement", "P2",
                "D段So What应包含headline之外的机制判断")
def check_so_what_mechanism_judgement(html: str | None, _data: dict | None) -> str | None:
    if html is None:
        return "article_editor_ready.html not found"
    text = _strip_html(html)
    if "So What" not in text and "so what" not in text.lower():
        return "未找到So What解释段"

    mechanism_markers = [
        "反直觉", "很多人以为", "真正", "瓶颈", "不在", "而在",
        "不是", "而是", "意味着", "换句话说", "说明", "关键",
        "结构", "机制", "成本", "失败来源", "评估口径", "工程",
    ]
    windows = [
        match.group(1)
        for match in re.finditer(r"So What\s*[:：]?\s*(.{0,360})", text, re.IGNORECASE)
    ]
    if not windows:
        windows = [text]
    if not any(any(marker in window for marker in mechanism_markers) for window in windows):
        return "So What偏解释性复述，缺少机制判断/反直觉对比"
    return None


# ── Core Logic ─────────────────────────────────────────────────────────────

def load_schema(out_dir: Path) -> dict:
    """Load grade criteria and check definitions from schema files."""
    schema = {
        "grade_criteria": DEFAULT_GRADE_CRITERIA,
    }
    # Try persona-registry.json
    registry_paths = [
        out_dir / "../../references/personas/persona-registry.json",
        Path(__file__).parent.parent / "references/personas/persona-registry.json",
    ]
    for rp in registry_paths:
        rp = rp.resolve()
        if rp.exists():
            try:
                data = json.loads(rp.read_text(encoding="utf-8"))
                qg = data.get("quality_gates", {})
                if qg.get("grade_criteria"):
                    schema["grade_criteria"] = qg["grade_criteria"]
                    break
            except (json.JSONDecodeError, KeyError):
                continue
    return schema


def compute_grade(p0: int, p1: int, p2: int, grade_criteria: list[dict]) -> str:
    """Compute overall grade from issue counts."""
    total_issues = p0 + p1 + p2
    score = max(10.0 - total_issues * 0.5, 0.0)  # heuristic

    best_grade = "B"
    for gc in sorted(grade_criteria, key=lambda x: x.get("min_score", 0), reverse=True):
        if (score >= gc["min_score"]
                and p0 <= gc["p0_max"]
                and p1 <= gc["p1_max"]
                and p2 <= gc["p2_max"]):
            best_grade = gc["grade"]
            break
    return f"{best_grade} (estimated: {score:.1f}/10, P0={p0}, P1={p1}, P2={p2})"


def run_validation(out_dir: Path, grade_criteria: list[dict]) -> dict:
    html = _read_html(out_dir)
    data = _read_json(out_dir)
    if data is not None:
        data["_out_dir"] = str(out_dir)

    issues = []
    for check_fn in CHECKS_REGISTRY:
        result = check_fn(html, data)
        if result is not None:
            issues.append({
                "check_id": check_fn.check_id,
                "severity": check_fn.severity,
                "description": check_fn.description,
                "detail": result,
            })

    p0 = len([i for i in issues if i["severity"] == "P0"])
    p1 = len([i for i in issues if i["severity"] == "P1"])
    p2 = len([i for i in issues if i["severity"] == "P2"])

    return {
        "out_dir": str(out_dir),
        "total_checks": len(CHECKS_REGISTRY),
        "passed_checks": len(CHECKS_REGISTRY) - len(issues),
        "failed_checks": len(issues),
        "p0_count": p0,
        "p1_count": p1,
        "p2_count": p2,
        "grade": compute_grade(p0, p1, p2, grade_criteria),
        "issues": issues,
    }


def write_report_files(out_dir: Path, report: dict) -> tuple[Path, Path]:
    json_path = out_dir / "validation_report.json"
    md_path = out_dir / "validation_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Validation Report",
        "",
        f"- 检查项：`{report['passed_checks']}/{report['total_checks']}`",
        f"- P0：`{report['p0_count']}`",
        f"- P1：`{report['p1_count']}`",
        f"- P2：`{report['p2_count']}`",
        f"- 等级：`{report['grade']}`",
        "",
        "## Issues",
    ]
    if not report["issues"]:
        lines.append("- none")
    else:
        for issue in report["issues"]:
            lines.append(
                f"- [{issue['severity']}] {issue['check_id']}: "
                f"{issue['description']} — {issue['detail']}"
            )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def print_report(report: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  论文速记质量校验报告")
    print(f"{'='*60}")
    print(f"  输出目录: {report['out_dir']}")
    print(f"  检查项  : {report['passed_checks']}/{report['total_checks']} 通过")
    print(f"  P0严重  : {report['p0_count']}")
    print(f"  P1优先  : {report['p1_count']}")
    print(f"  P2可选  : {report['p2_count']}")
    print(f"  等级    : {report['grade']}")
    print(f"{'='*60}")

    if not report["issues"]:
        print("\n  ✅ 全部检查通过！")
        return

    print("\n  ❌ 问题列表：")
    for issue in report["issues"]:
        icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue["severity"], "⚪")
        print(f"\n  {icon} [{issue['severity']}] {issue['check_id']}")
        print(f"     {issue['description']}")
        print(f"     → {issue['detail']}")

    # Suggestions
    p0_issues = [i for i in report["issues"] if i["severity"] == "P0"]
    if p0_issues:
        print(f"\n  {'='*56}")
        print(f"  建议：先修复 {len(p0_issues)} 个 P0 问题再发布")
        print(f"  {'='*56}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate paper-notes output against quality schema")
    ap.add_argument("--out-dir", required=True,
                    help="Paper-notes output directory (containing article_editor_ready.html)")
    ap.add_argument("--json", action="store_true",
                    help="Output raw JSON instead of human-readable report")
    ap.add_argument("--exit-code", action="store_true",
                    help="Exit with non-zero if P0 issues found")
    ap.add_argument("--write-report", action="store_true",
                    help="Write validation_report.json and validation_report.md into out-dir")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    if not out_dir.exists():
        print(f"ERROR: directory not found: {out_dir}", file=sys.stderr)
        return 2

    schema = load_schema(out_dir)
    report = run_validation(out_dir, schema.get("grade_criteria", DEFAULT_GRADE_CRITERIA))

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)

    if args.write_report:
        json_path, md_path = write_report_files(out_dir, report)
        if not args.json:
            print(str(json_path))
            print(str(md_path))

    if args.exit_code and report["p0_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
