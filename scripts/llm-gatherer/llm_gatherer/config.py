"""
配置 — 支持的 LLM 服务和状态路径
"""
import os
from pathlib import Path

STATE_DIR = Path.home() / ".ralph" / "llm-state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

# 支持的 LLM 服务
SERVICES = {
    "chatgpt": {
        "name": "ChatGPT (OpenAI)",
        "url": "https://chatgpt.com",
        "storage_state": STATE_DIR / "chatgpt.state.json",
        # 检测是否已登录的 CSS 选择器
        "ready_selector": 'a[href*="/chat"]',
        # Auth cookie name — indicates API auth is available
        "auth_cookie": "oai-sc",
        # 登录页的选择器（可能因 Google 登录而不同）
        "login_selector": 'button[type="submit"], #gomen-signin-btn',
    },
    "gemini": {
        "name": "Google Gemini",
        "url": "https://gemini.google.com",
        "storage_state": STATE_DIR / "gemini.state.json",
        "ready_selector": 'textarea[name="message"], [aria-label*="message"]',
        "login_selector": 'a[href*="accounts.google.com"]',
    },
    "doubao": {
        "name": "豆包 (Doubao)",
        "url": "https://www.doubao.com",
        "storage_state": STATE_DIR / "doubao.state.json",
        "ready_selector": 'textarea[placeholder], #chat-input',
        "login_selector": 'a[href*="login"]',
    },
    "kimi": {
        "name": "Kimi (月之暗面)",
        "url": "https://kimi.moonshot.cn",
        "storage_state": STATE_DIR / "kimi.state.json",
        "ready_selector": 'textarea, [contenteditable="true"]',
        "login_selector": 'a[href*="login"], .login-btn',
    },
}

# 浏览器超时设置（秒）
LAUNCH_TIMEOUT = 120
POLL_INTERVAL = 1.0  # 轮询间隔（秒）
