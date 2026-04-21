# Paper Notes Automation Entrypoints

## 目标
给未来 cron、automation、daily runner、外部 agent 一个统一接入说明，避免它们继续打到旧 skill 路径。

## 唯一工作目录

所有自动化的 `cwd` 应统一设置为：

`/Users/shenfei/clawd/paper-notes`

旧路径：

`/Users/shenfei/.openclaw/workspace/skills/paper-notes`

只保留兼容能力，不再作为新的 automation 目标路径。

## 推荐入口

### 1. 候选池阶段

```bash
python3 scripts/production/daily_runner.py phase1 --date 20260421
```

当前已存在的正式自动化：
- `Paper Notes Nightly Phase1`
- 执行时间：工作日凌晨 1 点（北京时间）
- 工作目录：`/Users/shenfei/clawd/paper-notes`
- 目标：检查当日 `inputs/chatgpt/YYYYMMDD.txt` 与 `inputs/grok/YYYYMMDD.txt` 是否齐全；齐全则运行 phase1，生成候选池与 Top 3 建议；缺输入则明确报缺。

### 2. 发布前治理

```bash
python3 scripts/maintenance/batch_standardize_outputs.py
```

### 3. 单目录预检

```bash
python3 scripts/production/preflight_check.py --out-dir /abs/path --mode publish
```

### 4. 历史目录补齐

```bash
python3 scripts/maintenance/backfill_output_dir.py --out-dir /abs/path --run-preflight
```

## 人工/自动化统一入口

如果需要尽量降低调用分歧，优先使用：

```bash
make help
make phase1 DATE=20260421
make standardize
make preflight OUT_DIR=/abs/path MODE=publish
make backfill OUT_DIR=/abs/path
```

## 不建议

- 不要把 automation 新接到旧 skill 路径
- 不要默认调用 `scripts/experimental/*`
- 不要把 `outputs/ready/` 当作脚本工作目录
