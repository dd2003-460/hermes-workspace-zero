# 浏览器自动化 LLM 对话 — 全面方案研究

**时间**: 2026-07-10
**目标**: 控制已登录的 Chrome 浏览器与 ChatGPT/Gemini/Doubao 对话

---

## 方案对比（按推荐排序）

### 1. Tampermonkey 脚本注入 chatgpt-api (0 stars, 但有现成 Python 封装)
**仓库**: zsodur/chatgpt-api-by-browser-script (254 stars)
**检测风险**: 无（在页面上下文运行，完全等同于真人）

原理：在 ChatGPT 页面注入 Tampermonkey 脚本，脚本暴露 `window.chatgptWebAPI`，本地 Python 通过 `cdp_client` 或 Playwright CDP 调用它。

优势：
- 零自动化检测（脚本运行在页面上下文，不是框架级注入）
- 可以直接读取 DOM 中的回复内容（不需要视觉识别）
- 可以管理多个对话、获取对话历史
- 绕过 Cloudflare（因为脚本是页面的一部分）

实现方式：
```python
# 1. 在 ChatGPT 页面安装 Tampermonkey 脚本
# 2. 通过 CDP 连接 Chrome
# 3. 注入脚本调用 window.chatgptWebAPI.send_message("你的问题")
# 4. 轮询 window.chatgptWebAPI.get_latest_reply()
```

### 2. Chrome 扩展（nanobrowser, 13,446 stars）
**检测风险**: 无（Chrome 扩展有最高权限）
**优势**: 最成熟的浏览器自动化生态

原理：安装 Chrome 扩展，通过扩展消息 API 控制浏览器页面。

```
本地 Python ↔ Chrome Extension ↔ 实际页面
(决策层)      (控制层)           (交互层)
```

nanobrowser 已经内置了：
- 页面元素定位和交互
- 截图 + 视觉分析
- 多标签页管理
- 异步事件驱动

### 3. 原始 CDP WebSocket（绕过 Playwright 框架指纹）
**检测风险**: 极低
**优势**: 最底层的控制方式，无框架痕迹

Playwright 本身有一些自动化指纹（如 `Page` 对象的结构），直接使用 WebSocket 连接 CDP 端点可以完全绕过：

```python
import asyncio
import websockets

# 直接连接 CDP
ws_url = "ws://127.0.0.1:9222/devtools/page/ABC123..."
async with websockets.connect(ws_url) as ws:
    # 导航
    await ws.send(json.dumps({
        "id": 1, "method": "Page.navigate",
        "params": {"url": "https://chatgpt.com"}
    }))
    # 执行 JS
    result = await ws.send(json.dumps({
        "id": 2, "method": "Runtime.evaluate",
        "params": {"expression": "document.body.innerText"}
    }))
```

### 4. 无障碍树 (Accessibility Tree)
**检测风险**: 低
**优势**: 最可靠的选择交互方式

Chrome 的无障碍树暴露了所有可交互元素：角色、名称、状态、位置。

```python
# browsegrab 项目的方法
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=CHROME_DIR)
    page = ctx.pages[0]

    # 获取无障碍树快照
    axtree = page.accessibility.snapshot()
    # axtree 包含所有可交互元素及其属性
    for node in axtree.get('children', []):
        print(node.get('name'), node.get('role'))
```

### 5. 截图 + 视觉 LLM（你想要的"视觉识别对话"）
**检测风险**: 极低
**劣势**: 成本高（~$0.01/次）、速度慢（~3-5s/次）

原理：截图 → 发送给 GPT-4V / Claude Vision → 获得文字内容和点击坐标。

```python
# 1. 截图
screenshot = page.screenshot()
# 2. 发送给视觉 LLM
response = openai.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "读取页面上的所有文字内容"},
            {"type": "image_url", {"image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}}}
        ]
    }]
)
reply = response.choices[0].message.content
```

### 6. veilbrowser（9 stars）
**检测风险**: 无
**优势**: 专为绕过 bot 检测设计

veilbrowser 不使用 Playwright/Puppeteer，而是直接用原始 CDP 连接真实 Chrome：
- 通过 sannysoft 57/57 检测
- 绕过 Cloudflare
- 完整的 Chrome 功能

---

## 推荐实施路径

### 路径 A: 最快实现 ChatGPT 自动化
1. **Tampermonkey 脚本注入** — 零检测风险
2. 安装 [chatgpt-api-by-browser-script](https://github.com/zsodur/chatgpt-api-by-browser-script)
3. 通过 CDP 或 Playwright 调用 `window.chatgptWebAPI`

### 路径 B: 通用多平台方案
1. **CDP + 无障碍树** — 兼容 ChatGPT/Gemini/Doubao
2. 使用 [browsegrab](https://github.com/ArkNill/browsegrab) 作为参考
3. 结合截图 + 视觉 LLM 处理动态内容

### 路径 C: 视觉识别方案
1. **截图 + GPT-4V/Claude Vision** — 完全黑盒，不需要了解页面结构
2. 使用 [ChromePilot](https://github.com/Varun-Patkar/ChromePilot) 作为参考

---

## 关键发现

1. **ChatGPT 的自动化检测核心不是 `navigator.webdriver`，而是页面加载行为** — 即使禁用了 `navigator.webdriver`，Playwright 创建的页面加载模式仍然会被检测到。

2. **Tampermonkey 脚本注入是唯一完全绕过检测的方式** — 因为脚本运行在页面上下文中，任何 ChatGPT 的 JS 检测都无法区分脚本操作和真人操作。

3. **视觉识别（截图 + LLM）不是最优解** — 对于纯文本聊天场景，DOM 读取或无障碍树远比视觉识别准确、快速、便宜。视觉识别更适合需要理解复杂 UI 布局的场景。

4. **CDP 直接连接 > Playwright** — Playwright 在 CDP 之上有一些抽象层，这些抽象层可能被检测到。直接 WebSocket 连接 CDP 端点最隐蔽。

---

## 参考资源

| 名称 | Stars | 用途 |
|------|-------|------|
| nanobrowser | 13,446 | Chrome 扩展浏览器自动化 |
| chatgpt-api-by-browser-script | 254 | Tampermonkey ChatGPT API |
| browsegrab | 8 | 无障碍树 + 本地 LLM |
| ChromePilot | 6 | 截图 + 无障碍树双引擎 |
| veilbrowser | 9 | 绕过 bot 检测 |
| browser-use | - | AI Agent 浏览器自动化框架 |
