# 步骤 2：替换 profile patch 中的 legacy preset 声明

## 目标
将 profile patch 中三个损坏的 legacy preset 声明（loop-recipe/loop-recipe2/loop-recipe3）替换为一个 0.14.0 兼容的新 preset 声明（id: loop）。

## 涉及文件
- `~/Library/Application Support/dsh-desktop/harness/profiles/desktop/cordis.patch.yml`（修改目标）
- `~/Library/Application Support/dsh-desktop/harness/.agent-presets/loop/agent.cordis.yml`（插件配置来源）
- `~/Library/Application Support/dsh-desktop/harness/.agent-presets/loop/preset.yml`（name/description 来源）

## 做法
1. 定位 legacy preset 区块：从 `# dsh-desktop legacy presets begin`（约 line 124）到 `# dsh-desktop legacy presets end`（约 line 1072）
2. 删除该区块内的三个 `- insert:` 块（preset-loop-recipe、preset-loop-recipe2、preset-loop-recipe3）
3. 插入一个新的 `- insert:` 块，声明 preset-loop：
   ```yaml
   - insert:
       - id: preset-loop
         name: '@deepseek-ai/dsh-agent-preset'
         config:
           id: loop
           name: "Loop 配方模式"
           description: "融合科研证据与任务拆分的自主循环工作流（0.14.0 适配版）"
           order: 10
           plugins:
             # <从 agent.cordis.yml 逐字复制所有插件条目>
   ```
4. 插件条目从 `agent.cordis.yml` 逐字复制（保持 YAML 格式一致），包括：
   - persona（config.prefix，119 行中文 persona 文本，仅含 {{model}}，无 {{cwd}}）
   - agent-instructions（maxBytes: 65536）
   - tool-bash（disabled: !!js process.platform === 'win32'）
   - tool-pwsh（disabled: !!js process.platform !== 'win32'）
   - tool-fs
   - tool-fs-search（sampleOverCapGlobResults: false）
   - tool-jobs
   - skill-filesystem
   - tool-skill
   - command-goal
   - tool-goal
   - planning group（isolate planMode; plan-mode with non-empty English section）
   - compaction group（isolate compaction+toolResultPruner; compaction-basic, command-compact, tool-result-pruner thresholdChars 8192/headChars 4096/tailChars 1024）
   - delegation group（isolate workflowEngine; tool-subagent-control, tool-subagent {provider: spawn, toolName: subagent, modelSelection: true, modelDiscovery: true}, tool-subagent-fork {provider: fork, toolName: subagent_fork}）
   - tool-ask-user
   - tool-todo（allowParallelInProgress: true）
   - tool-web（fetch: true, searchTimeoutMs: 60000）

## 验收标准
- profile patch 中不再包含 `preset-loop-recipe`、`preset-loop-recipe2`、`preset-loop-recipe3`
- profile patch 中包含 `preset-loop` 声明
- `grep -c "{{cwd}}" cordis.patch.yml` 返回 0（新 preset 中无 {{cwd}}）
- YAML 语法有效（可用 `python3 -c "import yaml; yaml.safe_load(open('cordis.patch.yml'))"` 验证）
