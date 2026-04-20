# Paper Notes

`paper-notes` 现已正式升格为独立项目。

## 主目录

唯一主目录：

`/Users/shenfei/clawd/paper-notes`

旧 skill 路径：

`/Users/shenfei/.openclaw/workspace/skills/paper-notes`

现在只保留为兼容壳层，内部通过 symlink 指向本项目。  
后续所有脚本修改、文档更新、产物治理，都应以本目录为准。

## 当前正式入口

- 全流程：`python3 scripts/production/daily_runner.py ...`
- 图片链：`python3 scripts/production/generate_cards.py ...` + `python3 scripts/production/generate_cover.py ...`
- 发布前检查：`python3 scripts/production/preflight_check.py --out-dir <dir> --mode publish`
- 历史补齐：`python3 scripts/maintenance/backfill_output_dir.py --out-dir <dir> --run-preflight`
- 批量治理：`python3 scripts/maintenance/batch_standardize_outputs.py`
- 命令统一入口：`make help`

## 目录结构

```text
paper-notes/
  docs/
  assets/
  references/
  inputs/
  fused/
  outputs/
    ready/
    archive/
    _reports/
    READY_INDEX.md
  scripts/
    production/
    maintenance/
    experimental/
```

## 先看哪里

- 正式边界：[docs/PRODUCTION_BASELINE.md](/Users/shenfei/clawd/paper-notes/docs/PRODUCTION_BASELINE.md)
- 运行地图：[docs/RUNBOOK_PAPER_NOTES.md](/Users/shenfei/clawd/paper-notes/docs/RUNBOOK_PAPER_NOTES.md)
- 目录重组与升格记录：[docs/REORG_PLAN.md](/Users/shenfei/clawd/paper-notes/docs/REORG_PLAN.md)
- 自动化接入说明：[docs/AUTOMATION_ENTRYPOINTS.md](/Users/shenfei/clawd/paper-notes/docs/AUTOMATION_ENTRYPOINTS.md)
- 正式可复用样例索引：[outputs/READY_INDEX.md](/Users/shenfei/clawd/paper-notes/outputs/READY_INDEX.md)
