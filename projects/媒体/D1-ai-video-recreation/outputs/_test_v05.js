// _test_v05.js — render specific test frames (times via CLI args, out dir via 2nd arg)
// usage: node _test_v05.js <outDir> <t1> <t2> ...
const fs = require('fs');
const path = require('path');
let src = fs.readFileSync(path.join(__dirname, 'render_full_pixel.js'), 'utf8');
src = src.replace(/\nmain\(\);\s*$/, '\nmodule.exports = { render, BW, BH, FPS, OUT };\n');
const m = { exports: {} };
const fn = new Function('module', 'exports', 'require', '__dirname', '__filename', src);
fn(m, m.exports, require, __dirname, path.join(__dirname, '_render_full_pixel.js'));
const { render, OUT, FPS } = m.exports;
const argOut = process.argv[2] || 'check_v05';
const times = process.argv.slice(3).map(Number).filter((x) => !isNaN(x));
const CHECK = path.resolve(argOut);
fs.mkdirSync(CHECK, { recursive: true });
if (!times.length) { console.error('no times given'); process.exit(1); }
for (const t of times) {
  const fi = Math.max(0, Math.floor(t * FPS));
  render(fi); // writes to OUT (frames_full) as f_<fi>.png
  const srcPath = path.join(OUT, 'f_' + String(fi).padStart(5, '0') + '.png');
  fs.copyFileSync(srcPath, path.join(CHECK, 't' + t + '.png'));
  console.log('wrote t' + t + ' fi=' + fi);
}
console.log('TEST DONE');
