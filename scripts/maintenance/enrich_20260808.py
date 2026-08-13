#!/usr/bin/env python3
"""One-off enrichment for 20260808 paper-notes payloads (Skill Entropy + SearchAuditor)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260808"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


SKILLENTROPY_RICH = {
    "intro_lead": "",
    "A_research_problem": "长程任务常要在同一推理链里切换不同技能，例如先做数学推导再做日程规划。现有评测多看单技能，难以度量切换难度，更难把它变成训练信号。",
    "B_core_contributions": [
        "提出 Skill Entropy：量化从一技能切到另一技能的难度",
        "发布 Skill²-Bench：558 技能 × 9 域，按任务级技能熵分档",
        "Skill-Entropy RL：步骤正确性 + 预测技能序列与金标对齐",
    ],
    "C_method_framework": "先定义跨技能长程任务与 Skill Entropy，再构建覆盖 558 技能、9 域的 Skill²-Bench；最后用 Skill-Entropy RL 同时预测答案与所用技能，用步骤正确性与技能序列对齐奖励联合优化。",
    "D_key_results": [
        "8 个 frontier 与 4 个开源模型：高熵任务准确率近乎单调下降",
        "Qwen3-4B-Instruct：Skill²-Bench 34.4%→68.4%；Qwen3-1.7B：14.6%→40.1%",
        "同一管线可接到 OpenR1-Math 等现成数据，技能熵可复用为训练信号",
    ],
    "E_industry_implications": [
        "长程 Agent/推理评测：除单技能分，还要报技能切换熵档表现",
        "训练方案：让模型显式预测技能序列，而不只刷最终答案",
        "数据方案：可把技能熵标注接到现有数学等可验证语料",
    ],
    "F_one_line_judgement": "这篇最适合做长程推理评测与训练的团队：用技能熵标尺暴露切换掉点，再用对齐技能序列的 RL 抬分；不过开放域步骤依赖 LLM judge，独立复现仍关键。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Skill Entropy", "definition": "衡量从一种推理技能切换到另一种技能有多难的标尺；越高表示切换越难。"},
        {"term": "Skill²-Bench", "definition": "跨技能长程推理基准，覆盖 558 技能、9 个可验证/开放域，按任务级技能熵分档。"},
        {"term": "Cross-skill long-horizon task", "definition": "多步任务，每步调用不同技能，且后续步骤依赖前面输出。"},
        {"term": "Skill-Entropy RL", "definition": "同时预测答案与所用技能，并用技能序列对齐奖励训练的强化学习框架。"},
        {"term": "Skill sequence alignment", "definition": "模型预测的技能链与金标技能链是否一致，作为训练信号。"},
        {"term": "OpenR1-Math", "definition": "现成可验证数学训练数据；论文用同一管线证明技能熵可迁移接入。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：单技能分看不出切换断点",
            "body": "模型在孤立技能上可能很强，但一旦要把数学结果接到规划、检索等后续技能，准确率会系统性下滑。缺的是切换难度本身的度量。",
        },
        {
            "title": "用技能熵给任务分档",
            "body": "Skill Entropy 把「从技能 A 切到技能 B」的难度做成标尺；Skill²-Bench 再按任务级熵分成低/中/高，暴露切换掉点。",
        },
        {
            "title": "把熵变成训练奖励",
            "body": "Skill-Entropy RL 不只奖励答对，还要求模型预测技能序列并对齐金标，让切换本身可优化。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "评测发现",
                "论文证据": "8 frontier + 4 开源：高熵任务准确率近乎单调下降。",
                "飞哥判断": "单技能榜单会掩盖切换脆性。",
            },
            {
                "看什么": "训练增益",
                "论文证据": "Qwen3-4B 34.4%→68.4%；Qwen3-1.7B 14.6%→40.1%。",
                "飞哥判断": "显式技能序列监督有杠杆。",
            },
            {
                "看什么": "可复用性",
                "论文证据": "同一管线可接到 OpenR1-Math 等现成数据。",
                "飞哥判断": "不必从零造技能标注语料。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "开放域步骤用 LLM judge；参考模型与技能标签管线会影响熵估计。",
                "飞哥判断": "当评测+训练信号样板，别当唯一难度真源。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Qwen3-4B 34.4%→68.4%；Qwen3-1.7B 14.6%→40.1%；558 skills / 9 domains。",
        "版本戳：arXiv:2608.05139v1 [cs.CL]；Grok 0807/0808 热度 #1（0808 主发）。",
        "单位：Princeton；CMU；Toronto；UIUC；Stanford；Oxford。",
        "开源入口：github.com/Gen-Verse/Skill-Entropy-RL。",
        "证据覆盖：跨技能评测与小模型 RL；开放域 judge 与独立复现仍关键。",
    ],
    "so_what": "说白了，长程推理别只问「会不会做题」。先问技能切换有多难，再让模型把技能序列说清楚、对齐金标。",
    "feige_view": "别只堆单技能榜。对照同日 SearchAuditor：一个管「切换难度怎么量与练」，一个管「搜错了怎么定位与修」。",
    "limitations": [
        "不过，开放域步骤依赖 LLM judge，评分噪声会影响结论。",
        "技能标签与参考模型选择会影响熵估计本身。",
        "主增益集中在 Qwen3 小模型设定，跨家族外推仍需验证。",
        "真实 Agent 环境的技能边界往往比基准更模糊。",
    ],
    "related_theme_picks": {
        "theme": "长程能力：技能切换与失败审计",
        "intro": "本篇讲技能切换如何度量与训练；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.05212",
                "title_cn": "长程搜索失败审计",
                "one_liner": "同日配对：执行侧要把关键错误定位到步。",
                "link": "https://arxiv.org/abs/2608.05212",
                "ready_date": "20260808",
            },
            {
                "arxiv_id": "2608.05144",
                "title_cn": "可验证运行时自演化",
                "one_liner": "0807：技能准入也要验证门控。",
                "link": "https://arxiv.org/abs/2608.05144",
                "ready_date": "20260807",
            },
            {
                "arxiv_id": "2608.05102",
                "title_cn": "答案反推的搜索步骤归因",
                "one_liner": "0807：训练侧也要把终局奖励拆到中间步。",
                "link": "https://arxiv.org/abs/2608.05102",
                "ready_date": "20260807",
            },
        ],
    },
    "target_audience": [
        "做长程推理评测与训练的研究工程团队。",
        "关心 Agent/LLM 技能编排与切换脆性的架构同学。",
        "希望把现有可验证语料升级为技能序列监督的数据同学。",
    ],
    "sales_use_cases": [
        "回应『我们单技能榜很高』：先问高熵跨技能任务掉了多少。",
        "方案评审：要求看技能熵分档、技能序列预测与对齐奖励。",
        "训练沟通：用 34.4%→68.4% 说明显式技能监督的杠杆。",
    ],
    "objection_handling": [
        "客户说：『不就是多跳推理吗？』→ 回应：关键是切换难度可度量，并能变成训练信号。",
        "客户说：『我们没有技能标签。』→ 回应：论文给出标注管线，也可接到 OpenR1-Math 类现成数据。",
    ],
    "copy_paste_lines": [
        "别再只测单技能：用技能熵看切换掉点。",
        "Qwen3-4B：Skill²-Bench 34.4%→68.4%。",
        "让模型预测技能序列，而不只刷最终答案。",
    ],
    "key_quotes": [
        "accuracy decreases on higher-entropy tasks",
        "improves the Skill2-Bench score from 34.4% to 68.4%",
        "skill entropy is a reusable training signal",
    ],
    "score_rationale": "Skill Entropy把跨技能切换做成可度量标尺与RL信号，Qwen3增益清楚。Impact/Novelty高；开放域judge使Evidence略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty"],
        "lowest_dimensions": ["可验证性 Evidence"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "长程推理/Agent 的核心瓶颈之一正是跨技能切换，而不只是单技能强弱。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "把切换难度形式化为熵标尺，并同时用于评测分档与 RL 奖励。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "lowest", "rationale": "主数字可核，但开放域步骤依赖 LLM judge，熵估计受参考模型影响。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "评测清单与训练配方可直接进长程推理/Agent 方案。"},
            {"label": "可复用性 Reusability", "value": 1.8, "role": "middle", "rationale": "有开源与现成语料接入路径；真实技能边界模糊仍是落地负担。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "Qwen3-4B-Instruct：34.4%→68.4%", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "Qwen3-1.7B：14.6%→40.1%", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "558 skills across 9 domains", "evidence": "Abstract / §3", "location": "Abstract"},
            {"claim": "高熵任务准确率近乎单调下降", "evidence": "Abstract / Table 2", "location": "Table 2"},
            {"claim": "可接到 OpenR1-Math 等现成数据", "evidence": "Abstract", "location": "Abstract"},
        ]
    },
}


SEARCHAUDITOR_RICH = {
    "intro_lead": "",
    "A_research_problem": "深搜 Agent 轨迹动辄数十轮、数万 token。第 17 步的小错可能到第 70 步才变成错答。靠人翻轨迹定位关键错误不可扩展，系统缺少可复现的失败审计能力。",
    "B_core_contributions": [
        "将长程搜索失败拆成 localization → attribution → repair",
        "SearchAuditBench：1,243 条失败轨迹，均值 73.1 消息 / 65.1K tokens，专家标关键步与根因",
        "多视角证据裁决 + 可回接轨迹的修复恢复",
    ],
    "C_method_framework": "SearchAuditBench 用专家标注失败轨迹评测 auditor；SearchAuditor 并行多视角审计，经证据驱动裁决后输出关键步、根因与修复，并可从故障点恢复执行。",
    "D_key_results": [
        "GPT-5.5 最强基线端到端通过率仅 26.6%；SearchAuditor 提到 32.3%",
        "关键错误中 45.9% 属推理侧；Candidate Mismanagement 占 27.2%",
        "修复后 Kimi-K2.6 失败轨迹恢复：约 34.0%→45.1%",
    ],
    "E_industry_implications": [
        "搜索 Agent 产品验收：除最终正确率，还要能审计关键失败步",
        "可观测性建设：轨迹日志要支持定位、归因、修复闭环",
        "自动修复可接回执行，但成本与误修风险需单独评估",
    ],
    "F_one_line_judgement": "这篇最适合做 Deep Research 与搜索 Agent 工程的团队：把失败轨迹拆成定位、归因、修复；不过端到端通过率仍低，专家标注有主观性，修复也不等于整条状态已纠正。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "SearchAuditor", "definition": "对长程搜索失败轨迹做多视角审计、证据裁决与修复合成的框架。"},
        {"term": "SearchAuditBench", "definition": "1,243 条专家标注失败搜索轨迹基准，评测定位、归因与修复。"},
        {"term": "Critical error localization", "definition": "找出真正导致终局失败的关键步骤，而不是只看最后答错。"},
        {"term": "Attribution / root cause", "definition": "给关键步贴上搜索特定根因，例如候选管理失误、约束忽略等。"},
        {"term": "Repair & resume", "definition": "给出修复方案并从故障点恢复执行，而不只做离线解释。"},
        {"term": "FPS (fully-passed score)", "definition": "端到端通过率：诊断与修复都过关的比例；本文主报 32.3% vs 基线 26.6%。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：终局错答掩盖第一次关键错",
            "body": "长程搜索里，错误会沿轨迹传播。只看最终答案，无法告诉工程团队该回滚到哪一步、为什么错、怎么修。",
        },
        {
            "title": "专家标注长轨迹失败语料",
            "body": "SearchAuditBench 收集 1,243 条失败轨迹，平均 73.1 消息、65.1K tokens，并标注关键步、根因与参考修复。",
        },
        {
            "title": "多视角审计后再裁决修复",
            "body": "SearchAuditor 并行提出候选诊断，用证据驱动裁决，再合成可执行修复，并可接回 Agent 继续跑。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "审计主结果",
                "论文证据": "GPT-5.5 最强基线 FPS 26.6%；SearchAuditor 32.3%。",
                "飞哥判断": "有提升，但绝对水平仍说明难题未解决。",
            },
            {
                "看什么": "失败画像",
                "论文证据": "45.9% 关键错误在推理侧；Candidate Mismanagement 27.2%。",
                "飞哥判断": "很多不是「不会搜」，而是搜到后管不好候选。",
            },
            {
                "看什么": "修复闭环",
                "论文证据": "修复后 Kimi-K2.6 失败恢复约 34.0%→45.1%。",
                "飞哥判断": "审计不只解释，还能改善后续执行。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "CS-Strict 仍不足半；专家关键步标注有主观性；开放新错型覆盖有限。",
                "飞哥判断": "当可观测性样板，别当自动排障银弹。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；FPS 26.6%→32.3%；1,243 trajectories；73.1 msg / 65.1K tokens；Kimi-K2.6 34.0%→45.1%。",
        "版本戳：arXiv:2608.05212v1 [cs.AI]；ChatGPT 0807批次 #1（0808 主发）。",
        "单位：University of Illinois Urbana-Champaign；Joy Future Academy, JD。",
        "开源入口：github.com/lzzzx666/SearchAuditor（论文声明将发布）。",
        "证据覆盖：深搜失败审计；开放环境新错型与绝对通过率仍是短板。",
    ],
    "so_what": "说白了，搜索 Agent 别只盯最终对错。先把轨迹做成可审计对象：错在哪一步、什么根因、修完能不能继续跑。",
    "feige_view": "别把「再搜一轮」当成唯一补救。对照同日 Skill Entropy：一个管技能切换怎么量与练，一个管搜错了怎么定位与修。",
    "limitations": [
        "不过，端到端通过率仍只有约三分之一，frontier auditor 远未解决。",
        "专家关键步标注本身有主观性，会影响评测上限。",
        "修复局部错误不一定纠正后续已累积的错误状态。",
        "额外 frontier 模型审计会显著增加成本。",
    ],
    "related_theme_picks": {
        "theme": "长程能力：技能切换与失败审计",
        "intro": "本篇讲搜索失败如何定位修复；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.05139",
                "title_cn": "技能熵与跨技能训练",
                "one_liner": "同日配对：评测/训练侧也要把技能切换做成信号。",
                "link": "https://arxiv.org/abs/2608.05139",
                "ready_date": "20260808",
            },
            {
                "arxiv_id": "2608.05102",
                "title_cn": "答案反推的搜索步骤归因",
                "one_liner": "0807：训练侧给搜索中间步打分。",
                "link": "https://arxiv.org/abs/2608.05102",
                "ready_date": "20260807",
            },
            {
                "arxiv_id": "2608.05144",
                "title_cn": "可验证运行时自演化",
                "one_liner": "0807：执行侧用验证门控积累经验。",
                "link": "https://arxiv.org/abs/2608.05144",
                "ready_date": "20260807",
            },
        ],
    },
    "target_audience": [
        "做 Deep Research / 网页搜索 Agent 的工程团队。",
        "建设 Agent 可观测性与轨迹调试能力的平台同学。",
        "关心长程失败自动定位与恢复的研究工程同学。",
    ],
    "sales_use_cases": [
        "回应『再加大模型/再加搜索轮次』：先问能不能定位第一次关键错误。",
        "方案评审：要求看轨迹审计、根因分类与修复回接能力。",
        "验收沟通：用 FPS 26.6%→32.3% 说明自动审计仍难，但方向对。",
    ],
    "objection_handling": [
        "客户说：『最终答对不就行？』→ 回应：长程系统还要知道错在哪一步，否则无法持续改进。",
        "客户说：『32% 通过率太低。』→ 回应：论文也承认；价值在把不可扩展的人肉翻轨迹变成可评测闭环。",
    ],
    "copy_paste_lines": [
        "别再只看最终答错：先定位第一次关键错误。",
        "SearchAuditor：端到端通过率 26.6%→32.3%。",
        "修复后还能从故障点恢复执行。",
    ],
    "key_quotes": [
        "1,243 failed trajectories, averaging 73.1 messages and 65.1K tokens",
        "end-to-end pass rate of 32.3%",
        "resuming failed runs with its repairs enables agents to better recover",
    ],
    "score_rationale": "SearchAuditor把长程搜索失败做成定位/归因/修复闭环，基准与数字清楚。Impact/Novelty高；绝对通过率低与标注主观性使Evidence略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty"],
        "lowest_dimensions": ["可验证性 Evidence"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "长程搜索 Agent 可调试性与故障恢复，几乎与任务成功率同等重要。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "把失败审计拆成定位/归因/修复，并用专家长轨迹基准系统评测。"},
            {"label": "可验证性 Evidence", "value": 1.7, "role": "lowest", "rationale": "主数字可核，但绝对通过率仍低，专家关键步标注有主观性。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "直接对应 Agent 可观测性与排障产品需求；成本与误修需单列。"},
            {"label": "可复用性 Reusability", "value": 1.8, "role": "middle", "rationale": "框架可迁移到其他长程工具轨迹；开放新错型覆盖仍有限。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "端到端通过率 26.6%→32.3%", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "1,243 failed trajectories；73.1 messages；65.1K tokens", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "45.9% 关键错误属推理侧；Candidate Mismanagement 27.2%", "evidence": "Introduction / analysis", "location": "§1"},
            {"claim": "Kimi-K2.6 修复后恢复约 34.0%→45.1%", "evidence": "Abstract / experiments", "location": "Abstract"},
            {"claim": "GPT-5.5 CS-Strict 44.89%", "evidence": "Experiments", "location": "§5"},
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

    # Keep card title_cn aligned
    if "info" in data and "title_cn" not in data["info"]:
        pass

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
        "2608.05139",
        "skillentropy",
        SKILLENTROPY_RICH,
        "别再只测单技能：Skill Entropy用切换难度标尺训练长程推理，Qwen3-4B从34.4%到68.4%",
        "长程推理的关键不只是会不会某个技能，而是技能切换有多难、模型能不能对齐技能序列。",
    )
    enrich_one(
        "2608.05212",
        "searchauditor",
        SEARCHAUDITOR_RICH,
        "别再只看最终答错：SearchAuditor定位长程搜索关键错误，端到端通过率提到32.3%",
        "长程搜索Agent真正难的是找到第一次关键错误，并把它修到能继续跑。",
    )
    print("enriched skillentropy + searchauditor")


if __name__ == "__main__":
    main()
