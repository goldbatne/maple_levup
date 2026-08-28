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

// ═══════════════════════════════════════════════════════════════════
// 엘리니아 5종 (T37-3). 위 11종과 같은 격자·같은 규칙.
// 스타일은 기존 넷에 물린다 — 새로 만들지 않는다 (README "스타일" 절).
// 색조는 아이콘과 맞추되 명도는 벌린다 (테두리 거의 검게, 속 거의 희게).
// ═══════════════════════════════════════════════════════════════════

// 중심에서 뻗는 광선 위에 정사각형을 늘어놓는다. 고리를 잘라 칸을 낼 때 쓴다.
const ray = (cx, cy, deg, r0, r1, w, fill) => {
  const out = [];
  const a = (deg * Math.PI) / 180;
  for (let d = r0; d <= r1; d += 0.5) {
    const x = Math.round(cx + Math.cos(a) * d), y = Math.round(cy + Math.sin(a) * d);
    out.push(r(x - Math.floor(w / 2), y - Math.floor(w / 2), w, w, fill));
  }
  return out.join('\n');
};

// ── 끈적한 몸통 (burst) — 튀는 점액 ─────────────────────────────────
// ⚠ 처음에 8방향 팔로 그렸더니 **성게**가 됐고, 같은 꼴인 뼈 무덤·물방울과
//   색만 다른 그림이 됐다 (실측). 튄 점액은 **좌우가 안 맞는 덩어리 + 흘러내리는
//   몇 가닥**이지 대칭 별이 아니다. 덩어리를 치우치게 겹치고 가닥은 넷만 뒀다.
const SLIME_FX = (() => {
  const out = [];
  const blobs = [[24, 25, 14], [15, 19, 9], [33, 20, 8], [28, 34, 9], [15, 33, 7]];
  const runs = [[-118, 23], [-32, 20], [58, 17], [140, 21]];
  // ⚠ **테두리를 전부 먼저 깔고 본체를 전부 나중에 칠한다.** 덩어리마다
  //   테두리→본체를 짝으로 그리면 뒤 가닥의 테두리가 앞 덩어리 위에 그어져
  //   **한 덩어리가 아니라 금이 간 것처럼** 보인다 (실측).
  const shape = (fill, shrink) => {
    const o = [];
    for (const [x, y, rad] of blobs) o.push(rows(disc(x, y, rad - shrink), fill));
    for (const [deg, len] of runs) {
      const a = (deg * Math.PI) / 180;
      for (let d = 8; d <= len; d += 1) {
        const t = (d - 8) / (len - 8);
        const w = Math.max(2, Math.round(7 * (1 - t * 0.75)));
        const x = Math.round(24 + Math.cos(a) * d), y = Math.round(24 + Math.sin(a) * d);
        o.push(rows(disc(x, y, w / 2 + 1 - shrink), fill));
      }
      const ex = Math.round(24 + Math.cos(a) * (len + 4));
      const ey = Math.round(24 + Math.sin(a) * (len + 4));
      o.push(rows(disc(ex, ey, 3 - shrink), fill));
    }
    return o.join('\n');
  };
  out.push(shape('#0d2405', 0));
  out.push(shape('#2e7a12', 2));
  // 젖은 광택 — 왼쪽 위에 몰아 둔다
  out.push(rows(disc(18, 19, 5), '#8cf24a'));
  out.push(rows(disc(28, 28, 4), '#8cf24a'));
  out.push(rows(disc(17, 18, 2), '#e8ffc0'));
  return out.join('\n');
})();

