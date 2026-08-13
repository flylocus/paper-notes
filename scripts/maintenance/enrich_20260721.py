#!/usr/bin/env python3
"""One-off enrichment for 20260721 paper-notes payloads (Grok + arXiv; ChatGPT unavailable)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260721"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


CRAFT_RICH = {
    "A_research_problem": "评测通常只回答『模型现在怎么样』：任务分、排行榜、类别平均。对后训练团队更关键的第二个问题——『下一轮该补什么数据』——却长期欠账。弱分把多种失败混在一起：同一道题可能是漏了法定例外、算错现金流行项，或格式不合规。只说『法律弱』『金融弱』，无法决定该采哪类样本。CRAFT要回答：能否把任意rubric评测集，转成模型专属的弱能力诊断，并直接驱动定向微调数据生成？",
    "B_core_contributions": [
        "把rubric准则当作能力探针：每个prompt–准则对抽取一条去语境化的能力描述，聚合成层级能力树",
        "跨层动态选弱节点：不固定树深，按『弱点最清晰的粒度』选节点，并排除祖先/后代重叠",
        "诊断→合成SFT闭环：在与EvalTree/Random相同数据预算与微调协议下，证明准则级定向优于prompt级与随机采数",
    ],
    "C_method_framework": "CRAFT（Clustering Rubrics for Actionable Fine-Tuning）输入rubric数据集与目标模型，输出模型专属弱能力节点集合。流程：①扁平化prompt–准则对，用LLM为每条准则抽取能力描述；②层次聚类成能力树（实验中约六层，覆盖约2万对）；③用LLM-as-a-judge对目标模型打准则级pass/fail，向上聚合为节点通过率；④自顶向下跨层搜索弱节点（支持度>30准则，选中后屏蔽祖先后代）；⑤下游用弱节点条件化生成合成SFT数据。对比基线EvalTree（整prompt聚类）与Random（无树、无弱项定向）共享同一教师生成、数据预算、超参与评测协议，只差『如何选训练数据』。",
    "D_key_results": [
        "金融域（Table 2）：四模型全域平均全部第一；Qwen3-4B平均46.0 vs EvalTree 40.8 / Random 37.6；Llama-3.1-8B 42.5 vs 36.0 / 36.6",
        "法律域（Table 1）：四模型中三模型平均第一；Qwen3-4B 53.0（EvalTree 51.7 / Random 49.9）；Llama-3.1-8B 51.0（+2.8 / +4.1）；Qwen3-8B与EvalTree差0.6且方差带重叠",
        "诊断与评测分离：PRBench金融629题/10806准则、法律532题/9637准则仅用于建树；最终13项持出基准全部disjoint",
    ],
    "E_industry_implications": [
        "专业域后训练别再按排行榜盲刷：先建rubric能力树，把弱节点清单当成数据工单",
        "评测产品要从『打分器』升级为『诊断器』：输出应是可执行的弱能力集合，而不只是平均分",
        "金融/法律等高风险域优先投资准则级rubric资产——没有准则探针，定向改进无从下手",
    ],
    "F_one_line_judgement": "CRAFT把评测从打分器改成训练数据生成器：准则级能力树 + 跨层弱节点定向造SFT后，金融域四模型平均全第一，法律域三模型第一——说明『哪里弱』要下沉到rubric准则，而不是停在题目或大类。",
    "glossary": [
        {"term": "CRAFT", "definition": "Clustering Rubrics for Actionable Fine-Tuning：把rubric准则聚类成层级能力树，诊断弱能力并驱动定向微调数据生成。"},
        {"term": "Rubric / 评分准则", "definition": "把回答质量拆成可独立判定的显式要求（如『引用控制性法条』『先定位现金流行项再算比率』），可pass/fail打分。"},
        {"term": "EvalTree", "definition": "对照基线：在整条prompt上建能力树并选弱簇；CRAFT把粒度下沉到prompt–准则对。"},
        {"term": "PRBench", "definition": "专业域rubric评测集；本文用其金融/法律子集做诊断，持出基准与之完全分离。"},
        {"term": "跨层动态选弱节点", "definition": "不固定树深：按支持度与通过率阈值跨层搜索弱节点，选中后排除祖先与后代，避免重叠选择。"},
        {"term": "decoding-variance band", "definition": "同一检查点多次温度解码的均值±样本标准差区间；用来判断领先是否落在噪声带内。"},
    ],
    "method_subsections": [
        {
            "title": "准则级能力抽取：一题多探针",
            "body": "同一prompt可挂多条准则，分别测试不同技能。CRAFT把数据集压成prompt–准则对，用LLM为每对写出短的去语境化能力描述，让不同措辞、不同题目里的同类失败能聚到同一节点。",
        },
        {
            "title": "能力树打分与跨层弱节点选择",
            "body": "先对目标模型跑完全部诊断题，LLM-as-a-judge给准则级pass/fail；内部节点取子树平均通过率。选弱时要求支持度>30准则，自顶向下松弛阈值收集目标数量弱节点，并屏蔽祖先/后代，保证选中区域互不重叠。",
        },
        {
            "title": "弱节点→合成SFT：评测输出变成数据接口",
            "body": "诊断完成后，另一步用弱节点描述条件化生成合成训练样本（也可换人写）。实验里CRAFT/EvalTree/Random只差选数策略，教师生成、预算、SFT与评测协议完全对齐，因此增益可归因于『选什么数据』。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "金融域平均（Table 2）",
                "论文证据": "四模型全域平均全部第一。Qwen3-4B：CRAFT 46.0 ±1.4 vs EvalTree 40.8 / Random 37.6；Llama-3.1-8B：42.5 vs 36.0 / 36.6。",
                "飞哥判断": "金融侧领先最干净，说明准则级定向对数值推理/披露QA这类可拆准则的任务特别有效。",
            },
            {
                "看什么": "法律域平均（Table 1）",
                "论文证据": "三模型第一：Qwen3-4B 53.0（+1.3/+3.1）、Llama-3.1-8B 51.0（+2.8/+4.1）；Qwen3-8B落后EvalTree 0.6且方差带重叠。",
                "飞哥判断": "法律增益更『拼盘式』——看全域平均，不看单基准通杀；Qwen3-8B提醒不要神话任何选数法。",
            },
            {
                "看什么": "诊断规模",
                "论文证据": "PRBench金融629题/10806准则、法律532题/9637准则；能力树约覆盖20443对；持出13基准disjoint。",
                "飞哥判断": "诊断资产本身就是门槛：没有大规模准则库，这套闭环跑不起来。",
            },
            {
                "看什么": "对照设计",
                "论文证据": "CRAFT vs EvalTree vs Random共享同一数据预算、教师生成、SFT与评测协议，只差选数。",
                "飞哥判断": "这是这篇最硬的工程品格：比的是诊断粒度，不是偷偷加数据或换训练配方。",
            },
        ],
    },
    "source_notes": [
        "主结果：Table 1（legal）、Table 2（finance）；Figure 2可视化域平均领先幅度。",
        "投稿时间：2026-07-17 17:00 UTC；Grok 0721 #3，经arXiv title-phrase解析为2607.16122；ChatGPT当日不可用。",
        "单位：Scale AI（PDF首页；overrides写入）。",
        "证据边界：下游训练数据为合成；节点打分依赖LLM-as-a-judge；未报告人写数据替代时的成本与增益差。",
    ],
    "so_what": "说白了，排行榜告诉你模型『哪门课挂了』，但不告诉你该补哪本练习册。CRAFT把rubric准则当成能力探针，聚成树后再按弱节点造数据——评测输出直接变成数据工单。对企业后训练团队，这意味着：先投资准则级诊断资产，再谈刷分；否则你只是在用更贵的算力重复采已经会的题。",
    "feige_view": "三个可执行动作：①盘点现有评测——有没有可独立判定的准则，还是只有整题对错？没有准则就先补rubric，别急着上能力树；②把『弱节点清单』写进数据需求单，按节点采数/合成，而不是按benchmark名盲刷；③对比选数策略时锁死数据预算与训练配方，只改诊断粒度——否则你分不清是方法赢了还是多喂了数据。",
    "limitations": [
        "不过，诊断依赖LLM-as-a-judge的准则一致性；若裁判本身不稳定，能力树分数会被系统性噪声污染。",
        "不过，实验下游数据全是合成样本；换真人标注或更高成本数据时，准则级定向的相对优势需要再测。",
        "不过，建树与路由依赖Gemini等外部模型，并要求节点支持度足够（实验>30准则）——小rubric集或冷门域可能选不出稳定弱节点。",
    ],
    "related_theme_picks": {
        "theme": "评测诊断与后训练数据",
        "intro": "本篇讲「评测如何直接变成数据工单」；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.15263", "title_cn": "安全Agent评测该把成本当一等指标", "one_liner": "评测坐标轴要从分数扩展到成本；和CRAFT的『可行动诊断』同一条产品化路径。", "link": "https://arxiv.org/abs/2607.15263", "ready_date": "20260719"},
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "系统可观测性的另一面：SearchOS外化执行状态，CRAFT外化能力弱点。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
            {"arxiv_id": "2607.16097", "title_cn": "预训练到RL的联合缩放", "one_liner": "后训练算力怎么分；和『后训练数据怎么选』构成训练预算的一体两面。", "link": "https://arxiv.org/abs/2607.16097", "ready_date": "20260721"},
        ],
    },
    "target_audience": [
        "做专业域（金融/法律等）后训练与评测体系的数据/算法负责人。",
        "要把benchmark从排行榜升级成数据工单的评测产品经理。",
        "关注rubric强化学习、能力诊断与合成数据闭环的研究者。",
    ],
    "sales_use_cases": [
        "回应『我们benchmark很多但模型总在同一类题翻车』：用准则级诊断解释为何类别分不够指导采数。",
        "金融/法律模型迭代评审：用Table 1/2的对照设计论证『锁预算只改选数』的实验品格。",
        "评测平台售前：把能力树+弱节点清单包装成下一轮数据需求输出，而不只是分数看板。",
    ],
    "objection_handling": [
        "客户说：『我们没有PRBench这种大规模rubric。』→ 回应：先从高频失败题补准则资产；CRAFT的前提是准则探针，不是某个公开集本身。",
        "客户说：『EvalTree不也建树吗？』→ 回应：粒度不同——prompt树说『这类题弱』，准则树说『答案里哪条要求没满足』；金融域四模型平均全胜支持这一差别。",
    ],
    "copy_paste_lines": [
        "评测不该只报分，还要输出下一轮数据工单。",
        "弱在题目，还是弱在准则？粒度选错，采数就会空转。",
        "金融域四模型平均全第一，靠的是选对数据，不是偷偷加预算。",
    ],
    "key_quotes": [
        "Evaluations should do more than measure a model's current performance",
        "Diagnosing weaknesses at the level of rubric criteria... yields both a sharper picture... and measurably better models",
        "CRAFT achieves the strongest finance-domain average for all four models",
    ],
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "金融域四模型平均全部第一；Qwen3-4B 46.0 vs EvalTree 40.8 / Random 37.6", "evidence": "Table 2 domain averages", "location": "Table 2 / Section 6.3"},
            {"claim": "法律域三模型第一；Llama-3.1-8B 51.0（+2.8/+4.1）", "evidence": "Table 1 domain averages", "location": "Table 1 / Section 6.2"},
            {"claim": "PRBench诊断与13持出基准disjoint", "evidence": "Dataset selection / benchmarks section", "location": "Section 5.4 / 6.1"},
            {"claim": "F段限制：LLM-as-judge与合成数据边界", "evidence": "Method judge step + synthetic generation", "location": "Section 3.4 / 4"},
        ]
    },
}


PRE2POST_RICH = {
    "A_research_problem": "标准LLM管线是大规模预训练，再接SFT与可验证奖励RL。两边的算力叙事却常常脱节：一边强调把基座做强，一边强调用RL从环境反馈里『炼』出能力。结果两个基本问题悬空——预训练选择（模型规模、数据量）如何塑造后续RL回报？RL对继承策略究竟做了什么：只是锐化已有偏好，还是挖出近零概率的正确行为？真实互联网语料又太大、太杂，很难把行为归因到预训练还是RL。",
    "B_core_contributions": [
        "建立预训练–RL联合缩放：预训练损失预测post-RL性能水平，预训练token量与RL奖励曲线斜率近似线性相关（Pearson r=+0.84）",
        "按谜题难度分解RL机制：易题放大SFT已偏好的正确着法；难题挖出近零概率正确着法，也可能强化错误模式",
        "开源pre2post-chess模型/数据/代码，并在1B数学域复现同类预测模式",
    ],
    "C_method_framework": "用国际象棋做可控推理实验台，复现LLM式预训练→SFT→RL全链路：在人类棋谱上预训练5M–1B模型；用合成推理轨迹做SFT；在可验证奖励的棋谜上跑RL。系统扫描预训练算力与RL算力分配，拟合局部RL缩放，再把拟合参数连回预训练损失与token量。机制分析按谜题难度对比SFT与RL策略的着法分布。最后在1B语言模型的数学域用不同预训练token检查点复现『损失预测水平、token预测斜率』的模式。",
    "D_key_results": [
        "预训练token与RL斜率近似线性相关（Pearson r=+0.84）；预训练损失稳定预测给定RL算力下的post-RL水平",
        "固定总算力前沿上，RL算力占比随总预算上升（如20M模型约从5%升到32%）；起步太早、预训练不足时RL收益有限",
        "pass@1与pass@16行为分叉：RL稳定抬高pass@1，但对更大k的覆盖不一定同样有效；1B数学域复现同类预测模式",
    ],
    "E_industry_implications": [
        "训练预算别两段拍脑袋：先保证足够预训练暴露，再加大RL份额；弱检查点过早开RL往往不划算",
        "业务指标要拆开看pass@1与pass@k：RL常把『会做的题做得更稳』，不等于拓宽解空间",
        "难题/稀疏奖励场景要防错误模式被强化：需要扩正确解支持的方法，而不只是策略锐化",
    ],
    "F_one_line_judgement": "RL不是孤立的后训练魔法——预训练损失预测post-RL能到多高，预训练token量近似决定RL爬得多快；算力越大越该把份额让给RL，但必须先有够强的初始化。",
    "glossary": [
        {"term": "联合缩放律（joint pretraining–RL scaling）", "definition": "把post-RL性能写成可被预训练损失/token预测的函数，从而量化『算力该投预训练还是RL』。"},
        {"term": "Rref / BN,T", "definition": "局部RL缩放拟合参数：Rref近似参考算力下的奖励水平，BN,T近似每增加一个数量级RL算力的奖励增益（斜率）。"},
        {"term": "pass@1 / pass@k", "definition": "采样1次或k次命中正确解的概率；文中RL对pass@1更稳，对pass@16常更平坦甚至退步。"},
        {"term": "可验证奖励RL", "definition": "用可自动判定对错的环境反馈（棋谜对错、数学答案）做强化学习，而非纯人类偏好。"},
        {"term": "IsoFLOP / 算力前沿", "definition": "在固定总算力下扫描预训练与RL分配，取最优表现形成Pareto前沿。"},
        {"term": "pre2post-chess", "definition": "本文开源的象棋预训练→后训练实验资产（HF模型/数据 + GitHub代码）。"},
    ],
    "method_subsections": [
        {
            "title": "象棋可控管线：把归因问题变可测",
            "body": "棋盘动作空间清晰、引擎可逐步监督，避免真实语料里『行为来自预训练还是RL』说不清。管线刻意对齐LLM三阶段：人类棋谱预训练、合成推理轨迹SFT、可验证奖励RL。",
        },
        {
            "title": "从预训练属性预测RL曲线",
            "body": "对多次RL run拟合局部对数线性缩放，得到水平项与斜率项；再检验它们能否被预训练验证损失与token量预测。核心经验规律：损失预测能到多高，token量预测爬得多快。",
        },
        {
            "title": "机制：RL不是均匀锐化",
            "body": "按谜题难度对比SFT与RL策略：易题上RL放大SFT已偏好的正确着法；难题上会抬起近乎为零的正确着法概率，同时也可能强化错误模式——这解释了pass@1改善与pass@16不稳定可以共存。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "斜率 vs 预训练token",
                "论文证据": "BN,T与log10 T近似线性相关，Pearson r=+0.84；更多预训练token对应更快的RL提升。",
                "飞哥判断": "这是最能直接指导预算的一条：数据暴露不足时，RL曲线会『爬不动』。",
            },
            {
                "看什么": "水平 vs 预训练损失",
                "论文证据": "更低预训练验证损失对应更高post-RL Rref；随参考RL算力增大，拟合往往更紧。",
                "飞哥判断": "基座损失仍是后训练天花板的强先行指标，别只看SFT小测。",
            },
            {
                "看什么": "算力分配前沿",
                "论文证据": "固定总算力下，前沿上RL占比随预算上升（例：20M从约5%到约32%）；过早从弱检查点开RL收益有限。",
                "飞哥判断": "经验法则：先把初始化做够，再把增量预算更多给RL。",
            },
            {
                "看什么": "数学域外推",
                "论文证据": "1B模型、10B–200B预训练token检查点上，损失→水平、token→斜率的模式复现。",
                "飞哥判断": "方向可迁移，但外推边界仍窄——别直接当成超大通用LLM的配方表。",
            },
        ],
    },
    "source_notes": [
        "主结果：联合缩放与机制分析见正文Figures 2–3及结论段；数学域见图6。",
        "投稿时间：2026-07-17 16:31 UTC；Grok 0721 #1，arXiv id 2607.16097；作者含Pavel Izmailov等（非Grok最初猜测的单一隶属）。",
        "单位：NYU、Modal Labs、UCLA、UIUC、Columbia（PDF首页+overrides）。",
        "开源：huggingface.co/pavelslab-nyu/pre2post-chess ；github.com/pavelslab-nyu/pre2post-chess。",
        "证据边界：主实验台是象棋可控域；数学外推仅1B；pass@16与pass@1结论不可混用。",
    ],
    "so_what": "说白了，别再把预训练和RL当成两本互不往来的账。这篇用可控实验台说明：基座损失大致框定post-RL能到的高度，预训练数据量大致框定RL还能爬多快。预算越大，越该把增量份额给RL——但前提是初始化已经够强；从太弱的检查点硬开RL，常常是浪费。",
    "feige_view": "三个动作：①排期时同时画『预训练损失曲线』和『RL回报曲线』，用损失当是否开RL的门槛，而不是看日历；②业务验收拆开pass@1与pass@k，避免被pass@1上涨骗成『解空间变宽了』；③难题/工具Agent场景默认假设RL会强化错误模式，评估里加错误着法/错误工具调用的放大率，而不只报平均分。",
    "limitations": [
        "不过，主结论来自象棋可控域，动作与奖励结构远比开放域自然语言干净；迁移到真实网页语料/工具Agent时，定量系数不能直接照搬。",
        "不过，数学域验证主要在1B尺度；更大模型、更杂数据配比下，损失–水平与token–斜率关系是否保持线性仍未知。",
        "不过，RL改善pass@1不等于改善pass@16；若产品目标是多样正确解或探索覆盖，单纯加RL可能不够，甚至有害。",
    ],
    "related_theme_picks": {
        "theme": "后训练算力与机制",
        "intro": "本篇讲「预训练与RL怎么一起缩放」；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.16122", "title_cn": "评测诊断到定向微调", "one_liner": "算力分配之外，后训练数据该补什么——CRAFT给的是数据侧接口。", "link": "https://arxiv.org/abs/2607.16122", "ready_date": "20260721"},
            {"arxiv_id": "2607.14952", "title_cn": "LongStraw长上下文RL", "one_liner": "Agent长轨迹RL的工程瓶颈：固定GPU预算冲到2M+上下文。", "link": "https://arxiv.org/abs/2607.14952", "ready_date": "backlog"},
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "后训练之外的系统层：把执行状态外化，减少RL/搜索空转。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
        ],
    },
    "target_audience": [
        "负责大模型预训练/后训练算力排期与配方的训练负责人。",
        "做reasoning/Agent RL、需要解释『RL到底改了什么』的研究与工程团队。",
        "关注scaling law与训练科学可复现实验台的研究者。",
    ],
    "sales_use_cases": [
        "回应『RL可以弥补弱基座』：用过早开RL收益有限的前沿结果，推动先补预训练暴露。",
        "训练预算评审：用损失→水平、token→斜率两条规则做可讨论的分配框架。",
        "产品指标设计：用pass@1/pass@k分叉说服业务不要只盯单次正确率。",
    ],
    "objection_handling": [
        "客户说：『象棋结论跟我们业务无关。』→ 回应：象棋是归因实验台；数学1B复现说明模式可迁移，但系数要在你的域重估，不能直接抄百分比。",
        "客户说：『我们只看pass@1就够了。』→ 回应：论文显示RL可抬pass@1却不稳抬pass@16；若需要多样正确路径或探索，指标必须拆开。",
    ],
    "copy_paste_lines": [
        "预训练损失框高度，预训练token框爬升斜率。",
        "算力越大越该给RL，但别从太弱的检查点起步。",
        "RL不是均匀锐化：易题放大旧正确，难题也可能放大错误。",
    ],
    "key_quotes": [
        "the post-RL performance at given RL compute level is well-predicted from the pretraining loss",
        "slope of the RL reward curves improves approximately linearly with the pretraining tokens",
        "RL does not simply sharpen the SFT policy",
    ],
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "预训练token与RL斜率Pearson r=+0.84", "evidence": "Fig.3 middle / scaling analysis", "location": "Figure 3 / Section 3"},
            {"claim": "20M模型前沿RL占比约5%→32%", "evidence": "Fig.2 frontier labels", "location": "Figure 2 / Section 3.2"},
            {"claim": "1B数学域复现损失→水平、token→斜率", "evidence": "Fig.6 math domain", "location": "Figure 6"},
            {"claim": "F段限制：象棋代理域与pass@k分叉", "evidence": "Conclusions + mechanism discussion", "location": "Conclusions / Related Work"},
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
        "重要性 Impact": "看问题是否卡在真实训练/评测痛点，以及结论对产业预算与流程是否有直接影响。",
        "创新性 Novelty": "看方法组合是否有辨识度：是新的诊断/缩放接口，还是已知模块的常规堆叠。",
        "可验证性 Evidence": "看对照是否干净、数字是否可追溯，以及代理域/合成数据/裁判模型带来的外推折扣。",
        "产业可用性 Applicability": "看单位、开源、专业域设置与落地动作是否够具体，能否直接改排期或数据工单。",
        "可复用性 Reusability": "看资产（代码/数据/协议）与抽象（能力树、联合缩放）迁移到其他域时的摩擦。",
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
    # keep card in sync on affiliations/title_cn
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
        "2607.16122",
        "craft",
        CRAFT_RICH,
        "评测只告诉你哪里弱还不够：Scale AI的CRAFT把rubric聚类成能力树，金融域四模型平均全第一",
        "CRAFT把评测从打分器改成训练数据生成器：在准则级找弱能力，再定向造SFT数据；金融持出基准上四模型全域平均第一。",
    )
    enrich_one(
        "2607.16097",
        "pre2post",
        PRE2POST_RICH,
        "算力该砸预训练还是RL？NYU用象棋可控实验台给出联合缩放律：预训练损失预测post-RL上限",
        "这篇用象棋复现预训练→SFT→RL全链路：预训练损失预测post-RL水平，预训练token量近似决定RL上升斜率；算力越大，最优预算越该让给RL，但起步太早收益有限。",
    )
    print("enriched both")


if __name__ == "__main__":
    main()
