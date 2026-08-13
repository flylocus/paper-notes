#!/usr/bin/env python3
"""One-off enrichment for 20260729 paper-notes payloads (DeepLook + CALM)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260729"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


DEEPLOOK_RICH = {
    "A_research_problem": "现有inference-time scaling常对整条推理轨迹均匀加码：难题并非每一步都需要同样多的搜索预算，既浪费token，又难躲开局部自信的短视。",
    "B_core_contributions": [
        "把token级置信度聚合成更稳的segment-level触发信号",
        "仅在不确定性瓶颈触发有限深度lookahead，而非全程搜索",
        "用Average Lookahead Confidence评价候选继续路径并剪枝投票",
        "无需额外训练，可直接接入已有推理模型",
    ],
    "C_method_framework": "训练无关的monitor-and-intervene：把token置信聚成segment信号；相对历史明显下降时触发；对K条候选做固定地平线lookahead；用Average Lookahead Confidence排序、剪枝并投票。",
    "D_key_results": [
        "四竞赛数学基准×四模型共16组设置中，11组优于DeepConf-low",
        "数据集级生成token平均减少87.3%",
        "Qwen3-32B在AIME25提升+3.1；GPT-OSS-20B在BRUMO25提升+8.8",
        "相对Cons@512等大采样预算，可在显著更少token下取得更强准确率–成本权衡",
    ],
    "E_industry_implications": [
        "推理服务看板应区分『全程加预算』与『瓶颈触发搜索』两类成本",
        "把置信度监控做成可插拔解码中间件，而不是只调温度/采样数",
        "上线前同时验收准确率、平均token、峰值延迟与KV-cache成本",
    ],
    "F_one_line_judgement": "推理算力不该均匀洒在整条轨迹上，而应在不确定性瓶颈触发有限深度前瞻。",
    "glossary": [
        {"term": "Segment-level confidence", "definition": "把token置信聚成更稳的片段信号，用于触发而非直接当最终答案分数。"},
        {"term": "Uncertainty bottleneck", "definition": "相对近期历史，置信度明显下降、值得额外搜索的局部位置。"},
        {"term": "ALC", "definition": "Average Lookahead Confidence：候选续写在固定地平线上的平均片段置信。"},
        {"term": "DeepConf-low", "definition": "主要对照的置信过滤/轨迹筛选基线；DeepLook在多数设置上优于它且更省token。"},
        {"term": "Cons@N", "definition": "自洽采样N条再投票；DeepLook强调用更少token逼近甚至超过大N预算。"},
        {"term": "Pareto frontier", "definition": "准确率与token成本同时看时的权衡前沿；DeepLook目标是把它往左上推。"},
    ],
    "method_subsections": [
        {
            "title": "问题：算力不该整条轨迹均摊",
            "body": "错误轨迹往往更早、更多出现不确定片段。关键是定位瓶颈，而不是从头到尾加采样。",
        },
        {
            "title": "三步：监控 → 分支 → ALC剪枝",
            "body": "segment置信触发；固定地平线看未来；ALC排序后剪枝投票，避免局部token自信的短视。",
        },
        {
            "title": "验收：准确率与token一起看",
            "body": "主结论写在Pareto上：多数设置更准，同时数据集级token平均砍掉约九成相对DeepConf-low。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主对照（16组）",
                "论文证据": "四基准×四模型；11/16优于DeepConf-low；数据集级token平均−87.3%。",
                "飞哥判断": "这是『选择性加码』不是『压缩CoT口号』。",
            },
            {
                "看什么": "代表涨点",
                "论文证据": "Qwen3-32B/AIME25 +3.1；GPT-OSS-20B/BRUMO25 +8.8。",
                "飞哥判断": "省token时仍能抬分，说明预算打在了瓶颈上。",
            },
            {
                "看什么": "对大采样",
                "论文证据": "如AIME25/Qwen3-32B可超过Cons@512且约少17×token（文中示例）。",
                "飞哥判断": "先问『何时搜索』，再问『搜多少条』。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主战场是竞赛数学；开放Agent置信更噪；峰值延迟与KV成本需另测。",
                "飞哥判断": "解码中间件可试，别直接当成通用Agent调度器。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract / Fig.1；四基准 AIME24/25、BRUMO25、HMMT25；四模型 DeepSeek-R1-8B、Qwen3-32B、GPT-OSS-20B/120B。",
        "版本戳：arXiv:2607.22602v1 [cs.AI]；ChatGPT 0728批次 #1；文中称Code available（abs页未见公开仓库链接）。",
        "单位：Technical University of Munich · LMU Munich · MCML / MemAgents Lab。",
        "证据边界：竞赛数学为主；自信做错与wall-clock/批处理仍开放。",
    ],
    "so_what": "说白了，test-time scaling别再默认『整条轨迹加长』。DeepLook证明：只在不确定处做有限前瞻，才能同时抬准确率与砍token。",
    "feige_view": "三个动作：①推理网关加segment置信触发开关；②看板同时报准确率、平均token、峰值延迟；③和今日CALM对照——何时多算，与模型是否会配合编排，是同一系统的两面。",
    "limitations": [
        "不过，主验证在竞赛数学；开放式Agent任务里置信信号可能更不稳。",
        "不过，模型置信度不总能反映真实正确率，尤其可能对『自信地犯错』失效。",
        "不过，lookahead仍要生成多分支，单请求峰值延迟与KV-cache成本可能上升。",
    ],
    "related_theme_picks": {
        "theme": "推理动态预算与编排适配",
        "intro": "本篇讲何时花额外推理算力；同线可对照：",
        "items": [
            {"arxiv_id": "2607.23771", "title_cn": "配合多种推理控制器", "one_liner": "同日配对：训练模型适配不同inference-time controllers。", "link": "https://arxiv.org/abs/2607.23771", "ready_date": "20260729"},
            {"arxiv_id": "2607.21596", "title_cn": "可执行技能共演化", "one_liner": "另一条推理期能力层：成功工作流编译成技能。", "link": "https://arxiv.org/abs/2607.21596", "ready_date": "20260727"},
            {"arxiv_id": "2607.22520", "title_cn": "技能回归税", "one_liner": "加能力时别只看平均涨分。", "link": "https://arxiv.org/abs/2607.22520", "ready_date": "20260727"},
        ],
    },
    "target_audience": [
        "做推理服务/解码优化/test-time scaling的研究与平台团队。",
        "关心准确率–成本Pareto的推理产品负责人。",
        "评估『再加采样能不能更值』的技术决策者。",
    ],
    "sales_use_cases": [
        "回应『我们再开大采样』：用87.3% token下降说明关键是触发点，不是N越大越好。",
        "方案评审：要求同时验收峰值延迟与平均token，不只看离线准确率。",
        "成本沟通：把预算从全程self-consistency改成瓶颈lookahead。",
    ],
    "objection_handling": [
        "客户说：『不就是tree search吗？』→ 回应：只在置信瓶颈触发固定地平线，不是全程展开。",
        "客户说：『置信度不可靠。』→ 回应：文中把它当触发器，最终仍靠ALC未来检查与投票；开放域需重测。",
    ],
    "copy_paste_lines": [
        "推理别全程加预算，只在置信度瓶颈做前瞻。",
        "16组里11组优于DeepConf-low，token平均少87.3%。",
        "关键问题是：推理模型应当在什么时候花费额外计算？",
    ],
    "key_quotes": [
        "concentrate lookahead compute at uncertainty bottlenecks",
        "Average Lookahead Confidence (ALC)",
        "reducing dataset-level token generation by 87.3% on average",
    ],
    "score_rationale": "DeepLook把test-time compute从整条轨迹均匀加码，改成只在置信度瓶颈触发有限深度lookahead，并用Average Lookahead Confidence排序剪枝。四竞赛数学基准×四模型共16组设置中有11组优于DeepConf-low，数据集级token平均少87.3%，Qwen3-32B/AIME25 +3.1、GPT-OSS-20B/BRUMO25 +8.8。Impact高：对准推理何时该多算。Novelty高：segment置信触发+ALC未来检查。Evidence高：四基准四模型Pareto与对比Cons@512。Applicability高：训练无关可挂现有推理模型。Reusability中高：范式可迁，但开放Agent场景置信度与wall-clock/KV成本仍需实测。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "11/16设置优于DeepConf-low；token平均−87.3%", "evidence": "Abstract + Fig.1 summary", "location": "Abstract / Fig.1"},
            {"claim": "Qwen3-32B AIME25 +3.1；GPT-OSS-20B BRUMO25 +8.8", "evidence": "Abstract representative wins", "location": "Abstract"},
            {"claim": "相对Cons@512可用约17×更少token取得更强权衡（文中示例）", "evidence": "Introduction quantitative claim", "location": "§1"},
            {"claim": "方法：segment触发 + ALC排序剪枝投票", "evidence": "Method / Fig.1 pipeline", "location": "§Method"},
            {"claim": "F段限制：数学域、自信做错、峰值延迟/KV", "evidence": "Limitations + ChatGPT notes", "location": "Limitations"},
        ]
    },
}


CALM_RICH = {
    "A_research_problem": "后训练常假设单一交互模式，但部署会用CoT、自洽、辩论、规划、校验等不同controller，造成训练–部署错配与工作流迁移失败。",
    "B_core_contributions": [
        "把controller-aware后训练表述为多任务强化学习",
        "将复杂controller分解为可复用的局部推理模块",
        "用turn-level GRPO训练不同controller与模块组合",
        "在held-out组合与更大controller shift上评估工作流迁移",
    ],
    "C_method_framework": "把controller-aware后训练写成多任务RL：controller由可复用local modules组合；用turn-level GRPO在多controller分布上训练，并比较MIXED/模块分解/自适应梯度平衡等变体。",
    "D_key_results": [
        "GSM8K训练controller平均：CALM-ADAPTIVE 73.72% vs 最强单控Step-back 71.11%",
        "组合层：ADAPTIVE 70.68%、MIXED 70.31%，高于最强单控68.31%",
        "controller shift层：MIXED 75.69%、SINGLE 75.46%，略高于CoT 74.91%",
        "AMC2023上MIXED三档平均20.00/26.25/23.75，显著高于CoT基线16.25/18.75/22.50",
    ],
    "E_industry_implications": [
        "Agent平台选型时，把『换编排是否掉点』列入验收，而不只测单流程",
        "后训练数据应按controller模块词表覆盖，避免只刷一种CoT模板",
        "多controller训练要单独预算不稳定与样本成本，不能当免费增益",
    ],
    "F_one_line_judgement": "部署侧controller会变，后训练就不能只优化一种固定推理协议。",
    "glossary": [
        {"term": "Inference-time controller", "definition": "组织推理的外部编排：CoT、自洽、辩论、规划、校验等。"},
        {"term": "Module", "definition": "可复用局部角色+接口，如COT/CRITIC/DEBATER/JUDGE；controller是其组合。"},
        {"term": "Turn-level GRPO", "definition": "把GRPO聚合到turn层，适配多轮、可变长度controller轨迹。"},
        {"term": "Compositional / Shift", "definition": "组合=熟悉模块新拼法；Shift=测试时引入新模块类型。"},
        {"term": "CALM-MIXED / ADAPTIVE", "definition": "MIXED平坦混训；ADAPTIVE按模块梯度范数做自适应加权。"},
        {"term": "Code-as-controller", "definition": "用可执行程序定义controller流程（文中沿ADAS思路），便于扩展与复现。"},
    ],
    "method_subsections": [
        {
            "title": "错配：训练一种、部署一堆",
            "body": "单controller后训练容易在本流程上漂亮、换编排就塌。部署现实是controller家族，不是一个提示模板。",
        },
        {
            "title": "把controller拆成模块再混训",
            "body": "共享模块词表 + turn-level GRPO；比较MIXED与多种模块分解/平衡策略。",
        },
        {
            "title": "验收分三层",
            "body": "训练controller平均、held-out组合、更大shift；再用MATH500/AMC看分布外迁移。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "相对单控",
                "论文证据": "四变体训练平均71.49%–73.72%，高于最强单控Step-back 71.11%。",
                "飞哥判断": "多controller训练不是平均稀释，而是抗过拟合。",
            },
            {
                "看什么": "组合 vs shift",
                "论文证据": "组合层ADAPTIVE最好；shift层MIXED更稳，ADAPTIVE可能掉到CoT以下。",
                "飞哥判断": "没有通吃变体；看你更怕『新拼法』还是『新模块』。",
            },
            {
                "看什么": "更难数学",
                "论文证据": "AMC2023上MIXED三档20.00/26.25/23.75 vs CoT 16.25/18.75/22.50。",
                "飞哥判断": "编排迁移收益在更难分布上更清楚。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主模型Llama-3.2-3B；数学题；多轮RL不稳；真实Agent harness未全覆盖。",
                "飞哥判断": "范式重要，生产要重测工具协议与更大模型。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 2（GSM8K各controller）；Table 3（MATH500/AMC2023）；§6讨论。",
        "版本戳：arXiv:2607.23771v1 [cs.AI] 26 Jul 2026；ChatGPT 0728批次 #2。",
        "单位：University of Massachusetts Amherst · Mitsubishi Electric Research Laboratories。",
        "证据边界：小模型数学域；多轮训练不稳；Agent工具协议外推需重测。",
    ],
    "so_what": "说白了，模型能力越来越由『权重+推理控制器』共同决定。CALM证明：后训练要把controller家族放进回路，模型才能在换编排时少塌方。",
    "feige_view": "三个动作：①验收加『换controller掉点』项；②SFT/RL数据按模块词表覆盖；③和今日DeepLook对照——一边决定何时多算，一边决定模型会不会配合你的编排。",
    "limitations": [
        "不过，多controller训练扩大分布与优化复杂度，且多轮GRPO可能不稳定。",
        "不过，模块词表与controller设计本身带人工偏差。",
        "不过，尚不确定能否覆盖真实Agent harness与工具协议差异。",
    ],
    "related_theme_picks": {
        "theme": "推理动态预算与编排适配",
        "intro": "本篇讲模型如何配合多种推理控制器；同线可对照：",
        "items": [
            {"arxiv_id": "2607.22602", "title_cn": "置信瓶颈前瞻", "one_liner": "同日配对：何时投入更多推理计算。", "link": "https://arxiv.org/abs/2607.22602", "ready_date": "20260729"},
            {"arxiv_id": "2607.13285", "title_cn": "Harness行为地图", "one_liner": "编排层可读可改：行为定位再编辑。", "link": "https://arxiv.org/abs/2607.13285", "ready_date": "20260726"},
            {"arxiv_id": "2607.21596", "title_cn": "可执行技能共演化", "one_liner": "推理期能力层另一条线：技能银行。", "link": "https://arxiv.org/abs/2607.21596", "ready_date": "20260727"},
        ],
    },
    "target_audience": [
        "做后训练/RLVR/多轮Agent训练的研究团队。",
        "维护多套推理编排（自洽/辩论/校验）的平台同学。",
        "担心『换脚手架就掉点』的产品与质量负责人。",
    ],
    "sales_use_cases": [
        "回应『我们只对CoT做了RL』：要求报held-out controller与shift成绩。",
        "方案评审：模块词表与controller清单进训练设计文档。",
        "对标沟通：用AMC上MIXED相对CoT的分档差距说明迁移价值。",
    ],
    "objection_handling": [
        "客户说：『多训几种提示就行。』→ 回应：单控会过拟合；文中Debate等本流程高、换流程塌。",
        "客户说：『自适应加权一定最好。』→ 回应：组合层可以，shift层MIXED更稳。",
    ],
    "copy_paste_lines": [
        "后训练别只适配一种流程，要让模型学会配合多种推理控制器。",
        "单controller容易过拟合；多controller训练提升工作流迁移。",
        "模型+编排才是系统，别假设换脚手架还能白嫖同一权重。",
    ],
    "key_quotes": [
        "Controller-Aware Language Models",
        "multi-task reinforcement learning over controller-induced interaction protocols",
        "improves generalization across inference-time workflows",
    ],
    "score_rationale": "CALM把inference-time controllers（CoT/自洽/辩论/规划/校验等）纳入后训练，按可复用local modules组合做多任务RL，并用turn-level GRPO训练。相对单controller过拟合，多controller训练在held-out组合与更大controller shift上迁移更好：GSM8K训练controller平均CALM-ADAPTIVE 73.72% vs 最强单控Step-back 71.11%；组合层ADAPTIVE 70.68%/MIXED 70.31%；AMC2023上MIXED三档平均20.00/26.25/23.75，显著高于CoT基线。Impact高：对准『模型+编排』系统。Novelty高：controller-aware多任务RL+模块分解。Evidence中高：GSM8K/MATH500/AMC分层评测。Applicability高：部署侧controller常变。Reusability中高：模块词表可迁，但训练成本、不稳定性与真实Agent harness覆盖仍开放。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "训练平均ADAPTIVE 73.72% vs Step-back 71.11%", "evidence": "Table 2 / §6.2", "location": "Table 2"},
            {"claim": "组合层ADAPTIVE 70.68%、MIXED 70.31%", "evidence": "§6.2 compositional discussion", "location": "§6.2"},
            {"claim": "shift层MIXED 75.69%；ADAPTIVE可能低于CoT", "evidence": "§6.2 controller-shift discussion", "location": "§6.2"},
            {"claim": "AMC2023 MIXED 20.00/26.25/23.75 vs CoT 16.25/18.75/22.50", "evidence": "Table 3 / §6.3", "location": "Table 3"},
            {"claim": "F段限制：小模型数学域、多轮不稳、harness外推", "evidence": "Limitations + ChatGPT notes", "location": "Limitations"},
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
        "重要性 Impact": "看问题是否卡在真实Agent/推理系统瓶颈，以及对验收看板是否有直接影响。",
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
        "2607.22602",
        "deeplook",
        DEEPLOOK_RICH,
        "推理别全程加预算：DeepLook只在置信度瓶颈做前瞻",
        "test-time scaling的关键不是一律加长，而是知道何时该多看几步。",
    )
    enrich_one(
        "2607.23771",
        "calm",
        CALM_RICH,
        "后训练别只适配一种流程：CALM让模型学会配合多种推理控制器",
        "未来模型不只是独立解题器，还要成为能配合多种推理编排的系统组件。",
    )
    print("enriched deeplook + calm")


if __name__ == "__main__":
    main()
