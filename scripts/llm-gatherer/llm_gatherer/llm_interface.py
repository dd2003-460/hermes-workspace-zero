"""
LLM 对话接口基类 + 实现
"""
import time
import os
from pathlib import Path
from playwright.sync_api import BrowserContext, Page
from llm_gatherer import browser, config


class LLMApi:
    """LLM 对话基类"""

    def __init__(self, context: BrowserContext, service_cfg: dict = None):
        self.context = context
        self.page = None
        self.service_cfg = service_cfg

    def ensure_page(self):
        """确保有活跃页面"""
        if self.page is None:
            self.page = self.context.new_page()
            if self.service_cfg and "url" in self.service_cfg:
                self.page.goto(self.service_cfg["url"])
                self.page.wait_for_load_state("networkidle")

    def ask(self, question: str, timeout=60) -> str:
        """发送问题并获取回复"""
        raise NotImplementedError

    def ask_with_file(self, question: str, file_path: str, timeout=90) -> str:
        """发送问题并附加文件"""
        raise NotImplementedError


class ChatGPTApi(LLMApi):
    """ChatGPT 接口 — 通过 ChatGPT 网页版"""

    def _wait_for_cloudflare(self, timeout=30):
        """Wait for Cloudflare verification to complete, or detect if stuck."""
        cf_detect_selectors = [
            'iframe[src*="challenges.cloudflare.com"]',
            'div[class*="cf-security"]',
            'div[class*="cf-hcaptcha"]',
        ]
        for attempt in range(timeout):
            # First check: is the ChatGPT UI ready?
            # Look for textarea with the ChatGPT placeholder
            try:
                tas = self.page.query_selector_all('textarea')
                for ta in tas:
                    try:
                        if ta.is_visible():
                            placeholder = ta.get_attribute('placeholder') or ''
                            if placeholder and len(placeholder) > 2:
                                return True
                    except Exception:
                        pass
                # If textarea has no placeholder, check if it's in the sidebar
                # (new ChatGPT UI has the textarea in the sidebar)
                sidebar = self.page.query_selector('#stage-sidebar-tiny-bar, .stage-sidebar-pure-surface')
                if sidebar:
                    return True
            except Exception:
                pass

            # Second check: are we stuck on Cloudflare?
            on_cf_page = False
            for sel in cf_detect_selectors:
                try:
                    els = self.page.query_selector_all(sel)
                    if els and any(e.is_visible() for e in els):
                        on_cf_page = True
                        break
                except Exception:
                    pass

            if on_cf_page:
                print(f"[llm-gatherer] Cloudflare challenge detected, waiting for verification...")
                try:
                    # Wait up to 20s for the Cloudflare challenge to auto-solve
                    self.page.wait_for_selector('iframe[src*="challenges.cloudflare.com"]', timeout=20000, state="hidden")
                    time.sleep(2)
                    # After Cloudflare clears, navigate to ChatGPT
                    self.page.goto(self.service_cfg["url"], wait_until="networkidle", timeout=30000)
                    time.sleep(3)
                    return True
                except Exception as e:
                    print(f"[llm-gatherer] Cloudflare challenge did not auto-solve ({e})")
                    print(f"[llm-gatherer] Please verify in the browser window")
                    return True
            time.sleep(1)
        return False

    def _find_input_element(self):
        """查找输入框"""
        # ChatGPT new UI: contenteditable div is the actual input (textarea is hidden)
        selectors = [
            '[contenteditable="true"]',
            'textarea[data-testid="conversation-form textarea"]',
            'textarea[placeholder]',
            '#prompt-textarea',
        ]
        for sel in selectors:
            try:
                el = self.page.wait_for_selector(sel, timeout=3000, state="visible")
                if el and el.is_visible():
                    return el
            except Exception:
                continue
        return None

    def _is_logged_in(self) -> bool:
        """Check if the user is actually logged in to ChatGPT (not on login gate)."""
        # Check via cookies (most reliable for OpenAI)
        try:
            cookies = self.page.context.cookies()
            has_cookie = any(c["name"] == "oai-sc" for c in cookies)
            cookie_details = [c for c in cookies if c["name"] == "oai-sc"]
            print(f"[llm-gatherer] [DEBUG] has_cookie={has_cookie} cookie_details={cookie_details[:1]}")
        except Exception as e:
            has_cookie = False
            cookie_details = []
            print(f"[llm-gatherer] [DEBUG] cookie check failed: {e}")

        # UI-based check: logged-in page has contenteditable input with placeholder
        # Logged-out gate has "Login" or "Sign in" as prominent content
        try:
            page_text = self.page.query_selector('body').inner_text() if self.page.query_selector('body') else ""
            has_login_gate = any(kw in page_text for kw in ["登录以获取", "Log in", "Sign in", "请登录"])
            has_input_placeholder = "有问题，尽管问" in page_text or "Ask me anything" in page_text
            print(f"[llm-gatherer] [DEBUG] page_text[:200]={page_text[:200]!r}")
        except Exception as e:
            has_login_gate = True
            has_input_placeholder = False
            print(f"[llm-gatherer] [DEBUG] page_text fetch failed: {e}")

        print(f"[llm-gatherer] [DEBUG] has_login_gate={has_login_gate} has_input_placeholder={has_input_placeholder}")

        # If cookie exists AND page doesn't show login gate, consider logged in
        if has_cookie and not has_login_gate:
            return True
        # If page shows the main input placeholder, user is logged in
        if has_input_placeholder:
            return True
        return False

    def ask(self, question: str, timeout=60) -> str:
        self.ensure_page()

        # Wait for Cloudflare verification (if any)
        self._wait_for_cloudflare(timeout=30)

        if not self._is_logged_in():
            # Check if it's a Cloudflare page that needs manual verification
            title = self.page.title()
            if "Cloudflare" in title or "Verify you are human" in self.page.content():
                print(f"[llm-gatherer] Cloudflare verification needed. Please complete it in the browser window.")
                time.sleep(30)
                if not self._is_logged_in():
                    return "[错误] Cloudflare 验证未通过，请手动完成验证后重试"
            else:
                print(f"[llm-gatherer] Not logged in to ChatGPT. Please log in in the browser window.")
                time.sleep(30)
                if not self._is_logged_in():
                    return "[错误] 未登录 ChatGPT，请手动登录后重试"

        input_el = self._find_input_element()
        if not input_el:
            return "[错误] 未找到 ChatGPT 输入框，可能需要重新登录"

        # 填入问题
        input_el.click()
        time.sleep(0.3)
        # contenteditable: use evaluate to set innerText and dispatch input event
        is_contenteditable = input_el.evaluate("el => el.contentEditable === 'true'")
        if is_contenteditable:
            input_el.evaluate("el => el.innerText = ''")
            input_el.evaluate("""q => {
                // In evaluate on ElementHandle, this is the element
                this.innerText = q;
                this.dispatchEvent(new Event('input', {bubbles: true}));
                this.dispatchEvent(new InputEvent('beforeinput', {bubbles: true}));
                this.focus();
            }""", question)
        else:
            input_el.fill(question)
        time.sleep(1)

        # 发送（点击发送按钮或按 Enter）
        send_selectors = [
            'button[type="submit"]',
            '[aria-label="Send"]',
            '#send-button',
        ]
        sent = False
        for sel in send_selectors:
            try:
                btn = self.page.wait_for_selector(sel, timeout=2000)
                if btn and btn.is_visible():
                    btn.click()
                    sent = True
                    break
            except Exception:
                continue

        if not sent:
            self.page.keyboard.press("Enter")

        # 等待回复
        print(f"[llm-gatherer] 等待 ChatGPT 回复（{timeout} 秒）...")
        time.sleep(min(timeout, 30))

        # 提取回复内容
        return self._extract_latest_reply()

    def _extract_latest_reply(self) -> str:
        """Extract the latest AI reply from the ChatGPT conversation."""
        # Debug: dump page state
        try:
            _title = self.page.title()
            _url = self.page.url
            _body_text = (self.page.query_selector('body').inner_text()[:500] if self.page.query_selector('body') else '(no body)')
            print(f"[llm-gatherer] [DEBUG] title={_title!r} url={_url!r}")
            print(f"[llm-gatherer] [DEBUG] body[:500]={_body_text!r}")
        except Exception as _e:
            print(f"[llm-gatherer] [DEBUG] error dumping state: {_e}")

        # Strategy: find all top-level message containers, skip empty ones
        # ChatGPT new UI uses <div class="..."> wrappers for each message pair
        # Inside each wrapper: user-message + assistant-markdown
        selectors = [
            # New ChatGPT UI: conversation turn wrappers
            '[data-testid="conversation-cell"]',
            # Legacy selectors
            '[data-testid="conversation-turn-0"]',
            'div[data-message-author-role="assistant"]',
            # Generic: assistant message blocks
            'div[class*="prose"]',
            'div[class*="markdown"]',
            'div[class*="message-body"], div[class*="chat-message"], div[class*="assistant-message"]',
        ]
        for sel in selectors:
            try:
                elements = self.page.query_selector_all(sel)
                for el in reversed(elements):
                    content = el.inner_text().strip()
                    if len(content) > 10:
                        # Exclude any content that's just user-like short prompts
                        return content
            except Exception:
                continue

        # Fallback: try to find any element with a large text block after the textarea
        try:
            body = self.page.query_selector('body')
            if body:
                text = body.inner_text()
                # Split by the user's last message (approximate) and take the last part
                # This is fragile but better than nothing
                if "有问题，尽管问" in text:
                    return "[警告] 回复尚未渲染完成，请检查浏览器窗口"
                if len(text) > 50:
                    return text[-1000:]  # Last 1000 chars
        except Exception:
            pass

        return "[警告] 未能自动提取回复，请检查浏览器窗口"


