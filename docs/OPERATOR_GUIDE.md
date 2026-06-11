# Paper-Notes 日常执行指南

本文件是 `paper-notes` 的单入口操作指南。目标是：新的执行者拿到本指南和代码后，可以按和日常操作一致的方式完成论文速记，从候选输入、选题、评分、PDF 核验、产物生成，到发布前检查。

---

## 1. 当前唯一工作目录

所有操作默认在：

```bash
cd /Users/shenfei/clawd/paper-notes
```

不要把新的任务接到旧路径：

```text
/Users/shenfei/.openclaw/workspace/skills/paper-notes
```

旧路径只作为历史参考，不再作为正式生产路径。

---

## 2. 正式生产边界

正式入口只使用：

```text
scripts/production/
scripts/maintenance/
Makefile
```

不要在临近发布时直接使用：

```text
scripts/experimental/
```

正式图片链固定为：

```bash
python3 scripts/production/generate_cards.py
python3 scripts/production/generate_cover.py
```

发布前必须跑：

```bash
python3 scripts/production/preflight_check.py --out-dir /abs/path --mode publish
```

---

## 3. 每日任务总流程

日常流程分 8 步：

1. 准备双源输入：ChatGPT 和 Grok/X。
2. 运行 phase1：生成候选池和 Top 3。
3. 去重和人工选题：避开已发布论文，确认是否符合当天主题。
4. 核验论文元数据和 PDF：首页单位、作者、摘要、分类、时间。
5. 写正式五维评分 JSON。
6. 调用 `daily_runner.py produce` 生成基础发布包。
7. 修正元数据覆盖问题并重建产物，特别是单位字段。
8. 做 preflight、图片尺寸、HTML 引用、编辑强化检查，最后发布。

---

## 4. 输入文件规则

每日必须准备两个原始输入文件：

```text
inputs/chatgpt/YYYYMMDD.txt
inputs/grok/YYYYMMDD.txt
```

示例：

```text
inputs/chatgpt/20260427.txt
inputs/grok/20260427.txt
```

规则：

- 缺任一输入时，`phase1` 应明确失败或停止，不允许编造候选。
- ChatGPT 输入通常是“Top 5 cs.AI papers”文本。
- Grok 输入通常来自 Grok/X 视角或 xAI API 拉取结果。
- 如果 Grok 页面不可用，可以使用 xAI API 补 Grok 文本，但不要把 API key 写进项目文件、任务卡或记忆文件。

---

## 5. Phase1：候选池构建

推荐使用 Makefile：

```bash
make phase1 DATE=20260427
```

等价命令：

```bash
python3 scripts/production/daily_runner.py phase1 --date 20260427
```

成功后会生成：

```text
fused/arxiv_candidates_YYYYMMDD.json
fused/candidates_YYYYMMDD.json
fused/top_ranked_YYYYMMDD.json
```

如果缺输入，会出现类似：

```text
FileNotFoundError: inputs/chatgpt/YYYYMMDD.txt
```

这是正确的 fail-fast 行为。补齐输入后重跑即可。

---

## 6. 选题规则

查看融合结果：

```bash
python3 - <<'PY'
import json
date='20260427'
data=json.load(open(f'fused/top_ranked_{date}.json'))
for i,x in enumerate(data[:10],1):
    aid=x.get('arxiv_id') or x.get('id')
    sources=','.join(x.get('sources',[])) if isinstance(x.get('sources'), list) else x.get('sources')
    print(i, aid, sources, x.get('title'))
PY
```

去重检查：

```bash
find outputs/ready -maxdepth 3 -type d -name '<arxiv_id>' -print
```

选题优先级：

1. 未发布过。
2. 官方 arXiv 链接真实存在。
3. 类别优先 `cs.AI`；额外论文可接受 `cs.CL` 等强相关类别，但要在记录里说明。
4. 符合栏目偏好：Agent、工程系统、生产落地、评估、工具使用、治理、工作流。
5. 不是纯噱头；必须有 PDF 中可追溯的核心数据或框架贡献。
6. 如果 Top 1/Top 2 已发布，顺延到最高的未发布候选。

已发布目录索引：

```text
outputs/READY_INDEX.md
```

