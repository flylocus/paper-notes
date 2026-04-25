# Paper Notes 输出样例

本目录包含使用 Paper Notes 生成的真实论文速记样例，供参考和测试使用。

## 样例列表

### 1. DeepSeek-V4 技术报告

**论文标题：** DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence  
**中文标题：** 百万 Token 上下文智能  
**评分：** 9.2 / 10  
**领域：** 大模型  

**生成文件：**
- `score_card.png` - 五维评分卡
- `info_card.png` - 论文信息卡
- `cover_235.png` - 2.35:1 封面图
- `note.md` - 正文 Markdown
- `card_data.json` - 卡片元数据

---

### 2. SCI-WORKFLOW: 科研自动化 Agent

**论文标题：** From Research Question to Scientific Workflow: Leveraging Agentic AI for Science Automation  
**中文标题：** 把科研问题变成可执行工作流  
**arXiv：** [2604.21910](https://arxiv.org/abs/2604.21910)  
**评分：** 8.8 / 10  
**领域：** Agent  

**生成文件：**
- `score_card.png` - 五维评分卡
- `info_card.png` - 论文信息卡
- `cover_235.png` - 2.35:1 封面图
- `note.md` - 正文 Markdown
- `card_data.json` - 卡片元数据

---

## 如何使用这些样例

### 查看生成效果

直接打开 `score_card.png`、`info_card.png`、`cover_235.png` 查看图片生成效果。

### 测试脚本

```bash
# 使用 DeepSeek-V4 的 card_data.json 测试生成脚本
python3 scripts/production/generate_cards.py --data examples/deepseek-v4/card_data.json --out test-output

# 对比生成结果与样例中的图片是否一致
```

### 作为模板参考

- 查看 `note.md` 了解正文 A-F 六段式结构
- 查看 `card_data.json` 了解数据格式要求
