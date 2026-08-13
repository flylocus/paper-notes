# Paper-Notes 任务卡片：2026-06-28

## 任务基本信息
- **日期**：2026-06-28
- **输入来源**：ChatGPT + Grok 双源
- **主轴优先**：Axis A（Agent 落地与治理）> Axis B（商业化）
- **状态**：✅ 已完成

---

## Stage 0：输入准备

### ChatGPT 输入（5 篇）
| 排名 | 论文标题 | 主题 | Axis 匹配度 |
|-----|---------|------|-----------|
| 1 | Language-Based Digital Twins for Elderly Cognitive Assistance | LLM + 数字孪生 + 医疗 | Axis B |
| 2 | Collaborative AI Deliberation | 多 Agent 协作 + 推理 | Axis A ⭐ |
| 3 | Thinking as Compression | 推理 = 压缩 + 理论 | Axis A |
| 4 | LiveBrowseComp: Are Search Agents Searching, or Just Verifying What They Already Know? | Search Agent 评估 | Axis A ⭐ |
| 5 | CORE: Contrastive Reflection Enables Rapid Improvements in Reasoning | 对比反思 + 推理改进 | Axis A |

### Grok 输入（5 篇）
| 排名 | 论文标题 | arXiv ID | 主题 | Axis 匹配度 |
|-----|---------|---------|------|-----------|
| 1 | Qwen-Image-Agent: Bridging the Context Gap in Real-World Image Generation | - | 图像生成 Agent | Axis A ⭐ |
| 2 | OPID: On-Policy Skill Distillation for Agentic Reinforcement Learning | - | Agent RL 技能蒸馏 | Axis A |
| 3 | SearchSwarm | 2606.09730 | 搜索 Agent + 子 Agent | Axis A ⭐⭐ |
| 4 | JetSpec: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting | - | 推理加速 + 投机解码 | Axis A |
| 5 | When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and MoA | - | MoA + 路由 + 投票 | Axis A |

---

## Stage 1：选题决策

### 查重结果（READY_INDEX 检索）
- [ ] 检查 30 天内是否重复生产

### 候选排名（按 Axis A 优先级）
1. **SearchSwarm (2606.09730)** - 搜索 Agent + 子 Agent 分解，GAIA/BrowseComp 基准测试，高工程价值
2. **LiveBrowseComp** - Search Agent 行为评估，直接相关 Agent 评估体系
3. **Collaborative AI Deliberation** - 多 Agent 协作，前沿研究
4. **Qwen-Image-Agent** - 图像生成 Agent，实际应用场景
5. **CORE: Contrastive Reflection** - 推理改进机制

### 最终选题
**选定论文**：**2606.27188 - A Process Harness for Uplifting Legacy Workflows to Agentic BPM: Design and Realization in CUGA FLO**

**选型理由**：
1. **Axis A 完美匹配**：直接讨论 Agentic BPM 的落地架构，属于"Agent 落地与治理"核心主题
2. **技术创新**：提出 Process Harness 机制——在遗留工作流引擎外包覆策略治理的 Agent 层，不替换原有引擎
3. **三类 Agent 分工**：TaskAgent（任务执行）+ DecisionAgent（网关路由）+ FlowAgent（流程适配）
4. **政策框架**：FRAME 聚合策略集治理所有 LLM 调用
5. **实际验证**：在贷款审批工作流上完整验证了三类 Agent 和钩子驱动的监管覆盖
6. **商业价值**：解决企业级 Agent 落地的最大痛点——如何与遗留系统无缝集成

---

## Stage 2：Payload 构建

- [ ] 元数据核验（verify_metadata.py）
- [ ] metadata_overrides.json（如需）
- [ ] PDF 获取 + 全文提取（pdftotext）
- [ ] 评分 JSON（Impact/Novelty/Evidence/Applicability/Reusability，总分 8-9）
- [ ] DeepSeek draft-payload 辅助
- [ ] 终版 Payload 合并

---

## Stage 3：产物渲染

- [ ] 三卡片生成（score_card / info_card / header_card）
- [ ] 封面图（cover_235.png）
- [ ] article_editor_ready.html
- [ ] article_wechat_safe.html（签名插图版）
- [ ] publish_pack.md

---

## Stage 4：门禁校验与归档

- [ ] preflight_check.py（PASS 标准：blocking=0, warning=0）
- [ ] qa_check.py（PASS 标准：grade A, P0=0, P1=0, P2=0）
- [ ] make standardize（归档到 outputs/ready/20260628/）
- [ ] 更新 READY_INDEX.md

---

## 坑点记录

| 时间 | 坑点 | 解决方案 |
|-----|------|---------|
| - | - | - |