---

## 7. 元数据和 PDF 核验

运行：

```bash
python3 scripts/production/verify_metadata.py \
  --arxiv-id 2604.22446 \
  --out fused/2604.22446_metadata.json \
  --keep-pdf
```

产物：

```text
fused/<arxiv_id>_metadata.json
fused/<arxiv_id>_metadata.pdf
```

必须检查 PDF 首页：

```bash
pdftotext -f 1 -l 3 fused/<arxiv_id>_metadata.pdf - | sed -n '1,260p'
```

核验重点：

- 标题是否和 arXiv 一致。
- 作者是否完整。
- 单位是否从 PDF 首页正确回填。
- 摘要是否一致。
- 分类是否符合主任务或额外任务口径。
- 发布时间是否符合当前窗口。

已知问题：

- `verify_metadata.py` 有时会漏单位或把单位抽成残缺项。
- `daily_runner.py produce` 会重新执行 metadata verify，可能覆盖你手动修正的 `affiliations`。
- 所以 produce 后必须再次检查 `card_data.json` 里的 `info.affiliations`。

手动修正 metadata 时，编辑：

```text
fused/<arxiv_id>_metadata.json
```

例：

```json
"affiliations": [
  "HUAWEI Noah’s Ark Lab",
  "University College London",
  "University Liverpool"
]
```

---

## 8. 五维评分规则

评分文件位置：

```text
fused/<arxiv_id>_score.json
```

评分规则：

- 5 个维度。
- 每维 0-2 分。
- 总分 10 分。
- 保留 1 位小数。

固定维度：

```text
重要性 Impact
创新性 Novelty
可验证性 Evidence
产业可用性 Applicability
可复用性 Reusability
```

模板：

```json
{
  "arxiv_id": "2604.22446",
  "total_score": 8.6,
  "dimensions": [
    {"label": "重要性 Impact", "value": 1.8},
    {"label": "创新性 Novelty", "value": 1.7},
    {"label": "可验证性 Evidence", "value": 1.6},
    {"label": "产业可用性 Applicability", "value": 1.8},
    {"label": "可复用性 Reusability", "value": 1.7}
  ],
  "reason": "正式五维评分说明...",
  "source_basis": [
    "arXiv metadata verified via arXiv API",
    "PDF downloaded and converted to local text",
    "PDF first-page inspection for affiliations",
    "Local PDF inspection for method, results, limitations",
    "User-provided ChatGPT and Grok source inputs"
  ]
}
```

评分注意：

- 证据是 simulation/projection 时，`Evidence` 要扣分。
- 只有 case study、没有系统 benchmark 时，`Evidence` 要扣分。
- 有代码、模型、数据、benchmark、生产系统评估时，`Applicability` 和 `Reusability` 可更高。
- 不要因为论文热度高就直接给高分；看证据质量。

---

## 9. Produce：生成基础发布包

命令结构：

```bash
python3 scripts/production/daily_runner.py produce \
  --date YYYYMMDD \
  --arxiv-id <arxiv_id> \
  --paper-key <short_key> \
  --title-cn "<中文短标题>" \
  --score-json fused/<arxiv_id>_score.json \
  --out-dir outputs/ready/YYYYMMDD/<arxiv_id> \
  --html-title "<公众号标题>" \
  --html-conclusion "<一句话结论>" \
  --one-line "<F. 一句话判断>" \
  --research-problem "<A. 研究问题>" \
  --method-framework "<C. 方法/框架>" \
  --core-contributions "<贡献点1>" \
  --core-contributions "<贡献点2>" \
  --key-results "<结果1>" \
  --key-results "<结果2>" \
  --industry-implications "<启示1>" \
  --industry-implications "<启示2>" \
  --publish-title "<备选标题1>" \
  --publish-title "<备选标题2>" \
  --publish-intro "<发布导语>" \
  --publish-summary "<发布摘要>"
```

`paper-key` 规则：

- 简短、可读、ASCII。
- 会用于 payload 文件名和封面左侧简称。
- 示例：`omc`、`agenticqwen`、`tool-attn`。

`title-cn` 规则：

- 中文短标题。
- 会进入信息卡和封面副标题。
- 封面副标题只写中文，不重复英文标题。

