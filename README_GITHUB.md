# Paper Notes - 论文速记生成器 / Paper Notes Generator

<div align="center">

**模板化生成论文速记全套物料**  
**Template-based generation for paper note cards & articles**

评分卡 · 信息卡 · 封面图 · 正文模板 · 公众号排版  
Score Cards · Info Cards · Cover Images · Article Templates · WeChat Formatting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

</div>

---

## 🚀 快速开始 / Quick Start

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 使用流程 / Workflow

```
准备数据 → 生成图片 → 编写正文 → 完成
Prepare Data → Generate Images → Write Article → Done
```

#### 1️⃣ 准备数据 / Prepare Data

复制 `references/data_template.json`，填入论文信息：  
Copy `references/data_template.json` and fill in paper information:

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

#### 3️⃣ 编写正文 / Write Article

参考 `references/md_template.md` 填写 A-F 六段式内容：  
Refer to `references/md_template.md` for the A-F article structure:

| 段落 / Section | 说明 / Description |
|------|------|
| A. 研究问题 / Research Question | 一句话说明问题 / One-sentence problem statement |
| B. 核心贡献 / Core Contributions | 列出 2-3 个贡献点 / List 2-3 contributions |
| C. 方法/框架 / Method/Framework | 描述技术方法 / Describe technical approach |
| D. 关键结果 / Key Results | 指标/对比/结论 / Metrics/comparison/conclusions |
| E. 产业启示 / Industry Implications | 对行业的启发 / Implications for industry |
| F. 一句话判断 / Final Verdict | 站队结论 / One-sentence verdict |

---

## 📦 输出样例 / Output Examples

| 文件 / File | 说明 / Description |
|------|------|
| `score_card.png` | 五维评分卡 / 5-Dimension Score Card |
| `info_card.png` | 论文信息卡 / Paper Info Card |
| `cover_235.png` | 2.35:1 封面图 / 2.35:1 Cover Image |
| `note.md` | 正文 Markdown / Article in Markdown |
| `article_editor_ready.html` | 公众号 HTML / WeChat Article HTML |

查看完整样例 / View full examples: [`examples/`](examples/)

---

## 📁 项目结构 / Project Structure

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

## 🎨 定制 / Customization

- **配色方案 / Color Scheme**：编辑 `references/css_main.md`
- **评分维度 / Score Dimensions**：修改 `data.json` 中的 `score.dimensions`
- **正文模板 / Article Template**：编辑 `references/md_template.md`

---

## 📄 许可证 / License

MIT License - 自由使用，欢迎贡献 / Free to use, contributions welcome

---

## 🔗 相关项目 / Related Projects

- 公众号 "AI 系统笔记" / WeChat Official Account "AI System Notes" - 每日论文速记解读 / Daily paper note interpretations

---

## ☕ 赞赏 / Sponsor

如果这个项目对你有帮助，欢迎请我喝杯咖啡：  
If this project helps you, consider buying me a coffee:

### 微信赞赏 / WeChat Reward（国内用户）

<div align="center">
<img src="assets/wechat-reward.png" width="200" alt="微信赞赏码 / WeChat Reward QR Code" />
<p><em>微信扫码赞赏 / Scan WeChat QR to Sponsor</em></p>
</div>

建议金额 / Suggested amounts: **¥9.9** / **¥49** / **¥199**

---

### PayPal（国际用户 / International Users）

如果你使用 PayPal，可以通过以下链接赞助：  
If you prefer PayPal, you can sponsor via:

**[https://paypal.me/aisystemnotes](https://paypal.me/aisystemnotes)**

建议金额 / Suggested amounts: **$1.99** / **$9.99** / **$49.99**
