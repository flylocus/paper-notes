# Paper-Notes 标准流程（SOP）

## 目标
将每日 AI 论文候选，从信息收集、候选筛选、人工拍板，到评分、成稿、出图、发布包装，固化为可重复执行的 paper-notes 生产流程。

---

## 总体流程（EPDCA）

### E — Explore / Establish
明确当天任务目标、时间窗口、输入来源和输出要求。

### P — Plan
拆成阶段执行，确保每一阶段都有输入、产物、检查点和反馈节点。

### D — Do
执行阶段任务，严格按步骤推进。

### C — Check
每阶段结束必须检查产物是否真实落盘、数据是否核实、是否存在占位符。

### A — Act
决定下一步继续、修正、或请用户拍板。

---

## 阶段 1：候选池构建与 Top 3 推荐

### 1.1 输入来源
必须至少包含三路：
1. **news-daily / RSS / arXiv 候选池**
2. **ChatGPT 候选摘要**
3. **Grok / X.com 候选摘要**

### 1.2 执行步骤
1. 从 news-daily 的 RSS OPML 或直接从 arXiv API 拉取候选论文
2. 解析 ChatGPT 输入
3. 解析 Grok 输入
4. 以 arXiv ID 为主键进行去重
5. 建立统一候选池
6. 根据项目目标做第一轮排序（注意：这一步是候选排序，不是正式论文评分）
7. 输出 **Top 3 可写论文** 给用户拍板

### 1.3 输出物
- `fused/candidates_YYYYMMDD.json`
- `fused/candidates_verified_YYYYMMDD.json`
- `fused/top_ranked_YYYYMMDD.json`

### 1.4 检查点
- 是否真的做了三路交叉，而不是只用单一路输入
- 是否按 arXiv ID 去重
- 是否给用户明确展示 Top 3
- 是否说明推荐理由和风险点

---

## 阶段 2：正式评分

### 2.1 前提
只有在用户拍板选定论文后，才进入正式评分。

### 2.2 评分标准
总分 10 分，5 个维度，每个维度满分 2 分：
1. 重要性 Impact
2. 创新性 Novelty
3. 可验证性 Evidence
4. 产业可用性 Applicability
5. 可复用性 Reusability

### 2.3 规则
- 每个维度：0~2 分
- 总分：五维相加
- **最终总分保留 1 位小数**
- 候选排序分与正式论文评分必须严格分开

### 2.4 输出物
- `fused/top3_scored_YYYYMMDD.json`
- 或目标论文单独评分 JSON

### 2.5 检查点
- 是否误把候选排序分当成正式评分
- 是否遵循 5 维 × 2 分 = 10 分
- 是否保留 1 位小数

---

## 阶段 3：元数据核实（禁止占位符）

### 3.1 核实顺序
1. **优先 arXiv API**：标题、作者、摘要、分类、发布时间
2. **必要时读取 PDF**：补作者单位、首页缺失信息

### 3.2 严格要求
- 禁止用 placeholder 作为最终交付内容
- 作者必须是真实作者
- 单位必须是真实单位
- 摘要和关键信息尽量来自论文原文或 arXiv

### 3.3 输出物
- 已核实的 payload 原始信息
- PDF 文件（如需要）

### 3.4 检查点
- 是否还有 `pending/manual enrichment/TBD` 之类占位词
- 作者单位是否真实可追溯
- 是否在必要时真的读了 PDF

---

## 阶段 4：Payload 构建

### 4.1 card payload
用于生成：
- score card
- info card
- cover

必须包含：
- 论文标题（英文）
- 中文标题
- arXiv 链接
- 作者
- 单位
- 五维评分
- 总分

### 4.2 article payload
用于生成正文：
- A. 研究问题
- B. 核心贡献
- C. 方法 / 框架
- D. 关键结果
- E. 产业启示
- F. 一句话判断

### 4.3 输出物
- `fused/<paper>_card_payload_YYYYMMDD.json`
- `fused/<paper>_article_payload_YYYYMMDD.json`

### 4.4 检查点
- 中文 framing 是否符合 ToB / Agent 语境
- 是否已经把真实作者/单位回填进去
- 是否避免空字段或占位字段

---

## 阶段 5：图片与正文生成

### 5.1 生成图片
使用：
- `generate_cards.py`
- `generate_cover.py`

默认不要使用：
- `scripts/experimental/generate_all_cards.py`
- `scripts/experimental/generate_cards_pillow.py`

它们属于实验脚本，不属于正式发布基线。

生成：
- `score_card.png`
- `info_card.png`
- `cover_235.png`

### 5.2 生成正文
至少输出两份：
1. `note.md`
2. `article_editor_ready.html`

### 5.3 正文结构要求
按固定结构：
- 标题
- 一句话结论
- score/info 图片
- A. 研究问题
- B. 核心贡献
- C. 方法/框架
- D. 关键结果
- E. 产业启示
- F. 一句话判断

### 5.4 检查点
- 输出目录是否真的存在文件
- 图片是否已生成且路径正确
- HTML 是否使用指定模板结构
- 正文是否符合公众号语气而不是内部备注语气

---

## 阶段 6：发布包装

### 6.1 必备内容
- 3 个备选标题
- 导语
- 摘要版文案
- 最终发布前 checklist

### 6.2 输出物
- `publish_pack.md`

### 6.3 检查点
- 是否给出默认推荐标题
- 是否说明发布顺序
- 是否给出最终交付清单

### 6.4 发布前硬检查
执行：

```bash
python3 scripts/production/preflight_check.py --out-dir <目标目录> --mode publish
```

要求：
- blocking = 0
- warning 可人工判断，但不能忽略 blocking

### 6.5 历史目录补齐
如果是旧目录回补，执行：

```bash
python3 scripts/maintenance/backfill_output_dir.py --out-dir <目标目录> --run-preflight
```

如果目录缺少基础材料，且明确不再作为正式发布资产维护：
- 写入 `ARCHIVE_ONLY.md`
- 在批量标准化中按 archive-only 管理

---

## 最终交付目录标准
单篇论文最终目录至少包含：
- `cover_235.png`
- `info_card.png`
- `score_card.png`
- `note.md`
- `article_editor_ready.html`
- `publish_pack.md`

## 正式基线补充规则
- 正式总入口优先使用 `scripts/production/daily_runner.py`
- 若只重跑图片，只允许使用：
  - `scripts/production/generate_cards.py`
  - `scripts/production/generate_cover.py`
- 临近发布时，禁止把实验图片脚本直接切成默认主链
- 主 `scripts/` 下旧实验同名入口会直接失败并提示正确入口
- 发布前必须跑 `scripts/production/preflight_check.py`
- 正式边界说明统一见 `docs/PRODUCTION_BASELINE.md`

---

## 反馈协议（必须执行）
每推进一个阶段，必须向用户反馈：
1. 当前阶段名称
2. 已完成内容
3. 关键结果
4. 是否有阻塞
5. 下一步做什么

禁止闷头做完全程不汇报。

---

## 本流程的关键原则
1. **先筛选，后评分，后成稿**
2. **候选排序分 ≠ 正式论文评分**
3. **真实元数据优先，禁止占位符交付**
4. **每阶段必须有反馈节点**
5. **按 EPDCA 推进，避免漏步**