---

## 10. Produce 后的必做修正

`verify_metadata.py` 已内置单位字段保护（2026-06-10 起）：

- **overrides 权威层**：若存在 `fused/<arxiv_id>_metadata_overrides.json`，其中字段（如 `affiliations`）无条件覆盖抽取结果，重跑 produce 也不会丢。
- **非空保留**：本次抽取为空而上次 `fused/<arxiv_id>_metadata.json` 非空时，自动保留上次值（`affiliations_source: preserved_previous`）。
- **preflight 门控**：`card_data.json` / `generate_data.json` 的 `info.affiliations` 为空时 preflight 直接 blocking FAIL（`affiliations_missing`）；含 `@` 或超长条目给 warning（`affiliations_suspicious`）。

produce 后仍需人工核对一次：

```bash
sed -n '1,220p' outputs/ready/YYYYMMDD/<arxiv_id>/card_data.json
```

如果 `affiliations` 错误或缺失，**标准做法是写 overrides 文件**（一次写入，永久权威）：

```bash
cat > fused/<arxiv_id>_metadata_overrides.json <<'EOF'
{"affiliations": ["University of Edinburgh", "Huawei Technologies"]}
EOF
```

然后重跑：

1. `verify_metadata.py`（或直接重跑 produce，overrides 会生效）。
2. 重跑 `build_payload.py`。
3. 复制 payload 到输出目录。
4. 重跑 `render_article.py`、`generate_cards.py`、`generate_cover.py`、`preflight_check.py`。

> 旧做法（直接改 `fused/<arxiv_id>_metadata.json`）仅在"本次抽取为空"时受保护；抽取到噪声值时仍会被覆盖，所以人工修正一律走 overrides。

示例：

```bash
python3 scripts/production/build_payload.py \
  --metadata fused/<arxiv_id>_metadata.json \
  --score fused/<arxiv_id>_score.json \
  --paper-key <paper_key> \
  --date YYYYMMDD \
  --title-cn "<中文短标题>" \
  --out-dir fused \
  --one-line "<F. 一句话判断>" \
  --research-problem "<A. 研究问题>" \
  --method-framework "<C. 方法/框架>" \
  --core-contributions "<贡献点>" \
  --key-results "<关键结果>" \
  --industry-implications "<产业启示>"

cp fused/<paper_key>_card_payload_YYYYMMDD.json outputs/ready/YYYYMMDD/<arxiv_id>/card_data.json
cp fused/<paper_key>_article_payload_YYYYMMDD.json outputs/ready/YYYYMMDD/<arxiv_id>/generate_data.json

python3 scripts/production/render_article.py \
  --article-payload fused/<paper_key>_article_payload_YYYYMMDD.json \
  --out-dir outputs/ready/YYYYMMDD/<arxiv_id> \
  --html-title "<公众号标题>" \
  --html-conclusion "<一句话结论>"

python3 scripts/production/generate_cards.py \
  --data fused/<paper_key>_card_payload_YYYYMMDD.json \
  --out outputs/ready/YYYYMMDD/<arxiv_id>

python3 scripts/production/generate_cover.py \
  --data fused/<paper_key>_card_payload_YYYYMMDD.json \
  --out outputs/ready/YYYYMMDD/<arxiv_id>/cover_235.png

python3 scripts/production/preflight_check.py \
  --out-dir outputs/ready/YYYYMMDD/<arxiv_id> \
  --mode publish
```

---

## 11. 输出目录和文件清单

正式输出目录：

```text
outputs/ready/YYYYMMDD/<arxiv_id>/
```

必须包含：

```text
article_editor_ready.html
note.md
publish_pack.md
score_card.png
info_card.png
cover_235.png
card_data.json
generate_data.json
evidence_ledger.json
preflight_report.md
preflight_report.json
validation_report.md
validation_report.json
qa_report.md
qa_report.json
```

图片尺寸应为：

```text
score_card.png 1080x720
info_card.png 1080x720
cover_235.png 2350x1000
```

检查命令：

