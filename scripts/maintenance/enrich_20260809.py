#!/usr/bin/env python3
"""One-off enrichment for 20260809 paper-notes payloads (Cross-Model KV + SkillHEX)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260809"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


CROSSKV_RICH = {
    "intro_lead": "",
    "A_research_problem": "生产里同系列大小模型切换、路由、级联时，目标端通常要从头重打整段上下文的 prefill。长会话越长，每次换模型越贵。",
    "B_core_contributions": [
        "闭式逐头岭回归：小样本校准、无需梯度训练",
        "跨层选型 + 去 RoPE 内容空间，映射可跨上下文长度复用",
        "三家族六对验证；attention-output 相似度可预测保留率",
    ],
    "C_method_framework": "先确认 matched-KV（源/目标 KV 头数与头维一致），再对每个目标层选 top-k 最可预测源层、去掉 RoPE 后做逐头岭回归；难 pair 可换非线性 MLP。校准约用 500 条 FineWeb-Edu、每条 1,024 token。",
    "D_key_results": [
        "四对最佳：平均保留约 73–98% 目标 standalone 准确率",
        "Qwen3 14B→32B 平均保留约 97.6%；映射比重 prefill 快约 2.7–25×",
        "难 pair 上 MLP 最高可回补约 +37pp HellaSwag 保留率",
    ],
    "E_industry_implications": [
        "级联/路由切换：先评估是否 matched-KV，再上线性 mapper",
        "验收别只看校准 R²，要看下游保留率与 attention-output 相似度",
        "难 pair 准备非线性备份，并监控多轮 handoff 漂移",
    ],
    "F_one_line_judgement": "这篇最适合做多模型路由与级联服务的团队：用闭式岭回归把源 KV 映射到目标，跳过重打 prefill；不过两对 Ministral 会大幅掉点，且要求 matched-KV。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Cross-model KV transfer", "definition": "把源模型已填充的 KV cache 映射成目标模型可用格式，从而跳过目标端重 prefill。"},
        {"term": "Matched-KV", "definition": "源与目标共享 KV 头数与每头维度；层数/参数量可不同。"},
        {"term": "Ridge mapper", "definition": "逐头闭式岭回归映射器；小样本拟合，无需梯度训练。"},
        {"term": "Content-space / RoPE-stripped", "definition": "先去掉位置旋转再拟合键映射，使权重可跨不同上下文长度复用。"},
        {"term": "Retention", "definition": "转移后准确率 / 目标自填 prefill 准确率；衡量映射质量。"},
        {"term": "Attention-output cosine", "definition": "映射后注意力输出与真值的相似度；比校准 R² 更能预示下游保留率。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：一切换就要重刷上下文",
            "body": "级联、路由、会话中升级模型都会换同系列另一尺寸。目标端重做 prefill，成本随上下文与模型尺寸上升。",
        },
        {
            "title": "先借线性结构再闭式拟合",
            "body": "matched-KV 下跨模型 KV 有可观线性成分。逐头岭回归 + top-k 源层拼接 + 去 RoPE，用少量校准序列即可落盘。",
        },
        {
            "title": "难 pair 再用非线性兜底",
            "body": "线性失败时往往不是误差太大，而是误差落在注意力敏感子空间；MLP 可重分配残差并显著抬保留率。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果",
                "论文证据": "四对最佳平均保留约 73–98%；Qwen3 14B→32B 约 97.6%。",
                "飞哥判断": "小到大切换在部分家族已接近可用。",
            },
            {
                "看什么": "延迟",
                "论文证据": "映射比重 prefill 快约 2.7–25×。",
                "飞哥判断": "真正卖点是省 prefill，不只是分数。",
            },
            {
                "看什么": "失败模式",
                "论文证据": "两对 Ministral Avg 掉到约 42–44%；MLP 最高 +37pp HellaSwag。",
                "飞哥判断": "matched-KV 是门槛，不是保证。",
            },
            {
                "看什么": "验收信号",
                "论文证据": "attention-output cosine 与 HellaSwag 保留率相关 r≈+0.57，优于 R²。",
                "飞哥判断": "别拿校准 R² 当上线唯一门禁。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract / Table 1；73–98% retention；Qwen3 14B→32B 97.6%；2.7–25×；MLP +37pp HellaSwag。",
        "版本戳：arXiv:2608.03893v1 [cs.LG]；本期固定 NVIDIA 篇。",
        "单位：NVIDIA。",
        "开源入口：论文未给出公开仓库链接（截至 v1）。",
        "证据覆盖：三家族六对 matched-KV；跨系列与 unmatched-KV 不在范围。",
    ],
    "so_what": "多模型服务里，模型切换税先于模型本身。能不能映射源 KV、下游保留率过不过关，比「校准看起来很准」更决定能不能上线。",
    "feige_view": "别把 KV 复用只当成同模型 prefix cache。对照同日 SkillHEX：一个管推理底座怎么少付切换税，一个管技能怎么少付误诊税。",
    "limitations": [
        "两对 Ministral 大幅掉点，matched-KV 不等于可用。",
        "研究范围限于同系列 matched-KV，跨系列或不匹配头配置未覆盖。",
        "线性映射器存储约 4–12GB，部署要单列容量账。",
        "大到小方向与多轮 handoff 仍需额外监控漂移。",
    ],
    "related_theme_picks": {
        "theme": "推理基础设施与技能进化",
        "intro": "本篇讲跨模型 KV 复用；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.05628",
                "title_cn": "假设驱动技能自进化",
                "one_liner": "同日配对：技能侧用实验证据改，而不是一路贪心改。",
                "link": "https://arxiv.org/abs/2608.05628",
                "ready_date": "20260809",
            },
            {
                "arxiv_id": "2608.05212",
                "title_cn": "长程搜索失败审计",
                "one_liner": "0808：执行错了怎么定位到步。",
                "link": "https://arxiv.org/abs/2608.05212",
                "ready_date": "20260808",
            },
            {
                "arxiv_id": "2608.05139",
                "title_cn": "技能熵与跨技能训练",
                "one_liner": "0808：技能切换难度怎么量与练。",
                "link": "https://arxiv.org/abs/2608.05139",
                "ready_date": "20260808",
            },
        ],
    },
    "target_audience": [
        "做多模型路由、级联与成本质量切换的推理平台团队。",
        "关心 prefill / KV cache 复用与延迟预算的系统工程师。",
        "评估同系列模型热切换可行性的研究工程同学。",
    ],
    "sales_use_cases": [
        "回应『切换模型就要重算上下文』：先问是否 matched-KV，能否映射 KV。",
        "方案评审：要求看下游保留率、失败 pair、mapper 体积与 handoff 漂移。",
        "延迟沟通：用 2.7–25× 说明卖点是省 prefill，不是又训一个大适配器。",
    ],
    "objection_handling": [
        "客户说：『prefix cache 不就够了？』→ 回应：那只省同模型；跨尺寸切换仍会重 prefill。",
        "客户说：『校准 R² 很高就能上。』→ 回应：论文明确 R² 不预测保留率，要看注意力输出相似度与下游分。",
    ],
    "copy_paste_lines": [
        "换同系列模型，别默认重刷 Prefill。",
        "四对最佳保留约 73–98%；最快约 25×。",
        "验收看下游保留率，别只看校准 R²。",
    ],
    "key_quotes": [
        "retains 73–98% of the receiver's standalone-prefill accuracy on four pairs",
        "mapper runs 2.7–25× faster than re-prefill",
        "nonlinear MLP recovers up to +37 pp HellaSwag retention",
    ],
    "score_rationale": "跨模型KV闭式映射直指生产切换税，延迟与最佳pair数字清楚。Impact/Applicability高；难pair与matched-KV约束使Evidence/Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "产业可用性 Applicability"],
        "lowest_dimensions": ["可验证性 Evidence", "可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "多模型编排下重 prefill 是真实成本项，KV 跨模型复用切中生产痛点。"},
            {"label": "创新性 Novelty", "value": 1.8, "role": "middle", "rationale": "闭式岭回归+去RoPE+跨层选型简洁有力；相关神经融合工作已有，但小样本梯度免费路径更务实。"},
            {"label": "可验证性 Evidence", "value": 1.7, "role": "lowest", "rationale": "三家族六对与消融较完整，但两对大幅失败，适用范围边界仍尖。"},
            {"label": "产业可用性 Applicability", "value": 1.9, "role": "highest", "rationale": "NVIDIA 作者与延迟数字直接服务推理平台决策。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "依赖 matched-KV，跨系列与头配置不匹配时难以直接搬用。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "四对最佳平均保留约 73–98%", "evidence": "Abstract / Table 1", "location": "Table 1"},
            {"claim": "Qwen3 14B→32B Avg retention 97.6%", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "映射比重 prefill 快约 2.7–25×", "evidence": "Abstract / §4.7", "location": "Abstract"},
            {"claim": "MLP 最高约 +37pp HellaSwag", "evidence": "Abstract / Table 3", "location": "Table 3"},
            {"claim": "attention-output cosine 与保留率 r≈+0.57", "evidence": "§4.5", "location": "§4.5"},
        ]
    },
}


SKILLHEX_RICH = {
    "intro_lead": "",
    "A_research_problem": "Agent 技能要靠执行反馈在线改，但终局成败混杂多种潜在失败原因。一路贪心改技能，常被早期误诊锁死，有限试验预算很快耗尽。",
    "B_core_contributions": [
        "假设驱动自验证：可证伪失败假设→可执行诊断测试→密集证据",
        "证据引导技能补丁树搜索，避免早期误诊一路写穿",
        "SkillsBench 87 任务、双骨干、消融与 token 成本对照",
    ],
    "C_method_framework": "SkillHEX 先把可能失败原因写成可证伪假设，并生成经规则校验的可执行测试，在缓存输出上复测得到诊断证据；再以证据引导持久化技能补丁树上的搜索，动态平衡已支持补丁与备选分支。",
    "D_key_results": [
        "GPT-5.3-Codex / Claude Opus 4.7：平均 pass 率 55.9% / 57.9%（5 次迭代）",
        "相对最强自进化基线 CoEvoSkills：+9.5 / +8.5pp，并超过人工技能总均值",
        "去自验证器掉 11.1pp；去补丁树掉 6.8pp；总 token 比 CoEvoSkills 少约 18%",
    ],
    "E_industry_implications": [
        "技能自演化：别只靠自然语言反思，先写可执行诊断测试",
        "版本管理：保留多条技能补丁分支，允许回退误诊路径",
        "预算控制：用证据库复用测试，减少无效环境交互",
    ],
    "F_one_line_judgement": "这篇最适合做 Agent 技能库与 test-time 自进化的团队：用可证伪假设生成诊断测试，再用证据引导树搜索改技能；不过知识密集域仍可能逊于人工技能，多分支也增加版本管理成本。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "SkillHEX", "definition": "假设驱动自验证 + 证据引导树搜索的技能自进化框架。"},
        {"term": "Exploitation trap", "definition": "早期误诊被贪心利用后，后续迭代都在错误补丁上耗预算。"},
        {"term": "Hypothesis-driven self-verification", "definition": "把失败原因写成可证伪假设，并生成可执行测试获取诊断证据。"},
        {"term": "Skill patch tree", "definition": "持久化保存多条技能修改分支，允许回退与再探索。"},
        {"term": "SkillsBench", "definition": "87 任务基准，固定模型/ harness /容器/验证器，隔离技能本身贡献。"},
        {"term": "Evidence-guided tree search", "definition": "用诊断证据做密集奖励，引导 PUCT 风格技能修订搜索。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：终局成败掩盖多种失败原因",
            "body": "只有最终对错时，第一次归因很容易错。若立刻贪心改技能，后面几轮会困在同一条误诊路径上。",
        },
        {
            "title": "把猜测写成可测假设",
            "body": "自验证器生成可执行测试并复测缓存输出，不用额外环境尝试就能得到更密的诊断信号。",
        },
        {
            "title": "多分支保留备选补丁",
            "body": "技能补丁树让后续预算可以回到更有证据的分支，而不是把早期错误补丁写穿。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果",
                "论文证据": "GPT-5.3-Codex 55.9%；Claude Opus 4.7 57.9%（5 次迭代）。",
                "飞哥判断": "短预算内可持续抬分，不是一次反思就撞顶。",
            },
            {
                "看什么": "相对基线",
                "论文证据": "相对 CoEvoSkills +9.5 / +8.5pp；相对 No Skill +22.6 / +23.8pp。",
                "飞哥判断": "关键差在搜索策略，不只是「会改技能」。",
            },
            {
                "看什么": "消融",
                "论文证据": "去自验证器 −11.1pp；去补丁树 −6.8pp。",
                "飞哥判断": "诊断证据比树结构更关键，但两者都要。",
            },
            {
                "看什么": "成本",
                "论文证据": "总 token 比 CoEvoSkills 少约 18%。",
                "飞哥判断": "多分支不一定更贵，误诊一路改到底才贵。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract / Table 1–3；55.9%/57.9%；+9.5/+8.5pp；消融 −11.1/−6.8pp；token −18%。",
        "版本戳：arXiv:2608.05628v1 [cs.AI]；ChatGPT 0807批次 #2（0809 工作流选篇）。",
        "单位：Microsoft；UC San Diego；USTC；UBC。",
        "开源入口：论文未给出公开仓库链接（截至 v1）。",
        "证据覆盖：SkillsBench 可控设定；开放知识密集域仍弱于人工技能。",
    ],
    "so_what": "技能自进化最贵的不是改几行说明，而是第一次误诊把后面几轮预算锁死。可测假设和补丁分支，是为了把反省变成可淘汰的路径。",
    "feige_view": "别把「再反思一轮」当成技能改进。对照同日 NVIDIA Cross-KV：一边省模型切换税，一边省技能误诊税——Agent 可靠正在变成基础设施问题。",
    "limitations": [
        "Natural Science / Finance 等知识密集域仍可能逊于人工技能。",
        "自动测试若不隔离真失败原因，会制造伪证据。",
        "多分支树提高技能版本管理与审计复杂度。",
        "SkillsBench 固定容器与验证器，开放世界泛化仍待验证。",
    ],
    "related_theme_picks": {
        "theme": "推理基础设施与技能进化",
        "intro": "本篇讲技能如何用实验证据自进化；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.03893",
                "title_cn": "跨模型KV Prefill复用",
                "one_liner": "同日配对：底座侧先少付模型切换税。",
                "link": "https://arxiv.org/abs/2608.03893",
                "ready_date": "20260809",
            },
            {
                "arxiv_id": "2608.05139",
                "title_cn": "技能熵与跨技能训练",
                "one_liner": "0808：技能切换难度怎么量与练。",
                "link": "https://arxiv.org/abs/2608.05139",
                "ready_date": "20260808",
            },
            {
                "arxiv_id": "2608.05212",
                "title_cn": "长程搜索失败审计",
                "one_liner": "0808：搜错了怎么定位到步。",
                "link": "https://arxiv.org/abs/2608.05212",
                "ready_date": "20260808",
            },
        ],
    },
    "target_audience": [
        "建设 Agent 技能库与自动演化流水线的研究工程团队。",
        "关心 test-time 自改进与工具/技能版本管理的平台同学。",
        "评估 Skills / prompt 资产如何持续迭代的产品技术同学。",
    ],
    "sales_use_cases": [
        "回应『失败了再让模型改一版技能』：先问有没有可执行诊断与多分支回退。",
        "方案评审：要求看假设→测试→证据→分支搜索，而不是单线反思日志。",
        "预算沟通：用 −18% token 与 −11.1pp 消融说明诊断证据的杠杆。",
    ],
    "objection_handling": [
        "客户说：『这不就是 self-refine 吗？』→ 回应：关键差在可证伪测试与补丁树，而不是又写一段反思。",
        "客户说：『分支一多更难运维。』→ 回应：论文显示原地改反而更费 token，且更容易锁死误诊。",
    ],
    "copy_paste_lines": [
        "别再一路贪心改技能：先写可测假设。",
        "SkillHEX：5 轮迭代 pass 率约 55.9% / 57.9%。",
        "去自验证器掉 11.1pp，说明诊断证据是主杠杆。",
    ],
    "key_quotes": [
        "average pass rate of 55.9% and 57.9%",
        "gains of up to 9.5 percentage points over the strongest self-evolution baseline",
        "Removing self-verification reduces the average pass rate from 55.9% to 44.8%",
    ],
    "score_rationale": "SkillHEX把技能自进化做成假设实验与多分支搜索，SkillsBench数字与消融清楚。Impact/Novelty高；知识密集域与版本复杂度使Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "技能资产成为 Agent 核心后，误诊驱动的贪心修订是真实生产风险。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "把可证伪假设、可执行测试与技能补丁树搜索绑成闭环，超出纯自然语言反思。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "middle", "rationale": "双骨干主结果、消融与 token 表完整；受控基准仍限制外推。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "可直接对照技能平台迭代流程；需要配套测试生成与分支管理。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "知识密集域仍弱，多分支运维成本不低，开放世界泛化未证明。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "GPT-5.3-Codex 55.9%；Claude Opus 4.7 57.9%", "evidence": "Abstract / Table 1", "location": "Table 1"},
            {"claim": "相对 CoEvoSkills +9.5 / +8.5pp", "evidence": "Abstract / §4.2", "location": "§4.2"},
            {"claim": "去自验证器 55.9%→44.8%（−11.1pp）", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "去补丁树 55.9%→49.1%（−6.8pp）", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "总 token 比 CoEvoSkills 少约 18%", "evidence": "Table 3 / §4.4", "location": "§4.4"},
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

    if ledger_path.exists():
        ledger = load(ledger_path)
        patch = rich.get("evidence_ledger_patch") or {}
        if patch.get("claim_evidence"):
            ledger["claim_evidence"] = patch["claim_evidence"]
        dump(ledger_path, ledger)
        dump(fused_ledger, ledger)

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
        "2608.03893",
        "crosskv",
        CROSSKV_RICH,
        "换同系列模型别重刷Prefill：NVIDIA闭式映射复用KV，最优保留约98%准确率",
        "跨模型KV闭式映射能跳过重prefill，但只在matched-KV且线性结构足够时稳。",
    )
    enrich_one(
        "2608.05628",
        "skillhex",
        SKILLHEX_RICH,
        "别再一路贪心改技能：SkillHEX用假设实验多分支搜索，5轮迭代pass率约58%",
        "技能自进化要先把失败原因变成可证伪实验，再在多分支上搜，而不是一路改到底。",
    )
    print("enriched crosskv + skillhex")


if __name__ == "__main__":
    main()
