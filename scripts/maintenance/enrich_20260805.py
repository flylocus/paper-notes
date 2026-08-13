#!/usr/bin/env python3
"""One-off enrichment for 20260805 paper-notes payloads (G-ReAct + Memory Reward Inflation)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260805"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


GREACT_RICH = {
    "intro_lead": "",
    "A_research_problem": "开放域深度搜索若只靠线性文本轨迹，长程多跳里容易丢中间状态、漂移约束并重复探索。瓶颈不只是检索工具能不能调，而是分支搜索里能不能把已搜路径、证据和约束稳住。",
    "B_core_contributions": [
        "用固定拓扑 query graph 替代纯线性 ReAct 历史，做结构—状态共演化",
        "同一框架既生成高质量监督轨迹，也可作无微调的推理时脚手架",
        "约 1.9K 轨迹微调 Qwen3-30B-A3B-Thinking-2507：BrowseComp-ZH 52.6%、XBench-DS 79.0%",
    ],
    "C_method_framework": "把复杂深搜题落到固定拓扑查询图：节点/边持续更新已搜分支、中间证据、待解约束与进度。搜索决策由图状态约束，而不是无限拉长文本历史。训练侧用图轨迹做 SFT；推理侧可直接挂到已有强模型上引导搜索。",
    "D_key_results": [
        "G-ReAct-OpenSeeker-v1：BrowseComp 35.6 / BrowseComp-ZH 52.6 / XBench-DS 79.0 / GAIA 64.2（pass@1）",
        "同池对照：相对 OpenSeeker-v1 仅用 16% 轨迹（1.9K vs 11.7K）仍涨 6.1/4.2/5.0；相对 DeepDive 同池大幅领先",
        "推理时无微调：doubao-seed-2.0-pro BrowseComp-ZH 64.71→71.28，Avg. Tool Calls 19.72→18.62",
    ],
    "E_industry_implications": [
        "深度搜索验收看结构化状态是否可追踪，而不只看多轮检索是否跑通",
        "轨迹结构优先于堆数据/堆参数：图监督可显著降低 SFT 样本量",
        "强模型可先挂推理脚手架，再决定是否小样本微调",
    ],
    "F_one_line_judgement": "这篇最适合开放式深度搜索/网页 Agent：用查询图状态代替线性 ReAct 历史，但固定拓扑可能跟不上动态新问题结构。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "G-ReAct", "definition": "在固定拓扑查询图上做结构—状态共演化的深度搜索推理框架。"},
        {"term": "Query graph", "definition": "把问题要素、约束与关系固定成图拓扑，搜索时更新节点/边状态。"},
        {"term": "Structure-state co-evolution", "definition": "图结构约束搜索路径，同时搜索过程持续写回图状态。"},
        {"term": "Deep search", "definition": "需多轮检索、验证与规划的开放域长程信息获取。"},
        {"term": "Inference-time scaffold", "definition": "不额外微调，仅在推理阶段用结构化脚手架引导已有强模型。"},
        {"term": "BrowseComp-ZH / XBench-DS", "definition": "偏网页/深搜难度的评测集；本文主报 pass@1。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：线性历史撑不住深搜",
            "body": "ReAct 轨迹越长，中间证据与约束越容易被冲淡。重复探索和搜索漂移，常常是状态表示问题，而不只是模型不够聪明。",
        },
        {
            "title": "固定图上的状态演化",
            "body": "先落查询图拓扑，再在节点/边上维护进度。后续动作由图状态约束，文本历史退居次要角色。",
        },
        {
            "title": "训练与推理同一脚手架",
            "body": "图轨迹可直接拿来 SFT；同一状态机也可在推理时挂到强模型上，先改善搜索效率再决定是否微调。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主质量（30B）",
                "论文证据": "OpenSeeker-v1 变体：BrowseComp-ZH 52.6、XBench-DS 79.0、BrowseComp 35.6、GAIA 64.2。",
                "飞哥判断": "深搜组织方式本身就能抬表现，不只是堆参数。",
            },
            {
                "看什么": "数据效率",
                "论文证据": "1.9K vs OpenSeeker-v1 11.7K 仍涨点；同池相对 DeepDive 大幅领先。",
                "飞哥判断": "图结构轨迹携带更强监督信号。",
            },
            {
                "看什么": "推理脚手架",
                "论文证据": "无微调时 doubao-seed-2.0-pro BrowseComp-ZH 64.71→71.28，工具调用下降。",
                "飞哥判断": "可先验证脚手架收益，再决定是否训练。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主基准偏 BrowseComp/XBench/GAIA；延迟与 token 完整成本账、企业开放搜索外推待补。",
                "飞哥判断": "先当深搜状态管理样本，别直接当通用企业检索银弹。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（主结果）；Table 2（推理时无微调）；同池对照叙述。",
        "版本戳：arXiv:2608.01324v1 [cs.AI]；ChatGPT 0804批次 #1（0805 主发）。",
        "单位：MiLM Plus, Xiaomi Inc. · Huazhong University of Science and Technology。",
        "证据覆盖：深搜准确率与工具调用；端到端延迟/token 账单需补读。",
    ],
    "so_what": "说白了，深搜Agent先别把上下文当成无限日记本。把分支、证据和约束写进可更新的查询图，训练与推理都能共用同一套状态纪律。",
    "feige_view": "别再把「多搜几轮」当成能力本体。先问状态能不能被读写复核。对照今日 Memory Reward Inflation：一个管搜索过程状态，一个管经验记忆评分。",
    "limitations": [
        "不过，固定图拓扑可能限制探索中动态长出的新问题结构。",
        "图状态抽取错误可能比普通文本遗漏更具系统性。",
        "主文准确率提升明确，但延迟、token 与工具成本完整账仍需补齐。",
        "BrowseComp/XBench/GAIA 不能完全代表开放科研与真实企业搜索。",
    ],
    "related_theme_picks": {
        "theme": "Agent 内部对象：状态、记忆与预算",
        "intro": "本篇讲深搜结构化状态；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.00017",
                "title_cn": "记忆奖励膨胀与Echo Gap",
                "one_liner": "同日配对：高分记忆也可能在放大错误。",
                "link": "https://arxiv.org/abs/2608.00017",
                "ready_date": "20260805",
            },
            {
                "arxiv_id": "2607.28642",
                "title_cn": "可学习中间接口重置",
                "one_liner": "0804：推理中途也要可继续状态。",
                "link": "https://arxiv.org/abs/2607.28642",
                "ready_date": "20260804",
            },
            {
                "arxiv_id": "2607.28069",
                "title_cn": "语义位置无关KV缓存",
                "one_liner": "0803：复用文档别反复 prefill。",
                "link": "https://arxiv.org/abs/2607.28069",
                "ready_date": "20260803",
            },
        ],
    },
    "target_audience": [
        "做网页/开放域深度搜索 Agent 的研究与平台团队。",
        "关心长程检索中状态遗忘与搜索漂移的工程负责人。",
        "评估「小样本图轨迹」能否替代海量 ReAct 轨迹的训练同学。",
    ],
    "sales_use_cases": [
        "回应『再加大上下文就能搜得更深』：先问分支证据与约束是否被显式管理。",
        "方案评审：要求看查询图状态字段、漂移率和同池数据效率对照。",
        "成本沟通：用 1.9K 轨迹 vs 更大 SFT/RL 流水线做监督信号密度对照。",
    ],
    "objection_handling": [
        "客户说：『多轮 ReAct 不够吗？』→ 回应：线性历史难稳住约束；论文用图状态同时抬准确率并降部分工具调用。",
        "客户说：『固定拓扑太死？』→ 回应：这是边界；但在现有深搜题型上，结构化状态收益已足够先验证。",
    ],
    "copy_paste_lines": [
        "深搜别只会堆历史：把分支、证据和约束写进查询图。",
        "1.9K 轨迹：BrowseComp-ZH 52.6 / XBench-DS 79.0。",
        "无微调挂脚手架，强模型 BrowseComp-ZH 也能再涨一截。",
    ],
    "key_quotes": [
        "state evolution over a fixed-topology query graph",
        "with only 1.9K generated trajectories",
        "when applied at inference time, G-ReAct consistently improves",
    ],
    "score_rationale": "G-ReAct把深度搜索做成查询图状态演化，数据效率与推理脚手架收益都清楚。Impact/Evidence/Applicability高；固定拓扑与成本账不全略扣Reusability。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "BrowseComp-ZH 52.6 / XBench-DS 79.0 / BrowseComp 35.6 / GAIA 64.2", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "1.9K vs OpenSeeker-v1 11.7K 仍涨 6.1/4.2/5.0", "evidence": "§4.2 / Table 1 narrative", "location": "§4.2"},
            {"claim": "同池相对 DeepDive：BrowseComp/ZH/XBench +15.8/+24.2/+26.0", "evidence": "§4.2", "location": "§4.2"},
            {"claim": "推理时无微调：doubao 64.71→71.28，工具调用下降", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "计划开源代码与权重", "evidence": "Abstract", "location": "Abstract"},
        ]
    },
}


MEMINFL_RICH = {
    "intro_lead": "",
    "A_research_problem": "许多自我改进 Agent 给历史经验打分，并优先检索高分段。部署期没有金标签时，评分靠 LLM 自评；错误经验一旦被系统性高估，会被反复召回并放大。",
    "B_core_contributions": [
        "定义 Echo Gap：错误记忆奖励被高估后，经检索复用持续放大",
        "提出 Error-Independence Assumption：纠偏信号须贴近真值，且与原评分误差去相关",
        "给出无答案标签去膨胀算法 LUCID，并在 BIRD 端到端验证",
    ],
    "C_method_framework": "把外部记忆检索看成隐式非参数策略更新：存分≈奖励，检索≈策略改善。若奖励来自自评，错误会因高分被重复暴露。论文证明同类确认型 judge 常复用同一盲点；真正有用的是与原偏差去相关的通道。LUCID 用答案无关信号标记过热记忆并下调效用。",
    "D_key_results": [
        "BIRD 执行准确率：LUCID 56.9% > 自评记忆 Agent 54.0% > 无记忆 52.4%（多 seed 均值）",
        "错误记忆自评 leniency 跨模型存在：Haiku 约 31%、GPT-5.4-mini 约 54%、GPT-5.4 约 41%",
        "检索型信息 verifier 更贴近 EIA；参数化 judge 面板误差仍相关（Corr(νi,νj)=+0.69）",
    ],
    "E_industry_implications": [
        "技能库/episodic memory 验收：查错误经验是否被高估并反复召回，而不只看高分库存",
        "纠偏通道优先执行/检索/测试信号，谨慎依赖同族 LLM 复评",
        "别默认「更多经验会平均掉偏差」——无标签记忆环可能固化自信错误",
    ],
    "F_one_line_judgement": "这篇最适合作经验记忆/技能库的 Agent：先查评分误差是否会自我放大；不过端到端主证在 BIRD，开放工具场景外推仍有限。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Echo Gap", "definition": "错误经验获得偏高奖励后被优先检索，导致偏差经记忆循环放大。"},
        {"term": "EIA", "definition": "Error-Independence Assumption：纠偏信号须贴近真值且与原评分误差去相关。"},
        {"term": "LUCID", "definition": "Leniency-corrected Utility Calibration via answer-free de-inflation；无答案标签的去膨胀算法。"},
        {"term": "Leniency", "definition": "错误记忆仍被自评为正确的概率 Pr[self=correct | U=0]。"},
        {"term": "Memory reward inflation", "definition": "无金标签时，LLM 自评系统抬高错误经验效用的现象。"},
        {"term": "BIRD EX", "definition": "BIRD text-to-SQL 官方执行准确率（execution accuracy）。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：高分经验也会带毒",
            "body": "没有金标签时，记忆分数多半是模型自评。错得最自信的轨迹，往往也最容易进高分库。",
        },
        {
            "title": "为何再加一个 judge 不够",
            "body": "同类参数化复评常共享同一盲点。信号若与原误差相关，只会把错误排序再盖一次章。",
        },
        {
            "title": "LUCID：无标签下调过热记忆",
            "body": "用答案无关、更满足 EIA 的信号标记过热记忆并降权；不改模型权重，只校准记忆效用。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "端到端增益",
                "论文证据": "BIRD：LUCID 56.9% vs 自评记忆 54.0% vs 无记忆 52.4%。",
                "飞哥判断": "增益不大但方向稳定：先止血记忆自膨胀。",
            },
            {
                "看什么": "失败模式普遍性",
                "论文证据": "多模型家族错误记忆 leniency 可观（约 31%–54%）。",
                "飞哥判断": "不是某一家小模型的偶发问题。",
            },
            {
                "看什么": "纠偏条件",
                "论文证据": "检索型 verifier 更贴近 EIA；参数化 judge/面板仍误差相关。",
                "飞哥判断": "选通道比「再找更强裁判」更关键。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "端到端主战场是 BIRD text-to-SQL；网页/代码/开放任务外推待补。",
                "飞哥判断": "先当记忆治理诊断样板，别直接当通用 Agent 银弹。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 2（leniency）；Table 4（去膨胀 payoff）；Table 5（BIRD 端到端）。",
        "版本戳：arXiv:2608.00017v1 [cs.AI]；ChatGPT 0804批次 #2（0805 主发）。",
        "单位：University of North Texas · Edge Hill University · University of Cincinnati · Iran University of Science and Technology · Islamic Azad University。",
        "证据覆盖：BIRD + 记忆银行诊断；开放工具 Agent 场景需外推。",
    ],
    "so_what": "说白了，经验记忆会保存能力，也会保存并放大自信的错误。验收时先问纠偏信号是否真的与原评分盲点去相关；会点头的同类裁判补不上这一刀。",
    "feige_view": "别把「存高分经验」默认等于可持续自我提升。对照今日 G-ReAct：一个管搜索状态怎么写，一个管记忆分数能不能信。",
    "limitations": [
        "不过，理论条件成立，不代表实际系统容易拿到真正误差独立的信号。",
        "端到端实证重点是 BIRD text-to-SQL，网页/代码/开放任务仍待覆盖。",
        "LUCID 效果取决于代理纠偏信号质量与 flagged 集精度。",
        "绝对增益稳健但有限（约 +2.9 分相对自评记忆基线）。",
    ],
    "related_theme_picks": {
        "theme": "Agent 内部对象：状态、记忆与预算",
        "intro": "本篇讲记忆奖励膨胀；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.01324",
                "title_cn": "图引导深度搜索状态",
                "one_liner": "同日配对：深搜也要把状态显式写出来。",
                "link": "https://arxiv.org/abs/2608.01324",
                "ready_date": "20260805",
            },
            {
                "arxiv_id": "2607.28642",
                "title_cn": "可学习中间接口重置",
                "one_liner": "0804：推理中途接口是否可继续。",
                "link": "https://arxiv.org/abs/2607.28642",
                "ready_date": "20260804",
            },
            {
                "arxiv_id": "2607.27415",
                "title_cn": "行动图正负价值记忆",
                "one_liner": "0801：经验复用别从零搜索。",
                "link": "https://arxiv.org/abs/2607.27415",
                "ready_date": "20260801",
            },
        ],
    },
    "target_audience": [
        "做 Agent 技能库、episodic memory、自动反思系统的团队。",
        "关心无标签自我进化风险的产品与治理负责人。",
        "评估 LLM-as-judge 能否校准经验库的研究/工程同学。",
    ],
    "sales_use_cases": [
        "回应『记忆越多 Agent 越强』：先问错误高分经验有没有被反复召回。",
        "方案评审：要求看 leniency、复用分布，以及纠偏通道是否满足 EIA。",
        "成本沟通：用 BIRD +2.9 对照说明——小幅稳住记忆质量，可能避免系统性偏差扩散。",
    ],
    "objection_handling": [
        "客户说：『换更强 judge 就行』→ 回应：论文显示相关误差的裁判再强也可能复写同一偏见。",
        "客户说：『涨点不大值得做吗？』→ 回应：Echo Gap 是循环放大机制；先止血往往比再堆经验划算。",
    ],
    "copy_paste_lines": [
        "高分记忆也可能在放大自信错答案。",
        "BIRD：LUCID 56.9 vs 自评记忆 54.0 vs 无记忆 52.4。",
        "纠偏信号要与原评分误差去相关，而不只是更会点头。",
    ],
    "key_quotes": [
        "Echo Gap",
        "Error-Independence Assumption",
        "raises execution accuracy to 56.9%",
    ],
    "score_rationale": "Echo Gap与EIA把经验记忆的失败模式讲清楚，LUCID给出可部署去膨胀路径。Impact/Novelty高；端到端增益稳健但场景偏窄，Evidence/Applicability略克制。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "BIRD：LUCID 56.9% / 自评记忆 54.0% / 无记忆 52.4%", "evidence": "Table 5 / Abstract", "location": "Table 5"},
            {"claim": "错误记忆 leniency：Haiku ~31% / GPT-5.4-mini ~54% / GPT-5.4 ~41%", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "检索型 verifier 去膨胀 payoff 显著高于参数化重评", "evidence": "Table 4", "location": "Table 4"},
            {"claim": "参数化 judge 面板误差相关 Corr(νi,νj)=+0.69", "evidence": "§4.2", "location": "§4.2"},
            {"claim": "EIA 是纠偏必要条件，而非可有可无的好味道描述", "evidence": "Abstract / §3.3", "location": "Abstract / §3.3"},
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
                    "rationale": f"{'最高维' if d['label'] in highest else ('最低维' if d['label'] in lowest else '中间维')}：{rich.get('score_rationale', '')[:180]}",
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
        "2608.01324",
        "greact",
        GREACT_RICH,
        "别再靠线性轨迹搜：G-ReAct用查询图管状态，1.9K轨迹BrowseComp-ZH达52.6%",
        "G-ReAct把深度搜索改成固定拓扑查询图上的状态演化：显式跟踪分支、证据与约束，训练与推理时共用同一脚手架。",
    )
    enrich_one(
        "2608.00017",
        "meminfl",
        MEMINFL_RICH,
        "别只会存高分经验：记忆自评会放大自信错答案，LUCID把BIRD准确率抬到56.9%",
        "Memory Reward Inflation指出自评记忆奖励会形成Echo Gap；有效纠偏信号必须与原始误差去相关，LUCID给出无标签去膨胀路径。",
    )
    print("enriched greact + meminfl")


if __name__ == "__main__":
    main()
