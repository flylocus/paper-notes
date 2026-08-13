# 20260804 · AI 论文速记视频号制作

## Context Pack

- Goal: 为已发布的 ThinkReset `2607.28642` 与 Zero-Mem `2607.29377` 各制作一条 AI 论文速记视频号视频。
- Constraints: 逐篇独立；不得改动已发图文；必须先取得完整审核脚本与连续配音稿的明确确认；正式 TTS 仅一次连续请求；原生 9:16；Logo 原样等比放置；完成视频专属 QA 后才可交人工终审。
- Read set: `docs/AI_PAPER_NOTE_VIDEO_GUIDE.md`; 两篇各自的 `note.md`、`evidence_ledger.json`。
- Out of scope: 平台发布、重跑文章生产链、混合两篇论文本体或复用昨日音频。
- Done means: 两篇均有独立的确认后连续旁白、9:16 成片、封面、SRT、发布材料与视频 QA；仅在人工终审后各自建立一个 `FINAL.md`。

## Current state

- 上游资格：两篇当前 `qa_report.md=PASS`、`preflight blocking=0`、`gate5=PASS` 且各有 `evidence_ledger.json`。
- 已完成：两篇最新审核脚本与双轨口播均为 `VOICE_SCRIPT_APPROVED`；各完成一段术语短审样音（48 kHz 单声道，分别 27.511 秒与 25.340 秒；正式 TTS 请求数均为 0）。
- 阻塞：等待申飞人工确认两段样音的专有词读法；此前不得调用每篇唯一的一次正式连续 TTS，亦不得输出正式视频。

## Handoff

- Goal: 同上。
- Done: 两篇已确认文字脚本、双轨口播适配与术语短审样音。
- Open: 申飞确认样音；确认后依次做每篇一次连续 TTS、原生竖版画面、合成与 QA。
- Constraints: 不改已发图文；不分段拼接配音；不发布平台。
- Next agent should: 仅在确认记录落盘后推进 Stage 5–7，并保留每篇版本边界。
- Read set: 同 Context Pack，加本任务卡。