class GeminiApi(LLMApi):
    """Google Gemini 接口"""

    def _find_input_element(self):
        selectors = [
            'textarea[name="message"]',
            '[aria-label*="message"]',
            '[aria-label*="输入"]',
            '#prompt-area',
        ]
        for sel in selectors:
            try:
                el = self.page.wait_for_selector(sel, timeout=3000, state="visible")
                if el:
                    return el
            except Exception:
                continue
        return None

    def ask(self, question: str, timeout=60) -> str:
        self.ensure_page()
        input_el = self._find_input_element()
        if not input_el:
            return "[错误] 未找到 Gemini 输入框，可能需要重新登录"

        input_el.click()
        input_el.fill(question)
        time.sleep(1)

        # 发送
        send_selectors = [
            'button[aria-label*="Send"], button[aria-label*="发送"]',
            'button[type="submit"]',
        ]
        sent = False
        for sel in send_selectors:
            try:
                btn = self.page.wait_for_selector(sel, timeout=2000)
                if btn and btn.is_visible():
                    btn.click()
                    sent = True
                    break
            except Exception:
                continue

        if not sent:
            self.page.keyboard.press("Enter")

        print(f"[llm-gatherer] 等待 Gemini 回复（{timeout} 秒）...")
        time.sleep(min(timeout, 30))

        # Extract Gemini reply
        selectors = [
            '[data-testid="conversation-cell"]',
            'div.js-output',
            'div.mdc-typography',
            'div[class*="gemini-response"], div[class*="answer"], div[class*="output"]',
            'div[class*="markdown"], div[class*="prose"]',
        ]
        for sel in selectors:
            try:
                elements = self.page.query_selector_all(sel)
                for el in reversed(elements):
                    content = el.inner_text().strip()
                    if len(content) > 10:
                        return content
            except Exception:
                continue
        return "[警告] 未能自动提取回复，请检查浏览器窗口"


