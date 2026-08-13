# paper-notes 公众号发布格式标准

**Status:** active  
**Date:** 2026-07-29（修订；初版 2026-07-16）  
**Decision:** [2026-07-16-paper-notes-wechat-publish-format-standard](/Users/shenfei/memory/decisions/2026-07-16-paper-notes-wechat-publish-format-standard.md)  
**Evidence:** 0716 双发对照（`2607.13034` + `2607.12893`）；0729 按双号备忘录「保持聚焦」去掉销售战斗卡

---

## 用途

- `article_wechat_safe.html` = **生产/QA 真源**（字段齐全、preflight/qa 可验）
- **粘贴到微信公众号编辑器后的线上形态** = **发布标准**（下文「线上块序」）
- 二者差异为**有意裁剪**，不是漏发；后续生产、审查、粘贴 checklist 均以此为准

---

## 线上块序（发布标准）

| # | 块 | 线上要求 |
|---|-----|----------|
| 1 | 标题 | 用 `publish_pack.md` **备选标题 #1**（非 `html-title` 长标题） |
| 2 | 判断句 | 保留 blockquote 一句结论 |
| 3 | 信息 pill | 文内一行：`arXiv：{id}` · `评分：x.x / 10` · `{title-cn}`（无英文题头盒） |
| 4 | `header_card.png` | 保留，360px 居中 |
| 5 | 术语说明 | 保留；标题可为「💡 术语说明」 |
| 6 | A–F 正文 | 全保留（含 D 证据 01–05、So What、E 编号条、飞哥视角、F + 限制面） |
| 7 | 同题精选（3） | 保留；**仅标题超链 + 一句说明**（见下节） |
| 8 | 文末 | 微信原生「喜欢作者」；**不上传**自定义签名图 footer |

可执行启发落在 **So What + 飞哥视角**，不再单开销售赋能段。

---

## 有意不粘贴的块（本地可有，线上无）

| 块 | 说明 |
|----|------|
| **英文题头盒** | 线上用微信 H1 + pill，不重复 EN 标题区 |
| **💡 顶碎句**（header_card 后、术语说明前） | 与 D 后 So What 重复；粘贴时删，So What 保留 |
| **🎯 销售战斗卡** | **2026-07-29 起不贴**（对谁/场景/反对/话术/金句）。调性偏销售赋能，与「技术判断 + 证据」「宁可少信息、多清楚判断」冲突；本地 HTML 可暂留字段，粘贴删除 |
| **来源链接** | 整段不贴；arXiv 靠 pill + 微信底部「阅读原文」 |
| **📚 关于 paper-notes** | 不贴（公域禁用双号互推 footer；见导流限推荐止血） |
| **`author-signature-card.png`** | 不贴；用微信「喜欢作者」替代安全签名策略 |

---

## 样式压平（接受，不追还原）

微信编辑器会压平内联样式，**不视为 QA 失败**：

- D 证据卡 / E 编号 pill：橙/蓝底 → 纯文本（如「证据 01规模」连写）
- 限制面条目：F 段已有「不过」时，列表项**去掉句首重复「不过，」**
- 同题精选：去掉 `(2607.xxxxx)` 与裸 URL 行；微信将标题转为**站内超链**（历史文可能自动加【论文速记】后缀）

---

## 同题精选（Beyond 风格 · 线上版）

```
同题精选（3）· {theme}

{一句导语}

1. {标题超链} —— {一句说明}
2. {标题超链} —— {一句说明}
3. {标题超链} —— {一句说明}   ← 可为 Dare to B2B 微信文，非 arXiv
```

- 位置：A–F 正文之后、文末「喜欢作者」之前（原「销售战斗卡之后」已取消）
- 本地 HTML 可保留 arXiv ID / 裸链供 QA；**粘贴时不带裸链行**
- Dare 导流：用已发微信短链（如 Harness 文），不必写 arXiv

---

## 粘贴前 Checklist（追加）

在 `publish_pack.md` 通用 checklist 之外：

- [ ] 标题 = publish_pack 备选 #1
- [ ] 删除：顶碎句、来源链接、📚 footer、签名图、**销售战斗卡**
- [ ] 保留：同题精选（仅链+说明）、飞哥视角、So What
- [ ] 签名策略：不上传 `author-signature-card.png`；依赖「喜欢作者」
- [ ] 同题精选 #3 若为 Dare 文，确认短链可打开

---

## 与 QA 的关系

- `qa_check.py` / `preflight_check.py` 仍对 **完整** `article_wechat_safe.html` 验字段（含来源链接、footer 等）
- **发布合规**以本文「线上块序」为准；QA PASS ≠ 全文都要粘贴
- **语义 / 去 AI 味审稿**：`docs/STYLE_SHENFEI_REVIEW_PROMPT.md`（共用底稿 `clawd/docs/editorial-review-base.md`）；备忘建议 `style-shenfei-deai-review-YYYYMMDD.md`
- 审查备忘录：区分「本地 artifact 完整」与「粘贴裁剪 intentional」
- 销售战斗卡：本地可有、线上必删；不以「线上无战斗卡」判 QA 失败

---

## 参考样例

| 论文 | 本地 HTML | 已发短链（0716） |
|------|-----------|------------------|
| MemOps `2607.12893` | `outputs/ready/20260716/2607.12893/article_wechat_safe.html` | `https://mp.weixin.qq.com/s/Z60rhuF3Ch4PaK_D9JnGqw` |
| E3 `2607.13034` | `outputs/ready/20260716/2607.13034/article_wechat_safe.html` | 同批双发（预览 tempkey 已失效） |
