# 20260805 · AI 论文速记视频号制作

## Status

- Stage: **成片待人工终审**（两篇）
- Gate: `VOICE_SCRIPT_APPROVED` → 正式 TTS ×1 ×2 → 渲染 PASS
- 平台发布：未做（待申飞终审后）

## Deliverables

### #1 G-ReAct `2608.01324` · 94.85s

- 视频：`outputs/ready/20260805/2608.01324/video-ai-paper-note/AI论文速记-2608.01324-视频号.mp4`
- 封面：`.../AI论文速记-2608.01324-封面.jpg`
- 发布文案：`.../AI论文速记-2608.01324-发布文案.md`
- TTS：request_count=1，speech_splicing=false；首尾静音清理后 94.85s（原 95.19s）
- 脚本：`outputs/video-drafts/20260805/2608.01324/AI论文速记-2608.01324-文字脚本-v1.md`

### #2 Memory Reward Inflation `2608.00017` · 90.67s

- 视频：`outputs/ready/20260805/2608.00017/video-ai-paper-note/AI论文速记-2608.00017-视频号.mp4`
- 封面：`.../AI论文速记-2608.00017-封面.jpg`
- 发布文案：`.../AI论文速记-2608.00017-发布文案.md`
- TTS：request_count=1，speech_splicing=false，90.67s
- 脚本：`outputs/video-drafts/20260805/2608.00017/AI论文速记-2608.00017-文字脚本-v1.md`

## Notes

- 跳过术语短审样音（申飞授权加速）。
- 画面按字数比例切镜（无 Whisper 实测时间线）；终审若不齐可再回校。
- 本版**不含烧录字幕**（与 0804 ThinkReset 成片策略一致，仅有 subtitle-reference.srt）。
- 未写 `FINAL.md`：需申飞人工终审后锁定。

## Next

1. 申飞耳审/目视两篇 MP4 + 封面
2. 若通过：各自补 `FINAL.md`，再考虑平台发布
3. 若改稿：必须新脚本确认 + 新一次连续 TTS（禁止复用旧音频）
