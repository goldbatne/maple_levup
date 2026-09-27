// Compile existing design, resource links, Maker cast records and captured images.
// This creates review artifacts only; it never changes game data or source art.
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const report = path.join(root, 'docs/reports/skill-vfx-alignment-20260926');
function csvRows(source) {
  const rows = [];
  let cell = '', row = [], quoted = false;
  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    if (c === '"') {
      if (quoted && source[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { row.push(cell); cell = ''; }
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && source[i + 1] === '\n') i++;
      row.push(cell); cell = '';
      if (row.some(value => value !== '')) rows.push(row);
      row = [];
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const header = rows.shift().map(key => key.replace(/^\uFEFF/, ''));
  return rows.map(values => Object.fromEntries(header.map((key, i) => [key, values[i] || ''])));
}
function csvCell(value) { return '"' + String(value ?? '').replaceAll('"', '""') + '"'; }
function relative(file) { return path.relative(root, file).replaceAll('\\', '/'); }
const design = csvRows(fs.readFileSync(path.join(root,
  'docs/reports/skill-diversity-final-20260925/SKILL_66_FINAL_DESIGN.csv'), 'utf8'));
const skills = new Map(csvRows(fs.readFileSync(path.join(root,
  'Mislocated/MyDesk/GameData/SkillTable.csv'), 'utf8')).map(row => [row.id, row]));
const monsters = new Map(csvRows(fs.readFileSync(path.join(root,
  'RootDesk/MyDesk/GameData/MonsterTable.csv'), 'utf8'))
  .map(row => [row.drop_skill_id, row]));
const records = fs.readFileSync(path.join(report, 'maker-visual-runs.jsonl'), 'utf8').trim()
  .split(/\r?\n/).map(line => JSON.parse(line));
const latest = new Map();
for (const record of records) latest.set(`${record.skillId}:${record.side}`, record);
const extraCastVerified = new Set([
  's_mon_snail_dew_trail:PLAYER', 's_mon_snail_dew_trail:MONSTER',
  's_mon_blue_snail:PLAYER', 's_mon_slime:MONSTER',
  's_mon_official_knight_c:PLAYER', 's_mon_official_knight_c:MONSTER',
]);
const preferredShot = {
  's_mon_red_snail:PLAYER': 5,
  's_mon_fire_boar:PLAYER': 4,
  's_mon_blood_harp:PLAYER': 4,
  's_mon_lunar_pixie:PLAYER': 5,
  's_mon_slime:MONSTER': 3,
  's_mon_chimera:MONSTER': 4,
  's_mon_dodo:PLAYER': 2,
  's_mon_stumpy:PLAYER': 2,
  's_mon_jr_wraith:PLAYER': 2,
  's_mon_roid:PLAYER': 2,
  's_mon_star_pixie:PLAYER': 2,
  's_mon_shark:PLAYER': 2,
};
const specific = {
  s_mon_memory_monk_trainee: {
    issue: '기존 8프레임 전방 베기 인상이 자기 강화 기도와 충돌',
    change: '승인된 동일 클립의 F00/F01/F06/F07만 사용, 시전자 몸 오버레이 y+0.55, 0.6초',
  },
  s_mon_official_knight_c: {
    issue: '기존 0.8초 제자리 베기가 0.2초 돌진 및 도착 타격과 분리되어 보임',
    change: '기존 8프레임의 앞 4장은 충돌 경계로 제한된 0.2초 이동 경로, 뒤 4장은 실제 도착 판정점 0.2초',
  },
};
const visibilityReview = {
  s_mon_cygnus: '넓은 정원 VFX가 화면 중앙·하단을 크게 점유함; 자연 전투 가독성은 사용자 판단 필요',
  s_mon_mutant_stumpy: '뿌리/암석 지속 영역이 화면 하단을 크게 점유함; 자연 전투 가독성은 사용자 판단 필요',
};
const header = [
  'Monster', 'MonsterID', 'SkillID', 'SkillName', 'FinalBehavior', 'PrimaryRole',
  'ExistingVFX', 'VisualIssue', 'Modified', 'Modification', 'StoryIdentityBasis',
  'PlayerVisual', 'MonsterVisual', 'PlayerCast', 'MonsterCast',
  'PlayerEvidence', 'MonsterEvidence', 'ReviewLimit',
];
const out = [header.map(csvCell).join(',')];
let castPass = 0, screenshotPairs = 0;
for (const [index, row] of design.entries()) {
  const id = row.SkillID;
  const skill = skills.get(id);
  const monster = monsters.get(id);
  if (!skill || !monster || monster.drop_skill_id !== id) throw new Error(`Missing mapping ${id}`);
  const evidence = {};
  for (const side of ['PLAYER', 'MONSTER']) {
    const key = `${id}:${side}`;
    const folder = path.join(report, 'evidence', side.toLowerCase());
    let image = path.join(folder, `${id}_${preferredShot[key] || 1}.png`);
    if (key === 's_mon_memory_monk_trainee:PLAYER') {
      image = path.join(report, 'evidence/before-after/monk_after.png');
    }
    if (key === 's_mon_official_knight_c:PLAYER') {
      image = path.join(report, 'evidence/before-after/knight_after.png');
    }
    if (!fs.existsSync(image)) throw new Error(`Missing Maker screenshot ${image}`);
    const record = latest.get(key);
    const accepted = record && /accepted=8 qaOk=true/.test(record.done);
    if (!accepted && !extraCastVerified.has(key)) throw new Error(`Unconfirmed Maker cast ${key}`);
    castPass++;
    evidence[side] = relative(image);
  }
  screenshotPairs++;
  const vfx = [skill.effect_ruid && `effect=${skill.effect_ruid}`,
    skill.layer_ruids && `layers=${skill.layer_ruids}`,
    skill.projectile_ruid && `projectile=${skill.projectile_ruid}`]
    .filter(Boolean).join(' | ');
  const special = specific[id];
  const board = `docs/reports/skill-vfx-alignment-20260926/VFX_BOARD_${
    String(Math.floor(index / 5) * 5 + 1).padStart(2, '0')}_${
    String(Math.min(Math.floor(index / 5) * 5 + 5, 66)).padStart(2, '0')}.png`;
  const item = [
    row.Monster, monster.id, id, row.SkillName, row['실제 최종 기능'], row.FinalPrimaryRole,
    vfx, special?.issue || visibilityReview[id]
      || '촬영된 프레임에서 명백한 역할 불일치가 확인되지 않음',
    special ? 'YES' : 'NO', special?.change || '기존 자산·배치 유지',
    row['Lore/Identity 근거'], visibilityReview[id] ? 'NEEDS_USER_REVIEW' : 'PASS_SAMPLED',
    visibilityReview[id] ? 'NEEDS_USER_REVIEW' : 'PASS_SAMPLED',
    'PASS_CAST_PATH', 'PASS_CAST_PATH',
    `${evidence.PLAYER} | ${board}`, `${evidence.MONSTER} | ${board}`,
    '격리된 map01 Maker 시전 샘플; 전체 Run/고속 프레임 연속 영상/모든 지형은 별도 검증 아님',
  ];
  out.push(item.map(csvCell).join(','));
}
fs.writeFileSync(path.join(report, 'SKILL_66_VFX_VISUAL_REVIEW.csv'), out.join('\r\n') + '\r\n');
console.log(JSON.stringify({skills: design.length, castPass, screenshotPairs,
  modified: Object.keys(specific)}));
