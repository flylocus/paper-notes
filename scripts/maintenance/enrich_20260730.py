#!/usr/bin/env python3
"""One-off enrichment for 20260730 paper-notes payloads (Matryoshka + Self-Spec)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260730"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


MATRYOSHKA_RICH = {
    "A_research_problem": "MLE类任务要多轮调试与昂贵环境交互；单体Agent同时背噪声长上下文、开放搜索与执行细节，容量和预算很快撞墙。",
    "B_core_contributions": [
        "把战略探索与具体执行拆成Orchestrator与Sub-Agent两层",
        "Orchestrator只保留压缩长期状态，不吞完整噪声轨迹",
        "用Solution Refinement Tree采样做轨迹级偏好，训练Orchestrator",
        "成功执行轨迹可回流改进Sub-Agent",
    ],
    "C_method_framework": "三层套娃：Orchestrator维护跨轮压缩状态并发战略指令；Tool格式化指令并返回摘要与分数；Sub-Agent用新鲜上下文独立执行尝试。训练用Solution Refinement Tree做分支比较与轨迹级排序RL。",
    "D_key_results": [
        "Qwen3-30B-Coder：Dojo 0.3302 → Matryoshka-RL 0.4515，相对最高+36.7%",
        "Qwen3-4B作Orchestrator配o4-mini执行层：SFT+RL后HumanRank 0.5360，接近o4-mini作Orchestrator的0.5465",
        "o4-mini仅换架构：Dojo 0.4832 → Matryoshka 0.5465",
        "上下文：Orchestrator增长慢于单体Dojo；Sub-Agent上下文不随轮次膨胀",
    ],
    "E_industry_implications": [
        "长程脚手架先定状态边界：战略层摘要 vs 执行层新鲜上下文",
        "验收同时看任务分、跨轮上下文长度与环境调用次数",
        "小模型编排 + 大模型/工具执行，可作为可控成本分层配方",
    ],
    "F_one_line_judgement": "长程MLE别让一个模型同时背超长历史、搜索空间和执行细节，应分层压缩战略并展开子Agent。",
    "glossary": [
        {"term": "Matryoshka Agent", "definition": "套娃式分层Agent：高层编排、低层可展开执行，上下文边界分离。"},
        {"term": "Orchestrator", "definition": "战略层；跨轮只保留指令、摘要结果与分数，不吞完整执行轨迹。"},
        {"term": "Sub-Agent", "definition": "执行层；每次用新鲜上下文实现、运行、调试具体尝试。"},
        {"term": "Dojo Agent", "definition": "单体对照脚手架；同一模型连续背完整交互史。"},
        {"term": "HumanRank", "definition": "相对人类参赛者排行榜的排序分数；越高越好。"},
        {"term": "Solution Refinement Tree", "definition": "从共同父状态采样分支精炼，用子树最佳回报构造轨迹级偏好。"},
    ],
    "method_subsections": [
        {
            "title": "问题：单体要同时扛上下文和执行",
            "body": "长程MLE噪声日志、开放动作空间、环境调用贵。一体模型很难同时做战略与细节。",
        },
        {
            "title": "拆法：压缩战略 / 展开执行",
            "body": "Orchestrator只看压缩状态；Sub-Agent独立尝试；Tool接口强制信息边界并回摘要分数。",
        },
        {
            "title": "训练：树上比分支，不只比下一步分数",
            "body": "Solution Refinement Tree用子树最佳回报做偏好，让编排学长期方向，而非短视 intermediate score。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "相对单体上限",
                "论文证据": "30B-Coder Dojo 0.3302 → Matryoshka-RL 0.4515（相对最高+36.7%）。",
                "飞哥判断": "分层不是贴个multi-agent标签，HumanRank抬得实。",
            },
            {
                "看什么": "小模型当编排",
                "论文证据": "4B+ o4-mini执行层：0.1878单体 → 0.5360（接近o4-mini编排0.5465）。",
                "飞哥判断": "小模型更适合做决策层，前提是执行层够强。",
            },
            {
                "看什么": "只换架构",
                "论文证据": "o4-mini Dojo 0.4832 → Matryoshka 0.5465。",
                "飞哥判断": "收益不全靠额外训练，接口边界本身有价值。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主战场MLE；分层总预算与wall-clock未必公平；摘要丢关键信息有风险。",
                "飞哥判断": "先试MLE/代码Agent脚手架，别直接宣称通用办公Agent。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1 HumanRank；§4.2–4.5；Fig.2上下文。",
        "版本戳：arXiv:2607.25090v1 [cs.AI] 27 Jul 2026；ChatGPT 0729批次 #1。",
        "单位：Georgia Institute of Technology。",
        "证据边界：MLE为主；预算公平性与通用Agent外推待验证。",
    ],
    "so_what": "说白了，长程Agent未必需要一个模型记住全部历史。Matryoshka证明：把战略压成摘要状态，把执行展开成子Agent，更能撑过昂贵的迭代实验。",
    "feige_view": "三个动作：①脚手架先切状态边界；②看板加上下文长度与调用次数；③和今日Self-Spec对照——一层拆战略/执行，一层藏工具等待，都是在拆单体全背。",
    "limitations": [
        "不过，分层收益可能部分来自更高总推理与环境交互预算，摘要未给同token/同调用次数的完整对照。",
        "不过，上层摘要一旦漏关键信息，后续所有Sub-Agent都会偏。",
        "不过，目前集中在MLE；网页研究、办公流程与通用Coding Agent仍待验证。",
    ],
    "related_theme_picks": {
        "theme": "长程Agent结构与执行效率",
        "intro": "本篇讲如何分层压缩战略、展开执行；同线可对照：",
        "items": [
            {"arxiv_id": "2607.25816", "title_cn": "边推理边投机工具调用", "one_liner": "同日配对：用自投机藏起工具等待延迟。", "link": "https://arxiv.org/abs/2607.25816", "ready_date": "20260730"},
            {"arxiv_id": "2607.21596", "title_cn": "可执行技能共演化", "one_liner": "成功工作流如何沉淀成可复用技能。", "link": "https://arxiv.org/abs/2607.21596", "ready_date": "20260727"},
            {"arxiv_id": "2607.22602", "title_cn": "只在不确定处前瞻", "one_liner": "另一条算力分配：瓶颈触发而非全程加码。", "link": "https://arxiv.org/abs/2607.22602", "ready_date": "20260729"},
        ],
    },
    "target_audience": [
        "做长程Agent / MLE / coding agent脚手架的研究与平台团队。",
        "关心上下文爆炸与环境调用成本的工程负责人。",
        "评估『小模型编排 + 大模型执行』分层配方的决策者。",
    ],
    "sales_use_cases": [
        "回应『再换更大单体模型』：用4B编排接近o4-mini说明瓶颈常在结构。",
        "方案评审：要求同时报任务分、上下文长度、环境调用次数。",
        "成本沟通：把一次长任务拆成可丢弃的执行尝试，而不是一条永不截断的轨迹。",
    ],
    "objection_handling": [
        "客户说：『不就是planner-executor吗？』→ 回应：关键是执行尝试隔离成可展开Sub-Agent，且战略层不吞噪声全史。",
        "客户说：『是不是多烧了预算？』→ 回应：论文未完全公平对照；上线验收必须锁调用次数与wall-clock。",
    ],
    "copy_paste_lines": [
        "长程别让单体Agent背全文：分层压缩战略、展开执行。",
        "30B-Coder相对最高+36.7%；4B编排接近o4-mini。",
        "扩展任务长度，关键可能是状态边界，不是更大单体。",
    ],
    "key_quotes": [
        "decouples strategic exploration from costly execution",
        "Qwen3-4B-Instruct to reach Orchestrator performance comparable to o4-mini",
        "at most 36.7% relative performance gain",
    ],
    "score_rationale": "Matryoshka把长程MLE Agent拆成Orchestrator（压缩战略状态）与Sub-Agent（独立执行尝试），并用Solution Refinement Tree采样+轨迹级排序RL训练。Qwen3-30B-Coder从Dojo 0.3302到Matryoshka-RL 0.4515，相对最高+36.7%；Qwen3-4B作Orchestrator配o4-mini执行层达0.5360，接近o4-mini自身作Orchestrator的0.5465。Impact高：对准长上下文污染与执行成本分离。Novelty高：套娃式展开+树状精炼采样。Evidence高：HumanRank跨任务类别与多模型配置。Applicability中高：MLE落地清晰，但预算对照未完全公平。Reusability中高：分层接口可迁，通用Agent仍待验证。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "30B-Coder Dojo 0.3302 → Matryoshka-RL 0.4515（相对最高+36.7%）", "evidence": "Abstract + Table 1 / §4.2", "location": "Abstract / Table 1"},
            {"claim": "Qwen3-4B编排+o4-mini执行层达0.5360，接近o4-mini编排0.5465", "evidence": "Table 1 rows", "location": "Table 1"},
            {"claim": "o4-mini仅换架构 0.4832→0.5465", "evidence": "Table 1 / §4.2", "location": "Table 1"},
            {"claim": "Orchestrator上下文增速慢于Dojo；Sub-Agent不随轮次膨胀", "evidence": "Fig.2 / §4.5", "location": "Fig.2"},
            {"claim": "F段限制：预算公平、摘要漏信息、MLE外推", "evidence": "ChatGPT limitations + paper discussion", "location": "Limitations"},
        ]
    },
}


SELF_SPEC_RICH = {
    "A_research_problem": "工具Agent大量wall-clock耗在搜索/API返回上；外置草稿模型或历史缓存常与真实部署Agent的下一步调用不一致，形成speculator–agent gap。",
    "B_core_contributions": [
        "把Agent与工具调用speculator合并到同一部署模型",
        "从Agent自身rollout生成on-policy speculation目标",
        "Agent/Speculator交替更新的联合强化学习",
        "复用prefix KV cache，避免为预测再算一遍完整上下文",
    ],
    "C_method_framework": "同一模型双模式：agent模式解题，speculator模式根据部分轨迹预测下一工具名与参数；用自rollout构造目标、交替RL更新，并复用prefix KV cache。",
    "D_key_results": [
        "Qwen3-4B平均Hit@1：SFT 44.1 → RL 61.2；成功率26.6→27.7",
        "Qwen3.5-4B平均Hit@1：SFT 48.9 → RL 66.3；成功率49.2→50.6",
        "同系列外置最强草稿Qwen3-1.7B平均Hit@1仅18.6，远低于自投机",
        "交替更新消融：1:1日程31.8 Hit@1/10.3成功率，4:8升到55.2/26.1",
    ],
    "E_industry_implications": [
        "先筛可投机工具：只对只读、幂等、可取消调用开预执行",
        "看板同时报Hit@1、任务成功率、工具等待占比与无效预调用成本",
        "别把Hit@1提升直接等同端到端加速，收益取决于工具延迟与可并行度",
    ],
    "F_one_line_judgement": "工具等待是真实延迟源；让同一Agent边推理边预测下一步调用，比外挂不相干的小草稿模型更对齐。",
    "glossary": [
        {"term": "Tool-call speculation", "definition": "在Agent明确发出调用前，预测并提前执行下一步工具；命中则可复用结果藏延迟。"},
        {"term": "Speculator–agent gap", "definition": "同一中间轨迹下，外置预测器与真实部署Agent选了不同下一步调用。"},
        {"term": "Self-speculating agent", "definition": "同一模型兼做任务Agent与next-call speculator。"},
        {"term": "Hit@1", "definition": "工具名与完整参数字典都精确匹配的命中率。"},
        {"term": "Joint agent-speculator RL", "definition": "自rollout构造投机目标，并交替更新两模式的强化学习。"},
        {"term": "Prefix KV reuse", "definition": "投机分支复用Agent已算好的前缀KV cache，避免重算全上下文。"},
    ],
    "method_subsections": [
        {
            "title": "问题：延迟在等待，不在多几个token",
            "body": "搜索、数据库、外部API常占秒级。传统投机解码优化生成，但工具I/O仍空等。",
        },
        {
            "title": "关键：预测器必须是自己",
            "body": "外置小模型/历史缓存与部署Agent分布不对齐。文中显示同系列小草稿Hit@1远低于自投机。",
        },
        {
            "title": "训练：交替更新稳住双目标",
            "body": "同一模型两模式；自rollout目标；交替块更新+优化器重置，避免投机抬高却把任务练崩。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "命中率",
                "论文证据": "4B Hit@1 44.1→61.2；4B-new 48.9→66.3。",
                "飞哥判断": "这是『更像自己下一步』，不是糊一个通用工具建议。",
            },
            {
                "看什么": "任务是否掉点",
                "论文证据": "成功率26.6→27.7、49.2→50.6，基本持平略升。",
                "飞哥判断": "投机能力不是靠牺牲解题换来的。",
            },
            {
                "看什么": "外置草稿",
                "论文证据": "Qwen3-1.7B平均Hit@1仅18.6，远低于同模型自投机。",
                "飞哥判断": "先填齐speculator-agent gap，再谈要不要小模型。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "写副作用工具不安全；Hit@1≠同比例加速；需权限/幂等/取消。",
                "飞哥判断": "默认只投机只读调用，写操作必须闸。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 2主结果；Table 4交替日程消融；§2 gap分析。",
        "版本戳：arXiv:2607.25816v1 [cs.AI] 28 Jul 2026；ChatGPT 0729批次 #2。",
        "单位：University of California, Santa Barbara · LinkedIn Inc。",
        "证据边界：副作用工具、端到端加速与权限一致性仍需系统层验证。",
    ],
    "so_what": "说白了，工具Agent优化别只盯着解码吞吐。Self-Spec证明：把下一步工具调用预测并进同一部署模型，才能真正对准你要藏住的那几秒等待。",
    "feige_view": "三个动作：①工具注册表标可投机/禁投机；②验收加Hit@1与等待占比；③和今日Matryoshka对照——一个拆战略/执行，一个并行推理与工具等待。",
    "limitations": [
        "不过，错误预测会触发无效甚至昂贵的工具调用。",
        "不过，写入、支付、删除等有副作用工具不能随意提前执行。",
        "不过，Hit@1提升不等于同比例端到端加速，还取决于工具延迟与可并行程度。",
    ],
    "related_theme_picks": {
        "theme": "长程Agent结构与执行效率",
        "intro": "本篇讲如何藏起工具等待；同线可对照：",
        "items": [
            {"arxiv_id": "2607.25090", "title_cn": "分层展开子Agent", "one_liner": "同日配对：压缩战略状态、展开执行尝试。", "link": "https://arxiv.org/abs/2607.25090", "ready_date": "20260730"},
            {"arxiv_id": "2607.22602", "title_cn": "只在不确定处前瞻", "one_liner": "推理算力也要选择性投入，而不是全程加码。", "link": "https://arxiv.org/abs/2607.22602", "ready_date": "20260729"},
            {"arxiv_id": "2607.21596", "title_cn": "可执行技能共演化", "one_liner": "降低重复探索：把成功流程沉淀成技能。", "link": "https://arxiv.org/abs/2607.21596", "ready_date": "20260727"},
        ],
    },
    "target_audience": [
        "做Agent推理服务、工具网关与延迟优化的工程团队。",
        "关心工具等待占端到端时长的产品与平台负责人。",
        "评估投机执行权限模型的安全/治理同学。",
    ],
    "sales_use_cases": [
        "回应『再换更快模型』：先问工具等待占比，可能比再砍几个生成token更值。",
        "方案评审：要求可投机工具白名单 + Hit@1/无效预调用成本看板。",
        "成本沟通：命中才复用；未命中必须可取消，不能默默烧外部API。",
    ],
    "objection_handling": [
        "客户说：『外挂个小模型不就行？』→ 回应：同系列小草稿Hit@1远低于自投机，先消gap。",
        "客户说：『会不会乱调工具？』→ 回应：默认只读可投机；写操作需权限闸与幂等设计。",
    ],
    "copy_paste_lines": [
        "工具等待别干等：同一Agent边推理边预测下一步调用。",
        "Hit@1从44.1到61.2，任务成功率基本不掉。",
        "优化Agent延迟，先问等待占比，再问要不要更快的解码。",
    ],
    "key_quotes": [
        "unifying the agent and speculator within the same model",
        "Hit@1 from 44.1 to 61.2 for Qwen3-4B",
        "from 48.9 to 66.3 for Qwen3.5-4B, while preserving agent task success",
    ],
    "score_rationale": "Self-speculating agent把下一步工具调用预测并入同一部署模型，用joint agent-speculator RL在自rollout上交替训练，并复用prefix KV cache。Qwen3-4B平均Hit@1从SFT 44.1到RL 61.2，Qwen3.5-4B从48.9到66.3，任务成功率基本不掉。Impact高：直接打工具等待这一真实延迟源。Novelty高：消除speculator-agent gap。Evidence高：多基准与外部draft对照。Applicability高：工程价值清晰，但副作用工具需门控。Reusability中高：范式可迁，端到端加速仍取决于工具延迟。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "Qwen3-4B Hit@1 44.1→61.2；成功率26.6→27.7", "evidence": "Abstract + Table 2", "location": "Abstract / Table 2"},
            {"claim": "Qwen3.5-4B Hit@1 48.9→66.3；成功率49.2→50.6", "evidence": "Abstract + Table 2", "location": "Abstract / Table 2"},
            {"claim": "外置最强同系列草稿平均Hit@1约18.6，低于自投机", "evidence": "Table 2 / §4", "location": "Table 2"},
            {"claim": "交替日程1:1仅31.8/10.3，4:8到55.2/26.1", "evidence": "Table 4 ablation", "location": "Table 4"},
            {"claim": "F段限制：副作用工具、加速非同比例、权限一致性", "evidence": "Discussion + ChatGPT limitations", "location": "Limitations"},
        ]
    },
}


def enrich_one(arxiv_id: str, paper_key: str, rich: dict, html_title: str, html_conclusion: str) -> Path:
    out = ROOT / "outputs" / "ready" / DATE / arxiv_id
    gen_path = out / "generate_data.json"
    card_path = out / "card_data.json"
    ledger_path = out / "evidence_ledger.json"
    fused_article = ROOT / "fused" / f"{paper_key}_article_payload_{DATE}.json"
    fused_card = ROOT / "fused" / f"{paper_key}_card_payload_{DATE}.json"
    fused_ledger = ROOT / "fused" / f"{paper_key}_evidence_ledger_{DATE}.json"

    data = load(gen_path)
    for key, value in rich.items():
        if key == "evidence_ledger_patch":
            continue
        data[key] = value

    # score_rationale_detail for QA flatness guard
    dims = data.get("score", {}).get("dimensions", [])
    if dims and "score_rationale_detail" not in data:
        by_label = {d["label"]: d["value"] for d in dims}
        highest = sorted(by_label, key=by_label.get, reverse=True)[:3]
        lowest = sorted(by_label, key=by_label.get)[:1]
        data["score_rationale_detail"] = {
            "schema_version": 1,
            "score_range": round(max(by_label.values()) - min(by_label.values()), 1),
            "highest_dimensions": highest,
            "lowest_dimensions": lowest,
            "dimension_rationales": [
                {
                    "label": d["label"],
                    "value": d["value"],
                    "role": "highest" if d["label"] in highest else ("lowest" if d["label"] in lowest else "middle"),
                    "rationale": f"{'最高维' if d['label'] in highest else ('最低维' if d['label'] in lowest else '中间维')}：{rich.get('score_rationale','')[:180]}",
                }
                for d in dims
            ],
        }

    dump(gen_path, data)
    dump(fused_article, data)

    card = load(card_path)
    card["info"] = data.get("info", card.get("info"))
    card["score"] = data.get("score", card.get("score"))
    if "title_cn" in data.get("info", {}):
        card["info"]["title_cn"] = data["info"]["title_cn"]
    dump(card_path, card)
    dump(fused_card, card)

    if ledger_path.exists() and "evidence_ledger_patch" in rich:
        ledger = load(ledger_path)
        patch = rich["evidence_ledger_patch"]
        if "claim_evidence" in patch:
            ledger["claim_evidence"] = patch["claim_evidence"]
        dump(ledger_path, ledger)
        dump(fused_ledger, ledger)

    notes = data.setdefault("discussion_notes", [])
    tag = f"Enriched with rich fields via enrich_{DATE}.py"
    if tag not in notes:
        notes.append(tag)
        dump(gen_path, data)
        dump(fused_article, data)

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/production/render_article.py"),
            "--article-payload",
            str(gen_path),
            "--out-dir",
            str(out),
            "--html-title",
            html_title,
            "--html-conclusion",
            html_conclusion,
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/production/render_article_wechat_safe.py"),
            "--article-payload",
            str(gen_path),
            "--out-dir",
            str(out),
            "--html-title",
            html_title,
            "--html-conclusion",
            html_conclusion,
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/production/generate_cards.py"),
            "--data",
            str(card_path),
            "--out",
            str(out),
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/production/generate_cover.py"),
            "--data",
            str(card_path),
            "--out",
            str(out / "cover_235.png"),
        ],
        check=True,
    )
    return out


def main() -> None:
    enrich_one(
        "2607.25090",
        "matryoshka",
        MATRYOSHKA_RICH,
        "长程别让单体Agent背全文：Matryoshka分层压缩战略、展开执行",
        "长程Agent的扩展关键，往往不是更大单体，而是把战略状态压住、把执行尝试展开。",
    )
    enrich_one(
        "2607.25816",
        "self-spec",
        SELF_SPEC_RICH,
        "工具等待别干等：同一Agent边推理边投机预测下一步调用",
        "工具Agent的延迟往往不在多生成几个token，而在能否把秒级等待藏进继续推理的时间里。",
    )
    print("enriched matryoshka + self-spec")


if __name__ == "__main__":
    main()
