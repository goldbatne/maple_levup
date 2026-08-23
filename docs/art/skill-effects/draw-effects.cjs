// 몬스터 스킬의 **시전 이펙트** 그림 (T21-1).
//
// 아이콘(docs/art/skill-icons)과 같은 방식으로 직접 그린다. 다른 점은 두 가지:
//
//   1) 월드에 뜨는 그림이라 UI 아이콘보다 크다 — 48x48 격자를 96x96으로 뽑는다.
//   2) **한 장짜리다.** 애니메이션은 스크립트가 만든다(커지고·옅어지고·돈다).
//      `asset_create_account_resource_storage_item`이 받는 category가
//      sprite / audioclip / avataritem뿐이라 **animationclip은 못 올린다.**
//      여러 장을 올려 프레임을 갈아끼우는 길도 있지만, 4종 x 5장 = 20장을
//      올려야 하고 그림마다 프레임 수를 따로 관리해야 한다. 한 장 + 움직임이
//      싸고, 되돌리기도 쉽다.
//
// 팔레트는 아이콘과 맞춘다 — 같은 스킬인데 아이콘과 이펙트의 색이 다르면
// 무엇이 터진 건지 연결이 안 된다.

const fs = require('fs');
const DIR = __dirname;

const r = (x, y, w, h, f) => `  <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${f}"/>`;
const rows = (list, fill) => list.map(([y, a, b]) => r(a, y, b - a + 1, 1, fill)).join('\n');

// 가운데 (24,24) 기준으로 그린다. 반지름 rad인 원의 각 행 폭.
const disc = (cx, cy, rad) => {
  const out = [];
  for (let y = Math.ceil(cy - rad); y <= Math.floor(cy + rad); y += 1) {
    const dy = y - cy;
    const dx = Math.floor(Math.sqrt(Math.max(rad * rad - dy * dy, 0)));
    if (dx <= 0) continue;
    out.push([y, cx - dx, cx + dx]);
  }
  return out;
};
// 두께 t인 고리 = 큰 원에서 작은 원을 뺀 행들.
const ring = (cx, cy, rad, t) => {
  const outer = new Map(disc(cx, cy, rad).map(([y, a, b]) => [y, [a, b]]));
  const inner = new Map(disc(cx, cy, rad - t).map(([y, a, b]) => [y, [a, b]]));
  const out = [];
  for (const [y, [a, b]] of outer) {
    const hole = inner.get(y);
    if (hole === undefined) { out.push([y, a, b]); continue; }
    out.push([y, a, hole[0] - 1]);
    out.push([y, hole[1] + 1, b]);
  }
  return out.filter(([, a, b]) => b >= a);
};

// ── 몸통 박치기 — 부딪히는 충격 ─────────────────────────────────────
// 별 모양으로 터진다. 아이콘의 노란 불꽃과 같은 색.
const IMPACT = (() => {
  const spikes = [];
  // 8방향 삐죽한 가시. 길이를 번갈아 둬야 별처럼 보인다.
  const arms = [
    [0, -22], [0, 22], [-22, 0], [22, 0],
    [-14, -14], [14, -14], [-14, 14], [14, 14],
  ];
  for (const [dx, dy] of arms) {
    const steps = 12;
    for (let i = 0; i <= steps; i += 1) {
      const t = i / steps;
      const x = Math.round(24 + dx * t);
      const y = Math.round(24 + dy * t);
      const w = Math.max(1, Math.round(5 * (1 - t)));
      spikes.push(r(x - Math.floor(w / 2), y - Math.floor(w / 2), w, w, '#ffc61e'));
    }
  }
  return [
    spikes.join('\n'),
    rows(disc(24, 24, 9), '#ffc61e'),
    rows(disc(24, 24, 7), '#fff3b0'),
    rows(disc(24, 24, 4), '#ffffff'),
  ].join('\n');
})();

// ── 푸른 껍질 — 감싸는 방어막 ───────────────────────────────────────
// 아이콘의 좌우 괄호를 고리로 키운 것. 커지며 옅어진다.
const GUARD = [
  rows(ring(24, 24, 22, 3), '#2f6bd0'),
  rows(ring(24, 24, 21, 1), '#6ea8f5'),
  rows(ring(24, 24, 16, 2), '#6ea8f5'),
  rows(ring(24, 24, 15, 1), '#dff0ff'),
  // 고리 위의 반짝임 넷
  rows([[3, 23, 25], [4, 22, 26], [5, 23, 25]], '#dff0ff'),
  rows([[43, 23, 25], [44, 22, 26], [45, 23, 25]], '#dff0ff'),
  rows([[23, 3, 5], [24, 2, 6], [25, 3, 5]], '#dff0ff'),
  rows([[23, 43, 45], [24, 42, 46], [25, 43, 45]], '#dff0ff'),
].join('\n');

