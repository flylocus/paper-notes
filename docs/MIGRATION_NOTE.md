# Paper-Notes 目录迁移说明（Migration Note）

## 结论
从现在开始，`paper-notes` 的**主版本目录**定义为：

`/Users/shenfei/clawd/paper-notes`

原目录：

`/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes`

改为视作：
- 历史来源
- 原始模板
- 备份参考
- 不再作为后续主开发目录

---

## 为什么主版本切到独立项目目录
当前独立项目目录已经承接了原 workspace 主线，并包含：

1. **新流程文档**
   - `docs/SOP_PAPER_NOTES.md`
   - `docs/RUNBOOK_PAPER_NOTES.md`

2. **新增标准脚本链**
   - `verify_metadata.py`
   - `build_payload.py`
   - `render_article.py`
   - `build_publish_pack.py`
   - `daily_runner.py`
   - `run_phase1.py`

3. **新实战中间产物**
   - `2604.09285_metadata.json`
   - `2604.09285_score.json`
   - `candidates_20260415.json`
   - `candidates_verified_20260415.json`

4. **新实战输出成果**
   - `outputs/20260415/...`（SAGE）

这意味着当前独立项目目录已经不只是项目拷贝，而是：
**原始项目 + 新流程沉淀 + 标准脚本化 + 最新产物** 的合并结果。

---

## 后续规则

### 1. 单一主目录原则
后续所有新增脚本、SOP、runner、payload、产物，一律以：

`/Users/shenfei/clawd/paper-notes`

为准。

旧 skill 路径：

`/Users/shenfei/.openclaw/workspace/skills/paper-notes`

现在仅保留为兼容入口，不再作为主开发目录。

### 2. Downloads 目录冻结
`/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes`
不再作为日常修改目录。

如需使用，仅用于：
- 历史参考
- 模板回看
- 差异对照

### 3. 新产物统一落 standalone 项目
避免 outputs / fused / scripts 在两个目录继续分叉。

### 4. 新 runner 统一指向 standalone 项目
所有未来 cron、daily runner、自动化入口，统一使用独立项目目录。

---

## 推荐后续动作
1. 后续继续补强独立项目目录中的标准脚本链
2. 若 Downloads 目录还有有价值内容，再按需回收
3. 若需要版本管理，再在独立项目目录上初始化/接入正式仓库

---

## 一句话说明
`/Users/shenfei/clawd/paper-notes` 现在是主版本；`Downloads/paper-notes-project/skills/paper-notes` 现在是历史参考版本；旧 skill 路径只保留兼容入口。

补充：
- 如果需要快速判断“哪个目录还能改、哪个目录只可参考”，先看 `docs/PROJECT_RELATIONSHIP.md`

## 补充：正式生产基线
目录迁移完成后，仍然需要避免“同一主目录下多条脚本链并存造成误用”。

因此正式基线再补一条：
- 正式生产说明以 `docs/PRODUCTION_BASELINE.md` 为准
- `daily_runner.py` 是正式总入口
- `generate_cards.py + generate_cover.py` 是正式图片入口
- `scripts/experimental/generate_all_cards.py` 等脚本保留为实验用途，不再视为默认正式链
- 主 `scripts/` 下旧实验入口已降级为 fail-fast 提示桩

## 下一阶段
如果后续要把当前 skill 工作区进一步收成更干净的单项目结构，执行顺序以 `docs/REORG_PLAN.md` 为准，不建议直接跳过分层步骤做一次性大搬迁。
