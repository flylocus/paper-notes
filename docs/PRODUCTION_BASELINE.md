# Paper Notes Production Baseline

## 目标
把 `paper-notes` 从“多版本并存”收敛到一个明确的正式生产基线，降低临近发布时误用实验脚本的概率。

## 单一主目录
唯一主目录：

`/Users/shenfei/clawd/paper-notes`

其他目录只作为历史参考，不再作为默认开发或发布路径。

## 正式生产入口

### 1. 全流程正式入口
使用：

`scripts/production/daily_runner.py`

它负责把正式链路串起来：
- `verify_metadata.py`
- `build_payload.py`
- `render_article.py`
- `generate_cards.py`
- `generate_cover.py`
- `build_publish_pack.py`
- `preflight_check.py`

### 2. 图片子流程正式入口
若只需要重生成正式图片，使用：
- `scripts/production/generate_cards.py`
- `scripts/production/generate_cover.py`

这是当前唯一认可的正式图片链。

## 脚本分级

### Production
- `scripts/production/daily_runner.py`
- `scripts/production/verify_metadata.py`
- `scripts/production/build_payload.py`
- `scripts/production/render_article.py`
- `scripts/production/build_publish_pack.py`
- `scripts/production/preflight_check.py`
- `scripts/maintenance/backfill_output_dir.py`
- `scripts/maintenance/batch_standardize_outputs.py`
- `scripts/production/generate_cards.py`
- `scripts/production/generate_cover.py`

### Experimental
- `scripts/experimental/generate_all_cards.py`
- `scripts/experimental/generate_cards_pillow.py`
- `scripts/experimental/run_pipeline.py`
- `scripts/experimental/mock_scoring_and_payload.py`

这些脚本可以保留用于试验，但不能默认进入正式发布链。

### Reference / Historical
- `references/`
- `outputs/20260216/`
- `outputs/20260415/`
- 单篇历史输出目录

这些内容用于视觉对齐、结构对照和回溯，不代表新的默认实现。

## 正式发布规则
1. 临近发布时，不允许把实验脚本直接替换正式图片链。
2. 如果要试验新图片样式，必须并行生成，对比后人工确认，不能覆盖正式结果。
3. 一旦发现正式产物与历史稳定样式不一致，优先回退到：
   - `scripts/production/generate_cards.py`
   - `scripts/production/generate_cover.py`
4. 单篇目录内要明确区分：
   - 最终产物
   - 中间数据
   - 追溯文件
5. 发布前必须通过 `scripts/production/preflight_check.py`
6. 历史目录补齐时，使用 `scripts/maintenance/backfill_output_dir.py`，不要手工零散修补
7. 需要批量治理 `outputs/` 时，使用 `scripts/maintenance/batch_standardize_outputs.py`
8. 缺少基础材料且明确不再升格的旧目录，应写入 `ARCHIVE_ONLY.md`
9. 需要快速查看当前正式可用样例时，先看 `outputs/READY_INDEX.md`
10. 如果要继续做目录级统一或单项目化，先看 `docs/REORG_PLAN.md`
11. `publish_ready` 目录应优先放在 `outputs/ready/`，`archive_only` 目录应优先放在 `outputs/archive/`
12. 如果仍需兼容旧路径，允许保留 symlink，但治理脚本应只统计真实目录，不重复统计兼容入口

## 当前结论
从 2026-04-20 的 `exp-compression-250420` 复盘看，系统真正需要的不是更多脚本，而是：

> 一个明确的正式入口，外加对实验脚本的清晰降级。

后续所有 SOP、runbook、迁移说明，都应以本文件为准。

补充：
- 主 `scripts/` 下旧同名入口现在只保留 fail-fast 提示桩
- 真正的实验代码已物理移入 `scripts/experimental/`
- 正式与维护脚本已继续分层到 `scripts/production/` 和 `scripts/maintenance/`
