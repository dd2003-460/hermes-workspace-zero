#!/usr/bin/env node
// P1 修复测试：验证 arena 通道是否可用
// 策略：最小任务（"回答 1+1=?"），30s 内落盘=可用，否则降级

import { taskSpace } from 'ego-browser';

async function main() {
  const task = await taskSpace('p1-fix-test-' + Date.now());
  const p1 = task.page('p1');
  
  // 1. 打开 arena
  await p1.goto('https://arena.ai/agent');
  await p1.waitForTimeout(3000);
  
  // 2. snapshot 验证页面加载
  const snap1 = await p1.snapshot();
  console.log('SNAP1:', snap1.slice(0, 200));
  
  // 3. 找输入框（F0 验证 1：提交前确认输入框存在）
  const input = p1.locator('textarea, [contenteditable="true"], input[type="text"]').first();
  const inputExists = await input.count() > 0;
  console.log('INPUT_EXISTS:', inputExists);
  
  if (!inputExists) {
    console.log('FAIL: 输入框不存在');
    await task.finish({ keep: [] });
    process.exit(1);
  }
  
  // 4. 输入最小任务
  const prompt = '1+1=?';
  await input.fill(prompt);
  await p1.waitForTimeout(500);
  
  // 5. snapshot 验证输入框有内容（F0 验证 2）
  const inputValue = await input.inputValue().catch(() => null);
  const hasContent = inputValue && inputValue.length > 0;
  console.log('INPUT_VALUE:', JSON.stringify(inputValue));
  console.log('HAS_CONTENT:', hasContent);
  
  if (!hasContent) {
    console.log('FAIL: 输入框无内容（page.fill 静默失败）');
    await task.finish({ keep: [] });
    process.exit(1);
  }
  
  // 6. 找发送按钮
  const sendBtn = p1.locator('button[type="submit"], [aria-label="发送"], [data-testid="send-button"]').first();
  const sendExists = await sendBtn.count() > 0;
  console.log('SEND_BTN_EXISTS:', sendExists);
  
  if (!sendExists) {
    console.log('FAIL: 发送按钮不存在');
    await task.finish({ keep: [] });
    process.exit(1);
  }
  
  // 7. 点击发送
  await sendBtn.click();
  console.log('SENT');
  
  // 8. 等待 30s，每 5s snapshot 一次
  for (let i = 0; i < 6; i++) {
    await p1.waitForTimeout(5000);
    const snap = await p1.snapshot();
    const hasReply = snap.includes('2') || snap.includes('回答');
    console.log(`SNAP${i+2} (${(i+1)*5}s): hasReply=${hasReply}`);
    if (hasReply) {
      console.log('PASS: arena 通道可用');
      await task.finish({ keep: [] });
      process.exit(0);
    }
  }
  
  console.log('FAIL: 30s 内无回复');
  await task.finish({ keep: [] });
  process.exit(1);
}

main().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
