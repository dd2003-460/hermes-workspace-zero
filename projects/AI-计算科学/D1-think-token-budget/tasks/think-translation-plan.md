# thinking 翻译方案（2026-10-19，think-translate）

## 需求
模型保持英文思考（不降表现），proxy 自动把 thinking 翻译成中文给前端显示。用户原话："我的模型都用英文思考，强制改中文可能降低表现，所以能不能翻译思考过程（写插件，不要让ai干，弄个自动的）。"

## 推荐方案：本地 NMT（onnxruntime + NLLB-600M-distilled 或 Argos en-zh）
**理由（性价比优先，AGENTS.md 默认画像）**：
1. 免费、本地、无 API 依赖——thinking 内容可能含私密信息，不出网（安全红线）。
2. 不占远程 vLLM 显存/token——远程 vLLM 方案被否决（同模型自译无信息增益，还烧卡）。
3. 流式可用：分片送译 → 边想边翻边显示，不需要等整段结束。
4. 一次性安装成本 ~1GB 模型，之后 CPU 常驻进程开销可忽略。

## 已定：接入层（已实现，默认关闭）
proxy.mjs think-split 模块预留 `THINK_TRANSLATE_CMD` 环境变量：
- 值 = 翻译子进程命令（stdin: JSONL `{"id":N,"part":"英文分片"}`；stdout: `{"id":N,"out":"中文"}`）
- proxy 对每个 thinking 分片（两个标签之间，或孤立 close 前的内容）逐片送译，FIFO 保序，60s 超时兜底原样回传英文。
- **流式显示**：英文 thinking 到达即写 `delta.reasoning_content`（前端立刻可折叠、可滚动）；当前部署实现为"整段 thinking 结束后翻译、原文照常显示"——翻译输出经 `THINK_TRANSLATE_CMD` 消费，但**尚未接到前端显示通道**（要显示中文需 DSH 前端配合或改 reasoning 块重建，见"接入点还缺什么"）。
- 未设置该变量 = 纯转换不翻译（当前部署态）。

## 翻译器选型（待决，按性价比排序）
| 方案 | 体积 | 速度（Mac CPU） | 质量 | 备注 |
|------|------|------|------|------|
| **ArgoMT-small / NLLB-600M-distilled int8** | ~0.6-1.5GB | ~5-20 tok/s | 中 | 需下载 HF 权重；onnxruntime CPU 可跑 |
| **LibreTranslate（本地）** | ~1GB | 慢 | 中 | 自带 HTTP 服务，接入简单 |
| **远程 vLLM 当翻译器** | 0 | 快 | **差** | 同模型同权重，英文→中文无信息增益，且占推理卡显存/token——否决 |
| **ego-browser 网页 LLM** | 0 | 秒级延迟 | 高 | 非流式、需人工登录、违反 subagent 网络规则——仅调试用 |
| **规则/词典** | 小 | 快 | 不可行 | thinking 是完整英文句子，词典覆盖不了 |

**推荐**：onnxruntime + NLLB-600M-distilled-en-zh（或 Argos Translate `en-zh` 包，`argos-translate install en-zh` 一条命令，自带 C 运行时，CPU 优化好）。封装成一个常驻 node/HTTP 小服务或 stdin 进程，填进 `THINK_TRANSLATE_CMD`。

## 最小可运行 stub
`think-translate-stub.py`（~30 行，与本文件同目录；/tmp 下也有一份）：stdin/stdout JSONL 协议，`translate()` 当前是 `[中文]` 前缀伪翻译，替换该函数接入 argostranslate 或 onnxruntime 即成品。启用方式：
```
THINK_TRANSLATE_CMD="python3 /path/to/think-translate-stub.py"
```
（写入 launchd plist 的 EnvironmentVariables 后 kickstart 即生效。）

## 接入点还缺什么
已定并部署：proxy 端翻译层（常驻子进程，stdin JSONL 请求 `{"id","part"}` / stdout `id:out` 行响应，10s 超时兜底回传原文；`THINK_TRANSLATE_CMD` 未设置时零开销）。还缺：
1. 一个真翻译进程填进 `THINK_TRANSLATE_CMD`（stub 已就绪并验证，模型待接）。
2. 翻译输出 → 前端的显示通道（当前 proxy 已能拿到中文结果，但 DSH 只消费 `reasoning_content`；要"中文显示/覆盖"需 DSH 前端侧改，见待决 3）。

## 待决
1. 翻译器模型下载（~1GB，走 ego-browser 查镜像源，免费）。
2. 流式增量翻译分片粒度（当前按标签段整段送译；thinking 可很长，需评估单段延迟 vs 分句送译的质量损失）。
3. 中文覆盖显示的前端支持：DSH 前端目前只认 `reasoning_content` 字段建 thinking 块——"先英文后中文"要前端配合（或翻译完成后重发整段覆盖，依赖 DSH 是否合并同 signature 的 thinking 块——需实测）。**若 DSH 是追加语义，则覆盖方案不可行，只能整段翻译完再一次性下发（牺牲流式）**。

## 回滚
`launchctl` 重启服务时不带 `THINK_TRANSLATE_CMD` 即回纯转换；或整体回滚见 /tmp/think-split-plan.md。
