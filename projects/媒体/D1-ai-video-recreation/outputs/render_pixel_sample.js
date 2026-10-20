// render_pixel_sample.js — v0.3 像素风样片
// 风格对标参考视频1《AI会难过吗》= 像素 Windows95 桌面模拟 + 像素小女孩
// 管线：320×180 低分辨率绘制 → 4× nearest-neighbor 放大到 1280×720（像素化）
// 叙事：她每天和 AI 聊天 → 时间流逝 → 她没再来 → 结尾金句卡
// 用法：node render_pixel_sample.js [startFrame] [endFrame]
// origin: ai
const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = require('canvas');

const BW = 320, BH = 180;      // base (draw) resolution
const OW = 1280, OH = 720;     // output resolution (4x)
const FPS = 60;                // 60fps for smooth motion
const DUR = 24;                // seconds
const NFRAMES = FPS * DUR;

const FRAME_DIR = path.join(__dirname, 'frames_px');
if (!fs.existsSync(FRAME_DIR)) fs.mkdirSync(FRAME_DIR, { recursive: true });

// ---------- palette (sunset Win95) ----------
const C = {
  skyTop:    '#241a45', skyMid: '#5a2d6b', skyLow: '#b8447a',
  skyHor:    '#f2795a', sun: '#ffd27a', sunEdge: '#ff9e4a',
  cloud:     '#f7b98f', cloudDark: '#c9788f',
  mtnFar:    '#4a2a5e', mtnNear: '#33204a',
  city:      '#241636', cityWin: '#ffcf7a',
  desk:      '#c0c0c0', deskDark: '#808080', deskLight: '#ffffff',
  winBlue1:  '#00007b', winBlue2: '#1084d0',
  winGray:   '#c0c0c0', winGrayDk: '#808080', winGrayLt: '#ffffff',
  titleText: '#ffffff',
  menuBg:    '#c0c0c0',
  chatBg:    '#fdfdf4',
  txtDark:   '#2a2a2a', txtGirl: '#3a2a1e', txtAI: '#5a3d8a',
  taskbar:   '#c0c0c0', taskbarDk: '#808080',
  start:     '#00007b',
  clockBg:   '#c0c0c0',
  cursor:    '#1a1a1a',
  black:     '#0a0810',
  quote:     '#f2f0e8',
};

// ---------- canvas setup ----------
const base = createCanvas(BW, BH);
const bctx = base.getContext('2d');
const out = createCanvas(OW, OH);
const octx = out.getContext('2d');
octx.imageSmoothingEnabled = false;

// ---------- easing ----------
const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
const easeOut = x => 1-Math.pow(1-x,3);
const easeInOut = x => x<0.5 ? 4*x*x*x : 1-Math.pow(-2*x+2,3)/2;

// ---------- drawing helpers (base res) ----------
function px(x,y,w,h,color){ bctx.fillStyle=color; bctx.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h)); }
function hex2rgb(h){ h=h.replace('#',''); if(h.length===3) h=h.split('').map(c=>c+c).join(''); return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]; }
const _tmp=createCanvas(8,8); const _tctx=_tmp.getContext('2d');
function txt(x,y,str,color,font=9,align='left'){
  if(str==null||str==='') return;
  const fstr=`${font}px "PingFang SC","Hiragino Sans GB",sans-serif`;
  _tctx.font=fstr;
  const tw=Math.ceil(_tctx.measureText(str).width);
  const w=tw+2, h=Math.ceil(font*1.7)+2;
  if(w>_tmp.width) _tmp.width=w;
  if(h>_tmp.height) _tmp.height=h;
  _tctx.clearRect(0,0,w,h);
  _tctx.font=fstr; _tctx.textBaseline='top'; _tctx.fillStyle=color;
  _tctx.fillText(str,0,0);
  const img=_tctx.getImageData(0,0,w,h), d=img.data;
  let r=255,g=255,b=255; try{[r,g,b]=hex2rgb(color);}catch(e){}
  for(let i=0;i<d.length;i+=4){ if(d[i+3]>110){d[i]=r;d[i+1]=g;d[i+2]=b;d[i+3]=255;} else d[i+3]=0; }
  _tctx.putImageData(img,0,0);
  let dx=Math.round(x);
  if(align==='center') dx=Math.round(x-w/2); else if(align==='right') dx=Math.round(x-w);
  bctx.drawImage(_tmp,0,0,w,h,dx,Math.round(y),w,h);
}

