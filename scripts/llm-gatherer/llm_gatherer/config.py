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
        "chat_url": "https://chatgpt.com/c/00000000-0000-4000-8000-000000000000",
        "storage_state": STATE_DIR / "chatgpt.state.json",
        "ready_selector": 'a[href*="/chat"]',
        "auth_cookie": "oai-sc",
        "login_selector": 'button[type="submit"], #gomen-signin-btn',
    },
    "gemini": {
        "name": "Google Gemini",
        "url": "https://gemini.google.com",
        "chat_url": "https://gemini.google.com",  # Gemini uses same URL for chat
        "storage_state": STATE_DIR / "gemini.state.json",
        "ready_selector": 'textarea[name="message"], [aria-label*="message"]',
        "login_selector": 'a[href*="accounts.google.com"]',
        "skip_login_wait": True,  # Landing page → auto-redirects to chat if logged in
    },
    "doubao": {
        "name": "豆包 (Doubao)",
        "url": "https://www.doubao.com",
        "chat_url": "https://www.doubao.com/chat/",
        "storage_state": STATE_DIR / "doubao.state.json",
        "ready_selector": 'textarea[placeholder], #chat-input',
        "login_selector": 'a[href*="login"]',
    },
    "kimi": {
        "name": "Kimi (月之暗面)",
        "url": "https://kimi.moonshot.cn",
        "chat_url": "https://kimi.moonshot.cn",
        "storage_state": STATE_DIR / "kimi.state.json",
        "ready_selector": 'textarea, [contenteditable="true"]',
        "login_selector": 'a[href*="login"], .login-btn',
    },
    "arena": {
        "name": "arena.ai (Agent)",
        "url": "https://arena.ai/agent",
        "chat_url": "https://arena.ai/agent",
        "storage_state": STATE_DIR / "arena.state.json",
        "ready_selector": 'textarea, [contenteditable="true"], [class*="chat-input"], [class*="message-input"]',
        "login_selector": 'a[href*="login"], button[class*="login"], button[class*="sign"]',
    },
    "bigmodel": {
        "name": "bigmodel.cn (GLM-5.2)",
        "url": "https://bigmodel.cn",
        "chat_url": "https://bigmodel.cn/personal/1066062442054835201",
        "storage_state": STATE_DIR / "bigmodel.state.json",
        "ready_selector": 'textarea, [contenteditable="true"], [class*="chat-input"], [class*="message-input"]',
        "login_selector": 'a[href*="login"], button[class*="login"], button[class*="sign"]',
    },
}

# 浏览器超时设置（秒）
LAUNCH_TIMEOUT = 120
POLL_INTERVAL = 1.0  # 轮询间隔（秒）
