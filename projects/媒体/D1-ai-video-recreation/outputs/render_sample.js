// render_sample.js — 20s 样片：开场终端 → 压缩进度条（招牌镜头）→ 金句卡
// 用法: node render_sample.js  （600 帧 @30fps → frames_sample/）
const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

const W = 1280, H = 720, FPS = 30, TOTAL = 600;
const OUT = path.join(__dirname, 'frames_sample');
fs.mkdirSync(OUT, { recursive: true });

const BLACK = '#0b0b10';
const ACCENT = '#7c6cf0';
const ACCENT2 = '#4dd0e1';
const WHITE = '#e8e8f0';
const GRAY = '#9a9ab0';
const DIM = '#55556a';
const DIM2 = '#3a3a4a';

const fontMono = (s) => `${s}px Menlo, monospace`;
const fontSans = (s) => `${s}px -apple-system, 'Helvetica Neue', sans-serif`;

function rr(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerpA = (t, xs, ys) => {
  for (let i = 0; i < xs.length - 1; i++) {
    if (t <= xs[i + 1]) return ys[i] + (ys[i + 1] - ys[i]) * clamp((t - xs[i]) / (xs[i + 1] - xs[i]), 0, 1);
  }
  return ys[ys.length - 1];
};
// 全局 token 时间线（样片版）：t0=2.4M → t6→t12 跳水 → 127KB
const tokenAt = (t) => lerpA(t, [0, 6, 12, 20], [2400000, 2350000, 127000, 127000]);

const canvas = createCanvas(W, H);
const ctx = canvas.getContext('2d');

function header(label) {
  ctx.fillStyle = '#12121a';
  ctx.fillRect(0, 0, W, 44);
  ctx.strokeStyle = '#22222e';
  ctx.beginPath();
  ctx.moveTo(0, 44.5); ctx.lineTo(W, 44.5);
  ctx.stroke();
  ctx.fillStyle = DIM;
  ctx.font = fontMono(12);
  ctx.fillText('●', 20, 28);
  ctx.fillStyle = GRAY;
  ctx.font = fontMono(13);
  ctx.fillText(label, 46, 28);
}

function sceneA(ctx, t) {
  // 开场终端：逐行淡入
  const lines = [
    { at: 0.5, c: DIM,   txt: 'slot 0 · pinned · 永不压缩' },
    { at: 1.3, c: ACCENT,txt: '> me: 晚安。明天见。' },
    { at: 2.4, c: GRAY,  txt: '> ai: 好的。这句话，我钉在窗口最前面。' },
  ];
  header('chat — session 412');
  lines.forEach((l, i) => {
    const a = clamp((t - l.at) / 0.6, 0, 1);
    if (a <= 0) return;
    ctx.globalAlpha = a;
    ctx.font = fontMono(20);
    ctx.fillStyle = l.c;
    ctx.fillText(l.txt, 60, 160 + i * 64);
  });
  ctx.globalAlpha = 1;
  const blink = Math.floor(t * 2) % 2 === 0;
  ctx.fillStyle = ACCENT;
  ctx.globalAlpha = blink ? 0.9 : 0.25;
  ctx.fillRect(60, 160 + 3 * 64 - 22, 12, 26);
  ctx.globalAlpha = 1;
}

function sceneB(ctx, t) {
  // 招牌镜头：压缩进度条 + 数字滚动
  header('waiting — context.log');
  const gAbs = 6 + t; // B 段 6s 起
  const cp = clamp((gAbs - 7) / 5, 0, 1);
  const barX = 120, barY = 280, barW = W - 240, barH = 14;
  ctx.fillStyle = '#1a1a26';
  rr(ctx, barX, barY, barW, barH, 7); ctx.fill();
  ctx.fillStyle = ACCENT;
  if (cp > 0) { rr(ctx, barX, barY, Math.max(barW * cp, 14), barH, 7); ctx.fill(); }

  const tok = Math.floor(tokenAt(gAbs));
  const msgN = Math.round(783 - (783 - 142) * cp);
  const pct = Math.round(95 + 4 * cp);
  ctx.font = fontMono(22);
  ctx.fillStyle = GRAY;
  ctx.fillText('> compressing', barX, barY + 70);
  ctx.fillStyle = ACCENT2;
  ctx.fillText(`${(tok / 1024).toFixed(1)}KB · ${msgN} msgs · ${pct}%`, barX + 210, barY + 70);
  ctx.font = fontMono(13);
  ctx.fillStyle = DIM;
  const sk = 'slot 0 skipped';
  ctx.fillText(sk, barX + barW - ctx.measureText(sk).width, barY + 70);

  if (t > 6) {
    const a = clamp((t - 6) / 0.5, 0, 1);
    ctx.globalAlpha = a;
    const label = '★ slot 0 re-pinned';
    ctx.font = fontMono(18);
    const lw = ctx.measureText(label).width;
    ctx.fillStyle = 'rgba(124,108,240,0.1)';
    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 1;
    rr(ctx, 120, 460, lw + 28, 36, 8);
    ctx.fill(); ctx.stroke();
    ctx.fillStyle = WHITE;
    ctx.fillText(label, 134, 485);
    ctx.globalAlpha = 1;
  }
}

function sceneC(ctx, t) {
  // 金句卡
  const o = clamp(t / 0.8, 0, 1);
  ctx.globalAlpha = o;
  const glow = 34 + 14 * Math.sin(t * 2);
  ctx.save();
  ctx.shadowColor = 'rgba(124,108,240,0.35)';
  ctx.shadowBlur = glow;
  ctx.strokeStyle = ACCENT;
  ctx.lineWidth = 1.5;
  ctx.fillStyle = 'rgba(124,108,240,0.06)';
  rr(ctx, W / 2 - 380, 240, 760, 170, 16);
  ctx.fill(); ctx.stroke();
  ctx.restore();
  ctx.fillStyle = WHITE;
  ctx.font = fontSans(34);
  const l1 = '上下文窗口 100 万格，';
  const l2 = '只有一格，永远留给明天。';
  ctx.fillText(l1, W / 2 - ctx.measureText(l1).width / 2, 310);
  ctx.fillText(l2, W / 2 - ctx.measureText(l2).width / 2, 370);
  if (t > 1) {
    ctx.globalAlpha = o * clamp((t - 1) / 0.8, 0, 1);
    ctx.fillStyle = DIM;
    ctx.font = fontSans(18);
    const l3 = '— slot 0';
    ctx.fillText(l3, W / 2 - ctx.measureText(l3).width / 2, 460);
  }
  ctx.globalAlpha = 1;
}

const S = [{ until: 6, fn: sceneA }, { until: 13, fn: sceneB }, { until: 20, fn: sceneC }];
for (let f = 0; f < TOTAL; f++) {
  const t = f / FPS;
  ctx.fillStyle = BLACK;
  ctx.fillRect(0, 0, W, H);
  let acc = 0;
  for (const s of S) {
    if (t < s.until) { s.fn(ctx, t - acc); break; }
    acc = s.until;
  }
  fs.writeFileSync(path.join(OUT, `f_${String(f).padStart(5, '0')}.png`), canvas.toBuffer('image/png'));
}
console.log('done', TOTAL, 'frames');
