#!/usr/bin/env python3
"""One-off enrichment for 20260811 paper-notes payloads (ADIAS + MemPrism)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "20260811"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


ADIAS_RICH = {
    "intro_lead": "",
    "A_research_problem": "自动化Agent设计多半以候选Agent为中心：每轮生成新版、跑评测、总结反馈。跨轮失败证据散落在版本记录里，修复进度隐式，容易重复无效干预、丢掉已经半修好的部分进展。",
    "B_core_contributions": [
        "提出issue-centric agent optimization：跨轮经验围绕问题而非候选版本组织",
        "ADIAS：持久issue state + issue-guided全码修改两机制",
        "五交互benchmark与消融：去掉issue state或退回candidate-centric最多掉40.7%",
    ],
    "C_method_framework": "ADIAS维护持久issue state（稳定身份、生命周期、证据、干预-结果史），再由issue-guided optimizer联合选定修复目标与改法，对完整Agent代码做聚焦修改，而不是每轮从候选历史里重新猜问题。",
    "D_key_results": [
        "DeepSeek-V4-Flash五benchmark平均78.4，超最强基线DGM-H 62.6，相对提升25.2%",
        "单任务：Tau-Bench 81.3 / ALFWorld 94.0 / TextCraft 91.0 / WebShop 69.4 / ScienceWorld 56.3，均为最优",
        "Archive-Wide Synthesis消融平均掉40.7%；Tau-Bench上四backbone均领先",
    ],
    "E_industry_implications": [
        "自改进流水线应维护问题账本，而不是只存Agent版本与轨迹摘要",
        "验收时同时看：未关闭issue是否下降、无效干预是否被复用、改动是否可归因",
        "全码自动改必须配回归门禁与变更审计，否则修复能力会变成新事故源",
    ],
    "F_one_line_judgement": "这篇最适合做Agent harness与自动化设计的团队：用持久issue state指导全码修改，五benchmark平均78.4 vs DGM-H 62.6（相对+25.2%）；不过issue误诊会污染后续修复，全码改还有回归与安全成本。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "ADIAS", "definition": "Automated Design of Interactive Agentic Systems：issue-centric的全码Agent自动设计框架。"},
        {"term": "Issue-centric optimization", "definition": "以持久问题状态组织跨轮经验，而不是以候选Agent版本为中心。"},
        {"term": "Persistent issue state", "definition": "记录issue身份、生命周期、证据与干预-结果史的显式优化状态。"},
        {"term": "Candidate-centric", "definition": "每轮围绕生成更好候选Agent组织反馈，修复进度隐式。"},
        {"term": "DGM-H", "definition": "论文最强自动化基线之一；五benchmark平均62.6。"},
        {"term": "Archive-Wide Synthesis", "definition": "消融：用原始候选档案合成下一步，去掉耐久issue state。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：版本历史≠修复进度",
            "body": "知道v7比v6好，并不等于知道哪个issue还开着、哪次干预无效。候选中心优化把这些信息埋进轨迹摘要。",
        },
        {
            "title": "问题账本：把bug tracker写进优化循环",
            "body": "每个issue有稳定身份、状态、证据与干预史。下一轮先选打哪个未关闭问题，再决定怎么改。",
        },
        {
            "title": "全码修改，但要可归因",
            "body": "允许改完整Agent代码以扩大设计空间；同时用聚焦修订，让后续行为变化更容易归因到目标issue。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果",
                "论文证据": "五benchmark平均78.4 vs DGM-H 62.6，相对+25.2%。",
                "飞哥判断": "不是单点刷分；五环境全赢，且效率也最高。",
            },
            {
                "看什么": "强项任务",
                "论文证据": "ALFWorld 94.0、TextCraft 91.0；效率8.95 / 9.01。",
                "飞哥判断": "长程规划与过程控制场景，issue账本杠杆最大。",
            },
            {
                "看什么": "消融",
                "论文证据": "Archive-Wide Synthesis平均掉40.7%；去掉round-level diagnosis后ALFWorld 94.0→63.4。",
                "飞哥判断": "光有候选档案不够；问题状态必须真正控优化。",
            },
            {
                "看什么": "跨模型",
                "论文证据": "Tau-Bench上DeepSeek/GLM/Hy3/GPT-5.4均第一，均分85.95。",
                "飞哥判断": "收益更像优化状态设计，不只是某一backbone技巧。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 1 平均78.4 vs DGM-H 62.6（相对+25.2%）；单任务81.3/94.0/91.0/69.4/56.3；Table 3 Archive-Wide -40.7%。",
        "版本戳：arXiv:2608.06410v1 [cs.AI]；ChatGPT 0810批次 #1（今日主发）。",
        "单位：University of Cambridge；LIGHTSPEED；Independent Researcher。",
        "开源入口：https://github.com/scylj1/adias/",
        "证据覆盖：五交互benchmark + 四backbone；真实长期软件Agent的issue规模外推仍有限。",
    ],
    "so_what": "说白了，做Agent自改进时先问系统有没有一份可继承的问题账本：未关闭issue、失败证据、有效/无效干预。没有它，你优化的往往是下一版候选，不是持续修复能力。",
    "feige_view": "对照近几期Harness-R1 / SkillHEX / SearchAuditor：技能与失败定位之后，还差一层——跨轮问题生命周期。ADIAS把这层做成可执行状态，而不是再多写几句反思prompt。",
    "limitations": [
        "issue合并错误会让后续修改持续受污染。",
        "全码自动修改带来回归、安全与版本管理成本。",
        "实验issue规模远小于真实长期软件Agent。",
        "优化预算固定为10轮；更长生命周期下的账本膨胀未充分验证。",
    ],
    "related_theme_picks": {
        "theme": "Harness自改进与运行时状态",
        "intro": "本篇讲问题账本驱动的全码自修；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.06745",
                "title_cn": "任务条件关系视图重组记忆",
                "one_liner": "同日配对：存到了还要按任务重组决策视图。",
                "link": "https://arxiv.org/abs/2608.06745",
                "ready_date": "20260811",
            },
            {
                "arxiv_id": "2608.05628",
                "title_cn": "假设驱动技能自进化",
                "one_liner": "0809：技能侧别一路贪心改，先做可证伪实验。",
                "link": "https://arxiv.org/abs/2608.05628",
                "ready_date": "20260809",
            },
            {
                "arxiv_id": "2608.05212",
                "title_cn": "长程搜索失败审计",
                "one_liner": "0808：终局答错时怎么定位关键错误步。",
                "link": "https://arxiv.org/abs/2608.05212",
                "ready_date": "20260808",
            },
        ],
    },
    "target_audience": [
        "做Agent harness / 自动化设计的研究工程团队。",
        "关心自改进流水线验收与回归门禁的平台同学。",
        "评估「多轮改了却反复踩坑」事故的产品技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们已经加了反思和轨迹摘要』：先问跨轮问题状态有没有显式账本。",
        "方案评审：要求看未关闭issue趋势、无效干预复用率与改动归因，而不是只看下一版分数。",
        "训练沟通：用+25.2%与-40.7%消融说明问题状态比候选档案更关键。",
    ],
    "objection_handling": [
        "客户说：『多存几轮轨迹就够了。』→ 回应：档案里有证据，不等于优化器知道打哪个未关闭问题。",
        "客户说：『全码自动改太危险。』→ 回应：正因如此才要issue归因 + 回归门禁；否则危险来自不可审计的改动。",
    ],
    "copy_paste_lines": [
        "别再只记版本号，记未关闭问题。",
        "ADIAS：五benchmark平均78.4（相对DGM-H +25.2%）。",
        "去掉issue state，最多掉40.7%。",
    ],
    "key_quotes": [
        "outperforms the strongest baseline by 25.2% on average",
        "performance drops of up to 40.7%",
        "repair progress is carried forward as an explicit persistent issue state",
    ],
    "info": {
        "title": "ADIAS: Automated Design of Interactive Agentic Systems",
        "title_cn": "问题账本驱动的Agent harness自修",
        "link": "https://arxiv.org/abs/2608.06410",
        "authors": ["Lekang Jiang", "Bohan Tang", "Stephan Goetz", "Yiwen Guo"],
        "affiliations": ["University of Cambridge", "LIGHTSPEED", "Independent Researcher"],
    },
    "score": {
        "total": 9.1,
        "dimensions": [
            {"label": "重要性 Impact", "value": 1.9},
            {"label": "创新性 Novelty", "value": 1.9},
            {"label": "可验证性 Evidence", "value": 1.8},
            {"label": "产业可用性 Applicability", "value": 1.8},
            {"label": "可复用性 Reusability", "value": 1.7},
        ],
    },
    "score_rationale": "把Agent自改进从候选版本历史改成持久issue lifecycle，切中harness工程痛点。五benchmark平均78.4 vs DGM-H 62.6（+25.2%相对提升），消融掉issue state最多掉40.7%；有代码。误诊合并与全码修改回归风险使Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["重要性 Impact", "创新性 Novelty"],
        "lowest_dimensions": ["可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.9, "role": "highest", "rationale": "Agent自改进生产中最贵的是重复踩坑与进展丢失；问题账本直接打这个点。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "把优化对象从候选Agent切到issue lifecycle，接近工程bug tracker，而不是再堆反思。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "middle", "rationale": "五benchmark、跨模型与关键消融清楚；真实大规模issue外推仍弱。"},
            {"label": "产业可用性 Applicability", "value": 1.8, "role": "middle", "rationale": "有代码与全码修改路径；落地需回归审计配套。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "issue误诊污染与全码回归风险限制直接照搬。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "五benchmark平均78.4 vs DGM-H 62.6，相对提升25.2%", "evidence": "Table 1 / §5.1", "location": "Table 1"},
            {"claim": "单任务81.3 / 94.0 / 91.0 / 69.4 / 56.3均为最优", "evidence": "Table 1", "location": "Table 1"},
            {"claim": "Archive-Wide Synthesis平均掉40.7%", "evidence": "Table 3 / §5.2", "location": "Table 3"},
            {"claim": "去掉round-level diagnosis后ALFWorld 94.0→63.4", "evidence": "§5.2", "location": "§5.2"},
            {"claim": "Tau-Bench四backbone均第一，均分85.95", "evidence": "Table 2", "location": "Table 2"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260811 dual publish: ADIAS + MemPrism.",
        "Affiliations via overrides: Cambridge + LIGHTSPEED + Independent Researcher.",
        "Numbers verified from PDF Table 1–3 and §5.",
    ],
}


MEMPRISM_RICH = {
    "intro_lead": "",
    "A_research_problem": "长程Agent常把失败归咎于没存住。更隐蔽的失败是representation mismatch：相关证据在永久库里，但决策时看到的关系形态不对，策略仍然「看不见」。",
    "B_core_contributions": [
        "提出representation mismatch：存到/检索到不等于决策时形态对",
        "任务条件关系视图：持久事件流 + 动态光学working memory",
        "长程embodied/web基准 + 跨VLM迁移与token对照",
    ],
    "C_method_framework": "MemPrism把永久事件流与决策时working memory拆开。轻量view policy选择关系结构、证据范围、结果条件与粒度；确定性composer/render生成临时光学视图，交给冻结任务VLM；视图不回写永久层。",
    "D_key_results": [
        "ALFWorld：SFT+GRPO SR 40.71%，超LangMem 38.27%约2.44点；相对SFT再+6.42点",
        "Mind2Web整体动作准确率12.87%（Full History 8.79%，+4.08）；EB-ALFRED平均SR 17.7%（Full History 10.3%，+7.4）",
        "≤50步阈值：相对Full History SR +9.3点，prompt token约降33.6%（797 vs 1201）；view policy可跨未见VLM迁移",
    ],
    "E_industry_implications": [
        "评测memory时除召回率，还要问当前子任务看到的关系视图是否对口",
        "部署上把永久存储与决策时重组拆开，避免整段历史原样塞进上下文",
        "给view policy单独监控：选错关系等于系统性看不见正确证据",
    ],
    "F_one_line_judgement": "这篇最适合做长程Agent memory的团队：永久事件流按任务重组为光学working memory；ALFWorld 40.71%超LangMem 2.44点，长轨迹收益更大且token可降约33.6%。不过view policy选错时，正确事实仍可能看不见。",
    "F_section_title": "F. 结论与边界",
    "glossary": [
        {"term": "MemPrism", "definition": "Task-conditioned relational memory：按当前任务动态构造关系视图的工作记忆框架。"},
        {"term": "Representation mismatch", "definition": "证据已存储/检索，但未按当前决策所需关系形态组织，导致策略用不上。"},
        {"term": "View policy", "definition": "选择关系结构、证据范围、结果条件与粒度的轻量策略。"},
        {"term": "Optical working memory", "definition": "把关系结构渲染成临时图像式工作记忆，供冻结VLM消费。"},
        {"term": "Event stream", "definition": "只追加真实交互事实的持久层；临时视图不回写。"},
        {"term": "LangMem", "definition": "ALFWorld对照中的最强外部memory基线之一（SR 38.27%）。"},
    ],
    "method_subsections": [
        {
            "title": "痛点：召回成功≠决策可用",
            "body": "同一批历史，做环路检测、实体状态跟踪、失败归因时需要不同关系切面。固定chunk检索只解决「拿到了」，不解决「怎么摆」。",
        },
        {
            "title": "两层记忆：永久事实 vs 临时视图",
            "body": "底层只记事件流；决策时按任务生成关系视图。视图临时、不回写，避免把一次组织错误固化进永久库。",
        },
        {
            "title": "光学呈现不是炫技",
            "body": "二维布局用邻近、对齐、箭头与高亮编码依赖与结果；Fixed Optical相对Fixed Text已有独立增益，动态组织再叠加。",
        },
    ],
    "result_table": {
        "columns": ["看什么", "论文证据", "飞哥判断"],
        "rows": [
            {
                "看什么": "主结果（ALFWorld）",
                "论文证据": "SFT+GRPO SR 40.71%；LangMem 38.27%（+2.44）；SFT 34.29%。",
                "飞哥判断": "绝对分差不大，但方向清楚：组织方式比再堆对话记忆更关键。",
            },
            {
                "看什么": "Web / 视觉",
                "论文证据": "Mind2Web 12.87% vs Full History 8.79%；EB-ALFRED 17.7% vs 10.3%。",
                "飞哥判断": "跨模态与网页交互也受益，不是只刷一个家务环境。",
            },
            {
                "看什么": "长轨迹×成本",
                "论文证据": "≤50步：SR +9.3点；token 797 vs 1201（约-33.6%）。",
                "飞哥判断": "轨迹越长越该看这篇；Full History成本爬升而收益平台。",
            },
            {
                "看什么": "机制",
                "论文证据": "Fixed Optical vs Fixed Text +5.71；动态组织再抬到40.71；固定细粒度掉到32.86。",
                "飞哥判断": "介质与动态选视图都重要；粒度自适应是最大杠杆之一。",
            },
        ],
    },
    "source_notes": [
        "主数字：Table 2 ALFWorld 40.71 / LangMem 38.27；Mind2Web 12.87 / 8.79；Table 3 EB-ALFRED 17.7 / Full History 10.3；Figure 4 ≤50步 +9.3 SR、797 vs 1201 tokens。",
        "版本戳：arXiv:2608.06745v1 [cs.AI]；ChatGPT 0810批次 #3（今日主发配对）。",
        "单位：NTU / SCUT / BUPT / USTC / PKU / ZJU / Fudan / SJTU。",
        "开源入口：https://github.com/Feld-maxiu/MemPrism",
        "证据覆盖：embodied + web；纯文本工具Agent与异构工具状态外推仍需验证。",
    ],
    "so_what": "检查长程Agent memory时，别只问「有没有召回」。要问：当前子任务看到的是时间线、因果链，还是实体状态表？形态不对，正确事实也会变成噪音。",
    "feige_view": "问题出在哪？不是没存住，而是决策时摆错了形态。对照LeanMem / ThinkReset / Zero-Mem：持久层之外，还缺决策时重组层。MemPrism把「怎么摆」做成可学习的view policy，而不是再加大检索top-k。",
    "limitations": [
        "view policy选错关系或证据范围时，永久库里的正确信息仍不可见。",
        "光学working memory与VLM绑定较强，纯文本工具Agent迁移成本未充分验证。",
        "ALFWorld绝对增益约2.4点，叙事需靠长轨迹与token曲线支撑。",
        "临时视图虽不回写，但错误view仍会污染当步动作分布。",
    ],
    "related_theme_picks": {
        "theme": "Agent memory组织与决策视图",
        "intro": "本篇讲任务条件关系视图；同线可对照：",
        "items": [
            {
                "arxiv_id": "2608.06410",
                "title_cn": "问题账本驱动的Agent harness自修",
                "one_liner": "同日配对：跨轮失败要有可继承的问题状态。",
                "link": "https://arxiv.org/abs/2608.06410",
                "ready_date": "20260811",
            },
            {
                "arxiv_id": "2607.29377",
                "title_cn": "Zero-Mem零参数记忆",
                "one_liner": "0804：memory能力不一定要写进权重。",
                "link": "https://arxiv.org/abs/2607.29377",
                "ready_date": "20260804",
            },
            {
                "arxiv_id": "2607.28642",
                "title_cn": "ThinkReset思维重置",
                "one_liner": "0804：长程推理里何时清掉工作状态。",
                "link": "https://arxiv.org/abs/2607.28642",
                "ready_date": "20260804",
            },
        ],
    },
    "target_audience": [
        "做长程Agent memory / 上下文压缩的研究工程团队。",
        "评估检索系统为何「召回了却仍做错」的平台同学。",
        "关心token成本与长轨迹稳定性的产品技术负责人。",
    ],
    "sales_use_cases": [
        "回应『我们已经上了向量记忆』：先问决策时关系视图是否按任务重组。",
        "方案评审：要求同时看SR、长轨迹曲线与prompt token，而不是只看平均召回。",
        "事故复盘：区分存储失败、检索失败与representation mismatch。",
    ],
    "objection_handling": [
        "客户说：『再加大top-k就行。』→ 回应：拿到更多chunk不等于摆成当前决策需要的关系。",
        "客户说：『绝对分才高2点。』→ 回应：看≤50步+9.3与token-33.6%；长任务账更明显。",
    ],
    "copy_paste_lines": [
        "存到不等于用对。",
        "MemPrism：ALFWorld 40.71%，长轨迹+9.3且token约-33.6%。",
        "先问关系视图，再问检索条数。",
    ],
    "key_quotes": [
        "representation mismatch, where relevant information is available but not organized for the current decision",
        "40.71%, outperforming all compared methods and exceeding the strongest baseline LangMem (38.27%) by 2.44 points",
        "33.6% token reduction (797 vs. 1,201) while delivering a 9.3-point SR improvement",
    ],
    "info": {
        "title": "MemPrism: Task-Conditioned Relational Memory Views for Long-Horizon Agents",
        "title_cn": "任务条件关系视图重组Agent记忆",
        "link": "https://arxiv.org/abs/2608.06745",
        "authors": [
            "Zhisheng Chen",
            "Bingfan Zeng",
            "Bangde Cao",
            "Zhengwei Xie",
            "Yuxuan Li",
            "Jinhan Li",
            "Zheng Lu",
            "Xiangchen Guan",
            "Zikai Xiao",
            "Rui Qian",
            "Jingwei Song",
        ],
        "affiliations": [
            "Nanyang Technological University",
            "South China University of Technology",
            "Beijing University of Posts and Telecommunications",
            "University of Science and Technology of China",
            "Peking University",
            "Zhejiang University",
            "Fudan University",
            "Shanghai Jiao Tong University",
        ],
    },
    "score": {
        "total": 8.9,
        "dimensions": [
            {"label": "重要性 Impact", "value": 1.8},
            {"label": "创新性 Novelty", "value": 1.9},
            {"label": "可验证性 Evidence", "value": 1.8},
            {"label": "产业可用性 Applicability", "value": 1.7},
            {"label": "可复用性 Reusability", "value": 1.7},
        ],
    },
    "score_rationale": "指出Agent memory失败常是representation mismatch：存到了但决策时形态不对。持久事件流+任务条件关系视图+光学working memory，ALFWorld SR 40.71%超LangMem 2.44点，长轨迹收益放大且token降约33.6%；view policy可跨VLM迁移。光学/VLM绑定与view policy新故障点使Applicability/Reusability略扣。",
    "score_rationale_detail": {
        "schema_version": 1,
        "score_range": 0.2,
        "highest_dimensions": ["创新性 Novelty"],
        "lowest_dimensions": ["产业可用性 Applicability", "可复用性 Reusability"],
        "dimension_rationales": [
            {"label": "重要性 Impact", "value": 1.8, "role": "middle", "rationale": "长程Agent「召回了却做错」是真痛点；绝对分差不大但问题定位准。"},
            {"label": "创新性 Novelty", "value": 1.9, "role": "highest", "rationale": "把memory从检索系统推向任务条件关系建模，持久层与工作层分离清晰。"},
            {"label": "可验证性 Evidence", "value": 1.8, "role": "middle", "rationale": "三基准、消融、长轨迹×token曲线与跨VLM迁移齐全。"},
            {"label": "产业可用性 Applicability", "value": 1.7, "role": "lowest", "rationale": "光学视图与VLM绑定；纯文本工具链落地需额外适配。"},
            {"label": "可复用性 Reusability", "value": 1.7, "role": "lowest", "rationale": "view policy成为新故障点；错误视图仍会污染当步决策。"},
        ],
    },
    "evidence_ledger_patch": {
        "claim_evidence": [
            {"claim": "ALFWorld SR 40.71%超LangMem 38.27%约2.44点", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "Mind2Web整体动作准确率12.87% vs Full History 8.79%", "evidence": "Table 2", "location": "Table 2"},
            {"claim": "EB-ALFRED平均SR 17.7% vs Full History 10.3%（+7.4）", "evidence": "Table 3", "location": "Table 3"},
            {"claim": "≤50步相对Full History SR +9.3点，token 797 vs 1201（约-33.6%）", "evidence": "Figure 4", "location": "Figure 4"},
            {"claim": "Fixed Optical相对Fixed Text +5.71；动态组织抬到40.71", "evidence": "Figure 3 / §4.3", "location": "Figure 3"},
        ]
    },
    "discussion_notes": [
        "Enriched 20260811 dual publish: ADIAS + MemPrism.",
        "Affiliations via overrides: eight universities listed explicitly.",
        "Numbers verified from PDF Table 2–3 and Figure 3–5.",
    ],
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

    dump(gen_path, data)
    dump(fused_article, data)

    card = load(card_path)
    card["info"] = data.get("info", card.get("info"))
    card["score"] = data.get("score", card.get("score"))
    if "title_cn" in data.get("info", {}):
        card["info"]["title_cn"] = data["info"]["title_cn"]
    dump(card_path, card)
    dump(fused_card, card)

    if ledger_path.exists():
        ledger = load(ledger_path)
        patch = rich.get("evidence_ledger_patch") or {}
        if patch.get("claim_evidence"):
            ledger["claim_evidence"] = patch["claim_evidence"]
        dump(ledger_path, ledger)
        dump(fused_ledger, ledger)

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
        "2608.06410",
        "adias",
        ADIAS_RICH,
        "别再只记版本号：用问题账本持续修Agent harness，平均超最强基线25.2%",
        "Agent自改进别只堆版本历史；把未关闭问题、干预与结果做成持久账本，再定向改完整代码。",
    )
    enrich_one(
        "2608.06745",
        "memprism",
        MEMPRISM_RICH,
        "存到不等于用对：任务条件关系视图重组记忆，长轨迹更赚且省token",
        "长程Agent记忆的关键不只是检索召回，而是当前决策该看到什么关系结构。",
    )
    print("enriched adias + memprism")


if __name__ == "__main__":
    main()
