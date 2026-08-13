#!/usr/bin/env python3
"""One-off enrichment for 20260810 paper-notes payloads (CIPO + WitProbe Runtime Observability)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260810"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


CIPO_RICH = {
    "intro_lead": "",
    "A_research_problem": "很多搜索 Agent 看似在检索，实际先用参数知识下结论，再搜材料背书。现有 RL 多奖终局对错或中间进度，很少直接衡量检索后动作是否真依赖新证据，确认偏误就被强化。",
    "B_core_contributions": [
        "指出先验驱动推理的奖励错位，并提出证据导向 RL 框架 CIPO",
        "EALR：对比可见/遮蔽证据的动作似然，无需额外 rollout 或奖励模型",
        "七个域内/域外 QA 基准 + 证据利用率与先验驱动率分析",
    ],
    "C_method_framework": "CIPO 在每次检索后，对比证据可见与证据遮蔽条件下下一步动作的似然，得到 EALR 作为 turn-level 密集型证据使用奖励，再与全局 outcome reward 组合做策略优化；无需人工过程标注，也不另训奖励模型。",
    "D_key_results": [
        "Qwen2.5-7B：宏观平均 F1 0.504，超次优 IGPO 0.457 约 4.7 点",
        "Qwen2.5-3B：宏观平均 F1 0.456，同样领先约 4.7 点",
        "组合后支持性证据利用率：3B 55.2% / 7B 60.7%；无关证据利用率：3B 10.6% / 7B 9.1%",
    ],
    "E_industry_implications": [
        "训练搜索 Agent 时，奖励别只看终局正确，要检查检索后推理是否被新证据改写",
        "评测要同时报答案分和证据使用质量（支持性/无关性利用率、先验驱动率）",
        "上线验收：抽样对比「搜到又没用」与「证据改结论」轨迹，而不是只看引用条数",
    ],
    "F_one_line_judgement": "这篇最适合做联网搜索 Agent 与 Deep Research 训练的团队：用 EALR 奖励「检索后动作是否依赖新证据」，并保留终局正确性；不过过程信号仍可能被表面复述 gaming，也不自动解决来源可信与证据冲突。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "CIPO", "definition": "Contextual Information Policy Optimization：证据导向的搜索 Agent RL 训练框架。"},
        {"term": "EALR", "definition": "Evidence-Access Log-Likelihood Ratio：对比证据可见/遮蔽时下一步动作似然，量化动作对检索证据的敏感度。"},
        {"term": "Prior-driven reasoning", "definition": "先验驱动推理：先用参数知识定结论，检索只负责背书，证据难改写后续动作。"},
        {"term": "Evidence-driven reasoning", "definition": "证据驱动推理：检索结果能引导或修正下一步动作与最终判断。"},
        {"term": "Sup. / Irr.", "definition": "支持性 / 无关性证据利用率：答案是否依赖有用证据，以及是否被无关检索内容牵引。"},
        {"term": "Outcome reward", "definition": "终局答案正确性奖励；与 EALR 组合可抑制「响应证据但不辨质量」。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：搜到不等于用到",
            "body": "终局正确或中间进度奖励，都无法判断检索后动作是否依赖新证据。Agent 可以先猜、再搜、再假装有据。",
        },
        {
            "title": "EALR：把证据使用变成可算信号",
            "body": "遮住最近 <information> 块后看下一步动作似然是否下降。正 EALR 表示动作真依赖刚检索到的内容，无需额外 rollout。",
        },
        {
            "title": "与终局奖励搭档，而不是互替",
            "body": "EALR 单独会抬证据响应度，也可能抬无关证据利用率；叠上 outcome 才同时抬 F1、抬 Sup.、压 Irr.。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果（7B）",
                "论文证据": "宏观平均 F1 0.504；次优 IGPO 0.457（+4.7）。",
                "飞哥判断": "不是单点刷分，宏观与多任务领先一致。",
            },
            {
                "看什么": "主结果（3B）",
                "论文证据": "宏观平均 F1 0.456；次优 GiGPO 0.409（+4.7）。",
                "飞哥判断": "小模型同样受益，说明不是只靠规模硬扛。",
            },
            {
                "看什么": "证据质量",
                "论文证据": "组合后 Sup.：3B 55.2% / 7B 60.7%；Irr.：3B 10.6% / 7B 9.1%。EALR-only 时 7B Irr. 会升到 28.9%。",
                "飞哥判断": "EALR 让模型响应证据，outcome 才逼它挑有用证据。",
            },
            {
                "看什么": "训练动态",
                "论文证据": "训练过程中 CIPO 先验驱动率低于 IGPO，且在答对样本里仍持续下降。",
                "飞哥判断": "答对了也可能在走先验捷径；这一项查的是行为，不只是分数。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 1 宏观 F1；7B 0.504 vs IGPO 0.457；3B 0.456 vs GiGPO 0.409；Table 2 Sup./Irr.（3B 55.2%/10.6%，7B 60.7%/9.1%）；§4.4 prior-driven。",
        "版本戳：arXiv:2608.06128v2 [cs.AI]；ChatGPT 0807 批次 #3（0808/0809 backlog，今日主发）。",
        "单位：Beihang University；Communication University of China。",
        "开源入口：https://github.com/gxingyu/cipo",
        "证据覆盖：七个 ID/OOD QA；真实开放网页与来源冲突场景外推仍有限。",
    ],
    "so_what": "说白了，联网 Agent 下一阶段验收别只数检索次数和引用条数。要问：新证据有没有改写后续动作？若没有，你训练的可能是会搜的确认偏误机。",
    "feige_view": "问题出在哪？不是没搜，而是搜了也不改判断。对照前两天 SearchAuditor / SkillHEX：一个找错在哪一步，一个用实验改技能，CIPO 补第三刀——证据到底有没有进推理。",
    "limitations": [
        "EALR 仍可能被表面复述检索文本 gaming。",
        "减少确认偏误不等于解决来源可靠性、证据冲突或事实新鲜度。",
        "评测仍以受控 QA 环境为主，开放网页噪声外推待验证。",
        "先验驱动率依赖 LLM 辅助评估协议，标注成本与噪声需单独管控。",
    ],
    "related_theme_picks": {
        "theme": "证据条件搜索与失败调试",
        "intro": "本篇讲证据条件推理训练；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.05863",
                "title_cn": "异构注意力内存运行时可观测",
                "one_liner": "同日配对：底座侧单次请求还值不值得信。",
                "link": "https://arxiv.org/abs/2608.05863",
                "ready_date": "20260810",
            },
            {
                "arxiv_id": "2608.05212",
                "title_cn": "长程搜索失败审计",
                "one_liner": "0808：终局答错时怎么定位关键错误步。",
                "link": "https://arxiv.org/abs/2608.05212",
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
        "训练搜索 / Deep Research Agent 的研究工程团队。",
        "关心确认偏误与证据使用质量评测的平台同学。",
        "评估「搜到了却没用」事故的产品技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们已经加了搜索工具』：先问奖励与评测有没有衡量证据是否改写推理。",
        "方案评审：要求同时看 F1 / Sup. / Irr. / prior-driven rate，而不是只看命中率。",
        "训练沟通：用 +4.7 F1 与 Sup. 60.7% 说明密集证据信号比只奖终局更有杠杆。",
    ],
    "objection_handling": [
        "客户说：『有了 citation 就够了。』→ 回应：citation 可以是背书；CIPO 查的是动作似然有没有因证据改变。",
        "客户说：『再加个反射环就行。』→ 回应：反射若不对照证据可见/遮蔽，仍可能在先验上原地打转。",
    ],
    "copy_paste_lines": [
        "别再先猜再搜：让证据真正改写下一步。",
        "CIPO：7B 宏观 F1 0.504（+4.7 vs IGPO）。",
        "EALR+outcome：支持性证据利用率到 60.7%。",
    ],
    "key_quotes": [
        "reach a score of 0.504, which exceeds the next best method (IGPO at 0.457) by 4.7 F1 points",
        "supportive-evidence utilization to 55.2% and 60.7%",
        "requires neither human process annotations nor an additional reward model",
    ],
    "info": {
        "title": "Contextual Information Policy Optimization for Search Agents",
        "title_cn": "证据条件策略优化改搜索Agent",
        "link": "https://arxiv.org/abs/2608.06128",
        "authors": ["Xingyu Guo", "Wei Chen", "Linlin Yang", "Baochang Zhang"],
        "affiliations": ["Beihang University", "Communication University of China"],
    },
    "score_rationale": "CIPO把检索后推理是否真正依赖新证据做成可优化信号（EALR），直击Search Agent确认偏误。7基准macro F1与证据利用率消融清楚；Impact/Novelty高。表面复述与过程信号被gaming的风险使Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "Deep Research 生产事故里，「搜了却没用」与确认偏误是高频真问题。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "EALR 用可见/遮蔽对比直接度量证据敏感度，越过纯终局或手注过程奖励。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "middle", "rationale": "七基准、消融与利用率表完整；开放网页与冲突证据场景仍弱。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "有代码与可复现检索环境；落地仍需 RL 训练栈与评测协议配套。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "过程信号可能被复述 gaming；来源可信与冲突消解未覆盖。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "7B 宏观平均 F1 0.504，超 IGPO 0.457 约 4.7 点", "evidence": "Table 1 / §4.2", "location": "Table 1"},
            {"claim": "3B 宏观平均 F1 0.456，超 GiGPO 0.409 约 4.7 点", "evidence": "Table 1 / §4.2", "location": "Table 1"},
            {"claim": "组合后 Sup. 3B 55.2% / 7B 60.7%；Irr. 3B 10.6% / 7B 9.1%", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "EALR-only 提升 F1 但抬高无关证据利用率", "evidence": "Table 2 / §4.3", "location": "§4.3"},
            {"claim": "训练中 CIPO prior-driven rate 低于 IGPO", "evidence": "Figure 4 / §4.4", "location": "§4.4"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260810 dual publish: CIPO + Runtime Observability.",
        "Affiliations normalized via overrides: Beihang + CUC.",
        "Numbers verified from PDF Table 1–2 and §4.2–4.4.",
    ],
}


WITPROBE_RICH = {
    "intro_lead": "",
    "A_research_problem": "当代模型运行时 memory 不再只有标准 KV cache，还有 latent cache、稀疏选择器与 recurrent state。它们压缩失败机制不同；只靠离线平均指标，无法告诉你当前这条真实请求是否已越过风险预算。",
    "B_core_contributions": [
        "四类 attention memory 的统一运行时可观测契约与三算子代数",
        "度量作为类型：非法组合被运行时与 Lean 双拒绝，组合继承最弱认证层级",
        "请求级 risk ledger + 12.4M entry replay 与 DeepSeek-V4 静默损坏定位",
    ],
    "C_method_framework": "把 attention memory 写成 update/select/read 三算子，给每阶段类型化误差契约；仅允许度量匹配的组合，无法形式认证的环节自动降级为 empirical，并汇总为可执行的请求级 risk ledger，配合 fail-closed 观测与回退。",
    "D_key_results": [
        "12.4M entry reads、八路并发下风险预算零违规",
        "六模型五家族八探针行；GLM/V4 top-1 认证约 99.26%/99.40%",
        "在 served DeepSeek-V4 压缩 KV 原型上定位到静默损坏的结构边界",
    ],
    "E_industry_implications": [
        "上线 KV 压缩前，先问：能否对单次请求给出风险预算与认证层级，而不只看离线平均掉点",
        "验收别把 empirical 段落写成 end-to-end certified；最弱一环决定整条链层级",
        "排查静默质量事故：用机器裁定的判别程序定位到 eviction/slot-reuse 边界，而不是只看下游任务成功率",
    ],
    "F_one_line_judgement": "这篇最适合做推理服务与 KV 压缩上线的团队：用类型化契约为异构 attention memory 建请求级风险账本，机器裁定认证层级；不过探针注入未随仓发布，closed API 也几乎用不上。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "WitCert / WitProbe", "definition": "论文给出的 attention memory 运行时可观测契约与探针/账本体系（仓库 witprobe-attention-memory）。"},
        {"term": "Attention memory classes", "definition": "dense KV、latent cache、learned sparse selector、recurrent state 四类运行时记忆形态。"},
        {"term": "Update / Select / Read", "definition": "统一三算子：写内存、选子集、读出注意力输出。"},
        {"term": "Certification tier", "definition": "certified / partially certified / empirical；组合继承最弱层级，由机器裁定而非文案自称。"},
        {"term": "Request-level risk ledger", "definition": "为单次真实请求汇总局部契约与预算花费，支持 fail-closed 判定。"},
        {"term": "Telescoping budget", "definition": "未知请求长度下仍不超额的 per-event δ 花费规则（机器检查定理）。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：静默损坏比崩溃更可怕",
            "body": "压缩 cache 仍可结构合法、模型继续生成，任务远下游才掉点。离线平均「看起来还行」救不了这一条请求。",
        },
        {
            "title": "先把异构 memory 写成同一代数",
            "body": "update/select/read + 局部契约，让新架构变成可证明义务，而不是再写一套专用检查器。",
        },
        {
            "title": "度量类型化，拒绝假合成",
            "body": "相对残差与总变差质量不能直接相加。作者自己的第一版链路被类型检查与 Lean 双拒绝，这才是工程纪律。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "覆盖面",
                "论文证据": "八探针行 / 六模型 / 五架构家族（Table 1），过验收门才上报。",
                "飞哥判断": "跨 dense / latent / sparse / recurrent 才谈得上统一观测。",
            },
            {
                "看什么": "账本纪律",
                "论文证据": "12.4M entry reads；风险预算零违规；δreq=0.01 望远镜花费有定理。",
                "飞哥判断": "验收要答「这条请求还在预算内吗」，不是「平均好看吗」。",
            },
            {
                "看什么": "局部认证",
                "论文证据": "GLM/V4 top-1 认证约 99.26%/99.40%；latent 代理 4,032 cells 上 0/4,032 Tier-A 违规。",
                "飞哥判断": "局部有证就标 certified；证不了就自动降 empirical。",
            },
            {
                "看什么": "生产定位",
                "论文证据": "DeepSeek-V4 压缩 KV 原型：静默损坏定位到 eviction/slot-reuse 边界。",
                "飞哥判断": "事故要能判定边界；光拿一个压缩分数不够。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract / Table 1 / §5；12.4M entry reads；零违规；8 probe rows；top-1 99.26%/99.40%；latent 代理 0/4032 Tier-A；DeepSeek-V4 案例。",
        "版本戳：arXiv:2608.05863v1 [cs.AI]；ChatGPT 0807 批次 #4（今日双发）。",
        "单位：Metask Lab。",
        "开源入口：https://github.com/metask-ai/witprobe-attention-memory（Lean/artifact 在仓；架构相关探针注入未发布）。",
        "证据覆盖：真实 serving 与并发实验强；closed API 与非自托管栈难直接复用。",
    ],
    "so_what": "Long Context 上线后，压缩考核不该停在平均掉点。单次请求有没有风险预算和认证层级——答不上来，就别把平均值当保险。",
    "feige_view": "平均值好看，救不了静默坏掉的那一条请求。对照同日 CIPO：一边查证据进没进推理，一边查底座这条请求还值不值信。",
    "limitations": [
        "架构相关探针注入实现未随公开仓发布，集成门槛仍高。",
        "部分保证只能做到 empirical；不得包装成全链路 certified。",
        "closed API / 黑盒推理服务几乎无法接入同级观测。",
        "过保守的风险界限可能侵蚀压缩收益，需要业务侧预算权衡。",
    ],
    "related_theme_picks": {
        "theme": "推理运行时 memory 与压缩可信",
        "intro": "本篇讲请求级 memory 可信；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.06128",
                "title_cn": "证据条件策略优化改搜索Agent",
                "one_liner": "同日配对：检索证据有没有真正改写推理。",
                "link": "https://arxiv.org/abs/2608.06128",
                "ready_date": "20260810",
            },
            {
                "arxiv_id": "2608.03893",
                "title_cn": "跨模型KV Prefill复用",
                "one_liner": "0809：同系列切换时 KV 怎么少付 prefill 税。",
                "link": "https://arxiv.org/abs/2608.03893",
                "ready_date": "20260809",
            },
            {
                "arxiv_id": "2607.29377",
                "title_cn": "Zero-Mem 结构化长期记忆",
                "one_liner": "0804：记忆访问未必需要 LLM 摘要税。",
                "link": "https://arxiv.org/abs/2607.29377",
                "ready_date": "20260804",
            },
        ],
    },
    "target_audience": [
        "做推理服务、KV 压缩与 Long Context 上线的系统团队。",
        "负责静默质量事故排查与 serving 可观测性的 SRE / 平台同学。",
        "评估压缩方案风险预算与认证话术的研究工程同学。",
    ],
    "sales_use_cases": [
        "回应『离线压缩几乎不掉点』：先问单次请求风险账本与认证层级。",
        "方案评审：要求看最弱环节是否 empirical，以及 eviction/slot-reuse 边界。",
        "事故复盘：用机器裁定判别程序，而不是只盯下游任务成功率。",
    ],
    "objection_handling": [
        "客户说：『平均掉点很小就能上。』→ 回应：静默损坏可以发生在平均值很好的系统里；要请求级预算。",
        "客户说：『我们已经做了 cache 校验。』→ 回应：先确认校验覆盖四类 memory，以及度量能否合法组合。",
    ],
    "copy_paste_lines": [
        "压缩后，这一请求还可信吗？",
        "12.4M entry reads，风险预算零违规。",
        "认证层级由机器裁定，别靠文案自称 end-to-end certified。",
    ],
    "key_quotes": [
        "holds its risk budget with zero violations",
        "Replayed over 12.4M entry reads",
        "composition inherits the weakest tier, and the tier is decided by the machine",
    ],
    "info": {
        "title": "Runtime Observability for Heterogeneous Attention Memory",
        "title_cn": "异构注意力内存运行时可观测",
        "link": "https://arxiv.org/abs/2608.05863",
        "authors": ["Fanzhe Wei", "Li Liu", "Ziyang Wang", "Chenyu Wang"],
        "affiliations": ["Metask Lab"],
    },
    "score_rationale": "异构attention memory的请求级risk ledger + 机器裁定认证层级，切中压缩部署后「这一请求还可信吗」。12.4M entry reads、Lean与claim guard证据硬。Impact/Novelty/Evidence高；探针注入未开源与集成门槛使Applicability/Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.3,
        "highest_dimensions": ["创新性 Novelty", "可验证性 Evidence"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.8, "role": "middle", "rationale": "压缩上线后的静默损坏是真实生产事故类型，请求级可信是刚需。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "度量类型化 + 机器裁定认证层级，把可观测从口号做成可拒绝非法合成的系统。"},
            {"label": "可验证性 Evidence", "value": 1.9, "role": "highest", "rationale": "大规模 entry replay、Lean、claim guard 与可重生物品链硬。"},
            {"label": "产业可用性 Applicability", "value": 1.7, "role": "middle", "rationale": "自托管 serving 可对齐；集成门槛高，探针注入未随仓开放。"},
            {"label": "可复用性 Reusability", "value": 1.6, "role": "lowest", "rationale": "closed API 难以接入；过保守预算也可能吃掉压缩收益。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "12.4M entry reads 下风险预算零违规", "evidence": "Abstract / §5", "location": "Abstract"},
            {"claim": "八探针行 / 六模型 / 五家族", "evidence": "Table 1 caption / §5.2", "location": "Table 1"},
            {"claim": "GLM/V4 top-1 认证约 99.26%/99.40%；latent 代理 0/4032 Tier-A", "evidence": "Table 1 / §5.3", "location": "§5.3"},
            {"claim": "类型检查拒绝作者第一版非法度量组合", "evidence": "§5.4", "location": "§5.4"},
            {"claim": "DeepSeek-V4 压缩 KV 原型定位静默损坏边界", "evidence": "Abstract / later sections", "location": "Abstract"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260810 dual publish: CIPO + Runtime Observability.",
        "Affiliations via overrides: Metask Lab.",
        "Numbers verified from PDF Abstract/Table 1/§5.",
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
    # Affiliations already in rich.info (+ overrides files). Skip live verify here to keep enrich offline-safe.
    enrich_one(
        "2608.06128",
        "cipo",
        CIPO_RICH,
        "别再先猜再搜：CIPO给证据使用打分，7B宏观F1从0.457提到0.504",
        "Search Agent 的关键不是搜没搜到，而是检索结果有没有改写后续推理；CIPO用EALR把这一点写进RL奖励。",
    )
    enrich_one(
        "2608.05863",
        "witprobe",
        WITPROBE_RICH,
        "压缩后这一请求还可信吗：请求级风险账本兜底异构attention memory",
        "Long Context上线后，难点不再只是能不能塞进1M tokens，而是压缩/淘汰后当前请求还值不值得信；WitCert把这件事做成可执行风险账本。",
    )
    print("enriched cipo + witprobe")


if __name__ == "__main__":
    main()
