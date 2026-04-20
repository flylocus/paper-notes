#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def generate_article(payload_path, out_path):
    with open(payload_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 将长文标题翻译为中文（保留行业术语）
    title_zh = "你的 Agent 归我了：测量 LLM 供应链中的恶意中间人攻击"

    # 移除 HTML 卡片，替换为图片占位符
    md = f"""# 【论文速记】{title_zh}

> 一句话结论：**值得关注（高威胁度，涉及 LLM 供应链安全实锤）**。

![封面图](cover_235.png)

![评分卡](score_card.png)

![信息卡](info_card.png)

## A. 研究问题
{data.get("A_research_problem", "")}

## B. 核心贡献
"""
    for c in data.get("B_core_contributions", []):
        md += f"- {c}\n"

    md += f"""
## C. 方法/框架
{data.get("C_method_framework", "")}

## D. 关键结果
"""
    for r in data.get("D_key_results", []):
        md += f"- {r}\n"

    md += f"""
## E. 产业启示
"""
    for imp in data.get("E_industry_implications", []):
        md += f"- {imp}\n"

    md += f"""
## F. 一句话判断
{data.get("F_one_line_judgement", "")}

---
### 补充信号（X.com/Grok 反馈）
"""
    for note in data.get("discussion_notes", []):
        md += f"- {note}\n"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Generated Article: {out_path}")

if __name__ == "__main__":
    generate_article("/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes/fused/article_payload.json", "/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes/rendered/article.md")