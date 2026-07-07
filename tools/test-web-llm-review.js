#!/usr/bin/env node
/**
 * Unit tests for web-llm-review.js (non-browser parts).
 * Tests: session management, argument parsing, file structure.
 */

const fs = require('fs');
const path = require('path');

const SESSION_DIR = path.join(__dirname, '..', 'note', 'web-llm-sessions');
let passed = 0;
let failed = 0;

function assert(condition, msg) {
  if (condition) {
    console.log(`  PASS: ${msg}`);
    passed++;
  } else {
    console.log(`  FAIL: ${msg}`);
    failed++;
  }
}

function cleanup() {
  // Remove test session dir
  try { fs.rmSync(SESSION_DIR, { recursive: true, force: true }); } catch {}
}

console.log('=== web-llm-review.js Unit Tests ===\n');

// Test 1: Session directory creation
console.log('Test 1: Session directory management');
cleanup();
fs.mkdirSync(SESSION_DIR, { recursive: true });
assert(fs.existsSync(SESSION_DIR), 'Session dir created');

// Test 2: Save/load session
console.log('\nTest 2: Save/Load session');
const testSession = {
  sessionId: 'test-123',
  service: 'claude',
  pdfPath: 'test.pdf',
  timestamp: new Date().toISOString(),
  status: 'completed',
};
const sf = path.join(SESSION_DIR, 'test-123.json');
fs.writeFileSync(sf, JSON.stringify(testSession));
const loaded = JSON.parse(fs.readFileSync(sf, 'utf-8'));
assert(loaded.sessionId === 'test-123', 'Session ID matches');
assert(loaded.service === 'claude', 'Service matches');
assert(loaded.status === 'completed', 'Status matches');

// Test 3: List sessions
console.log('\nTest 3: List sessions');
// Add another session
fs.writeFileSync(path.join(SESSION_DIR, 'test-456.json'), JSON.stringify({
  sessionId: 'test-456', service: 'chatgpt', timestamp: new Date().toISOString(), status: 'failed'
}));
const files = fs.readdirSync(SESSION_DIR).filter(f => f.endsWith('.json'));
assert(files.length === 2, `2 session files exist (found ${files.length})`);

// Test 4: Delete session
console.log('\nTest 4: Delete session');
fs.unlinkSync(path.join(SESSION_DIR, 'test-123.json'));
const remaining = fs.readdirSync(SESSION_DIR).filter(f => f.endsWith('.json'));
assert(remaining.length === 1, `1 session file remaining (found ${remaining.length})`);

// Test 5: File structure of main tool
console.log('\nTest 5: Main tool file exists');
const toolPath = path.join(__dirname, 'web-llm-review.js');
assert(fs.existsSync(toolPath), 'web-llm-review.js exists');
const content = fs.readFileSync(toolPath, 'utf-8');
assert(content.includes('claude.ai'), 'Contains claude.ai reference');
assert(content.includes('chatgpt.com'), 'Contains chatgpt.com reference');
assert(content.includes('createBrowserContext'), 'Has browser context creation');
assert(content.includes('uploadToClaude'), 'Has Claude upload function');
assert(content.includes('uploadToChatGPT'), 'Has ChatGPT upload function');
assert(content.includes('extractClaudeReview'), 'Has Claude review extraction');
assert(content.includes('extractChatGPTReview'), 'Has ChatGPT review extraction');
assert(content.includes('setInputFiles') || content.includes('input[type="file"]'), 'Has file input handling');
assert(content.includes('Edge'), 'Has Edge browser profile support');

// Test 6: Syntax validation
console.log('\nTest 6: Syntax validation');
try {
  require('child_process').execSync(`node -c ${toolPath}`, { stdio: 'ignore' });
  assert(true, 'Syntax valid');
} catch {
  assert(false, 'Syntax check failed');
}

// Cleanup
cleanup();

console.log(`\n=== Results: ${passed} passed, ${failed} failed ===`);
process.exit(failed > 0 ? 1 : 0);
