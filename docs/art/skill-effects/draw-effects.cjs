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


// ═══════════════════════════════════════════════════════════════════
// 페리온 7종 (T32-3). 위 4종과 같은 격자·같은 규칙.
// ⚠ **명도 대비로 버틴다** — 테두리는 거의 검게, 속은 거의 희게.
//   색조는 아이콘과 맞추되(같은 스킬로 읽혀야 한다) 명도는 벌린다.
// ═══════════════════════════════════════════════════════════════════

// 행 목록에서 사각형 밖을 잘라낸다. 호(arc)를 만들 때 쓴다.
const clip = (list, x0, x1, y0, y1) => list
  .filter(([y]) => y >= y0 && y <= y1)
  .map(([y, a, b]) => [y, Math.max(a, x0), Math.min(b, x1)])
  .filter(([, a, b]) => b >= a);

// ── 도끼 휘두르기 (burst) — 휘두른 은빛 호 ──────────────────────────
const AXE_FX = [
  // C자 호 — 오른쪽이 열린 초승달. 가운데(24,24) 기준이라 커져도 안 쏠린다.
  rows(clip(ring(24, 24, 21, 7), 2, 34, 2, 46), '#1a1c24'),
  rows(clip(ring(24, 24, 20, 4), 3, 33, 4, 44), '#c8cfdc'),
  rows(clip(ring(24, 24, 19, 2), 4, 32, 5, 43), '#f7f9ff'),
  // 호 바깥의 호박빛 잔상 — 휘두른 자취
  rows(clip(ring(24, 24, 25, 2), 3, 36, 3, 45), '#e0a33c'),
  // 날이 지나간 끝에서 튀는 불꽃 (위·아래 끝)
  rows([[3, 24, 28], [4, 26, 30], [5, 28, 31]], '#ffe08a'),
  rows([[44, 24, 28], [43, 26, 30], [42, 28, 31]], '#ffe08a'),
].join('\\n');

const ROOT_FX = (() => {
  const out = [];
  // 뿌리 다섯 가닥. 아래(y=46)에서 시작해 위로 갈수록 가늘어지고 옆으로 휜다.
  const stalks = [[24, 0, 42], [14, -7, 34], [34, 7, 34], [8, -12, 26], [40, 12, 26]];
  for (const [x0, bend, len] of stalks) {
    for (let i = 0; i <= len; i += 1) {
      const t = i / len;
      const x = Math.round(x0 + bend * t * t);
      const y = 46 - i;
      const w = Math.max(1, Math.round(5 * (1 - t) + 1));
      out.push(r(x - Math.floor(w / 2) - 1, y, w + 2, 1, '#0d0616'));   // 테두리
      out.push(r(x - Math.floor(w / 2), y, w, 1, '#4a2270'));           // 본체
      if (i % 4 === 0) out.push(r(x, y, 1, 1, '#b45cf0'));              // 마디 빛
    }
    // 끝에서 터지는 보라 기운
    const tx = Math.round(x0 + bend), ty = 46 - len;
    out.push(rows(disc(tx, ty - 2, 4), '#0d0616'));
    out.push(rows(disc(tx, ty - 2, 3), '#b45cf0'));
    out.push(rows(disc(tx, ty - 2, 1), '#efc6ff'));
  }
  return out.join('\n');
})();

