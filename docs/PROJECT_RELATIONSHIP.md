# Paper Notes 项目关系说明

## 一句话

现在只有一个真正的主项目：

`/Users/shenfei/clawd/paper-notes`

其他 `paper-notes` 相关目录，要么是兼容壳层，要么是历史参考，不再是主开发目录。

## 目录角色

### 1. 独立项目主目录

路径：

`/Users/shenfei/clawd/paper-notes`

角色：
- 唯一真实源头
- 远程仓库对应目录
- 后续脚本、文档、自动化、版本管理都以这里为准

你要做这些事时，应该来这里：
- 改代码
- 改文档
- 提交 git
- 配 automation / cron
- 看正式入口

### 2. 旧 skill 兼容壳层

路径：

`/Users/shenfei/.openclaw/workspace/skills/paper-notes`

角色：
- 兼容旧入口
- 内部大部分内容通过 symlink 指向独立项目
- 目的是不让旧调用立刻断掉

你不该在这里做这些事：
- 不要把它当主开发目录
- 不要优先从这里建新 automation
- 不要把它当“第二份项目副本”

只有这类情况还允许经过这里：
- 兼容旧脚本入口
- 兼容旧 skill 调用
- 排查历史调用为什么还能工作

### 3. 旧历史混合树

路径：

`/Users/shenfei/clawd/paper-notes-project`

角色：
- 历史版本集合
- 早期子项目、skills、实验实现和旧输出的汇总
- 只适合做对照和回看

规则：
- 不再作为当前主线实现目录
- 不要继续往里面补新脚本
- 只在“找历史版本差异”时回看

### 4. 更早的下载副本

路径：

`/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes`

角色：
- 更早的原始来源 / 下载副本
- 历史参考价值低于当前独立项目和 `paper-notes-project` 混合树

规则：
- 默认冻结
- 只有在你怀疑某个更早模板丢失时才去翻

## 现在的主从关系

```text
/Users/shenfei/clawd/paper-notes
  -> 唯一主项目

/Users/shenfei/.openclaw/workspace/skills/paper-notes
  -> 兼容壳层（指向主项目）

/Users/shenfei/clawd/paper-notes-project
  -> 历史混合树（参考）

/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes
  -> 更早下载副本（参考）
```

## 实际操作规则

1. 以后只在 `/Users/shenfei/clawd/paper-notes` 提交代码。
2. 以后所有新的 automation / cron 都应把 `cwd` 指到 `/Users/shenfei/clawd/paper-notes`。
3. 如果旧 skill 路径还能跑，不代表它重新变成了主目录。
4. 如果你在历史树里看到了更早实现，默认只抄思路，不把主线改回去。
5. 如果未来要删兼容壳层，先确认没有旧入口还依赖它。

## 遇到问题时先去哪

- “我要改正式流程”：
  去 `/Users/shenfei/clawd/paper-notes`

- “为什么旧命令还能跑”：
  看 `/Users/shenfei/.openclaw/workspace/skills/paper-notes`

- “之前是不是有另一版实现”：
  看 `/Users/shenfei/clawd/paper-notes-project`

- “最早模板长什么样”：
  看 `/Users/shenfei/Downloads/paper-notes-project/skills/paper-notes`
