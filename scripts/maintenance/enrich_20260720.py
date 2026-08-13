#!/usr/bin/env python3
"""One-off enrichment for 20260720 paper-notes payloads."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SEARCHOS_RICH = {
    "glossary": [
        {"term": "SOCM（Search-Oriented Context Management）", "definition": "搜索导向的上下文管理：把搜索进度外化为Frontier Task、Evidence Graph、Coverage Map、Failure Memory四元共享状态，而非藏在对话历史里。"},
        {"term": "关系型schema补全", "definition": "把开放域检索任务建模为多表实体发现+属性填充+跨表外键关联，每个单元格值都要锚定来源URL与摘录，进度在实体/属性粒度可度量。"},
        {"term": "Frontier Task", "definition": "SOCM中的待覆盖缺口队列：指向尚未填充或未验证的schema单元，驱动编排器持续分配搜索子任务。"},
        {"term": "Evidence Graph", "definition": "证据图：记录已发现事实、来源URL、锚定摘录及其与schema单元格的映射关系。"},
        {"term": "Failure Memory", "definition": "失败记忆：记录无效搜索路径与停滞轨迹，供Harness和技能系统跨会话避免重复踩坑。"},
        {"term": "WideSearch / GISA", "definition": "WideSearch测大规模宽表信息收集；GISA测通用信息检索助手，含Table/Set/List/Item四类问题。"},
    ],
    "method_subsections": [
        {"title": "关系型schema补全：把开放检索变成可度量的表格任务", "body": "给定自然语言请求，系统先构建关系型搜索schema（多表+主外键），任务变成联合发现实体行、填充属性、维护引用矩阵。每个值必须映射到来源URL和锚定摘录——这让『搜到了什么、还缺什么』不再靠模型从长对话里回忆，而是在Coverage Map上直接可见。"},
        {"title": "SOCM四元状态 + 流水线并行调度", "body": "中央编排器把schema缺口分解成Frontier Task，explore/search/writer三类专职Agent并行推进。关键设计是pipeline-parallel：不等整批同步结束，子任务一完成就释放槽位给下一个未覆盖缺口，减少慢任务拖全局的空转。Evidence Graph和Failure Memory跨Agent共享，避免重复劳动和死循环。"},
        {"title": "Search Tool Middleware Harness：把治理放在工具层", "body": "Harness拦截每次LLM调用和工具返回：注入相关共享状态、从工具输出提取并锚定证据、强制执行预算、检测重复/停滞轨迹并触发干预。分层搜索技能把策略技能（怎么搜）与站点访问技能（怎么进站提取）分离，成功和失败轨迹都可跨会话复用。"},
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {"看什么": "WideSearch主指标", "论文证据": "Item F1 80.3（最强基线A-MapReduce 76.0，+4.3pp）；Recall 79.7全场最高，Precision 83.9也领先。", "飞哥判断": "增益集中在召回，说明覆盖感知调度真的在减少漏单元格，不是单纯堆精度。"},
            {"看什么": "GISA集合类问题", "论文证据": "Set F1 76.5 vs 最强基线63.1（+13.4pp）；Table Item F1 76.9、List F1 68.1也全部第一。", "飞哥判断": "集合枚举是长程检索最难的题型，这里领先幅度最大，说明状态外化对『找全』特别有效。"},
            {"看什么": "六个headline F1", "论文证据": "Table 2：WideSearch与GISA上六个headline F1指标SearchOS全部领先。", "飞哥判断": "不是某一题型刷分，而是系统性领先；但基准规模和模型配置仍需看附录细节。"},
            {"看什么": "关系型schema价值", "论文证据": "Oracle选更高Item-F1固定schema per case：多表schema在部分case优于单表，但赢面不大（21胜17负2平）。", "飞哥判断": "schema分解是工程杠杆，不是银弹；价值更多在可观测性和Harness治理，而非每次都比单表强。"},
        ],
    },
    "source_notes": [
        "主结果：论文 Table 2，WideSearch与GISA六个headline F1；最强基线WideSearch为A-MapReduce（Item F1 76.0），GISA Set为63.1。",
        "投稿时间：2026-07-16 17:51 UTC，属07-16公告批次；ChatGPT 0720 Top1推荐，0718/0719 backlog转正。",
        "单位：中国人民大学高瓴人工智能学院 + Ant Group（PDF首页+overrides核验）；代码开源 github.com/antins-labs/SearchOS。",
        "论文未报告bootstrap置信区间；对比基线类别含单Agent（ReAct等）与多Agent方法，具体模型配置见附录。",
    ],
    "so_what": "说白了，搜索Agent绕圈不全是模型笨，有相当一部分是『进度、证据、失败全塞在对话里』——上下文一长就丢、一丢就重复搜、一重复就烧预算。SearchOS把这些问题变成系统状态：Coverage Map告诉你还缺哪格，Failure Memory记住哪条路走不通，Harness在工具层强制预算和停滞干预。对做Deep Research产品的团队，这意味着编排层投资比再堆一个搜索prompt更划算。",
    "feige_view": "给做信息检索/Deep Research Agent团队的三个动作：①画一张自己的『搜索状态图』——现在进度、证据、失败存在哪？如果答案只有对话历史，就是SearchOS要解决的问题；②把预算控制和停滞检测下沉到Harness/工具中间件，别指望Agent自觉停手；③评测别只看最终答案F1，加覆盖率和重复搜索率——SearchOS的Recall优势说明漏搜比答错更常见。",
    "limitations": [
        "不过，论文主要在WideSearch和GISA两个基准上验证，任务形态偏结构化表格补全；对完全开放、无schema先验的检索场景，关系型分解的收益需要额外验证。",
        "不过，流水线并行调度和Harness干预带来额外系统复杂度与运维成本；论文未充分报告端到端延迟、token开销和失败恢复的工程代价。",
        "不过，分层搜索技能依赖成功/失败轨迹积累，冷启动阶段Failure Memory和技能库为空时，系统优势可能打折扣——论文对跨会话学习的样本效率讨论有限。",
    ],
    "related_theme_picks": {
        "theme": "Agent 检索编排与评测",
        "intro": "本篇讲「搜索状态怎么外化」；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.15263", "title_cn": "安全Agent评测该把成本当一等指标", "one_liner": "检索/安全Agent都要回答：烧多少预算换来多少覆盖。", "link": "https://arxiv.org/abs/2607.15263", "ready_date": "20260719"},
            {"arxiv_id": "2607.13705", "title_cn": "AgentCompass统一评测基础设施", "one_liner": "Agent能力碎片化评测的统一框架，和SearchOS的『可观测状态』互补。", "link": "https://arxiv.org/abs/2607.13705", "ready_date": "backlog"},
            {"arxiv_id": "2607.14166", "title_cn": "Agent审批门形同虚设", "one_liner": "Harness治理的另一面：控制原语能不能被真正执行。", "link": "https://arxiv.org/abs/2607.14166", "ready_date": "20260718"},
        ],
    },
    "target_audience": [
        "做Deep Research / 企业调研 / 开放域信息检索Agent的产品与工程团队。",
        "在多Agent搜索编排中遇到死循环、重复探索、证据丢失问题的架构师。",
        "关注Agent基础设施（Harness、状态管理、评测）的研究者与投资人。",
    ],
    "sales_use_cases": [
        "回应「搜索Agent就是多调几次搜索API」：用80.3 vs 76.0论证系统级状态外化的独立贡献。",
        "Deep Research产品技术评审：用SOCM四元状态框架审计现有编排方案的可观测性缺口。",
        "客户调研自动化方案：用GISA Set +13.4pp论证『找全』能力对集合类调研任务的价值。",
    ],
    "objection_handling": [
        "客户说：「加更多Agent就能覆盖更全。」→ 回应：论文显示多Agent不加状态管理会重复劳动和空转；SearchOS的增益来自Coverage Map驱动的缺口调度，不是简单加人。",
        "客户说：「关系型schema太死板，真实任务没表格。」→ 回应：schema是运行时逐步发现/填充的，不是预置模板；价值在于让进度可度量，而非假设所有任务天生是Excel。",
    ],
    "copy_paste_lines": [
        "搜索进度不该藏在对话里，而该是一张人人看得见的覆盖图。",
        "Agent绕圈，往往是Failure Memory为空，不是模型不会搜。",
        "六个headline F1全领先，说明状态外化是系统性红利。",
    ],
    "key_quotes": [
        "search state should be maintained by the system rather than inferred repeatedly from interaction history",
        "SearchOS achieves 80.3 item-level F1 on WideSearch",
        "exceeding the strongest baseline on GISA Set F1 by 13.4 points",
    ],
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "WideSearch Item F1 80.3，最强基线76.0（+4.3pp）", "evidence": "Table 2 main results", "location": "Table 2 / Section 5"},
            {"claim": "GISA Set F1 76.5 vs 最强基线63.1（+13.4pp）", "evidence": "Set question type breakdown", "location": "Table 2 / Section 5"},
            {"claim": "六个headline F1在WideSearch与GISA上全部领先", "evidence": "全表对比", "location": "Table 2"},
            {"claim": "F段限制：基准规模与工程代价讨论有限", "evidence": "实验仅在两个基准，未报告端到端延迟/token成本", "location": "Section 5-7"},
        ],
    },
}

HALFLIFE_RICH = {
    "glossary": [
        {"term": "HALFLIFE", "definition": "论文提出的三阶段概率分析框架：估算毒样从网页注入→爬取捕获→数据过滤后的端到端存活（inclusion）概率。"},
        {"term": "第三方内容注入", "definition": "攻击者不拥有/运营网页，但通过公开接口（如评论区）把恶意文本嵌入页面静态HTML，随正常爬取进入语料。"},
        {"term": "P(injectable)", "definition": "目标页面是否存在可注入的第三方内容接口（如评论表单）的概率。"},
        {"term": "P(captured|injectable)", "definition": "已注入内容在爬取和文本提取后仍保留在文档中的条件概率。"},
        {"term": "Common Crawl WARC", "definition": "Common Crawl的原始网页存档格式；论文用它抽样估算评论区在真实网页中的出现率。"},
        {"term": "Dolma 3", "definition": "OLMo团队的开源预训练语料；论文用它复现过滤管线并对比维基切片占比（0.067%）。"},
    ],
    "method_subsections": [
        {"title": "攻击面：从改维基到评论区规模化注入", "body": "既有投毒多针对维基百科等已知小比例源（Dolma3仅占0.067%）。论文转向第三方内容注入：攻击者用Selenium等自动化在公开评论区批量留言，恶意文本直接写进页面静态HTML，随异构网页域大规模分布——不需要控制目标站点。"},
        {"title": "HALFLIFE三阶段概率链", "body": "S1注入：页面是否可注入（Common Crawl抽样测评论出现率）；S2捕获：注入内容爬取后是否仍在提取文本中（沙盒替换实验）；S3过滤：是否通过语言识别、质量分类、主题分类等Dolma3/AllDressed管线。端到端inclusion = P(injectable)×P(captured|injectable)×P(not filtered|injectable)。"},
        {"title": "受控scaling实验：存活毒样对模型的影响", "body": "在已知inclusion概率下，论文还做受控scaling实验：用自然格式（更像正常评论）的毒样评估对预训练和指令微调模型生成的影响，并对比程序化广告向量（HALFLIFE判定不可行）证明并非所有注入都有效。"},
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {"看什么": "可注入面", "论文证据": "Common Crawl 200个WARC文件、181,857页扫描：3.4%页面含评论平台签名，P(injectable)=0.034。", "飞哥判断": "评论区不是每个角落都有，但3.4%在网页级投毒里已经是很大的攻击面。"},
            {"看什么": "提取存活", "论文证据": "沙盒注入验证：71.9%注入评论在HTML文本提取后仍保留（P(captured|injectable)=0.719）。", "飞哥判断": "爬取管线不会自动洗掉评论——多数毒样会进纯文本。"},
            {"看什么": "过滤存活", "论文证据": "复现Dolma3过滤：28.8%含评论页面通过完整过滤；自然评论替换为对抗内容对过滤存活无显著影响。", "飞哥判断": "质量分类器对『看起来像正常评论』的毒样并不敏感——这是最令人不安的发现。"},
            {"看什么": "端到端影响面", "论文证据": "端到端inclusion约0.15%；0.13% Common Crawl文档投毒影响面超过Dolma3维基切片0.067%；Souly等显示约250条毒文档可植入后门。", "飞哥判断": "攻击成本可算：要n条毒文档进训练集，需尝试约n/0.0015次注入——在自动化评论工具面前并非遥不可及。"},
        ],
    },
    "source_notes": [
        "概率链：论文§3-4与Figure 2；WARC抽样CC-MAIN-2025-51，181,857页。",
        "过滤管线：复现Dolma3/AllDressed（fasttext语言识别+质量分类器+WebOrganizer主题分类）。",
        "投稿时间：2026-07-16 17:56 UTC；Grok 0720 Top1热议；单位华盛顿大学+Ai2（PDF首页核验）。",
        "代码开源 github.com/VictoriaGraf/HalfLife；scaling实验为受控设置，非真实大规模投毒实测。",
    ],
    "so_what": "预训练安全讨论长期盯着『有人改了维基百科』，但这篇论文把镜头拉到更脏的现实：互联网上到处是能留言的页面，攻击者不需要拥有网站，只要能在评论区批量贴字。更麻烦的是，这些字大概率能熬过爬取和过滤——因为长得像正常用户评论。对数据团队和模型安全来说，HALFLIFE给了一条可量化的审计路径：别问『能不能投毒』，问『投进去之后能活多久』。",
    "feige_view": "给数据/模型安全团队的三个动作：①用HALFLIFE框架审计自己的爬取-过滤管线：对评论区、论坛嵌入、第三方widget分别估P(injectable)/P(captured)/P(not filtered)；②把第三方页面内容当一等风险源写进数据治理SOP，和版权/PII并列；③红队演练别只测prompt注入，加一条『网页评论投毒→爬取→微调』供应链攻击链，用自然格式毒样测过滤器的盲区。",
    "limitations": [
        "不过，端到端inclusion是概率估计而非真实大规模投毒实测：WARC抽样、沙盒注入和管线复现都有代理误差，实际攻击成功率可能因目标站点和过滤策略而异。",
        "不过，论文聚焦评论区这一具体向量，对其他第三方注入（用户生成内容widget、嵌入评论系统等）的泛化需要逐向量重跑HALFLIFE。",
        "不过，scaling实验在受控环境下评估生成影响，未展示对大规模生产模型的端到端后门激活率——从『毒样存活』到『可利用后门』仍有距离。",
    ],
    "related_theme_picks": {
        "theme": "模型安全与数据供应链",
        "intro": "本篇讲「网页投毒怎么活过过滤」；同线三篇各补一块：",
        "items": [
            {"arxiv_id": "2607.14166", "title_cn": "Agent审批门形同虚设", "one_liner": "安全治理的另一端：运行时控制原语能不能被强制执行。", "link": "https://arxiv.org/abs/2607.14166", "ready_date": "20260718"},
            {"arxiv_id": "2607.15263", "title_cn": "安全Agent评测该把成本当一等指标", "one_liner": "攻防Agent评测都要量化成本-收益，不能只看成功率。", "link": "https://arxiv.org/abs/2607.15263", "ready_date": "20260719"},
            {"arxiv_id": "2607.02514", "title_cn": "分布式攻击面与Agent安全", "one_liner": "Agent系统的攻击面不只模型权重，还在数据和工具链。", "link": "https://arxiv.org/abs/2607.02514", "ready_date": "20260705"},
        ],
    },
    "target_audience": [
        "负责预训练/微调数据爬取与过滤的ML平台与数据工程团队。",
        "做模型安全、红队、AI供应链审计的安全研究者与合规负责人。",
        "关注LLM可信性与训练数据治理的产品决策者。",
    ],
    "sales_use_cases": [
        "数据安全评审：用HALFLIFE三阶段框架量化第三方内容注入风险，替代『应该没事吧』式判断。",
        "回应对外模型安全质疑：用0.15% inclusion vs 0.067%维基切片论证网页级投毒影响面更大。",
        "红队服务方案设计：以评论区投毒为供应链攻击链案例，展示过滤盲区检测能力。",
    ],
    "objection_handling": [
        "客户说：「我们的过滤很强，不用担心。」→ 回应：论文复现Dolma3管线后28.8%含评论页面仍存活，自然格式对抗评论与正常评论过滤存活率无显著差异。",
        "客户说：「0.15%概率太低，攻击不现实。」→ 回应：Souly等先前工作显示约250条毒文档即可植入后门；按inclusion反推所需上游注入量在自动化评论工具能力范围内。",
    ],
    "copy_paste_lines": [
        "预训练投毒不只能改维基百科，还能在评论区批量贴字。",
        "HALFLIFE问的不是能不能投毒，是投进去之后能活多久。",
        "看起来像正常评论的毒样，过滤器的盲区。",
    ],
    "key_quotes": [
        "third-party webpage content as a possible vector for attacking language model pretraining",
        "even our estimated 0.15% inclusion probability over Common Crawl can affect more documents than the entire Wikipedia slice",
        "natural comments survive filtering at comparable rates to curated adversarial content",
    ],
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "P(injectable)=0.034（3.4%页面含评论）", "evidence": "200 WARC files, 181,857 pages scanned", "location": "Section 4.1 / Appendix E"},
            {"claim": "P(captured|injectable)=0.719", "evidence": "sandbox injection survives text extraction", "location": "Section 4.2"},
            {"claim": "28.8%含评论页面通过完整Dolma3过滤", "evidence": "replicated AllDressed filtering pipeline", "location": "Section 4.3"},
            {"claim": "端到端inclusion约0.15%，影响面超维基切片0.067%", "evidence": "HALFLIFE probability chain + Dolma3 composition", "location": "Section 4.4 / Figure 2"},
        ],
    },
}

def enrich(out_dir: Path, rich: dict, paper_key: str, date: str, html_title: str, html_conclusion: str):
    gen_path = out_dir / "generate_data.json"
    data = json.loads(gen_path.read_text())
    ledger_patch = rich.pop("evidence_ledger_patch", {})
    data.update({k: v for k, v in rich.items()})
    if ledger_patch.get("claim_evidence"):
        data.setdefault("evidence_ledger", {})["claim_evidence"] = ledger_patch["claim_evidence"]
    data.setdefault("discussion_notes", []).append("Enriched with rich fields via enrich_20260720.py")
    gen_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    card_path = out_dir / "card_data.json"
    card_path.write_text(gen_path.read_text())

    fused_card = ROOT / "fused" / f"{paper_key}_card_payload_{date}.json"
    fused_article = ROOT / "fused" / f"{paper_key}_article_payload_{date}.json"
    fused_card.write_text(gen_path.read_text())
    fused_article.write_text(gen_path.read_text())

    import subprocess, sys
    py = sys.executable
    subprocess.run([py, str(ROOT / "scripts/production/render_article.py"),
                    "--article-payload", str(fused_article),
                    "--out-dir", str(out_dir),
                    "--html-title", html_title,
                    "--html-conclusion", html_conclusion], check=True)
    subprocess.run([py, str(ROOT / "scripts/production/generate_cards.py"),
                    "--data", str(fused_card), "--out", str(out_dir)], check=True)
    subprocess.run([py, str(ROOT / "scripts/production/generate_cover.py"),
                    "--data", str(fused_card),
                    "--out", str(out_dir / "cover_235.png")], check=True)
    subprocess.run([py, str(ROOT / "scripts/production/render_article_wechat_safe.py"),
                    "--article-payload", str(fused_article),
                    "--out-dir", str(out_dir)], check=True)
    ledger_src = ROOT / "fused" / f"{paper_key}_evidence_ledger_{date}.json"
    if ledger_src.exists():
        ledger = json.loads(ledger_src.read_text())
        ledger["claim_evidence"] = data.get("evidence_ledger", {}).get("claim_evidence", [])
        (out_dir / "evidence_ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

if __name__ == "__main__":
    enrich(
        ROOT / "outputs/ready/20260720/2607.15257",
        dict(SEARCHOS_RICH),
        "searchos", "20260720",
        "搜索Agent老在同一条死胡同里绕圈？SearchOS把进度外挂成证据图，WideSearch F1冲到80.3",
        "信息检索Agent的瓶颈不只在模型会不会搜，更在系统有没有把进度、证据和失败记忆外化成可共享状态——SearchOS用关系型schema补全+四元状态管理+中间件Harness，在WideSearch和GISA上六个headline F1全领先。",
    )
    enrich(
        ROOT / "outputs/ready/20260720/2607.15267",
        dict(HALFLIFE_RICH),
        "halflife", "20260720",
        "评论区也能给预训练数据投毒？华盛顿大学HALFLIFE：0.15%存活率影响面已超过整本维基百科",
        "预训练投毒不只能改维基百科——公开评论区这种第三方内容注入，经过爬取和过滤后仍有可观存活率，HALFLIFE框架把注入→捕获→过滤三阶段概率化，给数据供应链安全上了量化尺子。",
    )
    print("enriched both")
