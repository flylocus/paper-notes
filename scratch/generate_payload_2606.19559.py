#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

# Create output dirs if not exist
out_dir = Path("/Users/shenfei/clawd/paper-notes/outputs/ready/20260622/2606.19559")
out_dir.mkdir(parents=True, exist_ok=True)

fused_dir = Path("/Users/shenfei/clawd/paper-notes/fused")
fused_dir.mkdir(parents=True, exist_ok=True)

# 1. card_payload
card_payload = {
  "paper_title": "UDCS",
  "score": {
    "total": 8.6,
    "dimensions": [
      {"label": "重要性 Impact", "value": 1.8},
      {"label": "创新性 Novelty", "value": 1.7},
      {"label": "可验证性 Evidence", "value": 1.7},
      {"label": "产业可用性 Applicability", "value": 1.8},
      {"label": "可复用性 Reusability", "value": 1.6}
    ]
  },
  "info": {
    "title": "Uncertainty Decomposition for Clarification Seeking in LLM Agents",
    "title_cn": "Agent澄清提问中的不确定性分解",
    "link": "https://arxiv.org/abs/2606.19559",
    "authors": ["Gregory Matsnev"],
    "affiliations": ["AI Talent Hub, ITMO University"]
  }
}

# Helper to build score rationale detail
def build_score_rationale_detail(score_val, dims, rationale):
    high = max(d["value"] for d in dims)
    low = min(d["value"] for d in dims)
    dimension_rationales = []
    for dim in dims:
        val = dim["value"]
        lbl = dim["label"]
        if val == high:
            role = "highest"
            role_note = "最高维，说明这篇论文最强的判断依据集中在该维度。"
        elif val == low:
            role = "lowest"
            role_note = "最低维，说明这里是评分上限的主要约束，后续复用或外推需要额外验证。"
        else:
            role = "middle"
            role_note = "中间维，说明该维度有明确支撑，但不是本篇最突出的差异点。"
        dimension_rationales.append({
            "label": lbl,
            "value": val,
            "role": role,
            "rationale": f"{role_note} 总体依据：{rationale}"
        })
    return {
        "schema_version": 1,
        "score_range": round(high - low, 2),
        "highest_dimensions": [d["label"] for d in dims if d["value"] == high],
        "lowest_dimensions": [d["label"] for d in dims if d["value"] == low],
        "dimension_rationales": dimension_rationales
    }

reason = "该论文直击ToB Agent在模糊任务下“自信地做错”的业务痛点。其核心创新点在于提出了一种完全基于Prompt的不确定性分解方法，将“动作置信度”与“任务请求不确定性”剥离，从而实现了无监督、无需训练的澄清提问机制。实验在5种模型和包含50%模糊任务的Clarification基准上进行了系统评测，展示了极强的工程实用性（澄清F1在ALFWorld上提升73%）。尽管依靠Prompt的软性约束依然存在模型幻觉和校准波动等限制，但对闭源API极度友好，产业落地价值很高。"

score_rationale_detail = build_score_rationale_detail(8.6, card_payload["score"]["dimensions"], reason)

