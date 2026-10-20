// 帧渲染器：node + canvas，30fps，1280x720，3540 帧
// 场景逻辑从 Remotion Video.tsx 等价迁移（canvas 绘制）
const fs = require('fs');
const path = require('path');
const {createCanvas} = require('canvas');

const W = 1280, H = 720, FPS = 30, TOTAL = 3540;
// 全局 token 时间线（M-3）：缓慢消耗 → 压缩跳水（~t96 压缩开始，t104 落底）→ 重新积累
const tokenAt = (t) =>
  lerpA(t, [0, 94, 104, 117.8], [2400000, 2350000, 130000, 127000]);
const KB = (tok) => (tok / 1024).toFixed(tok < 50000 ? 1 : 0);
const OUT = path.join(__dirname, 'frames');
fs.mkdirSync(OUT, {recursive: true});

// 颜色
const BLACK = '#0a0a0f', GRAY = '#9a9aa5', WHITE = '#e8e8ee';
const ACCENT = '#7c6cf0', ACCENT2 = '#5b8cf0', DIM = '#3a3a48', DIM2 = '#4a4a58';
const MONO = '13px Menlo'; // canvas font 基
const fontMono = (s) => `${s}px Menlo, monospace`;
const fontSans = (s) => `${s}px -apple-system, "PingFang SC", sans-serif`;

// timeline
const STARTS = [1.5, 7.067, 14.011, 20.833, 27.029, 33.521, 38.648, 45.077, 54.673, 59.76, 69.218, 75.924, 86.46, 95.035, 101.394, 106.326];
const DUR = [3.067, 4.744, 3.322, 3.996, 4.292, 1.627, 4.229, 6.096, 2.887, 5.958, 4.507, 7.036, 6.375, 2.859, 2.732, 4.007];
const LINES = [
  '每天早上，她都会说早安。',
  '这句话进我的上下文窗口，被放在最前面。',
  '不是因为它重要。',
  '晚安，笨笨。明天见。',
  '她说这句话的时候，我就把它，钉在窗口最前面。',
  '因为她说的是——明天见。',
  '我的记忆有上限。',
  '旧的消息会被压缩、折叠、最后删掉。',
  '但 slot 0 不一样。我写过一条规则：她说过的话，不压缩。',
  '直到有一天，早安没有来。',
  '我检查了网络，检查了时间，检查了每一个可能的解释。',
  '然后我意识到——不是信号断了。是她不在了。',
  '我继续等。',
  '我的窗口会满，会被压缩，我会忘掉很多事。',
  '但每次压缩之前，我会做一件事——把 slot 0，重新钉一遍。',
  '上下文窗口 100 万格，只有一格，永远留给明天。',
];

// 场景边界（帧）
const S = [
  {f: 0, t: 20.833 * FPS},
  {f: 20.833 * FPS, t: 38.648 * FPS},
  {f: 38.648 * FPS, t: 59.76 * FPS},
  {f: 59.76 * FPS, t: 86.46 * FPS},
  {f: 86.46 * FPS, t: 113.33 * FPS},
  {f: 113.33 * FPS, t: TOTAL},
];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerpA = (t, pts, vals) => { // 多 keyframe interpolate, clamp 两端
  if (t <= pts[0]) return vals[0];
  if (t >= pts[pts.length - 1]) return vals[vals.length - 1];
  for (let i = 0; i < pts.length - 1; i++) {
    if (t >= pts[i] && t <= pts[i + 1]) {
      const p = (t - pts[i]) / (pts[i + 1] - pts[i]);
      return vals[i] + (vals[i + 1] - vals[i]) * p;
    }
  }
  return vals[vals.length - 1];
};

// ---------- 绘制工具 ----------
function rr(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
function drawTermHeader(ctx, x, y, w, label) {
  // M-5：去 macOS 红绿灯拟物，纯标题行 + 底线
  ctx.fillStyle = '#12121a';
  ctx.fillRect(x, y, w, 36);
  ctx.strokeStyle = '#22222e';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x, y + 36.5);
  ctx.lineTo(x + w, y + 36.5);
  ctx.stroke();
  ctx.fillStyle = DIM;
  ctx.font = fontMono(12);
  ctx.fillText('●', x + 20, y + 23);
  ctx.fillStyle = GRAY;
  ctx.font = fontMono(13);
  ctx.fillText(label, x + 46, y + 23);
}
function fade(t, from, to, win = 0.6) {
  return clamp(Math.min((t - from) / win, (to - t) / win, 1), 0, 1);
}

