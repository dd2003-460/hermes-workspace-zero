# T15: Edge 浏览器已登录账户与可用网页 LLM Review 服务调研

## 一、Edge 浏览器已登录账户

需要本地检查 Edge 浏览器的登录状态（Cookie/会话）。Playwright 可以通过 `--user-data-dir` 复用 Edge 的已登录会话：

```bash
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(
        args=['--channel=edge'],
        headless=False
    )
    # 复用 Edge 的用户数据目录
    browser = p.chromium.launch_persistent_context('/tmp/edge-profile')
"
```

Edge 的 user data dir 在 macOS 上位于: `~/Library/Application Support/Microsoft/Edge/`

## 二、可用的网页 LLM Review 服务

### 1. Claude Web (claude.ai)
- **文件上传**: 支持 PDF、TXT、Markdown、代码文件等
- **文件大小**: 最高 512KB 上传 (免费用户), Pro 用户更高
- **上下文窗口**: 200K tokens
- **优势**: 对 PDF 渲染质量好，LaTeX 公式渲染良好，支持多文件对比
- **缺点**: 需要登录账户，免费用户有消息限制
- **URL**: https://claude.ai

### 2. ChatGPT (chatgpt.com)
- **文件上传**: 支持 PDF、DOCX、TXT、CSV、代码文件等
- **上下文窗口**: 128K tokens
- **优势**: GPT-4o 支持详细分析，支持代码执行 (Code Interpreter)
- **缺点**: 需要 Plus/Pro 订阅
- **URL**: https://chatgpt.com

### 3. Google Gemini
- **文件上传**: 支持 PDF (API 级别支持，Web 界面 P1qjVc 标志显示为关闭)
- **模型**: gemini-2.0-flash, gemini-2.5-flash, gemini-3-pro
- **优势**: 免费用户可用，Google Docs 集成好
- **缺点**: Web 界面 PDF 上传功能可能关闭
- **URL**: https://gemini.google.com

### 4. Google AI Studio
- **文件上传**: API 支持文件上传
- **模型**: Gemini 系列
- **优势**: 免费 API key (API key 在 https://aistudio.google.com/apikey)
- **缺点**: 需要通过 API 使用，无 Web UI 直接上传
- **URL**: https://ai.google.dev

### 5. Microsoft Copilot
- **文件上传**: 有限支持
- **模型**: GPT-4 级别
- **优势**: 免费可用
- **缺点**: 文件上传功能有限
- **URL**: https://copilot.microsoft.com

### 6. Grok (x.ai)
- **文件上传**: 部分支持
- **模型**: Grok 系列
- **URL**: https://grok.com

## 三、推荐方案

### 方案 A: Claude Web (推荐)
最好的学术文档审查体验，LaTeX 公式渲染质量最好，上下文窗口最大。

实现方式:
1. Edge 浏览器登录 Claude 账户
2. Playwright 复用 Edge 的会话 (via persistent context)
3. 自动化上传文件到 claude.ai 并获取审查结果

### 方案 B: API 直接调用 (无需浏览器)
对已有的 `browser-review.js` 和 `llm-review-pipeline.py` 已支持 API 调用。
Claude Pro/Plus 用户可以直接使用 `@anthropic-ai/sdk`。

### 方案 C: Gemini API
免费 API key，支持文件上传和 PDF 分析。

## 四、Edge 浏览器会话复用

```python
from playwright.sync_api import sync_playwright
import os

# macOS Edge user data dir
edge_profile = os.path.expanduser("~/Library/Application Support/Microsoft/Edge/")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        edge_profile,
        headless=False,
        channel='edge'
    )
    page = context.new_page()
    page.goto('https://claude.ai')
    # 如果已登录，直接使用会话
    page.screenshot('claude-preview.png')
    context.close()
```

## 五、T18 实现状态

T18 已实现，见 `tools/web-llm-review.js`。

### T18 功能
1. 自动上传 PDF 到 claude.ai 或 chatgpt.com
2. 复用 Edge 浏览器已登录会话 (persistent context)
3. 发送自定义审查 prompt
4. 自动等待分析完成并提取审查结果
5. 会话管理 (list/status/result/logout)

### 使用
```bash
node tools/web-llm-review.js upload paper.pdf --service claude --prompt "review this paper"
node tools/web-llm-review.js list          # 查看所有会话
node tools/web-llm-review.js result <id>   # 查看审查结果
```

### 技术细节
- 首次运行需手动登录 (脚本会等待)
- 后续运行自动复用 Edge 会话
- 支持 claude.ai (推荐) 和 chatgpt.com

## 六、T18 集成建议 (历史, 已被实现)

T18 (上传论文到网页 LLM) 可以直接复用 Edge 浏览器会话来实现：

1. **自动化流程**:
   - Playwright 复用 Edge 已登录会话
   - 导航到 claude.ai 或 chatgpt.com
   - 点击文件上传按钮，选择 PDF
   - 等待分析完成
   - 抓取审查结果文本

2. **错误处理**:
   - 处理登录过期
   - 处理文件大小限制
   - 处理网络超时

3. **安全措施**:
   - 不上传敏感/未发表的论文内容
   - 本地 API 优先于网页上传