// ── 포자 살포 — 퍼지는 포자 구름 ────────────────────────────────────
// 덩어리 여러 개를 겹쳐 뭉게뭉게 만든다. 아이콘의 초록 그대로.
const SPORE = (() => {
  const puffs = [
    [24, 24, 15], [13, 20, 9], [35, 21, 9], [20, 34, 8], [33, 33, 7], [24, 11, 8],
  ];
  // ⚠ 색을 아이콘과 똑같이(#425c14 / #a8d24a) 뒀더니 **잔디 위에서 묻혔다**(실측).
  //   이펙트는 아이콘과 달리 아무 배경 위에나 뜨므로 **명도 대비**로 버텨야 한다 —
  //   테두리는 거의 검게, 속은 거의 흰 노랑으로 벌린다. 색조(초록)는 그대로 둔다.
  const dark = puffs.map(([x, y, rad]) => rows(disc(x, y, rad), '#20300a')).join('\n');
  const body = puffs.map(([x, y, rad]) => rows(disc(x, y, rad - 2), '#b8dc4e')).join('\n');
  const light = [[18, 19, 7], [28, 27, 6]].map(([x, y, rad]) => rows(disc(x, y, rad), '#f2ffb0')).join('\n');
  // 흩날리는 알갱이
  const motes = rows([[4, 8, 9], [6, 38, 39], [41, 10, 11], [44, 30, 31], [9, 43, 44]], '#20300a');
  return [dark, body, light, motes].join('\n');
})();

// ── 뿔 들이받기 — 꿰뚫는 획 ─────────────────────────────────────────
// 오른쪽으로 뻗는 뾰족한 획. 서버가 FlipX로 방향을 맞춘다.
const PIERCE = (() => {
  // ⚠ 처음엔 가운데가 제일 두꺼운 방추형으로 그렸더니 **렌즈(눈알)처럼** 보였다.
  //    찌르는 것은 **앞이 뾰족하고 뒤로 길게 끌리는** 모양이어야 한다.
  const out = [];
  const TIP = 45, TAIL = 3;
  for (let x = TAIL; x <= TIP; x += 1) {
    const t = (x - TAIL) / (TIP - TAIL);        // 0 = 꼬리, 1 = 끝
    // 뒤는 가늘게 시작해 2/3 지점에서 가장 두껍고, 끝은 한 점으로 모인다.
    let h;
    if (t < 0.7) h = 1 + Math.round(8 * (t / 0.7));
    else h = Math.max(1, Math.round(9 * (1 - (t - 0.7) / 0.3)));
    const y = Math.round(24 - h / 2);
    out.push(r(x, y, 1, h, '#2f2410'));
  }
  for (let x = TAIL + 1; x <= TIP - 1; x += 1) {
    const t = (x - TAIL) / (TIP - TAIL);
    let h;
    if (t < 0.7) h = 1 + Math.round(8 * (t / 0.7)) - 2;
    else h = Math.round(9 * (1 - (t - 0.7) / 0.3)) - 2;
    if (h <= 0) continue;
    const y = Math.round(24 - h / 2);
    out.push(r(x, y, 1, h, '#ead8b0'));
  }
  // 속이 밝게 달아오른 심지
  out.push(r(14, 24, 26, 1, '#fff3b0'));
  // 뒤로 끌리는 잔상
  out.push(rows([[19, 2, 8], [29, 4, 10]], '#c9b184'));
  // 끝에서 튀는 불꽃
  out.push(rows([[20, 46, 47], [24, 46, 47], [28, 46, 47]], '#ffc61e'));
  return out.join('\n');
})();

const EFFECTS = {
  'fx-snail-impact': IMPACT,
  'fx-blueshell-guard': GUARD,
  'fx-spore-cloud': SPORE,
  'fx-horn-pierce': PIERCE,
};

for (const [name, body] of Object.entries(EFFECTS)) {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"\n'
    + '     style="image-rendering: pixelated; image-rendering: crisp-edges;">\n'
    + body + '\n</svg>\n';
  fs.writeFileSync(DIR + '/' + name + '.svg', svg, 'utf8');
  console.log(name);
}