// ── 단단한 밑동 (ring) — 통나무 방책 ────────────────────────────────
// ⚠ 매끈한 동심 고리로 그렸더니 **강철 가죽과 같은 그림**이 됐다 (색만 다르다).
//   고리를 **열두 조각으로 잘라** 통나무를 둘러 세운 방책으로 만들었다 —
//   끊긴 자리가 나무 기둥의 경계라 철판과 실루엣부터 갈린다.
const STUMP_FX = (() => {
  const out = [];
  out.push(rows(ring(24, 24, 22, 9), '#140d06'));
  out.push(rows(ring(24, 24, 21, 7), '#3a2a1a'));
  out.push(rows(ring(24, 24, 20, 5), '#8a6a42'));
  out.push(rows(ring(24, 24, 19, 3), '#b08a5a'));
  out.push(rows(ring(24, 24, 18, 1), '#e8cfa8'));
  // 기둥 사이를 갈라 낸다 — 이게 방책으로 읽히게 하는 핵심
  for (let k = 0; k < 12; k += 1) {
    out.push(ray(24, 24, k * 30 + 15, 12, 24, 3, '#140d06'));
  }
  // 기둥마다 나이테 한 점 (아이콘과 이어지는 신호)
  for (let k = 0; k < 12; k += 1) {
    const a = ((k * 30) * Math.PI) / 180;
    const x = Math.round(24 + Math.cos(a) * 19), y = Math.round(24 + Math.sin(a) * 19);
    out.push(rows(disc(x, y, 2), '#5a4228'));
    out.push(rows(disc(x, y, 1), '#d8b585'));
  }
  return out.join('\n');
})();

// ── 물방울 터뜨리기 (burst) — 흩어지는 물보라 ───────────────────────
// ⚠ 방사형 팔로 그리면 눈꽃(뼈 무덤)이 된다. **이어지지 않은 방울들**을
//   반지름·크기를 제각각으로 흩어 놓아야 물보라로 읽힌다.
const BUBBLE_FX = (() => {
  const out = [];
  const drops = [
    [10, 21, 5], [58, 19, 4], [96, 22, 5], [132, 17, 3], [168, 21, 5],
    [205, 18, 4], [242, 22, 5], [278, 16, 3], [312, 20, 4], [340, 22, 5],
    [35, 12, 3], [120, 11, 2], [222, 12, 3], [300, 11, 2],
  ];
  for (const [deg, dist, rad] of drops) {
    const a = (deg * Math.PI) / 180;
    const x = Math.round(24 + Math.cos(a) * dist), y = Math.round(24 + Math.sin(a) * dist);
    out.push(rows(disc(x, y, rad + 1), '#062f45'));
    out.push(rows(disc(x, y, rad), '#79dcf7'));
    if (rad >= 3) out.push(rows(disc(x - 1, y - 1, Math.max(1, rad - 2)), '#d4f8ff'));
    if (rad >= 4) out.push(rows(disc(x - 1, y - 1, 1), '#ffffff'));
  }
  // 터진 자리 — 가운데만 밝게. 방울들이 여기서 흩어져 나갔다
  out.push(rows(disc(24, 24, 8), '#062f45'));
  out.push(rows(disc(24, 24, 6), '#79dcf7'));
  out.push(rows(disc(24, 24, 4), '#d4f8ff'));
  out.push(rows(disc(24, 24, 2), '#ffffff'));
  return out.join('\n');
})();

// ── 요정의 인분 (cloud) — 흩날리는 분홍 가루 ────────────────────────
const DUST_FX = (() => {
  const puffs = [[24, 25, 15], [12, 22, 9], [36, 22, 9], [19, 36, 8], [32, 35, 7], [24, 10, 8]];
  const dark = puffs.map(([x, y, rad]) => rows(disc(x, y, rad), '#4a0c2c')).join('\n');
  const body = puffs.map(([x, y, rad]) => rows(disc(x, y, rad - 2), '#ffb8de')).join('\n');
  const light = [[19, 20, 7], [29, 28, 6]].map(([x, y, rad]) => rows(disc(x, y, rad), '#ffe8f6')).join('\n');
  // 4각 반짝임 — 아이콘의 주인공이라 여기에도 넣어야 같은 스킬로 읽힌다
  const spark = (cx, cy, len) => {
    const out = [];
    for (let d = -len; d <= len; d += 1) {
      const w = Math.max(1, Math.round(3 * (1 - Math.abs(d) / len)));
      out.push(r(cx - Math.floor(w / 2), cy + d, w, 1, '#ffffff'));
      out.push(r(cx + d, cy - Math.floor(w / 2), 1, w, '#ffffff'));
    }
    return out.join('\n');
  };
  return [dark, body, light,
          spark(24, 24, 9), spark(10, 12, 5), spark(39, 15, 5),
          spark(14, 41, 4), spark(37, 39, 4)].join('\n');
})();

