# Hermes 机制描述包（迁移/重建用）

> 灵魂层已自动备份到私有仓库 `dd2003-460/hermes-config`（cron 每小时快照）。
> 本文件回答"这些文件怎么工作的、丢了怎么重建"——备份保数据，本文件保理解。
> 生成: 2026-11-20 · 来源: 实测 ~/.hermes 结构 + hermes-agent 源码

## 一、分层总览（9.8G 的构成）

| 层 | 内容 | 大小 | 保护方式 | 丢了的代价 |
|---|---|---|---|---|
| **灵魂层** | rules/ agent-hooks/ config.yaml .stage-gate/ memories/ skills/ cron/jobs.json | ~170M | git 私有仓库, 每小时快照 | **最高**: 规则/触发/记忆/技能全丢, 只能凭记忆重建 |
| **历史层** | sessions/*.jsonl + state.db (对话历史) | ~1.2G | 本地 tar 每日包 (保留7天) + 可手动上网盘 | 中: 历史对话丢, 但 session_search 索引和落盘笔记还在 |
| **可重装层** | hermes-agent/ (框架4.2G) tools/ (node/npm 929M) installs/ (743M) cache/ lsp/ logs/ | ~9.2G | **不备份**: `hermes update` / 重装即恢复 | 低: 重装即可, 耗时不丢数据 |

## 二、灵魂层各组件机制

### 1. 规则注入（pre_llm_call hook）
- **入口**: `config.yaml` hooks.pre_llm_call → `~/.hermes/agent-hooks/inject-rules.py`
- **路由表**: `~/.hermes/agent-hooks/routing.json` (21 条规则, 3 层)
  - `always: true` (9条): 每轮固定注入, 都是 100-170 字符小便签, 合计 ~262 tokens/轮
  - `trigger` (8条): 消息命中关键词/语义时注入**全文** (engineering 一条 ~4000 字符)
  - `random` (闲聊触发器): per-session 计数器 + 随机阈值 2-5 轮 + 滑动窗口防密集
- **规则本体**: `~/.hermes/rules/*.md` (22 个文件, 每条规则的完整正文)
- **重建**: clone hermes-config 仓库 → rsync 回 ~/.hermes/ → config.yaml hooks 路径不变即生效

### 2. 续推/停止门（pre_verify hook）
- **入口**: config.yaml hooks.pre_verify → `workspace/tools/stage-gate/stage_gate/adapters/stop_hook.py`
- **机制**: turn 结束 (模型返回无 tool_calls 的响应) 时**同步调用**, 返回 continue 则打回续推
- **节流**: `_pre_verify_nudges` 计数防 hook 锁死 turn (框架硬限制)
- **状态**: `~/.hermes/.stage-gate/*.json` (goal 状态机) + `agent-hooks/ralph-stop-count.json`

### 3. 工具调用拦截（pre/post_tool_call hook）
- `workspace/.hooks/engine.py` (PreToolUse/PostToolUse, 规则在 workspace/.hooks/rules.json, 已进 workspace git)
- `agent-hooks/loop-guard.py` (pre/post, 循环检测)
- **已知风险**: engine.py 挂死 = 所有工具调用阻塞 (2026-11-20 18:05 实测, pkill 恢复), 无自动熔断

### 4. 记忆
- `~/.hermes/memories/MEMORY.md` + `USER.md` (每轮注入 system prompt)
- 项目级记忆在 workspace 各项目 memory/ (workspace git 已保护)

### 5. 技能
- `~/.hermes/skills/` (62M, 含用户自建: arena-outsource/ego-browser/ralph-cross-validation 等)
- 内置技能可重装恢复, 用户自建 skill 靠本备份

### 6. 定时任务
- `~/.hermes/cron/jobs.json` (声明, 已备份) + executions.db (执行历史, 故意不备份)

## 三、迁移步骤（换机器/换 harness）

1. **框架**: `hermes update` 或按官方文档重装 (可重装层)
2. **灵魂**: `git clone dd2003-460/hermes-config` → 各目录 rsync 回 ~/.hermes/
3. **历史**(可选): 解 hermes-history-*.tar.gz 回 sessions/ + state.db
4. **验证**: 起一轮对话, 检查 ①规则注入出现 ②stop_hook 续推 ③记忆注入 ④cron 列表
5. **workspace**: 独立 git 仓库 (hermes-workspace-zero), 单独 clone

## 四、已知边界（诚实标注）

- **hook 接口兼容性**: 备份的是声明层 (routing.json schema)。若新 harness 的 hook 接口变了, 需适配 schema, 规则文本本身不丢
- **state.db 2.9G 未备份**: 里面主要是 async_delegations 等运行态, 历史对话在 sessions/ 里; 若发现 state.db 有不可替代数据, 加进历史层 tar
- **ego-browser 登录态**: 不在任何备份里 (浏览器 profile 在别处), 迁移后需重新登录 arena/battle
- **8787 vLLM 容器**: 在服务器上, 与本机 hermes 无关, 不受迁移影响

## 五、备份脚本

| 脚本 | 频率 | 产出 |
|---|---|---|
| `scripts/hermes-config-sync.sh` | cron 每小时 17 分 | git push → hermes-config 仓库 |
| `scripts/hermes-history-pack.sh` | 手动/每日 | workspace/backups/hermes-history-<日期>.tar.gz (保留7天) |
