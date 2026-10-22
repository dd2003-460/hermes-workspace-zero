# Arena 外包标准流程（SOP）【已并入 · 存档】

> ⚠️ **2026-10-22 起本文件不再单独使用**：全部内容已并入 `agents/arena-loop-pipeline.md`（唯一入口 SOP）。本文件仅作存档保留，goal 不再索引它。
> **仓库映射更新**（以 arena-loop-pipeline.md §3.1 为准）：prompt-first 流程调研 → `dd2003-460/prompt-first-bench`（**已建 · 已 push** 2026-10-22，含 loop/ + sop/ + rubric/ + tasks/001）。

> origin: ai · 2026-10-22 · 成璐指令"arena=免费劳动力，直接连仓库执行"
> 适用：所有需要 LLM 执行 + 评分 + push 的任务（decomp T4、风格蒸馏、论文校对等）

## 1. 选仓库（按任务选对应仓库，不是固定连一个）

| 任务类型 | 仓库 | 说明 |
|---------|------|------|
| decomp T4 消融 | `dd2003-460/decomp-bench` | 任务书在 `tasks/T4-arena-batch*.md` |
| 风格蒸馏 | `dd2003-460/persona-distill`（假设） | 任务书在 `tasks/` |
| 论文校对 | `dd2003-460/academic-AI`（假设） | 任务书在 `tasks/` |
| 媒体 pipeline | `dd2003-460/d1-media-pipeline`（假设） | 任务书在 `tasks/` |

**原则**：每个项目有自己的仓库，arena 连接对应仓库，读仓库内的任务书执行。不跨仓库混用。

## 2. 连接仓库（GitHub App 授权）

1. GitHub → Settings → Applications → Installed GitHub Apps → Arena AI Coding Agent → Configure
2. Repository access = "All repositories"（含私有）
3. 保存后，arena 的所有会话都能访问所有仓库

**验证**：`curl -s -H "Authorization: token <arena-app-token>" https://api.github.com/repos/dd2003-460/decomp-bench` 返回 200 = 连接成功

## 3. 发任务书（读仓库内 tasks/*.md）

```bash
# arena 会话内执行：
git clone https://github.com/dd2003-460/<repo>.git
cd <repo>
cat tasks/<task-id>.md  # 读任务书
# 按任务书执行
```

**任务书格式**（必须包含）：
- 任务目标（1-2 句）
- 变体清单（如有）
- 执行步骤（prompt→输出→评分→汇总）
- 评分标准（引用 rubric 文件）
- 验收标准（完整输出非摘要 / commit push）

## 4. 执行 + 评分 + push

```bash
# arena 按任务书执行，每步：
# 1. 生成输出 → bench/runs/<task>/<variant>/run<N>.md
# 2. 评分 → bench/runs/<task>/<variant>/run<N>-score.md
# 3. 汇总 → bench/runs/<task>/<variant>/summary.md
# 4. commit + push
git add -A
git commit -m "feat: <task> <variant> run<N> + score + summary"
git push
```

## 5. 失败降级（403 / 网络 / 权限）

| 故障 | 诊断 | 降级方案 |
|------|------|---------|
| git clone 403 | `curl -s -o /dev/null -w '%{http_code}' https://github.com` 测网络 | ① 用 GitHub REST API（Contents API）读写文件 ② 上传任务书到对话本机执行 ③ Lead 本地自答（conf-0.2） |
| token 过期 | `git ls-remote` 测权限 | 重新 OAuth 授权 / 用 `gh auth token` 生成新 token |
| arena 沙箱拦截 git | `curl https://api.github.com` 通但 `git clone` 不通 | 用 GitHub REST API（不走 git） |

**降级原则**：arena 通道不可用 → 不阻塞，降级到 Lead 本地自答（conf-0.2），同时记录故障到 `knowledge/efficiency-bottlenecks.md`。

## 6. goal 模板引用

所有需要 arena 执行的 goal，目标描述包含：
```
按 `agents/arena-outsource.md` 流程外包：
1. 选仓库：<repo>
2. 连接仓库：GitHub App 授权（all repositories）
3. 发任务书：读 <repo>/tasks/<task-id>.md
4. 执行 + 评分 + push
5. 失败降级：按 SOP §5
```

## 7. 维护

- 新增项目 → 更新 §1 仓库映射表
- 故障修复 → 更新 §5 降级方案
- SOP 本身变更 → commit + 更新本文件历史
