#!/usr/bin/env python3
"""
router_judge.py — 通用 Router Judge 执行器

基于 PilotDeck Token Saver + EdgeClaw 纯 LLM route decision 模式。
支持两套 schema：
  1. 论文速记 Router (paper-note-router.json) — 4-tier, trigger_examples
  2. 金融观察 Router (schema router 段) — 6-tier, trigger_patterns

用法：
  python3 router_judge.py --config <router.json> --input "用户输入" [options]

输出：JSON（tier, confidence, method, reasoning）
"""

import json, sys, re, os, argparse, textwrap
from pathlib import Path

# ── 硬匹配引擎 ──────────────────────────────────────────────

def hard_match_tier(input_text: str, tiers: dict) -> list[tuple[str, float]]:
    """
    对每个 tier 做 trigger_patterns 关键词硬匹配。
    返回 [ (tier_name, score), ... ]，按匹配数降序。
    仅匹配有 'trigger_patterns' 字段的 tier（金融观察风格）。
    """
    matches = []
    for name, cfg in tiers.items():
        patterns = cfg.get("trigger_patterns") or cfg.get("trigger_examples") or []
        if not patterns:
            continue
        # 统一处理：trigger_examples 是完整短语/句子匹配，trigger_patterns 是关键词匹配
        score = 0
        for p in patterns:
            if p.lower() in input_text.lower():
                # trigger_examples 是长短语，匹配权重更高
                if len(p) >= 4:
                    score += 2
                else:
                    score += 1
        if score > 0:
            matches.append((name, score))
    # 按得分降序（得分相同按 pattern 长度降序——更具体的赢）
    matches.sort(key=lambda x: (-x[1], -sum(len(p) for p in (tiers[x[0]].get("trigger_patterns") or tiers[x[0]].get("trigger_examples") or []) if p.lower() in input_text.lower())))

    # 平票保护：第一名和第二名得分相同时，交给 LLM Judge
    if len(matches) >= 2 and matches[0][1] == matches[1][1]:
        return []  # 平票，不返回硬匹配结果，留给 LLM Judge
    return matches


# ── LLM Judge Prompts ──────────────────────────────────────

def build_judge_prompt(input_text: str, tiers: dict, default_tier: str, rules: list[str]) -> str:
    """为 LLM 构建 tier 分类 prompt。注入全部 tier 描述 + rules。"""
    tier_descriptions = []
    for name, cfg in tiers.items():
        desc = cfg.get("description", "")
        patterns = cfg.get("trigger_patterns") or cfg.get("trigger_examples") or []
        patterns_str = ", ".join(patterns[:5])  # 最多5个示例
        tier_descriptions.append(
            f"- {name}: {desc} [触发示例: {patterns_str}]"
        )

    rules_str = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(rules))

    prompt = f"""你是一个 Router Judge。你的任务是根据用户输入，从预定义 tier 中选择最合适的一个。

可用 tier：
{chr(10).join(tier_descriptions)}

决策规则：
{rules_str}

默认 tier（不确定时使用）：{default_tier}

用户输入：{input_text}

请直接输出 tier 名称，不要任何前缀、标记、或额外文字。"""

    return prompt


def parse_judge_response(response_text: str, valid_tiers: set[str], default_tier: str) -> tuple[str, str]:
    """
    解析 LLM 返回，抽取出 tier 名称。
    返回 (tier, raw_response)。
    """
    clean = response_text.strip().lower()

    # 尝试直接匹配 tier 名称
    for tier in valid_tiers:
        if tier.lower() in clean:
            return tier, response_text.strip()

    # 尝试 <tier>NAME</tier> 格式
    m = re.search(r'<tier>(.*?)</tier>', clean, re.IGNORECASE)
    if m:
        candidate = m.group(1).strip().lower()
        for tier in valid_tiers:
            if tier.lower() == candidate:
                return tier, response_text.strip()

    # 回退到默认
    return default_tier, response_text.strip()


# ── Sticky 状态管理 ────────────────────────────────────────

STICKY_DIR = Path.home() / ".hermes" / "router_sticky"


