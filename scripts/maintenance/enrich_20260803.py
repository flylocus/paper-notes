#!/usr/bin/env python3
"""One-off enrichment for 20260803 paper-notes payloads (SemPIC + SVR)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260803"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


SEMPIC_RICH = {
    "intro_lead": "",
    "A_research_problem": "同一批长文档，会被不同指令、对话历史和文档次序反复塞进 Agent。前缀缓存对不上这种复用；朴素位置无关 KV 又缺后续上下文，质量容易塌。",
    "B_core_contributions": [
        "诊断：边界条件 PIC 能修好边界附近，却留下内部与任务级残差",
        "离线可训练的原生文档 Writer，输出标准分层 KV，在线 Reader 不变",
        "KV Gradient Checkpointing：保留缓存梯度路径，同时压峰值训练显存",
    ],
    "C_method_framework": "LoRA 只在 Writer 编译文档时打开；Writer 把文档蒸馏成原生 per-layer KV，预训练解码器作不变 Reader。行为蒸馏对齐 Full Recompute；在线仍走标准 cache-hit，不必改服务接口。",
    "D_key_results": [
        "三模型×四任务：相对 KV Packet 总体均值 micro-F1 0.53→0.60，逼近 Full Recompute 0.62",
        "12 个设置中 10 个高于 KV Packet；Qwen3 4B/8B 均值分别约 +0.10/+0.13",
        "Joint（边界+文档适应）总体均值 0.61，显示二者可互补",
    ],
    "E_industry_implications": [
        "高频复用的知识库/手册先离线编译成 KV，别每个问题都整段 prefill",
        "验收同时看 cache-hit 质量与离线编译成本，延迟单独比会骗人",
        "在线路径尽量保住标准 KV 命中接口，别轻易上辅助编码器改服务形态",
    ],
    "F_one_line_judgement": "这篇最适合反复检索同一批文档的 RAG/Agent：离线语义 KV 能逼近整段重算质量，但离线训练成本与跨域迁移仍是边界。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "PIC", "definition": "Position-Independent Caching：预先编译可复用文档 KV，再放到请求时位置并拼接。"},
        {"term": "SemPIC", "definition": "用可训练 Writer 编译语义化文档 KV，供不变 Reader 在标准缓存路径消费。"},
        {"term": "KV Packet", "definition": "主要学习可复用块边界状态的 PIC 基线。"},
        {"term": "Full Recompute", "definition": "对完整提示从头算 KV，质量上界对照。"},
        {"term": "KV Gradient Checkpointing", "definition": "反向时重算 Writer 中间激活，同时保留缓存 KV 梯度通路以省显存。"},
        {"term": "micro-F1", "definition": "语料级 token micro-F1，用于衡量缓存复用相对整段重算的任务质量。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：位置对齐 ≠ 上下文齐全",
            "body": "RoPE 重排只能修位置相位。文档在孤立编译时没见过后续邻居与指令，朴素拼接会上下文残缺。",
        },
        {
            "title": "为何要把适应从边界拉到整篇文档",
            "body": "诊断显示 KV Packet 明显压低近边界注意力偏差，但内部与任务级误差仍在。需要让文档表示本身离线可学。",
        },
        {
            "title": "为何不改在线 Reader",
            "body": "服务侧继续吃标准 KV、走 cache-hit。训练成本付在离线编译，在线路径保持不变，落地摩擦更小。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主增益",
                "论文证据": "总体均值 micro-F1：KV Packet 0.53 → SemPIC 0.60；Full Recompute 0.62。",
                "飞哥判断": "离线文档级适应已经逼近整段重算的大半收益。",
            },
            {
                "看什么": "覆盖面",
                "论文证据": "12 设置里 10 个高于 Packet；Qwen3 4B/8B 均值约 +0.10/+0.13。",
                "飞哥判断": "对主流开源解码器复用场景更友好。",
            },
            {
                "看什么": "互补空间",
                "论文证据": "Joint（边界+文档）总体 0.61，高于单用 SemPIC。",
                "飞哥判断": "边界修补与文档编译不是二选一。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "三模型×四任务；Llama MuSiQue 单点 Packet 更高。",
                "飞哥判断": "别当通用银弹；个别任务仍需 Joint/重算兜底。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（task-level corpus micro-F1）；§4–5 诊断与结果叙述。",
        "版本戳：arXiv:2607.28069v1 [cs.AI] 30 Jul 2026；ChatGPT 0731批次 #3（0803 顺延主发）。",
        "单位：Beihang University · State Key Laboratory of Complex & Critical Software Environment。",
        "证据覆盖：学习缓存相对 Packet/Full Recompute；离线训练成本与域迁移未充分展开。",
    ],
    "so_what": "说白了，文档 Agent 账单里最烫的那一段，常常是同一批长文在换指令后反复 prefill。SemPIC 把复用文档变成可落盘的语义 KV 资产。",
    "feige_view": "别再只优化「前缀能不能命中」。知识库更新完先离线编译一轮文档 KV，再验收 cache-hit 质量是否逼近整段重算。对照今日 SVR：一个省文档重算，一个省无效续写。",
    "limitations": [
        "不过，Writer 要离线训练与部署流水线，冷启动和文档变更成本不能假装没有。",
        "个别设置（如 Llama MuSiQue）边界方法仍可能更强，需任务级选型。",
        "跨域文档分布漂移时，语义缓存是否保持逼近 Full Recompute，还需外推验证。",
    ],
    "related_theme_picks": {
        "theme": "推理效率：少重算、少空转",
        "intro": "本篇讲文档 KV 复用；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.28457",
                "title_cn": "自验证自适应停算",
                "one_liner": "同日配对：续写预算也别平均撒。",
                "link": "https://arxiv.org/abs/2607.28457",
                "ready_date": "20260803",
            },
            {
                "arxiv_id": "2607.27415",
                "title_cn": "行动图正负价值记忆",
                "one_liner": "0801：少从零搜索，复用成败经验。",
                "link": "https://arxiv.org/abs/2607.27415",
                "ready_date": "20260801",
            },
            {
                "arxiv_id": "2607.27360",
                "title_cn": "盲区诊断自我演化",
                "one_liner": "0801：自我改进先学会主动找缺口。",
                "link": "https://arxiv.org/abs/2607.27360",
                "ready_date": "20260801",
            },
        ],
    },
    "target_audience": [
        "做 RAG / 文档 Agent / 长上下文服务的推理平台团队。",
        "关心 KV cache 命中率与 prefill 成本的 infra 同学。",
        "评估知识库复用资产化路线的产品与架构负责人。",
    ],
    "sales_use_cases": [
        "回应『前缀缓存已经够了』：先问文档是否常在变化指令/次序后复用。",
        "方案评审：要求看离线编译流水线、cache-hit 质量相对 Full Recompute 的缺口。",
        "成本沟通：把文档 KV 当可版本化资产，而不是每次请求的临时张量。",
    ],
    "objection_handling": [
        "客户说：『在线局部重算不行吗？』→ 回应：在线修补把算力塞回请求路径；SemPIC 把适应付在离线。",
        "客户说：『换更大上下文窗不就行？』→ 回应：窗口变大仍会为重复文档付 prefill；复用才是结构性省。",
    ],
    "copy_paste_lines": [
        "长文档别反复 prefill：先离线编译成语义 KV。",
        "相对 KV Packet：micro-F1 0.53→0.60，逼近整段重算 0.62。",
        "验收文档缓存：看命中质量，也看离线编译成本。",
    ],
    "key_quotes": [
        "mean micro-F1 over KV Packet from 0.53 to 0.60",
        "approaching Full Recompute at 0.62",
        "adaptation is confined to offline cache construction",
    ],
    "score_rationale": "SemPIC把文档级语义KV离线编译接到标准缓存接口，三模型四任务均值micro-F1 0.53→0.60逼近Full Recompute。Impact/Applicability/Evidence高；Novelty中高；Reusability略低因离线训练与域迁移成本。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "总体均值 micro-F1：KV Packet 0.53 → SemPIC 0.60，Full Recompute 0.62", "evidence": "Abstract + Table 1 narrative", "location": "Abstract / Table 1"},
            {"claim": "12 设置中 10 个高于 KV Packet；Qwen3 4B/8B 均值约 +0.10/+0.13", "evidence": "Table 1 discussion", "location": "§5 Table 1"},
            {"claim": "Joint（边界+文档）总体均值 0.61", "evidence": "Table 1 discussion", "location": "§5"},
            {"claim": "边界条件 PIC 仍留内部与任务级残差", "evidence": "§4 diagnostic", "location": "§4"},
            {"claim": "离线训练成本与跨域迁移仍是落地边界", "evidence": "Limitations discussion", "location": "F / Limitations"},
        ]
    },
}


SVR_RICH = {
    "intro_lead": "",
    "A_research_problem": "测试时算力常常平均撒：简单题浪费预算，难例又可能停太早。外部验证器难规模化；模型自己何时该停、何时该改，缺少可学控制器。",
    "B_core_contributions": [
        "把结构化自验证提升为测试时算力控制策略",
        "Joint Verdict–Confidence RL：解、验证与格式信号合成轨迹回报",
        "固定视野训练、自适应停算推理；训练不直接罚已用轮次",
    ],
    "C_method_framework": "每轮输出答案、Correct/Incorrect/Unsure 判定与置信度；仅当判定 Correct 且置信度过阈才停。用 GRPO 在固定视野轨迹上联合训练判定-置信；推理阶段不向策略暴露标准答案（oracle-free）。",
    "D_key_results": [
        "Qwen3.5-2B All-7 宏均准确率 0.563，平均仅 2.99 轮；相对骨干 +14.3 点",
        "相对最强非 oracle 多轮基线 Murphy +7.5 点；相对固定预算 oracle 参考 +4.4 点",
        "All-7 均 8.56k token，约等于 Maj@5 预算但更高分，并以约一半 token 逼近 Maj@10（0.564）",
    ],
    "E_industry_implications": [
        "推理预算看板要看实例级停算：轮次均值、过早停、过改率",
        "可验证任务可先把自验证信号接进控制器，别只靠统一 Best-of-N",
        "验收校准：低置信假阳浪费预算，过自信误答会卡死错误答案",
    ],
    "F_one_line_judgement": "这篇最适合需要自适应测试时算力的数学/可验证推理：内部判定能省轮次，但校准误差会直接变成预算误分配。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "SVR", "definition": "Self-Verifying Refinement：用自验证信号控制多轮精炼是否继续。"},
        {"term": "Verdict", "definition": "每轮离散正确性判定：Correct / Incorrect / Unsure。"},
        {"term": "Joint Verdict–Confidence RL", "definition": "把解题、自验证与格式分数合成轨迹回报，并约束置信度校准的多轮 RL。"},
        {"term": "Oracle-free（推理）", "definition": "精炼提示与停算不暴露标准答案；训练仍可用正确性构造奖励。"},
        {"term": "All-7", "definition": "七个数学推理基准的未加权宏平均。"},
        {"term": "GRPO", "definition": "Group Relative Policy Optimization，组内相对策略优化。"},
    ],
    "method_subsections": [
        {
            "title": "控制器：何时留下答案",
            "body": "不是轮次到了才停，而是判定 Correct 且置信度超阈才返回。Unsure/Incorrect 则带着自身验证继续改。",
        },
        {
            "title": "为何固定视野训练仍能自适应推理",
            "body": "训练轨迹固定最长轮次，回报不直接罚已用轮次；省算力出现在推理：停算规则可提前结束。",
        },
        {
            "title": "校准误差 = 分配误差",
            "body": "低估正确答会触发有害改写，高估错误答会过早停。自验证不是事后描述，而是预算控制器本身。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主指标",
                "论文证据": "All-7 Acc 0.563 @ 2.99 turns；相对骨干 +14.3 点。",
                "飞哥判断": "准确率与算力同步改善，不是靠堆轮次硬抬。",
            },
            {
                "看什么": "对照强度",
                "论文证据": "相对 Murphy +7.5 点；相对固定预算 oracle 参考 +4.4 点。",
                "飞哥判断": "完整系统对比下，自带停算信号更值钱。",
            },
            {
                "看什么": "相对多数投票",
                "论文证据": "8.56k token 优于 Maj@5（8.80k, 0.529）；以约一半 token 逼近 Maj@10（17.50k, 0.564）。",
                "飞哥判断": "自适应轨迹比均匀多采样更划算。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主结果在 Qwen3.5-2B 数学七基准；AIME/AMC 样本少。",
                "飞哥判断": "先当可验证域方案，开放生成别直接照搬。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table 1（All-7 / turns）；Table 2（Maj@k token）；§4 完整系统对比叙述。",
        "版本戳：arXiv:2607.28457v1；ChatGPT 0731批次 #4（0803 顺延主发）。",
        "单位：Sun Yat-sen University · Guangdong Key Laboratory of Big Data Analysis and Processing · X-Era AI Lab。",
        "证据覆盖：数学可验证域；开放域与校准稳健性仍待验证。",
    ],
    "so_what": "说白了，测试时算力不该平均撒。SVR 的机制是：把「判定×置信」接进停算门，实例级决定留下答案还是再改一轮，所以能用约 3 轮逼近多数投票一半代价的准确率。",
    "feige_view": "别把 Best-of-N 当成默认续费键。先给可验证任务接一个判定×置信的停算门：看板盯过早停和过改。对照今日 SemPIC：一个少重算文档，一个少空转推理。",
    "limitations": [
        "不过，校准误差会直接变成预算误分配：过度自信会锁死错答。",
        "主结果集中在 Qwen3.5-2B 与数学基准，开放域写作/工具任务尚未证明同等收益。",
        "AIME26/AMC23 样本偏少，细分排名不如 All-7 聚合稳健。",
    ],
    "related_theme_picks": {
        "theme": "推理效率：少重算、少空转",
        "intro": "本篇讲自适应停算；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.28069",
                "title_cn": "语义位置无关KV缓存",
                "one_liner": "同日配对：文档复用别反复 prefill。",
                "link": "https://arxiv.org/abs/2607.28069",
                "ready_date": "20260803",
            },
            {
                "arxiv_id": "2607.27415",
                "title_cn": "行动图正负价值记忆",
                "one_liner": "0801：搜索别从零开始。",
                "link": "https://arxiv.org/abs/2607.27415",
                "ready_date": "20260801",
            },
            {
                "arxiv_id": "2607.27360",
                "title_cn": "盲区诊断自我演化",
                "one_liner": "0801：自我改进先找未知缺口。",
                "link": "https://arxiv.org/abs/2607.27360",
                "ready_date": "20260801",
            },
        ],
    },
    "target_audience": [
        "做数学/代码等可验证推理服务的测试时算力团队。",
        "关心 Best-of-N / 多轮自改 ROI 的产品与评测同学。",
        "想把置信度从「展示」推进到「控制器」的对齐工程组。",
    ],
    "sales_use_cases": [
        "回应『再加采样就能涨』：先问有没有实例级停算与过改监控。",
        "方案评审：要求看判定/置信标签定义、阈值门与校准报表。",
        "成本沟通：用自适应轨迹对比 Maj@k 的准确率–token 前沿。",
    ],
    "objection_handling": [
        "客户说：『外部奖励模型当验证器不行吗？』→ 回应：外部通路难规模；SVR 把验证做成策略内生信号。",
        "客户说：『固定多轮更稳？』→ 回应：固定视野扫不到自适应优势；论文显示无单一共享停轮能匹配 SVR。",
    ],
    "copy_paste_lines": [
        "别给所有题同一预算：判定对、置信够再停。",
        "All-7：0.563 @ 2.99 轮；约一半 token 逼近 Maj@10。",
        "置信度别只展示——接到停算门上。",
    ],
    "key_quotes": [
        "All-7 macro-average accuracy of 0.563 with 2.99 inference turns",
        "outperforms the strongest non-oracle multi-turn baseline by 7.5 percentage points",
        "matches ... majority voting while consuming approximately half as many tokens",
    ],
    "score_rationale": "SVR把自验证做成测试时算力控制器，七基准0.563@2.99轮并逼近Maj@10一半token。Impact/Applicability/Evidence高；Novelty中高；Reusability略低因校准误差与域外推。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "All-7 Acc 0.563 @ 2.99 turns；相对骨干 +14.3 点", "evidence": "Abstract + Table 1", "location": "Abstract / Table 1"},
            {"claim": "相对 Murphy +7.5 点；相对固定预算 oracle 参考 +4.4 点", "evidence": "§4 complete-system comparison", "location": "§4"},
            {"claim": "All-7 8.56k token，优于 Maj@5，并以约一半 token 逼近 Maj@10", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "固定视野扫无单一共享停轮匹配自适应 SVR", "evidence": "§4 adaptive-inference analysis", "location": "§4"},
            {"claim": "校准误差会变成预算误分配；开放域外推未验证", "evidence": "Intro + Limitations", "location": "§1 / F"},
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
        "2607.28069",
        "sempic",
        SEMPIC_RICH,
        "长文档别反复prefill：SemPIC把复用文档编译成语义KV，micro-F1从0.53到0.60",
        "SemPIC把文档级KV离线编译成语义缓存，三模型×四任务逼近整段重算，适合RAG与文档Agent的重复上下文。",
    )
    enrich_one(
        "2607.28457",
        "svr",
        SVR_RICH,
        "别给所有题同一预算：SVR用自验证停算，七基准均值仅2.99轮、准确率0.563",
        "SVR把答案正确性判定和置信度做成停算信号，在七个数学基准上用约3轮拿到更高准确率并逼近多数投票一半代价。",
    )
    print("enriched sempic + svr")


if __name__ == "__main__":
    main()
