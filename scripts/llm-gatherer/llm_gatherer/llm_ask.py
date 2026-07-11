#!/usr/bin/env python3
"""
RALPH integration — programmatic LLM Gatherer calls.

Usage:
    from llm_gatherer.llm_ask import ask_llm
    result = ask_llm("chatgpt", "what is chiral gravitational wave coherence??")

Supported services: chatgpt, gemini, doubao, kimi
"""

import sys
import time
from pathlib import Path

from . import browser, config
from .llm_interface import get_llm_api


# Cache browser context and page, avoid restarting browser on every call
_context_cache = {
    "context": None, "browser": None, "pw": None,
    "page": None, "service": None,
}


def _get_context(service_name: str, service_cfg: dict):
    """Get or rebuild browser context (with login check)"""
    if (_context_cache["context"] is not None
            and _context_cache["service"] == service_name
            and _context_cache["page"] is not None):
        return _context_cache["page"]

    # Cleanup old resources
    if _context_cache["pw"] is not None:
        try:
            _context_cache["browser"].close()
            _context_cache["pw"].stop()
        except Exception:
            pass

    ctx, browser_obj, pw = browser.create_context()
    _context_cache["context"] = ctx
    _context_cache["browser"] = browser_obj
    _context_cache["pw"] = pw
    _context_cache["service"] = service_name

    # Navigate and check login
    page = ctx.new_page()
    page.goto(service_cfg["url"])
    page.wait_for_load_state("networkidle")

    if not browser.check_logged_in(page, service_cfg):
        print(f"[llm-ask] Login not detected for {service_cfg['name']}, attempting login...")
        success, login_page = browser.handle_login(ctx, service_cfg)
        if not success:
            raise RuntimeError(f"[llm-ask] Login failed: {service_cfg['name']}")
        page = login_page

    _context_cache["page"] = page
    return page


def ask_llm(service_name: str, question: str, file_path: str = None, timeout: int = 60) -> str:
    """
    Send a question to an LLM and get the reply.

    Args:
        service_name: "chatgpt", "gemini", "doubao", or "kimi"
        question: Question text
        file_path: Optional attached file
        timeout: Timeout waiting for reply (seconds)

    Returns:
        LLM reply text

    Raises:
        ValueError: Unsupported service
        RuntimeError: Login failure or browser error
    """
    if service_name not in config.SERVICES:
        raise ValueError(f"Unsupported service: {service_name}, supported: {list(config.SERVICES.keys())}")

    service_cfg = config.SERVICES[service_name]
    page = _get_context(service_name, service_cfg)

    api = get_llm_api(service_name, page.context, service_cfg)
    api.page = page  # reuse the existing page

    try:
        if file_path:
            return api.ask_with_file(question, file_path, timeout=timeout)
        return api.ask(question, timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"[llm-ask] Ask failed: {e}")


def close():
    """Cleanup resources"""
    if _context_cache["pw"] is not None:
        try:
            _context_cache["browser"].close()
            _context_cache["pw"].stop()
        except Exception:
            pass
        _context_cache["context"] = None
        _context_cache["browser"] = None
        _context_cache["page"] = None
        _context_cache["pw"] = None
        _context_cache["service"] = None


# CLI mode
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 llm_ask.py <service> <question> [--file <path>]")
        sys.exit(1)

    service = sys.argv[1]
    question = " ".join(sys.argv[2:-1] if "--file" in sys.argv else sys.argv[2:])

    file_path = None
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            file_path = sys.argv[idx + 1]

    result = ask_llm(service, question, file_path=file_path)
    print(result)
    close()
