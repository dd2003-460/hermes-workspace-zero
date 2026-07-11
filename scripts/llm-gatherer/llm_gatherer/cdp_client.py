"""
CDP-based browser control - connects to the user's real Chrome window
via Chrome DevTools Protocol. Uses raw CDP WebSocket (no Playwright)
to interact with ChatGPT in existing tabs.

Usage:
    client = await create_cdp_client()
    page_info = find_chatgpt_page(client)
    state = await page_info.evaluate("() => window.location.href")
    await close_cdp_client(client)
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

CHROME_USER_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome")
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CDP_PORT = 9222
CDP_URL = f"http://127.0.0.1:{CDP_PORT}"


async def _cdp_post(ws_url, msg):
    """Send a JSON-RPC message via CDP WebSocket."""
    import websockets
    async with websockets.connect(ws_url) as ws:
        await ws.send(json.dumps(msg))
        resp = await asyncio.wait_for(ws.recv(), timeout=10)
        return json.loads(resp)


INJECT_API_JS = r"""
(function() {
    if (window.__chatgptAPI__) return;
    window.__chatgptAPI__ = {
        send(q) {
            // ProseMirror editor (div.contenteditable)
            var el = document.getElementById('prompt-textarea') || document.querySelector('.ProseMirror');
            if (!el) return {error:'no editor found'};

            // Clear existing content
            el.innerHTML = '';

            // Insert text as a paragraph (ProseMirror required format)
            var p = document.createElement('p');
            p.textContent = q;
            el.appendChild(p);

            // Ensure trailing break for ProseMirror
            if (!el.querySelector('.ProseMirror-trailingBreak')) {
                var br = document.createElement('br');
                br.className = 'ProseMirror-trailingBreak';
                el.appendChild(br);
            }

            // Dispatch input events for React/ProseMirror change detection
            el.focus();
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new InputEvent('input', {bubbles: true, inputType: 'insertText'}));

            // send() only sets text — use getSubmitButtonRect() + CDP Input.dispatchMouseEvent
            // to actually send the message (btn.click() is a no-op on React UI)
            var btn = document.querySelector('button.composer-submit-button-color');
            if (btn) {
                var r = btn.getBoundingClientRect();
                return {status:'text_set', btnFound:true, btnRect:{left:r.left,top:r.top,width:r.width,height:r.height}};
            }
            return {status:'text_set', btnFound:false};
        },
        reply() {
            // Find last assistant message
            var els = document.querySelectorAll('[data-message-author-role="assistant"]');
            var lastEl = els[els.length - 1];
            if (lastEl) {
                // Check if streaming is still active (React state scan)
                var streaming = window.__chatgptAPI__.checkStreaming();
                // First try DOM text
                var text = lastEl.innerText.trim();
                if (!text) {
                    // DOM render bug: React has data but innerText is empty
                    // Walk the React fiber tree to find the actual message content
                    var msgId = lastEl.getAttribute('data-message-id');
                    if (msgId) {
                        text = window.__chatgptAPI__.textFromFiber(lastEl, msgId);
                    }
                }
                // If still empty, try getting text from the last message element's
                // content area (the actual rendered text node)
                if (!text) {
                    var contentDivs = lastEl.querySelectorAll('div[class*="result"], div[class*="message"], div[role="article"]');
                    for (var ci = 0; ci < contentDivs.length; ci++) {
                        var ct = contentDivs[ci].innerText.trim();
                        if (ct.length > text.length) {
                            text = ct;
                        }
                    }
                }
                return {text: text, textLen: text.length, streaming: streaming};
            }
            return {text: '', textLen: 0, streaming: false, noAssistant: true};
        },
        checkStreaming() {
            // Scan React state tree for any isActivelyStreaming flag
            var rootEls = document.querySelectorAll('[data-reactroot]');
            for (var ri = 0; ri < rootEls.length; ri++) {
                var keys = Object.keys(rootEls[ri]);
                for (var ki = 0; ki < keys.length; ki++) {
                    if (keys[ki].indexOf('__react') === 0) {
                        if (window.__chatgptAPI__.findStreaming(rootEls[ri][keys[ki]])) {
                            return true;
                        }
                    }
                }
            }
            // Fallback: check DOM for status/aria elements with streaming indicators
            var statusEls = document.querySelectorAll('[role="status"]');
            for (var i = 0; i < statusEls.length; i++) {
                if (statusEls[i].innerText && statusEls[i].innerText.trim().length > 0) {
                    return true;
                }
            }
            // Check for thinking indicators: result-thinking divs with empty <p> (still loading)
            var thinkingEls = document.querySelectorAll('div.result-thinking');
            for (var i = 0; i < thinkingEls.length; i++) {
                var p = thinkingEls[i].querySelector('p');
                if (p && !p.textContent.trim()) {
                    // Empty thinking div = still thinking
                    return true;
                }
            }
            // Check for typing cursor indicators on assistant messages
            var assistantMsgs = document.querySelectorAll('[data-message-author-role="assistant"]');
            for (var i = 0; i < assistantMsgs.length; i++) {
                var msg = assistantMsgs[i];
                // Check for empty result containers or blinking cursor
                var emptyResult = msg.querySelectorAll('div.result-thinking p:not([class]):not([id])');
                if (emptyResult.length > 0) {
                    return true;
                }
                // Check for cursor/animation indicators
                var cursors = msg.querySelectorAll('[class*="cursor"], [class*="animate"], [class*="blink"]');
                if (cursors.length > 0) {
                    return true;
                }
            }
            return false;
        },
        findStreaming(obj) {
            if (!obj || typeof obj !== 'object') return false;
            if (obj.isActivelyStreaming === true) return true;
            var k;
            for (k in obj) {
                if (k === 'memoizedProps' || k === 'pendingProps' || k === 'children') {
                    if (window.__chatgptAPI__.findStreaming(obj[k])) return true;
                }
            }
            return false;
        },
        textFromFiber(node, msgId) {
            if (!node || typeof node !== 'object') return '';
            // Search in memoizedProps and pendingProps
            var propsToCheck = [node.memoizedProps, node.pendingProps, node.props];
            var pi;
            for (pi = 0; pi < propsToCheck.length; pi++) {
                var p = propsToCheck[pi];
                if (p && typeof p === 'object') {
                    if (p.message && p.message.id === msgId && p.message.content && p.message.content.parts) {
                        return p.message.content.parts.join('');
                    }
                }
            }
            // Search in children
            var children = [node.memoizedProps, node.pendingProps, node.props];
            var ci;
            for (ci = 0; ci < children.length; ci++) {
                var c = children[ci];
                if (c && typeof c === 'object') {
                    var ck;
                    for (ck in c) {
                        var v = c[ck];
                        if (v && typeof v === 'object') {
                            if (Array.isArray(v)) {
                                var vi;
                                for (vi = 0; vi < v.length; vi++) {
                                    if (typeof v[vi] === 'object') {
                                        var found = window.__chatgptAPI__.textFromFiber(v[vi], msgId);
                                        if (found) return found;
                                    }
                                }
                            } else {
                                var found = window.__chatgptAPI__.textFromFiber(v, msgId);
                                if (found) return found;
                            }
                        }
                    }
                }
            }
            // Search sibling and parent refs
            if (node.return) {
                return window.__chatgptAPI__.textFromFiber(node.return, msgId);
            }
            return '';
        },
        state() {
            var btn = document.querySelector('button.composer-submit-button-color');
            return {
                url: location.href,
                title: document.title,
                hasEditor: !!document.getElementById('prompt-textarea'),
                cookieLength: document.cookie.length,
                buttonAriaLabel: btn ? btn.getAttribute('aria-label') : null,
                isStop: btn ? (btn.getAttribute('aria-label')||'').indexOf('停止') >= 0 : null
            };
        }
    };
})();
"""


def _cdp_available():
    try:
        import urllib.request
        resp = urllib.request.urlopen(f"{CDP_URL}/json", timeout=2)
        return len(resp.read()) > 0
    except Exception:
        return False


def _list_chrome_pages():
    try:
        import urllib.request
        resp = urllib.request.urlopen(f"{CDP_URL}/json", timeout=5)
        return json.loads(resp.read())
    except Exception as e:
        print(f"[llm-gatherer] [WARN] CDP /json failed: {e}")
        return []


def _launch_chrome_with_cdp():
    if _cdp_available():
        return True
    try:
        subprocess.Popen(
            [
                CHROME_PATH,
                f"--remote-debugging-port={CDP_PORT}",
                f"--user-data-dir={CHROME_USER_DIR}",
                "--disable-blink-features=AutomationControlled",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(15):
            if _cdp_available():
                print(f"[llm-gatherer] Chrome CDP ready on :{CDP_PORT}")
                return True
            time.sleep(1)
        print("[llm-gatherer] [WARN] Chrome CDP not ready after 15s")
        return False
    except Exception as e:
        print(f"[llm-gatherer] [WARN] Failed to launch Chrome: {e}")
        return False


async def _cdp_evaluate_raw(ws_url, expr, timeout=30):
    """
    Evaluate JS expression via CDP Runtime.evaluate with returnByValue.
    Uses strict message ID matching at page-level ws_url.
    Page-level ws_url merges auto-events + responses — must drain events.
    """
    import websockets

    msg_id = int(time.time() * 1000) % 1000000

    async with websockets.connect(ws_url) as ws:
        # Enable Runtime events first (catches exceptions, console logs)
        await ws.send(json.dumps({"id": msg_id, "method": "Runtime.enable"}))
        # Drain until we get the enable response
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=5)
            resp = json.loads(raw)
            if resp.get('id') == msg_id:
                break
            # Drain auto-events or other messages

        msg_id += 1

        # Send evaluate request
        await ws.send(json.dumps({
            "id": msg_id,
            "method": "Runtime.evaluate",
            "params": {"expression": expr, "returnByValue": True}
        }))

        # Drain until we get the evaluate response
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = max(0.01, deadline - time.monotonic())
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            except asyncio.TimeoutError:
                break
            resp = json.loads(raw)
            if resp.get('id') == msg_id:
                raw_result = resp.get('result', {})
                print(f"[CDP DEBUG] evaluate response result keys={list(raw_result.keys())} raw_result={json.dumps(raw_result)[:500]}")
                return raw_result
            # Auto-events (method) or unrelated messages — drain them
            if 'method' in resp:
                pass  # e.g., ExceptionEvent, LogEntryAdded
            elif 'result' in resp:
                pass  # unrelated response, drain

    return None


async def _cdp_create_target(url: str) -> str | None:
    """Create a new browser tab targeting url. Returns the new page_id or None."""
    import websockets
    # Get any existing page's ws_url to send the command
    pages = _list_chrome_pages()
    if not pages:
        return None
    ws_url = pages[0].get('webSocketDebuggerUrl')
    if not ws_url:
        return None

    async with websockets.connect(ws_url, close_timeout=5) as ws:
        # Create target
        msg = json.dumps({'id': 99, 'method': 'Target.createTarget', 'params': {'url': url}})
        await ws.send(msg)
        result = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        target_id = result.get('result', {}).get('targetId')
        return target_id


async def _cdp_find_new_chatgpt_page(timeout: int = 10) -> dict | None:
    """Wait for and return a new ChatGPT page that has loaded /new. Returns page_info dict or None."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        await asyncio.sleep(0.5)
        pages = _list_chrome_pages()
        for p in pages:
            pu = p.get('url', '')
            if 'chatgpt.com/new' in pu:
                return p
    return None


