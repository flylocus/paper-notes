#!/usr/bin/env python3
"""One-off enrichment for 20260725 paper-notes payloads (AREX + OpenForgeRL)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260725"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


AREX_RICH = {
    "A_research_problem": "多约束深度研究里，加长单条搜索轨迹并不保证系统进步：早期错误会残留，耗尽方向会反复，部分成立的候选也会被过早接受。难点不是『再搜一轮』，而是识别哪些约束仍未解决，并把诊断转成更有针对性的下一轮研究问题。",
    "B_core_contributions": [
        "用发现难、验证易的不对称性，把多约束研究写成递归自我改进（RSI）过程",
        "外环constraint-wise audit：按约束审计临时答案，决定接受/精炼/重启",
        "训练自主update_context工具，把长程轨迹压成保留已验证证据与未解决约束的状态",
        "放出AREX-Turbo(Qwen3.5-4B)与AREX-Base(122B-A10B)及主页/模型集合",
    ],
    "C_method_framework": "双环：内环搜证、整合、finish出临时答案+证据+置信度；外环按阈值决定Accept / Refine / Restart，Refine时把未解决约束写成下一轮定向目标。长程中自主调用update_context刷新研究状态。训练用可验证合成任务+教师轨迹过滤，并对关键取证/纠错区间做step-aware RL。",
    "D_key_results": [
        "BrowseComp消融：仅ACU 59.6→71.4；再加外环→82.5；相对两者皆无约+22.9",
        "Table1：AREX-Base DeepSearchQA 82.0 / WideSearch-en 52.4 / HLE(tool) 89.9；4B Turbo在六项中五项超过Qwen3.5-35B",
        "BrowseComp上80.3%案例会调用update_context",
    ],
    "E_industry_implications": [
        "深度研究Agent把『约束覆盖表』做成一等状态，而不只追加搜索轮次",
        "长程上下文优先学可执行状态更新工具，而不是固定截断或外部摘要",
        "评测同时看最终分与审计闭环：漏约束是否造成虚假完成感",
    ],
    "F_one_line_judgement": "深度研究的关键不是搜更久，而是把『哪些约束已证实、哪些还没』变成可递归推进的研究状态。",
    "glossary": [
        {"term": "Discovery–verification asymmetry", "definition": "找到同时满足多约束的答案很难，但对候选做约束级验证相对可分解、更便宜。"},
        {"term": "Outer self-improvement loop", "definition": "对外环：审计临时答案置信度与可恢复性，决定接受、精炼或重启，并生成下一轮定向目标。"},
        {"term": "ACU / update_context", "definition": "Autonomous Context Updating：模型自主把膨胀轨迹压缩为保留已验证证据与未解决约束的紧凑状态。"},
        {"term": "AREX-Turbo / AREX-Base", "definition": "Turbo=Qwen3.5-4B dense；Base=Qwen3.5-122B-A10B MoE。"},
        {"term": "BrowseComp / WideSearch / DeepSearchQA / HLE", "definition": "深度浏览、广覆盖检索、深度检索问答与带工具的Humanity’s Last Exam等搜索增强推理基准。"},
        {"term": "Constraint-wise audit", "definition": "按约束逐项检查支持证据，而不是只对整份答案做笼统反思。"},
    ],
    "method_subsections": [
        {
            "title": "内环：先形成可审计的临时答案",
            "body": "内环维护研究状态，调用搜索/浏览工具，必要时update_context，最后finish输出答案、支持证据与答案级置信度，供外环决策。",
        },
        {
            "title": "外环：Accept / Refine / Restart",
            "body": "置信度够则接受；不够则判断轨迹是否可恢复——可恢复则保留有效发现并定向补研，不可恢复则丢弃轨迹从原题重启。",
        },
        {
            "title": "训练：合成可验证任务 + 关键步强化",
            "body": "先构造多约束可验证题，再过滤教师轨迹；长程稀疏奖励下强调关键取证与纠错区间，避免整条轨迹等权回放。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "双环消融（BrowseComp）",
                "论文证据": "无ACU单轮59.6；+ACU→71.4；+外环→82.5；相对两者皆无约+22.9。",
                "飞哥判断": "增益来自『状态可维护+按约束再出发』，不是单纯加搜索次数。",
            },
            {
                "看什么": "主结果（Table1）",
                "论文证据": "Base：DeepSearchQA 82.0 / WideSearch-en 52.4 / HLE(tool) 89.9；4B Turbo六项中五项超过Qwen3.5-35B。",
                "飞哥判断": "规模效率故事成立：小模型靠研究状态管理也能打深研。",
            },
            {
                "看什么": "上下文更新频率",
                "论文证据": "BrowseComp上80.3%案例调用update_context。",
                "飞哥判断": "长程深研里，压缩状态是默认能力，不是可选插件。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "训练依赖合成可验证任务与高质量轨迹；摘要未给同等预算成本/延迟对比。",
                "飞哥判断": "落地前要单测审计器漏约束与压缩丢弱信号风险。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table1主结果；Table3双环/ACU消融（59.6/71.4/82.5，+22.9）；Table2称80.3%调用update_context。",
        "投稿/版本戳：arXiv:2607.21461v1 [cs.AI] 23 Jul 2026；ChatGPT 0725批次#1；Grok digest交叉提及。",
        "单位：Beijing Academy of Artificial Intelligence (BAAI) / AREX Team。",
        "资产：https://arex-research.com · https://vectorspacelab.github.io/arex-model/ · https://huggingface.co/collections/BAAI/arex",
        "证据边界：合成任务与教师轨迹依赖；审计漏约束可能虚假完成；成本/延迟/搜索调用量同等预算对比不足。",
    ],
    "so_what": "说白了，深度研究Agent缺的不是更多搜索步数，而是一份不断更新的『约束台账』：已证实的留下，未满足的变成下一题。AREX把这件事做成可训练的双环系统，并用ACU压住长程上下文膨胀。",
    "feige_view": "三个动作：①深研产品加约束覆盖面板（已支持/冲突/未解决）；②上下文策略从固定截断改为可学习的状态更新工具；③验收加『审计漏检』对抗用例，防止虚假完成。",
    "limitations": [
        "不过，收益可能依赖合成验证任务与高质量教师轨迹，开放网页噪声下外推需折扣。",
        "不过，自动审计器若漏约束，外环可能形成虚假完成感。",
        "不过，长程压缩是否丢失弱信号或矛盾证据，以及同等推理预算下的成本延迟，仍需更细评测。",
    ],
    "related_theme_picks": {
        "theme": "Agent训练与运行全生命周期",
        "intro": "本篇讲验证驱动的深研状态；同线可对照：",
        "items": [
            {"arxiv_id": "2607.21557", "title_cn": "在真实Harness里训Agent", "one_liner": "另一头：部署用什么脚手架，就在什么脚手架里做RL。", "link": "https://arxiv.org/abs/2607.21557", "ready_date": "20260725"},
            {"arxiv_id": "2607.21419", "title_cn": "策略感知的训练脚手架PATS", "one_liner": "训练期动态给提示、部署期拆掉，提高Agent RL样本效率。", "link": "https://arxiv.org/abs/2607.21419", "ready_date": "backlog"},
            {"arxiv_id": "2607.16716", "title_cn": "记忆失效后的组合推理评测", "one_liner": "状态管理另一刀：证据变更后下游该不该撤销。", "link": "https://arxiv.org/abs/2607.16716", "ready_date": "20260722"},
        ],
    },
    "target_audience": [
        "做深度研究/搜索增强Agent的研究与平台团队。",
        "关心长程上下文膨胀与可验证完成标准的产品负责人。",
        "评估是否自研双环深研系统的技术决策者。",
    ],
    "sales_use_cases": [
        "回应『我们加了多轮搜索』：用+22.9消融说明关键在约束审计与状态更新。",
        "方案评审：把约束覆盖表与ACU写成深研Agent验收项。",
        "模型选型：用4B Turbo相对35B的对比讲规模效率，而不是只比绝对分。",
    ],
    "objection_handling": [
        "客户说：『不就是Reflexion再搜一轮？』→ 回应：外环输出的是约束级未解决问题与可执行下一目标，并且有ACU维护结构化状态，不是笼统反思。",
        "客户说：『合成任务训出来的不能用。』→ 回应：同意外推要打折；价值在双环控制结构与消融证据，落地仍需真实流量复验。",
    ],
    "copy_paste_lines": [
        "深度研究别只多搜几轮，先把未证实约束变成下一题。",
        "已证实的留下，未满足的定向补研——这才是可递归的研究状态。",
        "BrowseComp：ACU+外环相对基线可抬约22.9分。",
    ],
    "key_quotes": [
        "discovery–verification asymmetry",
        "recursively improve its current answer by verifying intermediate results",
        "autonomous context-update tool that compresses growing interaction history",
    ],
    "score_rationale": "AREX把深度研究写成发现-验证不对称下的递归自我改进：内环搜证、外环约束审计，并训练自主context-update。BrowseComp消融与多基准结果扎实，且放出模型。扣分在合成任务依赖、审计漏约束风险与成本对比不足。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "BrowseComp：ACU 59.6→71.4；+外环→82.5；相对两者皆无约+22.9", "evidence": "Table 3 / ablation text around ACU and outer loop", "location": "Table 3 / Section ablation"},
            {"claim": "AREX-Base DeepSearchQA 82.0 / WideSearch-en 52.4 / HLE(tool) 89.9", "evidence": "Table 1 main results", "location": "Table 1"},
            {"claim": "4B Turbo在六项中五项超过Qwen3.5-35B", "evidence": "Table 1 discussion paragraph", "location": "Section results / Table 1"},
            {"claim": "BrowseComp上80.3%调用update_context", "evidence": "Table 2 context-update behavior", "location": "Table 2"},
            {"claim": "F段限制：合成任务、审计漏检、成本延迟", "evidence": "Limitations + ChatGPT notes + paper scope", "location": "Limitations"},
        ]
    },
}


OPENFORGE_RICH = {
    "A_research_problem": "生产Agent跑在Claude Code、Codex、OpenClaw一类复杂harness里，但开源SFT/RL栈很难原生表达多进程、带状态的真实推理过程。结果是：在简化循环里训完，部署到真实脚手架又掉点——训推环境不一致。",
    "B_core_contributions": [
        "把复杂harness推理与标准RL训练栈解耦，消除训推错配",
        "轻量代理记录模型调用，使veRL等框架能消费真实Agent轨迹",
        "Kubernetes为每条rollout开隔离容器，覆盖工具/Claw与GUI Agent",
        "实证不同harness可学性差异，并指出错误恢复仍是短板",
    ],
    "C_method_framework": "代理层承接harness的模型API请求，把多轮交互落成标准RL样本；编排层用K8s远程容器隔离任务与工具环境。研究者可在ZeroClaw/OpenClaw/Codex或GUI harness上直接做SFT+RL，而不必把脚手架逻辑硬塞进训练代码。",
    "D_key_results": [
        "OpenForge-Claw(SFT+RL)：ClawEval pass3 31.7 / pass@3 55.9；QwenClawBench 33.7；MCPAtlas 28.1（SFT为21.7/52.1/32.1/23.6）",
        "OpenForge-GUI(SFT+RL)：OSWorld-Verified 37.7；Online-Mind2Web 63.0；WebVoyager 72.3",
        "数百至数千任务即可超过同规模开源基线；分析显示RL抬升自我验证与工具覆盖，但错误恢复仍弱",
    ],
    "E_industry_implications": [
        "选型时评估『模型×harness』组合，而不只看裸模型分",
        "把部署用的OpenClaw/Codex直接接入训练环，减少模拟器迁移损耗",
        "RL看板单列错误恢复与自我验证，而不只看最终成功率",
    ],
    "F_one_line_judgement": "比较Agent不该只比权重：还要看模型能否在真实部署用的harness里被有效训练。",
    "glossary": [
        {"term": "Harness", "definition": "驱动多轮推理、工具调用与外部系统访问的推理脚手架（如Claude Code、Codex、OpenClaw）。"},
        {"term": "Harness-native RL", "definition": "直接在部署所用harness中采集轨迹并做强化学习，而不是在简化ReACT模拟器里训。"},
        {"term": "Proxy + orchestrator", "definition": "代理记录模型调用写成训练数据；编排器用容器隔离每条rollout环境。"},
        {"term": "OpenForge-Claw / OpenForge-GUI", "definition": "论文在Claw工具场景与多模态GUI场景上训练的两组Agent实例。"},
        {"term": "pass3 / pass@3", "definition": "ClawEval协议下的稳健性与多次尝试成功率指标。"},
        {"term": "veRL", "definition": "可消费标准轨迹样本的开源RL训练栈；本文用代理层与之对接。"},
    ],
    "method_subsections": [
        {
            "title": "解耦：harness照跑，训练栈只吃标准样本",
            "body": "不把多进程脚手架逻辑塞进RL代码，而是用代理拦截模型请求，把真实交互落成veRL可训的轨迹对。",
        },
        {
            "title": "扩展：任意harness × 任意环境",
            "body": "K8s为每条rollout开远程容器，可预装OpenClaw/Codex或GUI依赖，支持工具Agent与计算机/浏览器使用Agent。",
        },
        {
            "title": "分析：不是所有脚手架都一样好训",
            "body": "对比ReACT*/ZeroClaw/OpenClaw/Codex发现可学性差异大；RL改善自我验证与计划完成，但错误恢复仍明显薄弱。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "Claw主结果（Table2）",
                "论文证据": "SFT+RL：pass3 31.7 / pass@3 55.9 / QwenClawBench 33.7 / MCPAtlas 28.1；相对SFT全面抬升。",
                "飞哥判断": "在真实Claw harness里做RL有清晰增益，不是刷玩具环境。",
            },
            {
                "看什么": "GUI主结果（Table3）",
                "论文证据": "OSWorld-Verified 37.7；Online-Mind2Web 63.0；WebVoyager 72.3（约8B级）。",
                "飞哥判断": "同一套基础设施能跨工具与GUI，说明解耦设计站得住。",
            },
            {
                "看什么": "行为分析",
                "论文证据": "RL提升自我验证、工具覆盖、多步计划完成；错误恢复仍弱；部分harness更难学。",
                "飞哥判断": "上线看板要单列恢复力，否则会被平均成功率掩盖。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "K8s与多容器成本高；仍需数百至数千环境任务；harness间迁移不确定。",
                "飞哥判断": "这是基础设施投入题，不是提示词技巧题。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table2 Claw；Table3 GUI；摘要与§4叙述SFT→RL增益与错误恢复短板。",
        "投稿：arXiv:2607.21557v1 [cs.AI] 23 Jul 2026（ICLR 2026 under review）；ChatGPT 0725 #2。",
        "单位：Columbia University / Dartmouth College / Microsoft Research。",
        "资产：正文称将开源code/data/models（以最终发布为准）。",
        "证据边界：基础设施成本；harness迁移；错误恢复未系统解决；任务构造成本不可忽视。",
    ],
    "so_what": "说白了，Agent评测如果只在简化ReACT环里跑，和你线上真正用的OpenClaw/Codex可能不是同一物种。OpenForgeRL把真实harness接进RL，让『模型+脚手架』可以一起被训练和比较。",
    "feige_view": "三个动作：①内部排行榜改成模型×harness矩阵；②训练环境直接挂部署脚手架，少做模拟器迁移；③在RL指标里加错误恢复与自我验证分项。",
    "limitations": [
        "不过，Kubernetes与多容器rollout会带来较高基础设施成本。",
        "不过，不同harness行为差异大，训练成果迁移到新脚手架并不免费。",
        "不过，错误恢复短板已被承认，但尚未给出系统解决方案。",
    ],
    "related_theme_picks": {
        "theme": "Agent训练与运行全生命周期",
        "intro": "本篇讲harness-native RL基础设施；同线可对照：",
        "items": [
            {"arxiv_id": "2607.21461", "title_cn": "递归自我改进的深度研究Agent", "one_liner": "运行时另一头：用约束审计维护可验证研究状态。", "link": "https://arxiv.org/abs/2607.21461", "ready_date": "20260725"},
            {"arxiv_id": "2607.21419", "title_cn": "策略感知的训练脚手架PATS", "one_liner": "训练期动态给提示、成熟后拆掉，提高样本效率。", "link": "https://arxiv.org/abs/2607.21419", "ready_date": "backlog"},
            {"arxiv_id": "2607.13285", "title_cn": "Harness Handbook", "one_liner": "脚手架代码如何重排，才更利于编码Agent阅读与修改。", "link": "https://arxiv.org/abs/2607.13285", "ready_date": "backlog"},
        ],
    },
    "target_audience": [
        "运营OpenClaw/Codex等复杂harness的平台与Agent工程团队。",
        "做Agentic RL基础设施与评测的研究工程师。",
        "需要向管理层解释『为什么换脚手架分数大变』的技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们模型很大』：用同规模Claw/GUI增益说明关键在harness-native训练。",
        "基建立项：把代理+容器编排写成可复用训练平台能力。",
        "治理讨论：用错误恢复短板推动分项KPI，而不是只报平均成功率。",
    ],
    "objection_handling": [
        "客户说：『不就是远程环境RL吗？』→ 回应：重点是训推同一套复杂harness，而不是再造一个简化模拟器。",
        "客户说：『K8s太重。』→ 回应：同意成本高；但相对训推错配导致的返工，这是可计算的基础设施账。",
    ],
    "copy_paste_lines": [
        "别只比模型权重，要比模型在真实Harness里能不能被训起来。",
        "部署用OpenClaw，就尽量在OpenClaw里做RL。",
        "ClawEval pass3：SFT 21.7 → SFT+RL 31.7。",
    ],
    "key_quotes": [
        "train harness-based agents end-to-end in diverse environments",
        "decoupling training and inference",
        "error recovery remain weak",
    ],
    "score_rationale": "OpenForgeRL把真实复杂harness与标准RL栈解耦，使OpenClaw/Codex等部署脚手架可端到端训练；Claw与GUI多基准有清晰SFT→RL增益，并诚实标出错误恢复短板。扣分在K8s成本、迁移摩擦与恢复力未解。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "ClawEval pass3 31.7 / pass@3 55.9；QwenClawBench 33.7；MCPAtlas 28.1", "evidence": "Table 2 OpenForge-Claw(SFT+RL)", "location": "Table 2"},
            {"claim": "相对SFT：21.7/52.1/32.1/23.6 → 31.7/55.9/33.7/28.1", "evidence": "Table 2 SFT vs SFT+RL rows", "location": "Table 2"},
            {"claim": "OSWorld-Verified 37.7；Online-Mind2Web 63.0；WebVoyager 72.3", "evidence": "Table 3 OpenForge-GUI(SFT+RL)", "location": "Table 3"},
            {"claim": "RL改善自我验证/工具覆盖/多步计划，错误恢复仍弱", "evidence": "Abstract + analysis sections", "location": "Abstract / Section 5"},
            {"claim": "F段限制：成本、迁移、恢复力", "evidence": "Limitations discussion + ChatGPT notes", "location": "Limitations"},
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
        "2607.21461",
        "arex",
        AREX_RICH,
        "深度研究别只多搜几轮：AREX用约束审计把未证实部分变成下一题",
        "AREX把深度研究拆成内环搜证、外环按约束审计的递归自我改进；BrowseComp上从无ACU/无外环到完整系统可抬约22.9分，并放出4B与122B-A10B模型。",
    )
    enrich_one(
        "2607.21557",
        "openforgerl",
        OPENFORGE_RICH,
        "Agent别只比模型：OpenForgeRL让你在真实Harness里做端到端RL",
        "OpenForgeRL用代理+K8s把Claude Code/Codex/OpenClaw等真实harness接入标准RL栈；ClawEval pass3从SFT的21.7升到SFT+RL的31.7，GUI侧OSWorld-Verified达37.7。",
    )
    print("enriched both")


if __name__ == "__main__":
    main()