// ── 저돌 맹진 (pierce) — 앞으로 밀고 나가는 쐐기 ────────────────────
const CHARGE_FX = (() => {
  const out = [];
  const TIP = 45, TAIL = 2;
  for (let x = TAIL; x <= TIP; x += 1) {
    const t = (x - TAIL) / (TIP - TAIL);
    let h;
    if (t < 0.75) h = 1 + Math.round(11 * (t / 0.75));
    else h = Math.max(1, Math.round(12 * (1 - (t - 0.75) / 0.25)));
    out.push(r(x, Math.round(24 - h / 2), 1, h, '#1a0805'));
  }
  for (let x = TAIL + 1; x <= TIP - 1; x += 1) {
    const t = (x - TAIL) / (TIP - TAIL);
    let h;
    if (t < 0.75) h = 1 + Math.round(11 * (t / 0.75)) - 2;
    else h = Math.round(12 * (1 - (t - 0.75) / 0.25)) - 2;
    if (h <= 0) continue;
    out.push(r(x, Math.round(24 - h / 2), 1, h, '#c25f38'));
  }
  // 달아오른 심지
  out.push(r(12, 24, 30, 1, '#ffe08a'));
  out.push(r(18, 23, 20, 1, '#f2ead4'));
  out.push(r(18, 25, 20, 1, '#f2ead4'));
  // 뒤로 끌리는 속도선 (돌진이라 길게)
  out.push(rows([[16, 0, 12], [17, 0, 9], [31, 0, 12], [32, 0, 9]], '#8c3a22'));
  out.push(rows([[16, 0, 6], [31, 0, 6]], '#c25f38'));
  // 앞에서 터지는 흙먼지
  out.push(rows([[18, 45, 47], [24, 46, 47], [30, 45, 47]], '#ffc61e'));
  return out.join('\n');
})();

// ── 강철 가죽 (ring) — 철빛 방어 고리 + 금 리벳 ─────────────────────
const IRON_FX = [
  rows(ring(24, 24, 22, 4), '#161c26'),
  rows(ring(24, 24, 21, 2), '#93a8c0'),
  rows(ring(24, 24, 20, 1), '#eef4ff'),
  rows(ring(24, 24, 15, 3), '#161c26'),
  rows(ring(24, 24, 14, 1), '#5a6e86'),
  // 금 리벳 넷 (위·아래·좌·우) — 아이콘의 리벳과 같은 색이라 같은 스킬로 읽힌다
  rows(disc(24, 3, 3), '#3a2a08'), rows(disc(24, 3, 2), '#ffe08a'),
  rows(disc(24, 45, 3), '#3a2a08'), rows(disc(24, 45, 2), '#ffe08a'),
  rows(disc(3, 24, 3), '#3a2a08'), rows(disc(3, 24, 2), '#ffe08a'),
  rows(disc(45, 24, 3), '#3a2a08'), rows(disc(45, 24, 2), '#ffe08a'),
].join('\n');

// ── 뼈 무덤 (burst) — 방사형으로 솟구치는 뼈 ────────────────────────
const BONE_FX = (() => {
  const out = [];
  const arms = [[0, -23], [0, 23], [-23, 0], [23, 0],
                [-16, -16], [16, -16], [-16, 16], [16, 16]];
  for (const [dx, dy] of arms) {
    const steps = 14;
    for (let i = 3; i <= steps; i += 1) {
      const tt = i / steps;
      const x = Math.round(24 + dx * tt), y = Math.round(24 + dy * tt);
      const w = Math.max(1, Math.round(6 * (1 - tt * 0.6)));
      out.push(r(x - Math.floor(w / 2) - 1, y - Math.floor(w / 2) - 1, w + 2, w + 2, '#241c2c'));
      out.push(r(x - Math.floor(w / 2), y - Math.floor(w / 2), w, w, '#ecead8'));
    }
    // 뼈 끝 마디 (두 갈래)
    const ex = Math.round(24 + dx), ey = Math.round(24 + dy);
    out.push(rows(disc(ex, ey, 3), '#241c2c'));
    out.push(rows(disc(ex, ey, 2), '#fffdf2'));
  }
  // 가운데 자주빛 기운
  out.push(rows(disc(24, 24, 11), '#2a0a1e'));
  out.push(rows(disc(24, 24, 9), '#a3266f'));
  out.push(rows(disc(24, 24, 5), '#ecead8'));
  out.push(rows(disc(24, 24, 2), '#ffffff'));
  return out.join('\n');
})();

