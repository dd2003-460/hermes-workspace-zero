"""
Browser management — Playwright wrapper.
Uses Chrome persistent context (user data dir) to share login state.
"""
import os
import subprocess
from playwright.sync_api import sync_playwright, BrowserContext

CHROME_USER_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome")


def _kill_chrome_processes():
    """Kill Chrome processes that may conflict with persistent context launch."""
    try:
        subprocess.run(["pkill", "-f", "Google Chrome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def create_context(headless: bool = False):
    """
    Create a Playwright persistent context using Chrome's user data directory.
    This shares the actual browser's cookies and login state — no storage_state persistence needed.

    Returns:
        (context, browser, pw) tuple
    """
    _kill_chrome_processes()
    pw = sync_playwright().start()
    context = pw.chromium.launch_persistent_context(
        user_data_dir=CHROME_USER_DIR,
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ],
        ignore_default_args=["--enable-automation"],
    )
    browser = context.browser
    return context, browser, pw


def save_auth_state(context: BrowserContext, service_name: str):
    """Save current context auth state to file (fallback)"""
    state_file = context.storage_state()
    from llm_gatherer import config
    state_path = config.STATE_DIR / f"{service_name}.state.json"
    import json
    state_path.write_text(json.dumps(state_file, indent=2))
    print(f"[llm-gatherer] Auth state saved to {state_path}")


def check_logged_in(page_or_ctx, service_cfg: dict) -> bool:
    """
    Check if the user is logged in.
    Returns True if a logged-in UI element is detected AND
    (if configured) the auth cookie is present in the context.
    """
    auth_cookie_name = service_cfg.get("auth_cookie")
    if auth_cookie_name:
        # Get cookies from either a Page or BrowserContext
        cookies = (page_or_ctx.context if hasattr(page_or_ctx, "context")
                   else page_or_ctx).cookies()
        if not any(c["name"] == auth_cookie_name for c in cookies):
            return False
    try:
        element = page_or_ctx.wait_for_selector(
            service_cfg["ready_selector"],
            timeout=3000,
            state="visible",
        )
        return element is not None
    except Exception:
        return False


def handle_login(context: BrowserContext, service_cfg: dict, timeout=120):
    """
    Handle login flow. Opens a page and waits for user to log in.
    """
    page = context.new_page()
    page.goto(service_cfg["url"])
    page.wait_for_load_state("networkidle")

    if check_logged_in(page, service_cfg):
        print(f"[llm-gatherer] Login detected ({service_cfg['name']})")
        return True, page

    print(f"[llm-gatherer] Login not detected")
    print(f"[llm-gatherer] Please log in to {service_cfg['name']} in the browser")
    print(f"[llm-gatherer] Waiting {timeout}s...")

    try:
        page.wait_for_selector(
            service_cfg["ready_selector"],
            timeout=timeout * 1000,
            state="visible",
        )
        print(f"[llm-gatherer] Login successful")
        return True, page
    except Exception:
        print(f"[llm-gatherer] Login timeout ({timeout}s)")
        return False, None