async def _cdp_navigate_and_wait_editor(ws_url: str, url: str, timeout: int = 15) -> bool:
    """Navigate a page to url and wait for the #prompt-textarea editor to appear. Returns True if editor ready."""
    deadline = time.monotonic() + timeout
    # Navigate
    await _cdp_evaluate_raw(ws_url, f"(function() {{ location.href = '{url}'; }})()")
    while time.monotonic() < deadline:
        await asyncio.sleep(0.5)
        result = await _cdp_evaluate_raw(ws_url,
            "(function() { return document.getElementById('prompt-textarea') ? 'found' : 'missing'; })()")
        if result and result.get('result', {}).get('value') == 'found':
            return True
    return False


async def create_cdp_client(timeout=30):
    """
    Check if Chrome with CDP is available.
    Returns a dict with 'pages' (list of page info) and 'cdp_available' flag.
    """
    if not _cdp_available():
        print("[llm-gatherer] No Chrome with CDP found. Launching Chrome with your profile...")
        if not _launch_chrome_with_cdp():
            print("[llm-gatherer] Try manually: open Chrome, then retry")
            return None

    pages = _list_chrome_pages()
    if not pages:
        print("[llm-gatherer] No pages found in Chrome CDP")
        return None

    print(f"[llm-gatherer] Chrome CDP available with {len(pages)} page(s):")
    for p in pages:
        print(f"  - {p.get('title','?')[:40]} | {p.get('url','?')[:60]}")

    return {"pages": pages}


