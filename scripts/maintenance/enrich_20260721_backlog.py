#!/usr/bin/env python3
"""Rich-field enrichment for 20260721 backlog four (LongStraw / Muon / DSWorld / SciForge)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260721"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


LONGSTRAW = {
    "glossary": [
        {"term": "GRPO（Group Relative Policy Optimization）", "definition": "分组相对策略优化：同一prompt采样多条响应，用组内相对优势做RL更新；训练需对同一history下的多条响应打分并反传。"},
        {"term": "capture-once / replay-suffix", "definition": "共享prompt只做一次无自动微分前向（capture），只保留后续token需要的模型态，再逐条重放短响应分支（replay）并在其上建autograd图。"},
        {"term": "活跃训练图（live training graph）", "definition": "反向传播需要保留的计算图与中间态；LongStraw把它从『全prompt+全响应』压到单条响应分支，用replay时间换显存。"},
        {"term": "positions", "definition": "参与训练的token位置总数（prompt+响应×组大小）；文中以2.1M/4.46M positions衡量执行包线。"},
        {"term": "执行容量 vs 训练正确性", "definition": "执行容量=能否在显存内跑完前向/反向路径；训练正确性=梯度组合是否完整、能否真正收敛。本文明确只验证前者。"},
    ],
    "method_subsections": [
        {"title": "为什么长上下文RL卡显存", "body": "推理端逼近百万token，RL后训练却常停在256K。训练不同于推理：要对同一history下的多条响应打分并反传，二次注意力与长命周期反向态叠加，GPU显存成为扩上下文的主要瓶颈。"},
        {"title": "capture-once + suffix-replay", "body": "共享prompt先做一次无自动微分前向评估，只保留后续token所需的模型态；随后在autograd下逐条重放短响应分支，把活跃训练图从整条序列压成单分支。代价是额外replay时间，收益是显存大幅下降。"},
        {"title": "状态所有权与架构解剖", "body": "论文强调state lifetime与physical ownership是长上下文RL实际上限的关键。配合设备放置、整层checkpoint，在混合循环+全注意力的Qwen3.6-27B与压缩注意力MoE的GLM-5.2两种架构上分别实例化。"},
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {"看什么": "Qwen执行包线", "论文证据": "8×H20完成Qwen 2.1M positions的分组打分+响应反向；group size 2→8峰值显存仅+0.21GB。", "飞哥判断": "组大小几乎不吃显存，说明瓶颈确实被挪到了单分支replay上。"},
            {"看什么": "压力上限", "论文证据": "压力测试把执行包线扩到4.46M positions。", "飞哥判断": "这是能力上界演示，不代表该规模下训练收敛。"},
            {"看什么": "GLM端到端路径", "论文证据": "32×H20验证GLM-5.2全78层2.1M prompt端到端执行路径。", "飞哥判断": "跨架构可跑通，工程完成度不低。"},
            {"看什么": "证据边界", "论文证据": "作者声明当前只建立执行容量，captured prompt state detached，部分分布式前向/梯度组合路径未完成。", "飞哥判断": "这是最关键的一条：能跑≠训得对，选型别越读越激动。"},
        ],
    },
    "source_notes": [
        "主结果：Abstract与执行回执章节；2.1M/4.46M positions、+0.21GB、全78层均出自原文。",
        "投稿：2026-07-16 13:00 UTC；Grok 0721 #2；cs.LG/cs.DC。",
        "单位：MindLab + 复旦大学（PDF首页+overrides）；代码 github.com/MindLab-Research/longstraw。",
        "关键限制：作者自述实验建立execution capacity而非complete training correctness。",
    ],
    "so_what": "说白了，LongStraw把『长上下文RL跑不动』从一个『再买卡』问题，重新定义成『状态什么时候生、归谁管』的工程问题——共享prompt别反复建图，短分支逐条replay。它现在给的是一张能力证明：固定预算下能把执行推到2M+ token。但要提醒团队，论文自己划了红线：这是能跑，不是训得对。",
    "feige_view": "给做长轨迹Agent RL的团队三个动作：①先量一下你的活跃训练图到底在哪爆——是prompt前向还是响应反向；②评估capture-once/replay这类以时间换显存的方案时，先问清楚replay带来的墙钟代价；③别把『2M positions能跑通』直接写进训练承诺，等分布式梯度路径补齐、收敛验证出来再说。",
    "limitations": [
        "不过，作者明确当前实验只验证执行容量，captured prompt state是detached、部分分布式前向与梯度组合路径尚未完成——即没有端到端训练收敛证据。",
        "不过，capture-once+replay以额外replay时间换显存，长上下文下墙钟开销与吞吐代价论文披露有限。",
        "不过，方案强绑定具体架构解剖（Qwen3.6-27B/GLM-5.2）与显存所有权工程，迁移到其它架构仍需重做适配。",
    ],
    "related_theme_picks": {
        "theme": "长上下文与后训练系统",
        "intro": "本篇讲『长上下文RL怎么跑得起』；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.16097", "title_cn": "预训练到RL的联合缩放", "one_liner": "算力该给预训练还是RL；LongStraw解决的是RL那侧的显存可行性。", "link": "https://arxiv.org/abs/2607.16097", "ready_date": "20260721"},
            {"arxiv_id": "2607.16169", "title_cn": "Muon何时帮到agentic RL", "one_liner": "同为后训练侧研究：一个抠显存执行，一个抠优化器选择。", "link": "https://arxiv.org/abs/2607.16169", "ready_date": "20260721"},
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "都在讲状态管理：一个管搜索进度，一个管训练态生命周期。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
        ],
    },
    "target_audience": ["做长轨迹/长上下文Agent RL训练的基础设施团队。", "受限GPU预算、想探索长上下文后训练的中小团队。", "关注训练显存与执行栈工程的系统研究者。"],
    "sales_use_cases": ["回应『长上下文RL只能靠堆卡』：用固定预算2M+ positions说明状态工程的空间。", "训练栈选型评审：用execution-capacity红线区分能跑与训得对。", "中小团队方案：论证有限加速器下探索长上下文RL的可行路径。"],
    "objection_handling": [
        "客户说：『那我直接上LongStraw训2M上下文？』→ 回应：论文明确只验证执行容量，梯度组合路径未完，收敛性未证，先做小规模复验。",
        "客户说：『replay不是更慢吗？』→ 回应：这是以时间换显存的显式取舍；瓶颈在显存时才划算，需按你的墙钟预算评估。",
    ],
    "copy_paste_lines": ["长上下文RL卡的不是算力，是状态什么时候生、归谁管。", "能跑2M token，不等于训得对——作者自己划了红线。", "组大小2到8只多0.21GB，瓶颈已被挪走。"],
    "key_quotes": [
        "state lifetime and physical ownership are key determinants of the practical context limit of RL post-training",
        "establish execution capacity rather than complete training correctness",
        "Increasing the group size from 2 to 8 adds only 0.21 GB of peak allocated memory",
    ],
    "evidence_ledger_patch": {"claim_evidence": [
        {"claim": "8×H20跑Qwen 2.1M positions；group 2→8仅+0.21GB", "evidence": "Abstract + execution receipts", "location": "Abstract / Section 8"},
        {"claim": "压力测试扩到4.46M positions；GLM-5.2全78层2.1M端到端", "evidence": "Execution envelope", "location": "Abstract / Section 8"},
        {"claim": "只验证执行容量而非训练正确性", "evidence": "Self-declared correctness caveat", "location": "Abstract"},
        {"claim": "F段限制：detached state与未完成梯度路径", "evidence": "Author caveat", "location": "Abstract / Conclusions"},
    ]},
}


MUON = {
    "glossary": [
        {"term": "Muon", "definition": "用动量矩阵的近似谱归一化（Newton–Schulz迭代）替代Adam系逐元素自适应缩放的优化器；预训练可用约52%FLOPs追平AdamW。"},
        {"term": "advantage estimator", "definition": "优势估计器：决定credit assignment结构。GRPO用episode级，GiGPO叠加step级，GraphGPO聚合成状态转移图。"},
        {"term": "GiGPO", "definition": "Group-in-Group Policy Optimization：在episode级优势外，对跨轨迹重复锚点状态的动作分组补一层step级优势。"},
        {"term": "ALFWorld", "definition": "长程、稀疏奖励的文本具身任务环境；仅任务成功给正终止奖励，非法动作有小惩罚。"},
        {"term": "RLVR", "definition": "可验证奖励强化学习；已有工作报告vanilla Muon在单轮RLVR/GRPO上失败。"},
    ],
    "method_subsections": [
        {"title": "为什么怀疑Muon不适合RL", "body": "Muon在预训练很能打，但作者们自己就把『能否迁移到RL后训练』列为open question。已有证据混杂：NeMo RL报告minor改进，也有工作报告vanilla Muon在GRPO式目标上失败，归因于谱白化放大低信噪策略梯度的噪声尾部。负面证据集中在单轮、outcome-only优势估计。"},
        {"title": "受控对比设计", "body": "在ALFWorld上用Qwen2.5-0.5B-Instruct做单seed匹配对比：固定所有非优化器设置，只换优化器/学习率。Muon只作用于2D隐藏权重矩阵，非矩阵参数仍用AdamW；跨GRPO/GiGPO/GraphGPO三种credit assignment结构比较。"},
        {"title": "核心猜想：credit质量与弱方向", "body": "Muon近似极因子更新，只有当弱方向符号可靠时才有用。作者猜想GiGPO的锚点状态对比、GraphGPO的图聚合能改善部分维度信噪，从而让Muon的谱归一化落到有用方向——但明确这是toy scaling，未测梯度SNR。"},
    ],
    "result_table": {
        "columns": ["配置", "AdamW→Muon成功率", "飞哥判断"],
        "rows": [
            {"配置": "GiGPO（只隐藏权重）", "AdamW→Muon成功率": "final-window 0.290→0.546（+0.255，+88%）", "飞哥判断": "最亮眼的一格，但也最需要多seed复验。"},
            {"配置": "GRPO @3e-5", "AdamW→Muon成功率": "0.161→0.268（+0.107）", "飞哥判断": "episode级优势下也有正增益，反驳『Muon必然崩』。"},
            {"配置": "GraphGPO @1e-5", "AdamW→Muon成功率": "0.810→0.901；AUC 0.399→0.556；提前30/60更新到0.5/0.75", "飞哥判断": "强基线上仍有收敛加速，信号方向一致。"},
            {"配置": "证据规模", "AdamW→Muon成功率": "单seed / Qwen2.5-0.5B / 仅ALFWorld", "飞哥判断": "exploratory定性，别当定量结论外推。"},
        ],
    },
    "source_notes": [
        "主结果：Abstract与Table 1；成功率、AUC、提前更新数均出自原文。",
        "投稿：2026-07-17 17:49 UTC；Grok 0721 backlog；cs.LG/cs.AI。",
        "单位：人大高瓴 + 中科院计算所/自动化所 + Duke + 浙大 + 独立研究者（PDF首页）。",
        "关键限制：作者自述exploratory，单seed，多seed与跨任务open，未测梯度SNR。",
    ],
    "so_what": "说白了，『Muon能不能接RL』这个问题问错了粒度——真正的变量是你的advantage estimator。GiGPO这种带step级credit的结构下，Muon能把成功率从0.29拉到0.55；但这还是0.5B、单任务、单seed的探索性信号。对工程团队，价值是提供一个假设方向，不是一张可以照抄的配方表。",
    "feige_view": "三个动作：①想在RL里试Muon，先看你的credit assignment结构，episode-only上风险更高；②Muon与AdamW学习率不可直接比较（矩阵形状缩放不同），务必各自调；③把这篇当假设来源而非结论——上生产前自己补多seed、跨任务、更大模型的复验。",
    "limitations": [
        "不过，全部结论基于单seed对比，成功率在采样验证下本就波动，多seed稳健性未知。",
        "不过，仅在Qwen2.5-0.5B与ALFWorld单任务上验证，规模与任务覆盖窄，跨任务/跨规模外推证据缺失。",
        "不过，核心机制（弱方向信噪改善）是猜想+toy scaling，作者未实测梯度SNR或更新对齐。",
    ],
    "related_theme_picks": {
        "theme": "后训练优化与RL机制",
        "intro": "本篇讲『优化器×credit assignment』；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.16097", "title_cn": "预训练到RL的联合缩放", "one_liner": "同样研究RL对策略做了什么，一个看优化器一个看预训练。", "link": "https://arxiv.org/abs/2607.16097", "ready_date": "20260721"},
            {"arxiv_id": "2607.14952", "title_cn": "LongStraw长上下文RL", "one_liner": "后训练侧的另一半：一个抠优化器，一个抠显存执行。", "link": "https://arxiv.org/abs/2607.14952", "ready_date": "20260721"},
            {"arxiv_id": "2607.16122", "title_cn": "评测诊断到定向微调", "one_liner": "后训练要选对数据，也要选对优化器与credit结构。", "link": "https://arxiv.org/abs/2607.16122", "ready_date": "20260721"},
        ],
    },
    "target_audience": ["做RL后训练优化器/算法选型的研究与工程团队。", "关注agentic RL credit assignment的研究者。", "想复现Muon×RL、需要谨慎外推的实践者。"],
    "sales_use_cases": ["回应『Muon不能用于RL』：用GiGPO +88%说明取决于credit结构。", "优化器选型讨论：强调advantage estimator是关键调节变量。", "研究选题：把『优化器×credit×学习率联合』作为待验证方向。"],
    "objection_handling": [
        "客户说：『+88%那我上Muon。』→ 回应：单seed/0.5B/单任务的探索性数字，先做多seed跨任务复验。",
        "客户说：『之前不是说Muon在RL会崩？』→ 回应：负面证据集中在单轮RLVR+episode-only；换成带step级credit的GiGPO结果不同。",
    ],
    "copy_paste_lines": ["Muon能不能接RL，先看你的advantage estimator。", "GiGPO下0.29→0.55，但这是探索性信号不是定论。", "优化器、credit assignment、学习率要一起调。"],
    "key_quotes": [
        "applying Muon only to hidden weight matrices raises final-window validation success from 0.290 to 0.546",
        "The effect depends on the advantage estimator and learning rate",
        "Multi-seed and cross-task validation remain open",
    ],
    "evidence_ledger_patch": {"claim_evidence": [
        {"claim": "GiGPO下Muon 0.290→0.546（+88%）", "evidence": "Abstract + Table 1", "location": "Abstract / Table 1"},
        {"claim": "GRPO 0.161→0.268；GraphGPO 0.810→0.901，AUC 0.399→0.556", "evidence": "Table 1", "location": "Table 1"},
        {"claim": "效果依赖advantage estimator与学习率", "evidence": "Abstract claim", "location": "Abstract"},
        {"claim": "F段限制：单seed/单任务/exploratory", "evidence": "Author caveat", "location": "Abstract"},
    ]},
}


DSWORLD = {
    "glossary": [
        {"term": "Data Science World Model", "definition": "数据科学世界模型：条件于当前workflow状态与候选操作，预测环境状态转移，从而在昂贵真执行前预判效果。"},
        {"term": "成本感知路由（cost-aware routing）", "definition": "按操作代价决定走真执行还是LLM模拟：轻量操作真跑，昂贵操作交模拟器，兼顾效率与准确。"},
        {"term": "Reflective World Model Optimization", "definition": "反思式世界模型优化：SFT后接误差感知RL，用rollout组内奖励标准化提升转移预测质量。"},
        {"term": "转移预测（transition prediction）", "definition": "预测执行某数据科学操作后环境状态如何变化，是世界模型的核心评测任务。"},
        {"term": "MLE-Bench Lite", "definition": "机器学习工程任务基准的轻量版；本文用它评估DSWorld作为自主数据科学Agent环境模拟器的价值。"},
    ],
    "method_subsections": [
        {"title": "痛点：数据科学Agent贵在真执行", "body": "自主数据科学Agent能力不弱，但依赖试错式workflow，训练和推理都要反复真执行、算力昂贵。DSWorld的出发点是：能不能在昂贵执行前预判操作效果，从而少跑几次真的。"},
        {"title": "混合执行-模拟 + 成本感知路由", "body": "框架含结构化状态构建、成本感知路由、轻量真执行与LLM模拟器。轻量操作直接真跑保证准确，昂贵操作交模拟器省算力，通过路由在效率与准确间取平衡。"},
        {"title": "两阶段后训练", "body": "先用8K转移轨迹做SFT，再用Reflective World Model Optimization做误差感知RL：每样本多次rollout，用组内奖励均值/标准差归一化，并对路由错误加robust处理，提升转移预测。数据侧覆盖60K真实表格多域环境。"},
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {"看什么": "转移预测", "论文证据": "均值超最强LLM基线o4-mini 35.6%；子任务分别+33.4/57.6/71.5/50.5%。", "飞哥判断": "在执行相关任务上提升最大，正是世界模型该赢的地方。"},
            {"看什么": "训练提速", "论文证据": "作为环境模拟器把RL-based Agent训练提速约14×。", "飞哥判断": "同预算能多跑RL迭代，直接压缩调优周期。"},
            {"看什么": "推理提速", "论文证据": "search-based推理提速约3-6×且保持竞争力。", "飞哥判断": "效率提升不是以明显掉分为代价，性价比可观。"},
            {"看什么": "评测覆盖", "论文证据": "Predict-before-Execute + 自建540评测任务 + MLE-Bench Lite；代码开源。", "飞哥判断": "有公开基准也有自建集，自建部分需注意口径。"},
        ],
    },
    "source_notes": [
        "主结果：Abstract、Table 1/2；35.6%、14×、3-6×均出自原文。",
        "投稿：2026-07-17 12:14 UTC；Grok 0721 backlog；cs.AI。",
        "单位：香港科技大学（广州）（PDF首页）；代码 anonymous.4open.science/r/DSWorld。",
        "证据边界：部分基准为自建540任务；主力模型规模以8B为主；代码为匿名仓。",
    ],
    "so_what": "说白了，数据科学Agent最烧钱的不是想法，是反复真执行来试错。DSWorld的思路很直接：先用世界模型预判操作效果，昂贵的交模拟、轻量的真跑，把RL训练提速约14×。对做AutoML/数据科学Agent的团队，这等于在执行层前面加了一层『先想再做』的缓存。",
    "feige_view": "三个动作：①盘点你的Agent哪些操作最贵，优先给这些操作接世界模型预判；②借鉴成本感知路由——别一刀切全真跑或全模拟；③自建评测集的数字要看构造口径，落地前用自己的任务分布复测那14×是否成立。",
    "limitations": [
        "不过，部分结论依赖自建的540评测任务与转移预测口径，跨团队可比性需按其定义复核。",
        "不过，主力实验以8B级模型与特定数据科学操作空间为主，迁移到更大模型或其它Agent域的增益未充分验证。",
        "不过，LLM模拟器替代真执行本身会引入模拟误差，成本感知路由的错判代价论文披露有限。",
    ],
    "related_theme_picks": {
        "theme": "Agent效率与世界模型",
        "intro": "本篇讲『执行前先预判』；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "都在减少无效执行：一个外化搜索状态，一个预判操作效果。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
            {"arxiv_id": "2607.14952", "title_cn": "LongStraw长上下文RL", "one_liner": "Agent训练侧的效率工程：一个抠显存，一个抠真执行次数。", "link": "https://arxiv.org/abs/2607.14952", "ready_date": "20260721"},
            {"arxiv_id": "2607.16038", "title_cn": "SciForge科研工作台", "one_liner": "都面向真实科研/数据科学落地，一个建状态一个省执行。", "link": "https://arxiv.org/abs/2607.16038", "ready_date": "20260721"},
        ],
    },
    "target_audience": ["做数据科学/AutoML自主Agent的产品与工程团队。", "关注Agent训练/推理效率、世界模型的研究者。", "受算力预算约束、想缩短Agent调优周期的团队。"],
    "sales_use_cases": ["回应『数据科学Agent太慢太贵』：用14×训练提速说明世界模型预判的价值。", "效率方案评审：用成本感知路由框架审计现有真执行占比。", "转移预测能力论证：用超基线35.6%说明预判准确性。"],
    "objection_handling": [
        "客户说：『模拟器会不会预测不准？』→ 回应：成本感知路由让轻量操作真跑、昂贵操作才模拟，且转移预测已超最强基线35.6%。",
        "客户说：『14×是不是特例？』→ 回应：数字来自其评测口径，落地前用自己任务分布复测，方向是减少昂贵真执行。",
    ],
    "copy_paste_lines": ["数据科学Agent的贵，贵在反复真执行。", "先用世界模型预判效果，再决定要不要真跑。", "转移预测超最强基线35.6%，RL训练提速约14×。"],
    "key_quotes": [
        "predicting environment state transitions conditioned on current workflow states and candidate operations",
        "accelerates RL-based agent training by approximately 14x",
        "outperforms the strongest LLM baseline by 35.6% on transition prediction tasks",
    ],
    "evidence_ledger_patch": {"claim_evidence": [
        {"claim": "转移预测超最强基线o4-mini 35.6%", "evidence": "Abstract + Table 1", "location": "Abstract / Table 1"},
        {"claim": "RL训练提速约14×、搜索推理约3-6×", "evidence": "Abstract + Table 2", "location": "Abstract / Table 2"},
        {"claim": "8K转移轨迹 + 60K真实表格 + Reflective World Model Optimization", "evidence": "Method + dataset", "location": "Section 3-4"},
        {"claim": "F段限制：自建评测/8B规模/模拟误差", "evidence": "Benchmarks + method", "location": "Section 5"},
    ]},
}


SCIFORGE = {
    "glossary": [
        {"term": "研究状态（research state）", "definition": "把科学对象、Agent动作、人类决策、证据链组织成一个连贯、可审计、可跨会话延续的持久环境，而非session级对话。"},
        {"term": "translate-then-reason", "definition": "多模态科学输入先经领域翻译器（如Esm2Text/Prot2Text/BioT5+/C2S）转成结构化专家观察，再交主Agent推理；翻译输出是证据候选而非既定事实。"},
        {"term": "Evidence-DAG", "definition": "证据有向无环图：把结论连回支持/反驳边、出处链与审计指标，每个agent动作挂上软件版本、参数、环境、随机种子。"},
        {"term": "Scientific Model Router", "definition": "科学模型路由：按对象与任务把请求分发到合适的模型/翻译器，而非绑定单一模型提供商。"},
        {"term": "决策治理（decision governance）", "definition": "目标域的review gate与多角色审批，把科研目标、审批、跨会话交接、证据评审做成可治理流程。"},
    ],
    "method_subsections": [
        {"title": "瓶颈：缺可审计研究状态", "body": "科研跨越论文、代码、数据、科学文件格式、模型输出、图表、手稿、团队决策等异构对象，这些对象彼此依赖。通用助手很少把它们保存成连贯可审计的研究状态——瓶颈已从『模型/工具可及』转向『缺持久环境』。"},
        {"title": "五支柱架构", "body": "①目标域决策治理（review gate+共享评审面）；②translate-then-reason多模态输入；③Evidence-DAG证据治理；④协作团队科研（多角色决策、跨会话交接）；⑤真实应用场景。GUI留给人类判断，检索/解析/路由/执行/绘图/写作/演示作为模块化Agent服务。"},
        {"title": "核心组件与形态", "body": "薄交互层 + 上下文研究能力模式 + Agent Runtime与工作流引擎 + Evidence-DAG审计sidecar + Scientific Model Router；本地优先，桌面应用为主、支持移动端监督。开源于GitHub AGI4Sci/SciForge。"},
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {"看什么": "五支柱", "论文证据": "决策治理 / translate-then-reason / 证据治理 / 团队协作 / 真实场景。", "飞哥判断": "把『研究状态』拆成可落地的五块，方向清楚。"},
            {"看什么": "证据治理", "论文证据": "Evidence-DAG/Project-DAG把结论连回出处链，agent动作挂软件版本/参数/环境/随机种子。", "飞哥判断": "这是最有迁移价值的一块，尤其对高合规场景。"},
            {"看什么": "案例", "论文证据": "八个端到端案例：基因发现、de novo蛋白设计、分子优化、genome-to-BGC等多日agentic科研冲刺。", "飞哥判断": "覆盖面广，但属演示而非量化benchmark。"},
            {"看什么": "证据形态", "论文证据": "以架构+案例+类别级对比表为主，缺量化benchmark；论文部分由AI撰写、人类核验。", "飞哥判断": "系统论文常态，判断价值看设计而非跑分。"},
        ],
    },
    "source_notes": [
        "主结果：Abstract、五支柱与对比表（Table 1类别级）；八个案例出自原文。",
        "投稿：2026-07-17 15:13 UTC；Grok 0721 backlog；cs.AI。",
        "单位：上海人工智能实验室 SciForge Team（PDF首页+overrides）；开源 github.com/AGI4Sci/SciForge。",
        "证据边界：以架构与案例演示为主，无量化benchmark/失败率实测；论文由DeepSeek-v4-pro撰写、人类核验。",
    ],
    "so_what": "说白了，科研AI现在缺的不是又一个会写代码的模型，而是一个能把对象、动作、决策、证据串成可审计状态的环境。SciForge把这件事做成工作台：Evidence-DAG让每个结论都能顺着出处链查回去。对做研发/科研平台的团队，最值得抄的是这套证据治理，而不是整个桌面应用。",
    "feige_view": "三个动作：①先问自己的科研/研发流程有没有『可审计状态』，还是只有一堆散落文件和对话；②把Evidence-DAG理念落到自己的高合规场景——结论连回数据/脚本/参数/人类审批；③别被八个案例带节奏，系统论文要看架构是否结构化解决问题，而不是演示多炫。",
    "limitations": [
        "不过，论文以架构描述与八个案例演示、类别级对比表为主，缺量化benchmark与失败率实测，难与同类系统做硬指标对比。",
        "不过，团队协作等部分能力仍是planned/future release，当前完成度以单机桌面应用为主。",
        "不过，论文本身由AI（DeepSeek-v4-pro）撰写、人类核验，作为系统设计陈述阅读，其效果主张仍待第三方复现。",
    ],
    "related_theme_picks": {
        "theme": "Agent状态与证据治理",
        "intro": "本篇讲『把科研做成可审计状态』；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.15257", "title_cn": "搜索Agent状态外化", "one_liner": "同一母题：一个外化搜索状态，一个外化研究状态与证据。", "link": "https://arxiv.org/abs/2607.15257", "ready_date": "20260720"},
            {"arxiv_id": "2607.15901", "title_cn": "数据科学世界模型", "one_liner": "都面向真实科研/数据科学落地，一个建状态一个省执行。", "link": "https://arxiv.org/abs/2607.15901", "ready_date": "20260721"},
            {"arxiv_id": "2607.16122", "title_cn": "评测诊断到定向微调", "one_liner": "证据治理的另一面：把评测结论也变成可追溯的行动。", "link": "https://arxiv.org/abs/2607.16122", "ready_date": "20260721"},
        ],
    },
    "target_audience": ["做科研/研发平台、需要可审计流程的团队。", "药研/生信等高合规、多角色协作的科研组织。", "关注Agent状态管理与证据治理的架构师与研究者。"],
    "sales_use_cases": ["回应『再接个大模型就够了』：用『缺可审计研究状态』说明瓶颈已转移。", "高合规场景方案：用Evidence-DAG论证结论可追溯到出处与审批。", "科研平台评审：用五支柱审计现有系统缺哪一块。"],
    "objection_handling": [
        "客户说：『这不就是又一个AI科研助手？』→ 回应：核心差异是把研究状态与证据链做成一等设施，而非围绕单一模型封装。",
        "客户说：『没有benchmark怎么信？』→ 回应：系统论文价值在架构与治理设计；量化对比确是其短板，落地前建议自建评测。",
    ],
    "copy_paste_lines": ["科研AI的瓶颈已从模型可及，转向缺可审计研究状态。", "Evidence-DAG让每个结论都能顺着出处链查回去。", "值得抄的是证据治理，不是整个桌面应用。"],
    "key_quotes": [
        "the central bottleneck is no longer only access to models or tools, but the lack of a persistent environment",
        "linking claims to provenance chains and audit findings",
        "Translator output is an evidence candidate, not a verified fact; the human remains responsible for judgment",
    ],
    "evidence_ledger_patch": {"claim_evidence": [
        {"claim": "五支柱：决策治理/translate-then-reason/证据治理/团队协作/真实场景", "evidence": "Abstract + contributions", "location": "Abstract / Section 1.2"},
        {"claim": "Evidence-DAG把结论连回出处链与审计", "evidence": "Evidence governance", "location": "Section 1.2 / 3"},
        {"claim": "八个端到端案例（基因/蛋白/分子/BGC）", "evidence": "Real-world scenarios", "location": "Abstract"},
        {"claim": "F段限制：无量化benchmark、AI撰写", "evidence": "Paper form", "location": "Front matter / Related Work"},
    ]},
}


def distinct_score_detail(dims, reason):
    values = [d["value"] for d in dims]
    hi, lo = max(values), min(values)
    per = {
        "重要性 Impact": "看问题是否卡在真实痛点，结论对产业是否有直接影响。",
        "创新性 Novelty": "看方法组合是否有辨识度，而非已知模块的常规堆叠。",
        "可验证性 Evidence": "看对照是否干净、数字是否可追溯，以及代理域/单seed/案例演示带来的折扣。",
        "产业可用性 Applicability": "看单位、开源、场景设置与落地动作是否够具体。",
        "可复用性 Reusability": "看资产与抽象迁移到其它场景的摩擦。",
    }
    out = []
    for d in dims:
        role = "highest" if d["value"] == hi else ("lowest" if d["value"] == lo else "middle")
        prefix = {"highest": "最高维，本篇最强判断依据集中在此。", "lowest": "最低维，是评分上限的主要约束，外推需额外验证。", "middle": "中间维，有明确支撑但非最突出差异点。"}[role]
        out.append({"label": d["label"], "value": d["value"], "role": role, "rationale": f"{prefix} {per.get(d['label'],'')} 总体依据：{reason}"})
    return {"schema_version": 1, "score_range": round(hi - lo, 1), "highest_dimensions": [d["label"] for d in dims if d["value"] == hi], "lowest_dimensions": [d["label"] for d in dims if d["value"] == lo], "dimension_rationales": out}


JOBS = [
    ("2607.14952", "longstraw", LONGSTRAW,
     "长上下文RL训练卡在256K？LongStraw用capture-once+分支replay，固定GPU预算下把GRPO推到2M+ token",
     "LongStraw把长上下文RL的显存瓶颈拆成状态生命周期问题：共享prompt只前向一次、逐条replay短响应分支，8×H20跑到2.1M positions；但作者明确目前只验证执行容量，未证明完整训练正确性。"),
    ("2607.16169", "muon", MUON,
     "Muon能不能用于RL后训练？人大团队：在ALFWorld上只对隐藏权重用Muon，GiGPO成功率从0.29冲到0.55",
     "Muon在RL后训练一直评价不一：这篇在稀疏奖励agentic RL上发现，Muon是否有用强依赖advantage estimator——GiGPO下+88%，但单seed、0.5B、单任务，作者自述exploratory。"),
    ("2607.15901", "dsworld", DSWORLD,
     "数据科学Agent还在拿真执行试错？港科大DSWorld先预测操作效果，RL训练提速约14×",
     "DSWorld把世界模型搬进数据科学Agent：执行昂贵操作前先预测状态转移，用成本感知路由决定真跑还是模拟；转移预测超最强LLM基线35.6%，RL训练提速约14×、搜索推理提速约3-6×。"),
    ("2607.16038", "sciforge", SCIFORGE,
     "科研AI的瓶颈不再是模型，而是没有可审计的研究状态：上海AI Lab的SciForge用Evidence-DAG把结论连回出处",
     "SciForge把科研做成可审计的持久状态：五支柱围绕决策治理、多模态translate-then-reason、Evidence-DAG证据治理、团队协作与真实场景；八个端到端案例覆盖基因发现到蛋白设计，开源桌面应用。"),
]


def run(job):
    aid, key, rich, html_title, html_conclusion = job
    out = ROOT / "outputs" / "ready" / DATE / aid
    gen = out / "generate_data.json"
    card = out / "card_data.json"
    ledger = out / "evidence_ledger.json"
    data = load(gen)
    for k, v in rich.items():
        if k != "evidence_ledger_patch":
            data[k] = v
    data["score_rationale_detail"] = distinct_score_detail(data["score"]["dimensions"], data.get("score_rationale") or "")
    notes = data.get("discussion_notes") or []
    tag = f"Enriched with rich fields via enrich_{DATE}_backlog.py"
    if tag not in notes:
        notes.append(tag)
    data["discussion_notes"] = notes
    if "evidence_ledger_patch" in rich:
        led = load(ledger) if ledger.exists() else {}
        led.setdefault("schema_version", 1)
        led.setdefault("paper", {"arxiv_id": aid, "title": data["info"]["title"], "link": data["info"]["link"]})
        led["claim_evidence"] = rich["evidence_ledger_patch"]["claim_evidence"]
        if data.get("score_rationale"):
            led["score_rationale"] = data["score_rationale"]
        dump(ledger, led)
        data["evidence_ledger"] = led
    dump(gen, data)
    for script, extra in [
        ("render_article.py", ["--article-payload", str(gen), "--out-dir", str(out), "--html-title", html_title, "--html-conclusion", html_conclusion]),
        ("render_article_wechat_safe.py", ["--article-payload", str(gen), "--out-dir", str(out), "--html-title", html_title, "--html-conclusion", html_conclusion]),
        ("generate_cards.py", ["--data", str(card), "--out", str(out)]),
        ("generate_cover.py", ["--data", str(card), "--out", str(out / "cover_235.png")]),
    ]:
        subprocess.run([sys.executable, str(ROOT / "scripts/production" / script)] + extra, check=True)


def main():
    for job in JOBS:
        run(job)
        print("enriched", job[0])


if __name__ == "__main__":
    main()
