# 任务：接入 LLM Gatherer — 信息搜集阶段的对话能力

## 目标
跑通 RALPH gatherer agent 的大模型对话能力，通过浏览器自动化与 ChatGPT/Gemini/豆包 等 LLM 交互，用于：
- 向 LLM 询问物理概念和数学推导
- 上传本地文件让 LLM 审查分析结果
- 搜索最新的学术信息

## 安装状态
- [x] Playwright 已安装
- [x] Playwright Chromium 浏览器已安装
- [x] llm-gatherer 包结构已创建（config.py, browser.py, llm_interface.py, __main__.py）
- [x] RALPH 集成接口 llm_ask.py 已创建
- [x] 所有 import 测试通过

## 待办事项

### P0: 首次登录
- [ ] `cd /Users/a1-6/Desktop/workspace/scripts/llm-gatherer && python3 -m llm_gatherer login chatgpt`
- [ ] 在打开的浏览器中完成 Google/ChatGPT 登录
- [ ] 认证状态自动保存到 `~/.ralph/llm-state/chatgpt.state.json`

### P0: 验证对话能力
- [ ] `python3 -m llm_gatherer ask chatgpt "什么是引力波各向异性？"`
- [ ] 检查回复是否正确提取并保存到 llm_response.txt

### P1: 文件上传能力
- [ ] 实现 ChatGPTApi.ask_with_file() — 通过文件选择器上传
- [ ] 测试：`python3 -m llm_gatherer ask chatgpt "审查此文件" --file <path>`

### P2: 豆包/Kimi 支持
- [ ] 测试 DoubaoApi 和 KimiApi 的登录和提问流程
- [ ] 调整选择器以匹配最新 UI

## 使用示例

### 在 RALPH gatherer 中使用
```python
from llm_gatherer.llm_ask import ask_llm
result = ask_llm("chatgpt", "分析手征引力波对 ORF 的影响...")
```

### 直接命令行
```bash
cd /Users/a1-6/Desktop/workspace/scripts/llm-gatherer
python3 -m llm_gatherer ask gemini "解释 chi_orb 在镜面对称性下的行为"
```
