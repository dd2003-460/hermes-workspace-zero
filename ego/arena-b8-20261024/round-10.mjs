const task = await taskSpace(535);
const p1 = task.page("p1");
const info = await p1.evaluate(() => {
  const out = { textareas: [], editables: [], buttons: [] };
  document.querySelectorAll('textarea').forEach(t => out.textareas.push({ id: t.id, cls: t.className.slice(0,80), ph: t.placeholder }));
  document.querySelectorAll('[contenteditable="true"]').forEach(e => out.editables.push({ tag: e.tagName, id: e.id, cls: (e.className||'').toString().slice(0,80), role: e.getAttribute('role'), ariaLabel: e.getAttribute('aria-label') }));
  document.querySelectorAll('input').forEach(i => out.textareas.push({ tag: i.tagName, id: i.id, cls: (i.className||'').toString().slice(0,60), type: i.type, ph: i.placeholder }));
  return out;
});
console.log(JSON.stringify(info, null, 2));