def find_chatgpt_page(client):
    """Find ChatGPT page in the client's page list. Prefers conversation pages over /new."""
    if not client:
        return None
    # First pass: prefer conversation pages (/c/...) which have a proper message feed
    for p in client.get("pages", []):
        url = p.get("url", "")
        if "chatgpt.com" in url and "/c/" in url:
            print(f"[llm-gatherer] Found ChatGPT conversation tab: {url}")
            return p
    # Second pass: fall back to /new or any ChatGPT tab
    for p in client.get("pages", []):
        url = p.get("url", "")
        if "chatgpt.com" in url:
            print(f"[llm-gatherer] Found ChatGPT tab: {url}")
            return p
    return None


def find_page_by_domain(client, domain):
    """Find any page matching a domain. Returns page info dict or None."""
    if not client:
        return None
    for p in client.get("pages", []):
        url = p.get("url", "")
        if domain in url:
            print(f"[llm-gatherer] Found {domain} tab: {url}")
            return p
    return None


async def check_logged_in(page_info):
    """Check login status via evaluate."""
    ws_url = page_info["webSocketDebuggerUrl"]
    result = await _cdp_evaluate_raw(ws_url, """
(function() {
    var el = document.getElementById('prompt-textarea');
    if (!el) return {hasEditor: false, cookieLength: document.cookie.length, url: location.href, title: document.title};
    return {
        hasEditor: true,
        cookieLength: document.cookie.length,
        url: location.href,
        title: document.title
    };
})()""")
    if result is None:
        return False
    inner = result.get('result', {})
    if inner.get('subtype') == 'error':
        print(f"[llm-gatherer] Error: {inner.get('description', '')[:200]}")
        return False
    data = inner.get('value', {})
    print(f"[llm-gatherer] Page state: url={data.get('url','?')} title={data.get('title','?')} hasEditor={data.get('hasEditor')} cookieLength={data.get('cookieLength',0)}")
    # For ChatGPT pages: hasEditor may be false during navigation/loading;
    # accept logged-in if URL points to chatgpt.com with non-empty cookies
    url = data.get('url', '')
    if 'chatgpt.com' in url:
        # Logged in if cookies exist (auth via session cookie)
        if data.get('cookieLength', 0) > 0:
            print("[llm-gatherer] Logged in (chatgpt.com + cookies)")
            return True
        # Even without cookies, if it's chatgpt.com, allow proceed
        # (will be caught later if truly unauthenticated)
        print("[llm-gatherer] Appears to be ChatGPT page (proceeding)")
        return True
    return data.get('hasEditor', False) or data.get('cookieLength', 0) > 0