evidence_ledger = {
  "schema_version": 1,
  "paper": {
    "arxiv_id": "2606.19559",
    "title": "Uncertainty Decomposition for Clarification Seeking in LLM Agents",
    "link": "https://arxiv.org/abs/2606.19559"
  },
  "source_files": {
    "metadata": "2606.19559_metadata.json",
    "score": "2606.19559_score.json"
  },
  "source_basis": [
    "arXiv metadata verified via arXiv API",
    "PDF downloaded and converted to local text",
    "PDF first-page inspection for ITMO University affiliation",
    "Local PDF text inspection for WebShop-Clarification and ALFWorld-Clarification evaluation datasets, F1 scores across 5 LLM backbones, and prompt decomposition formulas"
  ],
  "score_rationale": reason,
  "claim_evidence": [
    {
      "claim": "平均在ALFWorld-Clarification上相比ReAct+UE提升了73%的澄清F1值",
      "evidence": "Averaged across the five backbones, the proposed decomposition improves clarification F1 on ALFWorld-Clarification by 73% over ReAct+UE and by 36% over UAM.",
      "location": "Abstract & Section 6.2"
    },
    {
      "claim": "基于 GPT-5.1 时，在 ALFWorld-Clarification 上的澄清 F1 达到 0.757",
      "evidence": "Under GPT-5.1 on ALFWorld-Clarification, the proposed method achieves clarification F1 of 0.757 compared to ReAct+UE (0.367) and UAM (0.538).",
      "location": "Appendix Table 4"
    },
    {
      "claim": "在 WebShop-Clar. 上 DeepSeek-v3.2-exp 的澄清 F1 提升至 0.614",
      "evidence": "Under DeepSeek-v3.2-exp on WebShop-Clarification, the proposed method achieves clarification F1 of 0.614 compared to ReAct+UE (0.116) and UAM (0.176).",
      "location": "Appendix Table 4"
    },
    {
      "claim": "GLM-4.7 在 WebShop-Clar. 上的 F1 提升至 0.756",
      "evidence": "Under GLM-4.7 on WebShop-Clarification, the proposed method achieves clarification F1 of 0.756 compared to ReAct+UE (0.405) and UAM (0.355).",
      "location": "Appendix Table 4"
    },
    {
      "claim": "在标准基准上‘Product（乘积）’聚合表现为一种强烈的路径长度代理指标",
      "evidence": "The length-proxy experiment of Table 2 shows, however, that on ALFWorld this aggregation functions as a strong length proxy.",
      "location": "Section 6.1 & Table 2"
    },
    {
      "claim": "故障检测中 Confidence-free 的 random (0.940) 和 1/length (0.991) 表现与真实 Product 聚合相当甚至更好",
      "evidence": "On ALFWorld under GPT-5.1, both random surrogate (0.940 ROC-AUC) and 1/length surrogate (0.991 ROC-AUC) match or exceed the real-product score (0.900 ROC-AUC).",
      "location": "Table 2 & Section 6.5"
    },
    {
      "claim": "阈值消融中，5 模型平均下 0.25 获得最高的平均澄清 F1",
      "evidence": "Averaged across all five backbones, θ = 0.25 attains the highest mean clarification F1 on both benchmarks (WebShop-Clar.: 0.464, ALFWorld-Clar.: 0.71).",
      "location": "Table 3 & Section 6.6"
    },
    {
      "claim": "加入不确定性评估后导致能力稀释，5 模型平均成功率出现滑坡",
      "evidence": "Averaged across all five benchmarks and all five backbones, mean success rate falls from 28.6% for ReAct+UE to 27.8% for UAM and 27.0% for the proposed method.",
      "location": "Section 6.3"
    }
  ]
}