// ── 화염 돌풍 (cloud) — 부풀어 오르는 불길 ──────────────────────────
const FIRE_FX = (() => {
  const puffs = [[24, 26, 16], [12, 24, 10], [36, 24, 10], [19, 12, 9], [31, 13, 8], [24, 38, 9]];
  const dark = puffs.map(([x, y, rad]) => rows(disc(x, y, rad), '#3a0a02')).join('\n');
  const body = puffs.map(([x, y, rad]) => rows(disc(x, y, rad - 2), '#e85a12')).join('\n');
  const mid = [[24, 26, 11], [17, 20, 6], [30, 20, 6]].map(([x, y, rad]) => rows(disc(x, y, rad), '#ffb020')).join('\n');
  const core = [[24, 26, 6], [24, 17, 4]].map(([x, y, rad]) => rows(disc(x, y, rad), '#ffef9e')).join('\n');
  // 흩날리는 불티 — "돌풍"을 말한다
  const motes = rows([[4, 6, 8], [7, 40, 42], [42, 8, 10], [45, 34, 36], [2, 22, 24]], '#e85a12');
  return [dark, body, mid, core, motes].join('\n');
})();

// ── 대지 가르기 (burst) — 가로로 터지는 균열 충격파 ─────────────────
const REND_FX = (() => {
  const out = [];
  // 가로로 터지는 균열 — 가운데가 가장 두껍다. 이게 주인공이라 크게 잡는다.
  for (let x = 0; x <= 47; x += 1) {
    const tt = Math.abs(x - 24) / 24;
    const h = Math.max(1, Math.round(19 * (1 - tt * tt)));
    out.push(r(x, Math.round(24 - h / 2) - 1, 1, h + 2, '#120c06'));
  }
  for (let x = 3; x <= 44; x += 1) {
    const tt = Math.abs(x - 24) / 21;
    const h = Math.max(1, Math.round(14 * (1 - tt * tt)));
    out.push(r(x, Math.round(24 - h / 2), 1, h, '#9c7038'));
  }
  for (let x = 6; x <= 41; x += 1) {
    const tt = Math.abs(x - 24) / 18;
    const h = Math.max(1, Math.round(9 * (1 - tt * tt)));
    out.push(r(x, Math.round(24 - h / 2), 1, h, '#ffc61e'));
  }
  out.push(r(11, 24, 26, 1, '#fff3b0'));
  out.push(r(15, 23, 18, 1, '#fff3b0'));
  // 튀어 오르는 흙 파편 — 위로만, 크기도 제각각이라 장식으로 안 보인다
  const chunks = [[9, 13, 4], [17, 6, 3], [26, 9, 5], [34, 5, 3], [40, 14, 4], [21, 15, 2]];
  for (const [x, y, rad] of chunks) {
    out.push(rows(disc(x, y, rad), '#3d2a14'));
    out.push(rows(disc(x, y, rad - 1), '#9c7038'));
    if (rad >= 4) out.push(rows(disc(x, y - 1, 1), '#e8c07a'));
  }
  // 아래로 떨어지는 부스러기 (적게)
  out.push(rows([[38, 12, 14], [41, 30, 31], [44, 20, 21]], '#3d2a14'));
  return out.join('\\n');
})();

Object.assign(EFFECTS, {
  'fx-axe-arc': AXE_FX,
  'fx-dark-root': ROOT_FX,
  'fx-boar-charge': CHARGE_FX,
  'fx-iron-hide': IRON_FX,
  'fx-bone-burst': BONE_FX,
  'fx-fire-cloud': FIRE_FX,
  'fx-earth-rend': REND_FX,
});

for (const [name, body] of Object.entries(EFFECTS)) {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"\n'
    + '     style="image-rendering: pixelated; image-rendering: crisp-edges;">\n'
    + body + '\n</svg>\n';
  fs.writeFileSync(DIR + '/' + name + '.svg', svg, 'utf8');
  console.log(name);
}
