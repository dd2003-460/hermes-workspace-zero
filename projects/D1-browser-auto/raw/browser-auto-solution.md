# 浏览器自动化大模型对话方案

**来源**：AI 生成方案
**时间**：2026-07-10
**摘要**：通过 Playwright 持久化浏览器上下文，实现本地 AI 驱动的稳定多轮网页大模型对话

---

## 一、核心方案：持久化浏览器上下文

Playwright 提供两种持久化登录状态的方式：

| 方法 | 适用场景 | 特点 |
|------|----------|------|
| `launchPersistentContext` | 手动登录一次，长期挂机/持续对话 | 直接指定用户数据目录，保存所有 Cookies、LocalStorage、扩展等，反自动化检测能力最强 |
| `storageState` 保存与加载 | 自动化流程中独立保存/注入登录状态 | 序列化为 JSON，可复用可分发，但部分站点检测更敏感 |

**推荐**：`launchPersistentContext`，等同于真实 Chrome 行为。

---

## 二、实现步骤（launchPersistentContext）

### Step 1：手动登录一次

```python
# step1_manual_login.py
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./my_browser_profile"  # 自定义持久化目录

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,                 # 必须可见，方便手动操作
        args=["--disable-blink-features=AutomationControlled"],
        slow_mo=100,                    # 放慢操作，更像真人
    )
    page = context.new_page()
    page.goto("https://chat.openai.com")

    print("请在浏览器中完成登录，完成后按回车继续...")
    input()  # 等待手动登录完成

    context.close()
    print("登录状态已保存。")
```

运行一次，手动扫码/输入密码登录，状态会永久保存到 `USER_DATA_DIR`。

### Step 2：后续自动化脚本复用登录状态

```python
# step2_ai_driven_chat.py
import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./my_browser_profile"

def ask_local_ai(prompt):
    """调用本地 AI（如 Ollama）生成下一步操作"""
    # response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    # return response['message']['content']
    return '输入"你好，请介绍一下你自己"并回车'

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,  # 调试阶段 False，稳定后可 True
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = context.new_page()
    page.goto("https://chat.openai.com")

    page.wait_for_selector("textarea[placeholder*='消息']", timeout=15000)

    for i in range(5):  # 5 轮对话示例
        last_response = page.locator("...").last.inner_text()

        ai_command = ask_local_ai(f"当前回复：{last_response}，接下来说什么？")

        input_box = page.locator("textarea[placeholder*='消息']")
        input_box.fill("这是本地 AI 驱动的回复：你好！")
        input_box.press("Enter")
        time.sleep(3)  # 等待回复生成

    context.close()
```

---

## 三、反自动化加固

### 1. 隐藏 Playwright 自动化特征

```python
args=[
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process",
],

page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

### 2. 模拟人类行为

- 打字速度随机化（`page.type` 的 `delay` 参数）
- 随机移动鼠标、滚动页面
- 避免机械定时器，加入随机等待 `time.sleep(random.uniform(1, 3))`

### 3. 处理会话过期

- 定时保活：每 1-2 小时自动刷新或发送简单对话
- 人工介入：检测到"登录已过期"/"验证码"时通知用户手动处理

### 4. 多账号管理

为每个账号分配独立 `user_data_dir`，如 `./profiles/account_1`。

---

## 四、备选方案：storageState

```python
# 保存状态
context = browser.new_context()
page = context.new_page()
# ... 手动或自动登录 ...
context.storage_state(path="state.json")

# 加载状态
context = browser.new_context(storage_state="state.json")
```

**注意**：部分网站会检测 WebDriver 注入的存储，`launchPersistentContext` 更稳定。

---

## 五、推荐架构

```
┌─────────────────────────────────────────────┐
│                  调度循环                      │
├─────────────────────────────────────────────┤
│  1. Playwright 提取页面状态                    │
│  2. 本地 AI 根据状态决策下一步操作              │
│  3. Playwright 执行操作                       │
│  4. 等待结果，回到步骤 1                       │
└─────────────────────────────────────────────┘
         ▲                    │
         │                    ▼
    ┌─────────┐          ┌─────────┐
    │本地 AI  │◄────────►│Playwright│
    │决策层    │          │执行层     │
    └─────────┘          └─────────┘
```

**扩展方向**：通用 AI Agent 操控浏览器应用，支持多网站、多任务。