```bash
python3 - <<'PY'
from PIL import Image
from pathlib import Path
out=Path('outputs/ready/YYYYMMDD/<arxiv_id>')
for name in ['score_card.png','info_card.png','cover_235.png']:
    im=Image.open(out/name)
    print(name, im.size)
for name in ['note.md','article_editor_ready.html','publish_pack.md','card_data.json','generate_data.json','preflight_report.md','preflight_report.json']:
    p=out/name
    print(name, p.exists(), p.stat().st_size if p.exists() else 0)
PY
```

检查 HTML 引用：

```bash
rg -n "score_card.png|info_card.png|TODO|待补充|placeholder|Unknown" \
  outputs/ready/YYYYMMDD/<arxiv_id>/article_editor_ready.html \
  outputs/ready/YYYYMMDD/<arxiv_id>/note.md \
  outputs/ready/YYYYMMDD/<arxiv_id>/publish_pack.md
```

---

## 12. Preflight 通过标准

运行：

```bash
make preflight OUT_DIR=/Users/shenfei/clawd/paper-notes/outputs/ready/YYYYMMDD/<arxiv_id> MODE=publish
```

或：

```bash
python3 scripts/production/preflight_check.py \
  --out-dir /Users/shenfei/clawd/paper-notes/outputs/ready/YYYYMMDD/<arxiv_id> \
  --mode publish
```

或使用统一 QA 门禁，同时运行工程 preflight 与内容质量 validation：

```bash
make qa OUT_DIR=/Users/shenfei/clawd/paper-notes/outputs/ready/YYYYMMDD/<arxiv_id> MODE=publish
```

近期产物若缺独立证据账本，可只回填 evidence/score，不重写正文：

```bash
make backfill-evidence DATE_FROM=YYYYMMDD DATE_TO=YYYYMMDD
```

旧稿若缺当前模板的术语说明、So What、F 段限制面，可做低风险结构标准化：

```bash
make standardize-legacy DATE_FROM=YYYYMMDD DATE_TO=YYYYMMDD
```

通过标准：

```text
PASS
blocking: 0
warning: 0
```

注意：

- preflight 只检查基础文件、占位符、图片引用等。
- `make qa` 会额外写入 `validation_report.*` 与 `qa_report.*`，并把 F 段限制面、评分扁平、So What 机制判断、原文核验证据源等作为质量信号。
- 新产物优先用独立 `evidence_ledger.json` 记录 PDF/arXiv/fulltext 核验来源；旧产物仍兼容 `generate_data.json` 内的 `evidence_ledger` / `discussion_notes`。
- 若五维评分过于扁平，`generate_data.json` 必须包含 `score_rationale_detail`：至少覆盖最高维、最低维和 3 个维度解释，且维度解释不能全部复用同一段话。
- `standardize-legacy` 只插入带 `data-standardized="20260606"` 标记的结构块，并保存 `article_editor_ready.legacy_pre_standardize.html` 备份；它不负责重写旧正文里的对称句式、表格缺失或副词空话。
- 若旧产物缺 `fused/<id>_score.json`，`backfill-evidence` 可从 `generate_data.json` 里的既有 `score` 降级生成 ledger，并在 `source_basis` 中记录 fallback；这只用于历史补账，不替代正式评分文件。
- 当前 QA 失败条件是 preflight blocking 或 validation P0；P1/P2 作为发布前编辑提醒处理。

---

## 13. 发布前编辑强化清单

脚本生成的是基础发布包。正式发布前，应优先把 `article_editor_ready.html` 人工增强成“数据锚定稿”。

### 13.1 风格优化 skill

遇到 paper-notes 发布前/发布后风格优化任务，优先加载：

```text
~/.hermes/skills/content-strategy/paper-notes-style-optimization/SKILL.md
```

遇到“三风格融合”、或用户提到“申飞 + 乱翻书 + 首席数智官”时，同时加载：

```text
~/.hermes/skills/content-strategy/paper-notes-triple-style-fusion/SKILL.md
```

OPSD 优化案例：

```text
~/.hermes/skills/content-strategy/paper-notes-style-optimization/references/opsd-compression-case-study.md
```

硬规则：

