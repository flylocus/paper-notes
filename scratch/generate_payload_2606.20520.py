#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

# Create output dirs if not exist
out_dir = Path("/Users/shenfei/clawd/paper-notes/outputs/ready/20260623/2606.20520")
out_dir.mkdir(parents=True, exist_ok=True)

fused_dir = Path("/Users/shenfei/clawd/paper-notes/fused")
fused_dir.mkdir(parents=True, exist_ok=True)

# 1. card_payload
card_payload = {
  "paper_title": "SEB",
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
    "title": "Sovereign Execution Brokers: Enforcing Certificate-Bound Authority in Agentic Control Planes",
    "title_cn": "Agent主权执行代理：如何用证书级防线拦截失控的API调用？",
    "link": "https://arxiv.org/abs/2606.20520",
    "authors": ["Jun He", "Deying Yu"],
    "affiliations": ["OpenKedge.io"]
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

reason = "该论文直击AI Agent在企业生产环境（Cloud/Kubernetes/AWS）中落地时的权限安全与审计痛点。其核心创新点在于提出了一种主权执行代理（Sovereign Execution Broker, SEB）架构，将Agent的“proposal (非确定性动作建议)”、“admission (安全准入认证)”和“execution (具体执行)”在物理和逻辑上彻底剥离。Agent不持有长期生产凭证，而是由SAB根据安全合同签发Omega证书，再由SEB在执行瞬间校验撤销与状态漂移，并分发短期凭证进行API调用，从而闭栏了非确定性推理与确定性基础设施变更之间的安全围栏。实验在AWS和Kubernetes集群上对延迟、证书撤销、漂移检测进行了实测，具有极强的工业落地和治理参考价值。"

score_rationale_detail = build_score_rationale_detail(8.6, card_payload["score"]["dimensions"], reason)

evidence_ledger = {
  "schema_version": 1,
  "paper": {
    "arxiv_id": "2606.20520",
    "title": "Sovereign Execution Brokers: Enforcing Certificate-Bound Authority in Agentic Control Planes",
    "link": "https://arxiv.org/abs/2606.20520"
  },
  "source_files": {
    "metadata": "2606.20520_metadata.json",
    "score": "2606.20520_score.json"
  },
  "source_basis": [
    "arXiv metadata verified via arXiv API",
    "PDF downloaded and converted to local text",
    "PDF first-page inspection for OpenKedge.io affiliation",
    "Local PDF text inspection for Sovereign Execution Broker (SEB) execution model, certification predicates, Kubernetes and AWS evaluation, and revocation propagation latencies"
  ],
  "score_rationale": reason,
  "claim_evidence": [
    {
      "claim": "在 Kubernetes 集群中，SEB 自身的验证与凭据派生延迟仅为 p50 28.2 ms，端到端延迟为 40.7 ms",
      "evidence": "Under Kubernetes setup, SEB broker-only latency is p50 28.2 ms and E2E is 40.7 ms.",
      "location": "Section VI-B & Table 4"
    },
    {
      "claim": "在 AWS 部署下，SEB 自身的验证延迟为 p50 136.9 ms，端到端延迟为 221.9 ms",
      "evidence": "Under AWS, SEB broker-only latency is p50 136.9 ms and E2E is 221.9 ms.",
      "location": "Section VI-B & Table 4"
    },
    {
      "claim": "安全通知废止传播的最大延迟为 5.2 秒，平均仅需 2.6 秒",
      "evidence": "Max propagation latency is 5.2 s, with a mean of 2.6 s.",
      "location": "Section VI-C & Figure 3"
    },
    {
      "claim": "针对 10 种典型的越权与故障注入攻击，SEB 实现了 100% 的拦截阻断",
      "evidence": "SEB rejected 100% of injected threat and fault scenarios (uncertified, revoked, drift, parameter tampering, etc.).",
      "location": "Section VI-D"
    },
    {
      "claim": "SEB 成功识别了 100% 的 drift 状态漂移案例并予以挂起或拒绝",
      "evidence": "SEB successfully detected 100% of state drift cases injected in tests.",
      "location": "Section VI-E & Figure 5"
    }
  ]
}

article_payload = {
  **card_payload,
  "A_research_problem": "在企业级 Agent 落地中，仅给自主 Agent 赋予长期生产环境凭据（如 AWS IAM Access Key 或数据库密码）会导致极高的安全风险。AI Agent 本质上是非确定性的推理过程，如果它直接持有修改物理或云资源的 credentials，任何提示词注入（Prompt Injection）或幻觉调用都可能瞬间引发越权操作、数据删除或资源滥用。现有的准入网关（如 SAB）仅在提案阶段签发静态证书，却无法在执行（Mutation）瞬间强制验证，形成了合规漏洞。我们必须把 Agent 动作的提案（Proposal）、准入（Admission）和具体执行（Execution）三者彻底解耦，使 Agent 原生不具备直接执行能力。",
  "B_core_contributions": [
    "提出主权执行代理（Sovereign Execution Broker, SEB）架构，作为 certificate-bound 动态权限的运行时强制执行边界，阻断任何非经纪商（Non-broker）身份的直接基础设施修改操作。",
    "设计了一套极简的 Ω 证书认证、撤销与重放校验谓词，能够在执行时刻（mutation time）校验证书有效期、策略版本、废止纪元（revocation epochs）以及运行期状态漂移（state drift）。",
    "在 AWS 和 Kubernetes 环境中实现并测试了 SEB 原型，证明了在几乎不引入明显延迟的前提下，能够对 100% 的未认证、超期、漂移和越权请求进行精准阻断。"
  ],
  "C_method_framework": "SEB (Sovereign Execution Broker) 架构。其核心思想是分离 Agent 提案与执行。Agent 仅产生动作提案（Proposal），由 SAB (Sovereign Assurance Boundary) 对提案进行合规评估，通过后签发包含具体执行合同的加密证书 Ω。执行时，Agent 将 Ω 提交给 SEB，SEB 解析 Ω 中的指令与约束，进行五维状态校验（验证时间窗口、策略纪元、废止列表、重放攻击及当前运行状态漂移）。若通过，SEB 扮演托管凭据角色，临时向 API 网关申请短期 scoped identity 进行操作并记录签名审计日志。所有底层 API 原生拒绝除 SEB 代理身份之外的任何直接请求。",
  "D_key_results": [
    "Table 4/Section VI.B 运行时延迟开销：SEB 原型表现出极高的执行效率。在 Kubernetes 集群中，Broker 自身的验证与凭据派生延迟仅为 p50 28.2 ms（E2E 客户端延迟为 40.7 ms）；在 AWS 多区域部署中，Broker 自身延迟为 p50 136.9 ms（E2E 客户端延迟为 221.9 ms），完全不影响工业级微服务交互体验。",
    "Figure 3/Section VI.C 撤销传播时效：模拟了 SAB 签发废止通知后，SEB 废止纪元（revocation epoch）更新的全球同步时限。在分布式节点网络下，废止更新传播的最大延迟为 5.2 秒，平均仅需 2.6 秒，为突发性安全事件提供了秒级快速隔离响应。",
    "Section VI.D 注入故障与漂移拦截率：针对 10 种典型的越权与故障注入攻击（包括伪造证书、篡改执行参数、重放旧证书、策略纪元过时、证书遭撤销、网络分区下的过期凭证及运行期状态漂移等），SEB 均实现了 100% 的拦截阻断，误报率为 0%。",
    "Figure 5/Section VI.E 状态漂移检测：在 proposal 与 execution 的时间窗口内注入数据库/集群状态变更，SEB 成功识别了 100% 的 drift 案例，挂起或拒绝了执行提案，有效防范了竞争条件（Race Conditions）安全漏洞。"
  ],
  "E_industry_implications": [
    "为企业部署具备自主执行（AWS 部署、CI/CD 触发、数据库写入）的 Agent Control Planes 提供了一套工业级的零信任（Zero Trust）安全解决方案，实现了“非确定性大脑”与“确定性骨干网”的物理隔离。",
    "通过外置 Omega 证书与 SEB 决策日志，为金融、审计、运维行业提供天然的强审计线索（Audit Trails），彻底解决 LLM 内部决策不可追溯的合规难题。"
  ],
  "F_one_line_judgement": "说白了，它是通过将 Agent 的动作提案与持有 production 凭据的 SEB 运行时拦截器彻底分离，利用加密的 Ω 证书做执行时刻的零信任控制，从根本上封死了 Agent 因幻觉或注入攻击导致基础设施失控的可能。不过，由于 SEB 架构依赖外部基础设施与 API 网关（如 IAM 临时凭证派生）的物理隔离，对既有 legacy 系统的改造侵入性极强，且在网络分区（Network Partition）状态下如何处理本地缓存废止纪元的时效性与一致性仍待优化。\n\n【Actionable Insight】在规划多 Agent 复杂工作流（如自动运维、自动化代码发布）的企业，切记绝不能给 Agent 容器配置任何 standing keys（长期 Access Key）。应当在基础设施网关层配置 SEB 中间件，规定生产 mutation API 仅接受来自 broker 的 scoped token，并使用短期 Ω 证书传递命令。在下周的设计方案中，我们建议先基于本地 Kubernetes 集群部署一个 SEB 代理网关，以进行安全策略的回测与延迟性能基准测试。\n\n【🗳️ 下期选题由你决定】\n今天我们选读了 Agentic 安全网关 SEB 这一篇，另外还有三篇高价值论文。欢迎大家在推文末尾参与投票，得票最高者我们将作为后续增补解读的依据：\n\n① 2606.20363 (CUA Skills): 计算机使用 Agent 的 SKILL.md 技能自动生成。通过 GUI 交互轨迹挖掘与 GRPO 训练，诊断自动技能挖掘的泛化性障碍与政策约束。\n\n② 2606.20510 (Sound Verification): 针对 AI Agent 的高效概率性策略验证框架。利用分布鲁棒优化计算 upper bound，在 ambiguity 场景下防范 PII 泄漏与安全违规。\n\n③ 2606.20493 (Contagion Networks): 多 Agent LLM 系统中的评估偏差传播（Contagion）。量化同一/跨模型代理间的偏差传播系数，并提出三模型委员会的平抑方法。",
  "discussion_notes": [
    "Generated from verified metadata: 2606.20520_metadata.json",
    "Generated from score file: 2606.20520_score.json"
  ],
  "score_rationale": reason,
  "score_rationale_detail": score_rationale_detail,
  "evidence_ledger": evidence_ledger,
  "glossary": [
    {
      "term": "Sovereign Execution Broker (SEB)",
      "explanation": "主权执行代理，充当 AI Agentic 基础设施控制平面的运行时强制执行网关，负责在动作执行瞬间校验授权证书并调用 API。"
    },
    {
      "term": "Sovereign Assurance Boundary (SAB)",
      "explanation": "主权保证边界，在 Agent 动作提交阶段的合规与策略评估网关，通过后签发 Ω 加密证书。"
    },
    {
      "term": "Ω Certificate (Omega)",
      "explanation": "Ω 证书，由安全准入网关签发的具有时效限制的加密执行合同证书，承载 Agent 被准许的具体操作参数。"
    },
    {
      "term": "Scoped Identity",
      "explanation": "范围受限身份，由 SEB 执行端动态分配的短期、极低权限凭证，用于物理执行单个 certified 变更动作。"
    },
    {
      "term": "State Drift",
      "explanation": "状态漂移，指在 Agent 提案被安全准入评估到具体执行的延迟窗口内，底层系统状态发生变更而导致执行条件不再满足的现象。"
    }
  ],
  "method_subsections": [
    {
      "title": "证书解析与合同核验",
      "body": "SEB 接收 Ω 证书并解密，校验发行方签名、任务参数与执行指令合同是否完全一致。"
    },
    {
      "title": "多维运行时拦截",
      "body": "验证证书的有效期时间窗口、SAB 策略纪元与废止纪元列表，防范证书重放和过时授权。"
    },
    {
      "title": "动态凭据派生与审计",
      "body": "在安全网关层面为受准入动作临时 mint 短期、 scoped token 物理执行底层 mutation，同时完成签名日志审计。"
    }
  ],
  "result_table": {
    "columns": ["评估指标与部署环境", "执行时刻的安全校验与延迟性能表现"],
    "rows": [
      {"评估指标与部署环境": "Kubernetes 部署延迟 (SEB 验证 / 客户端端到端)", "执行时刻的安全校验与延迟性能表现": "p50 28.2 ms / 40.7 ms (超低开销实时交互)"},
      {"评估指标与部署环境": "AWS 部署延迟 (SEB 验证 / 客户端端到端)", "执行时刻的安全校验与延迟性能表现": "p50 136.9 ms / 221.9 ms (多区域网络传输下开销)"},
      {"评估指标与部署环境": "安全通知废止传播延迟 (最大值 / 平均值)", "执行时刻的安全校验与延迟性能表现": "5.2 秒 / 2.6 秒 (秒级撤销与隔离响应)"},
      {"评估指标与部署环境": "越权、重放与状态漂移故障注入拦截率", "执行时刻的安全校验与延迟性能表现": "100% 成功拦截 (确保不确定推理无法绕过安全合规网关)"}
    ]
  },
  "source_notes": [
    "arXiv论文全文（2606.20520）",
    "PDF第一页确认作者单位（OpenKedge.io）",
    "PDF第3-4节SEB执行模型与证书和重放校验谓词",
    "PDF第6节Kubernetes与AWS原型性能评估数据"
  ],
  "so_what": "置信度不能一概而论。让 Agent 学会‘装傻提问’比‘假装自信执行’在商业落地中安全得多。分解不确定性是提升 ToB Agent UX 和安全水位最经济的工程手段。",
  "feige_view": "从销售和交付角度看：很多客户不信任 Agent，就是怕它任务不清时瞎干。如果我们把‘请求不确定性拦截’做成可视化的安全门（Security Gate），当 ut 超标时高亮提示‘正在向用户澄清验证’，能够瞬间打消客户的安全疑虑，大幅提高方案的中标率。",
  "limitations": [
    {
      "title": "物理隔离改造侵入性强",
      "body": "由于 SEB 架构依赖外部基础设施与 API 网关（如 IAM 临时凭证派生）的物理隔离，对既有 legacy 系统的改造侵入性极强。"
    },
    {
      "title": "网络分区下废止更新同步难题",
      "body": "在网络分区状态下，SEB 节点如何保证本地缓存的废止纪元与全局一致且不退化为不安全状态，仍是一个设计难点。"
    },
    {
      "title": "证书有效期时间差风险",
      "body": "在准入评估到具体执行的延迟窗口内，微小的状态漂移仍可能绕过静态合同，需细化状态校验规则的精度。"
    }
  ]
}

# Save in fused
with open(fused_dir / "seb_card_payload_20260623.json", "w", encoding="utf-8") as f:
    json.dump(card_payload, f, ensure_ascii=False, indent=2)

with open(fused_dir / "seb_article_payload_20260623.json", "w", encoding="utf-8") as f:
    json.dump(article_payload, f, ensure_ascii=False, indent=2)

with open(fused_dir / "seb_evidence_ledger_20260623.json", "w", encoding="utf-8") as f:
    json.dump(evidence_ledger, f, ensure_ascii=False, indent=2)

# Save in output dir directly
with open(out_dir / "card_data.json", "w", encoding="utf-8") as f:
    json.dump(card_payload, f, ensure_ascii=False, indent=2)

with open(out_dir / "generate_data.json", "w", encoding="utf-8") as f:
    json.dump(article_payload, f, ensure_ascii=False, indent=2)

with open(out_dir / "evidence_ledger.json", "w", encoding="utf-8") as f:
    json.dump(evidence_ledger, f, ensure_ascii=False, indent=2)

print("Generated all payloads successfully.")
