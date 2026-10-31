const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-chat");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 找含"继续工作"按钮的容器，打印其完整结构（标签+class+文本）
const info = await page.evaluate(() => {
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === '继续工作');
  if (!b) return null;
  let el = b.parentElement;
  for (let i = 0; i < 3 && el; i++) el = el.parentElement;
  // 递归收集浅层结构
  function walk(node, depth) {
    if (depth > 3 || !node) return [];
    const out = [{ tag: node.tagName, cls: (node.className||'').toString().slice(0,50), txt: (node.childNodes.length===1 && node.firstChild.nodeType===3 ? node.textContent : '').slice(0,40) }];
    for (const c of node.children) out.push(...walk(c, depth+1));
    return out;
  }
  return walk(el, 0).slice(0, 60);
});
console.log(JSON.stringify(info, null, 1));
await task.finish({ keep: [] });