def load_sticky(router_name: str) -> dict | None:
    """加载 sticky 状态。返回 {tier, session_key} 或 None。"""
    sticky_file = STICKY_DIR / f"{router_name}.json"
    if sticky_file.exists():
        try:
            return json.loads(sticky_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return None


def save_sticky(router_name: str, tier: str, session_key: str = ""):
    """保存 sticky 状态。"""
    STICKY_DIR.mkdir(parents=True, exist_ok=True)
    sticky_file = STICKY_DIR / f"{router_name}.json"
    sticky_file.write_text(json.dumps({"tier": tier, "session_key": session_key}, ensure_ascii=False))
    return sticky_file


def clear_sticky(router_name: str):
    """清除 sticky 状态。"""
    sticky_file = STICKY_DIR / f"{router_name}.json"
    if sticky_file.exists():
        sticky_file.unlink()


# ── 主入口 ──────────────────────────────────────────────────

def router_judge(config_path: str, input_text: str, clear_sticky_flag: bool = False,
                  session_key: str = "", enable_sticky: bool = True) -> dict:
    """
    执行 Router Judge 分类。

    参数:
        config_path: router JSON 文件的绝对路径
        input_text: 用户输入（论文标题/摘要 或 股票查询）
        clear_sticky_flag: 是否强制清除 sticky
        session_key: 会话标识（用于 sticky scope 判断）
        enable_sticky: 是否启用 sticky

    返回:
        {
            "tier": str,
            "confidence": "high" | "medium" | "low",
            "method": "hard_match" | "llm_judge" | "sticky" | "default",
            "reasoning": str,
            "valid_tiers": list[str]
        }
    """
    # 1. 加载配置
    with open(config_path) as f:
        config = json.load(f)

    router = config.get("router", config)  # 兼容两种 JSON 结构
    tiers = router.get("tiers", {})
    default_tier = router.get("default_tier", list(tiers.keys())[0] if tiers else "unknown")
    sticky_cfg = router.get("sticky", {})
    fallback = router.get("fallback", {})
    rules = router.get("rules", [])
    router_name = config.get("agent_name", config.get("// schema_description", "router"))

    valid_tiers = set(tiers.keys())
    result = {
        "tier": default_tier,
        "confidence": "low",
        "method": "default",
        "reasoning": f"回退到默认 tier: {default_tier}",
        "valid_tiers": list(valid_tiers),
    }

    # 2. 清除 sticky（如果用户要求）
    if clear_sticky_flag:
        clear_sticky(router_name)
        result["reasoning"] = f"Sticky 已清除，重新分类"

    # 3. Sticky 检查（如果启用且 sticky 数据存在）
    sticky_used = False
    if enable_sticky and sticky_cfg.get("enabled", False):
        sticky_data = load_sticky(router_name)
        if sticky_data:
            # 检查 session_key 是否匹配
            stored_key = sticky_data.get("session_key", "")
            if not stored_key or stored_key == session_key:
                # 如果 session_key 有变化，金融观察模式需要重新分类
                if session_key and stored_key and session_key != stored_key:
                    pass  # session 变化，跳过 sticky
                else:
                    tier = sticky_data["tier"]
                    if tier in valid_tiers:
                        result.update({
                            "tier": tier,
                            "confidence": "high",
                            "method": "sticky",
                            "reasoning": f"Sticky 命中: 保持 tier={tier} (来自上次分类)",
                        })
                        sticky_used = True

    # 4. 硬匹配（快速路径）
    if not sticky_used:
        hard_matches = hard_match_tier(input_text, tiers)
        if hard_matches:
            best_tier, best_score = hard_matches[0]
            result.update({
                "tier": best_tier,
                "confidence": "high" if best_score >= 3 else "medium",
                "method": "hard_match",
                "reasoning": f"硬匹配命中: tier={best_tier} (匹配得分={best_score}, 命中词={[p for p in (tiers[best_tier].get('trigger_patterns') or tiers[best_tier].get('trigger_examples') or []) if p.lower() in input_text.lower()]})",
            })

        # 5. LLM Judge（回退路径）
        if not hard_matches:
            judge_prompt = build_judge_prompt(input_text, tiers, default_tier, rules)
            # 通过 stdin/stdout 通讯：输出 prompt 供 Hermes agent 读取
            result.update({
                "tier": "__needs_llm_judge__",
                "confidence": "pending",
                "method": "llm_judge_pending",
                "reasoning": "需要 LLM Judge 分类",
                "judge_prompt": judge_prompt,
                "valid_tiers": list(valid_tiers),
            })

    # 6. 保存 sticky（如果命中且 sticky 启用）
    if sticky_used or (result["method"] in ("hard_match",) and enable_sticky and sticky_cfg.get("enabled", False)):
        if result["tier"] != "__needs_llm_judge__":
            save_sticky(router_name, result["tier"], session_key)

    result["router_name"] = router_name
    return result


# ── 辅助: 对 LLM Judge 的返回做后处理 ──────────────────────

def apply_llm_response(result: dict, llm_raw: str) -> dict:
    """当 judge 返回 __needs_llm_judge__ 后，用 LLM 的输出更新结果。"""
    if result.get("tier") != "__needs_llm_judge__":
        return result

    valid_tiers = set(result.get("valid_tiers", []))
    config_path = result.get("_config_path", "")
    default_tier = result.get("_default_tier", list(valid_tiers)[0] if valid_tiers else "unknown")

    # 加载配置获取默认值
    if config_path:
        with open(config_path) as f:
            config = json.load(f)
        router = config.get("router", config)
        default_tier = router.get("default_tier", default_tier)
        fallback = router.get("fallback", {})
        if fallback.get("strategy") == "fallback_to_default":
            default_tier = fallback.get("default_fallback", default_tier)

    tier, raw = parse_judge_response(llm_raw, valid_tiers, default_tier)
    result.update({
        "tier": tier,
        "confidence": "medium",
        "method": "llm_judge",
        "reasoning": f"LLM Judge 分类: {tier}",
        "llm_raw": raw,
    })

    # 保存 sticky
    router_name = result.get("router_name", "")
    session_key = result.get("_session_key", "")
    if router_name:
        save_sticky(router_name, tier, session_key)

    return result


# ── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Router Judge — 通用 tier 分类器")
    parser.add_argument("--config", required=True, help="Router JSON 文件路径")
    parser.add_argument("--input", required=True, help="用户输入文本")
    parser.add_argument("--session-key", default="", help="会话标识（用于 sticky scope）")
    parser.add_argument("--clear-sticky", action="store_true", help="清除 sticky 状态")
    parser.add_argument("--no-sticky", action="store_true", help="禁用 sticky")
    parser.add_argument("--llm-raw", help="(选填) LLM Judge 的原始输出，用于后处理 __needs_llm_judge__ 结果")
    args = parser.parse_args()

    result = router_judge(
        config_path=args.config,
        input_text=args.input,
        clear_sticky_flag=args.clear_sticky,
        session_key=args.session_key,
        enable_sticky=not args.no_sticky,
    )

    # 如果提供了 LLM 输出，做后处理
    if args.llm_raw and result.get("tier") == "__needs_llm_judge__":
        result["_config_path"] = args.config
        result["_session_key"] = args.session_key
        result = apply_llm_response(result, args.llm_raw)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
