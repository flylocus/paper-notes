import json

def main():
    path = 'outputs/ready/20260621/2606.19464/generate_data.json'
    el_path = 'outputs/ready/20260621/2606.19464/evidence_ledger.json'
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. A_research_problem (Direct judgment & stance first for AI System Notes)
    data['A_research_problem'] = "在企业级 Agent 落地中，仅做 allow/deny 的静态授权（如 Rego 或 Cedar）无异于等死。对于金融、医疗等强监管行业的 AI Agent，我们必须在 LLM 外部建立运行时道义治理（Deontic Governance），强行管理‘义务生命周期’和‘例外豁免’，否则 authority creep（权限潜移）和幻觉失控只是迟早的事。"

    # 2. B_core_contributions
    data['B_core_contributions'] = [
        "提出一种专为 Agentic 系统定制的 Deontic 运行时治理框架 AgenticRei，原生支持 Obligation 和 Dispensation 的全生命周期管理",
        "采用三阶段 extract-evaluate-apply 中间件架构，利用外部逻辑引擎（RDFox）实现高解释性的 OWL/RDFS 策略推理",
        "统一了工具调用（Tool Invocations）与 Agent 间通信（A2A Message）的治理面，并实现与 A2AS 行业规范的兼容集成"
    ]

    # 3. E_industry_implications
    data['E_industry_implications'] = [
        "强监管行业（如金融、医疗）在落地 AI Agent 时，可采用该 Deontic 运行时框架替代传统的 flat ACL 列表，以支撑复杂的审计与例外审批流程",
        "为缓解 Agent 幻觉带来的 authority creep 风险，提供了一种外置的安全沙箱治理门禁"
    ]

    # 4. F_one_line_judgement (Adding Actionable Insight & next steps)
    data['F_one_line_judgement'] = "说白了，它是通过基于 OWL/Rei 框架的 AgenticRei 动态引擎，将 Deontic 治理从静态授权中解放出来，提供了高可审计性与 LLM 幻觉防御。不过，由于其依赖 OWL 本体表示与特定的 RDFox 推理引擎，企业的策略编写和维护门槛相对较高，对复杂策略链的吞吐性能待验证，且其目前的安全机制仍处于模拟阶段。\n\n【Actionable Insight】由于 AgenticRei 与 A2AS 天然兼容，开发复杂多 Agent 系统的企业团队应在架构设计期将‘运行时道义拦截器’（Deontic Interceptor）写进框架中间件，以防后期因合规审计压力被迫重构整个工具链。下周我们将继续追踪该框架在 Microsoft Agent 上的实际集成进展。"

    # 5. Glossary enrichment
    glossary = data.get('glossary', [])
    has_creep = any(item.get('term') == 'Authority Creep' for item in glossary)
    if not has_creep:
        glossary.append({
            "term": "Authority Creep",
            "explanation": "权限潜移，指 Agentic 系统在部署运行过程中，由于其确认要求被逐步放宽、自主性阈值被逐步提高，导致实际拥有的操作权限超出初始安全设计的现象。"
        })
    data['glossary'] = glossary

    # 6. claim_evidence
    claim_ev = [
        {
            "claim": "在微秒级时间内完成策略的评估推理，推理延迟满足工业级 Agent 系统的实时性交互要求",
            "evidence": "Every decision is evaluated by a high-performance logic engine (RDFox) at runtime; Section VI reports microsecond-level query latencies.",
            "location": "Section III-Evaluate & Section VI"
        },
        {
            "claim": "由于其依赖 OWL 本体表示与特定的 RDFox 推理引擎，企业的策略编写 and 维护门槛相对较高",
            "evidence": "Limitations include added implementation and rule maintenance overhead and specific description logic system dependence.",
            "location": "Section VIII-Limitations"
        },
        {
            "claim": "其目前的安全机制仍处于模拟阶段",
            "evidence": "Credential verification is currently simulated through trusted-issuer matching rather than cryptographic signature checking.",
            "location": "Section III-Apply & Section VIII"
        }
    ]
    data['evidence_ledger']['claim_evidence'] = claim_ev

    # 7. Battlecard 5 Modules for Deontic Agent Governance (2606.19464)
    data['target_audience'] = [
        "做客服 Agent、售后 Agent、订单/账户自动化和企业 Agent 平台的团队。",
        "金融、医疗、政务等强监管行业落地 AI Agent 的架构师与安全合规团队。",
        "关注 Agent 运行时安全性与权限控制的企业 CTO 和技术负责人。"
    ]
    data['sales_use_cases'] = [
        "金融交易审批、敏感医疗数据调取、政务审批等涉及“多级义务”与“例外豁免”的强合规场景。",
        "企业内网多 Agent 通信和工具调用审计，防范 Authority Creep（权限潜移）。",
        "面向合规监管机构做技术选型汇报和安全风控设计展示。"
    ]
    data['objection_handling'] = [
        "客户说“我们已经在应用层用 Rego / Cedar 做了权限控制”：静态授权（Permit/Prohibit）无法管理“义务生命周期”（如触发后必须在规定时间内履行并记录）和“例外豁免”，道义策略才是解决运行时权限潜移的刚需。",
        "客户说“我们直接在 LLM 提示词里写明合规守则就行”：LLM 存在幻觉且提示词易被注入攻击，合规性决策必须外置在确定性的逻辑推理引擎中。"
    ]
    data['copy_paste_lines'] = [
        "企业级 Agent 安全的核心原则是：读状态和写系统必须在 LLM 外部强力拦截，决不能依赖模型“自觉”。",
        "仅做静态授权是等死！要防范 Agent 运行时的权限黑盒，Deontic 运行时道义拦截器是框架设计的刚需。",
        "读状态是一码事，改写物理世界是另一码事。只要 Agent 涉及工具调用，就必须有一层可审计的策略治理门。"
    ]
    data['key_quotes'] = [
        "Deontic policies express permissions, prohibitions, and obligations, along with rules for conflict resolution and dispensations.",
        "By enforcing policies externally, we ensure governance decisions are explainable and immune to LLM hallucination."
    ]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(el_path, 'r', encoding='utf-8') as f:
        el = json.load(f)
    el['claim_evidence'] = claim_ev
    with open(el_path, 'w', encoding='utf-8') as f:
        json.dump(el, f, indent=2, ensure_ascii=False)

    print("Patched generate_data.json and evidence_ledger.json successfully!")

if __name__ == '__main__':
    main()