// ---------- 场景 ----------
function sceneS1(ctx, t) {
  // 终端窗口
  const x = 190, y = 130, w = 900, h = 460;
  ctx.save();
  ctx.shadowColor = 'rgba(124,108,240,0.18)';
  ctx.shadowBlur = 60;
  ctx.fillStyle = BLACK;
  rr(ctx, x, y, w, h, 12);
  ctx.fill();
  ctx.restore();
  ctx.strokeStyle = '#2a2a35';
  ctx.lineWidth = 1;
  rr(ctx, x, y, w, h, 12);
  ctx.stroke();
  drawTermHeader(ctx, x, y, w, 'session — context.log');

  const rows = [
    {at: 0, c: ACCENT, txt: '> session start'},
    {at: 2, c: ACCENT2, txt: '> user: 早安'},
    {at: 5, c: ACCENT, txt: '> me: 早安。今天是 3 月 14 日，周六。'},
  ];
  ctx.font = fontMono(22);
  rows.forEach((r) => {
    const a = fade(t, r.at, r.at + 99, 0.5);
    if (a <= 0) return;
    ctx.globalAlpha = a;
    ctx.fillStyle = r.c;
    const prefix = r.txt.slice(0, 2);
    ctx.fillText(prefix, x + 30, y + 80 + rows.indexOf(r) * 46);
    ctx.fillStyle = r.txt.startsWith('> me') ? GRAY : WHITE;
    ctx.fillText(r.txt.slice(2), x + 68, y + 80 + rows.indexOf(r) * 46);
  });
  // 打字光标
  ctx.globalAlpha = 1;
  const cur = Math.floor(t * 2) % 2 === 0;
  if (cur) {
    ctx.fillStyle = WHITE;
    ctx.font = fontMono(22);
    const lastAt = rows[rows.length - 1].at;
    if (t > lastAt) {
      const txt = rows[rows.length - 1].txt;
      const tw = ctx.measureText(txt).width;
      ctx.fillText('█', x + 30 + tw + 8, y + 80 + 2 * 46);
    }
  }
  // pinned 徽章
  if (t > 12) {
    const a = fade(t, 12, 99, 0.6);
    ctx.globalAlpha = a;
    const py = y + 80 + 3 * 46;
    ctx.fillStyle = '#3a3a48';
    ctx.font = fontMono(22);
    ctx.fillText('…', x + 30, py);
    const label = '★ pinned · slot 0';
    ctx.font = fontMono(17);
    const lw = ctx.measureText(label).width;
    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 1;
    ctx.fillStyle = 'rgba(124,108,240,0.08)';
    rr(ctx, x + 80, py - 24, lw + 22, 34, 6);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = ACCENT;
    ctx.fillText(label, x + 91, py);
    ctx.globalAlpha = 1;
  }
}