- F 段必须有转折词（首选“不过”，也接受“但/然而”）引导的限制面/负面判断，且要有实质内容（局限/外推边界/成本约束等），不能只是转折修辞。
- “不是...而是...”对称句式不超过 3 次，超过时改成“其实是”“说白了就是”等更自然表达。
- A 段之前补“术语说明”，覆盖核心缩写、技术概念、benchmark 和模型名称。
- 表格、列表、段落样式要与微信公众号文章统一。
- 修改 `article_editor_ready.html` 后，必须并行更新 `generate_data.json` 对应字段，并在 `discussion_notes` 记录修订说明。
- **人工强化完成后必须重跑 `make qa OUT_DIR=... MODE=publish`**，让 `validation_report` / `qa_report` 反映最终稿。改后不复验会留下过期 PASS 报告（2026-06-09 实例）；preflight 现以 `qa_report_stale` warning 兜底报警，但不要依赖兜底。
- 新版 `render_article.py` 已支持结构化强稿字段：`glossary`、`method_subsections`、`result_table`、`source_notes`、`so_what`、`feige_view`、`limitations`。优先把这些内容写进 payload，让 renderer 生成 `note.md` 和 HTML，而不是直接把 HTML 片段塞进 Markdown 源文档。

三风格融合补充规则：

- 默认采用“主风格 + 辅助技法”模式，不做简单机械权重拼贴。
- 可把 A/B/F、C/D、E 三组并行处理：A/B/F 以申飞本人为主，C/D 以乱翻书为主，E 以首席数智官为主。
- 三风格版统一放在 `outputs/v2/{date}/{id}/`，与 `outputs/ready/{date}/{id}/` 版本隔离。
- 交付前执行 Anti-AI-tone 检查：无自我标注前缀；“不是...而是...”≤3；无“系统性地/有效地/重要地”等副词型空话；人工确认有碎句节奏。
- 最终按 A/A-/B+/B 评级；发布级目标至少 A-。

ABCDEF 小标题样式偏好：

- 参考更理想的发布稿：`https://mp.weixin.qq.com/s/FdfsrNYzRUb_HbjeDer8CA?token=82910661&lang=zh_CN`。
- 不要只输出平铺的 `h2 + 段落/列表`。每个内容密集的 ABCDEF 段落都应有内部层级。
- C/D 段优先加入 1-3 个 `h3` 小标题，使用 accent 色，与主 `h2` 拉开层级。
- 对紧凑概念可用 bold standalone 小标题，例如 `GPR（...）`、`TPE（...）` 这种一行解释。
- D 段有 3 个以上可比较指标时，优先做表格；表格后必须补“数据来源 + so what”说明。
- E 段使用 `01/02/03` 分层时，编号标题要作为独立小标题或强加粗段落，不要埋在长段落里。
- 发布前人工扫一遍视觉节奏：主标题、ABCDEF、段内小标题、表格、列表之间要有清晰层级。

检查项：

- 标题包含至少 1 个真实数据点：分数、提升比例、成本、排名、论文数量、benchmark 数量等。
- 一句话结论包含核心对比数字和机制；如果没有性能数据，用真实规模数据替代。
- 关键结果优先用表格呈现，至少包含基线、改进方法、关键指标。
- 表格后必须说明数据来源：哪个 benchmark、哪张表、是否 simulation/projection/live measurement。
- 方法部分不要出现 200 字以上长段落；复杂方法拆成阶段、表格或 bullet。
- 术语首次出现要解释：如 `GRPO（Group Relative Policy Optimization）`、`E2R（Explore-Execute-Review）`。
- 每条产业启示尽量配一个具体场景示例。
- `F. 一句话判断` 可以写 3 句话：核心贡献、趋势启示、行动价值。
- 所有数字必须能在 PDF、arXiv 或可信来源中追溯。

不要做：

- 不要为了强标题编造百分比。
- 不要把 projection 写成实测。
- 不要把 case study 写成大规模 benchmark。
- 不要给 survey 类论文强套性能提升模板。

---

## 14. 发布后收口

用户确认发布后，记录：

```text
最终发布文件：outputs/ready/YYYYMMDD/<arxiv_id>/article_editor_ready.html
是否有人工修改：有/无
```

更新：