// ── 어둠의 손아귀 (burst) — 움켜쥐는 검은 발톱 ──────────────────────
// ⚠ 곧게 뻗은 가시로 두면 **뼈 무덤**과 같은 그림이 된다. 끝을 한쪽으로 꺾어
//   **갈고리**로 만들면 (burst가 조금 돌려 주므로) 움켜쥐는 것으로 읽힌다.
// ⚠ 다섯 개는 많다 — 가늘어져서 눈꽃이 된다. **넷으로 줄여 굵게** 세우고
//   갈고리를 크게 꺾었다. 발톱이 굵어야 손가락으로 읽힌다.
const GRIP_FX = (() => {
  const out = [];
  const arms = [[-0.71, -0.71], [0.71, -0.71], [-0.71, 0.71], [0.71, 0.71]];
  for (const [ux, uy] of arms) {
    const len = 21, steps = 14;
    const px = -uy, py = ux;    // 팔에 수직인 방향 — 이쪽으로 끝을 꺾는다
    for (let i = 2; i <= steps; i += 1) {
      const t = i / steps;
      const hook = 11 * Math.pow(Math.max(0, (t - 0.45) / 0.55), 2);
      const x = Math.round(24 + ux * len * t + px * hook);
      const y = Math.round(24 + uy * len * t + py * hook);
      const w = Math.max(2, Math.round(11 * (1 - t * 0.72)));
      out.push(rows(disc(x, y, w / 2 + 1), '#050508'));
      out.push(rows(disc(x, y, w / 2), '#241d33'));
    }
    // 발톱 끝 — 진홍
    const ex = Math.round(24 + ux * len + px * 11), ey = Math.round(24 + uy * len + py * 11);
    out.push(rows(disc(ex, ey, 3), '#050508'));
    out.push(rows(disc(ex, ey, 2), '#c81030'));
    out.push(rows(disc(ex, ey, 1), '#ff5a6e'));
  }
  // 움켜쥔 어둠
  out.push(rows(disc(24, 24, 13), '#050508'));
  out.push(rows(disc(24, 24, 10), '#5c0a1c'));
  out.push(rows(disc(24, 24, 6), '#c81030'));
  out.push(rows(disc(24, 24, 3), '#ff5a6e'));
  return out.join('\n');
})();

Object.assign(EFFECTS, {
  'fx-axe-arc': AXE_FX,
  'fx-dark-root': ROOT_FX,
  'fx-boar-charge': CHARGE_FX,
  'fx-iron-hide': IRON_FX,
  'fx-bone-burst': BONE_FX,
  'fx-fire-cloud': FIRE_FX,
  'fx-earth-rend': REND_FX,
  'fx-slime-splat': SLIME_FX,
  'fx-stump-guard': STUMP_FX,
  'fx-bubble-spray': BUBBLE_FX,
  'fx-fairy-dust': DUST_FX,
  'fx-dark-grip': GRIP_FX,
});

for (const [name, body] of Object.entries(EFFECTS)) {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100%" height="100%"\n'
    + '     style="image-rendering: pixelated; image-rendering: crisp-edges;">\n'
    + body + '\n</svg>\n';
  fs.writeFileSync(DIR + '/' + name + '.svg', svg, 'utf8');
  console.log(name);
}