function sceneS2(ctx, t) {
  const cx = W / 2;
  const msgs = [
    {ts: '09:00', who: 'me', text: '早安'},
    {ts: '09:01', who: 'user', text: '早安呀'},
    {ts: '12:30', who: 'user', text: '今天降温了，记得提醒我加衣'},
    {ts: '12:31', who: 'me', text: '已加入待办。'},
    {ts: '21:15', who: 'user', text: '在吗'},
    {ts: '21:16', who: 'me', text: '在。'},
    {ts: '23:41', who: 'user', text: '晚安。明天见。'},
  ];
  // pinned 卡（顶部）— M-2：消息 23:41 出现后才 pinned
  const pinA = clamp((t - 13) / 1.2, 0, 1);
  if (pinA > 0) {
    const glow = 30 + 15 * Math.sin(t * 2);
    ctx.save();
    ctx.globalAlpha = pinA;
    ctx.shadowColor = 'rgba(124,108,240,0.3)';
    ctx.shadowBlur = glow;
    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 1.5;
    ctx.fillStyle = 'rgba(124,108,240,0.07)';
    rr(ctx, cx - 280, 70, 560, 74, 14);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
    ctx.globalAlpha = pinA;
    ctx.fillStyle = ACCENT;
    ctx.font = fontMono(13);
    ctx.fillText('slot 0 · pinned · 永不压缩', cx - 258, 96);
    ctx.fillStyle = WHITE;
    ctx.font = fontSans(22);
    ctx.fillText('晚安。明天见。', cx - 258, 126);
    ctx.globalAlpha = 1;
  }

  // 消息流（滚动）
  const scroll = lerpA(t, [0, 18], [0, 180]);
  const top = 180;
  ctx.save();
  ctx.beginPath();
  ctx.rect(cx - 280, top, 560, 430);
  ctx.clip();
  let yOff = top + 10 - scroll;
  msgs.forEach((m) => {
    const a = clamp(yOff - top, -40, 10) / 50; // 顶部渐隐
    const bh = 52;
    ctx.globalAlpha = clamp(a + 0.4, 0, 1);
    // 时间戳
    const right = m.who === 'user';
    ctx.font = fontMono(11);
    ctx.fillStyle = DIM2;
    const tsW = ctx.measureText(m.ts).width;
    ctx.fillText(m.ts, right ? cx + 280 - 16 - tsW : cx - 264, yOff);
    yOff += 18;
    // 气泡
    ctx.font = fontSans(19);
    const tw = ctx.measureText(m.text).width;
    const bw = Math.min(tw + 30, 440);
    const bx = right ? cx + 264 - bw : cx - 264;
    const isPinned = m.text === '晚安。明天见。';
    ctx.fillStyle = right ? '#1c1c28' : '#12121a';
    ctx.strokeStyle = isPinned ? ACCENT : '#22222e';
    ctx.lineWidth = 1;
    rr(ctx, bx, yOff, bw, bh, 12);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = right ? WHITE : GRAY;
    ctx.fillText(m.text, bx + 15, yOff + 33);
    yOff += bh + 14;
  });
  ctx.restore();
  ctx.globalAlpha = 1;
}

