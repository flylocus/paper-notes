#!/usr/bin/env python3
"""One-off enrichment for 20260726 paper-notes payloads (PATS + ICAE-Bench)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260726"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


PATS_RICH = {
    "A_research_problem": "长程Agent RL里，弱策略常反复撞同一失败，整组rollout缺少可学习对比；现有技能方法多把技能当可检索/可内化的部署资产，而不是按当前策略调节的临时训练支持。结果是：要么引导不足、采样全灭；要么提示过满、行为方差塌缩。",
    "B_core_contributions": [
        "把技能重定义为策略感知、可丢弃的训练脚手架，而非永久记忆模块",
        "用组级成败证据驱动EXPAND/REVISE/COMPRESS，弱策略多引导、强策略少提示",
        "部署期零脚手架成本：训练增益在移除支持后仍保留",
        "在ALFWorld/WebShop与七项搜索QA上验证样本效率与token节省",
    ],
    "C_method_framework": "每轮先冻结脚手架快照条件化采样；轨迹用环境奖励走标准GRPO/RLVR更新策略，同时把组内成败写成evidence cards，按任务类型能力与脚手架压力选择扩展、修订或压缩。编辑只对下一轮可见；部署时整库丢弃。",
    "D_key_results": [
        "相对同规模GRPO：ALFWorld SR最多+17.6，WebShop SR最多+18.6（1.5B/7B）",
        "部署交互token在ALFWorld下降约30.4%/38.7%，WebShop约31.7%/30.7%",
        "搜索QA上相对保留技能库的SkillRL少32.1% prompt tokens，且去掉训练脚手架",
        "1.5B ALFWorld消融：去掉在线脚手架约-7.14 SR；语义修订去掉伤害最大（约-12.62）",
    ],
    "E_industry_implications": [
        "Agent RL训练看板应跟踪脚手架压力与混合结果组占比，而不只看最终成功率",
        "把『训练期支持 vs 部署期能力』拆开验收，避免把提示依赖当成模型能力",
        "技能库产品优先做成可收缩课程，而不是永久塞进推理上下文",
    ],
    "F_one_line_judgement": "Agent RL缺的不是更多固定技能，而是能随策略强弱伸缩、部署时可丢弃的训练脚手架。",
    "glossary": [
        {"term": "Training scaffold / Bank", "definition": "训练期注入的临时文本支持集合；按策略证据动态改写，部署时整库移除。"},
        {"term": "Evidence card", "definition": "由最新rollout组对比成功与失败行为生成的证据卡，用于决定下一轮支持强度与内容。"},
        {"term": "EXPAND / REVISE / COMPRESS", "definition": "控制器编辑模式：扩展缺失引导、语义修订、压缩冗余；避免单调撤退或无限堆积。"},
        {"term": "RLVR / GRPO", "definition": "用可验证环境奖励做组相对策略优化；PATS不改奖励与优化器，只改采样上下文。"},
        {"term": "SkillRL / SKILL0", "definition": "对照：保留或按日程撤回技能库的方法；PATS强调脚手架可丢弃且随策略自适应。"},
        {"term": "Mixed-outcome groups", "definition": "同组rollout既有成功也有失败，才能提供组相对更新所需的对比信号。"},
    ],
    "method_subsections": [
        {
            "title": "问题：技能该服务下一组采样，而不是永久存在",
            "body": "推理要立刻成功，RL要有可学差异。固定技能库可能提高即时成功率，却压缩组内对比；PATS把支持当作采样控制面。",
        },
        {
            "title": "闭环：冻结快照采样 → 更新策略 → 改脚手架",
            "body": "同轮rollout只读冻结Bank；证据与能力指标驱动下一快照的EXPAND/REVISE/COMPRESS，避免编辑泄漏进当轮轨迹。",
        },
        {
            "title": "验收：部署必须裸奔",
            "body": "主结果在无脚手架条件下报告；带脚手架行只作诊断，防止把训练提示误读成产品能力。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果 vs GRPO（Table1）",
                "论文证据": "ALFWorld SR +12.9/+17.6；WebShop SR +3.5/+18.6；交互token下降约30%–39%。",
                "飞哥判断": "增益同时抬成功率并缩短部署交互，不只是堆更多提示。",
            },
            {
                "看什么": "搜索QA权衡（Table2）",
                "论文证据": "去掉脚手架后相对SkillRL少32.1% prompt tokens，平均分仍具竞争力。",
                "飞哥判断": "比的是『性能–上下文』权衡，不是堆技能库刷分。",
            },
            {
                "看什么": "在线适应消融（Table3）",
                "论文证据": "去在线脚手架约-7.14；去语义修订约-12.62；冻结/只扩展都伤。",
                "飞哥判断": "关键在随策略改写支持，而不是初始化一次就完。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主实验在ALFWorld/WebShop与受控搜索QA；证据卡依赖任务评测器。",
                "飞哥判断": "开放互联网/代码仓外推要打折；先验证评测器可靠性。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table1 vs GRPO；Table2搜索QA与32.1% token；Table3在线消融。",
        "投稿/版本戳：arXiv:2607.21419v1 [cs.AI] 23 Jul 2026；ChatGPT 0725 backlog #3 / 本日合成主发。",
        "单位：Peking University · Tencent。",
        "证据边界：模拟环境；评测器质量；静态技能库早期也可能有用但后期伤对比。",
    ],
    "so_what": "说白了，Agent RL的技能不该默认『越全越好』。PATS证明：支持强度应跟着策略能力走——弱时打开路径，强时收回提示，最后还能在裸部署里保住收益。",
    "feige_view": "三个动作：①训练日志加『脚手架压力/混合结果组』面板；②验收强制跑无脚手架checkpoint；③技能产品设计成可收缩课程，而不是永久RAG片段。",
    "limitations": [
        "不过，主结果仍在ALFWorld/WebShop与受控搜索设定，开放网页与真实代码仓外推需折扣。",
        "不过，evidence card质量依赖任务评测器；评测器偏了，脚手架会学歪。",
        "不过，过早或过晚撤脚手架都可能回退；生产上要有按验证曲线的退出策略。",
    ],
    "related_theme_picks": {
        "theme": "Agent训练控制面",
        "intro": "本篇讲训练期可丢弃脚手架；同线可对照：",
        "items": [
            {"arxiv_id": "2607.21557", "title_cn": "真实Harness里做端到端RL", "one_liner": "另一头：部署用什么脚手架，就在什么脚手架里训。", "link": "https://arxiv.org/abs/2607.21557", "ready_date": "20260725"},
            {"arxiv_id": "2607.21461", "title_cn": "验证驱动的深研状态", "one_liner": "运行时约束审计 vs 训练时策略脚手架，两端互补。", "link": "https://arxiv.org/abs/2607.21461", "ready_date": "20260725"},
            {"arxiv_id": "2607.21217", "title_cn": "交互式项目构建评测", "one_liner": "训练控采样，评测控模糊需求下的交付。", "link": "https://arxiv.org/abs/2607.21217", "ready_date": "20260726"},
        ],
    },
    "target_audience": [
        "做Agent RL/技能库/课程学习的研究与平台团队。",
        "关心训练提示依赖是否污染部署能力的产品负责人。",
        "评估技能记忆产品该不该永久进上下文的技术决策者。",
    ],
    "sales_use_cases": [
        "回应『我们加了技能库』：用+18.6与token下降说明关键是可收缩训练支持。",
        "方案评审：要求无脚手架验收与混合结果组指标。",
        "成本沟通：部署token下降约三成，不是只吹成功率。",
    ],
    "objection_handling": [
        "客户说：『不就是curriculum吗？』→ 回应：任务分布与奖励不变，变的是临时上下文；且部署必须拆掉。",
        "客户说：『SkillRL分更高。』→ 回应：它常保留测试期技能；PATS比的是去掉脚手架后的权衡。",
    ],
    "copy_paste_lines": [
        "Agent RL别只会堆技能库，先让脚手架能随策略强弱伸缩。",
        "训练期给提示，部署期拆掉——这才是可验收的能力。",
        "WebShop上相对GRPO最多+18.6 SR，同时交互token下降约三成。",
    ],
    "key_quotes": [
        "policy-aware training scaffolding",
        "skills as a dynamic training scaffold",
        "the training scaffold is discarded at deployment",
    ],
    "score_rationale": "PATS把技能从部署资产改写成可丢弃的策略感知训练脚手架：弱策略加引导、强策略收缩上下文，部署期零成本。ALFWorld/WebShop与搜索QA数字清楚，消融指向在线适应。扣分在模拟环境与评测器依赖。Impact高：直击Agent RL采样失败。Novelty高：政策中心脚手架而非技能中心库。Evidence中高：多表+消融。Applicability高：训练配方可迁移。Reusability中高：控制器可复用，环境外推待证。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "ALFWorld SR相对GRPO +12.9/+17.6；WebShop SR +3.5/+18.6", "evidence": "Table 1 main results vs GRPO", "location": "Table 1"},
            {"claim": "部署交互token下降约30%–39%", "evidence": "Table 1 avg tokens discussion", "location": "Table 1 / §4"},
            {"claim": "搜索QA相对SkillRL少32.1% prompt tokens", "evidence": "Table 2 Avg. Prompt Tok.", "location": "Table 2"},
            {"claim": "去在线脚手架约-7.14 SR；去REVISE约-12.62", "evidence": "Table 3 ablations on 1.5B ALFWorld", "location": "Table 3"},
            {"claim": "F段限制：模拟环境、评测器、撤架时机", "evidence": "Limitations + experiment scope", "location": "Limitations / §4"},
        ]
    },
}


ICAE_RICH = {
    "A_research_problem": "vibe coding从模糊产品意图起步：Agent要澄清、规划、调试并交付可运行仓库。但主流Coding Agent基准仍给静态、完整规格，测的是『按说明实现』，不是『在互动中把不完整意图做成可测产品』。",
    "B_core_contributions": [
        "把评测从静态规格实现推进到交互式0到1项目构建",
        "用真实开源仓接地模糊性，避免无约束空想需求",
        "User Agent Data约束模拟用户，防编造需求与实现泄露",
        "480任务/12语言 + 黑盒行为测试与多维诊断，开源评测资产",
    ],
    "C_method_framework": "金仓→可执行行为与GroundPRD→模糊化隐藏约束进User Agent Data→ultimate image去掉金码/测试→评测时Coding Agent向受控User Agent提问（最多16轮）→黑盒用例+结构/语义/交互诊断打分。",
    "D_key_results": [
        "Claude-Opus-4.8全量Overall约38.2%、Lite约48.2%；GPT-5.5接近；顶尖模型远未饱和",
        "交互只能收回部分相对GroundPRD的差距；约束覆盖高不等于pass率高",
        "仓库级Clean极少（每模型约1–13/480），失败常在隐藏约束、边界与长程集成",
        "公开资产：https://github.com/ALEX-nlp/ICAE-EVAL",
    ],
    "E_industry_implications": [
        "Coding Agent验收应含『模糊需求→澄清→可测交付』，而不只看SWE-bench式修issue",
        "产品评测要分开看：问得好、记得住、落得下——三者不可互相替代",
        "内部基准可借鉴：从金仓抽隐藏约束+黑盒用例，而不是只写完整PRD",
    ],
    "F_one_line_judgement": "Coding Agent该测的不是『会不会写代码』，而是模糊需求下能否通过互动交付可运行项目。",
    "glossary": [
        {"term": "GroundPRD", "definition": "从金仓行为提炼的完整产品需求文档，作为信息充分时的上界参照。"},
        {"term": "Fuzzy PRD / L1–L3", "definition": "逐步隐藏约束后的模糊需求层级；L1信息最少，L3更接近GroundPRD。"},
        {"term": "User Agent Data", "definition": "基准预写的隐藏约束记录；模拟用户只能据此回答，不能编造或泄金实现。"},
        {"term": "Ultimate image", "definition": "保留运行依赖但去掉金码/原测试的评测容器镜像。"},
        {"term": "Overall / Clean", "definition": "Overall为用例级通过率；Clean要求仓库级全部用例通过，远更严格。"},
        {"term": "Public / Hidden cases", "definition": "可见示例用例 vs 隐藏行为用例；模糊设定下Public常需交互找回。"},
    ],
    "method_subsections": [
        {
            "title": "接地模糊：从精确仓库『藏』出不完整意图",
            "body": "先保证金仓Docker可测，再写成GroundPRD与黑盒用例，最后隐藏部分约束——模糊来自真实产品，而不是空写一句『做个XX』。",
        },
        {
            "title": "控制交互：User Agent只泄露预写记录",
            "body": "最多16问，答案路由到User Agent Data，避免自由模型胡编需求或泄露实现细节。",
        },
        {
            "title": "评价开放实现：约束行为，不约束长什么样",
            "body": "黑盒功能为主，辅以语义/API、结构、设计与交互诊断，允许不同内部设计。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "全量主结果（Table VI）",
                "论文证据": "Claude-Opus-4.8 Overall约38.2%；GPT-5.5接近；多数模型更低。",
                "飞哥判断": "模糊项目构建远未饱和，不是刷分玩具。",
            },
            {
                "看什么": "交互 vs 完整规格",
                "论文证据": "GroundPRD上界更强；RecoveredPRD仍常低于GroundPRD。",
                "飞哥判断": "会提问≠会交付；关键在组织答案并落到仓库。",
            },
            {
                "看什么": "仓库级Clean",
                "论文证据": "每模型约1–13/480仓库全过；远严于用例级Overall。",
                "飞哥判断": "产品验收要用仓库级标准，别被平均pass率安慰。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "任务来自反向构造；User Agent≠真人；黑盒难覆盖可维护性。",
                "飞哥判断": "适合做相对能力诊断，不能直接当上线质量证明。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table VI/VII Overall；交互 vs GroundPRD分析；Clean计数。",
        "投稿/版本戳：arXiv:2607.21217v1 [cs.AI] 23 Jul 2026；ChatGPT 0725 backlog #4 / 本日合成主发。",
        "单位：Fudan University · Meituan Group · Singapore Management University · Shanghai Innovation Institute。",
        "资产：https://github.com/ALEX-nlp/ICAE-EVAL",
        "证据边界：自动User Agent、反向构造偏差、可维护性/架构质量覆盖不足。",
    ],
    "so_what": "说白了，Coding Agent下一张真正难的考卷不是HumanEval，也不是只修issue，而是：用户说不清楚时，你能不能问明白、记下来、做成能跑的项目。ICAE-Bench把这张考卷标准化了。",
    "feige_view": "三个动作：①内部评测加『模糊PRD+隐藏约束』套件；②看板拆开澄清质量/约束保持/黑盒通过；③别再用完整规格分数替代vibe coding交付能力。",
    "limitations": [
        "不过，自动User Agent仍难模拟真人需求漂移、偏好冲突与含糊表达。",
        "不过，从现有仓库反向构造，可能偏向『可还原』产品而非全新品类。",
        "不过，黑盒通过不等于可维护与长期架构质量，需另补审查。",
    ],
    "related_theme_picks": {
        "theme": "Coding Agent × Harness工程",
        "intro": "本篇讲模糊需求下的项目交付评测；同线可对照：",
        "items": [
            {"arxiv_id": "2607.13285", "title_cn": "Harness行为地图与定位", "one_liner": "改脚手架前先找行为落点；本篇测交付能力。", "link": "https://arxiv.org/abs/2607.13285", "ready_date": "20260726"},
            {"arxiv_id": "2607.21557", "title_cn": "真实Harness端到端RL", "one_liner": "已发：在真实脚手架里训Agent。", "link": "https://arxiv.org/abs/2607.21557", "ready_date": "20260725"},
            {"arxiv_id": "2607.21419", "title_cn": "策略感知训练脚手架", "one_liner": "训练侧可丢弃支持；本篇是评测侧模糊交付。", "link": "https://arxiv.org/abs/2607.21419", "ready_date": "20260726"},
        ],
    },
    "target_audience": [
        "做Coding Agent/IDE Agent产品与评测的团队。",
        "关心vibe coding交付质量与验收标准的工程负责人。",
        "建设内部Agent基准与红队套件的平台同学。",
    ],
    "sales_use_cases": [
        "回应『我们SWE-bench很高』：用Overall约38%说明模糊项目构建是另一维能力。",
        "方案评审：要求模糊需求套件与仓库级Clean指标。",
        "对标沟通：开源ICAE-EVAL可做相对诊断，不替代上线质量门禁。",
    ],
    "objection_handling": [
        "客户说：『不就是加个聊天用户吗？』→ 回应：关键是金仓接地+受控泄露+黑盒可测，不是自由对话。",
        "客户说：『Overall不够高说明基准太难。』→ 回应：难才有分辨力；并看Clean与GroundPRD差距定位瓶颈。",
    ],
    "copy_paste_lines": [
        "Coding Agent别只测写代码，要测模糊需求下的项目交付。",
        "会提问不等于会交付：约束要记得住、落得下。",
        "480任务里仓库级全过往往只有个位数——别被平均pass率安慰。",
    ],
    "key_quotes": [
        "interactive project-building settings",
        "ambiguity from precise real open-source repository",
        "higher constraint coverage does not automatically translate into higher pass rate",
    ],
    "score_rationale": "ICAE-Bench把Coding Agent评测推到模糊意图下的交互式项目构建：480/12语言、接地User Agent、黑盒+多维诊断，开源可复用。主结果暴露顶尖模型仍低Overall与极低Clean。扣分在自动用户与反向构造外推。Impact高：对准vibe coding真场景。Novelty中高：交互0到1基准设计完整。Evidence高：规模与表格扎实。Applicability中高：可直接复用评测。Reusability中高：管线可迁移到内部金仓。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "Claude-Opus-4.8全量Overall约38.2%，Lite约48.2%", "evidence": "Table VI / Table VII main results", "location": "Table VI/VII"},
            {"claim": "交互只能部分追平GroundPRD；覆盖≠pass", "evidence": "Fuzzy vs GroundPRD / RecoveredPRD analysis", "location": "§Results / Fig.6-8"},
            {"claim": "Clean约1–13/480", "evidence": "Failure-mode / Clean repository discussion", "location": "§Results"},
            {"claim": "480任务、12语言、开源ICAE-EVAL", "evidence": "Abstract + GitHub link", "location": "Abstract / resources"},
            {"claim": "F段限制：User Agent、反向构造、可维护性", "evidence": "Limitations + ChatGPT notes", "location": "Limitations"},
        ]
    },
}


HANDBOOK_RICH = {
    "A_research_problem": "生产级Agent harness行为分散在多文件与执行阶段；修改请求描述『做什么』，仓库按文件组织。人和coding agent都要先做behavior localization——找全实现落点——否则改不全、改偏、还烧token。",
    "B_core_contributions": [
        "把behavior localization定义为harness演进前置瓶颈",
        "Harness Handbook：按系统行为组织实现知识并链到源码（L1–L3）",
        "BGPD：行为引导的渐进披露与源码再校验工作流",
        "在Codex/Terminus-2共60条修改请求上验证定位与规划质量",
    ],
    "C_method_framework": "静态分析抽取程序事实，再经LLM行为结构化生成L1系统概览→L2阶段组件→L3源码单元；定位走BGPD：先行为层收窄，再沿调用扩候选，最后回仓库校验locator。评测对比Baseline直翻仓库 vs Handbook-Assisted规划。",
    "D_key_results": [
        "规划胜率：Codex 38.3% vs 28.3%；Terminus-2 45.6% vs 26.7%（三裁判一致方向）",
        "planner token：Codex约-12.7%，Terminus约-8.6%",
        "相对Opus参考：Codex文件级F1 +15.2、Wrong -22.2；符号级F1 +18.8、Wrong -25.9",
        "散落/跨模块/冷门路径改动增益最大；项目页 https://ruhan-wang.github.io/Harness-Handbook/",
    ],
    "E_industry_implications": [
        "Harness工程验收先看『行为→代码』地图是否可维护，而不只看功能清单",
        "给coding agent改脚手架时，优先提供行为索引而非整仓长上下文",
        "散落路径/跨模块/冷门分支的改动，最该上行为定位层",
    ],
    "F_one_line_judgement": "改Agent Harness的第一难关不是写补丁，而是找到行为落在哪些代码点。",
    "glossary": [
        {"term": "Behavior localization", "definition": "在修改请求下，找全实现该行为的所有代码落点（文件/符号级）。"},
        {"term": "Harness Handbook", "definition": "行为中心的L1–L3文档树，把『系统做什么』链到源码locator。"},
        {"term": "BGPD", "definition": "Behavior-Guided Progressive Disclosure：从高层行为逐步披露到实现细节，并回仓库校验。"},
        {"term": "L1 / L2 / L3", "definition": "系统概览 → 阶段/组件概览 → 源码单元深潜；按需展开。"},
        {"term": "Terminus-2 / Codex", "definition": "评测用的两个开源agent harness；分别对应function-as-leaf与file-as-leaf模式。"},
        {"term": "Wrong ↓", "definition": "预测计划与参考计划零重叠的请求占比；越低越好。"},
    ],
    "method_subsections": [
        {
            "title": "先钉瓶颈：行为落点找不到，补丁无从谈起",
            "body": "请求说行为，仓库按文件。现有搜索/长上下文仍把『行为→代码』映射留给人和agent自己拼。",
        },
        {
            "title": "Handbook：按行为重组，而不是按目录复述",
            "body": "L1看全局执行模型，L2看阶段职责与状态，L3落到可校验源码条目；跨阶段状态另有寄存器视图。",
        },
        {
            "title": "BGPD：渐进披露 + 仓库仍是权威",
            "body": "先用Handbook收窄候选，再打开当前仓库校验locator；失效条目冻结，避免过时地图误导编辑。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "规划胜率（Fig.3）",
                "论文证据": "Codex 38.3% vs 28.3%；Terminus-2 45.6% vs 26.7%；三裁判同向。",
                "飞哥判断": "行为地图先抬『改哪里的计划质量』，不是空谈可读性。",
            },
            {
                "看什么": "Token成本",
                "论文证据": "Codex约-12.7%，Terminus约-8.6% planner tokens。",
                "飞哥判断": "更好计划并不靠塞更多上下文。",
            },
            {
                "看什么": "定位指标（Table1）",
                "论文证据": "Codex相对Opus参考：文件F1 +15.2、Wrong -22.2；符号F1 +18.8、Wrong -25.9。",
                "飞哥判断": "关键增益在少漏落点——正好打中散落行为。",
            },
            {
                "看什么": "证据边界",
                "论文证据": "主评测是规划/定位；完整落地改写与长期Handbook维护成本另议。",
                "飞哥判断": "先当工程导航层试点，再谈全自动修harness。",
            },
        ],
    },
    "source_notes": [
        "主数字：Fig.3胜率与token；Table1定位F1/Wrong；Fig.5按请求类型/难度。",
        "投稿/版本戳：arXiv:2607.13285v1 [cs.AI] 14 Jul 2026；Grok/X backlog，本日与ICAE配对主发。",
        "单位：Tencent HY LLM Frontier · Indiana University · UMD · UGA · NUS。",
        "资产：https://ruhan-wang.github.io/Harness-Handbook/",
        "证据边界：规划质量≠端到端补丁成功率；Handbook同步维护成本需产品化验证。",
    ],
    "so_what": "说白了，Agent工程下一刀不只是『换更强模型』或『在真实harness里训』，还有『让人和coding agent找得到该改的行为落点』。Handbook把这张行为地图做成可导航资产。",
    "feige_view": "三个动作：①给内部OpenClaw/Codex类脚手架建行为索引MVP；②改动验收加『落点召回』而不只看diff通过；③散落/跨模块需求优先走BGPD式导航，再开整仓搜索。",
    "limitations": [
        "不过，主结果是规划与定位指标，不等于端到端自动改完并通过回归。",
        "不过，Handbook需与仓库同步；locator失效与重建成本要进运维账。",
        "不过，评测集中在两个开源harness、各30请求，更大生产仓外推需折扣。",
    ],
    "related_theme_picks": {
        "theme": "Coding Agent × Harness工程",
        "intro": "本篇讲行为定位地图；同线可对照：",
        "items": [
            {"arxiv_id": "2607.21217", "title_cn": "模糊需求下的项目交付评测", "one_liner": "找到落点之后：coding agent能否交互交付可测仓库。", "link": "https://arxiv.org/abs/2607.21217", "ready_date": "20260726"},
            {"arxiv_id": "2607.21557", "title_cn": "真实Harness端到端RL", "one_liner": "已发：结构可读之外，还要能在真实脚手架里训。", "link": "https://arxiv.org/abs/2607.21557", "ready_date": "20260725"},
            {"arxiv_id": "2607.21419", "title_cn": "策略感知训练脚手架", "one_liner": "训练侧可丢弃支持；本篇是演进侧行为地图。", "link": "https://arxiv.org/abs/2607.21419", "ready_date": "20260726"},
        ],
    },
    "target_audience": [
        "维护OpenClaw/Codex/Claude Code类harness的平台与基础架构团队。",
        "用coding agent改Agent脚手架的工程负责人。",
        "评估『仓库地图/行为索引』产品化价值的技术决策者。",
    ],
    "sales_use_cases": [
        "回应『我们给了长上下文』：用token下降+Wrong下降说明关键是行为索引，不是塞更多文件。",
        "方案评审：把behavior localization列入harness演进验收。",
        "对标OpenForge已发稿：那边讲『在harness里训』，这边讲『改harness前先定位』。",
    ],
    "objection_handling": [
        "客户说：『不就是更好的repo map吗？』→ 回应：组织轴是行为与执行阶段，不是文件树复述，且有源码再校验。",
        "客户说：『胜率也就四成。』→ 回应：相对Baseline的抬升与Wrong下降更关键；且难例（散落/跨模块）增益更大。",
    ],
    "copy_paste_lines": [
        "改Harness别先翻仓库，先找行为落点。",
        "更好的编辑计划，可以更少planner token。",
        "Codex上文件级Wrong从37.0降到14.8——少漏落点才是关键。",
    ],
    "key_quotes": [
        "behavior localization is therefore a central bottleneck in harness evolution",
        "organizes implementation knowledge around system behaviors",
        "improves behavior localization and edit-plan quality while using fewer planner tokens",
    ],
    "score_rationale": "Harness Handbook把harness演进前置瓶颈钉成behavior localization，用行为中心地图+BGPD提升定位与规划、降低token。Codex/Terminus数字清楚。扣分在规划≠端到端改写、维护成本待证。Impact高：贴合生产harness演进。Novelty中高：行为轴重组。Evidence中高：双仓60请求+多指标。Applicability高：可直接试点行为索引。Reusability中：资产可迁移，同步运维有摩擦。",
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "Codex胜率38.3% vs 28.3%；Terminus-2 45.6% vs 26.7%", "evidence": "Figure 3 overall win rates", "location": "Figure 3 / §4.2.1"},
            {"claim": "planner token Codex约-12.7%，Terminus约-8.6%", "evidence": "Figure 3(c) token cost", "location": "Figure 3"},
            {"claim": "Codex文件F1 +15.2、Wrong -22.2；符号F1 +18.8、Wrong -25.9", "evidence": "Table 1 vs Opus 4.8 reference", "location": "Table 1"},
            {"claim": "散落/跨模块/冷门路径增益最大", "evidence": "Abstract + difficulty/type analysis", "location": "Abstract / Figure 5"},
            {"claim": "F段限制：规划≠端到端；维护成本；双仓外推", "evidence": "Limitations + experiment scope", "location": "Limitations / §4"},
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
    # publish pair for 20260726 (post OpenForge): Handbook + ICAE
    enrich_one(
        "2607.13285",
        "harness-handbook",
        HANDBOOK_RICH,
        "改Harness别先翻仓库：Handbook用行为地图做定位再编辑",
        "Agent能力不只看模型，还看harness能不能被准确定位与演进——Harness Handbook把行为映射到代码；Codex/Terminus胜率抬升且planner token下降约9%–13%。",
    )
    enrich_one(
        "2607.21217",
        "icae",
        ICAE_RICH,
        "Coding Agent别只测写代码：ICAE-Bench用模糊需求测交互式项目交付",
        "vibe coding的关键不是补全函数，而是在模糊意图下澄清、落地并交付可测仓库——ICAE-Bench用480任务显示顶尖模型Overall仍约38%。",
    )
    print("enriched handbook + icae")


if __name__ == "__main__":
    main()
