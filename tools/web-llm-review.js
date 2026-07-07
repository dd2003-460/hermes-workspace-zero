#!/usr/bin/env node
/**
 * T18: Upload papers to web LLM services for external review.
 * Uses Playwright to automate browser interaction with Claude Web / ChatGPT
 * via Edge browser profile (session reuse — no API needed).
 *
 * Usage:
 *   node tools/web-llm-review.js upload <pdf_file> --service claude [--prompt "review prompt"]
 *   node tools/web-llm-review.js upload <pdf_file> --service chatgpt [--prompt "review prompt"]
 *   node tools/web-llm-review.js status <session_id>
 *   node tools/web-llm-review.js result <session_id>
 *   node tools/web-llm-review.js list
 *   node tools/web-llm-review.js logout <session_id>
 *
 * Services:
 *   claude    — claude.ai (recommended, best LaTeX rendering)
 *   chatgpt   — chatgpt.com (requires Plus subscription)
 *
 * Session reuse:
 *   Uses Edge browser profile to maintain logged-in sessions.
 *   macOS: ~/Library/Application Support/Microsoft/Edge/
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const PARENT_DIR = path.join(__dirname, '..');
const SESSION_DIR = path.join(PARENT_DIR, 'note', 'web-llm-sessions');
const EDGE_PROFILE_MAC = path.join(os.homedir(), 'Library', 'Application Support', 'Microsoft', 'Edge');
const EDGE_PROFILE_LINUX = path.join(os.homedir(), '.microsoft-edge-dev');

// ─── Session Management ─────────────────────────────────────────────

function generateSessionId() {
  return crypto.randomUUID();
}

function saveSession(sessionId, config) {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
  const file = path.join(SESSION_DIR, `${sessionId}.json`);
  fs.writeFileSync(file, JSON.stringify(config, null, 2));
  return file;
}

function loadSession(sessionId) {
  const file = path.join(SESSION_DIR, `${sessionId}.json`);
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, 'utf-8'));
}

function listSessions() {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
  if (!fs.existsSync(SESSION_DIR)) return [];
  return fs.readdirSync(SESSION_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => JSON.parse(fs.readFileSync(path.join(SESSION_DIR, f), 'utf-8')));
}

function deleteSession(sessionId) {
  const file = path.join(SESSION_DIR, `${sessionId}.json`);
  if (fs.existsSync(file)) {
    fs.unlinkSync(file);
    return true;
  }
  return false;
}

// ─── Browser Context ────────────────────────────────────────────────

function getEdgeProfile() {
  // Try macOS first, then fall back to default
  if (os.platform() === 'darwin' && fs.existsSync(EDGE_PROFILE_MAC)) {
    return EDGE_PROFILE_MAC;
  }
  // Chromium's default user data dir (no Edge profile — will need manual login)
  return null;
}

async function createBrowserContext(service) {
  const edgeProfile = getEdgeProfile();
  const browserType = service === 'chatgpt' ? chromium : chromium;

  if (edgeProfile) {
    // Reuse Edge persistent context — maintains all logged-in sessions
    const context = await browserType.launchPersistentContext(edgeProfile, {
      headless: false, // Must be visible for file upload dialogs
      viewport: { width: 1280, height: 900 },
      slowMo: 100, // Slow down for reliability
    });
    return context;
  } else {
    // Fallback: launch new browser with user data dir
    const userDataDir = path.join(os.tmpdir(), `web-llm-review-${Date.now()}`);
    fs.mkdirSync(userDataDir, { recursive: true });
    const browser = await browserType.launch({ headless: false });
    const context = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      slowMo: 100,
    });
    // Store userDataDir for cleanup
    context._userDataDir = userDataDir;
    return context;
  }
}

// ─── Claude Web Integration ─────────────────────────────────────────

const CLAUDE_URL = 'https://claude.ai';

async function waitForClaudeLoad(page) {
  try {
    await page.waitForLoadState('networkidle', { timeout: 30000 });
    await page.waitForSelector('textarea, [contenteditable="true"]', { timeout: 15000 });
    return true;
  } catch {
    return false;
  }
}

async function uploadToClaude(page, pdfPath, prompt) {
  const absPath = path.resolve(PARENT_DIR, pdfPath);
  if (!fs.existsSync(absPath)) {
    throw new Error(`File not found: ${absPath}`);
  }

  // Check if already logged in
  const url = page.url();
  if (url.includes('signin') || url.includes('login') || (await page.locator('textarea, [contenteditable]').count()) === 0) {
    console.log('Not logged in — waiting for manual login...');
    console.log('Open claude.ai and login in the current browser window.');
    console.log('Press any key when ready...');

    // Wait for user to log in
    await new Promise((resolve) => {
      const checkInterval = setInterval(async () => {
        const count = await page.locator('textarea, [contenteditable]').count();
        if (count > 0 && !page.url().includes('signin')) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 1000);
      // Also listen for keypress (timeout after 5 minutes)
      setTimeout(() => {
        clearInterval(checkInterval);
        resolve();
      }, 300000);
    });
  }

  // Click file upload button
  // Claude Web: look for upload icon or "Attach file" button
  const uploadSelectors = [
    '[data-testid="file-upload-button"]',
    'button:has-text("Attach")',
    'button:has(svg.clipboard)',
    'label:has(input[type="file"])',
    'button:has-text("Upload")',
    'input[type="file"]',
  ];

  let uploadBtn = null;
  for (const sel of uploadSelectors) {
    const el = page.locator(sel).first();
    if (await el.count().catch(() => 0) > 0) {
      uploadBtn = el;
      break;
    }
  }

  if (uploadBtn) {
    // Try clicking the upload button
    await uploadBtn.click({ timeout: 5000 }).catch(async () => {
      // If click fails, try dispatching event
      await uploadBtn.dispatchEvent('click').catch(() => {});
    });
  } else {
    // Fallback: try drag-and-drop zone
    const dropZone = page.locator('[dropzone], .drop-zone, [data-drop-zone]').first();
    if (await dropZone.count().catch(() => 0) > 0) {
      console.log('Found drop zone, trying drag approach');
    }
  }

  // Wait for file input (Playwright can also directly set files)
  const fileInput = page.locator('input[type="file"]').first();
  if (await fileInput.count().catch(() => 0) > 0) {
    await fileInput.setInputFiles(absPath);
    console.log(`Uploaded: ${path.basename(pdfPath)}`);
  } else {
    console.log('Could not find file input. The file may need to be attached manually.');
    console.log('Try dragging the PDF onto the Claude Web chat window.');
  }

  // Wait for upload to complete
  await page.waitForTimeout(3000);

  // Enter the review prompt
  const textareas = page.locator('textarea, [contenteditable="true"]');
  if (await textareas.count().catch(() => 0) > 0) {
    await textareas.first().click();
    await textareas.first().fill(prompt);
    console.log('Review prompt entered.');
  }

  // Send the message
  const sendSelectors = [
    'button:has-text("Send")',
    'button:has-text("Send message")',
    'button.send',
    'button[data-testid="send-button"]',
    'form button[type="submit"]',
  ];

  let sent = false;
  for (const sel of sendSelectors) {
    const btn = page.locator(sel).first();
    if (await btn.count().catch(() => 0) > 0) {
      await btn.click();
      sent = true;
      console.log('Review request sent.');
      break;
    }
  }

  if (!sent) {
    // Try pressing Enter in the text area
    const textarea = page.locator('textarea, [contenteditable]').first();
    if (await textarea.count().catch(() => 0) > 0) {
      await textarea.press('Enter');
      sent = true;
      console.log('Sent via Enter key.');
    }
  }

  return sent;
}

async function extractClaudeReview(page, maxWaitMs = 120000) {
  // Wait for response to appear
  // Claude displays response as text in the chat area
  const responseSelectors = [
    '[data-testid="message"]',
    '.markdown-body',
    '.prose',
    '[class*="message"]',
    '[class*="response"]',
  ];

  console.log(`Waiting for Claude response (max ${maxWaitMs / 1000}s)...`);

  let responseText = null;

  // Strategy 1: Wait for new message element
  try {
    await page.waitForSelector(responseSelectors[0], { timeout: maxWaitMs });
    responseText = await page.locator(responseSelectors[0]).first().textContent();
  } catch {
    console.log('Could not find expected response element. Falling back to page text...');
  }

  // Strategy 2: Extract all text from page body
  if (!responseText || responseText.length < 50) {
    try {
      responseText = await page.evaluate(() => {
        const body = document.body;
        // Get text, stripping excessive whitespace
        return body.innerText
          .replace(/\s+/g, ' ')
          .replace(/:{2,}/g, ':')
          .trim();
      });
    } catch {
      responseText = null;
    }
  }

  // Strategy 3: Try to extract just the new response (not the conversation)
  if (responseText && responseText.length > 5000) {
    // Likely includes full conversation, try to get only the latest response
    try {
      const latestMsg = await page.evaluate(() => {
        const messages = document.querySelectorAll('[class*="message"], [class*="response"], [data-testid="message"]');
        if (messages.length > 0) {
          const last = messages[messages.length - 1];
          return last.innerText || last.textContent;
        }
        return null;
      });
      if (latestMsg && latestMsg.length > 100) {
        responseText = latestMsg;
      }
    } catch {}
  }

  return responseText || 'No response extracted. Check the browser window manually.';
}

// ─── ChatGPT Integration ────────────────────────────────────────────

const CHATGPT_URL = 'https://chatgpt.com';

async function waitForChatGPTLoad(page) {
  try {
    await page.goto(CHATGPT_URL, { waitUntil: 'networkidle', timeout: 30000 });
    // Wait for chat input
    await page.waitForSelector('textarea, [contenteditable="true"]', { timeout: 15000 });
    return true;
  } catch (e) {
    console.log('ChatGPT load failed:', e.message);
    return false;
  }
}

async function uploadToChatGPT(page, pdfPath, prompt) {
  const absPath = path.resolve(PARENT_DIR, pdfPath);
  if (!fs.existsSync(absPath)) {
    throw new Error(`File not found: ${absPath}`);
  }

  // Check login status
  const url = page.url();
  if (url.includes('/auth/login') || url.includes('/start')) {
    console.log('Not logged in to ChatGPT — waiting for manual login...');
    await new Promise((resolve) => {
      const checkInterval = setInterval(async () => {
        if (!page.url().includes('/auth/login') && !page.url().includes('/start')) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 1000);
      setTimeout(() => { clearInterval(checkInterval); resolve(); }, 300000);
    });
  }

  // Click attachment button
  const attachSelectors = [
    'button[aria-label*="upload"]',
    'button:has-text("Upload")',
    'label:has(input[type="file"])',
    '[data-testid="attachment-button"]',
  ];

  let attached = false;
  for (const sel of attachSelectors) {
    const el = page.locator(sel).first();
    if (await el.count().catch(() => 0) > 0) {
      await el.click().catch(() => {});
      break;
    }
  }

  // Try to set files via file input
  const fileInput = page.locator('input[type="file"]').first();
  if (await fileInput.count().catch(() => 0) > 0) {
    await fileInput.setInputFiles(absPath);
    console.log(`Uploaded: ${path.basename(pdfPath)}`);
    attached = true;
  }

  await page.waitForTimeout(2000);

  // Enter prompt
  const textarea = page.locator('textarea, [contenteditable]').first();
  if (await textarea.count().catch(() => 0) > 0) {
    await textarea.click();
    await textarea.fill(prompt);
  }

  // Send
  const sendBtn = page.locator('button:has-text("Send"), form button[type="submit"]').first();
  if (await sendBtn.count().catch(() => 0) > 0) {
    await sendBtn.click();
  } else {
    await textarea.press('Enter').catch(() => {});
  }
  console.log('Review request sent to ChatGPT.');

  return attached;
}

async function extractChatGPTReview(page, maxWaitMs = 120000) {
  // Similar extraction logic
  const responseSelectors = [
    '[data-testid="conversation-assistant-message"]',
    '[class*="assistant-message"]',
    '[class*="markdown"]',
  ];

  console.log(`Waiting for ChatGPT response (max ${maxWaitMs / 1000}s)...`);

  try {
    await page.waitForSelector(responseSelectors[0], { timeout: maxWaitMs });
    const msg = page.locator(responseSelectors[0]).last();
    const text = await msg.textContent();
    if (text && text.length > 50) return text;
  } catch {}

  // Fallback to full page text
  try {
    return await page.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').trim());
  } catch {
    return 'No response extracted. Check the browser window manually.';
  }
}

// ─── Main Pipeline ──────────────────────────────────────────────────

async function uploadPaper(pdfPath, service, options = {}) {
  const {
    prompt = 'Please review this academic paper for: 1) Technical accuracy of arguments and methodology, 2) Clarity of exposition and logical flow, 3) Quality of LaTeX equation rendering, 4) Adequacy of literature review and citations, 5) Originality and significance of contributions, 6) Specific issues or improvements.',
    timeout = 180000, // 3 minutes for response
  } = options;

  const sessionId = generateSessionId();
  const serviceUrls = {
    claude: CLAUDE_URL,
    chatgpt: CHATGPT_URL,
  };

  console.log(`\n=== T18: Web LLM Review ===`);
  console.log(`Service: ${service}`);
  console.log(`Paper: ${pdfPath}`);
  console.log(`Session: ${sessionId}\n`);

  let context = null;
  let page = null;

  try {
    context = await createBrowserContext(service);

    // Navigate to service
    page = context.pages()[0] || await context.newPage();
    await page.goto(serviceUrls[service], { waitUntil: 'networkidle', timeout: 30000 });

    if (service === 'claude') {
      await uploadToClaude(page, pdfPath, prompt);
    } else if (service === 'chatgpt') {
      await uploadToChatGPT(page, pdfPath, prompt);
    } else {
      throw new Error(`Unknown service: ${service}`);
    }

    // Extract review
    const extractFn = service === 'claude' ? extractClaudeReview : extractChatGPTReview;
    const review = await extractClaudeReview(page, timeout);

    // Save session state
    const sessionFile = saveSession(sessionId, {
      sessionId,
      service,
      pdfPath,
      prompt,
      review,
      timestamp: new Date().toISOString(),
      status: 'completed',
    });

    console.log(`\nReview saved to session: ${sessionFile}`);
    console.log(`Review length: ${review.length} characters`);
    console.log(`\n--- Review Preview (first 500 chars) ---\n${review.substring(0, 500)}\n`);

    await context.close();

    return { sessionId, review, sessionFile };

  } catch (err) {
    console.error('Error during review:', err.message);
    if (context) {
      // Save session for recovery
      saveSession(sessionId, {
        sessionId,
        service,
        pdfPath,
        prompt,
        error: err.message,
        timestamp: new Date().toISOString(),
        status: 'failed',
      });
      await context.close().catch(() => {});
    }
    throw err;
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (cmd === 'upload') {
    const pdfPath = args[1];
    const serviceArg = args.findIndex('--service');
    const service = serviceArg >= 0 ? args[serviceArg + 1] : 'claude';
    const promptArg = args.findIndex('--prompt');
    const prompt = promptArg >= 0 ? args.slice(promptArg + 1).join(' ') : null;

    if (!pdfPath) {
      console.error('Usage: web-llm-review.js upload <pdf_file> --service <claude|chatgpt> [--prompt "review prompt"]');
      process.exit(1);
    }

    const result = await uploadPaper(pdfPath, service, { prompt });
    console.log(JSON.stringify(result, null, 2));

  } else if (cmd === 'status') {
    const sessionId = args[1];
    const session = loadSession(sessionId);
    if (!session) {
      console.error(`Session not found: ${sessionId}`);
      process.exit(1);
    }
    console.log(JSON.stringify(session, null, 2));

  } else if (cmd === 'list') {
    const sessions = listSessions();
    console.log(`\n${sessions.length} session(s):\n`);
    sessions.forEach(s => {
      console.log(`  ${s.sessionId.slice(0, 8)}...  ${s.service}  ${path.basename(s.pdfPath)}  ${s.status}  ${s.timestamp}`);
    });

  } else if (cmd === 'result') {
    const sessionId = args[1];
    const session = loadSession(sessionId);
    if (!session) {
      console.error(`Session not found: ${sessionId}`);
      process.exit(1);
    }
    if (session.status !== 'completed') {
      console.error(`Session not completed: ${session.status}`);
      process.exit(1);
    }
    console.log(session.review);

  } else if (cmd === 'logout') {
    // Clear session data for a fresh login
    const sessionId = args[1];
    if (deleteSession(sessionId)) {
      console.log(`Session ${sessionId} deleted.`);
    } else {
      console.error(`Session not found: ${sessionId}`);
    }

  } else {
    console.log(`T18: Upload papers to web LLM for external review

Usage:
  node web-llm-review.js upload <pdf_file> --service <claude|chatgpt> [--prompt "review prompt"]
  node web-llm-review.js status <session_id>
  node web-llm-review.js list
  node web-llm-review.js result <session_id>
  node web-llm-review.js logout <session_id>

Services:
  claude    — claude.ai (recommended, best LaTeX rendering, 200K context)
  chatgpt   — chatgpt.com (requires Plus subscription)

Session reuse:
  Uses Edge browser profile to maintain logged-in sessions.
  First run requires manual login — script will wait for it.`);
  }
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
