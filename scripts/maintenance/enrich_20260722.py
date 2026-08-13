#!/usr/bin/env python3
"""One-off enrichment for 20260722 paper-notes payloads (RECON + AgentBrew)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260722"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


RECON_RICH = {
    "A_research_problem": "现有记忆基准多问两件事：散落事实找不找得到、变更检不检测得到。真实工作流里事实会互相依赖——一条证据被否定后，哪些下游结论必须撤销、哪些因独立支撑而存活？长上下文、RAG与记忆Agent常把失败统一归因于窗口不够，却分不清是检索层还是推理层崩了。",
    "B_core_contributions": [
        "把Agent Memory评测从状态跟踪推进到组合推理：变更后的依赖追踪与撤销",
        "确定性provenance生成管线：显式失效与反事实，答案由代码派生而非LLM标注",
        "跨架构实证：long-context / RAG / memory agents同台，分离检索与推理瓶颈",
    ],
    "C_method_framework": "RECON（Reasoning over Extended Contexts with Obfuscated Narratives）用确定性六层生成器构造带provenance图的案例：24个刑事/医疗/金融案卷，每案50k–100k token，共1604题。六任务覆盖多跳证据链重建、级联失效传播、来源冲突裁决、反事实时间线、时间约束满足、时间事实检索。评测族包括直接塞全文的long-context、四类RAG变体、Mem0/Mem0-Graph/Supermemory/Hindsight等记忆Agent，以及拿到结构化真相图的Oracle上限。",
    "D_key_results": [
        "最强非Oracle Accuracy仅22.4%（Gemini-2.5-Pro）；最强非Oracle Score 0.287（GPT-5.1）",
        "Oracle拿到结构化真相图也仅54.6% Accuracy / Score 0.654——任务难，不只是检索",
        "24案例/1604题；人标κ=0.69（200题）；先验可猜题已剔除11.8%",
    ],
    "E_industry_implications": [
        "上线记忆层前先压测『证据失效→下游撤销』，别只测召回率",
        "把失败拆成检索失败 vs 推理失败，避免一律加窗口或加向量库",
        "高风险域（医疗/金融/合规）要把级联失效当作一等验收项",
    ],
    "F_one_line_judgement": "RECON把Agent记忆从『找事实』改成『事实失效后的级联推理』——24个5万–10万token案例上，最强非Oracle准确率只有22.4%，连Oracle也才54.6%。",
    "glossary": [
        {"term": "RECON", "definition": "Reasoning over Extended Contexts with Obfuscated Narratives：评测长上下文上的组合记忆推理，而非静态事实检索。"},
        {"term": "Cascade Propagation / 级联失效", "definition": "一条证据被否定后，追踪哪些下游结论必须撤销、哪些因独立支撑而存活。"},
        {"term": "Provenance graph", "definition": "案例生成时维护的证据依赖图；支撑确定性出题与答案派生。"},
        {"term": "Oracle", "definition": "直接读取结构化真相图而非叙述案卷的上界系统；用来分离『读不懂长文』与『推理本身难』。"},
        {"term": "组合推理（compositional reasoning）", "definition": "结论依赖多条证据及其交互；变更一处会改变依赖闭包。"},
        {"term": "Abstain%", "definition": "系统选择拒答的比例；与Accuracy一起报告，避免只会瞎猜。"},
    ],
    "method_subsections": [
        {
            "title": "六任务：记忆要过的不只是找针",
            "body": "链重建要求跨文档拼5–15跳因果序；级联失效考察依赖闭包；来源冲突要求用独立旁证裁决；反事实问替代时间线；时间约束对齐并行数据流；时间检索作控制基线。",
        },
        {
            "title": "确定性生成：答案不靠LLM标",
            "body": "六层生成器先建provenance与失效/反事实结构，再渲染成叙事案卷。结构与时间一致性校验（0循环依赖、时间单调），压力测试能抓出注入的时间戳倒置。",
        },
        {
            "title": "同台评测：拆检索与推理",
            "body": "long-context吃满案卷、RAG压缩到约7K–9K token、记忆Agent外挂索引、Oracle直接吃真相图。对比能看出压缩伤害级联任务、RAG在时间事实检索上更强等结构差异。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "非Oracle上限",
                "论文证据": "最强Accuracy 22.4%（Gemini-2.5-Pro）；最强Score 0.287（GPT-5.1）；无一系统超25% Accuracy。",
                "飞哥判断": "这不是『再加一点上下文就好』的问题，是能力断层。",
            },
            {
                "看什么": "Oracle天花板",
                "论文证据": "Oracle Score 0.654 / Accuracy 54.6%；反事实等任务上绝对分仍低。",
                "飞哥判断": "即便跳过叙述噪声，组合推理本身也硬——产品别假装『检索对了就完事』。",
            },
            {
                "看什么": "数据与人标",
                "论文证据": "24案卷、1604题、50k–100k token；200题人标κ=0.69；剔除11.8%先验可猜题。",
                "飞哥判断": "规模不算巨大，但生成管线与人标让分数可信；扩案例多样性是下一刀。",
            },
            {
                "看什么": "架构对照",
                "论文证据": "RAG在时间事实检索领先，但级联任务上被压缩伤害；记忆Agent与long-context各有短板。",
                "飞哥判断": "选型要用任务剖面，而不是统一『谁窗口大谁赢』。",
            },
        ],
    },
    "source_notes": [
        "主结果：非Oracle 22.4% Accuracy / Oracle 54.6%；见评测总表与正文分析段。",
        "投稿时间：2026-07-18 09:11 UTC；ChatGPT 0722 #1（9.3口径）；cs.AI。",
        "单位：RV College of Engineering（PDF首页）。",
        "代码/数据：anonymous.4open.science/r/RECON-Bench（匿名评审链接）。",
        "证据边界：仅24案例；结果耦合具体检索组件与模型；Oracle也未接近满分。",
    ],
    "so_what": "说白了，给Agent更长上下文，不等于它知道『哪条记忆还可信』。RECON逼你测变更之后的依赖闭包：证据改了，下游结论该不该撤。22.4%的非Oracle上限，是在提醒产品团队——记忆层验收别停在召回率。",
    "feige_view": "三个动作：①给记忆系统加『失效演练』回归集：故意翻一条关键事实，看哪些结论跟着变；②故障分析表拆检索失败/推理失败两栏，禁止一律『加窗口』；③高风险工作流把级联失效写进上线门禁，和幻觉率并列。",
    "limitations": [
        "不过，只有24个案例，叙事模板与任务结构的多样性仍有限，外推到开放企业知识库要打折。",
        "不过，22.4%同时受检索组件与答题模型选择影响，不能直接当成某一种记忆产品的绝对能力分。",
        "不过，Oracle也仅约55%准确率，说明基准难度高；解读时要同时看相对排序与绝对水平，避免过度唱衰或过度吹捧单一系统。",
    ],
    "related_theme_picks": {
        "theme": "Agent记忆与长上下文",
        "intro": "本篇负责『测缺口』；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.16851", "title_cn": "强教师经验酿成弱Agent外存", "one_liner": "缺口之外的补法：把失败经验认证成可执行笔记，而不是只加窗口。", "link": "https://arxiv.org/abs/2607.16851", "ready_date": "20260722"},
            {"arxiv_id": "2607.14952", "title_cn": "LongStraw长上下文RL执行栈", "one_liner": "另一条轴：固定GPU预算把长上下文RL推到2M+。", "link": "https://arxiv.org/abs/2607.14952", "ready_date": "20260721"},
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "系统层可观测性：把执行状态外化，和记忆依赖追踪同一类工程思维。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
        ],
    },
    "target_audience": [
        "做企业Agent记忆层、RAG与长文档工作流的产品/工程负责人。",
        "需要给记忆系统定验收标准的评测与质量团队。",
        "研究Agent memory / long-context reasoning的研究者。",
    ],
    "sales_use_cases": [
        "回应『我们已经上了百万token窗口』：用22.4%说明窗口≠组合记忆能力。",
        "高风险域售前：把级联失效演练包装成记忆层POC验收项。",
        "架构评审：用检索vs推理分栏，推动别只堆向量库。",
    ],
    "objection_handling": [
        "客户说：『24个案例太少。』→ 回应：同意要扩；但确定性生成+人标κ与跨架构同台已经足够暴露断层，先用来定验收，再扩域。",
        "客户说：『Oracle也才55%，是不是题出太难？』→ 回应：难是设计目标；产品应同时看相对排序——今天非Oracle连1/4都过不了。",
    ],
    "copy_paste_lines": [
        "记忆评测别停在找事实，要测证据失效后的级联撤销。",
        "最强非Oracle准确率22.4%：窗口不是唯一瓶颈。",
        "失败要拆检索层与推理层，不能一律加上下文。",
    ],
    "key_quotes": [
        "even the strongest non-Oracle system reaches only 22.4% Accuracy",
        "RECON evaluates what happens after the change",
        "retrieval and reasoning each surfacing as challenges",
    ],
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "最强非Oracle Accuracy 22.4%（Gemini-2.5-Pro）", "evidence": "Main evaluation table / text", "location": "Section Evaluation / Table"},
            {"claim": "Oracle Accuracy 54.6% / Score 0.654", "evidence": "Oracle row in main results", "location": "Section Evaluation"},
            {"claim": "24案例、1604题、50k–100k token；κ=0.69", "evidence": "Benchmark construction + human validation", "location": "Section Benchmark / Validation"},
            {"claim": "F段限制：案例规模与组件耦合", "evidence": "Limitations / discussion", "location": "Limitations"},
        ]
    },
}


AGENTBREW_RICH = {
    "A_research_problem": "生产上服务端往往只能跑小模型或冻结权重的API模型，训练期却请得到更强教师。如何把教师交互经验沉淀成弱学生真正执行得动的外部记忆？环境通常只有稀疏二值反馈；教师若按自己粒度写笔记，弱模型读得懂也用不了。",
    "B_core_contributions": [
        "training-free brew–serve：稀疏二值反馈下为固定弱Agent终身攒外存",
        "student-aware合成 + Ralph环境认证：知识必须对学生可执行，而非教师自洽",
        "代码/数学/工具用六基准对照：相对ACE/ExpeL/Simple RAG与Reflexion协议清晰",
    ],
    "C_method_framework": "AgentBrew分brew与serve。Brew：学生失败触发教师写结构化笔记（trigger、corrective_rule、minimal_steps等）；Ralph Loop把候选笔记塞回学生重跑，环境recovery才入库；student-aware prompting把规则压到弱模型操作粒度；curator只做去重与质量门。Serve：记忆只读、教师离线，学生按技能范围检索top-k笔记后单次rollout。默认教师DeepSeek-Chat-v3.1、学生Qwen3-14B。",
    "D_key_results": [
        "Table1：AgentBrew MATH 75.96* / GSM8K 88.17* / MBPP 61.22 / MBPP+ 71.43* / AppWorld Normal 31.55* / Challenge 15.35*",
        "单次rollout仍匹配或超过Reflexion(k=2)在代码与工具用（如MBPP 61.22 vs 54.22）",
        "消融：去Ralph或用强学生代写笔记，MATH/GSM8K下降；说明认证与学生校准都必要",
    ],
    "E_industry_implications": [
        "部署配方：强模型离线攒经验，小模型线上跑；别默认先上持续微调",
        "外存笔记要对学生模型做可执行化验收，教师反思原文不能直接当技能库",
        "用环境recovery当质量门，比只靠curator文本审核更稳",
    ],
    "F_one_line_judgement": "AgentBrew证明：强模型负责离线把失败酿成对学生可执行的笔记，廉价模型负责长期跑——无需改权重、无需测试期教师。",
    "glossary": [
        {"term": "AgentBrew / brewing", "definition": "离线把教师知识蒸馏进持久外存、并在目标学生上验证的过程；测试期不再调用教师。"},
        {"term": "Ralph Loop", "definition": "把候选笔记注入学生并重跑同一任务；环境成功才认证入库的验证环。"},
        {"term": "student-aware synthesis", "definition": "按弱执行器的阅读与操作粒度写笔记，而不是按教师舒适区写。"},
        {"term": "brew–serve", "definition": "训练流可写记忆、测试流只读记忆的两阶段协议。"},
        {"term": "ExpeL / ACE / Simple RAG", "definition": "同属教师增强外存基线：保存轨迹或经验，但不强调对学生可执行化与环境认证。"},
        {"term": "UpSkill", "definition": "作者开源代码仓（github.com/HKUDS/UpSkill）。"},
    ],
    "method_subsections": [
        {
            "title": "失败才请教师：把二值反馈变成监督事件",
            "body": "学生先rollout；成功则跳过教师。失败时教师只看任务与失败轨迹写结构化笔记，不接触参考答案——这让只有pass/fail的环境也能学。",
        },
        {
            "title": "Ralph认证：看起来对 ≠ 学生能用",
            "body": "候选笔记必须帮弱学生在同一任务上recovery。消融显示去Ralph后GSM8K掉到84.61（全文88.17），且更多笔记被curator拒掉——环境侧预过滤比纯文本审核更有效。",
        },
        {
            "title": "笔记要对学生校准",
            "body": "Figure1与消融『强学生代写』都显示：笔记好坏取决于酿造时的学生，而不只是教师有多强。知识不是通用的，要贴执行器。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果（Table1）",
                "论文证据": "MATH 75.96*、GSM8K 88.17*、MBPP+ 71.43*、AppWorld Normal 31.55* / Challenge 15.35*；多处显著优于同组最强基线。",
                "飞哥判断": "Group III里最干净的故事：同一单次rollout协议下，学生校准+环境认证打得过ACE/ExpeL/RAG。",
            },
            {
                "看什么": "vs Reflexion",
                "论文证据": "尽管Reflexion(k=2)有测试期多轮反馈，AgentBrew单次仍在MBPP 61.22 vs 54.22、AppWorld上不落下风；Reflexion优势集中在数学。",
                "飞哥判断": "线上若舍不得多轮试错，外存笔记是更便宜的稳定性来源。",
            },
            {
                "看什么": "消融（Table2）",
                "论文证据": "w/o Ralph：GSM8K 84.61；w/ Strong Student Knowledge：MATH 74.92 / GSM8K 85.52；全文75.96 / 88.17。",
                "飞哥判断": "两处都别省：不认证会装进假笔记；不对着弱学生写会迁移失效。",
            },
            {
                "看什么": "开源与设定",
                "论文证据": "港大；GitHub HKUDS/UpSkill；教师DeepSeek-Chat-v3.1、学生Qwen3-14B。",
                "飞哥判断": "配方可直接拿去试点：先定学生模型，再开酿造流水线。",
            },
        ],
    },
    "source_notes": [
        "主结果：Table 1；消融 Table 2；Ralph训练统计 Table 3。",
        "投稿时间：2026-07-18 15:23 UTC；ChatGPT 0722 #2（9.0口径）；cs.AI。",
        "单位：The University of Hong Kong（PDF首页）。",
        "开源：https://github.com/HKUDS/UpSkill",
        "证据边界：默认师生模型对固定；外存膨胀与跨环境/跨学生迁移未充分验证；数学上Reflexion多轮仍可能更强。",
    ],
    "so_what": "说白了，弱Agent要变强，不一定先微调。AgentBrew给了一条更轻的路：强模型离线把失败酿成『对学生可执行』的笔记，环境认证后再给小模型单次调用。贵的算力花在酿造，便宜的算力花在服务。",
    "feige_view": "三个动作：①选定线上学生模型后再开酿造，禁止用强模型自嗨笔记直接上线；②每条外存技能必须过recovery门禁，文本好看不算数；③监控记忆体积与检索命中，提前做去重/降权，别让外存无限膨胀。",
    "limitations": [
        "不过，外部记忆可能持续膨胀；长期需要更强的去重、降权与遗忘策略，论文对此着墨有限。",
        "不过，教师经验能否跨环境、跨学生模型迁移仍不明确——换学生往往需要重新酿造。",
        "不过，数学场景下多轮Reflexion仍可能更高；若产品允许测试期反复试错，外存不是唯一解。",
    ],
    "related_theme_picks": {
        "theme": "Agent自我改进与外存",
        "intro": "本篇讲『如何沉淀可执行经验』；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.16716", "title_cn": "记忆失效后的组合推理评测", "one_liner": "先测缺口：变更后的级联推理，最强非Oracle仅22.4%。", "link": "https://arxiv.org/abs/2607.16716", "ready_date": "20260722"},
            {"arxiv_id": "2607.16122", "title_cn": "评测诊断到定向微调", "one_liner": "另一条改进接口：把rubric弱能力变成数据工单（改权重路线）。", "link": "https://arxiv.org/abs/2607.16122", "ready_date": "20260721"},
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "系统层配套：外化执行状态，减少经验沉淀时的盲区。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
        ],
    },
    "target_audience": [
        "要在固定小模型/API模型上提升Agent成功率的工程负责人。",
        "规划『强模型离线、弱模型在线』算力分工的平台团队。",
        "研究Agent memory / distillation / self-evolution的研究者。",
    ],
    "sales_use_cases": [
        "回应『小模型不够聪明只能换大模型』：用brew–serve说明可先外挂认证经验。",
        "成本评审：把教师调用关在离线酿造，线上保持单次rollout。",
        "质量门设计：用环境recovery替代纯人工审笔记。",
    ],
    "objection_handling": [
        "客户说：『这不就是RAG吗？』→ 回应：存的不是教师成功轨迹原文，而是对学生校准、环境认证过的结构化规则；消融证明学生校准不可省。",
        "客户说：『我们会微调。』→ 回应：可以并行；但在权重冻结或API-only场景，外存是唯一能终身累积的旋钮。",
    ],
    "copy_paste_lines": [
        "知识不是通用的：要酿给具体学生模型。",
        "强模型离线攒经验，弱模型线上跑——别默认先微调。",
        "笔记好看不算数，环境recovery才算数。",
    ],
    "key_quotes": [
        "knowledge is not universal—it must fit the agent that executes it",
        "no weight updates, expert demonstrations, ground-truth labels, or test-time teacher access",
        "student-aware synthesis calibrates teacher knowledge to the weak executor",
    ],
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "Table1主结果 MATH 75.96* / GSM8K 88.17* 等", "evidence": "Table 1 main results", "location": "Table 1 / Section 3.2"},
            {"claim": "单次rollout vs Reflexion(k=2) 代码/工具用对比", "evidence": "Table 1 Group II vs III discussion", "location": "Section 3.2"},
            {"claim": "消融：Ralph与学生校准必要", "evidence": "Table 2 ablation", "location": "Table 2 / Section 3.3"},
            {"claim": "F段限制：记忆膨胀与跨学生迁移", "evidence": "Discussion / limitations cues in intro+conclusion", "location": "Discussion"},
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
        "重要性 Impact": "看问题是否卡在真实Agent记忆/部署痛点，以及结论对验收与架构是否有直接影响。",
        "创新性 Novelty": "看方法或评测接口是否有辨识度：是新的问题定义/协议，还是已知模块的常规堆叠。",
        "可验证性 Evidence": "看对照是否干净、数字是否可追溯，以及案例规模/模型选择带来的外推折扣。",
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
        "2607.16716",
        "recon",
        RECON_RICH,
        "Agent记忆别再只测找事实：证据改了以后，下游结论该不该撤销",
        "最强非Oracle准确率只有22.4%：长上下文Agent的瓶颈不只是窗口，而是记忆上的组合推理。",
    )
    enrich_one(
        "2607.16851",
        "agentbrew",
        AGENTBREW_RICH,
        "别急着微调弱Agent：把强模型失败经验酿成可执行外存",
        "AgentBrew用training-free brew–serve：强教师离线认证笔记，弱学生单次rollout调用——MATH 75.96%、GSM8K 88.17%，代码与工具用也领先同组外存基线。",
    )
    print("enriched both")


if __name__ == "__main__":
    main()
