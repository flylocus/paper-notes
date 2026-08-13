#!/usr/bin/env python3
"""One-off enrichment for 20260806 paper-notes payloads (LeanMem + ToolLIFT)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260806"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


LEANMEM_RICH = {
    "intro_lead": "",
    "A_research_problem": "长期记忆若对所有历史走同一套摘要与检索，要么 token 爆掉，要么细粒度证据被压扁丢光。瓶颈不只是向量库够不够大，而是不同信息该不该、能不能被同一种压缩方式对待。",
    "B_core_contributions": [
        "区分 profile / event / record 三类长期记忆，而不是统一摘要检索",
        "维护时只更新动态事件，避免反复压缩稳定画像与不可变记录",
        "按查询动态选择记忆类型与检索预算，在保真、上下文长度与成本间分层权衡",
    ],
    "C_method_framework": "LeanMem 先过滤低价值内容，再按可压缩性、时序动态与保真需求分别写入 profile（稳定画像）、event（可变事件）与 record（指向原文证据）。维护时只更新持续变化的事件；推理时按查询证据需求选记忆类型并分配检索预算，再按角色组装上下文。",
    "D_key_results": [
        "LoCoMo+GPT-4.1-mini：Acc 84.87，相对最强记忆基线 +5.54；构建/推理 token 与延迟同步下降",
        "LongMemEval-S+GPT-4.1-mini：Acc 91.80，相对最强记忆基线 +15.07；构建约 117.61K tokens",
        "Qwen3-8B 上同样 Acc 领先，并保持最低或近最低推理延迟",
    ],
    "E_industry_implications": [
        "个人/客服长期 Agent：先问记忆是否分层，而不是只会统一向量召回",
        "验收看证据保真与检索预算是否可解释，而不只看记忆条数",
        "成本沟通：对照 A-Mem 百万级构建 token，分层存储可显著压建设成本",
    ],
    "F_one_line_judgement": "这篇最适合长期对话 Agent：把记忆拆成画像、事件与原始记录，按问题动态分配检索预算；不过分类错了可能不可逆丢证据，主战场仍偏对话问答。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "LeanMem", "definition": "按信息性质分层存储、按查询动态分配检索预算的轻量长期记忆框架。"},
        {"term": "Profile memory", "definition": "压缩保存稳定用户属性与偏好的画像型记忆。"},
        {"term": "Event memory", "definition": "按时序记录状态变化、可选择性更新的事件型记忆。"},
        {"term": "Record memory", "definition": "保留原文指针、需要高保真证据时再展开的记录型记忆。"},
        {"term": "Adaptive Evidence Composition", "definition": "按问题证据需求选择记忆类型并分配检索深度，再按角色组装上下文。"},
        {"term": "LoCoMo / LongMemEval-S", "definition": "长对话问答基准；本文主报 LLM-judged Accuracy、Recall 与构建/推理成本。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：一锅炖会丢细节或烧 token",
            "body": "异构对话内容压缩性、时序性、保真要求不同。统一摘要检索，要么把细节压没，要么把整段历史反复喂给模型。",
        },
        {
            "title": "三类记忆，各管一段",
            "body": "稳定属性进 profile，状态变化进 event，细节证据留 record 指针。维护时只更新还会变的事件，避免反复重压稳定信息。",
        },
        {
            "title": "按问题分配检索预算",
            "body": "不是全局 top-k 一锅端。先判断需要哪类证据，再分配检索深度，最后按画像/时序/原文角色组装。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "短会话质量（LoCoMo）",
                "论文证据": "GPT-4.1-mini：Acc 84.87 / Recall 83.80；相对最强记忆基线 +5.54 Acc。",
                "飞哥判断": "分层取证在多跳/时序题上也站得住。",
            },
            {
                "看什么": "长历史质量（LongMemEval-S）",
                "论文证据": "GPT-4.1-mini：Acc 91.80，相对最强记忆基线 +15.07；构建约 117.61K tokens。",
                "飞哥判断": "越长越能看出「保真分层」的价值。",
            },
            {
                "看什么": "成本",
                "论文证据": "相对 A-Mem 百万级构建 token，LeanMem 构建/推理 token 与延迟最低或近最低。",
                "飞哥判断": "准确率与成本同向改善，才像可部署记忆系统。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主战场是长对话问答；分类错误可能造成不可逆损失；代码库/网页/多工具场景待外推。",
                "飞哥判断": "先当长期对话记忆样板，别直接当通用 Agent 记忆银弹。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（LoCoMo/LongMemEval-S Acc/成本）；§4.2 叙述。",
        "版本戳：arXiv:2608.03463v1 [cs.AI]；ChatGPT 0805批次 #1（0806 主发）。",
        "单位：Hefei University of Technology。",
        "证据覆盖：对话记忆准确率与 token/延迟；开放工具/代码 Agent 外推待补。",
    ],
    "so_what": "说白了，长期记忆别再默认「摘要+向量」一条管道。先按信息能不能压、会不会变、要不要原文，分流存储；查询时再按证据类型花预算。",
    "feige_view": "别把记忆系统做成统一压缩器。对照同日 ToolLIFT：一个管「存什么证据」，一个管「工具经验如何跨接口迁移」。",
    "limitations": [
        "不过，记忆类型分类错误可能造成不可逆的信息损失。",
        "主验证在长期对话问答，对代码库、网页与多工具 Agent 适用性仍待证明。",
        "Accuracy 依赖 LLM-as-judge；不同评测提示可能改变绝对分，但不改相对排序叙事。",
    ],
    "related_theme_picks": {
        "theme": "Agent 内部对象：记忆、工具与预算",
        "intro": "本篇讲长期记忆分层；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.03468",
                "title_cn": "功能级工具工作流",
                "one_liner": "同日配对：工具经验也要从具体 API 抬一层。",
                "link": "https://arxiv.org/abs/2608.03468",
                "ready_date": "20260806",
            },
            {
                "arxiv_id": "2608.00017",
                "title_cn": "记忆奖励膨胀与Echo Gap",
                "one_liner": "0805：高分记忆也可能在放大错误。",
                "link": "https://arxiv.org/abs/2608.00017",
                "ready_date": "20260805",
            },
            {
                "arxiv_id": "2608.01324",
                "title_cn": "图引导深度搜索状态",
                "one_liner": "0805：深搜也要把状态显式写出来。",
                "link": "https://arxiv.org/abs/2608.01324",
                "ready_date": "20260805",
            },
        ],
    },
    "target_audience": [
        "做个人助理、客服与长期会话 Agent 记忆层的团队。",
        "关心记忆构建成本、推理 token 与证据保真平衡的工程负责人。",
        "评估「统一向量记忆」是否已到瓶颈的研究同学。",
    ],
    "sales_use_cases": [
        "回应『再加大上下文就能记住』：先问稳定画像、可变事件与原文证据是否分流。",
        "方案评审：要求看记忆类型、维护策略与按查询分配的检索预算。",
        "成本沟通：用相对 A-Mem 的构建 token 差距说明分层存储的工程账。",
    ],
    "objection_handling": [
        "客户说：『向量库召回不够吗？』→ 回应：统一 top-k 难同时保住画像稳定性与原文保真；论文用分层+预算同向改善 Acc 与成本。",
        "客户说：『分类错了怎么办？』→ 回应：这是真实边界；所以 record 指针与可审计检索预算更关键。",
    ],
    "copy_paste_lines": [
        "长期记忆别一锅炖：画像、事件、原文记录分开存。",
        "LongMemEval-S：Acc 91.80，相对最强记忆基线 +15.07。",
        "按问题分配检索预算，比全局 top-k 更像数据库查询规划。",
    ],
    "key_quotes": [
        "profile memory, temporally structured event memory, or source-grounded record memory",
        "improves accuracy ... by up to 15.1 points",
        "dynamically selects memory types and allocates retrieval budgets",
    ],
    "score_rationale": "LeanMem把长期记忆做成可分层存储与按需检索的结构，准确率与成本同向改善。Impact/Evidence/Applicability高；分类错误风险与场景偏对话略扣Reusability。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "可验证性 Evidence", "产业可用性 Applicability"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "Agent 长期记忆是个人助理与连续工作流的核心瓶颈，分层证据管理直接命中工程痛点。"},
            {"label": "创新性 Novelty", "value": 1.8, "role": "middle", "rationale": "profile/event/record + 动态检索预算，把统一摘要检索推进到类似数据库分层与查询规划。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "highest", "rationale": "LoCoMo/LongMemEval-S 双骨干、多基线，Acc 与构建/推理成本同表可核。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "highest", "rationale": "架构轻量、成本账清楚，适合先落地长期对话记忆层。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "分类错误可能不可逆丢证据；主战场偏对话，开放工具/代码场景外推仍有限。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "LoCoMo+GPT-4.1-mini Acc 84.87 / Recall 83.80", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "相对最强记忆基线 LoCoMo +5.54 Acc", "evidence": "§4.2 / Table 1", "location": "§4.2"},
            {"claim": "LongMemEval-S+GPT-4.1-mini Acc 91.80，相对最强 +15.07", "evidence": "Table 1 / §4.2", "location": "Table 1"},
            {"claim": "LongMemEval-S 构建约 117.61K tokens；相对 A-Mem >1.2M", "evidence": "Table 1 / §4.2", "location": "Table 1"},
            {"claim": "Qwen3-8B 全设置 Acc 领先且推理延迟最低或近最低", "evidence": "Table 1 / Abstract", "location": "Table 1"},
        ]
    },
}


TOOLLIFT_RICH = {
    "intro_lead": "",
    "A_research_problem": "历史工具轨迹若只记具体 API，工具名或接口一变就难迁移。企业与 MCP 场景里工具集持续变化，程序性经验需要可跨工具复用的抽象层。",
    "B_core_contributions": [
        "从具体工具轨迹抽取功能级工作流图，跨工具共享协作经验",
        "解耦整体工作流规划与具体工具选择，对齐全局结构",
        "source-gated / skill-specific reward + 工作流扰动，提升参数来源追踪与抗规划误差能力",
    ],
    "C_method_framework": "ToolLIFT 将工具轨迹抬升为 Function-Level Workflow Graph（FWG）：先聚成功能簇并共享跨工具协作结构，再解耦工作流规划与具体工具选择；训练侧用 source-gated 与 skill-specific reward，保证参数来源可追踪，并用两阶段 GRPO 分别训规划器与工具调用生成器。",
    "D_key_results": [
        "Llama：HuggingFace/Multimedia Acc 77.44/80.38，相对最强基线约 +1.37/+1.50",
        "Llama OOD：DailyLifeAPIs/Seal-Tools/ToolAlpaca Acc 69.30/56.63/40.68，相对最强基线约 +4.69/+3.22/+4.90",
        "SER 低于 EM 变体；去掉 FWG/规划器/扰动时 OOD 掉点更明显",
    ],
    "E_industry_implications": [
        "MCP/函数调用平台：经验库验收看能否跨工具集迁移，而不只看同工具复现",
        "方案评审：要求看功能簇、工作流与参数来源追踪，而不只看调用成功率",
        "部署前先评估抽象层是否覆盖权限、副作用与业务约束",
    ],
    "F_one_line_judgement": "这篇最适合工具集经常换的 Agent/MCP 场景：把经验从具体 API 抬到功能工作流；不过过度抽象可能丢掉权限与副作用约束。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "ToolLIFT", "definition": "把工具轨迹抬到功能级工作流图，并解耦规划与工具选择的通用工具规划框架。"},
        {"term": "FWG", "definition": "Function-Level Workflow Graph：以功能簇而非具体 API 编码协作结构。"},
        {"term": "Trajectory lifting", "definition": "把具体工具调用抽象成可跨工具共享的功能级转移。"},
        {"term": "Source-gated reward", "definition": "参数来源类型不匹配则零奖励，匹配后再按技能评分。"},
        {"term": "SER", "definition": "Source Error Rate：参数信息来源识别错误率。"},
        {"term": "ID / OOD", "definition": "训练工具集内/外评测；OOD 强调未见工具集泛化。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：记住 API 不等于可迁移",
            "body": "同构任务常共享功能步骤，但具体工具名不同。工具级图绑死接口后，换工具集就像换方言，旧经验立刻贬值。",
        },
        {
            "title": "先抬一层：功能工作流图",
            "body": "把轨迹聚到功能簇，形成 FWG。新工具映射到最近功能后，可继承该功能上的协作转移。",
        },
        {
            "title": "规划与选型解耦，并管住数据流",
            "body": "先规划功能完整工作流，再选具体工具；source-gated reward 逼模型写清参数来自哪里，扰动训练降低规划误差传导。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "分布内质量",
                "论文证据": "Llama：HF/Multimedia Acc 77.44/80.38，相对最强基线约 +1.37/+1.50。",
                "飞哥判断": "同工具集也有增益，但真正卖点在迁移。",
            },
            {
                "看什么": "未见工具集",
                "论文证据": "Llama OOD：Daily/Seal/ToolAlpaca 相对最强基线约 +4.69/+3.22/+4.90 Acc。",
                "飞哥判断": "功能级抽象在跨工具泛化上更值钱。",
            },
            {
                "看什么": "数据流可靠性",
                "论文证据": "SER 低于 EM 奖励变体；消融显示 FWG/规划器/扰动对 OOD 更关键。",
                "飞哥判断": "迁移不只看选对工具，还看参数来源能不能追。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主评测是规划 Acc/n-F1/l-F1；权限、副作用与真实业务约束未完全进入图。",
                "飞哥判断": "先当工具经验可迁移架构样板，别跳过业务约束层。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 1（ID/OOD Acc）；Table 2（SER）；Table 3（消融）；§5.2–5.4。",
        "版本戳：arXiv:2608.03468v1 [cs.AI]；ChatGPT 0805批次 #2（0806 主发）。",
        "单位：Beihang University。",
        "证据覆盖：工具规划准确率与来源错误率；真实权限/副作用需外推。",
    ],
    "so_what": "说白了，工具经验别只存「调了哪个 API」。先记住功能步骤与数据流，再在当前工具集里落地；换 MCP/供应商时才有东西可迁移。",
    "feige_view": "别把「会调工具」当成会积累程序性知识。对照同日 LeanMem：一个管证据怎么分层存，一个管工具经验怎么跨接口抽象。",
    "limitations": [
        "不过，过度抽象可能忽略特定工具的权限、副作用和业务约束。",
        "图构建与强化学习会增加系统复杂度与调参成本。",
        "论文假设参数常有单一来源；多源合成参数仍是后续方向。",
    ],
    "related_theme_picks": {
        "theme": "Agent 内部对象：记忆、工具与预算",
        "intro": "本篇讲工具经验可迁移；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.03463",
                "title_cn": "分层长期记忆",
                "one_liner": "同日配对：记忆也要从统一管道改成分层。",
                "link": "https://arxiv.org/abs/2608.03463",
                "ready_date": "20260806",
            },
            {
                "arxiv_id": "2608.01324",
                "title_cn": "图引导深度搜索状态",
                "one_liner": "0805：深搜状态也要结构化。",
                "link": "https://arxiv.org/abs/2608.01324",
                "ready_date": "20260805",
            },
            {
                "arxiv_id": "2608.00017",
                "title_cn": "记忆奖励膨胀与Echo Gap",
                "one_liner": "0805：经验复用前先查评分是否自膨胀。",
                "link": "https://arxiv.org/abs/2608.00017",
                "ready_date": "20260805",
            },
        ],
    },
    "target_audience": [
        "做 MCP、函数调用与企业工具编排的 Agent 平台团队。",
        "关心工具集变更后经验是否可迁移的产品与架构负责人。",
        "评估工具图/工作流图是否值得上 RL 的研究工程同学。",
    ],
    "sales_use_cases": [
        "回应『我们把历史 API 调用都存了』：先问换供应商/换 MCP 后经验还能否复用。",
        "方案评审：要求看功能簇、工作流与参数来源追踪，而不只看同工具成功率。",
        "迁移沟通：用 OOD +4.9 对照说明——功能级抽象比死记 API 更抗工具漂移。",
    ],
    "objection_handling": [
        "客户说：『工具级图不够吗？』→ 回应：工具一换图边就断；论文显示功能级图在未见工具集上增益更明显。",
        "客户说：『抽象会不会丢业务约束？』→ 回应：会，这是边界；落地仍需权限/副作用层补齐。",
    ],
    "copy_paste_lines": [
        "工具经验别绑死 API：先抬到功能级工作流。",
        "Llama OOD：DailyLifeAPIs 相对最强基线约 +4.69 Acc。",
        "规划与选型解耦，参数来源还要能追。",
    ],
    "key_quotes": [
        "function-level workflow graph (FWG)",
        "strong generalization to unseen tool sets",
        "source-gated and skill-specific rewards",
    ],
    "score_rationale": "ToolLIFT把工具经验从具体API抬到功能工作流，ID/OOD证据扎实。Impact/Novelty/Evidence高；业务约束与系统复杂度略扣Reusability。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.1,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty", "可验证性 Evidence", "产业可用性 Applicability"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.8, "role": "highest", "rationale": "工具集漂移是 Agent 从 benchmark 走向企业/MCP 部署的核心障碍。"},
            {"label": "创新性 Novelty", "value": 1.8, "role": "highest", "rationale": "功能级工作流图 + 规划/选型解耦 + 来源门控奖励，结构清晰。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "highest", "rationale": "两 ID 三 OOD、双骨干、SER 与消融齐全，数字可核。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "highest", "rationale": "直接对应工具平台持续换接口的现实，工程叙事清楚。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "过度抽象可能丢权限副作用；图构建+RL 增加复杂度。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "Llama HF/Multimedia Acc 77.44/80.38", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "Llama OOD Daily/Seal/ToolAlpaca Acc 69.30/56.63/40.68", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "OOD 相对最强基线约 +4.69/+3.22/+4.90", "evidence": "§5.2", "location": "§5.2"},
            {"claim": "SER 低于 EM 奖励变体", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "去掉 FWG/规划器/扰动后 OOD Acc 显著下降", "evidence": "Table 3", "location": "Table 3"},
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
        "2608.03463",
        "leanmem",
        LEANMEM_RICH,
        "别再统一摘要检索：LeanMem按画像/事件/记录分层，LongMemEval最高+15.1",
        "长期记忆先别把所有历史塞进同一管道；分层存、按需取，准确率与成本可以一起改善。",
    )
    enrich_one(
        "2608.03468",
        "toollift",
        TOOLLIFT_RICH,
        "别再死记API轨迹：ToolLIFT抬到功能级工作流图，未见工具集也能泛化",
        "工具经验先别绑死具体 API；先规划功能步骤，再在当前环境选能落地的工具。",
    )
    print("enriched leanmem + toollift")


if __name__ == "__main__":
    main()
