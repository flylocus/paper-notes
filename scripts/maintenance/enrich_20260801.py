#!/usr/bin/env python3
"""One-off enrichment for 20260801 paper-notes payloads (SkillMentor + GAMER)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260801"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


SKILLMENTOR_RICH = {
    "intro_lead": "",
    "A_research_problem": "技能平台常说「我们会从失败里学习」，可多数失败仍要等用户撞上才暴露。卡住长期演化的，往往是还没被发现的盲区——诊断本身很少被当成可优化能力。",
    "B_core_contributions": [
        "把「发现不知道什么」定义为独立于任务执行的 Agent 能力",
        "用强化学习训练 Mentor 生成有诊断价值的测试任务",
        "从重复失败中提取可复用纠正技能，而非只修单条轨迹",
    ],
    "C_method_framework": "冻结执行 Agent、零人工标注；Mentor 经 RL 学习：生成诊断任务 → 测量与强参考模型的诊断间隙 → 将反复失败整理为 ADD/UPDATE/MERGE 纠正技能，仅当效用过阈才入库。",
    "D_key_results": [
        "AppWorld 与 BFCLv3 上相对 No Skill 平均提升 44.2%",
        "Qwen3.5-9B 执行器 Avg Acc：0.478→0.682；AppWorld Acc：0.300→0.410；BFCLv3 Agentic：0.452→0.660",
        "同执行器下持续优于 Reflexion / MemP / ReasoningBank 与更强提示导师 DeepSeek-V4-Flash",
    ],
    "E_industry_implications": [
        "验收时多问一句：本周新发现的盲区，有多少是系统主动找出来的？",
        "看板加三列就够用：诊断间隙、技能入库/驱逐、相对 No Skill 增益",
        "先落在可自动验证的工具调用；开放域科研盲区另开评测，别混 KPI",
    ],
    "F_one_line_judgement": "这篇最适合工具调用与技能库场景：它证明盲区诊断可学，但开放科研/复杂工程里的隐性缺口，以及技能冲突治理，仍未给出完整答案。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Blind-spot diagnosis", "definition": "主动发现执行 Agent 尚未暴露、但会反复出现的能力缺口。"},
        {"term": "SkillMentor", "definition": "用 RL 训练的独立 Mentor：生成诊断任务并沉淀纠正技能。"},
        {"term": "Frozen executor", "definition": "执行 Agent 权重不变，增益只能来自诊断与外部技能库。"},
        {"term": "Diagnostic gap", "definition": "强参考模型得分与冻结执行器得分之差，用于衡量任务的诊断价值。"},
        {"term": "Corrective skill", "definition": "针对反复失败模式整理出的可复用纠正技能（ADD/UPDATE/MERGE）。"},
        {"term": "AppWorld / BFCLv3", "definition": "工具使用与函数调用类 Agent 基准。"},
    ],
    "method_subsections": [
        {
            "title": "为什么要冻结执行器、禁人工标注",
            "body": "若执行器可训练或有标注，增益可能来自参数更新或标签泄漏，诊断贡献无法单独归因。冻结权重 + 零标注，迫使进步只能来自学会「找盲区」。",
        },
        {
            "title": "发现与策展为何要联合优化",
            "body": "更好的诊断任务带来更好技能，更好技能又暴露新盲区。只优化其中一侧，会错过正反馈回路。",
        },
        {
            "title": "入库门控",
            "body": "候选技能须语法合法，且相对 Gap Evaluation 基线 ∆>0.5 才入库；成功率低于 0.05 的旧技能会被驱逐。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主增益",
                "论文证据": "相对 No Skill 平均 +44.2%；9B 执行器 Avg Acc 0.478→0.682。",
                "飞哥判断": "不改执行权重也能涨，说明诊断侧确实贡献了能力。",
            },
            {
                "看什么": "任务面",
                "论文证据": "AppWorld Acc 0.300→0.410；BFCLv3 Agentic 0.452→0.660。",
                "飞哥判断": "工具调用场景证据清楚，开放域仍需外推谨慎。",
            },
            {
                "看什么": "对照强度",
                "论文证据": "同执行器下压过 Reflexion/MemP/ReasoningBank 与 DeepSeek-V4-Flash 提示导师。",
                "飞哥判断": "换更强提示导师也干不过可学习 Mentor——诊断策略本身在涨。",
            },
            {
                "看什么": "证据覆盖",
                "论文证据": "双基准 × 多执行器；含发现—策展正反馈消融。",
                "飞哥判断": "证据链完整，但尚不能证明复杂软件工程/开放科研盲区同样可被自动构造。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（AppWorld / BFCLv3）；§3.3–3.5 方法与门控。",
        "版本戳：arXiv:2607.27360v1 [cs.AI] 29 Jul 2026；ChatGPT 0731批次 #1。",
        "单位：The Hong Kong Polytechnic University · Tencent Platform and Content Group · Soochow University。",
        "证据覆盖：冻结执行器 + 零标注约束下的相对增益；开放域外推与技能冲突仍待验证。",
    ],
    "so_what": "说白了，自我演化规模化之后，最贵的风险可能是：系统从来不主动找自己的能力边界。SkillMentor 把诊断从修错前置，做成可训练能力。",
    "feige_view": "别把红队当成偶尔抽检。给技能平台加一个「找盲区」岗：KPI 看诊断间隙有没有缩小、纠正技能能不能复用——别再只数修了几条轨迹。对照昨日 SkillBoost：一个问更新稳不稳，一个问缺口找没找。",
    "limitations": [
        "不过，Mentor 生成的诊断任务可能偏向容易自动构造和验证的盲区。",
        "AppWorld / BFCLv3 主要覆盖工具使用，开放科研或复杂软件工程里的隐性缺口，这篇还没证明能找出来。",
        "技能持续入库后，冲突、冗余和负迁移仍可能把库拖垮。",
    ],
    "related_theme_picks": {
        "theme": "Agent 自我演化：找缺口与管经验",
        "intro": "本篇讲主动诊断盲区；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.27415",
                "title_cn": "行动图正负价值记忆",
                "one_liner": "同日配对：成败经验如何指导下次搜索。",
                "link": "https://arxiv.org/abs/2607.27415",
                "ready_date": "20260801",
            },
            {
                "arxiv_id": "2607.26643",
                "title_cn": "技能演化防过拟合",
                "one_liner": "昨日主发：更新技能必须过回归关。",
                "link": "https://arxiv.org/abs/2607.26643",
                "ready_date": "20260731",
            },
            {
                "arxiv_id": "2607.27191",
                "title_cn": "开放科研影子评测",
                "one_liner": "能力真伪：工程能做≠可发表研究。",
                "link": "https://arxiv.org/abs/2607.27191",
                "ready_date": "20260731",
            },
        ],
    },
    "target_audience": [
        "做 Agent Skills / 外部程序性记忆 / 技能库平台的团队。",
        "关心自我演化如何发现未知缺口的工程与评测负责人。",
        "评估红队自动化与技能版本治理的产品同学。",
    ],
    "sales_use_cases": [
        "回应『我们会从失败里学习』：先问失败是用户撞出来的，还是系统主动找出来的。",
        "方案评审：要求看诊断任务生成策略、入库门控与旧技能驱逐规则。",
        "路线图沟通：修错流水线与找盲区流水线分开验收。",
    ],
    "objection_handling": [
        "客户说：『换更强执行模型就行？』→ 回应：论文冻结执行器仍涨 44.2%，瓶颈在诊断侧。",
        "客户说：『提示一个强模型当导师不行吗？』→ 回应：同设置下可学习 Mentor 持续优于静态强提示导师。",
    ],
    "copy_paste_lines": [
        "自我演化别只会修已知失败：先学会主动找盲区。",
        "冻结执行权重仍平均 +44.2%：诊断本身可学。",
        "验收自我改进：修错流水线之外，还要有找缺口流水线。",
    ],
    "key_quotes": [
        "learning to discover what an agent does not know",
        "44.2% average relative improvement",
        "freeze the executor and remove human supervision",
    ],
    "score_rationale": "SkillMentor把盲区诊断做成可学习Mentor能力，冻结执行器+零标注下AppWorld/BFCLv3平均+44.2%。Impact/Novelty高；Evidence中高；Applicability中高；Reusability略低因技能冲突与开放域外推未解。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "相对 No Skill 平均提升 44.2%", "evidence": "Abstract + Table 1 narrative", "location": "Abstract / Table 1"},
            {"claim": "Qwen3.5-9B Avg Acc 0.478→0.682；AppWorld 0.300→0.410；BFCLv3 Agentic 0.452→0.660", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "优于 Reflexion/MemP/ReasoningBank 与 DeepSeek-V4-Flash 提示导师", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "冻结执行器、零人工标注约束下归因诊断贡献", "evidence": "Abstract + §1 / Figure 1", "location": "Abstract / §1"},
            {"claim": "证据覆盖完整但不足以证明开放域/复杂工程盲区同等可发现", "evidence": "Limitations discussion", "location": "F / Limitations"},
        ]
    },
}


GAMER_RICH = {
    "intro_lead": "",
    "A_research_problem": "推理预算往上加，相似问题却还在重复踩坑——Best-of-N 常常是无状态的。纯文本记忆又把检索和价值判断绑在 LLM 上：上下文贵，失败经验也很难变成「别这么做」。",
    "B_core_contributions": [
        "用行动图而非纯文本摘要保存 episodic experience",
        "双流 TD：正价值建议、负价值规避高风险行动",
        "记忆决策机制与 LLM 解耦，降低上下文与调用成本",
    ],
    "C_method_framework": "把历史推理建成 Action-Centric Graph；双流 TD 分别学正建议价值 Q+ 与负规避价值 Q−；推理时用图指导搜索，记忆决策与 LLM 解耦。",
    "D_key_results": [
        "相对 vanilla 成功率/进度率分别 +20.81% / +6.17%（四基准 × 四模型均值）",
        "AlfWorld 成功率相对 vanilla 约 +53.17%；相对次优 A-Mem 进度率约 +5 个百分点",
        "相对 A-Mem 平均约省 50% token（1.41M vs 2.76M）；图构建约 0.0013s、TD 学习每任务 <4s",
    ],
    "E_industry_implications": [
        "看板多加两列：重复探索次数、规避命中率；成功率单独看会骗自己",
        "失败轨迹必须进价值更新——只存成功案例，等于把避坑手册撕掉",
        "先在工具调用/规划这类结构可复现的任务试；开放域行动对齐另开实验",
    ],
    "F_one_line_judgement": "这篇最适合需要重复探索的长程 Agent：它证明行动图记忆能抬成功率并省 token，但行动等价性与错误经验传播仍是限制，开放域外推也未验证。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "GAMER", "definition": "Graph-based Action-centric Memory with Episodic Reasoning：行动中心图 + 双流价值记忆。"},
        {"term": "Action-Centric Graph", "definition": "以离散行动为节点、用历史轨迹连边的动态图记忆。"},
        {"term": "Dual-stream TD", "definition": "分别估计正向建议价值 Q+ 与负向规避价值 Q− 的时序差分学习。"},
        {"term": "Inference-time scaling", "definition": "用更多测试时计算（如 Best-of-N）换推理表现。"},
        {"term": "Success / Progress Rate", "definition": "AgentBoard 风格指标：任务成功与过程完成进度。"},
    ],
    "method_subsections": [
        {
            "title": "机制：为何无状态搜索贵",
            "body": "每次 Best-of-N 从零展开搜索，会反复验证已知死路。没有可积累的行动价值，token 只会跟着 N 线性堆。",
        },
        {
            "title": "为什么要正负双流",
            "body": "正价值告诉「值得试什么」，负价值告诉「别再踩坑」。只学成功会漏掉高风险行动；只罚失败又缺少可迁移启发。",
        },
        {
            "title": "为何与 LLM 解耦",
            "body": "价值更新走图上的 TD，不依赖再调 LLM 做记忆摘要；上下文更短、费用更可预期。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主增益",
                "论文证据": "相对 vanilla SR/PR +20.81% / +6.17%；AlfWorld SR 约 +53.17%。",
                "飞哥判断": "有状态记忆对重复探索任务的回报最明显。",
            },
            {
                "看什么": "对照强度",
                "论文证据": "均值上优于 A-Mem 等记忆/自演化基线；Tool 基准上仍能继续抬，而 A-Mem 难增益。",
                "飞哥判断": "细粒度行动建议比粗粒度记忆召回更稳。",
            },
            {
                "看什么": "效率",
                "论文证据": "相对 A-Mem 约省 50% token（1.41M vs 2.76M）；图构建 0.0013s、TD <4s/任务。",
                "飞哥判断": "省下来的，主要是少让 LLM 再做一遍记忆推理。",
            },
            {
                "看什么": "证据覆盖",
                "论文证据": "AlfWorld / SciWorld / PDDL / Tool × 四模型；含缩放曲线与 token 表。",
                "飞哥判断": "证据完整，但行动节点跨状态等价与错误价值传播仍是工程风险。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（SR/PR）；Table 2（token）；§5.1 AlfWorld +53.17% 叙述。",
        "版本戳：arXiv:2607.27415v1 [cs.AI] 29 Jul 2026；ChatGPT 0731批次 #2。",
        "单位：Florida International University · Stanford University · NEC Laboratories America · Singapore Management University。",
        "证据覆盖：四基准×四模型；行动等价性与环境漂移下的价值稳健性仍待验证。",
    ],
    "so_what": "说白了，推理预算上涨之后，该盯的是：过去成败有没有变成可查询的行动价值。GAMER 把记忆从召回事实，做成搜索策略资产。",
    "feige_view": "别把失败日志当事后复盘附件。每次探索更新一张「做什么 / 别做什么」的行动价值图，再塞进下一轮 Best-of-N。对照今日 SkillMentor：一个找能力缺口，一个复用探索经验。",
    "limitations": [
        "不过，不同任务状态下行动节点如何等价，仍是工程局限。",
        "TD 价值会跟着环境变化和历史策略偏；错误经验也可能在图里继续传播。",
        "当前结果主要来自 AgentBoard 风格环境，开放域行动对齐仍未验证。",
    ],
    "related_theme_picks": {
        "theme": "Agent 自我演化：找缺口与管经验",
        "intro": "本篇讲行动图记忆如何服务推理扩展；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.27360",
                "title_cn": "盲区诊断自我演化",
                "one_liner": "同日配对：主动找还没暴露的能力缺口。",
                "link": "https://arxiv.org/abs/2607.27360",
                "ready_date": "20260801",
            },
            {
                "arxiv_id": "2607.26643",
                "title_cn": "技能演化防过拟合",
                "one_liner": "昨日主发：技能更新必须过回归关。",
                "link": "https://arxiv.org/abs/2607.26643",
                "ready_date": "20260731",
            },
            {
                "arxiv_id": "2607.25090",
                "title_cn": "分层展开子Agent",
                "one_liner": "长程结构：压缩战略、展开执行。",
                "link": "https://arxiv.org/abs/2607.25090",
                "ready_date": "20260730",
            },
        ],
    },
    "target_audience": [
        "做长程 Agent / test-time search / Best-of-N 的工程团队。",
        "关心 Agent Memory 成本与失败经验复用的架构同学。",
        "评估推理预算 ROI 的产品与评测负责人。",
    ],
    "sales_use_cases": [
        "回应『再加预算就能涨』：先问有没有把历史失败变成规避价值。",
        "方案评审：要求看行动图更新规则、正负价值口径与 token 对照。",
        "成本沟通：相对文本记忆摘要，图上 TD 往往更可预期。",
    ],
    "objection_handling": [
        "客户说：『多塞点轨迹进上下文不行吗？』→ 回应：论文相对 A-Mem 约省一半 token 仍更高分。",
        "客户说：『失败经验会不会污染？』→ 回应：同意风险；负价值流就是为了显式管理，但仍需环境漂移监控。",
    ],
    "copy_paste_lines": [
        "推理别每次从零搜索：成败都该进行动价值图。",
        "相对 vanilla 成功率 +20.8%；相对 A-Mem 约省一半 token。",
        "Memory 要能建议，也要能规避——只召回事实不够。",
    ],
    "key_quotes": [
        "20.81%/6.17% for success/progress rate",
        "positive (suggestion) and negative (avoidance) value",
        "saves 50% tokens on average",
    ],
    "score_rationale": "GAMER用行动图+双流TD连接记忆与推理扩展，相对vanilla SR/PR +20.81%/+6.17%，相对A-Mem约省50% token。Impact/Novelty/Evidence/Applicability中高；Reusability略低因行动等价与错误传播。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "相对 vanilla 成功率/进度率 +20.81%/+6.17%", "evidence": "Abstract + Table 1", "location": "Abstract / Table 1"},
            {"claim": "AlfWorld 成功率相对 vanilla 约 +53.17%", "evidence": "§5.1 endpoint analysis", "location": "§5.1"},
            {"claim": "相对 A-Mem 约省 50% token（1.41M vs 2.76M）", "evidence": "Table 2 + §5 token analysis", "location": "Table 2"},
            {"claim": "图构建约 0.0013s、TD 学习每任务 <4s", "evidence": "§5 inference time comparison", "location": "§5"},
            {"claim": "行动等价性与错误经验传播仍是落地边界", "evidence": "Discussion / Limitations", "location": "F / Limitations"},
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
    style_tag = "Style-shenfei + de-AI review pass 20260801: cut 不是而是 / 真正该落地的是; vary 不过 openings; tighten E"
    if style_tag not in notes:
        notes.append(style_tag)
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
        "2607.27360",
        "skillmentor",
        SKILLMENTOR_RICH,
        "自我演化别只会修已知失败：SkillMentor主动找盲区平均提升44.2%",
        "失败别再只等用户撞上：盲区诊断可以学成独立能力，冻结执行权重也能把纠正技能沉淀下来。",
    )
    enrich_one(
        "2607.27415",
        "gamer",
        GAMER_RICH,
        "推理别每次从零搜索：GAMER把成败记成正负价值图成功率+20.8%",
        "推理预算往上加，仍在重复踩坑？把历史行动建成图，用正负价值同时告诉 Agent 该做什么、别做什么。",
    )
    print("enriched skillmentor + gamer")


if __name__ == "__main__":
    main()
