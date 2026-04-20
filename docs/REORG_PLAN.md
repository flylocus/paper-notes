# Paper Notes 项目化与目录统一方案

## 结论
是，应该着手把 `paper-notes` 继续收成一个更明确的单项目结构。  
但**不是今天直接大搬家**。

原因很简单：
- 今天前一阶段的重点是把正式发布链收稳，这一步已经完成
- 现在正式链虽然稳定，但目录层面仍然混放了文档、正式脚本、实验脚本、维护脚本、历史产物和中间态
- 如果现在立刻做大规模移动，最容易重新打断已验证可用的 `daily_runner.py -> preflight -> outputs` 正式链

因此更合理的做法是：
- **今天完成“方案定版”**
- **后续在一次独立整理窗口里按阶段迁移**

## 当前问题

### 1. 根目录语义还不够干净
当前主目录：

`/Users/shenfei/clawd/paper-notes`

同时承担了这些角色：
- 技能包目录
- 正式生产目录
- 历史实验目录
- 文档目录
- 输出资产目录
- 中间态工作目录

这会导致两个长期问题：
- 新人或未来自己进入目录时，不知道第一眼应该看哪里
- 正式脚本、维护脚本、实验脚本长期并列，误选入口的概率依然偏高

### 2. `scripts/` 已经出现“用途混杂”
虽然正式链已经钉死，但 `scripts/` 里仍然同时存在：
- 生产入口
- 维护治理脚本
- 数据准备脚本
- 实验入口提示桩
- `__pycache__`
- `.DS_Store`
- `scripts/outputs`

这说明功能分层已经开始成形，但目录分层还没跟上。

### 3. `outputs/` 已治理，但还没真正分层
现在 `outputs/` 已经通过：
- `READY_INDEX.md`
- `_reports/`
- `ARCHIVE_ONLY.md`

把状态梳理清楚了。

但物理布局仍是：
- 正式可参考目录
- 历史归档目录
- 报告目录

并列在一起。  
从治理角度足够用，但从长期维护角度，还不算最终形态。

## 推荐目标结构

建议未来把主目录收成下面这套结构：

```text
paper-notes/
  docs/
    PRODUCTION_BASELINE.md
    RUNBOOK_PAPER_NOTES.md
    SOP_PAPER_NOTES.md
    MIGRATION_NOTE.md
    REORG_PLAN.md
  assets/
  inputs/
    chatgpt/
    grok/
  references/
  scripts/
    production/
    maintenance/
    experimental/
  outputs/
    ready/
    archive/
    _reports/
    READY_INDEX.md
```

## 各层职责

### `docs/`
只放规则、SOP、迁移说明、运行说明。  
目标是让操作者进入项目后，所有“先看哪份文档”都在一个地方解决。

### `scripts/production/`
只放正式生产链：
- `daily_runner.py`
- `verify_metadata.py`
- `build_payload.py`
- `render_article.py`
- `generate_cards.py`
- `generate_cover.py`
- `build_publish_pack.py`
- `preflight_check.py`

### `scripts/maintenance/`
只放治理和修复工具：
- `backfill_output_dir.py`
- `batch_standardize_outputs.py`
- 未来若需要的 cleanup / migrate / doctor 工具

### `scripts/experimental/`
继续保留实验代码，但彻底与正式链隔离。

### `outputs/ready/`
只放当前认可的正式可复用样例目录。

### `outputs/archive/`
只放 `archive_only` 历史目录。

### `outputs/_reports/`
只放批量治理和状态报告。

## 推荐迁移顺序

### Phase 1：保持功能不变，只做结构标定
这一步已经基本完成：
- 正式入口已经固定
- 实验脚本已经降级
- preflight 已接入
- 历史目录已区分 `publish_ready` / `archive_only`
- `READY_INDEX.md` 已提供快速入口

当前可以把 Phase 1 视为完成。

### Phase 2：目录分层，但保留兼容桩
这一轮已经执行到位，当前已完成：
1. 新建 `docs/`
2. 把现有顶层说明文档迁入 `docs/`
3. 新建 `scripts/production/` 与 `scripts/maintenance/`
4. 把正式脚本与治理脚本分开
5. 在旧路径保留薄兼容桩，避免一次性打断已有调用

这一轮的目标不是“变漂亮”，而是：
- 让目录语义变明确
- 让正式链入口更难被误选

### Phase 3：输出目录物理归档
这一轮已经执行到位，当前已完成：
1. 把 `publish_ready` 目录迁到 `outputs/ready/`
2. 把 `archive_only` 目录迁到 `outputs/archive/`
3. 更新 `READY_INDEX.md` 和治理脚本路径逻辑

这一轮执行时，保持了：
- `outputs/_reports/` 继续留在根目录
- `outputs/READY_INDEX.md` 继续留在根目录
- 旧路径优先保留兼容 link，而不是立刻彻底删除

这一轮会改动真实输出路径，所以应该放在单独窗口做，并重新验证 runner / preflight / batch 工具。

### Phase 4：决定是否独立仓库化
这一轮已经执行到位，当前已完成：
- 主目录正式切到 `/Users/shenfei/clawd/paper-notes`
- 旧 skill 路径 `/Users/shenfei/.openclaw/workspace/skills/paper-notes` 降级为兼容壳层
- `README.md` 已补齐，独立项目身份已经明确

下一层如果继续，不再是“要不要拆项目”，而是：
- 是否初始化/接入正式 git 仓库
- 是否建立 release / tag / 版本管理
- 是否把自动化、cron、发布流程统一改指向独立项目路径

## 最适合现在继承的主线
如果今天就要定义“未来继续维护哪一版”，答案仍然不变：

- 主目录：`/Users/shenfei/clawd/paper-notes`
- 正式总入口：`scripts/production/daily_runner.py`
- 正式图片链：`scripts/production/generate_cards.py + scripts/production/generate_cover.py`
- 快速可用样例入口：`outputs/READY_INDEX.md`
- 全量治理入口：`scripts/maintenance/batch_standardize_outputs.py`

## 一句话判断
`paper-notes` 现在已经完成从 skill 工作区到独立项目的正式升格。  
后续应该进入“项目运营阶段”，而不是继续停留在结构补丁阶段。
