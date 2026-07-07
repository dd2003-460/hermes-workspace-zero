#!/usr/bin/env node
/**
 * Browser rendering + Claude visual analysis pipeline for T10.
 * Renders documents in headless Chromium, captures screenshots,
 * and sends them to Claude for visual review.
 *
 * Usage:
 *   node tools/browser-review.js render <file> <output.png>
 *   node tools/browser-review.js analyze <output.png> "[CLAUDE_API_KEY]"
 *   node tools/browser-review.js pipeline <file> "[CLAUDE_API_KEY]"
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { fileURLToPath } = require('url');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const parentDir = path.join(__dirname, '..');

// ─── Playwright rendering ───────────────────────────────────────────

async function renderToFile(filePath, outputFile, options = {}) {
  const {
    waitUntil = 'networkidle',
    viewport = { width: 1280, height: 800 },
    selector = 'body',
    fullPage = false,
    delayMs = 2000,
  } = options;

  const absPath = path.resolve(parentDir, filePath);
  const fileUrl = `file://${absPath}`;

  console.log(`Opening: ${fileUrl}`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport });
  await page.goto(fileUrl, { waitUntil });
  await page.waitForSelector(selector, { timeout: 10000 }).catch(() => {});
  await new Promise(r => setTimeout(r, delayMs)); // Allow rendering (math, charts)

  if (fullPage) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await new Promise(r => setTimeout(r, 1000));
  }

  await page.screenshot({ path: outputFile, fullPage });
  await browser.close();

  console.log(`Screenshot saved: ${outputFile}`);
  return outputFile;
}

// ─── Claude visual analysis ─────────────────────────────────────────

async function analyzeWithClaude(screenshotPath, prompt, apiKey) {
  const { default: anthropic } = await import('@anthropic-ai/sdk');
  const client = new anthropic({ apiKey });

  const imageContent = fs.readFileSync(screenshotPath);
  const base64Img = imageContent.toString('base64');

  const messageType = {
    type: 'image',
    source: {
      type: 'base64',
      media_type: 'image/png',
      data: base64Img,
    },
  };

  const msg = await client.messages.create(
    {
      model: 'claude-sonnet-4-5-20260401',
      max_tokens: 2000,
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: prompt || 'Review this document screenshot for: formatting, equation rendering, layout issues, and overall presentation quality.',
            },
            { ...messageType },
          ],
        },
      ],
    },
    { headers: { 'anthropic-dangerous-direct-browser-access': '1' } }
  );

  const review = msg.content.find(c => c.type === 'text')?.text || 'No response';
  console.log('Claude Review:\n', review);
  return review;
}

// ─── Pipeline ────────────────────────────────────────────────────────

async function pipeline(inputFile, apiKey, outputDir = 'note/reviews') {
  const basename = path.basename(inputFile, path.extname(inputFile));
  const screenshotFile = path.join(outputDir, `${basename}-review.png`);

  console.log('=== Step 1: Render document ===');
  await renderToFile(inputFile, screenshotFile, {
    fullPage: true,
    delayMs: 3000,
  });

  console.log('\n=== Step 2: Claude visual analysis ===');
  const review = await analyzeWithClaude(screenshotFile, `Review this document for:
1. Formatting and layout issues
2. Equation rendering quality (LaTeX/math)
3. Table/chart readability
4. Overall presentation quality
5. Specific issues or improvements`);

  // Save review
  const reviewFile = path.join(outputDir, `${basename}-review.txt`);
  fs.writeFileSync(reviewFile, `Review Date: ${new Date().toISOString()}\nInput: ${inputFile}\n\n${review}`);
  console.log(`\nReview saved: ${reviewFile}`);

  return { screenshot: screenshotFile, review };
}

// ─── CLI ─────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (cmd === 'render') {
    await renderToFile(args[1], args[2]);
  } else if (cmd === 'analyze') {
    await analyzeWithClaude(args[1], args[3] === '[CLAUDE_API_KEY]' ? undefined : args[3], args[3] === '[CLAUDE_API_KEY]' ? process.env.ANTHROPIC_API_KEY : args[3]);
  } else if (cmd === 'pipeline') {
    await pipeline(args[1], args[2] || process.env.ANTHROPIC_API_KEY);
  } else {
    console.log(`Usage:
  node browser-review.js render <file> <output.png>
  node browser-review.js analyze <screenshot.png> "[CLAUDE_API_KEY]"
  node browser-review.js pipeline <input_file> "[CLAUDE_API_KEY]"

Environment:
  ANTHROPIC_API_KEY - Required for analysis step`);
  }
}

main().catch(console.error);