// ---------- girl sprite (16 x 24) ----------
const GIRL_MAP = [
  ".....HHHHHH.....",
  "....HHHHHHHH....",
  "...HHHHHHHHHH...",
  "...HHHHHHHHHH...",
  "...HssssssssH...",
  "...HssssssssH...",
  "...HseSssSeSH...",
  "...HssssssssH...",
  "....ssssssss....",
  "....yyyyyyyy....",
  "...yyyyyyyyyy...",
  "...yyyyyyyyyy...",
  "...yyyyyyyyyy...",
  "....yyyyyyyy....",
  "....pppppppp....",
  "....pppppppp....",
  "....pp...pp.....",
  "....pp...pp.....",
  "....pp...pp.....",
  "....pp...pp.....",
  "....ss...ss.....",
  "....ss...ss.....",
  "...sss...sss....",
  "...sss...sss....",
];
const GIRL_COL = { H:'#3a2416', s:'#f2c9a0', S:'#f2c9a0', e:'#241a12', y:'#e6b83c', p:'#4a4a6a', '.':null };
function drawGirl(x,y,alpha=1){
  bctx.globalAlpha = alpha;
  for(let r=0;r<GIRL_MAP.length;r++){
    for(let c=0;c<GIRL_MAP[r].length;c++){
      const ch=GIRL_MAP[r][c]; const col=GIRL_COL[ch];
      if(col){ px(x+c, y+r, 1, 1, col); }
    }
  }
  bctx.globalAlpha = 1;
}

// ---------- wallpaper ----------
function drawWallpaper(){
  // sky gradient bands
  const bands = [
    [0,26,C.skyTop],[26,40,C.skyMid],[40,56,C.skyLow],[56,70,'#e0654f'],
    [70,82,C.skyHor],[82,90,'#f9a86a'],
  ];
  for(const [y0,y1,col] of bands) px(0,y0,BW,y1-y0,col);
  // sun (pixel circle)
  const sunY=58, sunR=11, sunCx=232;
  for(let dy=-sunR;dy<=sunR;dy++)for(let dx=-sunR;dx<=sunR;dx++){
    if(dx*dx+dy*dy<=sunR*sunR){ px(sunCx+dx, sunY+dy, 1,1, (Math.abs(dx)+Math.abs(dy)<2)?C.sun:C.sunEdge); }
  }
  // clouds
  px(40,30,26,5,C.cloud); px(50,26,14,5,C.cloud); px(150,44,30,5,C.cloud); px(162,40,16,5,C.cloud);
  // mountains (far)
  px(0,74,90,18,C.mtnFar); px(70,68,70,24,C.mtnFar);
  // mountains (near)
  for(let i=0;i<BW;i++){
    const h = 10 + Math.round(6*Math.sin(i*0.11)) + Math.round(4*Math.sin(i*0.05+1));
    px(i, 90-h, 1, h, C.mtnNear);
  }
  // city skyline
  const cityY=90;
  for(let bx=0;bx<BW;bx+=12){
    const bh = 8 + ((bx*7)%3)*4;
    px(bx, cityY-bh, 10, bh+14, C.city);
    // lit windows
    for(let wy=cityY-bh+2; wy<cityY+6; wy+=4){
      for(let wx=bx+2; wx<bx+9; wx+=4){
        if(((wx*13+wy*7)%5)<2) px(wx, wy, 2, 2, C.cityWin);
      }
    }
  }
  // ground strip
  px(0,104,BW,BH-104,'#1c1230');
}

// ---------- desktop icons ----------
function drawIcon(x,y,kind,label){
  // 16x16 icon box
  px(x,y,16,16,'#00000000');
  if(kind==='bin'){
    px(x+4,y+3,8,11,'#dfe6ee'); px(x+3,y+2,10,2,'#aab4c0'); px(x+5,y+4,6,9,'#c9d2dc');
    px(x+5,y+6,1,7,'#9aa4b0'); px(x+7,y+6,1,7,'#9aa4b0'); px(x+9,y+6,1,7,'#9aa4b0');
  } else if(kind==='pc'){
    px(x+2,y+3,12,9,'#cfd8e2'); px(x+4,y+5,8,5,'#2a3a4a'); px(x+6,y+13,4,2,'#aab4c0'); px(x+4,y+15,8,1,'#8a94a0');
  } else if(kind==='txt'){
    px(x+4,y+2,9,13,'#f6f4ea'); px(x+4,y+2,9,2,'#c9c4b0');
    for(let i=0;i<5;i++) px(x+5,y+6+i*2,7,1,'#9a947f');
  } else if(kind==='ai'){
    px(x+3,y+3,10,11,'#5a3d8a'); px(x+5,y+6,2,3,'#ffd27a'); px(x+9,y+6,2,3,'#ffd27a');
    px(x+5,y+11,6,1,'#ffd27a');
  }
  txt(x+8, y+18, label, C.deskLight, 7, 'center');
}

