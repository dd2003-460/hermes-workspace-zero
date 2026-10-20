const { createCanvas } = require('canvas');
const fs = require('fs');
// 加载主渲染器但只渲染一帧
process.env.FRAMES_OUT = '/tmp/test_card';
fs.mkdirSync('/tmp/test_card', { recursive: true });
// 直接 require 主脚本会执行全部渲染, 改为内联关键代码
// 读取主脚本, 替换 OUT 和只渲染指定帧
const src = fs.readFileSync('render_full_pixel.js', 'utf-8');
// 找到 CARD 时间段并渲染
const T = 44.5; // CARD 刚开始
const FPS = 60;
const fi = Math.floor(T * FPS);
// 修改: 只渲染这一帧
const modified = src
  .replace("const OUT = process.env.FRAMES_OUT || path.join(__dirname, 'frames_full');", "const OUT = '/tmp/test_card';")
  .replace(/for \(let fi = 0; fi < NFRAMES; fi\+\+\)/, "for (let fi = " + fi + "; fi < " + (fi+1) + "; fi++)");
eval(modified);
console.log('rendered frame', fi, 'at t=' + T + 's');