async def inject_api(page_info):
    """Inject the ChatGPT API into the page."""
    ws_url = page_info["webSocketDebuggerUrl"]
    result = await _cdp_evaluate_raw(ws_url, INJECT_API_JS)
    if result is None:
        print("[llm-gatherer] [WARN] API injection failed (timeout)")
        return False
    inner = result.get('result', {})
    if inner.get('subtype') == 'error':
        print(f"[llm-gatherer] [WARN] API injection JS error: {inner.get('description', '')[:200]}")
        return False
    # Check if injection succeeded
    check = await _cdp_evaluate_raw(ws_url, "typeof window.__chatgptAPI__")
    check_inner = (check or {}).get('result', {})
    if check_inner.get('value') == 'object':
        print("[llm-gatherer] ChatGPT API injected successfully")
        return True
    print("[llm-gatherer] [WARN] API injection may have failed")
    return False


async def _cdp_pixel_click(ws_url: str, x: float, y: float):
    """Send a CDP pixel-click (mousePressed + mouseReleased) at exact coordinates."""
    import websockets
    async with websockets.connect(ws_url, close_timeout=5) as ws:
        # mousePressed
        await ws.send(json.dumps({
            'id': 200,
            'method': 'Input.dispatchMouseEvent',
            'params': {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1}
        }))
        await asyncio.wait_for(ws.recv(), timeout=5)
        await asyncio.sleep(0.2)
        # mouseReleased
        await ws.send(json.dumps({
            'id': 201,
            'method': 'Input.dispatchMouseEvent',
            'params': {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1, 'modifiers': 0}
        }))
        await asyncio.wait_for(ws.recv(), timeout=5)


