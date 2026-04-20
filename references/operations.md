# 操作流程（图片卡 + 正文）

## 产物
- 评分卡（总分 + 5 维度）
- 论文信息卡（标题 / 链接 / 作者 / 单位）
- 2.35:1 封面（可选）

## 必要资源
- 字体（工作区根目录）：SourceHanSansCN-Regular.otf / SourceHanSansCN-Bold.otf
- LOGO：assets/logo.jpg（已内置）

## 1) 准备数据 JSON
参考 `data_template.json`：

```json
{
  "paper_title": "Agentic Test-Time Scaling for WebAgents",
  "score": {
    "total": 8.4,
    "dimensions": [
      {"label": "重要性 Impact", "value": 1.8},
      {"label": "创新性 Novelty", "value": 1.7},
      {"label": "可验证性 Evidence", "value": 1.6},
      {"label": "产业可用性 Applicability", "value": 1.7},
      {"label": "可复用性 Reusability", "value": 1.6}
    ]
  },
  "info": {
    "title": "论文标题",
    "link": "https://arxiv.org/abs/XXXX.XXXXX",
    "authors": ["作者1*", "作者2*", "作者3"],
    "affiliations": ["UC Berkeley", "ICSI", "LBNL"]
  }
}
```

## 2) 生成评分卡 + 信息卡

```bash
python3 scripts/generate_cards.py --data data.json --out outputs
```

输出：
- outputs/score_card.png
- outputs/info_card.png

### ✅ 推荐：按论文子目录输出（避免覆盖历史文件）

```bash
# 建议用 arXiv id 做目录名
python3 scripts/generate_cards.py --data data.json --out outputs/2602.18456
```

输出：
- outputs/2602.18456/score_card.png
- outputs/2602.18456/info_card.png

## 3) 生成 2.35:1 封面（可选）

> 注意：generate_cover.py 当前是参数式脚本（不读 data.json），用 --out 指向同一子目录即可。

```bash
python3 scripts/generate_cover.py \
  --title "【论文速记】" \
  --subtitle "<Paper Title>" \
  --keywords "<kw1,kw2,kw3>" \
  --score "<8.2 / 10>" \
  --domain "<领域1|领域2>" \
  --out outputs/2602.18456
```

输出：
- outputs/2602.18456/cover_235.png

## 公众号排版顺序（建议）
1) 评分卡
2) 论文信息卡
3) 正文（A–F）
4) 封面图（若作为首图则放最前）
