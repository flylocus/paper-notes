# PilotDeck 架构模式参考（2026-05-30）

> 来源：源代码阅读 `github.com/OpenBMB/PilotDeck`（commit 未固定）
> 用途：论文速记 / 金融观察系统的架构演进参考

## 1. Smart Routing（Token Saver）

### 核心思想

不所有请求走同一模型，而是用一个小 Judge 对输入做 **tier 分类**，按分类路由到不同模型。

### 三层路由

| 层 | 判定依据 | 优先级 |
|----|---------|--------|
| **Explicit** | `metadata.explicitProvider/model` 显式指定 | 最高 |
| **Subagent tag** | 消息体含 `<pilotdeck-subagent-model>provider/model</...>` | 次高 |
| **Token Saver Judge** | LLM 分类 → tier | 默认 |
| **Fallback** | Judge 失败 → default tier | 最低 |

### Token Saver 执行流程

```
用户消息 → extractLastUserMessage()
    → generateJudgePrompt() 注入 tier 描述 + rules
    → judgeRuntime.complete(judgeRequest) — temperature=0, maxOutputTokens=256, timeout=5s
    → parseTier() 用 <tier>NAME</tier> 解析
    → 选对应 tier 的 model → return
```

### Tier 设计（默认 4 层）

```typescript
const DEFAULT_TIER_DESCRIPTIONS = {
  simple:   "Simple greetings, confirmations, single-step Q&A, trivial file writes, remembering rules",
  medium:   "Single tool call, short text generation, 1-2 file read/write, code generation",
  complex:  "Needs sub-agent orchestration: parallel workstreams, delegation to specialized agents",
  reasoning:"Deep single-agent work: multi-file operations, data analysis, multi-step workflows, web research"
}
```

complex 是**唯一触发 Auto-Orchestrate** 的 tier——主代理被替换成编排者（只剩 5 个 tool: agent/read_file/grep/glob/read_skill）。

### Sticky 机制

- 同一 session 内的后续消息粘着上次 tier，避免重新分类
- `sessionStore.set({ sessionId, tokenSaverTier, stickyProvider, stickyModel })`
- `invalidateSticky()` 在新 turn 开始时清除，让 Judge 重新评估新鲜消息
- 短确认消息（"go" "ok" "好的" "继续"）保持 previousTier——Judge prompt 里用 CRITICAL RULE 声明

### Judge Prompt 模板

```
Available tiers:
- simple: ...
- medium: ...
- complex: ...
- reasoning: ...

Routing rules:
- ...

User message:
"""..."""

Respond with only <tier>NAME</tier>.
```

### 关键文件

| 文件 | 函数/类 | 作用 |
|------|---------|------|
| `src/router/RouterRuntime.ts` | `createRouterRuntime().decide()` | 路由总入口，编排 resolveCustom→decideScenario→tokenSaver→orchestration |
| `src/router/scenario/decideScenario.ts` | `decideScenario()` | explicit/subagent/default 三层检出 |
| `src/router/tokenSaver/classifyAndRoute.ts` | `classifyAndRoute()` | Judge 调用 + parseTier + retry+timeout |
| `src/router/tokenSaver/generateJudgePrompt.ts` | `generateJudgePrompt()` | 构建 Judge prompt + previousTier 注入 |
| `src/router/tokenSaver/parseTier.ts` | `parseTier()` | `<tier>NAME</tier>` 正则 + fuzzy fallback |
| `src/router/config/schema.ts` | `RouterConfig / RouterTokenSaverConfig` | 类型定义 + DEFAULT_TIER_DESCRIPTIONS |
| `src/router/session/sessionUsageCache.ts` | `SessionUsageCache` | Sticky 缓存，TTL 30s |
| `src/router/fallback/runFallbackChain.ts` | `planFallback()` | 按 scenario 类型构建 fallback chain |

---

## 2. White-box Memory（EdgeClaw / ClawXMemory）

### 核心思想

**不用 embedding / vector DB。** 纯 LLM 做所有路由决策（route decision + file selection + dream rewrite），每一步都有 trace，可审计、可调试。

### 三层架构

```
EdgeClawMemoryProvider (Bridge)
  → EdgeClawMemoryService (orchestrator)
      → ReasoningRetriever (retrieval loop)
          → FileMemoryStore (filesystem .md)
          → SQLite (L0 sessions, traces, pipeline state)
      → HeartbeatIndexer (background capture→index→dream)
      → LlmMemoryExtractor (LLM judge calls)
```