async def _cdp_do_pixel_click(ws_url: str, x: float, y: float):
    """Attempt pixel click with retry (3 attempts, 0.5s apart)."""
    for attempt in range(3):
        try:
            await _cdp_pixel_click(ws_url, x, y)
            return True
        except Exception as e:
            print(f"[llm-gatherer] [WARN] Pixel click attempt {attempt+1} failed: {e}")
            await asyncio.sleep(0.5)
    return False


async def _cdp_send_enter_key(ws_url: str):
    """Send Enter key via CDP Input.dispatchKeyEvent to submit message."""
    for attempt in range(3):
        try:
            import websockets
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # keydown
                await ws.send(json.dumps({
                    'id': 300,
                    'method': 'Input.dispatchKeyEvent',
                    'params': {'type': 'keyDown', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13, 'nativeVirtualKeyCode': 13}
                }))
                await asyncio.wait_for(ws.recv(), timeout=3)
                # keyup
                await ws.send(json.dumps({
                    'id': 301,
                    'method': 'Input.dispatchKeyEvent',
                    'params': {'type': 'keyUp', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13, 'nativeVirtualKeyCode': 13}
                }))
                await asyncio.wait_for(ws.recv(), timeout=3)
            return True
        except Exception as e:
            print(f"[llm-gatherer] [WARN] Enter key attempt {attempt+1} failed: {e}")
            await asyncio.sleep(0.3)
    return False


