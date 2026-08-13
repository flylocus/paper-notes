# paper-notes 视频画面函数参考（2026-08-13 首版）

> 用途：produce_ai_paper_video.py 的 art_pages 按 paper_id 白名单分发画面函数。新论文渲染前必须为其写页面函数并加 elif 分支，否则报「未配置画面模板」。

## 画布 API（produce_ai_paper_video.py 内置）

| 函数 | 作用 |
|------|------|
| `canvas()` | 1080×1920 深海蓝底 `#0B1739` + 网格 + 光晕 |
| `header(d, title)` | 顶部「AI 论文速记」+ 标题 + 分隔线（art_pages 自动调） |
| `statement(d, title, line)` | 大标题（~78px）+ 副行（~58px，accent 色） |
| `label(d, box, value, accent, size)` | 圆角卡片 + 居中文字 |
| `metric(d, box, value, name, accent, value_size)` | 数字大卡（value + 说明） |
| `boundary_item(d, y, title, detail)` | 边界紫卡 `#29244A`/PURPLE |
| `card(d, box, fill, outline, r, width)` | 通用圆角卡（判断橙 `#4F3D28`/ORANGE） |
| `close_page(data)` | 末帧：标语 + Logo + arXiv（品牌尾） |
| 配色 | NAVY 底 / CYAN 事实 / PURPLE 边界 / ORANGE 判断 / WHITE / MUTED |

## 五段式 → 视觉映射（2026-08-13 双发验证）

| unit | 视觉 | 元素 |
|------|------|------|
| hook | 冲突句 + 场景 label | statement(双行) + label(问题卡) |
| judgment | 判断橙卡 | card fill `#4F3D28` outline ORANGE + 2-3 行判断句 |
| evidence_1 | 方法/第一个证据 | statement + label 列表 或 metric |
| evidence_2 | 数字证据 | metric 大卡（vs 对比）+ 底部说明 |
| boundary | 边界紫卡 ×3 | boundary_item(误剪/范围/口径) |
| peak | 唯一峰值卡（判断橙） | 与 judgment 同款卡，落点句 3 行 |
| close | 品牌尾 | close_page（Logo 收尾） |

## 加新论文的步骤

1. 在 `art_pages` 的 elif 链加 `elif pid == "XXXX": xxx_page(d, visual)`
2. 定义 `xxx_page(d, visual)`（参照下方示例，覆盖 hook/judgment/evidence_1/evidence_2/boundary/peak）
3. timeline 最后一段 `visual: "close"`（否则末帧是大白板）
4. video-brief.json 必须含 `cover_title` + `cover_subtitle`

## 示例：retree_page（2608.10676）

```python
def retree_page(d, visual):
    if visual in {"hook"}:
        statement(d, "同一个错误", "会付几遍钱？")
        label(d, (110, 735, 970, 930), "滚动摘要把错话锁进去", CYAN, 42)
    elif visual in {"judgment"}:
        tx(d, (72, 300), "我的判断", 58, WHITE, True)
        card(d, (86, 540, 994, 1080), fill="#4F3D28", outline=ORANGE, r=48, width=5)
        tx(d, (W // 2, 690), "压缩管长度", 60, ORANGE, True, "mm")
        tx(d, (W // 2, 850), "溯源才管安全回滚", 46, WHITE, True, "mm")
    elif visual == "evidence_1":
        statement(d, "证据树", "冲突 → 定位 → 回滚")
        label(d, (112, 660, 968, 810), "摘要 + 来源 + 修订史", CYAN, 42)
        label(d, (112, 860, 968, 1010), "替换证据 · 重生摘要", CYAN, 44)
        label(d, (112, 1060, 968, 1210), "剪掉依赖子孙再搜", CYAN, 44)
    elif visual == "evidence_2":
        tx(d, (72, 300), "2149 题 · Qwen3-8B", 46, WHITE, True)
        metric(d, (88, 500, 992, 740), "44.0 vs 30.1", "总体 · +13.9pp", CYAN, 60)
        metric(d, (88, 830, 992, 1070), "61.6 vs 36.0", "Bamboogle · +25.6pp", CYAN, 58)
    elif visual in {"boundary", "boundary_close"}:
        tx(d, (72, 300), "不能直接外推", 62, PURPLE, True)
        boundary_item(d, 540, "硬剪枝误剪", "子孙一律当依赖，有用状态被丢")
        boundary_item(d, 760, "评测范围", "停在 QA/search，最多 8 次检索")
        boundary_item(d, 980, "冲突判定", "假阴性留污染，假阳性过度修剪")
    elif visual in {"peak"}:
        tx(d, (72, 300), "唯一判断", 58, WHITE, True)
        card(d, (86, 540, 994, 1080), fill="#4F3D28", outline=ORANGE, r=48, width=5)
        tx(d, (W // 2, 680), "结论被推翻时", 56, ORANGE, True, "mm")
        tx(d, (W // 2, 840), "依赖状态必须", 50, WHITE, True, "mm")
        tx(d, (W // 2, 960), "一起失效", 64, WHITE, True, "mm")
```

> catmem_page（2608.11095）同构：hook「一百行开外/只增不减」、judgment「不是忘了/是不敢忘」、evidence「+226%/+4.9」「99.3%」、boundary「自动删不安全/模型打分/语料范围」、peak「删规则要先记得当初为什么加」。

## 时长与 speed

- render 硬检查 70–95s（audio duration）
- 脚本 voice.speed 硬编码 0.98（约 280 字 → 75s）；长稿（>320 字）需 speed 1.1–1.15（11095 用 1.15 → 79.4s），改脚本 `"speed": 0.98` 后跑 formal