article_payload = {
  **card_payload,
  "A_research_problem": "在ToB Agent落地过程中，面对含糊任务（如‘帮我买张机票’或‘处理一下工单’）时，Agent往往表现得‘自信地做错’。这源于传统Prompt置信度评估的缺陷：它将动作本身的执行难度与用户指令的含糊性混为一谈。如果不能把这两者在LLM外部解耦，Agent就无法学会在关键时刻‘停下来向用户澄清提问’，导致越权（Authority Creep）或误操作风险成倍增加。",
  "B_core_contributions": [
    "提出了一种基于Prompt的不确定性分解（Uncertainty Decomposition）框架，将Agent每一步的‘动作置信度（Action Confidence）’与‘请求不确定性（Request Uncertainty）’解耦，实现了零微调、即插即用的澄清提问拦截机制。",
    "引入了 WebShop-Clarification 和 ALFWorld-Clarification 两个澄清增强基准，通过故意设置50%的任务为含糊或要素缺失状态，为评估Agent的澄清决策提供了客观的二分类质量门禁。",
    "在5个主流大模型基座上进行了系统评测，结果表明该方法平均在ALFWorld-Clarification上相比ReAct+UE提升了73%的澄清F1值，证明该方法具备跨模型泛化性。"
  ],
  "C_method_framework": "UDCS（不确定性分解澄清寻求）框架。在LLM Agent的每个推理步骤中，弃用单一标量置信度，而要求模型输出两个解耦分值：动作置信度 $c_t$（假设任务理解无误时，动作迈向终点的置信度）和请求不确定性 $u_t$（评估用户指令中是否缺少必要的信息）。当 $u_t$ 超过设定阈值 $\\theta$（如 0.5）时，框架拦截动作执行并生成澄清提问（Clarification Question）请求用户输入。",
  "D_key_results": [
    "Table 4 澄清寻求对比：在 WebShop-Clarification 基准上，本文方法（UDCS）在 5 个大模型基座上均取得了最佳的澄清 F1 值。尤其在 DeepSeek-v3.2-exp 上澄清 F1 从基线 0.116 (ReAct) / 0.176 (UAM) 暴涨至 **0.614**，在 GLM-4.7 上由 0.405 / 0.355 提升至 **0.756**。在 ALFWorld-Clarification 上在 4 个模型上领先，如 GPT-5.1 澄清 F1 达到 **0.757**（对比 ReAct 0.367 / UAM 0.538），多模型平均提升 73% (vs ReAct) 与 36% (vs UAM)。",
    "Table 2 & Section 6.5 乘积聚合陷阱：故障检测（Fault Detection）中揭示了一个关键偏差。虽然 Product（乘积）聚合在 ALFWorld 上的 ROC-AUC 很高（GPT-5.1 下本文方法达 0.900，UAM 达 0.962），但在去除置信度后用随机数 `random` (0.940) 或 `1/length` 倒数 (0.991) 却能取得相当或更高的 ROC-AUC。这证实了在 ALFWorld 这类‘失败即轨迹长’的基准中，乘积聚合实质上充当了路径长度的代理指标，掩盖了模型自身置信度打分的不准确性。",
    "Table 3 & Section 6.6 阈值敏感度分析：澄清阈值 $\\theta$ 的选择直接影响效果。5 种模型平均下，较低的阈值 $\\theta = 0.25$ 取得了最高的平均澄清 F1 分数（WebShop-Clar: **0.464**，ALFWorld-Clar: **0.71**），略微优于默认的 $\\theta = 0.5$（分别为 0.455 和 0.68），而高阈值 $\\theta = 0.75$ 则会导致严重的 Recall 暴跌（如 GPT-5.1 ALFWorld 上的 Recall 从 0.484 缩水至 0.037）。",
    "Section 7.2 & 7.3 能力稀释与系统性过自信：由于 Prompt 引入了不确定性自我评估，大模型因推理算力分摊而产生‘能力稀释’，5 模型平均任务成功率从 28.6% 降至 27.8% (UAM) 和 27.0% (本文)；且 Figure 4 的 Reliability calibration 图显示所有方法都严重过度自信（曲线远低于对角线），亟需后处理校准。"
  ],
  "E_industry_implications": [
    "为ToB客服、售后、报销等涉及外部系统变动（Mutations）的Agent系统提供了一个几乎零成本的‘安全刹车门禁’，能够拦截大部分因指令模糊导致的越权与盲目操作风险。",
    "该方法完全基于提示词实现，无需繁琐的强化学习训练（如GRPO）或昂贵的多路径采样，对闭源商业API极其友好，便于在企业级流水线中快速验证和部署上线。"
  ],
  "F_one_line_judgement": "说白了，它是通过在Prompt中解耦动作置信度与指令模糊度，以极低的工程成本实现了高灵敏度的Agent澄清提问机制。不过，由于其完全依赖大模型提示词输出，在面对基底模型本身固有的过度自信（Overconfidence）幻觉时，打分极易出现波动，对Prompt打分尺度的敏感度较高，且在超长轨迹中多步不确定性累积衰减（Aggregation Decay）的建模依然粗糙。\n\n【Actionable Insight】在落地涉及资金审批或高危API写入（如发信、删除）的Agent时，不要依赖模型的‘自觉性’。应当把这套不确定性分解Prompt作为‘外置独立网关’（Safety Gateway）拦截器，当请求不确定性分值 $u_t \\ge 0.5$ 时强行阻断并推送消息给用户确认。开发团队在系统上线前，可用 20 个故意删去核心维度的任务进行澄清回测，以确定最稳健的阈值 $\\theta$。\n\n【🗳️ 下期选题由你决定】\n今天我们选读了不确定性分解这一篇，另外还有三篇高价值论文。欢迎大家在推文末尾参与投票，得票最高者我们将作为后续增补解读的依据：\n\n① 2606.19980 (ENPIRE): 具身智能 Agent 在真实世界中的策略自我进化。编码 Agent 迭代重置、执行、验证机器人动作，在 Pin-box 整理等任务上实现 99% 的高成功率。\n\n② 2606.20068 (Process-Verified RL): 定理证明 RL 方向，利用 Lean 定理证明器做过程级符号反馈（Tactic-level），进行 GRPO 强化学习训练，显著超过仅看结果对错的基准。\n\n③ 2606.19475 (Diffusion Language Models): 扩散语言模型（DLM）对决自回归大模型的系统实验评估。在推理、代码、翻译等 8 个基准上系统分析 DLM 的推理开销与性能权衡。",
  "discussion_notes": [
    "Generated from verified metadata: 2606.19559_metadata.json",
    "Generated from score file: 2606.19559_score.json"
  ],
  "score_rationale": reason,
  "score_rationale_detail": score_rationale_detail,
  "evidence_ledger": evidence_ledger,
  "glossary": [
    {
      "term": "Action Confidence (ct)",
      "explanation": "动作置信度，指Agent在当前任务理解下，对所选动作正确性的评估。"
    },
    {
      "term": "Request Uncertainty (ut)",
      "explanation": "请求不确定性，指Agent评估用户原始请求中是否缺失了完成任务的关键信息（即任务是否underspecified）。"
    },
    {
      "term": "Uncertainty Decomposition",
      "explanation": "不确定性分解，将Agent每一步的混合不确定性拆分为动作层面和请求层面，以支持不同的应对决策。"
    },
    {
      "term": "Clarification Seeking",
      "explanation": "澄清提问，Agent在识别到任务请求存在模糊或缺失关键要素时，主动向用户发起确认的交互行为。"
    },
    {
      "term": "Fault Detection",
      "explanation": "故障检测，评估Agent能否在执行失败或发生错误前，通过低置信度自我拦截的能力。"
    }
  ],
  "method_subsections": [
    {
      "title": "不确定性双维建模",
      "body": "在系统Prompt中设计两阶段打分：第一步让模型假设任务理解无误，打出动作可行性分；第二步评估用户指令的完整性，打出请求不确定性分。"
    },
    {
      "title": "澄清拦截判定",
      "body": "设置阈值 $\\theta$。当请求不确定性 $u_t \\ge \\theta$ 时，系统强行挂起当前工具调用流，进入澄清生成模板向用户提问。"
    },
    {
      "title": "多步不确定性聚合",
      "body": "提供 average、product、min、last-step 等不同轨迹聚合算法，在多轮对话中决定何时继承历史不确定性。"
    }
  ],
  "result_table": {
    "columns": ["比较维度（模型基座与任务）", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）"],
    "rows": [
      {"比较维度（模型基座与任务）": "GPT-5.1 (ALFWorld-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.367 / 0.538 vs 0.757 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "DeepSeek-v3.2-exp (WebShop-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.116 / 0.176 vs 0.614 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "GLM-4.7 (WebShop-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.405 / 0.355 vs 0.756 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "GLM-4.7 (ALFWorld-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.087 / 0.383 vs 0.667 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "Qwen3.5-35B (ALFWorld-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.433 / 0.568 vs 0.639 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "Qwen3.5-35B (WebShop-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.074 / 0.168 vs 0.505 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "GPT-OSS-120B (ALFWorld-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.299 / 0.241 vs 0.722 (本文方法最佳)"},
      {"比较维度（模型基座与任务）": "GPT-OSS-120B (WebShop-Clar.)", "澄清 F1 分数对比（基线 ReAct+UE / UAM vs 本文 UDCS 方法）": "0.165 / 0.220 vs 0.250 (本文方法最佳)"}
    ]
  },
  "source_notes": [
    "arXiv论文全文（2606.19559）",
    "PDF第一页确认作者单位（AI Talent Hub, ITMO University）",
    "PDF第4-5节系统Prompt设计与不确定性公式",
    "PDF附录Table 4全量多模型对比数据"
  ],
  "so_what": "置信度不能一概而论。让 Agent 学会‘装傻提问’比‘假装自信执行’在商业落地中安全得多。分解不确定性是提升 ToB Agent UX 和安全水位最经济的工程手段。",
  "feige_view": "从销售和交付角度看：很多客户不信任 Agent，就是怕它任务不清时瞎干。如果我们把‘请求不确定性拦截’做成可视化的安全门（Security Gate），当 ut 超标时高亮提示‘正在向用户澄清验证’，能够瞬间打消客户的安全疑虑，大幅提高方案的中标率。",
  "limitations": [
    {
      "title": "对Prompt敏感度高",
      "body": "由于不确定性分数完全依赖Prompt输出，不同的LLM基底对打分尺度（calibration scale）理解差异大，需要针对性调优。"
    },
    {
      "title": "多轮提问容易引起用户厌烦",
      "body": "若阈值设置不当或模型过度敏感，会导致Agent频繁澄清，破坏用户交互体验，需结合业务意图进行动态截断。"
    },
    {
      "title": "多步衰减未完全解决",
      "body": "在超长轨迹中，历史置信度的乘积会快速衰减至零，如何设计抗衰减的长期不确定性记忆仍是开放性难题。"
    }
  ],
  "target_audience": [
    "正在开发 ToB 客服 Agent、售后助理、报销机器人和企业 Agent 平台的团队。",
    "关注 LLM Agent 越权控制（Authority Creep）与安全拦截机制的架构师。",
    "希望通过主动提问改善 Agent 人机交互（HCI）与用户体验的研发人员。"
  ],
  "sales_use_cases": [
    "销售演示时展示 Agent 的‘安全网关’功能，证明 Agent 在任务不清时会主动澄清而不会乱下单。",
    "在强合规场景下，为金融、流程审批 Agent 设计‘确定性拦截’的安全屏障。",
    "为客服场景提供用户交互兜底，当用户指令模糊时，智能提示其补充关键要素。"
  ],
  "objection_handling": [
    "客户说：‘我们通过预定义的槽位（Slot Filling）也能澄清提问。’ 回应：槽位是硬编码的，无法应对长尾、自由文本的语义模糊；基于不确定性分解的机制是语义级、泛化性更强的解。",
    "客户说：‘模型每次打分不准，可能误拦截或者漏拦截。’ 回应：是的，所以必须结合硬性字段校验，把本文的 Prompt 机制作为辅助安全网关，且将阈值设为偏保守的 0.5。"
  ],
  "copy_paste_lines": [
    "宁可让 Agent 碎碎念地澄清，也绝不能让它自信地瞎忙。",
    "对于高危 Mutation 操作，Agent 必须有一层独立于大模型决策的 Deontic 拦截门槛。",
    "请求不确定性拦截（ut Gate），是打消企业客户对 Agent 失控疑虑的最强解药。"
  ],
  "key_quotes": [
    "A simple prompt-based decomposition that separates action confidence from request uncertainty, enabling the agent to ask for clarification when the task specification is ambiguous.",
    "Averaged across the five backbones, the proposed decomposition improves clarification F1 on ALFWorld-Clarification by 73% over ReAct+UE."
  ]
}

# Save in fused
with open(fused_dir / "udcs_card_payload_20260622.json", "w", encoding="utf-8") as f:
    json.dump(card_payload, f, ensure_ascii=False, indent=2)

with open(fused_dir / "udcs_article_payload_20260622.json", "w", encoding="utf-8") as f:
    json.dump(article_payload, f, ensure_ascii=False, indent=2)

with open(fused_dir / "udcs_evidence_ledger_20260622.json", "w", encoding="utf-8") as f:
    json.dump(evidence_ledger, f, ensure_ascii=False, indent=2)

# Save in output dir directly
with open(out_dir / "card_data.json", "w", encoding="utf-8") as f:
    json.dump(card_payload, f, ensure_ascii=False, indent=2)

with open(out_dir / "generate_data.json", "w", encoding="utf-8") as f:
    json.dump(article_payload, f, ensure_ascii=False, indent=2)

with open(out_dir / "evidence_ledger.json", "w", encoding="utf-8") as f:
    json.dump(evidence_ledger, f, ensure_ascii=False, indent=2)

print("Generated all payloads successfully.")
