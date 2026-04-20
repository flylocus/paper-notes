# Experimental Scripts

这些脚本已从 `scripts/` 主表面归档到 `scripts/experimental/`。

原因很简单：
- 它们仍有参考价值
- 但不属于正式发布基线
- 继续把它们放在主目录，容易在临近发布时被误用

## 当前归档脚本
- `generate_all_cards.py`
- `generate_cards_pillow.py`
- `run_pipeline.py`
- `mock_scoring_and_payload.py`

## 使用规则
- 可以做并行实验
- 不能默认替代正式链
- 若实验结果要升格，必须先经过人工对比并更新正式基线文档

## 正式入口
- 总入口：`../daily_runner.py`
- 正式图片：`../generate_cards.py` + `../generate_cover.py`