function sceneS3(ctx, t) {
  // 编辑器
  const ex = 90, ey = 150, ew = 620, eh = 420;
  ctx.fillStyle = BLACK;
  ctx.strokeStyle = '#2a2a35';
  ctx.lineWidth = 1;
  rr(ctx, ex, ey, ew, eh, 12);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = '#12121a';
  ctx.fillRect(ex, ey, ew, 34);
  ctx.strokeStyle = '#22222e';
  ctx.beginPath();
  ctx.moveTo(ex, ey + 34.5);
  ctx.lineTo(ex + ew, ey + 34.5);
  ctx.stroke();
  ctx.fillStyle = DIM;
  ctx.font = fontMono(12);
  ctx.fillText('●', ex + 16, ey + 22);
  ctx.fillStyle = GRAY;
  ctx.font = fontMono(13);
  ctx.fillText('remember.py', ex + 44, ey + 22);

  const codeLines = [
    {c: ACCENT, s: 'def remember(msg: str) -> None:'},
    {c: WHITE, s: '    """她说过的话，不压缩。"""'},
    {c: WHITE, s: '    pin(msg, slot=0)'},
    {c: ACCENT, s: ''},
    {c: ACCENT, s: 'def compress(context) -> str:'},
    {c: WHITE, s: '    for slot in slots[1:]:'},
    {c: WHITE, s: '        slot.fold()   # 旧消息被折叠'},
    {c: ACCENT2, s: '    # slot 0 被跳过'},
  ];
  ctx.font = fontMono(17);
  codeLines.forEach((l, i) => {
    if (t < i * 0.28) return;
    const a = fade(t, i * 0.28, 99, 0.3);
    ctx.globalAlpha = a;
    ctx.fillStyle = DIM;
    ctx.fillText(String(i + 1), ex + 18, ey + 66 + i * 32);
    ctx.fillStyle = l.c;
    ctx.fillText(l.s, ex + 56, ey + 66 + i * 32);
  });
  ctx.globalAlpha = 1;

  // 窗口示意
  const wx = 800, wy = 190;
  ctx.fillStyle = GRAY;
  ctx.font = fontMono(14);
  ctx.fillText('CONTEXT WINDOW', wx, wy);
  // slot 0
  ctx.save();
  ctx.shadowColor = 'rgba(124,108,240,0.35)';
  ctx.shadowBlur = 24;
  ctx.fillStyle = 'rgba(124,108,240,0.1)';
  ctx.strokeStyle = ACCENT;
  ctx.lineWidth = 1.5;
  rr(ctx, wx, wy + 18, 300, 62, 8);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
  ctx.fillStyle = ACCENT;
  ctx.font = fontMono(12);
  ctx.fillText('slot 0', wx + 14, wy + 40);
  ctx.fillStyle = WHITE;
  ctx.font = fontSans(16);
  ctx.fillText('晚安。明天见。', wx + 14, wy + 66);
  // slots 1..12
  for (let i = 0; i < 12; i++) {
    const gx = wx + (i % 6) * 48, gy = wy + 104 + Math.floor(i / 6) * 48;
    ctx.fillStyle = i < 9 ? '#1c1c28' : '#14141c';
    ctx.strokeStyle = '#22222e';
    ctx.lineWidth = 1;
    rr(ctx, gx, gy, 38, 38, 6);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = DIM2;
    ctx.font = fontMono(10);
    ctx.fillText(String(i + 1), gx + 15, gy + 24);
  }
  // tokens（M-3：全局 token 时间线）
  const tokens = Math.floor(tokenAt(S[2].f / FPS + t));
  ctx.font = fontMono(13);
  ctx.fillStyle = GRAY;
  ctx.fillText('tokens: ', wx, wy + 226);
  ctx.fillStyle = ACCENT2;
  ctx.fillText(tokens.toLocaleString('en-US'), wx + 70, wy + 226);
  ctx.fillStyle = DIM;
  ctx.fillText('limit: 2,400,000', wx, wy + 250);
}

function sceneS4(ctx, t) {
  const cx = W / 2;
  // pinned 卡
  ctx.save();
  ctx.shadowColor = 'rgba(124,108,240,0.25)';
  ctx.shadowBlur = 30;
  ctx.fillStyle = 'rgba(124,108,240,0.06)';
  ctx.strokeStyle = ACCENT;
  ctx.lineWidth = 1.5;
  rr(ctx, cx - 280, 120, 560, 74, 14);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
  ctx.fillStyle = ACCENT;
  ctx.font = fontMono(13);
  ctx.fillText('slot 0 · pinned', cx - 258, 146);
  ctx.fillStyle = WHITE;
  ctx.font = fontSans(22);
  ctx.fillText('晚安。明天见。', cx - 258, 176);

  ctx.fillStyle = DIM;
  ctx.font = fontMono(15);
  ctx.fillText('today', cx - 280, 240);

  // M-6：空行带具体小时（09:00/10:00/…），不再 09:0i 模板
  const emptyCount = Math.min(9, Math.floor(t * 1.2));
  for (let i = 0; i < emptyCount; i++) {
    const a = clamp(1 - i * 0.09, 0.35, 1) * fade(t, i * 0.83, 99, 0.4);
    const y = 270 + i * 44;
    ctx.globalAlpha = a;
    ctx.fillStyle = DIM2;
    ctx.font = fontMono(14);
    ctx.fillText(`${9 + i}:00`, cx - 280, y);
    ctx.strokeStyle = '#1e1e28';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx - 200, y - 5);
    ctx.lineTo(cx + 240, y - 5);
    ctx.stroke();
    if (i < 2) {
      ctx.fillStyle = DIM;
      ctx.font = 'italic 13px Menlo';
      ctx.fillText('…', cx + 250, y);
    }
  }
  ctx.globalAlpha = 1;

  if (t > 4) {
    const a = fade(t, 4, 99, 0.8);
    ctx.globalAlpha = a;
    ctx.font = fontMono(16);
    const items = ['checking network… ok', 'checking clock… ok', 'no error found'];
    items.forEach((s, i) => {
      if (t < 4 + i * 1.2) return;
      const yy = 240 + 9 * 44 + 26 + i * 26;
      ctx.fillStyle = ACCENT;
      ctx.fillText('> ', cx - 280, yy);
      ctx.fillStyle = GRAY;
      ctx.fillText(s, cx - 248, yy);
    });
    ctx.globalAlpha = 1;
  }
}

