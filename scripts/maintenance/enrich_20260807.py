#!/usr/bin/env python3
"""One-off enrichment for 20260807 paper-notes payloads (Argus + ABSeeker)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260807"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


ARGUS_RICH = {
    "intro_lead": "",
    "A_research_problem": "长程任务里用户意图往往稳定，但操作目标、约束与验证标准会随证据变化。允许改目标，看起来像合理化失败；禁止改目标，又会把错误规格锁死。缺的是把修订做成可审计、可累积状态的运行时。",
    "B_core_contributions": [
        "分离稳定用户意图与可变操作目标、约束、验证标准",
        "验证门控准入：记忆、技能、验证器、路由与失败路径经审查后才持久化",
        "固定模型权重，自演化发生在持久运行时状态与控制策略",
    ],
    "C_method_framework": "Argus 以 Manager、Planner、Engineer、Reviewer 在持久项目状态上执行有限任务。工作契约把稳定意图与可变目标分开；候选记忆、技能、程序、验证器、路由决策与被否定路径，只有经角色审查或任务原生验证后才进入长期状态。模型权重保持固定。",
    "D_key_results": [
        "SWE-Bench Pro 约 78% vs Direct Copilot 59%，总 token 约 1.41 倍",
        "成熟 Wave：solve 输入 token 降 21%，活动工时降 15%；记录 34 次验证器恢复、22 次严格审查救援",
        "AARRI-Bench 76.8%；另覆盖数学数据合成、GPU kernel、模型训练与多日研究",
    ],
    "E_industry_implications": [
        "Agent 产品验收：先问运行时有没有验证门控与失败路径沉淀，而不是只问模型版本",
        "长程工程/研究场景优先投可审计状态层，再谈权重微调",
        "成本账按任务重复度算：初期 token 更高，收益来自经验复用",
    ],
    "F_one_line_judgement": "这篇最适合做长程工程与研究 Agent 的团队：把自我改进放在可验证运行时，而不是反复改权重；不过多组件难归因，初期 token 成本更高，独立复现仍关键。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Argus", "definition": "固定模型权重、用验证门控持久状态做自演化的通用长程 Agent 运行时。"},
        {"term": "Verification-gated admission", "definition": "候选记忆/技能/路由/失败路径，经角色审查或任务原生验证后才写入长期状态。"},
        {"term": "Manager / Planner / Engineer / Reviewer", "definition": "围绕持久项目状态执行有限任务的四类角色分工。"},
        {"term": "SWE-Bench Pro", "definition": "仓库级软件工程基准，带可执行验收测试；本文主报约 78% vs Direct Copilot 59%。"},
        {"term": "AARRI-Bench", "definition": "研究生命周期细粒度任务基准；本文报 76.8%。"},
        {"term": "Runtime self-evolution", "definition": "不改权重，通过持久运行时状态与控制策略积累可复用能力。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：改目标像失败，不改又锁死错误规格",
            "body": "长程研究与工程里，意图可稳定，但操作目标常被证据改写。没有审计的转向像合理化失败；完全禁止转向又会把 misspecification 固化。",
        },
        {
            "title": "四角色 + 持久项目状态",
            "body": "Manager/Planner/Engineer/Reviewer 在可持久的项目状态上跑有限任务；稳定意图与可变目标、约束、验证标准分开记账。",
        },
        {
            "title": "验证门控才准入长期经验",
            "body": "记忆、技能、验证器、路由与被否定路径，不是随手写入。要过角色审查或任务原生验证，才成为后续任务可复用状态。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "软件工程主结果",
                "论文证据": "SWE-Bench Pro 约 78% vs Direct Copilot 59%；总 token 约 1.41×。",
                "飞哥判断": "能力抬升明显，但先付更多 token。",
            },
            {
                "看什么": "运行时成熟后的成本",
                "论文证据": "成熟 Wave 相对 startup：solve 输入 token −21%，活动工时 −15%。",
                "飞哥判断": "重复任务才谈得上「经验复用」账。",
            },
            {
                "看什么": "恢复与拒止",
                "论文证据": "34 次验证器恢复、22 次严格审查救援；另有任务被显式 blocked 而非伪完成。",
                "飞哥判断": "这比只报最终成功率更像真实长程系统。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "多组件系统、特定模型与内部 arena；增益归因与独立复现仍关键。",
                "飞哥判断": "当 harness 路线样板，别当一键银弹。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；SWE-Bench Pro ≈78%/59%/1.41×；成熟 Wave −21%/−15%；34/22 恢复计数；AARRI-Bench 76.8%。",
        "版本戳：arXiv:2608.05144v1 [cs.AI]；ChatGPT 0806批次 #1（0807 主发）。",
        "单位：Microsoft；Shanghai Jiao Tong University（另有复旦/南大/清华/港大等）。",
        "开源入口：github.com/lbx154/Argus；argusbot.cn。",
        "证据覆盖：长程 harness 与软件工程主结果；跨任务增益归因待独立复现。",
    ],
    "so_what": "说白了，长程 Agent 别只盯着改权重或加提示。先把可验证的运行时状态建起来：哪些技能能进、哪些失败路径要记住、谁有权改目标。",
    "feige_view": "别把「模型升级」当成唯一扩展路径。对照同日 ABSeeker：一个管运行时怎么积累经验，一个管训练时怎么给中间步打分。",
    "limitations": [
        "不过，系统组件多，性能增益难拆到单一模块。",
        "主结果依赖特定模型、运行时与内部 benchmark arena，独立复现仍重要。",
        "初期 token 更高；成本收益依赖任务重复度与长期经验复用。",
        "持久保存技能与失败路径会引入版本冲突、错误累积与安全治理问题。",
    ],
    "related_theme_picks": {
        "theme": "长程 Agent：可验证状态与可归因步骤",
        "intro": "本篇讲运行时如何积累经验；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.05102",
                "title_cn": "答案反推的搜索步骤归因",
                "one_liner": "同日配对：训练侧也要把终局奖励拆到中间步。",
                "link": "https://arxiv.org/abs/2608.05102",
                "ready_date": "20260807",
            },
            {
                "arxiv_id": "2608.03463",
                "title_cn": "分层长期记忆",
                "one_liner": "0806：记忆也要按画像/事件/记录分流。",
                "link": "https://arxiv.org/abs/2608.03463",
                "ready_date": "20260806",
            },
            {
                "arxiv_id": "2608.03468",
                "title_cn": "功能级工具工作流",
                "one_liner": "0806：工具经验也要从 API 抬一层。",
                "link": "https://arxiv.org/abs/2608.03468",
                "ready_date": "20260806",
            },
        ],
    },
    "target_audience": [
        "做长程工程、研究与软件 Agent harness 的团队。",
        "关心固定模型下如何持续提升执行能力的架构负责人。",
        "评估「自我演化」是否应落在权重还是运行时的研究工程同学。",
    ],
    "sales_use_cases": [
        "回应『我们换更大模型就行』：先问运行时是否有验证门控与失败路径沉淀。",
        "方案评审：要求看意图/目标分离、准入门控与 Reviewer 救援计数。",
        "成本沟通：用 1.41× 起步 token 与成熟后 −21% 对照说明重复任务账。",
    ],
    "objection_handling": [
        "客户说：『不就是多 Agent 分工吗？』→ 回应：关键是验证门控准入与持久状态，不是角色名字。",
        "客户说：『token 更贵怎么省？』→ 回应：论文也报初期更贵；成熟后靠经验复用降输入 token 与工时。",
    ],
    "copy_paste_lines": [
        "长程自演化别只改权重：先建可验证运行时。",
        "SWE-Bench Pro：约 78% vs Direct Copilot 59%。",
        "成熟后输入 token 降 21%，活动工时降 15%。",
    ],
    "key_quotes": [
        "model weights remain fixed, so self-evolution occurs in the persistent runtime state",
        "approximately 78% on SWE-Bench Pro versus 59% for Direct Copilot",
        "21% fewer solve input Tokens and 15% less active workflow time",
    ],
    "score_rationale": "Argus把长程自演化做成验证门控运行时，SWE-Bench Pro与成熟后成本账清楚。Impact/Novelty高；多组件归因与内部arena使Evidence略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty"],
        "lowest_dimensions": ["可验证性 Evidence"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "固定模型下如何持续提升长程执行，是 Agent 产品与 harness 的核心扩展问题。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "把意图/目标分离 + 验证门控持久状态作为自演化载体，范围大于只改技能库或轨迹记忆。"},
            {"label": "可验证性 Evidence", "value": 1.7, "role": "lowest", "rationale": "主数字可核，但多组件系统难归因，且依赖特定模型与内部 arena。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "有开源与工程叙事；适合长程软件/研究 Agent 验收清单。"},
            {"label": "可复用性 Reusability", "value": 1.8, "role": "middle", "rationale": "运行时思路可迁移；持久技能版本冲突与安全治理仍是落地负担。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "SWE-Bench Pro 约 78% vs Direct Copilot 59%", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "总 token 约 1.41×", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "成熟 Wave：solve 输入 token −21%，活动工时 −15%", "evidence": "Abstract / RQ2", "location": "Abstract"},
            {"claim": "34 verifier recoveries；22 strict review-loop rescues", "evidence": "Abstract", "location": "Abstract"},
            {"claim": "AARRI-Bench 76.8%", "evidence": "Abstract", "location": "Abstract"},
        ]
    },
}


ABSEEKER_RICH = {
    "intro_lead": "",
    "A_research_problem": "长程搜索通常只有最终答案对错的稀疏奖励。成功轨迹可能含冗余搜索，失败轨迹也可能含关键取证。若整条轨迹统一当正/负样本，模型很难学会真正推进证据链的动作。",
    "B_core_contributions": [
        "Answer-Backtracked Clue Recovery：从标准答案反推必要中间线索",
        "Clue-Anchored Step Scoring：按是否推进证据链给每步打分",
        "ABC-SFT / ABC-GRPO：把步骤分接到监督重加权与强化学习奖励",
    ],
    "C_method_framework": "ABC 先从问题与标准答案反推实体、事实、关系等中间线索；再对轨迹每步做线索锚定评分，区分推进证据、冗余搜索与错误推断。ABC-SFT 按步骤价值重加权损失；ABC-GRPO 直接把步骤分用作 GRPO 奖励。",
    "D_key_results": [
        "Qwen3.5-4B + 8.5k：BrowseComp / BrowseComp-ZH 37.3% / 39.1%",
        "加上下文管理后 55.3% / 52.9%，接近约 30B 搜索 Agent",
        "另报 xbench-2505 77.0%、xbench-2510 46.0%、GAIA-text 81.6%",
    ],
    "E_industry_implications": [
        "Deep Research / 搜索 Agent 训练：先建步骤级过程奖励，再谈堆更大模型",
        "数据方案评审：要求能区分有效取证与空转浏览，而不是只留成功轨迹",
        "开放式任务仍需另找无标准答案的过程监督替代",
    ],
    "F_one_line_judgement": "这篇最适合训练 Deep Research 与长程搜索 Agent：用答案反推线索给中间步打分；不过依赖标准答案，真正开放研究还不能直接套，且上下文管理贡献需拆开看。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "ABSeeker", "definition": "基于答案反推信用分配训练的长程搜索 Agent（Qwen3.5-4B）。"},
        {"term": "ABC", "definition": "Answer-Backtracked Credit Assignment：从答案反推线索并为每步打分的框架。"},
        {"term": "Clue Recovery", "definition": "从标准答案回溯解题所需实体、事实与关系等中间线索。"},
        {"term": "Clue-Anchored Step Scoring", "definition": "用线索集评估每步是否发现、核验、精炼或错误推理。"},
        {"term": "ABC-SFT / ABC-GRPO", "definition": "按步骤分重加权 SFT；以及把步骤分用作 GRPO 奖励的 RL。"},
        {"term": "BrowseComp / BrowseComp-ZH", "definition": "多约束网页浏览搜索基准；本文主报 37.3%/39.1%，含上下文管理后 55.3%/52.9%。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：终局对错太稀疏",
            "body": "长程搜索里，成功不等于每步都对，失败也不等于每步都废。只做轨迹级监督，会把空转与有效取证混在一起。",
        },
        {
            "title": "从答案反推必要线索",
            "body": "有标准答案后，任务可回溯：先恢复解题必须碰到的实体、事实与关系，再把它当作步骤评分锚点。",
        },
        {
            "title": "步骤分接到 SFT 与 RL",
            "body": "ABC-SFT 提高高价值步的损失权重；ABC-GRPO 用步骤分做奖励，让失败轨迹里的有效动作也能被学到。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "同规模主结果",
                "论文证据": "Qwen3.5-4B + 8.5k：BrowseComp/ZH 37.3%/39.1%。",
                "飞哥判断": "小模型也能靠过程归因抬搜索能力。",
            },
            {
                "看什么": "加上下文管理",
                "论文证据": "BrowseComp/ZH 升至 55.3%/52.9%，接近约 30B Agent。",
                "飞哥判断": "信用分配与上下文管理要拆开看，别把增益全归一边。",
            },
            {
                "看什么": "迁移",
                "论文证据": "xbench-2505 77.0%、xbench-2510 46.0%、GAIA-text 81.6%。",
                "飞哥判断": "不只刷单一浏览基准。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "训练依赖标准答案；事后线索可能有偏差；开放研究外推有限。",
                "飞哥判断": "先当有答案搜索训练样板。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract / Table 2；BrowseComp 37.3→55.3；BrowseComp-ZH 39.1→52.9；8.5k；xbench/GAIA。",
        "版本戳：arXiv:2608.05102v1 [cs.AI]；ChatGPT 0806批次 #2（0807 主发）。",
        "单位：Shanghai Jiao Tong University。",
        "开源：github.com/PolarSeeker/ABSeeker；HF PolarSeeker/ABSeeker-4B-RL。",
        "证据覆盖：有答案搜索基准；开放式无答案研究待外推。",
    ],
    "so_what": "说白了，训练搜索 Agent 别把整条轨迹当一个标签。先从答案反推出该碰到的证据，再给每一步打分：有效取证加分，空转与胡猜降权。",
    "feige_view": "别只奖励最终答对。对照同日 Argus：一个解决「运行时经验怎么准入」，一个解决「训练时中间步怎么归因」。",
    "limitations": [
        "不过，方法依赖已知标准答案，难以直接用于真正开放式研究。",
        "从答案反推线索可能产生事后偏差，奖励偏好已知答案路径。",
        "上下文管理贡献较大，需进一步拆分其与信用分配本身的增益。",
        "BrowseComp 类任务仍不能完全代表多工具、长期现实研究流程。",
    ],
    "related_theme_picks": {
        "theme": "长程 Agent：可验证状态与可归因步骤",
        "intro": "本篇讲搜索步骤如何归因；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.05144",
                "title_cn": "可验证运行时自演化",
                "one_liner": "同日配对：执行侧也要把经验做成可审计状态。",
                "link": "https://arxiv.org/abs/2608.05144",
                "ready_date": "20260807",
            },
            {
                "arxiv_id": "2608.01324",
                "title_cn": "图引导深度搜索状态",
                "one_liner": "0805：深搜状态也要结构化。",
                "link": "https://arxiv.org/abs/2608.01324",
                "ready_date": "20260805",
            },
            {
                "arxiv_id": "2608.03468",
                "title_cn": "功能级工具工作流",
                "one_liner": "0806：工具经验同样需要可复用抽象。",
                "link": "https://arxiv.org/abs/2608.03468",
                "ready_date": "20260806",
            },
        ],
    },
    "target_audience": [
        "训练 Deep Research / 网页搜索 Agent 的团队。",
        "关心过程奖励与长程信用分配的研究工程同学。",
        "希望用小模型逼近大搜索 Agent 的成本敏感团队。",
    ],
    "sales_use_cases": [
        "回应『再加数据/再加大模型』：先问轨迹里每一步有没有可解释的过程分。",
        "方案评审：要求看线索恢复、步骤评分与失败轨迹中的正样本利用。",
        "成本沟通：用 4B+8.5k 逼近约 30B 对照说明过程归因的杠杆。",
    ],
    "objection_handling": [
        "客户说：『成功轨迹整段模仿不就行？』→ 回应：成功里也有空转；失败里也有好步骤；论文正是要拆开。",
        "客户说：『我们任务没有标准答案。』→ 回应：这是边界；开放研究需另找过程监督，本文主战场是有答案搜索。",
    ],
    "copy_paste_lines": [
        "别只奖最终对错：从答案反推线索，给搜索步骤打分。",
        "4B + 8.5k：BrowseComp 37.3%，加上下文管理到 55.3%。",
        "失败轨迹里的有效取证，也应该被学到。",
    ],
    "key_quotes": [
        "Answer-Backtracked Clue Recovery",
        "37.3% on BrowseComp and 39.1% on BrowseComp-ZH",
        "with context management ... 55.3% and 52.9%",
    ],
    "score_rationale": "ABSeeker把稀疏终局奖励变成答案反推的步骤分，小模型数据效率高。Novelty/Evidence强；依赖标准答案使Applicability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["创新性 Novelty", "可验证性 Evidence"],
        "lowest_dimensions": ["产业可用性 Applicability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.8, "role": "middle", "rationale": "长程搜索信用分配是 Deep Research Agent 训练的核心瓶颈。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "答案反推线索 + 步骤锚定评分，同时利用失败轨迹中的有效动作。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "highest", "rationale": "BrowseComp/ZH、xbench、GAIA 多基准数字可核，训练设置清楚。"},
            {"label": "产业可用性 Applicability", "value": 1.7, "role": "lowest", "rationale": "依赖标准答案，开放式研究与无答案场景不能直接套。"},
            {"label": "可复用性 Reusability", "value": 1.8, "role": "middle", "rationale": "SFT/RL 配方可复用；线索质量与上下文管理仍需工程拆解。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "BrowseComp 37.3%；BrowseComp-ZH 39.1%", "evidence": "Abstract / Table 2", "location": "Table 2"},
            {"claim": "含上下文管理后 55.3% / 52.9%", "evidence": "Abstract / Table 2", "location": "Table 2"},
            {"claim": "Qwen3.5-4B；8.5k examples", "evidence": "Abstract / §4", "location": "§4"},
            {"claim": "xbench-2505 77.0%；xbench-2510 46.0%；GAIA-text 81.6%", "evidence": "Abstract / Table 2", "location": "Table 2"},
            {"claim": "接近约 30B 搜索 Agent 表现（论文表述）", "evidence": "Abstract", "location": "Abstract"},
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
        "2608.05144",
        "argus",
        ARGUS_RICH,
        "别再只改权重：Argus把长程自演化放进可验证运行时，SWE-Bench Pro约78%",
        "固定模型权重，用验证门控的持久运行时积累可复用技能与失败路径，是更现实的长程Agent扩展路径。",
    )
    enrich_one(
        "2608.05102",
        "absseeker",
        ABSEEKER_RICH,
        "别再只奖最终对错：ABSeeker从答案反推线索给搜索步骤打分，4B逼近30B",
        "长程搜索Agent的关键不只是最终答对，而是识别哪些中间动作真正推进了证据链。",
    )
    print("enriched argus + absseeker")


if __name__ == "__main__":
    main()
