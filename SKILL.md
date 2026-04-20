---
name: paper-notes
description: Generate “论文速记”内容与配套图片卡（评分卡/论文信息卡/2.35:1 封面），并提供 mdnice 正文模板与 CSS。用于论文筛选评分、公众号图文排版、固定模板复用场景。
---

# Paper Notes

当前唯一主目录：

`/Users/shenfei/clawd/paper-notes`

旧 skill 路径：

`/Users/shenfei/.openclaw/workspace/skills/paper-notes`

现在只保留为兼容壳层，不再作为主开发目录。

## Overview
一套固定化的“论文速记”生产流程：评分体系 + 文章模板 + 图片卡（评分卡/信息卡/封面）+ mdnice CSS。

## Workflow

正式默认流程：
- 全流程：`python3 scripts/production/daily_runner.py ...`
- 图片重生成：`python3 scripts/production/generate_cards.py ...` + `python3 scripts/production/generate_cover.py ...`
- 发布前检查：`python3 scripts/production/preflight_check.py --out-dir <dir> --mode publish`
- 历史目录补齐：`python3 scripts/maintenance/backfill_output_dir.py --out-dir <dir> --run-preflight`
- 批量标准化：`python3 scripts/maintenance/batch_standardize_outputs.py`
- 不再升格的旧目录：写入 `ARCHIVE_ONLY.md`
- 当前正式可用目录索引：`outputs/READY_INDEX.md`
- 兼容说明：旧 `scripts/*.py` 路径仍可运行，但现在只作为 shim，优先使用新路径

不要默认使用实验脚本（例如 `scripts/experimental/generate_all_cards.py`）替代正式图片链。

1) **准备数据 JSON**（评分 + 论文信息）
- 参考：`references/data_template.json`

2) **生成图片卡**
```bash
python3 scripts/production/generate_cards.py --data data.json --out outputs
```
输出：`outputs/score_card.png`、`outputs/info_card.png`

> 推荐：按论文子目录输出，避免覆盖历史文件（例如 `outputs/2602.18456/`）。

3) **生成 2.35:1 封面（可选）**
```bash
python3 scripts/production/generate_cover.py --help
```
输出：`outputs/cover_235.png`（若使用 `--out outputs/<arxiv_id>` 则会生成到子目录）

4) **正文排版**
- 模板：`references/md_template.md`
- CSS：`references/css_main.md`

## Conventions
- 评分体系：5 维度，0–2 分/项，总分 10。
- 公众号排版顺序：评分卡 → 信息卡 → 正文 A–F（封面可置顶）。
- 配色：深海军蓝 #0B1430 + 冰蓝 #4CC3FF。

## Resources
- docs/
  - `PRODUCTION_BASELINE.md`（正式链与实验链边界）
  - `RUNBOOK_PAPER_NOTES.md`（运行说明）
  - `SOP_PAPER_NOTES.md`（操作流程）
  - `MIGRATION_NOTE.md`（主目录迁移说明）
  - `REORG_PLAN.md`（后续项目化/目录统一方案）
- scripts/
  - production/（正式生产链）
  - maintenance/（治理与补齐工具）
  - experimental/（实验脚本归档）
  - 旧顶层入口 shim（兼容旧命令）
- references/
  - operations.md（操作流程）
  - data_template.json（数据模板）
  - md_template.md（正文模板）
  - css_main.md（mdnice CSS）
- assets/
  - logo.jpg（圆形 LOGO）
