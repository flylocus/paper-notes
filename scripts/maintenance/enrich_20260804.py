#!/usr/bin/env python3
"""One-off enrichment for 20260804 paper-notes payloads (ThinkReset + Zero-Mem)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260804"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


THINKRESET_RICH = {
    "intro_lead": "",
    "A_research_problem": "长链推理在有限窗口里会堆冗余、顶满上下文，还把早期错假设一路继承。压轨迹或调测试时调度都不够：缺的是一个能替换历史、还能继续解题的中间接口。终局奖励下，窗口快耗尽时模型更爱猜答案。",
    "B_core_contributions": [
        "把有限窗口长程推理重定义为可复用中间接口学习问题",
        "ThinkReset：文本空间 interface writeback + reset，直接优化 reset 后继续成功率",
        "指出 outcome-reward 长链 RL 在窗口耗尽边缘会诱导仓促猜答",
    ],
    "C_method_framework": "上下文占用越过阈值后触发写回：生成可复用中间状态，清空旧轨迹，仅从问题与接口继续。训练分阶段：先 SFT 写回可解接口，再对首次 reset 后继续成功做 RLOO，失败样本进二次 reset，学习分层接口。",
    "D_key_results": [
        "Qwen3-8B Avg@8：AIME24 81.3 / AIME25 73.2 / ZebraLogic 91.5 / AutoLogi 93.5 / GPQA-D 66.7",
        "相对骨干 Qwen3-8B 与轨迹保留强基线 Halo（79.6 / 70.4 / 89.2 / 93.1 / 64.8）整体更高",
        "14B/32B 与配对 bootstrap（p<0.01）支持收益来自接口学习，而非仅触发 reset",
    ],
    "E_industry_implications": [
        "上下文管理验收：别只问「摘要保真」，要问 reset 后能否继续完成任务",
        "长程 Agent 预算板：监控窗口耗尽前猜答率与写回触发次数",
        "训练信号要对齐「可继续状态」，终局奖励 alone 会把模型推向仓促交卷",
    ],
    "F_one_line_judgement": "这篇最适合窗口受限的长程推理/Agent：学会写可继续的中间接口并主动遗忘历史，但接口写错就失去原轨迹可查性。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "ThinkReset", "definition": "在有限窗口下主动写回中间接口、清空旧轨迹并继续求解的文本空间方法。"},
        {"term": "Intermediate interface", "definition": "可替代已丢弃推理历史、支持继续解题的可复用中间状态。"},
        {"term": "Interface writeback", "definition": "把关键问题状态写成接口并写回上下文，替换原长轨迹。"},
        {"term": "Post-reset continuation success", "definition": "清空历史后，仅从接口继续求解的成功率（论文主优化目标）。"},
        {"term": "Error anchoring", "definition": "早期错误假设被后续推理不断继承，难以脱离。"},
        {"term": "RLOO", "definition": "Leave-One-Out 相对策略优化，用于 reset 后继续成功奖励。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：轨迹保留 ≠ 能继续算",
            "body": "压缩、剪枝、调度都默认轨迹本身是主对象。窗口有限时，真正要答的是：丢掉历史后，还剩什么状态够继续解题。",
        },
        {
            "title": "写回—重置—继续",
            "body": "触发后生成接口并替换原轨迹；继续求解时输入只有问题与接口。优化目标直接对准继续成功，而非 token 级复原。",
        },
        {
            "title": "为何终局奖励会诱使猜答",
            "body": "题还没解完窗口却快满时，只看最终答案的奖励会推动模型放弃细推、抢先交卷。接口学习把「可继续」写进训练信号。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主增益（8B）",
                "论文证据": "ThinkReset Avg@8：AIME24 81.3、AIME25 73.2、ZebraLogic 91.5、AutoLogi 93.5、GPQA-D 66.7。",
                "飞哥判断": "固定窗口下继续解题能力明显抬升，不是单纯变短。",
            },
            {
                "看什么": "对照强度",
                "论文证据": "高于 Qwen3-8B 骨干与 Halo（SFT+RL 轨迹保留）；相对 TokenSkip 等重压缩也更稳。",
                "飞哥判断": "关键差在「写回状态是否被训练成可继续接口」。",
            },
            {
                "看什么": "统计支撑",
                "论文证据": "5 seed、95% bootstrap CI；相对基线配对 bootstrap p<0.01。",
                "飞哥判断": "不是单次抽卡数字。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主任务偏数学/逻辑长程；工具型网页 Agent 与开放研究流程需外推。",
                "飞哥判断": "先验企业长程规划，别直接当通用 Agent 银弹。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（8B Avg@8）；§4 实验设置与对照叙述。",
        "版本戳：arXiv:2607.28642v1 [cs.AI]；ChatGPT 0803批次 #1（0804 主发）。",
        "单位：Alibaba Group · Tsinghua University。",
        "证据覆盖：固定窗口继续成功率；token/延迟/reset次数完整成本账需补读附录。",
    ],
    "so_what": "说白了，压缩轨迹最多让上下文「塞得下」；ThinkReset逼模型在耗尽前写出「还能接着算」的状态，再主动忘掉旧历史——验收改成reset后继续成功率，而不是摘要看起来像不像。",
    "feige_view": "别再把上下文管理做成「更好的摘要」。验收标准改成：写回之后还能不能解。对照今日 Zero-Mem：一个管推理中途状态，一个管长期记忆账单。",
    "limitations": [
        "不过，接口若漏约束或写入错误结论，reset 后原始证据无法再查。",
        "文本接口仍可能带歧义与未经验证推断。",
        "公开主文对 token、延迟与 reset 次数的成本账不够完整；网页/代码仓 Agent 有效性仍待验证。",
    ],
    "related_theme_picks": {
        "theme": "长程 Agent：状态、记忆与预算",
        "intro": "本篇讲推理中途接口；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.29377",
                "title_cn": "零Token记忆操作",
                "one_liner": "同日配对：记忆管线别再烧 LLM。",
                "link": "https://arxiv.org/abs/2607.29377",
                "ready_date": "20260804",
            },
            {
                "arxiv_id": "2607.28069",
                "title_cn": "语义位置无关KV缓存",
                "one_liner": "0803：复用文档别反复 prefill。",
                "link": "https://arxiv.org/abs/2607.28069",
                "ready_date": "20260803",
            },
            {
                "arxiv_id": "2607.28457",
                "title_cn": "自验证自适应停算",
                "one_liner": "0803：续写预算也别平均撒。",
                "link": "https://arxiv.org/abs/2607.28457",
                "ready_date": "20260803",
            },
        ],
    },
    "target_audience": [
        "做长程推理与 Agent 上下文管理的研究/工程团队。",
        "关心窗口耗尽失败模式与训练目标错配的 RL 同学。",
        "评估「摘要式压缩」是否真能支撑继续求解的产品架构。",
    ],
    "sales_use_cases": [
        "回应『再加大上下文就行』：先问窗口耗尽前是否学会保存可继续状态。",
        "方案评审：要求看 writeback 触发规则、reset 后继续成功率与猜答率。",
        "成本沟通：用接口学习对照轨迹压缩/重调度，对齐验收指标。",
    ],
    "objection_handling": [
        "客户说：『摘要压缩不够吗？』→ 回应：摘要保真不等于可继续；论文直接优化 reset 后成功率。",
        "客户说：『无限上下文来了还需要？』→ 回应：再大窗口仍付冗余与错锚成本；接口是结构能力，不是窗长补丁。",
    ],
    "copy_paste_lines": [
        "别只压缩轨迹：学会写出可继续的中间接口再 reset。",
        "8B：AIME24 81.3 / ZebraLogic 91.5，高于 Halo 等轨迹保留基线。",
        "终局奖励在窗口耗尽边缘，会把模型推向猜答案。",
    ],
    "key_quotes": [
        "bounded-context long-horizon reasoning is fundamentally an intermediate interface learning problem",
        "directly optimizes post-reset continuation success",
        "final-answer reward encourages premature guessing rather than continued careful reasoning",
    ],
    "score_rationale": "ThinkReset把有限窗口长程推理做成可学习中间接口，8B多基准相对Halo等提升显著。Impact/Novelty高；Evidence扎实；Applicability中高；Reusability略低因成本账与开放Agent外推。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "8B Avg@8：AIME24 81.3 / AIME25 73.2 / ZebraLogic 91.5 / AutoLogi 93.5 / GPQA-D 66.7", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "高于 Halo（79.6 / 70.4 / 89.2 / 93.1 / 64.8）与骨干 Qwen3-8B", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "配对 bootstrap p<0.01；5 seed + 95% CI", "evidence": "Table 1 caption", "location": "Table 1"},
            {"claim": "直接优化 post-reset continuation success", "evidence": "Abstract / §3", "location": "Abstract / §3"},
            {"claim": "终局奖励在窗口耗尽边缘诱使猜答", "evidence": "Abstract / Intro", "location": "Abstract / §1"},
        ]
    },
}


ZEROMEM_RICH = {
    "intro_lead": "",
    "A_research_problem": "Agent 记忆系统常靠再调用 LLM 做摘要、建图、更新笔记。额外 token 与延迟会滚雪球；生成式抽象还可能丢掉可追溯证据。能不能让结构化记忆访问本身不再烧 LLM？",
    "B_core_contributions": [
        "定义 zero-token memory operations：除最终 QA 外，记忆全管线零 LLM 调用与零 LLM token",
        "Zero-Mem：保留原始交互轨迹，双视图（实体-上下文图 + 时间层级）检索与融合",
        "确定性证据/答案校准，保证 reader 只看见可追溯证据",
    ],
    "C_method_framework": "轨迹原样落库。实体-上下文图暴露跨交互关系；时间层级保住会话局部与会话状态。查询侧用轻量 profile 协调两视图，融合排序并做证据闭包；确定性校准去掉冲突项。只有最终 reader 调 LLM，事后再做答案格式/支持检查。",
    "D_key_results": [
        "统一配置：F1 59.15 / BLEU-1 52.96；记忆操作 LLM tokens = 0",
        "记忆操作总耗时 334.77s、0.22s/query，相对最快基线 LightMem 降 57.6%",
        "LoCoMo 与 HotpotQA（56K–448K）上表现有竞争力；消融支持双视图互补",
    ],
    "E_industry_implications": [
        "记忆账单独计：把 memory-op LLM token/延迟从最终答题账单里拆出来",
        "优先保留可追溯原始轨迹，别默认「先摘要再检索」",
        "检索设计同时要有关系视图与时间视图，扁相似检索不够",
    ],
    "F_one_line_judgement": "这篇最适合长期交互 Agent 的记忆账单治理：结构化记忆不必生成式中间层，但编码器与管线工程成本仍要单独立项。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "Zero-Mem", "definition": "除最终 QA reader 外，记忆操作零 LLM 调用/零 LLM token 的记忆框架。"},
        {"term": "Zero-token memory operations", "definition": "记忆构建、组织、路由、检索与校准不消耗 LLM 输入输出 token。"},
        {"term": "Entity–context graph", "definition": "基于实体共现与轨迹邻接的关系视图，支持跨交互连通检索。"},
        {"term": "Temporal hierarchy", "definition": "按时间组织的层级视图，保留会话局部与会话级状态。"},
        {"term": "Deterministic calibration", "definition": "用规则过滤冲突证据并校准答案，不再调用 LLM。"},
        {"term": "Provenance-preserving", "definition": "证据始终可追溯到原始交互轨迹，不被生成摘要替换。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：生成式记忆在收费",
            "body": "摘要/笔记/图谱更新若每步都调用 LLM，成本会随交互增长。中间层一抽象，原始证据也可能难回溯。",
        },
        {
            "title": "双视图，不生成替代品",
            "body": "图视图抓关系，时间视图抓局部与会话状态；二者指向同一批原始轨迹单元，而不是另写一份记忆文档。",
        },
        {
            "title": "只有最后一步用 LLM",
            "body": "检索与校准是确定性管线。最终 reader 吃证据集答题；答案侧再做支持性/类型/格式检查。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主质量",
                "论文证据": "统一配置 F1 59.15 / BLEU-1 52.96，高于对照记忆系统。",
                "飞哥判断": "省钱不是靠降质量换来的。",
            },
            {
                "看什么": "记忆账单",
                "论文证据": "记忆操作 LLM tokens = 0；总耗时 334.77s、0.22s/query。",
                "飞哥判断": "真正把 memory-op 从生成式 workload 里拆出来了。",
            },
            {
                "看什么": "相对最快基线",
                "论文证据": "相对 LightMem 记忆操作时延降 57.6%。",
                "飞哥判断": "非生成管线没有变成更慢的替代成本。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主评 LoCoMo + HotpotQA 记忆变体；代码审稿后公开；编码器成本另计。",
                "飞哥判断": "先当记忆管线改造样本，工具执行 Agent 需再验。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 2（效率与 F1/BLEU）；消融与 HotpotQA 叙述。",
        "版本戳：arXiv:2607.29377v1 [cs.CL]；Grok/X 0804窗口热议项。",
        "单位：The Hong Kong Polytechnic University · Southwestern University of Finance and Economics · Jilin University。",
        "证据覆盖：长记忆/长上下文 QA；开放工具 Agent 与编码器账单需另评。",
    ],
    "so_what": "说白了，Agent 记忆不一定要先「写一篇摘要」。把原始轨迹结构化检索好，再只在最终答题时用一次 LLM，账单会干净很多。",
    "feige_view": "别把记忆系统默认建成又一轮 agent 套娃。先拆账：哪些步骤必须 LLM，哪些可以确定性完成。对照今日 ThinkReset：一个省推理中途上下文，一个省记忆管线 token。",
    "limitations": [
        "不过，零 LLM token ≠ 零计算：编码器、建索引与检索仍有成本。",
        "代码与实现细节待审稿后公开，复现节奏受限。",
        "主基准偏记忆问答；强工具调用/网页操作场景需外推验证。",
    ],
    "related_theme_picks": {
        "theme": "长程 Agent：状态、记忆与预算",
        "intro": "本篇讲零 token 记忆；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.28642",
                "title_cn": "可学习中间接口重置",
                "one_liner": "同日配对：推理中途也要可继续状态。",
                "link": "https://arxiv.org/abs/2607.28642",
                "ready_date": "20260804",
            },
            {
                "arxiv_id": "2607.27415",
                "title_cn": "行动图正负价值记忆",
                "one_liner": "0801：经验复用别从零搜索。",
                "link": "https://arxiv.org/abs/2607.27415",
                "ready_date": "20260801",
            },
            {
                "arxiv_id": "2607.28069",
                "title_cn": "语义位置无关KV缓存",
                "one_liner": "0803：复用文档别反复 prefill。",
                "link": "https://arxiv.org/abs/2607.28069",
                "ready_date": "20260803",
            },
        ],
    },
    "target_audience": [
        "做 Agent 长期记忆与检索管线的平台团队。",
        "关心记忆子系统 token/延迟账单的产品与成本负责人。",
        "评估生成式记忆 vs 结构化原轨迹检索的研究/工程同学。",
    ],
    "sales_use_cases": [
        "回应『记忆当然要靠 LLM 摘要』：先问摘要层是否引入不可追溯损失与重复账单。",
        "方案评审：要求拆 memory-op 与 final-QA 两套成本，并看证据 provenance。",
        "成本沟通：用零 LLM memory token + 相对最快基线时延降幅做对照。",
    ],
    "objection_handling": [
        "客户说：『不用 LLM 记忆会不会笨？』→ 回应：论文在统一 reader 与预算下质量仍领先/竞争力强。",
        "客户说：『编码器不算成本吗？』→ 回应：算，但应单独立项；关键是去掉反复生成式 memory 调用。",
    ],
    "copy_paste_lines": [
        "记忆管线可以零 LLM token：只在最终答题时调用一次。",
        "F1 59.15；相对最快基线记忆操作时延降 57.6%。",
        "先保留可追溯原始轨迹，再谈要不要生成摘要。",
    ],
    "key_quotes": [
        "zero-token memory operations",
        "reduces memory-operation time cost by 57.6% relative to the fastest compared baseline",
        "structured agent memory need not generate an intermediate representation of the past",
    ],
    "score_rationale": "Zero-Mem把Agent记忆做成零LLM管线，统一配置F1 59.15且时延降57.6%。Impact/Applicability/Evidence高；Novelty中高；Reusability略低因代码待公开与编码器成本另计。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "统一配置 F1 59.15 / BLEU-1 52.96；记忆 LLM tokens = 0", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "记忆操作时延相对 LightMem 降 57.6%（0.22s/query）", "evidence": "Table 2 / efficiency discussion", "location": "Table 2"},
            {"claim": "LoCoMo + HotpotQA（56K–448K）有竞争力/最优区间表现", "evidence": "Experiment section", "location": "§Experiment"},
            {"claim": "双视图消融显示互补；去闭包/校准会掉点", "evidence": "Ablation / Figure 3 narrative", "location": "Ablation"},
            {"claim": "代码审稿后公开；编码器成本另计", "evidence": "Abstract / Limitations", "location": "Abstract / F"},
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
        "2607.28642",
        "thinkreset",
        THINKRESET_RICH,
        "别只压轨迹：ThinkReset学会写可继续的中间接口，窗口耗尽前reset继续算",
        "ThinkReset把有限窗口长程推理做成可学习中间接口：写回状态、清空旧轨迹，直接优化reset后继续成功率。",
    )
    enrich_one(
        "2607.29377",
        "zeromem",
        ZEROMEM_RICH,
        "Agent记忆可以零LLM token：Zero-Mem只在最终答题调用模型，时延降57.6%",
        "Zero-Mem让记忆构建与检索不再烧LLM：保留原始轨迹、双视图检索，统一配置下F1 59.15且记忆操作时延降57.6%。",
    )
    print("enriched thinkreset + zeromem")


if __name__ == "__main__":
    main()
