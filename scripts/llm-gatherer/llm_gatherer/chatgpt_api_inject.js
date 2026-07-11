// ChatGPT Web API Injector
// Inject this script into the ChatGPT page to expose a local API
// Usage: Run in the browser console, then call window.__chatgptAPI.{method}

(function() {
    // Ensure we're on chatgpt.com
    if (!window.location.hostname.includes('chatgpt.com')) {
        console.warn('[API Injector] Not on chatgpt.com');
        return;
    }

    console.log('[API Injector] Initializing...');

    // ============ Message Sending ============
    window.__chatgptAPI = {
        async send_message(prompt) {
            // Find contenteditable input
            const editor = document.querySelector('[contenteditable="true"]');
            if (!editor) {
                return { error: 'Could not find contenteditable editor' };
            }

            // Set text
            editor.innerText = prompt;
            editor.dispatchEvent(new Event('input', { bubbles: true }));
            editor.dispatchEvent(new InputEvent('beforeinput', { bubbles: true }));
            editor.focus();
            await new Promise(r => setTimeout(r, 300));

            // Find and click send button
            const sendBtn = document.querySelector('button[type="submit"]');
            if (sendBtn) {
                sendBtn.click();
                return { status: 'sent', message: 'Message sent' };
            }

            // Fallback: keyboard Enter
            editor.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
            return { status: 'sent_via_keypress', message: 'Message sent via Enter key' };
        },

        get_latest_reply() {
            // Try to find the latest assistant response
            const selectors = [
                '[data-testid="conversation-cell"]',
                'div[data-message-author-role="assistant"]',
                'div[class*="prose"]',
            ];

            for (const sel of selectors) {
                const els = document.querySelectorAll(sel);
                for (let i = els.length - 1; i >= 0; i--) {
                    const text = els[i].innerText.trim();
                    if (text.length > 10) return text;
                }
            }

            // Fallback: body text
            const body = document.body.innerText;
            if (body.includes('有问题，尽管问') || body.includes('Ask me anything')) {
                return ''; // No reply yet
            }
            return body.slice(-2000);
        },

        get_conversation_list() {
            const items = document.querySelectorAll('[data-testid^="conversation-cell"]');
            const convos = [];
            items.forEach(item => {
                const titleEl = item.querySelector('[class*="title"]');
                if (titleEl) {
                    convos.push(titleEl.innerText.trim());
                }
            });
            return convos;
        },

        get_page_state() {
            return {
                url: window.location.href,
                title: document.title,
                body_text: document.body.innerText.substring(0, 1000),
                has_editor: !!document.querySelector('[contenteditable="true"]'),
                has_sidebar: !!document.querySelector('[class*="sidebar"]'),
                cookies: document.cookie
            };
        }
    };

    console.log('[API Injector] Ready! Call window.__chatgptAPI.send_message("your prompt")');
})();
