#!/usr/bin/env python3
"""One-off enrichment for 20260727 paper-notes payloads (FlowEvo + Regression Tax)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260727"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


FLOWEVO_RICH = {
    "A_research_problem": "LLM Agent越来越靠推理期工作流（分解、工具、写代码、校验、修复）解题，但成功轨迹往往只以文本短暂存在。后续任务仍要从头探索：既烧token，又难把程序性经验迁移出去。",
    "B_core_contributions": [
        "把成功轨迹编译成持久可调用的skill records，而非纯文本记忆",
        "技能可直接执行或注入结构化上下文，支撑后续工作流构造",
        "按下游效用策展并抑制负迁移技能，无需更新模型参数",
        "在ALFWorld与HumanEval/GSM8K上验证准确率–成本权衡，并开源代码",
    ],
    "C_method_framework": "无训练闭环：成功且通过校验的轨迹→编译可调用skill record（接口/重放/安全检查后入库）→检索后走直接执行或技能条件生成→按下游对比成功率抑制有害技能。自演化发生在推理期能力层（技能银行），不改模型权重。",
    "D_key_results": [
        "ALFWorld成功率82.8%，较最强基线AFLOW高23.6个百分点（Reflexion仅52.2%）",
        "ALFWorld平均token 12,267，低于任一基线一半（基线约2.97万–3.30万）",
        "HumanEval 95.1%/880tok；GSM8K 97.1%/541tok",
        "消融：ReAct 33.6%→编译38.8%→技能反馈80.6%→策展82.8%（S2W主导+41.8pp）；直接复用101/134、命中约75%",
    ],
    "E_industry_implications": [
        "把Agent记忆产品从『存摘要/反思』升级为『可调用技能库+准入与淘汰』",
        "上线技能库时同步做负迁移监控，而不是只报平均成功率",
        "交互环境优先投可复用执行体；单题代码/数学则看技能条件生成能否省掉固定多阶段流水线",
    ],
    "F_one_line_judgement": "Agent缺的不是更多文本反思，而是能直接调用、可策展、会淘汰负迁移的可执行技能层。",
    "glossary": [
        {"term": "Skill record", "definition": "可调用执行体 + 结构化指导与元数据；不是自由文本笔记。"},
        {"term": "W2S / S2W", "definition": "Workflow-to-Skill编译；Skill-to-Workflow反馈（直接执行或上下文注入）。"},
        {"term": "Skill curation", "definition": "按下游效用抑制造成负迁移的技能，无需改模型参数。"},
        {"term": "Direct execution vs skill-conditioned generation", "definition": "兼容则直接跑技能；否则把技能当结构化上下文生成新工作流。"},
        {"term": "ALFWorld", "definition": "文本家务交互环境；成功由环境二进制反馈判定。"},
        {"term": "AFLOW / ADAS / Reflexion / ExpeL", "definition": "对照：工作流拓扑搜索或文本级反思/经验积累方法。"},
    ],
    "method_subsections": [
        {
            "title": "问题：成功工作流不该只活这一集",
            "body": "文本记忆难验证、难调用；手写工具又太固定。FlowEvo把成功工作流落在两者之间：可执行、可审计、可策展。",
        },
        {
            "title": "闭环：编译 → 复用 → 策展",
            "body": "只从校验通过的成功回合编译；入库前做接口/重放/安全检查；检索后双路由；负对比效用触发抑制。",
        },
        {
            "title": "验收：准确率与token一起看",
            "body": "主表同时报成功率与平均token；消融拆开编译、反馈、策展三块贡献，避免只吹一个总分。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "ALFWorld主结果（Table 2）",
                "论文证据": "FlowEvo 82.8% / 12,267 tok；AFLOW 59.2% / 30,137；Reflexion 52.2% / 31,900。",
                "飞哥判断": "可执行复用同时抬成功率与砍探索成本，不是堆更长推理。",
            },
            {
                "看什么": "代码/数学",
                "论文证据": "HumanEval 95.1%/880；GSM8K 97.1%/541；AFLOW/ADAS token常3k–4k级。",
                "飞哥判断": "固定多阶段流水线贵；技能条件生成+自适应升级更省。",
            },
            {
                "看什么": "机制消融（§4.3）",
                "论文证据": "33.6→38.8→80.6→82.8；S2W +41.8pp占主导；策展再+2.2。",
                "飞哥判断": "关键在技能反馈，不是只把轨迹写进笔记。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "GPT-4o-mini设定；ALFWorld在线累积134题；跨基准不传技能；离线编译/重放有成本。",
                "飞哥判断": "换模型与开放工具接口后，技能失效与治理成本要重测。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 2（ALFWorld/HumanEval/GSM8K）；§4.3消融；Fig.2复用动态。",
        "投稿/版本戳：arXiv:2607.21596v1 [cs.AI]；ChatGPT 0727 #1；代码 https://github.com/DEFENSE-SEU/FlowEvo。",
        "单位：Southeast University · Rensselaer Polytechnic Institute · HKUST。",
        "证据边界：单模型API设定；交互环境在线累积；跨环境接口漂移与长期技能治理开放。",
    ],
    "so_what": "说白了，Agent自我演化不该停在『多写几段反思』。FlowEvo证明：把成功工作流编译成可调用技能，再按下游收益淘汰有害技能，才能同时抬成功率与砍token。",
    "feige_view": "三个动作：①记忆层加『可执行体+准入检查』，别只存摘要；②看板加技能复用命中率与负迁移对比；③和今日Regression Tax对照——积累技能时必须算回归税。",
    "limitations": [
        "不过，技能编译与重放验证会抬高离线成本；生产上要预算这笔账。",
        "不过，跨环境接口变化可能导致技能失效，需要版本与失效检测。",
        "不过，技能库长期增长后的去重、版本管理和安全治理仍是开放问题。",
    ],
    "related_theme_picks": {
        "theme": "Agent技能积累与负迁移",
        "intro": "本篇讲如何把成功工作流变成可执行技能；同线可对照：",
        "items": [
            {"arxiv_id": "2607.22520", "title_cn": "技能回归税", "one_liner": "同日配对：技能为何也会伤害Agent。", "link": "https://arxiv.org/abs/2607.22520", "ready_date": "20260727"},
            {"arxiv_id": "2607.21419", "title_cn": "策略感知训练脚手架", "one_liner": "训练期可丢弃支持 vs 推理期可执行技能。", "link": "https://arxiv.org/abs/2607.21419", "ready_date": "20260726"},
            {"arxiv_id": "2607.21461", "title_cn": "验证驱动深研状态", "one_liner": "另一条自演化线：约束审计递归补研。", "link": "https://arxiv.org/abs/2607.21461", "ready_date": "20260725"},
        ],
    },
    "target_audience": [
        "做Agent记忆/技能库/长期运行系统的研究与平台团队。",
        "关心推理成本与可复用程序性经验的产品负责人。",
        "评估『自动积累技能』是否可靠的技术决策者。",
    ],
    "sales_use_cases": [
        "回应『我们有Agent记忆』：用82.8%与token腰斩说明关键是可调用技能，不是摘要。",
        "方案评审：要求技能准入（接口/重放/安全）与负迁移抑制。",
        "成本沟通：ALFWorld token约1.2万 vs 基线约3万，谈的是探索绕路被砍掉。",
    ],
    "objection_handling": [
        "客户说：『不就是工具库吗？』→ 回应：工具是人手写的；FlowEvo从成功工作流自动编译并可策展淘汰。",
        "客户说：『文本记忆也行。』→ 回应：文本难直接调用与验证；主增益来自S2W可执行反馈（+41.8pp）。",
    ],
    "copy_paste_lines": [
        "Agent别只存文本记忆，要把成功工作流编译成可执行技能。",
        "ALFWorld 82.8%，比AFLOW高23.6pp，token不到最高效基线一半。",
        "技能反馈贡献+41.8pp；策展再收掉负迁移。",
    ],
    "key_quotes": [
        "workflow–skill–workflow feedback loop",
        "compiles successful traces into reusable skill records",
        "suppresses skills that cause negative transfer",
    ],
    "score_rationale": "FlowEvo把成功工作流编译成可调用skill records，形成工作流→技能→新工作流闭环，并以接口/重放/安全检查与下游负迁移抑制做策展，无需更新模型参数。ALFWorld 82.8%（较AFLOW +23.6pp），token约12267约为最高效基线一半以下；HumanEval 95.1%/880tok、GSM8K 97.1%/541tok；消融显示S2W贡献主导（+41.8pp）。Impact高：对准Agent技能积累与推理成本。Novelty高：可执行技能+策展闭环。Evidence高：三基准+消融+代码仓。Applicability高：训练无关、可挂现有agent。Reusability中高：范式可迁移，跨环境接口漂移与离线验证成本仍是限制。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "ALFWorld 82.8%，较AFLOW +23.6pp；token 12,267", "evidence": "Table 2 main results GPT-4o-mini", "location": "Table 2"},
            {"claim": "HumanEval 95.1%/880；GSM8K 97.1%/541", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "消融33.6→38.8→80.6→82.8；S2W +41.8pp", "evidence": "Section 4.3 ablation study", "location": "§4.3"},
            {"claim": "直接复用101/134，命中约75%", "evidence": "Figure 2 skill accumulation dynamics", "location": "Figure 2"},
            {"claim": "F段限制：离线成本、接口漂移、长期治理", "evidence": "Limitations + ChatGPT notes", "location": "Limitations"},
        ]
    },
}


REGTAX_RICH = {
    "A_research_problem": "给Agent加程序性技能通常只报平均成功率。这会掩盖回归——原本能完成的任务在加技能后失败——也看不到技能描述仅存在于上下文、甚至未被调用时的隐性干扰。",
    "B_core_contributions": [
        "把通过率变化配对分解为gains与regressions，量化回归税",
        "识别三类回归机制，含未被调用时的描述渗透（osmosis）",
        "把残差失败定位到grounding与verification，而非缺更多程序性步骤",
        "在两基准×三harness、5832次任务条件运行上给出可复现分解",
    ],
    "C_method_framework": "固定模型与harness，只换技能库；与无技能条件配对比较。通过率差=（增益数−回归数）/任务数。用轨迹判据标注osmosis、grounding displacement、verification displacement，并纠正评分器伪影后重评。",
    "D_key_results": [
        "5832次任务条件运行；324次回归抵消553次毛收益的59%，净剩229",
        "OfficeQA-Pro：增益122/破坏81（66%抵消）；SpreadsheetBench：431/243（56%抵消）",
        "按增益排序与按净效应排序会颠倒库名次：少回归比多增益更决定赢家",
        "残差失败主要落在grounding与verification；程序性步骤往往不是瓶颈",
    ],
    "E_industry_implications": [
        "技能/MCP说明上线前做配对回归测试，而不只看平均通过率",
        "技能库治理要同时管『被调用』与『仅出现在上下文』两条通道",
        "优先补齐输入对齐与输出校验能力，而不是继续堆程序性步骤",
    ],
    "F_one_line_judgement": "技能库该用gains减regressions来验收：最好的技能常常是少破坏，而不是多刷新增成功。",
    "glossary": [
        {"term": "Regression", "definition": "无技能时通过、加技能后失败的任务；与双方都失败的residual failure区分。"},
        {"term": "Regression tax", "definition": "毛收益被回归抵消的部分；文中324抵消553的59%。"},
        {"term": "Skill-description osmosis", "definition": "技能未被调用，仅因描述出现在上下文就改变行为。"},
        {"term": "Grounding / Verification displacement", "definition": "固定流程覆盖正确输入理解，或抑制本会执行的输出校验。"},
        {"term": "OfficeQA-Pro / SpreadsheetBench", "definition": "金融文档问答与表格操作两个办公自动化基准。"},
        {"term": "Model–harness stack", "definition": "评测用的三套『模型+脚手架』组合；库变、栈不变。"},
    ],
    "method_subsections": [
        {
            "title": "先改口径：平均涨分会撒谎",
            "body": "两个库可以有同样平均增益，却破坏完全不同数量的任务。必须配对拆开增益与回归。",
        },
        {
            "title": "三条伤人路径",
            "body": "osmosis管『没调用也干扰』；grounding与verification displacement管『流程挤掉正确读入与校验』。",
        },
        {
            "title": "残差失败指哪补哪",
            "body": "持续失败更多卡在读对输入与验对输出，而不是再缺一段程序性说明。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "回归税总量",
                "论文证据": "553 gains vs 324 regressions；抵消59%，净229。",
                "飞哥判断": "只报涨分会漏掉近六成毛收益被自己吃掉。",
            },
            {
                "看什么": "分基准",
                "论文证据": "OfficeQA 122/81（66%）；Spreadsheet 431/243（56%）。",
                "飞哥判断": "两边都不是噪声；办公自动化技能库尤其要算回归。",
            },
            {
                "看什么": "名次颠倒",
                "论文证据": "同栈内按gains与按net排序可相反；赢家常因少回归。",
                "飞哥判断": "选型指标要从『谁新增最多』改成『谁破坏最少』。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "两办公基准、三harness；技能形式与描述方式会显著影响结果；尚无完整自动修复。",
                "飞哥判断": "诊断框架可迁移，编码Agent/研究Agent外推需重测。",
            },
        ],
    },
    "source_notes": [
        "主数字：Contributions（324/553/59%）；Table 2配对分解；Table 3–4机制标注。",
        "投稿/版本戳：arXiv:2607.22520v1 [cs.AI] 24 Jul 2026；ChatGPT 0727 #5；Sentient skill-creator相关资产见论文脚注。",
        "单位：Sentient Labs。",
        "证据边界：办公自动化域；技能写法敏感；诊断为主、自动修复未闭环。",
    ],
    "so_what": "说白了，『让Agent自动积累技能』若只看平均成功率，会系统性低估伤害。Regression Tax把账拆开：赢家往往靠少破坏，而残差错误更该补grounding与verification。",
    "feige_view": "三个动作：①技能上线门禁改成配对回归报表；②系统提示里的技能目录也要测presence-only；③和FlowEvo同看——能编译技能不够，还要能算清回归税。",
    "limitations": [
        "不过，实验集中在两个办公自动化基准与三种harness，外推到编码/研究Agent需折扣。",
        "不过，技能形式和描述方式可能显著影响结果，机制占比会变。",
        "不过，论文主要做失效分解，尚未形成完整自动修复闭环。",
    ],
    "related_theme_picks": {
        "theme": "Agent技能积累与负迁移",
        "intro": "本篇讲技能为何伤害Agent；同线可对照：",
        "items": [
            {"arxiv_id": "2607.21596", "title_cn": "可执行技能共演化", "one_liner": "同日配对：如何把成功工作流编译成技能。", "link": "https://arxiv.org/abs/2607.21596", "ready_date": "20260727"},
            {"arxiv_id": "2607.21419", "title_cn": "策略感知训练脚手架", "one_liner": "训练期可丢弃支持，避免永久技能干扰。", "link": "https://arxiv.org/abs/2607.21419", "ready_date": "20260726"},
            {"arxiv_id": "2607.21461", "title_cn": "验证驱动深研状态", "one_liner": "另一条自演化线：约束审计递归补研。", "link": "https://arxiv.org/abs/2607.21461", "ready_date": "20260725"},
        ],
    },
    "target_audience": [
        "做Agent Skills/MCP工具说明/系统提示模块化的团队。",
        "建设长期技能库与自动技能生成的平台同学。",
        "用平均成功率验收Agent能力的产品与质量负责人。",
    ],
    "sales_use_cases": [
        "回应『我们技能库提升了X%』：要求同时报regression count与配对Δ。",
        "方案评审：presence-only消融必须进门禁。",
        "对标沟通：用59%抵消率说明为何不能只看毛增益。",
    ],
    "objection_handling": [
        "客户说：『回归可以靠检索过滤。』→ 回应：osmosis在未调用时也会伤；过滤调用不够。",
        "客户说：『再多写点程序性步骤就好。』→ 回应：残差失败主要在grounding/verification。",
    ],
    "copy_paste_lines": [
        "加技能别只看平均涨分，先算回归税。",
        "324次回归抵消553次毛收益的59%。",
        "最好的技能往往是少破坏，而不是多新增。",
    ],
    "key_quotes": [
        "regressions offset 59% of gross gains",
        "skill-description osmosis",
        "reliability depends more on grounding and verification",
    ],
    "score_rationale": "Regression Tax把技能库净提升拆成gains与regressions：5832次配对运行中，324次回归抵消553次毛收益的59%。三类机制——description osmosis、grounding displacement、verification displacement——解释为何最好的技能往往是『少破坏』而非『多新增』。Impact高：直接反证技能库堆量叙事。Novelty高：presence-only效应与配对分解。Evidence高：双基准×三harness、机制标注与grader纠错。Applicability中高：对MCP/技能说明/提示模块化有即用规范，但场景偏办公自动化。Reusability中：诊断框架可迁移，自动修复闭环尚未成形。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "324 regressions offset 59% of 553 gains；净229", "evidence": "Contributions bullet 1 / §Regression Tax", "location": "Contributions / §Results"},
            {"claim": "OfficeQA 122/81；Spreadsheet 431/243", "evidence": "Paired decomposition discussion", "location": "§Results"},
            {"claim": "按gains与按net排序可颠倒", "evidence": "Table 2 discussion / ranking reversal", "location": "Table 2"},
            {"claim": "三类机制含osmosis；残差在grounding/verification", "evidence": "Abstract + Tables 3–4 + Figure 1", "location": "Abstract / Tables 3–4"},
            {"claim": "F段限制：办公域、技能写法、无完整自动修复", "evidence": "Limitations + ChatGPT notes", "location": "Limitations"},
        ]
    },
}


def distinct_score_detail(score_obj: dict, reason: str) -> dict:
    dims = score_obj["dimensions"]
    values = [d["value"] for d in dims]
    hi = max(values)
    lo = min(values)
    rationales = []
    per = {
        "重要性 Impact": "看问题是否卡在真实Agent系统瓶颈，以及对验收/训练看板是否有直接影响。",
        "创新性 Novelty": "看方法或基础设施接口是否有辨识度：是新的问题定义/协议，还是已知模块的常规堆叠。",
        "可验证性 Evidence": "看对照是否干净、数字是否可追溯，以及设定带来的外推折扣。",
        "产业可用性 Applicability": "看单位、开源、任务设定与落地动作是否够具体，能否直接改验收或部署配方。",
        "可复用性 Reusability": "看资产（代码/数据/协议）与抽象迁移到其他域时的摩擦。",
    }
    for d in dims:
        role = "highest" if d["value"] == hi else ("lowest" if d["value"] == lo else "middle")
        prefix = {
            "highest": "最高维，说明这篇最强的判断依据集中在这里。",
            "lowest": "最低维，是评分上限的主要约束，外推或复用需额外验证。",
            "middle": "中间维，有明确支撑，但不是本篇最突出的差异点。",
        }[role]
        rationales.append(
            {
                "label": d["label"],
                "value": d["value"],
                "role": role,
                "rationale": f"{prefix} {per.get(d['label'], '')} 总体依据：{reason}",
            }
        )
    return {
        "schema_version": 1,
        "score_range": round(hi - lo, 1),
        "highest_dimensions": [d["label"] for d in dims if d["value"] == hi],
        "lowest_dimensions": [d["label"] for d in dims if d["value"] == lo],
        "dimension_rationales": rationales,
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
    patch = {k: v for k, v in rich.items() if k != "evidence_ledger_patch"}
    data.update(patch)
    data["score_rationale_detail"] = distinct_score_detail(
        {"dimensions": data["score"]["dimensions"]},
        data.get("score_rationale") or "",
    )
    notes = data.get("discussion_notes") or []
    note = f"Enriched with rich fields via enrich_{DATE}.py"
    if note not in notes:
        notes.append(note)
    data["discussion_notes"] = notes

    if "evidence_ledger_patch" in rich:
        ledger = load(ledger_path) if ledger_path.exists() else {}
        ledger.setdefault("schema_version", 1)
        ledger.setdefault(
            "paper",
            {"arxiv_id": arxiv_id, "title": data["info"]["title"], "link": data["info"]["link"]},
        )
        ledger["claim_evidence"] = rich["evidence_ledger_patch"]["claim_evidence"]
        if data.get("score_rationale"):
            ledger["score_rationale"] = data["score_rationale"]
        dump(ledger_path, ledger)
        data["evidence_ledger"] = ledger
        dump(fused_ledger, ledger)

    dump(gen_path, data)
    dump(fused_article, data)
    card = load(card_path)
    card["info"] = data["info"]
    card["score"] = data["score"]
    dump(card_path, card)
    dump(fused_card, card)

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
        "2607.21596",
        "flowevo",
        FLOWEVO_RICH,
        "Agent别只存文本记忆：FlowEvo把成功工作流编译成可执行技能",
        "FlowEvo用工作流→技能→新工作流闭环，在ALFWorld拿到82.8%成功率，token不到最高效基线一半。",
    )
    enrich_one(
        "2607.22520",
        "regression-tax",
        REGTAX_RICH,
        "加技能别只看平均涨分：Regression Tax用配对分解算出负迁移账",
        "5832次配对运行里，324次回归抵消553次毛收益的59%；最好的技能往往是少破坏，而不是多新增。",
    )
    print("enriched flowevo + regression-tax")


if __name__ == "__main__":
    main()
