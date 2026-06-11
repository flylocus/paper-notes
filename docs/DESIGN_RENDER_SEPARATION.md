# DESIGN: Markdown/HTML 渲染彻底分离(payload 单源)

- 日期:2026-06-11
- 状态:设计稿(待飞哥批准后开分支实施)
- 来源:2026-06-06 monthly review 迭代项;前置工作 `94514db`(payload schema P1 门控)
- 原则:先设计后实现;稳态系统优先增强不打断主流程;实施开新分支

## 1. 问题

`render_article.py` 已是 payload 单源双渲染(note.md + HTML),但**编辑面仍是 HTML**:
发布级人工强化直接改 HTML,payload/note.md 靠人工回填,漂移不可见、不可检。

实测漂移(`scripts/maintenance/audit_render_drift.py --month 202606`,similarity = 重渲染稿与实际 HTML 的归一化文本相似度):

| 时段 | similarity | 解读 |
|---|---|---|
| 6/1-6/8(除 6/7) | 0.05-0.37 | payload 只有骨架(16-19 行),HTML 基本手写(~55 行) |
| 6/7、6/9-6/11 | 0.72-0.87 | 结构化字段投用后,payload 已承载大部分内容 |

审计脚本首跑即抓到活体漂移:6/11 的 payload `source_notes` 仍是旧文案(6/11 晚补同步时只改了 HTML/note.md)。

## 2. 目标架构

```
generate_data.json(唯一编辑面,schema 门控)
        │ render_article.py
        ├──> note.md(构建产物,不手改)
        └──> article_editor_ready.html(构建产物,不手改)
```

验收定义:发布稿 similarity ≥ 0.98;HTML/note.md 任何内容修改都必须经由 payload。

## 3. 残差表达力缺口(6/9-6/11 实测枚举)

| 缺口 | 现状 | 方案 |
|---|---|---|
| `html_title` / `html_conclusion` | daily_runner CLI 参数,payload 无此字段,重渲染无法复现 | payload 新增这两个字段,renderer 优先读 payload,CLI 参数降级为兼容 |
| E 段 `01/02/03` 编号小标题 | 人工在 HTML 加编号 | renderer 对 `E_industry_implications` 的 dict 形态自动编号(或约定 title 自带编号) |
| 数据来源行的富化(作者/会议) | 人工改 HTML,payload `source_notes` 漂移 | 无需新字段,靠一致性门控(Phase 2)逼出同步 |
| 段内多段落/自由排版 | item_text 只支持单段+首个 bold | item dict 增加 `paragraphs: []` 支持;**不提供 raw-html 逃生门**(会重新打开漂移) |

## 4. 迁移阶段

**Phase 1 表达力补全(~1 次会话)**
- schema + renderer 支持上表四项;`render` 增加 `make render OUT_DIR=...` 入口(从 payload 重渲染三件套)
- 验收:对 6/9-6/11 三天,把残差内容回填 payload 后重渲染,similarity ≥ 0.98,`make qa` 全过

**Phase 2 一致性门控(~0.5 次会话,依赖 Phase 1)**
- validator 新增 `render_consistency` 检查:重渲染 payload 与实际 HTML 的 similarity < 0.98 → 先 P2 观察 2-3 个生产日 → 升 P1
- audit_render_drift.py 即该检查的实现基础,逻辑复用

**Phase 3 编辑入口切换(流程变更,1-2 个生产日并行试点)**
- SOP 改为:人工强化只改 payload → `make render` → `make qa`;HTML/note.md 进入"构建产物"地位
- 试点方式:正常流程照跑,同日用新流程平行产一份对比;两天 similarity 达标且编辑负担可接受 → 切换
- 回滚:SOP 退回旧流程即可,代码无破坏性变更

**Phase 4(可选远期)模板外置**
- STYLE/结构模板从 renderer 代码抽到模板文件,样式迭代不再动代码

## 5. 风险与对策

| 风险 | 对策 |
|---|---|
| 表达力补全后仍有想不到的排版需求 | 不开 raw-html 逃生门;新需求按"先加 schema 字段+renderer 支持"处理,宁可慢一天 |
| AI 编辑器改 payload 的可靠性 | 发布级强化由 AI 按格式规范执行(2026-06-11 飞哥确认),强化动作与 payload 字段一一对应,比 HTML 直改更不易碰坏样式;约定用 Python json 读改写、禁止 shell 拼接 JSON(中文引号坑,见 clawd MEMORY 生产 Pitfall) |
| 迁移期 skill 指令不一致 | 一次性翻转 `~/.hermes/skills/content-strategy/paper-notes-*` 与 OPERATOR_GUIDE 第 13 节的编辑指令("改 HTML 后同步 payload" → "只改 payload → make render → make qa");Phase 3 试点前完成 |
| 重渲染覆盖历史手工稿 | `make render` 仅对显式 OUT_DIR 执行,且先备份原 HTML(`.legacy_pre_render.html`);历史产出永不批量重渲染 |
| 与 claim_evidence 观察期互相干扰 | 无耦合;但 Phase 3 试点日避开 claim_evidence 升级决策日(6/14) |

## 6. 实施约定

- 分支:`feat/render-separation`(基线原则:真正调整时开新分支)
- 建议节奏:6/12-6/14 先跑 claim_evidence 观察期 → 6/15 起 Phase 1/2 → 6/16-6/17 Phase 3 试点
- Phase 3 验收(2026-06-11 更新):AI 以 payload-first 流程完成发布级强化,轮次/耗时不劣于现状、QA 通过率不降、similarity ≥ 0.98;达标即切换,无需额外人工决策点
