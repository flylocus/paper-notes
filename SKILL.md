---
name: paper-notes
description: 论文速记模板化生成工具 - 提供评分卡、信息卡、封面图的自动化生成，以及正文 A-F 六段式模板。适合公众号图文排版、组会汇报材料生成。/ Template-based paper note generator - Automated score cards, info cards, cover images, and A-F article templates. Suitable for WeChat articles and presentation materials.
---

# Paper Notes - 论文速记模板化工具 / Paper Notes Template Generator

> 提供论文速记的**模板化生成能力**：自动化生成评分卡、信息卡、封面图，并提供正文 A-F 六段式模板。  
> Provides **template-based generation** for paper notes: automated score cards, info cards, cover images, and A-F article templates.

## 快速开始 / Quick Start

### 前置条件 / Prerequisites

- Python 3.8+
- 依赖库 / Dependencies: `pip install -r requirements.txt`
- 字体文件（已内置）/ Fonts (included): `SourceHanSansCN-Regular.otf` / `SourceHanSansCN-Bold.otf`

### 使用流程 / Workflow

```
准备数据 → 生成图片 → 编写正文 → 完成
Prepare Data → Generate Images → Write Article → Done
```

#### 1️⃣ 准备数据 / Prepare Data

复制 [`references/data_template.json`](references/data_template.json)，填入论文信息：  
Copy [`references/data_template.json`](references/data_template.json) and fill in paper information:

```json
{
  "paper_title": "论文标题 / Paper Title",
  "score": {
    "total": 8.5,
    "dimensions": [
      {"label": "重要性 Impact", "value": 1.8},
      {"label": "创新性 Novelty", "value": 1.7},
      {"label": "可验证性 Evidence", "value": 1.6},
      {"label": "产业可用性 Applicability", "value": 1.7},
      {"label": "可复用性 Reusability", "value": 1.6}
    ]
  },
  "info": {
    "title": "英文标题 / English Title",
    "title_cn": "中文标题 / Chinese Title",
    "link": "https://arxiv.org/abs/XXXX.XXXXX",
    "authors": ["作者1 / Author 1", "作者2 / Author 2"],
    "affiliations": ["机构A / Institution A", "机构B / Institution B"]
  }
}
```

#### 2️⃣ 生成图片 / Generate Images

```bash
# 评分卡 + 信息卡 / Score Card + Info Card
python3 scripts/production/generate_cards.py --data data.json --out outputs/my-paper

# 封面图（可选）/ Cover Image (optional)
python3 scripts/production/generate_cover.py --data data.json --out outputs/my-paper/cover_235.png
```

**输出 / Output:**
- `score_card.png` - 五维评分卡 / 5-Dimension Score Card
- `info_card.png` - 论文信息卡 / Paper Info Card
- `cover_235.png` - 2.35:1 封面 / 2.35:1 Cover

#### 3️⃣ 编写正文 / Write Article

参考 [`references/md_template.md`](references/md_template.md) 填写 A-F 六段式内容：  
Refer to [`references/md_template.md`](references/md_template.md) for the A-F article structure:

| 段落 / Section | 说明 / Description |
|------|------|
| A. 研究问题 / Research Question | 一句话说明问题 / One-sentence problem statement |
| B. 核心贡献 / Core Contributions | 列出 2-3 个贡献点 / List 2-3 contributions |
| C. 方法/框架 / Method/Framework | 描述技术方法 / Describe technical approach |
| D. 关键结果 / Key Results | 指标/对比/结论 / Metrics/comparison/conclusions |
| E. 产业启示 / Industry Implications | 对行业的启发 / Implications for industry |
| F. 一句话判断 / Final Verdict | 站队结论 / One-sentence verdict |

---

## 输出样例 / Output Examples

| 文件 / File | 说明 / Description | 尺寸 / Size |
|------|------|------|
| `score_card.png` | 五维评分卡 / 5-Dimension Score Card | 1080x720 |
| `info_card.png` | 论文信息卡 / Paper Info Card | 1080x720 |
| `cover_235.png` | 2.35:1 封面 / 2.35:1 Cover | 2350x1000 |
| `note.md` | 正文 Markdown / Article in Markdown | - |
| `article_editor_ready.html` | 公众号 HTML / WeChat Article HTML | - |

查看完整样例 / View full examples: [`examples/`](examples/)

---

## 定制与扩展 / Customization & Extension

### 修改配色方案 / Modify Color Scheme

编辑 [`references/css_main.md`](references/css_main.md):

```css
:root {
  --primary: #0B1430;   /* 深海军蓝 / Dark Navy */
  --secondary: #4CC3FF; /* 冰蓝 / Ice Blue */
}
```

### 调整评分维度 / Adjust Score Dimensions

在 `data.json` 中修改 `score.dimensions` 数组，保持总分 10 分（每维 0-2 分）。  
Modify `score.dimensions` array in `data.json`, keeping total score at 10 (0-2 per dimension).

---

## 目录结构 / Directory Structure

```
paper-notes/
├── references/          # 模板与说明 / Templates & Docs
├── scripts/production/  # 正式生产脚本 / Production Scripts
├── outputs/             # 最终产物 / Final Outputs
├── examples/            # 输出样例 / Output Examples
├── docs/                # 完整文档 / Full Documentation
└── assets/              # logo/字体 / Logo & Fonts
```

---

## 相关资源 / Related Resources

- 📖 [完整文档 / Full Documentation](docs/)
- 🎨 [CSS 样式 / CSS Styles](references/css_main.md)
- 📋 [数据模板 / Data Template](references/data_template.json)
- 📝 [正文模板 / Article Template](references/md_template.md)

---

## 许可证 / License

MIT License - 自由使用，欢迎贡献 / Free to use, contributions welcome