```text
outputs/READY_INDEX.md
tasks/YYYY-MM-DD-paper-notes-daily-production.md
memory/YYYY-MM-DD.md
```

`READY_INDEX.md` 需要：

- `publish_ready` 数量 +1。
- 增加 `ready/YYYYMMDD/<arxiv_id>` 条目。
- 写明 preflight 状态和关键文件。

---

## 15. 常见问题和处理

### 15.1 缺 ChatGPT/Grok 输入

表现：

```text
FileNotFoundError: inputs/chatgpt/YYYYMMDD.txt
```

处理：

- 向用户要源文本。
- 或在用户允许时用 xAI API 拉 Grok。
- 不允许自行编造输入。

### 15.2 Top 1 已经发布

处理：

- 用 `outputs/READY_INDEX.md` 和 `find outputs/ready ...` 去重。
- 顺延到最高未发布候选。
- 在任务卡中记录为什么跳过。

### 15.3 论文不是 cs.AI

处理：

- 主任务优先 cs.AI。
- 如果用户指定额外论文，可以接受 cs.CL / cs.LG / cs.SE 等强相关类别。
- 必须在任务卡和记忆里注明“作为额外论文速记处理，不混入主 cs.AI Top 5 排序”。

### 15.4 单位缺失或不完整

处理：

- 用 PDF 首页手动核验。
- 修正 `fused/<arxiv_id>_metadata.json`。
- 重建 payload、卡片、封面和 preflight。

### 15.5 图片流程走错

处理：

- 不使用实验图链覆盖正式图。
- 回退到：

```bash
python3 scripts/production/generate_cards.py
python3 scripts/production/generate_cover.py
```

### 15.6 Preflight PASS 但稿件仍需要改

这是正常情况。

- preflight 是工程完整性检查。
- 编辑强化是人工质量检查。
- 发布稿允许基于 `article_editor_ready.html` 继续人工修改。

---

## 16. 最小命令清单

```bash
cd /Users/shenfei/clawd/paper-notes

# 1. 候选池
make phase1 DATE=YYYYMMDD

# 2. 元数据核验
python3 scripts/production/verify_metadata.py \
  --arxiv-id <arxiv_id> \
  --out fused/<arxiv_id>_metadata.json \
  --keep-pdf

# 3. PDF 首页核验
pdftotext -f 1 -l 3 fused/<arxiv_id>_metadata.pdf - | sed -n '1,260p'

# 4. 写 fused/<arxiv_id>_score.json

# 5. 生成基础发布包
python3 scripts/production/daily_runner.py produce \
  --date YYYYMMDD \
  --arxiv-id <arxiv_id> \
  --paper-key <paper_key> \
  --title-cn "<中文短标题>" \
  --score-json fused/<arxiv_id>_score.json \
  --out-dir outputs/ready/YYYYMMDD/<arxiv_id> \
  --html-title "<公众号标题>" \
  --html-conclusion "<一句话结论>" \
  --one-line "<F. 一句话判断>" \
  --research-problem "<A. 研究问题>" \
  --method-framework "<C. 方法/框架>" \
  --core-contributions "<贡献点>" \
  --key-results "<关键结果>" \
  --industry-implications "<产业启示>" \
  --publish-title "<备选标题>" \
  --publish-intro "<导语>" \
  --publish-summary "<摘要>"

# 6. 发布前检查
make preflight OUT_DIR=/Users/shenfei/clawd/paper-notes/outputs/ready/YYYYMMDD/<arxiv_id> MODE=publish

# 7. 推荐统一QA
make qa OUT_DIR=/Users/shenfei/clawd/paper-notes/outputs/ready/YYYYMMDD/<arxiv_id> MODE=publish
```

---

## 17. 推荐参考样例

当前可参考正式目录见：

```text
outputs/READY_INDEX.md
```

近期最有参考价值的样例：

```text
outputs/ready/20260426/2604.21816
outputs/ready/20260427/2604.22446
outputs/ready/20260427/2604.21590
```

分别对应：

- `2604.21816`：工具/MCP tax，工程系统类论文。
- `2604.22446`：多 Agent 组织层，framework + benchmark 类论文。
- `2604.21590`：额外指定论文，cs.CL 但强 agent 工业落地相关。
