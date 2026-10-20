// v1.0 overlap auditor: replicate element placements, report overlaps per scene.
// Same geometry as render_full_pixel.js (BW=320, BH=180 base, SCALE=4).
const BW = 320, BH = 180;

function clawdBox(x, y) { return [x, y, 20, 9]; }        // body 20x9 + legs below
function fatFishBox(x, y) { return [x, y, 24, 14]; }      // fat oval + fins
function herBox(x, y) { return [x, y, 16, 30]; }
function noteBox(x, y) { return [x, y, 44, 26]; }
function textLine(x, y, len, px) { return [x - len * px / 2, y - 5, len * px, 10]; }

function overlap(a, b) {
  return a[0] < b[0] + b[2] && a[0] + a[2] > b[0] && a[1] < b[1] + b[3] && a[1] + a[3] > b[1];
}
function interArea(a, b) {
  const w = Math.min(a[0] + a[2], b[0] + b[2]) - Math.max(a[0], b[0]);
  const h = Math.min(a[1] + a[3], b[1] + b[3]) - Math.max(a[1], b[1]);
  return w > 0 && h > 0 ? w * h : 0;
}

const scenes = {
  S2: [
    ['her', herBox(5, 100)], ['clawd', clawdBox(BW - 42, 100)], ['note', noteBox(242, 29)],
    ['inputBar', [24, 130, BW - 48, 8]],
    ['msg1', [28, 42, 120, 14]], ['msg2', [28, 60, 140, 14]], ['msg3', [28, 78, 160, 14]],
  ],
  S3: [
    ['codePanel', [12, 8, BW - 24, 134]],
    ['code1', [34, 12, 150, 10]], ['code2', [34, 26, 160, 10]],
    ['slotBar', [BW - 110, 96, 96, 10]], ['slotLabel', [BW - 110, 84, 30, 10]],
  ],
  S4: [
    ['pinned', [26, 30, BW - 60, 15]],
    ['battery', [28, 126, 60, 10]], ['slotBar', [BW - 60, 128, 30, 8]],
    ['clawd', clawdBox(BW - 44, 104)], ['emptyLines', [28, 52, 230, 56]],
  ],
  S5: [
    ['waitTxt', [14, 34, 140, 12]], ['tokens', [14, 54, 90, 10]],
    ['compress', [14, 64, 110, 10]], ['pinAnim', [14, 74, 130, 10]],
    ['waitLog', [14, 94, 140, 40]], ['fatfish', fatFishBox(BW - 50, 56)],
  ],
  S6: [
    ['golden', textLine(BW / 2, 56, 8, 10)], ['slot0', textLine(BW / 2, 86, 9, 10)],
    ['forever', textLine(BW / 2, 100, 6, 8)],
    ['clawd', clawdBox(BW / 2 - 7, 112)], ['note', noteBox(28, 86)], ['her', herBox(264, 86)],
  ],
  CARD: [
    ['card', [BW - 200, BH - 80, 180, 50]], ['cardTxt', [BW - 200, BH - 75, 180, 12]],
    ['tape', [BW - 115, BH - 84, 30, 8]],
  ],
};

for (const [name, els] of Object.entries(scenes)) {
  console.log(`\n=== ${name} ===`);
  let found = false;
  for (let i = 0; i < els.length; i++) {
    for (let j = i + 1; j < els.length; j++) {
      const a = els[i][1], b = els[j][1];
      if (overlap(a, b)) {
        const area = interArea(a, b);
        const small = Math.min(a[2] * a[3], b[2] * b[3]);
        console.log(`  OVERLAP: ${els[i][0]} ${JSON.stringify(a)} x ${els[j][0]} ${JSON.stringify(b)}  inter=${area}px (${Math.round(100 * area / small)}% of smaller)`);
        found = true;
      }
    }
  }
  if (!found) console.log('  no overlaps');
}