// ---------- chat window (Win95) ----------
function drawChatWindow(x,y,w,h, progress=1, messages=[], cursorBlink=true, title='AI'){
  // outer border
  px(x-1,y-1,w+2,h+2,C.winGrayLt);
  px(x,y,w,h,C.winGray);
  // title bar
  px(x+1,y+1,w-2,12,C.winBlue1);
  for(let i=0;i<w-2;i++){ px(x+1+i,y+1,1,12, i/ (w-2) <0.5?C.winBlue1:C.winBlue2); }
  txt(x+4,y+3,title,C.titleText,8);
  // close button
  px(x+w-9,y+3,6,8,C.winGray); px(x+w-9,y+3,6,1,C.winGrayLt);
  txt(x+w-6,y+3,'×','#000',7,'center');
  // menu bar
  px(x+1,y+13,w-2,9,C.menuBg);
  const menus=['文件','编辑','查看','帮助'];
  let mx=x+5;
  for(const m of menus){ txt(mx,y+14,m,'#000',7); mx+= 7*m.length+6; }
  // content area (clipped by progress for grow-in)
  const contentY=y+22, contentH=h-22-16;
  bctx.save();
  bctx.beginPath(); bctx.rect(x+1,contentY,w-2,contentH); bctx.clip();
  px(x+1,contentY,w-2,contentH,C.chatBg);
  // messages
  let my=contentY+4;
  for(const m of messages){
    const isGirl=m.who==='g';
    const name=isGirl?'她':'AI';
    const labelW = 7*name.length;
    txt(x+5, my, name, isGirl?C.txtGirl:C.txtAI, 7);
    // message text (already sliced by caller)
    txt(x+5+labelW+4, my, m.text, isGirl?C.txtGirl:C.txtAI, 7);
    my += 12;
  }
  // blinking cursor at end of last message
  if(cursorBlink && messages.length>0 && Math.floor(performanceNow*FPS/20)%2===0){
    const last=messages[messages.length-1];
    const lw = 7*last.text.length;
    px(x+5+ (last.who==='g'? 7*2+4:7*2+4) + lw, my-12+1, 4, 1, C.cursor);
  }
  bctx.restore();
  // input bar
  const iy=contentY+contentH+1;
  px(x+1,iy,w-2,15,C.winGray);
  px(x+3,iy+2,w-6,11,C.chatBg);
  txt(x+5,iy+3,'输入消息…','#9a9a8a',7);
}

let nowSec=0;
function performanceNow(){ return nowSec; }

// ---------- taskbar ----------
function drawTaskbar(clockText){
  const ty=BH-14;
  px(0,ty,BW,14,C.taskbar);
  px(0,ty,BW,1,C.winGrayLt);
  // start button
  px(1,ty+2,20,10,C.start);
  txt(3,ty+3,'开始','#fff',7);
  // task button
  px(23,ty+2,40,10,C.winGray); px(23,ty+2,40,1,C.winGrayLt);
  txt(26,ty+3,'AI 聊天','#000',6);
  // clock
  px(BW-32,ty+2,30,10,C.clockBg); px(BW-32,ty+2,30,1,C.winGrayLt);
  txt(BW-17,ty+3,clockText,'#000',7,'center');
}

// ---------- scene timeline ----------
// Messages for typing sequence
const MSGS=[
  {who:'g', full:'今天也还好。'},
  {who:'a', full:'我记着呢。'},
  {who:'g', full:'晚安。'},
  {who:'a', full:'晚安。明天见。'},
];