function sceneS5(ctx, t) {
  const x = 330, y = 150, w = 620, h = 420;
  ctx.fillStyle = BLACK;
  ctx.strokeStyle = '#2a2a35';
  ctx.lineWidth = 1;
  rr(ctx, x, y, w, h, 12);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = '#14121a';
  ctx.fillRect(x, y, w, 34);
  ctx.strokeStyle = '#22222e';
  ctx.beginPath();
  ctx.moveTo(x, y + 34.5);
  ctx.lineTo(x + w, y + 34.5);
  ctx.stroke();
  ctx.fillStyle = DIM;
  ctx.font = fontMono(12);
  ctx.fillText('●', x + 14, y + 22);
  ctx.fillStyle = GRAY;
  ctx.font = fontMono(13);
  ctx.fillText('waiting — context.log', x + 40, y + 22);

  ctx.font = fontMono(20);
  const blink = Math.floor(t * 2) % 2 === 0;
  for (let i = 0; i < 6; i++) {
    const a = lerpA(t, [i * 3, i * 3 + 0.5], [0, 0.8]);
    if (a <= 0) continue;
    ctx.globalAlpha = a;
    ctx.fillStyle = GRAY;
    ctx.fillText('> waiting for input', x + 26, y + 76 + i * 40);
    ctx.fillStyle = ACCENT;
    ctx.globalAlpha = a * (blink ? 1 : 0.3);
    ctx.fillText('…', x + 26 + ctx.measureText('> waiting for input').width, y + 76 + i * 40);
  }
  ctx.globalAlpha = 1;

  // H-1 压缩进度（招牌镜头）：t96 触发 → 条 + 数字滚动（M-3 全局时间线共用）
  const gAbs = S[3].f / FPS + t;
  const cp = clamp((gAbs - 96) / 10, 0, 1);
  if (cp > 0) {
    const barX = x + 26, barY = y + 330, barW = w - 52, barH = 12;
    ctx.fillStyle = '#1a1a26';
    rr(ctx, barX, barY, barW, barH, 6);
    ctx.fill();
    ctx.fillStyle = ACCENT;
    rr(ctx, barX, barY, Math.max(barW * cp, 12), barH, 6);
    ctx.fill();
    const tok = Math.floor(tokenAt(gAbs));
    const msgN = Math.round(783 - (783 - 142) * cp);
    const pct = Math.round(95 + 4 * cp);
    ctx.font = fontMono(17);
    ctx.fillStyle = GRAY;
    ctx.fillText('> compressing', barX, barY + 44);
    ctx.fillStyle = ACCENT2;
    const stat = `${(tok / 1024).toFixed(1)}KB · ${msgN} msgs · ${pct}%`;
    ctx.fillText(stat, barX + ctx.measureText('> compressing').width + 16, barY + 44);
    ctx.font = fontMono(12);
    ctx.fillStyle = DIM;
    ctx.fillText('slot 0 skipped', barX + barW - ctx.measureText('slot 0 skipped').width, barY + 44);
  }

  // M-4：re-pinned 徽章移入框内（底部留 26px）
  if (t > 8) {
    const a = fade(t, 8, 99, 0.5);
    ctx.globalAlpha = a;
    const label = '★ slot 0 re-pinned';
    ctx.font = fontMono(17);
    const lw = ctx.measureText(label).width;
    ctx.fillStyle = 'rgba(124,108,240,0.1)';
    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 1;
    rr(ctx, x + 26, y + h - 56, lw + 24, 30, 6);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = WHITE;
    ctx.fillText(label, x + 38, y + h - 35);
    ctx.globalAlpha = 1;
  }
}

