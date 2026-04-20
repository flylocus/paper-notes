# Paper-Notes 执行地图（Runbook）

## 目标
把 `paper-notes` 从“可参考的 SOP”推进成“可执行的日常流程地图”，明确每个阶段该调用什么脚本、产出什么文件、在哪里检查。

---

## 一、目录职责

### 工作目录
`/Users/shenfei/clawd/paper-notes/`

### 核心子目录
- `inputs/chatgpt/`：ChatGPT 原始输入
- `inputs/grok/`：Grok / X.com 原始输入
- `fused/`：中间结果（候选池、评分、payload）
- `outputs/YYYYMMDD/<arxiv_id>/`：单篇论文最终产物
- `scripts/production/`：正式生产脚本
- `scripts/maintenance/`：治理与补齐脚本
- `scripts/`：兼容 shim 与实验入口汇总层
- `references/`：模板与说明

---

## 二、阶段执行地图

## 阶段 1：候选池构建

### 目标
把 news-daily / arXiv 候选、ChatGPT 候选、Grok 候选汇总成统一候选池，并推荐 Top 3。

### 当前已知脚本
- `scripts/production/run_phase1.py`：解析 ChatGPT / Grok 输入并生成基础候选池
- （待补强）RSS / arXiv 拉取与交叉验证逻辑

### 输入
- `inputs/chatgpt/YYYYMMDD.txt`
- `inputs/grok/YYYYMMDD.txt`
- news-daily RSS / arXiv API

### 产物
- `fused/candidates_YYYYMMDD.json`
- `fused/candidates_verified_YYYYMMDD.json`
- `fused/top_ranked_YYYYMMDD.json`

### 当前缺口
- 还没有一个完整统一脚本，把 RSS / arXiv + ChatGPT + Grok 真正一次性整合
- 当前阶段1仍是“半自动 + 人工判断”

---

## 阶段 2：正式评分

### 目标
用户拍板目标论文后，对目标论文按 5 维度进行正式评分。

### 评分规则
- 5 维度
- 每维满分 2 分
- 总分 10 分
- 保留 1 位小数

### 当前实现方式
- 通过单独 JSON 生成评分结果
- 当前偏手动/半手动，不是固定脚本

### 产物
- `fused/top3_scored_YYYYMMDD.json`
- 或单论文评分 JSON

### 当前缺口
- 还没有 `score_paper.py` 之类的标准评分脚本

---

## 阶段 3：元数据核实

### 目标
确认标题、作者、单位、摘要为真实信息，不允许占位符。

### 当前实现方式
1. arXiv API 获取：
   - 标题
   - 作者
   - 摘要
   - 分类
   - 发布时间
2. PDF 首页补充：
   - 单位
   - 作者脚注
   - 首页摘要核对

### 当前工具链
- arXiv API
- PDF 下载
- 文本提取（如 `pdftotext`）

### 当前状态
- 已有 `verify_metadata.py`
- 仍需继续验证更多论文上的稳定性，尤其是单位回填与 PDF 补充逻辑

---

## 阶段 4：Payload 构建

### 目标
构建渲染与写作用的 card payload / article payload。

### 当前实现方式
- 以 `build_payload.py` 为主
- 必要时仍允许人工补字段，但不再建议临时散写 JSON

### 产物
- `fused/<paper>_card_payload_YYYYMMDD.json`
- `fused/<paper>_article_payload_YYYYMMDD.json`

### 当前状态
- 已有统一的 `build_payload.py`
- 仍需继续压缩人工补写步骤

---

## 阶段 5：渲染生成

### 当前已可用脚本
- 正式入口：`scripts/production/daily_runner.py`
- `scripts/production/generate_cards.py`
- `scripts/production/generate_cover.py`
- `scripts/production/preflight_check.py`
- `scripts/maintenance/backfill_output_dir.py`
- 实验脚本：`scripts/experimental/generate_all_cards.py`（非默认）

### 输出
- `score_card.png`
- `info_card.png`
- `cover_235.png`
- `note.md`
- `article_editor_ready.html`

### 当前实现方式
- 图片脚本已可直接调用
- 正文和 HTML 目前仍偏拼装式生成
- 正式图片链固定为 `generate_cards.py + generate_cover.py`
- `scripts/experimental/generate_all_cards.py` 仅允许做并行实验，不允许临近发布时直接替换正式图链
- 主 `scripts/` 下旧实验同名入口现已改成 fail-fast 提示桩，防止误用

### 当前状态
- 已有 `render_article.py`
- 已有 `daily_runner.py` 作为正式总入口
- 当前缺口主要不是“有没有脚本”，而是“是否所有人都沿用同一正式入口”

---

## 阶段 6：发布包装

### 当前实现方式
- 手工/脚本写入 `publish_pack.md`

### 输出
- 备选标题
- 导语
- 摘要版文案
- 发布 checklist

### 当前状态
- 已有 `build_publish_pack.py`
- 发布包装内容仍可能需要人工润色，但脚本入口已经存在
- 正式发布前可用 `preflight_check.py` 做硬拦截
- 历史目录若缺 `note.md` / `publish_pack.md`，可用 `backfill_output_dir.py` 回填到当前基线
- 如果目录缺少文章层或图片层关键基础材料，且决定不再升格，直接写入 `ARCHIVE_ONLY.md`
- 需要快速找当前可复用正式目录时，优先看 `outputs/READY_INDEX.md`

---

## 三、脚本状态清单
以下脚本已存在并可作为当前基线的一部分：

1. `fetch_candidates.py`
2. `verify_metadata.py`
3. `build_payload.py`
4. `render_article.py`
5. `build_publish_pack.py`
6. `daily_runner.py`

以下脚本仍属于后续可补强项：

1. `verify_candidates.py`
   - 校验 arXiv 真伪与时间窗口

2. `score_paper.py`
   - 按 5 维度输出正式评分 JSON

---

## 四、推荐演进路径

### 第一阶段（现在）
固定正式基线，只允许：
- 总入口：`daily_runner.py`
- 图片入口：`generate_cards.py + generate_cover.py`
- 发布拦截：`preflight_check.py`

先把“不会再走错正式链”放在第一优先级。

### 第二阶段
继续减少人工补字段和人工对齐动作。

### 第三阶段
再补强评分、候选验证和更多自动化。

---

## 五、当前最重要的结论
`paper-notes` 现在已经有：
- 一套真实跑通过的流程
- 一份 SOP
- 一份执行地图
- 一次完整产出案例（SAGE）

但它还没有完全变成“一键日跑系统”，目前处于：
**流程已经跑通，脚本化还差最后一层总装。**

补充：
- 正式生产边界见 `docs/PRODUCTION_BASELINE.md`
- 2026-04-20 已验证：实验图链如果直接入主线，会显著放大发布前返工风险
- 当前最重要工作已从“继续加脚本”切换为“统一入口与版本边界”
