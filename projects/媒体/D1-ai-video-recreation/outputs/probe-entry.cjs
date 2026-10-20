// 探针：手动模拟 renderer 流程，抓页面错误
const {bundle} = require('@remotion/bundler');
const puppeteer = require(require('path').join(__dirname, 'node_modules/@remotion/renderer/node_modules/puppeteer-core'));
(async () => {
  const r = await bundle({entryPoint: './index.ts'});
  const dir = typeof r === 'string' ? r : r[0];
  console.log('DIR:', dir);
  const browser = await puppeteer.launch({
    executablePath: './node_modules/.remotion/chrome-headless-shell/mac-arm64/chrome-headless-shell-mac-arm64/chrome-headless-shell',
    headless: 'shell',
    args: ['--no-sandbox', '--disable-gpu', '--user-data-dir=/tmp/chs-prof-4'],
    dumpio: true,
  });
  const page = await browser.newPage();
  page.on('console', (m) => console.log('[PAGE]', m.type(), m.text().slice(0, 300)));
  page.on('pageerror', (e) => console.log('[PAGEERROR]', String(e).slice(0, 400)));
  await page.evaluateOnNewDocument(() => { window.remotion_puppeteerTimeout = 30000; });
  const res = await page.goto('file://' + dir + '/index.html', {waitUntil: 'load', timeout: 60000}).catch((e) => e);
  console.log('GOTO:', res && res.status ? res.status() : String(res).slice(0, 200));
  await new Promise((res2) => setTimeout(res2, 8000));
  const state = await page.evaluate(() => ({
    hasFn: typeof window.getStaticCompositions,
    keys: Object.keys(window).filter((k) => k.startsWith('remotion')).length,
    body: document.body.innerHTML.slice(0, 200),
  })).catch((e) => 'EVAL ERR: ' + e.message);
  console.log('STATE:', JSON.stringify(state));
  await browser.close();
  process.exit(0);
})().catch((e) => { console.log('FATAL:', e.message.slice(0, 300)); process.exit(1); });
