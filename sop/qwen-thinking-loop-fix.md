# Qwen3.6 思考和输出循环解决方案

> 来源：2026-08-06 ego-browser 搜索研究
> 参考：Steve Scargall 博客、HuggingFace 讨论、GitHub Issue #145、Zach Mueller TIL

## 问题本质

Qwen3.6（及其他推理模型）有"思考模式"，在输出实际答案前先生成内部推理内容。这导致：

1. **Token 预算耗尽**：思考模式消耗了 `max_tokens` 预算，`content: null` + `finish_reason: "length"`
2. **无限推理循环**：模型陷入循环思考，输出重复无意义内容
3. **preserve_thinking 参数**：Qwen3.6 默认启用 `preserve_thinking`，跨轮次保留思考上下文，加剧循环
4. **Agent 重试循环**：Agent 收到 `content: null` 后重试，设置不变，无限循环

## 核心解决方案（4 层防御）

### 第 1 层：服务端默认思考关闭

```bash
# vLLM
--default-chat-template-kwargs '{"enable_thinking": false}'

# llama.cpp
--reasoning-budget 4096
--reasoning-budget-message "OK, I've thought long enough. Let's answer."
```

### 第 2 层：Agent 按需开启（带高预算）

```json
{
  "model": "YOUR_MODEL",
  "messages": [...],
  "chat_template_kwargs": {"enable_thinking": true},
  "max_tokens": 16000
}
```

注意：思考开启时需要 4-6 倍预算（1500-3000 tokens 思考开销）

### 第 3 层：LiteLLM 别名模式

```yaml
models:
  - model_name: "local/llm"  # 默认，快速
    litellm_params:
      model: "hosted_vllm/YOUR_MODEL"
      api_base: "http://YOUR_SERVER:8000/v1"
      extra_body:
        chat_template_kwargs:
          enable_thinking: false

  - model_name: "local/llm-thinking"  # 复杂问题
    litellm_params:
      model: "hosted_vllm/YOUR_MODEL"
      api_base: "http://YOUR_SERVER:8000/v1"
      extra_body:
        chat_template_kwargs:
          enable_thinking: true
```

### 第 4 层：防御性重试逻辑

```python
def call_llm(messages, prefer_thinking=False):
    max_tokens = 6000 if prefer_thinking else 1500
    for attempt in range(3):
        response = client.chat_completion(
            messages=messages,
            chat_template_kwargs={"enable_thinking": prefer_thinking},
            max_tokens=max_tokens,
        )
        choice = response.choices[0]

        # 成功响应
        if choice.finish_reason == "stop" and choice.message.content:
            return choice.message.content

        # 思考耗尽预算 → 降级为思考关闭
        if prefer_thinking and choice.finish_reason == "length":
            prefer_thinking = False
            max_tokens = 1500
            continue

        # 通用截断 → 增加预算重试
        max_tokens *= 2

    raise RuntimeError(f"No usable response after 3 attempts")
```

## Prompt 层修复（最关键）

在 system prompt 中明确添加思考控制指令：

```markdown
## 思考模式控制

1. **简单任务**（代码生成、工具调用、分类、摘要）：直接回答，不要思考
2. **复杂任务**（多步研究、架构决策、数学证明）：可以思考，但必须：
   - 思考不超过 2000 tokens
   - 思考后必须输出明确答案
   - 如果思考超过 1000 tokens 仍未得出结论，立即停止思考并回答
3. **禁止**：循环思考、重复推理、无结论的思考
4. **如果收到 `content: null` 响应**：降低思考深度，直接给出最简答案
```

## 检测是否受影响

```bash
# 快速诊断
curl -s http://YOUR_SERVER:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "YOUR_MODEL",
    "messages": [...],
    "max_tokens": YOUR_AGENT_MAX_TOKENS
  }' | jq '.choices[0]'

# 检查三个字段：
# finish_reason: "length" → 截断
# message.content: null → 无输出
# message.reasoning: "..." → 思考内容填充
```

## 适用模型

- Qwen3 系列（Qwen3.5, Qwen3.6）
- Gemma 系列
- GLM-4.5/4.6/4.7
- DeepSeek-R1
- gpt-oss

## 关键参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| `enable_thinking` | false | 默认关闭 |
| `max_tokens` (thinking off) | 1500 | 足够大多数任务 |
| `max_tokens` (thinking on) | 16000 | 留足思考+回答空间 |
| `--reasoning-budget` (llama.cpp) | 4096 | 思考 token 上限 |
| `--reasoning-budget-message` | 自定义 | 自然停止思考的提示 |
| `repetition_penalty` | 1.0-1.15 | 防止重复输出 |
| `temperature` (reasoning) | 0.6-1.0 | 高温度增加多样性 |