class DoubaoApi(LLMApi):
    """豆包接口"""

    def _find_input_element(self):
        selectors = [
            'textarea[placeholder*="输入"], textarea[placeholder*="输入"]',
            '#chat-input',
            '[contenteditable="true"][data-v-*]',
        ]
        for sel in selectors:
            try:
                el = self.page.wait_for_selector(sel, timeout=3000, state="visible")
                if el:
                    return el
            except Exception:
                continue
        return None

    def ask(self, question: str, timeout=60) -> str:
        self.ensure_page()
        input_el = self._find_input_element()
        if not input_el:
            return "[错误] 未找到豆包输入框，可能需要重新登录"

        input_el.click()
        input_el.fill(question)
        time.sleep(1)

        send_selectors = [
            'button[type="submit"]',
            'button[class*="send"]',
        ]
        sent = False
        for sel in send_selectors:
            try:
                btn = self.page.wait_for_selector(sel, timeout=2000)
                if btn and btn.is_visible():
                    btn.click()
                    sent = True
                    break
            except Exception:
                continue

        if not sent:
            self.page.keyboard.press("Enter")

        print(f"[llm-gatherer] 等待豆包回复（{timeout} 秒）...")
        time.sleep(min(timeout, 30))

        return "[警告] 豆包回复提取待完善，请检查浏览器窗口"


# 服务到接口的映射
SERVICE_MAP = {
    "chatgpt": ChatGPTApi,
    "gemini": GeminiApi,
    "doubao": DoubaoApi,
}


def get_llm_api(service_name: str, context: BrowserContext, service_cfg: dict = None) -> LLMApi:
    """获取指定服务的 LLM 接口"""
    if service_name not in SERVICE_MAP:
        raise ValueError(f"不支持的服务: {service_name}，支持: {list(SERVICE_MAP.keys())}")
    return SERVICE_MAP[service_name](context, service_cfg)