async def ask_chatgpt_cdp(page_info, question: str, timeout: int = 60) -> str:
    """Send question and wait for reply using CDP pixel click + DOM polling."""
    ws_url = page_info["webSocketDebuggerUrl"]
    page_url = page_info.get("url", "")

    if "/c/" not in page_url:
        # Not on a conversation page — create a new tab via CDP Target API
        print("[llm-gatherer] No conversation page available, creating new ChatGPT tab via CDP...")
        try:
            target_id = await _cdp_create_target('https://chatgpt.com')
            if target_id:
                print(f"[llm-gatherer] Created target {target_id}, waiting for page to load /new...")
                new_page = await _cdp_find_new_chatgpt_page(timeout=10)
                if new_page:
                    page_info = new_page
                    ws_url = page_info["webSocketDebuggerUrl"]
                    print(f"[llm-gatherer] New page found: {ws_url}")
                    editor_ready = await _cdp_navigate_and_wait_editor(ws_url, 'https://chatgpt.com/new', timeout=15)
                    if editor_ready:
                        print("[llm-gatherer] Editor ready on new page")
                    else:
                        print("[llm-gatherer] [WARN] Editor not ready, still trying to inject...")
                    await inject_api(page_info)
                else:
                    print("[llm-gatherer] [WARN] New target created but page not found in list")
            else:
                print("[llm-gatherer] [WARN] _cdp_create_target returned None")
        except Exception as e:
            print(f"[llm-gatherer] [WARN] Could not create new page: {e}")
            import traceback
            traceback.print_exc()

    # If on an existing conversation, navigate to /new for a fresh composer
    # (pixel click only works reliably on fresh pages, not existing conversations)
    if "/c/" in page_url and page_url != "https://chatgpt.com/new":
        print(f"[llm-gatherer] Existing conversation detected ({page_url}), navigating to /new...")
        nav_ok = await _cdp_navigate_and_wait_editor(ws_url, 'https://chatgpt.com/new', timeout=15)
        if nav_ok:
            print("[llm-gatherer] Editor ready on /new")
            page_url = "https://chatgpt.com/new"
        else:
            print("[llm-gatherer] [WARN] Editor not ready after navigation, trying to inject anyway...")

    # Inject API
    await inject_api(page_info)

    # Count assistant messages before sending (baseline)
    # On /new, this will be 0. Track it regardless for edge cases.
    count_before = await _cdp_evaluate_raw(ws_url,
        r"""(function() { return document.querySelectorAll('[data-message-author-role="assistant"]').length; })()""")
    before_count = 0
    if count_before:
        inner = count_before.get('result', {})
        before_count = inner.get('value', 0)

    # Escape single quotes in question for JS string
    esc_question = question.replace(chr(39), chr(92) + chr(39))
    send_expr = f"(function() {{ return window.__chatgptAPI__.send('{esc_question}'); }})()"

    send_result = await _cdp_evaluate_raw(ws_url, send_expr)
    if send_result is None:
        return "[错误] 发送失败（超时）"
    send_inner = send_result.get('result', {})
    if send_inner.get('subtype') == 'error':
        return f"[错误] {send_inner.get('description', '')[:200]}"

    data = send_inner.get('value', {})
    print(f"[llm-gatherer] Send result: {json.dumps(data, ensure_ascii=False)}")
    if data.get("error"):
        return f"[错误] {data['error']}"

    # send() sets text but does NOT click — try Enter key first, then fallbacks
    if data.get("btnFound"):
        # 1) Try keyboard Enter (most reliable — submit button has onKeyDown)
        print("[llm-gatherer] Trying Enter key to submit...")
        ok = await _cdp_send_enter_key(ws_url)
        if ok:
            print("[llm-gatherer] Enter key sent — waiting for response...")
        else:
            print("[llm-gatherer] Enter key failed, trying fallbacks...")
            rect = data.get("btnRect", {})
            if rect:
                cx = rect["left"] + rect["width"] / 2
                cy = rect["top"] + rect["height"] / 2
                print(f"[llm-gatherer] Trying pixel click at ({cx:.0f}, {cy:.0f})")
                ok2 = await _cdp_do_pixel_click(ws_url, cx, cy)
                if not ok2:
                    print("[llm-gatherer] [WARN] Pixel click failed, trying React fiber onClick injection...")
                    # Fallback 2: inject onClick directly into React fiber
                    await _cdp_evaluate_raw(ws_url, """
(function(){var b=document.querySelector('button.composer-submit-button-color');
if(!b)return;var el=b;while(el&&!el.__reactFiber){el=el.parentNode}
if(el&&el._return){var stateNode=el._return;while(stateNode){
if(stateNode.memoizedProps&&typeof stateNode.memoizedProps.onClick==='function'){
stateNode.memoizedProps.onClick();return'onClick_injected'}stateNode=stateNode._return}}
b.click()})()""")
            else:
                print("[llm-gatherer] [WARN] btnFound but no btnRect — doing direct click")
                await _cdp_evaluate_raw(ws_url, "document.querySelector('button.composer-submit-button-color')?.click()")
    else:
        print("[llm-gatherer] [WARN] Button not found — send may have failed")

    # Allow response to start streaming
    await asyncio.sleep(2)

    # Check if SPA navigation happened (URL changed to /c/uuid)
    current_url = ""
    url_result = await _cdp_evaluate_raw(ws_url, "(function() { return location.href; })()")
    if url_result:
        current_url = (url_result.get('result', {}) or {}).get('value', '')
    if "/c/" in current_url and current_url != page_url:
        print(f"[llm-gatherer] SPA navigated to {current_url}, re-injecting API...")
        await inject_api(page_info)
        ws_url = page_info["webSocketDebuggerUrl"]

    # Poll for reply — wait for new assistant message + text stability
    print(f"[llm-gatherer] Waiting for reply ({timeout}s), baseline assistant count: {before_count}")
    prev_text = ''
    stable_count = 0
    for i in range(timeout):
        await asyncio.sleep(1)
        # Check if new assistant message appeared
        count_now = await _cdp_evaluate_raw(ws_url,
            r"""(function() { return document.querySelectorAll('[data-message-author-role="assistant"]').length; })()""")
        cur_count = 0
        if count_now:
            c = count_now.get('result', {})
            cur_count = c.get('value', 0)

        if cur_count <= before_count:
            if i % 5 == 0:
                print(f"  ... waiting for new message ({i+1}s, assistant count: {cur_count}/{before_count})")
            continue

        # New message exists — get its text
        reply = await _cdp_evaluate_raw(ws_url, r"""(function(){
    var turns=document.querySelectorAll('[data-message-author-role="assistant"]');
    if(!turns||turns.length<=0)return'';
    var last=turns[turns.length-1];
    return last.textContent.trim().substr(0,5000);
})()""".lstrip("\n"))
        t = ''
        if reply:
            r = (reply or {}).get('result', {})
            if r.get('subtype') != 'error':
                t = r.get('value', '')
        if not t:
            if i % 10 == 0:
                print(f"  ... new message appeared, waiting for content ({i+1}s)...")
            continue

        # Text stability heuristic: if text stays the same for 3 consecutive polls,
        # streaming is complete. DOM-based streaming detection is unreliable on
        # ChatGPT's SPA (cursor/blink classes and empty result-thinking divs persist
        # after the response is fully rendered).
        if t == prev_text:
            stable_count += 1
            if stable_count >= 3:
                print(f"[llm-gatherer] Reply stable after {i+1}s ({len(t)} chars)")
                return str(t)
        else:
            stable_count = 0

        if stable_count > 0 and i % 5 == 0:
            print(f"  ... text stable ({stable_count}/3) text={len(t)} chars ({i+1}s)...")
        prev_text = t

    return "[超时] 未在 {}s 内收到回复".format(timeout)


async def evaluate(page_info, expr: str):
    """Evaluate JS expression on the page. Returns parsed result."""
    result = await _cdp_evaluate_raw(page_info["webSocketDebuggerUrl"], expr)
    if result is None:
        return None
    inner = result.get('result', {})
    if inner.get('subtype') == 'error':
        raise Exception(f"JS Error: {inner.get('description', '')[:500]}")
    return inner.get('value')
