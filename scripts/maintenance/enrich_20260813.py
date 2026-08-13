#!/usr/bin/env python3
"""One-off enrichment for 20260813 paper-notes payloads (ReTree + Catastrophic Remembering)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260813"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


RETREE_RICH = {
    "intro_lead": "",
    "A_research_problem": "搜索Agent每多查一步，轨迹更长、噪声更多。滚动摘要能把上下文压住，可早期错误一旦写进摘要，后面的检索和结论会继续被污染。问题出在哪？改当前答案也修不掉已经长出来的下游依赖。",
    "B_core_contributions": [
        "把检索错误级联写成结构状态修复：有界上下文、claim到源溯源、依赖一致修订要一起满足",
        "证据树把压缩和回滚绑在同一套机制上：冲突确认后定位引入节点，重生摘要并剪掉受污染分支",
        "段落级源绑定在修订后仍可追溯；四公开搜索基准上对照扁平更新与报告压缩",
    ],
    "C_method_framework": "ReTree把搜索建模成证据树：节点存有界任务摘要、带稳定ID和URL的原子证据、以及修订历史。策略每步只看当前摘要加top-k相关证据，完整活跃路径留在树里。新证据先按同一实体/槽位/范围/时间做冲突检测，历史感知确认后再动刀：回溯到引入该事实的节点，替换证据与来源，重生该节点摘要，剪掉依赖子孙，从修复后的状态继续搜。",
    "D_key_results": [
        "Qwen3-8B、2149题：相对Full-Trajectory ReAct，judge准确率+8.3–25.6pp，总体44.0 vs 30.1（+13.9pp）",
        "Bamboogle 61.6 vs 36.0为最大涨幅；峰值策略上下文Full ReAct是ReTree的1.27–1.51×",
        "FRAMES 600题溯源：CitePrec/Rec 44.5/41.3，高于Full ReAct 37.7/27.1与ReportMemory 16.8/21.4",
    ],
    "E_industry_implications": [
        "Deep Research验收先问：结论被推翻时，依赖它的中间状态会不会一起失效",
        "记忆层要同时保留短上下文和可定位来源；只压字数会把错误锁进摘要",
        "上线前统计回滚触发率与误剪，不要只看终局准确率",
    ],
    "F_one_line_judgement": "这篇最适合做Deep Research / 长程搜索的团队：ReTree把搜索历史做成带溯源的证据树，新证据推翻旧claim时定位引入节点、重生摘要并剪掉受污染分支；四benchmark共2149题，相对Full-Trajectory ReAct judge准确率最高+25.6pp（总体44.0 vs 30.1），峰值推理上下文仅为其约2/3。不过硬剪枝把子孙一律当依赖，评测也主要是QA/search。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "ReTree", "definition": "Revision Tree：把搜索历史做成可修订证据树的工作记忆，而不是一份越写越长的轨迹。"},
        {"term": "Evidence tree", "definition": "节点存有界摘要、带源指针的原子证据和修订历史；边表示子状态由父节点的活跃证据派生。"},
        {"term": "Dependency-directed revision", "definition": "来自truth-maintenance：改一条依据时，依赖它的结论必须失效或按新证据重生。"},
        {"term": "FlatUpdate", "definition": "机制对照：共享摘要预算和冲突检测，但证据是扁平列表，冲突时只替换该条事实。"},
        {"term": "ReportMemory", "definition": "把检索折进一份有界报告并保留访问过的URL，丢掉事实级依赖谱系。"},
        {"term": "FRAMES / Bamboogle / 2Wiki / HotpotQA", "definition": "四个公开搜索/多跳QA基准；本文共2149题，Bamboogle与FRAMES用全集。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：压缩会把错误锁进摘要",
            "body": "完整轨迹让每步上下文随搜索轮次膨胀；滚动摘要能压长度，却常留下结论、丢掉是哪段原文撑起来的。后面证据改了前提，下游推理还在用旧值。",
        },
        {
            "title": "策略只看短上下文，树里留谱系",
            "body": "每步给模型的是当前摘要加top-5相关证据；完整活跃路径、源URL和修订史留在外部树。压缩发生在读侧，溯源发生在写侧。",
        },
        {
            "title": "冲突确认后，从引入点回滚",
            "body": "同一实体/槽位/范围/时间上的不相容取值才会立案，并用历史感知确认挡住来回翻转。确认后修引入节点、剪依赖子孙，再接着搜。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果（四基准）",
                "论文证据": "2149题，Qwen3-8B：ReTree 44.0 vs Full ReAct 30.1（+13.9pp）；区间+8.3–25.6pp。",
                "飞哥判断": "涨分来自可回滚的工作记忆，不是把历史全塞进上下文。",
            },
            {
                "看什么": "最大单集",
                "论文证据": "Bamboogle 61.6 vs 36.0（+25.6pp）；FRAMES 31.8 vs 15.8。",
                "飞哥判断": "组合缺口和事实查找上，早期错误级联更致命。",
            },
            {
                "看什么": "机制对照",
                "论文证据": "相对FlatUpdate每集+2.2–4.7pp；总体超ReportMemory 3.0pp（44.0 vs 40.9）。2Wiki上ReportMemory 50.8、ReTree 50.5，差0.3pp。",
                "飞哥判断": "只改一条事实不够；只写短报告也不够。结构修复才是增量。",
            },
            {
                "看什么": "上下文与溯源",
                "论文证据": "峰值上下文Full ReAct是ReTree的1.27–1.51×；FRAMES CitePrec/Rec 44.5/41.3 vs ReAct 37.7/27.1。回滚触发率9.6–17.5%。",
                "飞哥判断": "更短，同时更能指回段落。真实检索确实在触发修复。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 1 Qwen3-8B，n=2149；Bamboogle 61.6/36.0；Overall 44.0/30.1。",
        "对照：FlatUpdate / ReportMemory / Full ReAct；§5.5 +2.2–4.7pp 与 +3.0pp。",
        "溯源：Table 2 FRAMES 600题 CitePrec/Rec；Figure 3 逐步上下文；回滚9.6–17.5%。",
        "版本戳：arXiv:2608.10676v1 [cs.AI] 11 Aug 2026；ChatGPT 0812批次 #1。",
        "单位：Shanghai Jiao Tong University。",
    ],
    "so_what": "真正的瓶颈不在「还能不能塞进更多历史」，而在结论被推翻以后，依赖它的中间状态会不会一起失效。压缩管长度；provenance才管能不能安全改过去。",
    "feige_view": "对照0811 MemPrism、0812 TRACE：那边问「当前query该看哪类记忆 / 该修哪份上下文资产」；ReTree补的是第三问——已经写进状态的错，怎么按依赖回滚。Deep Research缺的往往是这层。",
    "limitations": [
        "硬剪枝把修订节点的全部子孙当依赖，部分下游事实其实仍成立，误剪会丢掉有用状态。",
        "冲突判定假阴性会留下污染，假阳性会过度修剪；同范围规则降低但不消灭这类错。",
        "评测是QA/search（最多8次检索），不是多工具、跨天开放工作流。",
        "相对FlatUpdate多7–11%模型调用、10–13% token；外部证据库随轮次变大。",
        "骨干是Qwen3-8B + 实时Google Search，网络方差下未报墙钟延迟。",
    ],
    "related_theme_picks": {
        "theme": "可修订的Agent记忆",
        "intro": "本篇讲搜索状态被推翻后怎么按依赖回滚；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.11095",
                "title_cn": "指令文件只增不减的灾难性记住",
                "one_liner": "同日配对：运行时能回滚，持久规则也要能安全删。",
                "link": "https://arxiv.org/abs/2608.11095",
                "ready_date": "20260813",
            },
            {
                "arxiv_id": "2608.06745",
                "title_cn": "任务条件关系视图重组记忆",
                "one_liner": "0811：当前query该看哪类记忆结构。",
                "link": "https://arxiv.org/abs/2608.06745",
                "ready_date": "20260811",
            },
            {
                "arxiv_id": "2608.09153",
                "title_cn": "从不满轨迹归因并修复上下文资产",
                "one_liner": "0812：坏了先查该改哪份prompt/KB/Skill。",
                "link": "https://arxiv.org/abs/2608.09153",
                "ready_date": "20260812",
            },
        ],
    },
    "target_audience": [
        "做Deep Research / 长程搜索Agent的研究工程团队。",
        "关心记忆压缩会不会把错误锁死的平台同学。",
        "评估「改答案却改不掉污染」事故的产品技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们做了滚动摘要』：问错误进入摘要后，下游状态怎么失效。",
        "方案评审：同时看准确率、峰值上下文、引用忠实度和回滚触发率。",
        "训练沟通：用Bamboogle +25.6pp说明结构修复比留全轨迹更值钱。",
    ],
    "objection_handling": [
        "客户说：『树形依赖太理想。』→ 回应：论文自己也写了硬剪枝过粗；先把provenance留下，再换成更细的依赖图。",
        "客户说：『多花了token。』→ 回应：相对扁平更新多10–13%，但峰值上下文比全轨迹短，且准确率更高。",
    ],
    "copy_paste_lines": [
        "压缩管长度，回滚管污染。",
        "ReTree：2149题总体44.0 vs 30.1，Bamboogle最高+25.6pp。",
        "结论被推翻时，依赖它的中间状态必须一起失效。",
    ],
    "key_quotes": [
        "improving answer accuracy by up to 25.6 percentage points",
        "the average maximum per-step reasoning context of Full-Trajectory ReAct is 1.27–1.51× that of ReTree",
        "memory is not merely a shorter transcript, but an editable state representation for provenance-aware repair",
    ],
    "info": {
        "title": "Self-Correcting Long-Horizon Search Agents via Tree-Structured Memory",
        "title_cn": "用证据树回滚被污染的搜索记忆",
        "link": "https://arxiv.org/abs/2608.10676",
        "authors": [
            "Aijun Yang",
            "Qianxue Guo",
            "Ziyi Huang",
            "Yuxuan Chen",
            "Shiyou Qian",
            "Jian Cao",
        ],
        "affiliations": ["Shanghai Jiao Tong University"],
    },
    "score": {
        "total": 9.1,
        "dimensions": [
            {"label": "重要性 Impact", "value": 1.9},
            {"label": "创新性 Novelty", "value": 1.8},
            {"label": "可验证性 Evidence", "value": 1.8},
            {"label": "产业可用性 Applicability", "value": 1.9},
            {"label": "可复用性 Reusability", "value": 1.7},
        ],
    },
    "score_rationale": "把长程搜索的记忆压缩与错误回滚合成一件事：证据树保留来源溯源，新证据推翻旧claim时定位引入节点、重生摘要并剪掉受污染分支。四benchmark共2149题，相对Full-Trajectory ReAct judge准确率+8.3–25.6pp（总体44.0 vs 30.1），峰值推理上下文仅为其1/1.27–1.51。机制消融把结构修复从扁平改写和报告压缩里拆开。局限是硬剪枝假设树形依赖、评测以QA/search为主。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "产业可用性 Applicability"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "直接打中长程搜索的运行时问题：错误一旦进摘要就会污染后续检索。"},
            {"label": "创新性 Novelty", "value": 1.8, "role": "middle", "rationale": "把TMS式依赖修订接到LLM搜索环，边语义是状态谱系而不是候选思维树。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "middle", "rationale": "四基准2149题、FlatUpdate/ReportMemory对照、FRAMES溯源和回滚触发率都在PDF里。"},
            {"label": "产业可用性 Applicability", "value": 1.9, "role": "highest", "rationale": "Deep Research已经在用滚动摘要；这篇给出可落地的回滚接口。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "硬剪枝过粗，评测停在QA/search，多工具开放工作流还要另验。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "相对Full ReAct judge准确率+8.3–25.6pp，总体44.0 vs 30.1", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "Bamboogle 61.6 vs 36.0（+25.6pp）", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "峰值上下文Full ReAct是ReTree的1.27–1.51×", "evidence": "Table 1 / Abstract", "location": "Table 1"},
            {"claim": "FRAMES CitePrec/Rec 44.5/41.3 vs ReAct 37.7/27.1", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "自然回滚触发率9.6–17.5%；相对FlatUpdate多7–11%调用、10–13% token", "evidence": "§5.5 / §6", "location": "§5.5"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260813 dual publish: ReTree + Catastrophic Remembering.",
        "Affiliations via overrides: Shanghai Jiao Tong University.",
        "Numbers verified from PDF Table 1–2, Figure 3, §5–6.",
    ],
}


CATAMEM_RICH = {
    "intro_lead": "",
    "A_research_problem": "CLAUDE.md、AGENTS.md、copilot-instructions.md 这类Agent指令文件，在真实仓库里往往只增不减。加一条规则永远便宜；当初为什么存在的rationale一丢，安全删除的代价随指令数指数上升。文件一直涨到整份重写，然后又开始涨。",
    "B_core_contributions": [
        "把灾难性记住写成形式：latent reasoning不可恢复时，即使任务不变，提示规模也会发散",
        "用247694条instruction lifetime的删除风险随年龄下降，排除单纯过时或内容脆弱作为主因",
        "倒置IFEval得到已知最优覆盖，证明带outcome的prompt comment能停住棘轮并买回instruction-following",
    ],
    "C_method_framework": "先在1867个公开仓追踪单条instruction的出生、存活和死亡，用删除风险随年龄、作者数的变化区分过时、脆弱与不完美回忆。再把IFEval反过来：隐藏最优指令集D⋆，只给维护者带噪声的约束反馈，比较手边有没有记录失败/假设/结果的prompt comment。最后把同一套倒置用到WildIFEval，看真实散文约束下，多余指令造成的跟随损失能不能被买回来。",
    "D_key_results": [
        "1867仓、247694条lifetime：生命周期平均+226%；排除整页重写后，19267次commit每笔净+4.9条；中位文件39条指令",
        "受控实验T=51：多余规模从+211.3%降到+1.4%（去掉99.3%）；T=15从+60.4%到-5.8%（66.2pp），约束满足率持平",
        "WildIFEval：50.4%升到62.0%（+11.6pp，相对+23.1%）",
    ],
    "E_industry_implications": [
        "给每条Agent规则写为什么存在，而不只写做什么；注释对执行器不可见",
        "删除权留人审：自动按注释清规则会误删仍有效的约束",
        "整页重写不是治理——重写后增长会更快回来",
    ],
    "F_one_line_judgement": "这篇最适合维护CLAUDE.md / AGENTS.md 的团队：作者把只增不减的指令膨胀命名为灾难性记住——加一条很便宜，rationale一丢就没人敢删。1867仓、247694条lifetime上平均+226%、每commit净+4.9条；带outcome的prompt comment砍掉99.3%多余规则，WildIFEval上最多相对+23.1%。不过证据主战场是公开GitHub上的coding instruction file，自动按注释删除并不安全。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Catastrophic remembering", "definition": "灾难性记住：持续Agent不敢删过时规则，与灾难性遗忘方向相反、机制同类——许可更新的依据丢了。"},
        {"term": "Latent reasoning", "definition": "写下这条指令时的失败、假设和结果；写时O(1)，事后重建约O(2^|D|)。"},
        {"term": "Prompt comment", "definition": "写给下一任维护者、对执行器不可见的注释；本文要求带outcome，空叙事或噪声注释不够。"},
        {"term": "IFEval inversion", "definition": "把基准指令藏成未知最优覆盖D⋆，维护者只看见目标摘要和约束反馈，从而能量多余规模。"},
        {"term": "WildIFEval", "definition": "真实请求上的instruction-following基准；本文用LLM judge打分，并做了第二judge复核。"},
        {"term": "Ratchet", "definition": "整页重写把文件砍短后，增长立刻恢复甚至更快，形成锯齿状膨胀。"},
    ],
    "method_subsections": [
        {
            "title": "观测：文件只在整页重写时变短",
            "body": "中位文件已经39条指令。64.3%的多版本仓在涨、26.6%在缩。77.3%的instruction死亡来自整页重写或迁到兄弟文件——删一条需要理由，删全部反而不需要。",
        },
        {
            "title": "机制：删除风险随年龄下降",
            "body": "若主因是过时，年龄越大越该删；数据相反，log-hazard每commit -0.032。多作者还会再压一截。这更像rationale丢失，而不是规则自然过期。",
        },
        {
            "title": "干预：注释里写下失败和结果",
            "body": "注释告诉下一任为什么加；执行器只看见指令本身。消融说明必须带outcome：评论形噪声几乎等于没写，只讲经过不讲结果是最差臂。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "真实仓库棘轮",
                "论文证据": "1867仓、247694条lifetime，平均+226%；排除整页重写后每commit净+4.9；中位39条。",
                "飞哥判断": "这不是个别仓库脏，是默认动力学。",
            },
            {
                "看什么": "删除为何越来越难",
                "论文证据": "log-hazard -0.032/commit（95% CI [-0.047,-0.019]）；77.3%死亡是重写或迁移。重写后10次commit回到预重写的91.5%。",
                "飞哥判断": "整页重写是泄压阀，不是治理。",
            },
            {
                "看什么": "受控实验",
                "论文证据": "T=51：+211.3% → +1.4%（99.3%多余被去掉），满足率持平；T=15：+60.4% → -5.8%。",
                "飞哥判断": "能记住为什么加，规模会停在最小覆盖附近。",
            },
            {
                "看什么": "真实跟随",
                "论文证据": "WildIFEval 50.4%→62.0%（+11.6pp，相对+23.1%）；16条噪声指令先让真约束掉24.1pp。",
                "飞哥判断": "多余规则有正确性税；注释把一部分税买回来。",
            },
        ],
    },
    "source_notes": [
        "观测：Abstract / Figure 1b / §3.1–3.3；247694 lifetime、1867仓、+226%、+4.9、中位39。",
        "风险：§3.4 log-hazard -0.032；§3.2 77.3%重写或迁移。",
        "实验：Table 2 T=15/51；§4.3 WildIFEval 50.4→62.0。",
        "版本戳：arXiv:2608.11095v1 [cs.AI] 11 Aug 2026；ChatGPT 0812批次 #4。",
        "单位：South Park Commons。",
    ],
    "so_what": "说白了，持续Agent的技术债往往不是模型忘了，是组织不敢删。许可删除的依据如果没写下来，context就会变成不可维护的遗留系统。",
    "feige_view": "近几期都在教Agent多记一点：Skill、记忆视图、问题账本。这篇把方向拧过来——没有rationale、provenance和垃圾回收，自我演化就是在堆遗留规则。写注释几乎零成本；自动按注释删除才危险。",
    "limitations": [
        "改写阈值50%、迁移规则、分词文法都未做扫描；matcher只在50条人工标注上验证。",
        "受控实验覆盖只有2–3条指令，对照中位文件的39条，15步视界，维护者与执行器还是同一模型。",
        "WildIFEval用LLM judge，第二judge效应量差未排除零，测量的是一致性而不是ground truth。",
        "语料是公开GitHub上的英文coding instruction file，不覆盖企业policy、记忆库或非英文规则。",
        "作者明确：写注释安全，按注释自动删除不安全，删除路径要留人。",
    ],
    "related_theme_picks": {
        "theme": "Agent上下文的技术债",
        "intro": "本篇讲持久指令为什么不敢删；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.10676",
                "title_cn": "用证据树回滚被污染的搜索记忆",
                "one_liner": "同日配对：运行时状态被推翻后怎么按依赖回滚。",
                "link": "https://arxiv.org/abs/2608.10676",
                "ready_date": "20260813",
            },
            {
                "arxiv_id": "2608.09153",
                "title_cn": "从不满轨迹归因并修复上下文资产",
                "one_liner": "0812：坏了先查该改哪份prompt/KB/Skill。",
                "link": "https://arxiv.org/abs/2608.09153",
                "ready_date": "20260812",
            },
            {
                "arxiv_id": "2608.05139",
                "title_cn": "Skill熵与技能选择",
                "one_liner": "0808：技能库变大后，怎么选才不熵增。",
                "link": "https://arxiv.org/abs/2608.05139",
                "ready_date": "20260808",
            },
        ],
    },
    "target_audience": [
        "维护CLAUDE.md / AGENTS.md / copilot-instructions.md 的工程团队。",
        "做self-evolving Agent、会不断往prompt打补丁的平台同学。",
        "担心规则只增不减变成遗留系统的技术负责人。",
    ],
    "sales_use_cases": [
        "回应『再加一条规则就好』：先问这条规则的rationale写在哪、谁有权删。",
        "方案评审：把指令生命周期、删除率和整页重写频率列入上下文治理指标。",
        "训练沟通：用+226%和99.3%说明「不敢忘」有数据，也有低成本干预。",
    ],
    "objection_handling": [
        "客户说：『注释也会过时。』→ 回应：过时的注释仍比空白好；空白让删除成本指数涨。自动删才危险。",
        "客户说：『我们整份重写过。』→ 回应：论文里重写后10次commit就回到91.5%，棘轮还在。",
    ],
    "copy_paste_lines": [
        "Agent不怕忘，怕不敢忘。",
        "1867仓平均+226%；带outcome的注释砍掉99.3%多余规则。",
        "加规则很便宜，删规则要先记得当初为什么加。",
    ],
    "key_quotes": [
        "catastrophic remembering, the inverse of catastrophic forgetting",
        "comments encoding latent reasoning remove 99.3% of excess instructions",
        "If English is the new code, why don't we have comments yet?",
    ],
    "info": {
        "title": "Why Does CLAUDE.md Keep Growing? Catastrophic Remembering in Agentic Coding",
        "title_cn": "指令文件只增不减的灾难性记住",
        "link": "https://arxiv.org/abs/2608.11095",
        "authors": ["Kushal Chakrabarti"],
        "affiliations": ["South Park Commons"],
    },
    "score": {
        "total": 8.9,
        "dimensions": [
            {"label": "重要性 Impact", "value": 1.9},
            {"label": "创新性 Novelty", "value": 1.8},
            {"label": "可验证性 Evidence", "value": 1.7},
            {"label": "产业可用性 Applicability", "value": 1.8},
            {"label": "可复用性 Reusability", "value": 1.7},
        ],
    },
    "score_rationale": "给持续Agent点名一个反向问题：不是忘了，是不敢忘。1867仓、247694条instruction lifetime上，agentic README生命周期平均+226%、每commit净+4.9条，删除风险随年龄下降。受控实验里带outcome的prompt comment砍掉99.3%多余规则；WildIFEval上instruction-following最多相对+23.1%。Evidence因WildIFEval用LLM judge、改写阈值未扫而略扣；适用范围主要是coding instruction file。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact"],
        "lowest_dimensions": ["可验证性 Evidence", "可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "把每个用CLAUDE.md的人都能感到的棘轮写成可测量机制。"},
            {"label": "创新性 Novelty", "value": 1.8, "role": "middle", "rationale": "灾难性记住这个命名，加上IFEval倒置，让「最小覆盖」第一次可测。"},
            {"label": "可验证性 Evidence", "value": 1.7, "role": "lowest", "rationale": "仓库观测很强；WildIFEval靠LLM judge，改写阈值也未扫描。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "写注释当天就能做；自动删除需要人审，作者自己也警告了。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "范围停在公开GitHub的英文coding instruction file，企业policy还要另验。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "1867仓、247694条lifetime，生命周期平均+226%", "evidence": "Figure 1b / Abstract", "location": "Figure 1b"},
            {"claim": "排除整页重写后每commit净+4.9条；中位文件39条", "evidence": "§3.1", "location": "§3.1"},
            {"claim": "T=51多余规模+211.3%→+1.4%，去掉99.3%", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "WildIFEval 50.4%→62.0%（+11.6pp，相对+23.1%）", "evidence": "§4.3", "location": "§4.3"},
            {"claim": "删除log-hazard -0.032/commit；77.3%死亡来自重写或迁移", "evidence": "§3.2 / §3.4", "location": "§3.4"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260813 dual publish: ReTree + Catastrophic Remembering.",
        "Affiliations via overrides: South Park Commons.",
        "Numbers verified from PDF Figure 1, Table 2, §3–4, Limitations.",
        "score_rationale 含「不是忘了，是不敢忘」属评分说明，正文So What已改成「往往不是模型忘了，是组织不敢删」以免对称句式堆叠。",
    ],
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
        "2608.10676",
        "retree",
        RETREE_RICH,
        "别只压缩记忆：证据树可回滚，搜索准确率最高+25.6个百分点",
        "长程搜索Agent接下来要比的，是结论被推翻后依赖状态能不能安全回滚。",
    )
    enrich_one(
        "2608.11095",
        "catamem",
        CATAMEM_RICH,
        "CLAUDE.md为什么只增不减：缺rationale就不敢删，平均涨226%",
        "Agent不怕忘，怕不敢忘；规则要能删，先把当初为什么加上写下来。",
    )
    print("enriched retree + catamem")


if __name__ == "__main__":
    main()