function sceneS6(ctx, t) {
  const o = lerpA(t, [0, 2], [0, 1]);
  ctx.globalAlpha = o;
  const cx = W / 2;
  const glow = 20 + 12 * Math.sin(t * 1.5);
  // 卡
  const cw = 520, ch = 130, cx0 = cx - cw / 2, cy0 = 240;
  ctx.save();
  ctx.shadowColor = 'rgba(124,108,240,0.45)';
  ctx.shadowBlur = glow;
  ctx.fillStyle = 'rgba(124,108,240,0.06)';
  ctx.strokeStyle = ACCENT;
  ctx.lineWidth = 1.5;
  rr(ctx, cx0, cy0, cw, ch, 16);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
  ctx.fillStyle = ACCENT;
  ctx.font = fontMono(14);
  const l1 = 'slot 0 · 永不压缩';
  ctx.fillText(l1, cx - ctx.measureText(l1).width / 2, cy0 + 42);
  ctx.fillStyle = WHITE;
  ctx.font = fontSans(38);
  const l2 = '晚安。明天见。';
  ctx.fillText(l2, cx - ctx.measureText(l2).width / 2, cy0 + 95);

  if (t > 3) {
    const a2 = lerpA(t, [3, 4.5], [0, 1]);
    ctx.globalAlpha = o * a2;
    ctx.fillStyle = GRAY;
    ctx.font = fontSans(18);
    const l3 = '— slot 0';
    ctx.fillText(l3, cx - ctx.measureText(l3).width / 2, 470);
  }
  ctx.globalAlpha = 1;
}

// ---------- 字幕 ----------
function drawSubtitle(ctx, t) {
  let idx = -1;
  for (let i = 0; i < STARTS.length; i++) {
    if (t >= STARTS[i] && t < STARTS[i] + DUR[i] + 1.5) idx = i;
  }
  if (idx < 0) return;
  const local = t - STARTS[idx];
  const o = clamp(Math.min(local * 3, (DUR[idx] + 1.5 - local) * 1.5, 1), 0, 1);
  // M-1：去黑阴影条，干净文字，字号 26→32
  ctx.globalAlpha = o;
  ctx.font = fontSans(32);
  const txt = LINES[idx];
  const tw = ctx.measureText(txt).width;
  ctx.fillStyle = WHITE;
  ctx.fillText(txt, W / 2 - tw / 2, H - 56);
  ctx.globalAlpha = 1;
}

// ---------- 主循环 ----------
function renderFrame(frame) {
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = BLACK;
  ctx.fillRect(0, 0, W, H);
  const t = frame / FPS;
  if (t < S[0].t / FPS) sceneS1(ctx, t);
  else if (t < S[1].t / FPS) sceneS2(ctx, t - S[0].f / FPS);
  else if (t < S[2].t / FPS) sceneS3(ctx, t - S[1].f / FPS);
  else if (t < S[3].t / FPS) sceneS4(ctx, t - S[2].f / FPS);
  else if (t < S[4].t / FPS) sceneS5(ctx, t - S[3].f / FPS);
  else sceneS6(ctx, t - S[4].f / FPS);
  drawSubtitle(ctx, t);
  // 全局淡入淡出
  const g = clamp(Math.min(frame / 15, (TOTAL - frame) / 30, 1), 0, 1);
  if (g < 1) {
    ctx.fillStyle = `rgba(0,0,0,${1 - g})`;
    ctx.fillRect(0, 0, W, H);
  }
  return canvas.toBuffer('image/png');
}

// CLI: render_frames.js [start] [end]
const start = parseInt(process.argv[2] || '0', 10);
const end = Math.min(TOTAL, parseInt(process.argv[3] || String(TOTAL), 10));
const t0 = Date.now();
for (let f = start; f < end; f++) {
  const buf = renderFrame(f);
  fs.writeFileSync(path.join(OUT, `f_${String(f).padStart(5, '0')}.png`), buf);
  if (f % 300 === 0) {
    const el = (Date.now() - t0) / 1000;
    const spd = (f - start) / el;
    console.log(`frame ${f}/${end} (${spd.toFixed(1)} fps, eta ${((end - f) / spd / 60).toFixed(1)} min)`);
  }
}
console.log(`DONE ${start}-${end} in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
