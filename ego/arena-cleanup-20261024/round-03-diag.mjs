const task = await taskSpace("arena-cleanup-20261024");
const page = task.page("p1");
console.log("URL:", await page.url());
console.log("TITLE:", await page.title());
// what's actually on the page
const diag = await page.evaluate(() => {
  const body = document.body;
  return {
    bodyLen: body ? body.innerText.length : 0,
    bodyHead: body ? body.innerText.slice(0, 600) : "(no body)",
    iframes: Array.from(document.querySelectorAll("iframe")).map(f => f.src).slice(0, 5),
    aCount: document.querySelectorAll("a").length,
    agentAnchors: document.querySelectorAll('a[href*="/agent/"]').length,
    allAnchors: Array.from(document.querySelectorAll("a")).slice(0, 15).map(a => (a.getAttribute("href") || "").slice(0, 60))
  };
});
console.log(JSON.stringify(diag, null, 1));
await page.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-cleanup-20261024/diag.png" });
