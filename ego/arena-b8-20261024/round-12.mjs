import { readFileSync } from "node:fs";
const fileText = readFileSync("/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/prompt-b8.txt", "utf8");
const task = await taskSpace(535);
const p1 = task.page("p1");
const tail = await p1.evaluate(() => {
  const el = document.querySelector('[contenteditable="true"]');
  return { len: el.innerText.length, tail: el.innerText.slice(-120) };
});
console.log("fileTail:", JSON.stringify(fileText.slice(-120)));
console.log("editorTail:", JSON.stringify(tail));