function render(fi){
  const t=fi/FPS;
  nowSec=t;
  const frame=fi;
  bctx.clearRect(0,0,BW,BH);
  bctx.fillStyle=C.black; bctx.fillRect(0,0,BW,BH);

  // ===== phase 4: ending card (t 19-24) =====
  if(t>=19){
    const a=clamp((t-19)/1,0,1);
    bctx.globalAlpha=a;
    bctx.fillStyle=C.black; bctx.fillRect(0,0,BW,BH);
    bctx.globalAlpha=1;
    txt(BW/2, 62, '上下文窗口 100 万格', C.quote, 14, 'center');
    txt(BW/2, 88, '只有一格', C.quote, 14, 'center');
    txt(BW/2, 114, '永远留给明天。', '#ffd27a', 14, 'center');
    // small pixel girl bottom
    if(a>=1) drawGirl(BW/2-8, 140, 1);
    return finish(frame);
  }

  // ===== desktop present (t 0.5+) =====
  const deskA = clamp((t-0.5)/1.2, 0, 1);
  bctx.globalAlpha = deskA;
  drawWallpaper();

  // icons (fade in staggered)
  const icons=[['bin','回收站'],['pc','我的电脑'],['txt','笔记.txt'],['ai','AI.txt']];
  let ix=8;
  for(const [kind,label] of icons){
    const ia=clamp((t-1.0 - ix*0.0)/0.6,0,1);
    if(ia>0){ bctx.globalAlpha=deskA*ia; drawIcon(ix, 14, kind, label); }
    ix+=34;
  }
  bctx.globalAlpha=deskA;

  // ===== time / clock =====
  // phase 2 (t<14): clock 9:36 -> 9:37 slowly ; phase 3 (14-19): jump to 17:00
  let clockText='9:36';
  if(t<14){ clockText = t>11 ? '9:37':'9:36'; }
  else { clockText='17:00'; }

  // ===== chat window grow-in (t 2.5-4) =====
  const winA = easeOut(clamp((t-2.5)/1.5,0,1));
  const winX=96, winY=34, winW=176, winH=104;
  const winHnow = winH*winA;

  // ===== girl: walks in at 1.8s, leaves at 15s =====
  let girlX=250, girlAlpha=0, girlY=104;
  if(t>=1.8 && t<15.5){
    // walk in from right to x=250 between 1.8-3.0, then bob; leave 15-16.5 (walk right off)
    let gx;
    if(t<3.0) gx = 320 - easeInOut((t-1.8)/1.2)*70;   // 320->250 eased
    else if(t<15.0) gx = 250 + Math.sin(t*2)*1;
    else gx = 250 + easeInOut((t-15.0)/1.5)*90;       // 250 -> 340 eased
    girlX=gx; girlAlpha = clamp(Math.min((t-1.8)/0.4, (16.5-t)/0.4),0,1);
  }

  // ===== typing messages (t 5-11) =====
  const typeStart=5, perChar=0.16, gap=0.55;
  const msgs=[];
  if(t>=typeStart){
    let ct=typeStart;
    for(const m of MSGS){
      const start=ct;
      const charsShown=clamp(Math.floor((t-start)/perChar),0,m.full.length);
      if(charsShown>0 || t>start+perChar) msgs.push({who:m.who, text:m.full.slice(0,charsShown)});
      ct=start+m.full.length*perChar+gap;
    }
  }
  const typingNow = t>=typeStart && msgs.length<MSGS.length && (t - typeStart) < (MSGS.reduce((s,m)=>s+m.full.length*perChar+gap,0));

  // window content: during phase3 (t>=14) show all msgs + a lonely blinking cursor
  const showAll = t>=14;
  const finalMsgs = showAll ? MSGS.map(m=>({who:m.who,text:m.full})) : msgs;

  if(winA>0.02){
    drawChatWindow(winX, winY, winW, winHnow, 1, finalMsgs, true, 'AI');
  }

  // girl
  if(girlAlpha>0) drawGirl(Math.round(girlX), Math.round(girlY), girlAlpha);

  // taskbar
  drawTaskbar(clockText);
  bctx.globalAlpha=1;
  return finish(frame);
}

function finish(frame){
  // upscale base -> out (nearest neighbor)
  octx.imageSmoothingEnabled=false;
  octx.clearRect(0,0,OW,OH);
  octx.drawImage(base, 0,0,BW,BH, 0,0,OW,OH);
  const f=out.toBuffer('image/png');
  const fp=path.join(FRAME_DIR, `f_${String(frame).padStart(5,'0')}.png`);
  fs.writeFileSync(fp,f);
  return fp;
}

// ---------- main ----------
const [ , , a, b ] = process.argv;
const start = a? parseInt(a):0;
const end = b? parseInt(b):NFRAMES-1;
const t0=Date.now();
for(let i=start;i<=end;i++){
  render(i);
  if((i-start)%60===0) console.log(`frame ${i}/${end}`);
}
console.log(`done ${end-start+1} frames in ${((Date.now()-t0)/1000).toFixed(1)}s -> ${FRAME_DIR}`);
