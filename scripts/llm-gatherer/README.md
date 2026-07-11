# RALPH LLM Gatherer

通过浏览器自动化与各类大模型对话，用于 RALPH 信息搜集阶段。

## 支持的服务

| 服务 | 服务名 | 说明 |
|------|--------|------|
| ChatGPT | `chatgpt` | OpenAI ChatGPT 网页版 |
| Google Gemini | `gemini` | Gemini 网页版 |
| 豆包 | `doubao` | 字节跳动豆包 |
| Kimi | `kimi` | 月之暗面 Kimi |

## 快速开始

### 1. 首次登录

```bash
cd /Users/a1-6/Desktop/workspace/scripts/llm-gatherer
python3 -m llm_gatherer login chatgpt
```

浏览器会自动打开，手动完成登录（Google/微软账号等）。登录成功后认证状态会自动保存到 `~/.ralph/llm-state/`。

### 2. 命令行提问

```bash
# 简单提问
python3 -m llm_gatherer ask chatgpt "什么是手征引力波的光学相干性？"

# 带文件提问（上传文件给 LLM 审查）
python3 -m llm_gatherer ask chatgpt "请审查这份分析结果" --file /path/to/file.pdf

# 通过 Gemini 搜索
python3 -m llm_gatherer search "chiral gravitational wave OLC"
```

### 3. 从 RALPH 程序调用

```python
from llm_gatherer.llm_ask import ask_llm

result = ask_llm("chatgpt", "分析以下公式的物理含义：...")
print(result)
```

## 认证状态管理

首次登录后，认证状态（cookies/tokens）保存在 `~/.ralph/llm-state/`：

```
~/.ralph/llm-state/
├── chatgpt.state.json
├── gemini.state.json
├── doubao.state.json
└── kimi.state.json
```

这些文件会持久化浏览器登录状态，后续使用无需重新登录。

## 架构

```
llm_gatherer/
├── __init__.py          # 包初始化
├── __main__.py          # CLI 入口
├── config.py            # 服务配置和状态路径
├── browser.py           # Playwright 浏览器封装（登录、认证状态）
├── llm_interface.py     # LLM 服务接口实现
│   ├── LLMApi           # 基类
│   ├── ChatGPTApi       # ChatGPT 网页版接口
│   ├── GeminiApi        # Gemini 网页版接口
│   └── DoubaoApi        # 豆包网页版接口
└── llm_ask.py           # RALPH 程序化调用接口
```

## 已知限制

- ChatGPT 回复提取：使用多选择器尝试提取 AI 回复，如失效请检查浏览器窗口
- 豆包回复提取：尚未实现自动提取，会提示检查浏览器窗口
- 文件上传：`ask_with_file()` 目前为接口占位，实际实现需根据各平台 UI 调整上传逻辑
