#!/usr/bin/env python3
"""One-off enrichment for 20260731 paper-notes payloads (ShadowEval + SkillBoost)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260731"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


SHADOW_RICH = {
    "intro_lead": "",
    "A_research_problem": "现有评测要么让Agent在窄指标上hill-climb，要么靠随机性高的盲审；都难回答——Agent能否推进真正开放的研究问题。",
    "B_core_contributions": [
        "提出「同题影子审稿」协议：未发表高质量论文的核心开放问题 + 原作者按会议标准打分",
        "完整释放专家评审、调查、仓库与Agent日志",
        "提炼跨案例、跨scaffold重复出现的失败模式"
    ],
    "C_method_framework": "从未发表NeurIPS投稿抽取核心开放问题；给前沿Agent六天墙钟、$3000级API与GPU预算、完整VM与联网；产出由原作者按会议标准审稿。",
    "D_key_results": [
        "Personas 2/6 Reject；TabPFN 1/6 Strong Reject",
        "预算常耗不足半（例约$1130/$3000）",
        "自审多轮从未 accept，却仍沿错误方向打补丁"
    ],
    "E_industry_implications": [
        "验收开放研究Agent时，不要把「能跑通实验」等同「能出可发表研究」",
        "看板要看：可发表门槛判断、死路回退、预算耗用、指令是否漂移",
        "把影子评测当作研发自动化第三类测量，与窄任务、盲审互补"
    ],
    "F_one_line_judgement": "这项工作证明「同题影子评测」能够检验完整开放研究能力，但没有证明 Agent 的总体科研自动化率。它适合评估假设选择、证据设计和死路回退，不适合替代 CUDA 优化、封闭科学 QA 等子任务评测。",
    "F_section_title": "F. 结论与边界",
    "failure_modes": {
        "title": "五类反复失败",
        "intro": "以论文 Abstract / 引言归纳为准，稳健性复现中仍成立：",
        "items": [
            "对可发表研究门槛判断不足——不清楚「何时算做完」",
            "面对研究设计缺陷时缺乏创造性响应",
            "无法从死路有效回退",
            "资源与时间分配缺乏研究策略",
            "长程执行中的指令漂移"
        ]
    },
    "glossary": [
        {
            "term": "Shadow evaluation",
            "definition": "让Agent接手未发表高质量论文的核心开放问题，并由原作者按审稿标准打分。"
        },
        {
            "term": "Open-ended AI research",
            "definition": "无法仅靠固定指标hill-climb的研究：假设选择、证据设计、何时推倒重来。"
        },
        {
            "term": "Publishable bar",
            "definition": "顶会可发表门槛。"
        },
        {
            "term": "Backtracking",
            "definition": "从无前途路线有效回退并换方向，而非局部修补死路。"
        },
        {
            "term": "Instruction drift",
            "definition": "长程执行中逐渐偏离原始研究目标与约束。"
        }
    ],
    "method_subsections": [
        {
            "title": "为什么要同题、未公开、原作者审",
            "body": "同题保证可比；未公开防止检索污染；原作者对同一问题最有资格判可发表门槛。三者分别控制对照有效性、答案泄漏与评审深度。"
        },
        {
            "title": "稳健性复现",
            "body": "主跑OpenClaw+Opus；再以Codex+GPT-5.6 Sol复跑，失败模式仍成立——说明瓶颈不只是单一scaffold偶然性。"
        }
    ],
    "result_table": {
        "columns": [
            "看什么",
            "论文证据",
            "飞哥判断"
        ],
        "rows": [
            {
                "看什么": "是否可发表",
                "论文证据": "Personas 2/6 Reject；TabPFN 1/6 Strong Reject。",
                "飞哥判断": "两案均为明确拒稿，且评审置信度高。"
            },
            {
                "看什么": "资源意识",
                "论文证据": "预算常耗不足半（例约$1130/$3000），且提前收工。",
                "飞哥判断": "会监控用量，却不会战略性分配时间与预算。"
            },
            {
                "看什么": "自审与回退",
                "论文证据": "多轮AI自审从未给出accept，却仍沿错误方向打补丁。",
                "飞哥判断": "会识别问题，却不能据此真正换方向。"
            }
        ]
    },
    "source_notes": [
        "主数字：Abstract；Table 1审稿分；§4.1–4.2；资源消耗图约$1130/$3000。",
        "五类失败：Abstract 列举；引言 §1 展开；§6 稳健性复现。",
        "版本戳：arXiv:2607.27191v1 [cs.AI] 29 Jul 2026；ChatGPT 0730批次 #2 / Grok #1。",
        "单位：Princeton University · UK AI Security Institute · Stanford 等；复现材料见 cruxevals.com。"
    ],
    "so_what": "说白了，风险不是 Agent 不会执行，而是组织误把工程产出当成研究突破。影子评测把测量从「任务是否完成」升级为「原作者是否认这是可发表研究」。",
    "feige_view": "真正该落地的是「双账本验收」：工程自动化看仓库完整性、实验复现率和执行效率；开放研究判断看问题选择、证据充分性、死路回退，以及领域专家是否认可其达到可发表门槛。和今日SkillBoost对照：一个问能力真不真，一个问改进稳不稳。",
    "limitations": [
        "不过，只有两个案例，且具体 scaffold、模型与计算预算会显著影响结果。",
        "不过，原作者评价专业但难以完全标准化。",
        "不过，测量的是完整研究任务，不等于否定某些子任务可自动化。"
    ],
    "related_theme_picks": {
        "theme": "Agent能力是否真实、改进是否稳定",
        "intro": "本篇讲开放研究判断是否够格；同线可对照：",
        "items": [
            {
                "arxiv_id": "2607.26643",
                "title_cn": "技能演化防过拟合",
                "one_liner": "同日配对：更新技能必须过回归关。",
                "link": "https://arxiv.org/abs/2607.26643",
                "ready_date": "20260731"
            },
            {
                "arxiv_id": "2607.25090",
                "title_cn": "分层展开子Agent",
                "one_liner": "长程结构：压缩战略、展开执行。",
                "link": "https://arxiv.org/abs/2607.25090",
                "ready_date": "20260730"
            },
            {
                "arxiv_id": "2607.21596",
                "title_cn": "可执行技能共演化",
                "one_liner": "成功工作流如何沉淀成可复用技能。",
                "link": "https://arxiv.org/abs/2607.21596",
                "ready_date": "20260727"
            }
        ]
    },
    "target_audience": [
        "评估AI R&D自动化与研究Agent路线图的团队。",
        "做科研助手、自动实验与论文Agent的产品与研究负责人。",
        "关心『工程能力≠研究品味』测量方法的治理/评测同学。"
    ],
    "sales_use_cases": [
        "回应「Agent已经会做研究了」：先问有没有原作者/领域专家按可发表标准审过。",
        "方案评审：要求看回退日志、预算耗用曲线、自审后是否换方向。",
        "路线图沟通：工程自动化与开放研究判断分开验收，不要混成一个KPI。"
    ],
    "objection_handling": [
        "客户说：『换更强模型就行？』→ 回应：稳健性复现换scaffold仍见同类失败，瓶颈在判断与回退。",
        "客户说：『两案太少？』→ 回应：同意；价值在方法与失败模式，不在总体率估计。"
    ],
    "copy_paste_lines": [
        "开放科研别只看写代码：影子评测两案均被原作者明确拒稿。",
        "Personas 2/6、TabPFN 1/6；预算常耗不足半。",
        "AI研究自动化，缺的不是执行流水线，而是可发表判断的验收标准。"
    ],
    "key_quotes": [
        "both papers were unambiguously rejected by the authors",
        "agents can do the engineering of AI research, but struggle with critical parts of the research lifecycle",
        "five recurring failure modes"
    ],
    "score_rationale": "Shadow evaluation用未发表顶会稿核心问题测Agent，并由原作者打分。两案工程可完成但明确拒稿（2/6与1/6）；五类失败可复现。Impact高、Novelty高；Evidence因仅两案中等；方法与产物可复用。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {
                "claim": "Personas Overall 2/6 Reject；TabPFN 1/6 Strong Reject",
                "evidence": "Table 1 + §4.1",
                "location": "Table 1 / §4.1"
            },
            {
                "claim": "API预算常耗不足50%（例约$1130/$3000）",
                "evidence": "resource spend figure / §4",
                "location": "Fig resource spend"
            },
            {
                "claim": "自审多轮从未 accept，却仍沿错误方向打补丁",
                "evidence": "§4 / Figure 3",
                "location": "§4"
            },
            {
                "claim": "五类失败：门槛判断、设计缺陷无创造性、死路回退、资源意识、指令漂移",
                "evidence": "Abstract + §1",
                "location": "Abstract"
            },
            {
                "claim": "Codex+GPT-5.6 Sol稳健性复现仍见同类失败",
                "evidence": "§6 robustness",
                "location": "§6"
            },
            {
                "claim": "F边界：两案/scaffold敏感；不等于子任务自动化率",
                "evidence": "§7 Limitations",
                "location": "Limitations"
            }
        ]
    }
}

SKILLBOOST_RICH = {
    # One Fact, One Place：核心论点只留 Hook / So What / 销售话术
    "intro_lead": "",
    "A_research_problem": "技能库越改越多，不等于越来越强。只报平均成功率，看不到「新案子修好、旧案子回退」；这对持续部署的 Agent Skills 是结构性风险，不是偶发 bug。",
    "B_core_contributions": [
        "把技能自我演化从「拟合当前轨迹」改写成带回归约束的搜索问题",
        "提出 SkillBoost 框架，实现「定位—探索—验证」闭环",
        "在 23 个模型—基准配置上验证，并展示跨 Agent 技能迁移",
    ],
    "C_method_framework": "把技能建成可编辑状态（组件坐标），每轮：执行收集失败 → 定位组件 → 生成修复候选 → 全量回测后按「有改进且回归有界」决定是否接受。",
    "D_key_results": [
        "23 个模型—基准配置上优于人工技能与 LLM 生成技能",
        "相对 No-skill，模型级增益约 +10.6 至 +28.4；Claude-opus-4-6 在 LiveMath/Spreadsheet 可达 +47.4/+32.5",
        "SkillOpt/Trace2Skill 出现大负泛化间隙；SkillBoost 将 ∆=Test−Train 压到接近零",
        "去掉验证门控掉点（BFCL 上 Claude 37.7→有门控 48.5）；跨模型迁移约 +0.7–14.3 点",
    ],
    "E_industry_implications": [
        "技能库更新必须加回归集与接受门控，不能只看失败集修了多少",
        "看板同时报：测试增益、Train-Test 间隙、回归案例数、技能体积变化",
        "先在工具调用 / 表格 / 数学等程序性任务试，再谈跨领域复用",
    ],
    "F_one_line_judgement": "这篇最适合可回测、程序性的技能更新：它证明回归门控能抑制技能过拟合，但跨领域复用、长期版本治理与验证成本，仍未给出完整答案。",
    "glossary": [
        {"term": "Skill overfitting", "definition": "技能在当前轨迹批次上变准，却在后续不同分布任务上掉点，并可能破坏旧能力。"},
        {"term": "SkillBoost", "definition": "带回归约束的技能自我演化框架。"},
        {"term": "Structured exploitation", "definition": "把失败归因到具体可编辑技能组件，而不是整份技能乱改。"},
        {"term": "Prior-guided exploration", "definition": "用 LLM 先验在定位后的组件空间生成多样修复候选。"},
        {"term": "Verified acceptance", "definition": "候选需带来改进，且对已解决案例的回归保持在约束内才提交。"},
        {"term": "Generalization gap ∆", "definition": "Test−Train；大负值表示过拟合。"},
    ],
    "method_subsections": [
        {
            "title": "机制：为何会过拟合",
            "body": "目标若只最小化当前轨迹批次损失，技能会记住短视模式；增益难迁移到 held-out，已解决案例也可能被改坏。",
        },
        {
            "title": "为什么要拆成三步",
            "body": "定位减少无关修改范围，探索避免只生成单一路径，验证则阻止局部收益以旧能力损伤为代价。三者分别控制编辑空间、候选多样性和版本风险。",
        },
        {
            "title": "门控案例",
            "body": "规则从 87 扩到 150 行：修了 20 案却破 23 案（净 −3），门控直接拒收；无门控会把局部修复误当成进步。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主增益",
                "论文证据": "模型级约 +10.6 至 +28.4；Claude LiveMath/Spreadsheet 可达 +47.4/+32.5。",
                "飞哥判断": "程序性约束强的任务，迭代优化比一次性写技能更稳。",
            },
            {
                "看什么": "过拟合对照",
                "论文证据": "SkillOpt/Trace2Skill 大负 ∆；SkillBoost 接近零。",
                "飞哥判断": "主证据不是「又涨了几分」，而是对照方法把 Train-Test 间隙拉开了。",
            },
            {
                "看什么": "门控消融",
                "论文证据": "BFCL 上 Claude 无门控 37.7→有门控 48.5。",
                "飞哥判断": "门控不是装饰：去掉它，分数会掉。",
            },
            {
                "看什么": "证据覆盖",
                "论文证据": "覆盖 23 个模型—基准配置，并含门控消融与技能迁移实验。",
                "飞哥判断": "证据链较完整，但尚不能直接证明长期、跨领域技能演化的稳定性。",
            },
        ],
    },
    "source_notes": [
        "主数字：Abstract；Table I主结果叙述；Table III过拟合；Table V门控消融；迁移§。",
        "版本戳：arXiv:2607.26643v1 [cs.AI] 29 Jul 2026；ChatGPT 0730批次 #1。",
        "单位：Zhejiang University · Alibaba Group。",
        "证据覆盖：23 配置 + 门控消融 + 迁移；长期跨领域稳定性仍待验证。",
    ],
    "so_what": "当 Agent Skills 开始被持续自动更新，真正的风险不再是某次修改失败，而是局部收益被误判为系统进步。SkillBoost 给出的关键启示，是把技能演化从「生成问题」升级为「版本治理问题」。",
    "feige_view": "别把回归当成又一项检查清单。真正该落地的是：把回归测试做成 Agent 持续学习的 CI/CD——技能 PR 不过闸，就不能合入线上技能库。和今日影子评测对照：一个问能力真不真，一个问改进稳不稳。",
    "limitations": [
        "不过，回归约束依赖有代表性的验证任务；未覆盖的能力仍可能被破坏。",
        "不过，生成并验证多个候选会增加环境执行成本。",
        "不过，迁移实验仍偏相似任务，跨领域复用与长期技能库版本治理尚未解决。",
    ],
    "related_theme_picks": {
        "theme": "Agent能力是否真实、改进是否稳定",
        "intro": "本篇讲技能更新如何防过拟合；同线可对照：",
        "items": [
            {"arxiv_id": "2607.27191", "title_cn": "开放科研影子评测", "one_liner": "同日配对：工程能做，研究判断仍拒稿。", "link": "https://arxiv.org/abs/2607.27191", "ready_date": "20260731"},
            {"arxiv_id": "2607.21596", "title_cn": "可执行技能共演化", "one_liner": "成功流程如何沉淀成可复用技能。", "link": "https://arxiv.org/abs/2607.21596", "ready_date": "20260727"},
            {"arxiv_id": "2607.25090", "title_cn": "分层展开子Agent", "one_liner": "长程结构：压缩战略、展开执行。", "link": "https://arxiv.org/abs/2607.25090", "ready_date": "20260730"},
        ],
    },
    "target_audience": [
        "做Agent Skills / 外部程序性记忆 / 技能库平台的团队。",
        "关心自我演化会不会破坏旧能力的工程与评测负责人。",
        "评估技能迁移与版本治理的产品同学。",
    ],
    "sales_use_cases": [
        "回应『技能库会自动越用越强』：先问有没有 Train-Test 间隙与回归闸。",
        "方案评审：技能 PR 必须附失败集收益与回归集损伤。",
        "成本沟通：多候选验证有执行成本，但比线上静默回退便宜。",
    ],
    "objection_handling": [
        "客户说：『多采点轨迹不就行？』→ 回应：目标若仍只拟合当前批次，根因不变。",
        "客户说：『门控会不会太保守？』→ 回应：无门控会接受净回归为负的膨胀规则。",
    ],
    "copy_paste_lines": [
        "技能别只追新成功：更新先过回归关。",
        "23 组配置上压过拟合，∆ 接近零。",
        "Agent 的自我改进，不只需要学习机制，还需要版本治理。",
    ],
    "key_quotes": [
        "mitigating Skill Overfitting",
        "23 model–benchmark configurations",
        "keeping the generalization gap near zero",
    ],
    "score_rationale": "SkillBoost把技能演化建成带回归约束的探索—利用搜索，在23个配置上优于人工/LLM技能，并将泛化间隙压到接近零。Impact高；Evidence高；Applicability/Reusability中高，跨领域与成本仍待验证。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "23 个模型—基准配置上优于人工/LLM 技能", "evidence": "Abstract + Table I narrative", "location": "Abstract / Table I"},
            {"claim": "模型级增益约 +10.6 至 +28.4；Claude LiveMath/Spreadsheet 可达 +47.4/+32.5", "evidence": "Main Results paragraph", "location": "§Experiments Main Results"},
            {"claim": "SkillBoost 将 ∆=Test−Train 压到接近零，对照方法大负间隙", "evidence": "Table III", "location": "Table III"},
            {"claim": "BFCL 上 Claude 无门控 37.7→有门控 48.5", "evidence": "Table V", "location": "Table V"},
            {"claim": "证据覆盖完整但不足以证明长期跨领域稳定性", "evidence": "Discussion + revised D04", "location": "D / Limitations"},
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
        "2607.27191",
        "shadow-eval",
        SHADOW_RICH,
        "开放科研别只看写代码：影子评测两案均被原作者明确拒稿",
        "前沿Agent能独立完成工程，但在开放研究问题上仍达不到顶会可发表标准。",
    )
    enrich_one(
        "2607.26643",
        "skillboost",
        SKILLBOOST_RICH,
        "技能别只追新成功：SkillBoost把回归界写进自我演化",
        "Agent技能库可以持续改，但每次局部优化都必须过回归关，否则旧能力会被悄悄拆掉。",
    )
    print("enriched shadow-eval + skillboost")


if __name__ == "__main__":
    main()
