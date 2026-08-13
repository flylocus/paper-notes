#!/usr/bin/env python3
"""One-off enrichment for 20260812 paper-notes payloads (Reason Wide + TRACE)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260812"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


REASONWIDE_RICH = {
    "intro_lead": "",
    "A_research_problem": "Reasoning模式在多步Agent任务上更强，但每集都付3–6×输出token溢价。读trace会发现：很多 deliberation 不是实例特异解题，而是反复重推同一领域程序。如何把这笔溢价摊销掉？",
    "B_core_contributions": [
        "提出wide vs deep：跨episode蒸馏摊销test-time reasoning溢价",
        "四Agent benchmark：Skill恢复大部分reasoning gap并大幅降token",
        "证明不必依赖昂贵reasoning traces：仅从non-thinking轨迹蒸馏也具竞争力",
    ],
    "C_method_framework": "被动Skill蒸馏三步：在训练split收集既有轨迹→用coding agent做一次宽搜索式反思，编译40–130行可追溯自然语言Skill→原样注入非reasoning模型的system prompt。不改harness、解码与工具；Skill是可缓存前缀。",
    "D_key_results": [
        "GPT-5.4-mini：ALFWorld no-think+skill 0.787 vs think 0.713（token 832 vs 3723，约4.5×）",
        "四benchmark恢复55%–100%+ reasoning gap；retail 0.408也超过think 0.350",
        "相对GEPA：retail/telecom更高分，且生产Skill成本约1.28–2.44美元，比GEPA便宜约4.1×",
    ],
    "E_industry_implications": [
        "部署前区分：哪些推理是领域程序、可编译进Skill；哪些是实例特异、必须保留reasoning",
        "把历史评测轨迹当成资产：一次蒸馏、多次复用，比每请求开thinking更划算",
        "Skill要进版本与过期治理：环境规则一变，自然语言程序也可能失效",
    ],
    "F_one_line_judgement": "这篇最适合做Agent成本与推理效率的团队：从历史轨迹蒸馏自然语言Skill注入非reasoning模型，GPT-5.4-mini在四benchmark恢复55%–100%+ reasoning gap，ALFWorld 0.787甚至超过think的0.713，token降2.9–4.5×；不过telecom与SpreadsheetBench仍有剩余深搜索缺口，Skill也会随环境规则过期。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Reason Wide, Not Deep", "definition": "主张用跨episode宽搜索蒸馏Skill，摊销单集deep reasoning溢价。"},
        {"term": "Reasoning premium", "definition": "开启thinking模式相对no-think多付的输出token成本（论文约3–6×）。"},
        {"term": "Passive skill distillation", "definition": "对既有轨迹语料做一次外部coding-agent反思，编译可注入system prompt的自然语言Skill。"},
        {"term": "Wide search / Deep search", "definition": "宽搜索=跨多集语料一次付费；深搜索=单集内实时推理，每次部署重付。"},
        {"term": "τ²-bench", "definition": "双控客户服务Agent基准，本文用telecom与retail两域。"},
        {"term": "GEPA", "definition": "reflective prompt evolver基线；本文Skill在两域更高分且生产成本更低。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：同一程序被反复现算",
            "body": "零售Agent每次重新想「先确认邮箱再查账号」；家务Agent反复重发现「heat是原子命令」。这些不是实例特异深搜，却占了thinking账单。",
        },
        {
            "title": "一次宽搜索，永久复用",
            "body": "coding agent对比成败轨迹与失败模式频率，写出可追溯规则。蒸馏是一次性成本；部署只加缓存前缀，不再生成reasoning tokens。",
        },
        {
            "title": "不必先有昂贵traces",
            "body": "主结果Skill来自no-think轨迹。paired think语料在某些域更好，但no-think-only已能恢复大部分gap——这对只剩廉价评测日志的团队更现实。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果（ALFWorld）",
                "论文证据": "no-think+skill 0.787 vs think 0.713；token 832 vs 3723（约4.5×）。",
                "飞哥判断": "Skill甚至反超thinking：聚合50集规则可比单次现推更稳。",
            },
            {
                "看什么": "四域摊销",
                "论文证据": "恢复55%–100%+ gap；retail 0.408>think 0.350；telecom仍有剩余gap。",
                "飞哥判断": "程序型域吃满摊销；长依赖/实例逻辑域仍要保留深搜。",
            },
            {
                "看什么": "成本对照",
                "论文证据": "相对think降2.9–4.5×输出token；蒸馏成本约1.28–2.44美元/域。",
                "飞哥判断": "相对每请求溢价，一次蒸馏几乎免费。",
            },
            {
                "看什么": "vs GEPA",
                "论文证据": "retail/telecom分更高；生产成本约便宜4.1×。",
                "飞哥判断": "不是又一轮prompt进化搜索，而是对既有轨迹的一次编译。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 1 GPT-5.4-mini ALFWorld 0.787/0.713（832/3723）；retail 0.408/0.350；§5.1恢复55%–100%+ gap。",
        "对照：Table 3 vs GEPA；蒸馏成本$1.28–$2.44；Table 2蒸馏源消融。",
        "版本戳：arXiv:2608.07885v1 [cs.AI]；ChatGPT 0811批次 #1 + Grok双源交叉。",
        "单位：Microsoft。",
        "证据覆盖：四Agent基准×两模型；telecom/SSB剩余gap与Skill过期需治理。",
    ],
    "so_what": "说白了，先把Agent推理账单拆开：哪些是领域程序，哪些是这单才要的深搜。前者编译进Skill；后者才值得开thinking。",
    "feige_view": "对照近几期SkillHEX / AMD / SkillSmith：能力不一定要塞进weights。Reason Wide把问题说得更尖——很多reasoning其实是在重新发现本该缓存的程序。",
    "limitations": [
        "telecom与SpreadsheetBench仍有剩余reasoning gap，实例特异深搜不能被固定Skill完全替代。",
        "自然语言Skill会随环境规则、工具schema更新而过期。",
        "蒸馏依赖训练split轨迹质量；域迁移需重新编译。",
        "主实验是workshop论文规模；更复杂企业工具链外推仍需验证。",
    ],
    "related_theme_picks": {
        "theme": "Skill层摊销与推理成本",
        "intro": "本篇讲把重复reasoning编译成Skill；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.09153",
                "title_cn": "从不满轨迹归因并修复上下文资产",
                "one_liner": "同日配对：Skill写错了，要能从不满轨迹自动修。",
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
            {
                "arxiv_id": "2608.05628",
                "title_cn": "假设驱动技能自进化",
                "one_liner": "0809：技能侧别一路贪心改，先做可证伪实验。",
                "link": "https://arxiv.org/abs/2608.05628",
                "ready_date": "20260809",
            },
        ],
    },
    "target_audience": [
        "做Agent推理成本与serving预算的研究工程团队。",
        "关心何时开thinking、何时靠Skill的平台同学。",
        "评估「同一领域反复烧token」事故的产品技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们默认全开reasoning』：先问重复程序有没有外化成Skill。",
        "方案评审：要求同时看成功率、输出token与reasoning token，而不是只看分数。",
        "训练沟通：用ALFWorld 0.787>0.713说明摊销可以反超现算。",
    ],
    "objection_handling": [
        "客户说：『thinking越强越好。』→ 回应：强在实例深搜；领域程序被反复现算是浪费。",
        "客户说：『Skill会过期。』→ 回应：正因为会过期，才要版本与重蒸馏，而不是永远付每请求溢价。",
    ],
    "copy_paste_lines": [
        "别再每题重想一遍。",
        "Reason Wide：ALFWorld 0.787反超thinking，token约降4.5×。",
        "先问能不能摊销，再问要不要开thinking。",
    ],
    "key_quotes": [
        "skills recover 55%–100%+ of the reasoning gap",
        "exceeding the reasoning mode outright on ALFWorld (0.787 vs. 0.713)",
        "test-time reasoning is deep search inside a single episode... corpus distillation is wide search across episodes",
    ],
    "info": {
        "title": "Reason Wide, Not Deep: Amortizing the Reasoning Premium into Distilled Skills",
        "title_cn": "把推理溢价摊销成可复用Skill",
        "link": "https://arxiv.org/abs/2608.07885",
        "authors": [
            "Agamdeep Singh",
            "Srishti Gautam",
            "Priyanshu Gupta",
            "Nikita Mehrotra",
            "Tanmay Bakshi",
            "Sumit Gulwani",
        ],
        "affiliations": ["Microsoft"],
    },
    "score": {
        "total": 9.2,
        "dimensions": [
            {"label": "重要性 Impact", "value": 1.9},
            {"label": "创新性 Novelty", "value": 1.9},
            {"label": "可验证性 Evidence", "value": 1.8},
            {"label": "产业可用性 Applicability", "value": 1.9},
            {"label": "可复用性 Reusability", "value": 1.7},
        ],
    },
    "score_rationale": "把重复出现的Agent程序性知识从单次test-time reasoning摊销为可缓存Skill：四benchmark上GPT-5.4-mini恢复55%–100%+ reasoning gap，ALFWorld/retail甚至超过think模式，输出token降2.9–4.5×且零reasoning token。wide vs deep框架清晰；蒸馏可不依赖昂贵reasoning traces。telecom/SSB剩余gap与Skill过期使Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty", "产业可用性 Applicability"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "直接打中Agent推理账单：重复程序被每请求现算。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "wide vs deep把摊销说成可操作框架，而不只是又一个prompt技巧。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "middle", "rationale": "四基准、两模型、蒸馏源消融与GEPA对照齐全；workshop规模外推仍有限。"},
            {"label": "产业可用性 Applicability", "value": 1.9, "role": "highest", "rationale": "落地路径极短：蒸馏一次、注入system prompt即可。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "Skill随环境过期；telecom/SSB剩余深搜缺口限制一刀切。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "ALFWorld no-think+skill 0.787 vs think 0.713，token 832 vs 3723", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "四benchmark恢复55%–100%+ reasoning gap", "evidence": "§5.1 / Abstract", "location": "§5.1"},
            {"claim": "retail 0.408超过think 0.350", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "相对think输出token降2.9–4.5×", "evidence": "Table 1 Token Reduction", "location": "Table 1"},
            {"claim": "相对GEPA生产成本约便宜4.1×，retail/telecom分更高", "evidence": "Table 3 / §5.3", "location": "Table 3"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260812 dual publish: Reason Wide + TRACE.",
        "Affiliations via overrides: Microsoft.",
        "Numbers verified from PDF Table 1–3 and §5.",
    ],
}


TRACE_RICH = {
    "intro_lead": "",
    "A_research_problem": "生产Agent失败常不在模型权重，而在system prompt、知识库、工具描述或程序性Skill的错误与缺口。交互量上升后，人工翻日志无法规模化定位该改哪一份上下文资产。",
    "B_core_contributions": [
        "把轨迹挖掘用于context layer维护，而不只做模型微调",
        "多组件因果归因：从单体prompt优化扩展到skill/KB/tool/prompt",
        "探索式验证区分CREATE vs UPDATE，并给出可复用仿真评测方法论",
    ],
    "C_method_framework": "TRACE把轨迹建成上下文图，跑检测→根因→推荐闭环：从隐式不满信号提取诊断信息，做多组件textual-gradient式归因，再主动读取上下文源区分CREATE缺失与UPDATE陈旧，输出可执行CRUD建议供人工审核。",
    "D_key_results": [
        "60条DSAT轨迹：根因节点归因72.7%，端到端fix effectiveness 82%",
        "CREATE/UPDATE操作准确率96%；无探索时KB操作准确率仅33%，有探索升至83%",
        "整体归因相对迭代式TextGrad基线：节点准确率约2×，LLM调用约少16×",
    ],
    "E_industry_implications": [
        "Agent维护中心应从「再训模型」转向「持续修context资产」",
        "把用户纠正、重问、放弃当成可计算信号，接到自动归因与变更建议",
        "自动改KB/工具说明/Skill后必须配回归门禁，避免修一个坏一片",
    ],
    "F_one_line_judgement": "这篇最适合做生产Agent运维与Context Engineering的团队：TRACE从隐式不满信号归因异构上下文组件并建议CREATE/UPDATE，60条轨迹上节点归因72.7%、端到端修复82%、操作判断96%；不过证据主要来自合成基准（最长16节点），真实超长workflow仍需回归验证。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "TRACE", "definition": "TRajectory Attribution for Automated Context Engineering：从轨迹归因并修复上下文资产的反馈环。"},
        {"term": "Context engineering", "definition": "用prompt、KB、工具说明、Skill等上下文层定制Agent，而不改模型权重。"},
        {"term": "DSAT", "definition": "Dissatisfaction：用户不满轨迹，含纠正、重述、放弃等隐式信号。"},
        {"term": "Textual gradient", "definition": "用自然语言描述组件应如何改动的优化信号；TRACE扩展到异构上下文源。"},
        {"term": "CREATE / UPDATE", "definition": "内容缺失则CREATE；内容过时则UPDATE；需主动读源文件才能判对。"},
        {"term": "Holistic attribution", "definition": "对整段轨迹一次归因，避免迭代逐节点误把级联效应当根因。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：坏在上下文，却在人工翻日志",
            "body": "同一事故可能来自Skill阈值过期、KB缺条、工具schema写错或system prompt约束冲突。只看终局答错，定位不了该改哪份资产。",
        },
        {
            "title": "三阶段：检测→根因→推荐",
            "body": "Detector挖隐式不满；Root Cause做整图归因；Recommender主动读文件，给出CREATE/UPDATE/DELETE/NO_ACTION与路径。",
        },
        {
            "title": "为什么必须探索",
            "body": "只从对话很难区分「没有」与「有但旧」。无探索时KB操作准确率33%；读完源文件后升到83%。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果",
                "论文证据": "60条DSAT：节点归因72.7%；端到端修复82%。",
                "飞哥判断": "方向成立：多数context故障可自动诊断并给出可执行修复建议。",
            },
            {
                "看什么": "操作判断",
                "论文证据": "CREATE/UPDATE操作准确率96%；路径准确率82%。",
                "飞哥判断": "知不知道该新建还是改旧，已经很稳；精确到文件路径更难。",
            },
            {
                "看什么": "探索消融",
                "论文证据": "无探索KB Op Acc 33%→有探索83%；可从错误根因中恢复67%。",
                "飞哥判断": "读源文件不是锦上添花，是CREATE/UPDATE分水岭。",
            },
            {
                "看什么": "归因方式",
                "论文证据": "整体归因相对迭代基线：节点准确约2×，调用约少16×。",
                "飞哥判断": "别把级联传播节点逐个当根因；要一次看清比较信号。",
            },
        ],
    },
    "source_notes": [
        "主数字：节点归因72.7%、端到端82%、操作96%（Abstract / Table系列）；探索消融Table 6。",
        "消融：Holistic vs iterative Table 5；组件类型准确率Skill/prompt 100%、KB 83.3%、tool 66.7%。",
        "版本戳：arXiv:2608.09153v1 [cs.AI]；ChatGPT 0811批次 #3（今日人工补位）。",
        "单位：Amazon。",
        "证据边界：合成60条DSAT、最长16节点；真实超长生产轨迹外推需谨慎。",
    ],
    "so_what": "检查生产Agent故障时，别默认「模型不行」。先问：是哪一份prompt、KB、工具说明或Skill在骗它？有没有从不满轨迹接到自动归因？",
    "feige_view": "对照0808 SearchAuditor：那边找「轨迹哪一步坏了」，TRACE继续问「哪份上下文资产导致这一步坏掉」。Agent运维正在从模型训练转向context maintenance。",
    "limitations": [
        "主评测是合成基准（60条，最长16节点），真实超长workflow外推有限。",
        "隐式不满信号可能误判用户意图。",
        "自动修改context后若无回归门禁，会引入新故障。",
        "工具类归因更难（66.7%），文件边界模糊时路径命中下降。",
    ],
    "related_theme_picks": {
        "theme": "Context维护与失败归因",
        "intro": "本篇讲从不满轨迹修上下文资产；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.07885",
                "title_cn": "把推理溢价摊销成可复用Skill",
                "one_liner": "同日配对：Skill要编译，也要能被生产信号修。",
                "link": "https://arxiv.org/abs/2608.07885",
                "ready_date": "20260812",
            },
            {
                "arxiv_id": "2608.05212",
                "title_cn": "长程搜索失败审计",
                "one_liner": "0808：终局答错时怎么定位关键错误步。",
                "link": "https://arxiv.org/abs/2608.05212",
                "ready_date": "20260808",
            },
            {
                "arxiv_id": "2608.06410",
                "title_cn": "问题账本驱动的Agent harness自修",
                "one_liner": "0811：跨轮失败要有可继承的问题状态。",
                "link": "https://arxiv.org/abs/2608.06410",
                "ready_date": "20260811",
            },
        ],
    },
    "target_audience": [
        "做生产Agent运维 / Context Engineering的研究工程团队。",
        "关心KB、工具说明与Skill变更治理的平台同学。",
        "评估「模型没变但越用越差」事故的产品技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们准备再微调一版』：先问context资产有没有归因与修复环。",
        "方案评审：要求看CREATE/UPDATE准确率、回归门禁与人工审核入口。",
        "事故复盘：把纠正/重问/放弃从客服噪音改成诊断信号。",
    ],
    "objection_handling": [
        "客户说：『人工抽查看就行。』→ 回应：量一上来，瓶颈就是定位该改哪份资产。",
        "客户说：『合成评测不够真。』→ 回应：先把方法论跑通；落地仍要用真实DSAT+回归门禁。",
    ],
    "copy_paste_lines": [
        "别只改模型，先修上下文。",
        "TRACE：72.7%根因归因，端到端修复82%。",
        "SearchAuditor找坏步骤，TRACE找坏资产。",
    ],
    "key_quotes": [
        "72.7% root cause node attribution and 82% end-to-end fix effectiveness",
        "achieving 96% operation accuracy",
        "without exploration, the agent achieves only 33% accuracy... with exploration, accuracy rises to 83%",
    ],
    "info": {
        "title": "TRACE: TRajectory Attribution for Automated Context Engineering",
        "title_cn": "从不满轨迹归因并修复上下文资产",
        "link": "https://arxiv.org/abs/2608.09153",
        "authors": ["Yikai Zhao", "Pradeep Kumar Misra", "Saurabh Pandey"],
        "affiliations": ["Amazon"],
    },
    "score": {
        "total": 8.7,
        "dimensions": [
            {"label": "重要性 Impact", "value": 1.9},
            {"label": "创新性 Novelty", "value": 1.8},
            {"label": "可验证性 Evidence", "value": 1.5},
            {"label": "产业可用性 Applicability", "value": 1.8},
            {"label": "可复用性 Reusability", "value": 1.7},
        ],
    },
    "score_rationale": "生产Agent故障常在context layer，TRACE用隐式不满信号做多组件归因并给出CREATE/UPDATE，补齐SearchAuditor后的资产侧维护环。60条DSAT上节点归因72.7%、端到端82%、操作96%。证据主要来自合成基准（最长16节点），Evidence扣分；仿真方法论可复用，真实超长workflow外推仍有限。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.4,
        "highest_dimensions": ["重要性 Impact"],
        "lowest_dimensions": ["可验证性 Evidence"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "生产Agent维护瓶颈正从模型转向context资产，问题切得准。"},
            {"label": "创新性 Novelty", "value": 1.8, "role": "middle", "rationale": "把textual gradient扩到异构上下文并加探索式CREATE/UPDATE，工程组合清楚。"},
            {"label": "可验证性 Evidence", "value": 1.5, "role": "lowest", "rationale": "主证据是60条合成轨迹、最长16节点；真实性与规模外推弱。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "闭环可直接接到运维审核流；需配回归门禁。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "middle", "rationale": "仿真方法论可迁移；自动改写带来的回归风险限制照搬。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "根因节点归因72.7%，端到端修复82%", "evidence": "Abstract / Evaluation", "location": "Abstract"},
            {"claim": "CREATE/UPDATE操作准确率96%", "evidence": "Table 2 / Recommender", "location": "Table 2"},
            {"claim": "无探索KB Op Acc 33%→有探索83%", "evidence": "Table 6", "location": "Table 6"},
            {"claim": "整体归因相对迭代基线节点准确约2×、调用约少16×", "evidence": "Table 5", "location": "Table 5"},
            {"claim": "Skill/prompt组件归因100%，tool 66.7%", "evidence": "Table 4", "location": "Table 4"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260812 dual publish: Reason Wide + TRACE.",
        "Affiliations via overrides: Amazon.",
        "Numbers verified from PDF Abstract and Tables 2–6; synthetic eval boundary called out.",
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
        "2608.07885",
        "reasonwide",
        REASONWIDE_RICH,
        "别再每题重想一遍：轨迹蒸馏Skill摊销推理溢价，恢复55%–100%+缺口",
        "重复性Agent推理别每次现算；先把领域程序知识编译成Skill，再让非reasoning模型便宜复用。",
    )
    enrich_one(
        "2608.09153",
        "trace",
        TRACE_RICH,
        "别只改模型：从不满轨迹归因上下文资产，端到端修复有效率82%",
        "生产Agent坏了先别急着微调；很多故障在prompt、KB、工具说明和Skill里，可以从历史不满轨迹自动归因并修。",
    )
    print("enriched reasonwide + trace")


if __name__ == "__main__":
    main()