### Retrieval 流程

```
query → 1. Route Decision (LLM: decideFileMemoryRoute)
         → "user" / "project" / "mix" / "none"
             ↓
         2. Load base (user profile OR project meta)
             ↓
         3. Scan manifest (list .md files in scope)
             ↓
         4. File Selection (LLM: selectFileManifestEntries)
             → pick top-k files (user=1, project=5)
             ↓
         5. Build System Context
             → ## ClawXMemory Recall section → inject into system prompt
```

### Storage

**File-system .md 即数据库** — 每个 memory entry 是带 frontmatter 的 markdown 文件：

```yaml
---
name: xxx
description: xxx
type: user | feedback | project | general_project_meta
scope: global | project
projectId: ...
updatedAt: ...
dreamUpdatedAt: ...
deprecated: ...
---
```

目录结构：
```
~/.pilotdeck/memory/
├── workspaces/<hash>/   # 每个 workspace 独立
│   ├── Global/
│   │   ├── UserIdentity/user-profile.md
│   │   └── UserIdentityNotes/
│   ├── Project/*.md
│   ├── Feedback/*.md
│   └── MEMORY.md (manifest)
└── global/              # general workspace 模式
```

### Dream Pipeline（后台跑步机）

```
HeartbeatIndexer (background)
  → Capture: L0 session 存 SQLite
  → Index: LLM 提取关键信息 → 写 .md
  → Dream: LLM 跨文件融合、去重、重写 → 更新 frontmatter
  → trace 记录每一步（可 rollback）
```

### 关键文件

| 文件 | 类/函数 | 作用 |
|------|---------|------|
| `src/context/memory/edgeclaw-memory-core/src/core/retrieval/reasoning-loop.ts` | `ReasoningRetriever.retrieve()` | 完整 retrieval loop |
| `src/context/memory/edgeclaw-memory-core/src/core/retrieval/reasoning-loop.ts` | `buildProjectShortlist()` | 通用 workspace 模式下的项目匹配（纯 token 匹配，无 embedding） |
| `src/context/memory/edgeclaw-memory-core/src/core/storage/sqlite.ts` | `MemoryRepository` | SQLite 会话存储 + 文件系统桥接 |
| `src/context/memory/edgeclaw-memory-core/src/core/file-memory.ts` | `FileMemoryStore` | 文件系统操作：读写 .md manifest/frontmatter |
| `src/context/memory/edgeclaw-memory-core/src/core/types.ts` | `MemoryRoute / MemoryFileFrontmatter` | 类型定义 |
| `src/context/memory/edgeclaw-memory-core/src/core/pipeline/heartbeat.ts` | `HeartbeatIndexer` | 后台 capture→index→dream 调度 |
| `src/context/memory/EdgeClawMemoryProvider.ts` | `EdgeClawMemoryProvider` | 桥接：适配 Hermes MemoryResolver 接口 |
| `src/context/memory/MemoryResolver.ts` | `canonicalMessagesToMemoryMessages()` | 消息标准化 |

### 关键设计决策

1. **不用 embedding** — 纯 LLM route decision + file selection，每一步有 trace，可调试
2. **文件系统的 .md 就是数据库** — 可读、可编辑、可 git diff
3. **workspace 隔离** — `workspaces/<hash>/` 不同项目独立
4. **General vs Single 模式** — Single 模式一个项目一份记忆，General 模式跨项目共享
5. **CJK 搜索** — 扩展 2-3 字中文 token，含 stopwords 过滤

---

## 3. 对论文速记系统的借鉴总结

| 借鉴点 | PilotDeck 实现 | 论文速记对应 |
|--------|---------------|-------------|
| Tier 路由 | Token Saver Judge → 4-tier | `paper-note-router.json` 4-tier |
| Sticky | sessionStore + invalidateSticky | 同一论文会话保持 tier |
| Judge prompt | `generateJudgePrompt()` 模板 | 已集成到 style-optimization SKILL.md |
| Route decision | 纯 LLM 不用 embedding | Judge 主模型 temperature=0 直接分类 |
| Fallback | `planFallback()` → fallback chain | Judge 无效 → 默认 standard |
| White-box trace | 每一步有 RetrievalTrace | validate_output.py 9 项检查 |
| Session isolation | workspace/<hash>/ 隔离 | outputs/{date}/{id}/ 目录隔离 |
