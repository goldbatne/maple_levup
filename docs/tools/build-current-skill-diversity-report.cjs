#!/usr/bin/env node
'use strict';
// Mechanical current-state report. Reads live CSV and dated Maker QA logs;
// does not edit gameplay files or reuse old runtime verdicts as current proof.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const out = path.join(root, 'docs/reports/skill-diversity-rework-20260925');
function readCsv(relative) {
  const input = fs.readFileSync(path.join(root, relative), 'utf8').replace(/^\uFEFF/, '');
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i = 0; i < input.length; i++) {
    const c = input[i];
    if (c === '"') {
      if (quoted && input[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { row.push(cell); cell = ''; }
    else if ((c === '\r' || c === '\n') && !quoted) {
      if (c === '\r' && input[i + 1] === '\n') i++;
      row.push(cell); if (row.some(Boolean)) rows.push(row);
      row = []; cell = '';
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const head = rows.shift();
  return rows.map(values => Object.fromEntries(head.map((key, i) => [key, values[i] ?? ''])));
}
function writeCsv(file, rows) {
  const keys = Object.keys(rows[0]);
  const escape = value => '"' + String(value ?? '').replace(/"/g, '""') + '"';
  fs.writeFileSync(path.join(out, file), [keys.map(escape).join(','),
    ...rows.map(row => keys.map(key => escape(row[key])).join(','))].join('\r\n') + '\r\n');
}
const lore = readCsv('docs/reports/skill-diversity-lore-rework-20260924/LORE_DESIGN_66.csv');
const before = new Map(readCsv('docs/reports/skill-diversity-rework-20260922/SKILL_BEFORE.csv')
  .map(row => [row.SkillID, row]));
const skills = new Map(readCsv('RootDesk/MyDesk/GameData/SkillTable.csv')
  .map(row => [row.id, row]));
const monsters = new Map(readCsv('RootDesk/MyDesk/GameData/MonsterTable.csv')
  .map(row => [row.id, row]));
const control = new Set(['s_mon_slime', 's_mon_squid', 's_mon_rombot', 's_mon_timer',
  's_mon_wooden_dummy', 's_mon_king_clang', 's_mon_official_knight_c',
  's_mon_tauromacis', 's_mon_zeno', 's_mon_starfish', 's_mon_eliza',
  's_mon_ancient_dark_golem', 's_mon_mutant_stumpy']);
const debuff = new Set(['s_mon_faust', 's_mon_fairy', 's_mon_homun', 's_mon_octopus']);
function primaryRole(skill) {
  if (skill.behavior === 'SHIELD') return 'DEFENSE';
  if (skill.behavior === 'BUFF') return 'BUFF';
  if (debuff.has(skill.id)) return 'DEBUFF';
  if (control.has(skill.id)) return 'CONTROL';
  if (skill.behavior === 'DASH_STRIKE') return 'DASH';
  if (skill.behavior.includes('PROJECTILE')) return 'PROJECTILE';
  if (skill.behavior === 'DAMAGE_ZONE' || skill.behavior === 'DELAYED_BLAST') return 'AREA';
  return 'DIRECT';
}
const playerUse = {
  SHIELD: '자신에게 피해 감소', BUFF: '자신에게 일시 공격 강화',
  DASH_STRIKE: '바라보는 방향으로 돌진하고 도착점 공격',
  PROJECTILE: '바라보는 방향으로 투사체 발사',
  PROJECTILE_BLAST: '투사체 착탄 지점 폭발',
  PIERCING_PROJECTILE: '바라보는 방향으로 관통 투사체',
  SPREAD_PROJECTILE: '바라보는 방향으로 산탄',
  CENTER_BURST: '시전자 주변 즉발 판정',
  FRONT_CONE: '시전자 전방 부채꼴 판정',
  LINE_STRIKE: '시전자 전방 직선 판정',
  DELAYED_BLAST: '조준 지점 예고 후 지연 판정',
  DAMAGE_ZONE: '조준 지점에 지속 영역'
};
function runtime(tag, logs) {
  const end = logs.findLastIndex(item => String(item.message).startsWith(tag + ' DONE '));
  if (end < 0) return { date: '', done: 'NOT_RUN', rows: new Map() };
  let begin = -1;
  for (let i = end; i >= 0; i--) {
    if (String(logs[i].message).startsWith(tag + ' BEGIN ')) { begin = i; break; }
  }
  if (begin < 0) return { date: '', done: 'INCOMPLETE_LOG', rows: new Map() };
  const results = new Map();
  for (const item of logs.slice(begin + 1, end)) {
    const match = String(item.message).match(/^\[[^\]]+\] ROW id=(\S+) status=(\S+)/);
    if (match) results.set(match[1], match[2]);
  }
  return { date: logs[end].dateTime, done: String(logs[end].message), rows: results };
}
let logs = [];
try {
  const response = cp.execFileSync(process.execPath,
    [path.join(root, 'docs/tools/maker-mcp-call.cjs'), 'maker_logs', '{"kind":"normal"}'],
    { cwd: root, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  logs = JSON.parse(response).logs ?? [];
} catch (error) {
  process.stderr.write('Maker logs unavailable: ' + error.message + '\n');
}
const player = runtime('[SkillRework66]', logs);
const monster = runtime('[MonsterSkillRework66]', logs);
if (lore.length !== 66) throw new Error('Expected 66 lore-linked abilities');
const rows = lore.map(row => {
  const skill = skills.get(row.SkillID), old = before.get(row.SkillID);
  const mob = monsters.get(row.MonsterID);
  if (!skill || !old || !mob || mob.drop_skill_id !== row.SkillID)
    throw new Error('Live identity mismatch: ' + row.SkillID);
  const role = primaryRole(skill);
  const secondary = skill.secondary_effect || 'NONE';
  const runtimePlayer = player.rows.get(row.SkillID) ?? 'NOT_RUN';
  const runtimeMonster = monster.rows.get(row.SkillID) ?? 'NOT_RUN';
  let reason = row.Evidence;
  if (role === 'CONTROL') reason += ' | 위치·이동 제어가 주 역할(직접 피해는 보조)';
  if (role === 'DEBUFF') reason += ' | 약화가 주 역할(직접 피해는 보조)';
  if (role === 'DEFENSE' || role === 'BUFF') reason += ' | 직접 피해 대신 사용 시점 판단';
  return {
    MonsterID: row.MonsterID, Monster: row.MonsterName,
    SkillID: row.SkillID, Skill: skill.name, PrimaryRole: role,
    SecondaryRole: secondary, BeforeBehavior: old.BeforeBehavior,
    CurrentBehavior: skill.behavior, BeforeCoefficient: old.Damage,
    CurrentCoefficient: skill.coefficient, EffectType: skill.effect_type,
    PlayerUse: playerUse[skill.behavior] + (secondary === 'NONE' ? '' : ' + ' + secondary),
    MonsterUse: (skill.behavior === 'SHIELD' || skill.behavior === 'BUFF'
      ? '몬스터 자신에게 적용' : '현재 대상 플레이어를 향해 동일 판정')
      + (secondary === 'NONE' ? '' : ' + ' + secondary),
    CurrentTooltip: skill.description, Reason: reason,
    SourceType: row.SourceType, SourceURL: row.SourceURL,
    PlayerRuntime: runtimePlayer, MonsterRuntime: runtimeMonster,
    VFXReview: 'INVOCATION_PATH_ONLY_NOT_VISUAL_CERTIFICATION'
  };
});
const counts = Object.fromEntries([...new Set(rows.map(row => row.PrimaryRole))]
  .sort().map(role => [role, rows.filter(row => row.PrimaryRole === role).length]));
const targets = { DIRECT: [14, 18], PROJECTILE: [8, 12], AREA: [6, 10],
  DASH: [6, 10], DEFENSE: [4, 8], CONTROL: [4, 8],
  BUFF: [3, 7], DEBUFF: [3, 7], SPECIAL: [0, 4] };
fs.mkdirSync(out, { recursive: true });
writeCsv('SKILL_66_CURRENT.csv', rows);
const summary = [
  '# 스킬 다양성 개편 현행 결과', '',
  '원본 프로젝트 `D:/maplestory_levup`의 현재 SkillTable/MonsterTable과 이전 66종 분석·원작 대조표에서 기계적으로 생성했다. 이 보고서 생성기는 게임 파일을 수정하지 않는다.',
  '', `행 수: ${rows.length}. PrimaryRole은 중복 없는 주 역할이며 SecondaryRole은 별도 집계한다.`,
  '', '| 주 역할 | 현행 | 요청 목표(±2) | 판정 |', '|---|---:|---:|---|',
  ...Object.entries(targets).map(([key, [minimum, maximum]]) => {
    const actual = counts[key] ?? 0;
    return `| ${key} | ${actual} | ${minimum}–${maximum} | ${actual >= minimum && actual <= maximum ? '범위 안' : '목표 이탈'} |`;
  }),
  '', '이전 감사 기준에는 `CENTER_DIRECT`가 44/66이었다(`SKILL_BEFORE.csv`). 현행은 중심 즉발 `CENTER_BURST` 5/66이며, 방향·지연·지속·투사체·돌진·방어/강화/제어 판정으로 분화했다. 다만 현행 DIRECT 19, BUFF 1, CONTROL 13은 요청 목표 범위 밖이다. 숫자만 맞추기 위한 역할 재명명은 하지 않았다.',
  '', '이번 후속 보완에서 바뀐 핵심 역할: 북치는 토끼는 북 연주 공격 강화, 추억의 수호대장·셰이드는 시전자 방어, 슬라임은 점성 감속, 불가사리는 회전 가시 밀기, 엘리쟈는 폭풍 감속, 에인션트 다크골렘은 지진 기절, 변형 스텀피는 뿌리 감속이다. 그 밖의 상태 중심 피해 조정과 66종별 전후 값은 `SKILL_66_CURRENT.csv`를 참조한다.',
  '', '재검증 중 엘리쟈의 PULL·고대 골렘의 KNOCKBACK은 단일 표적을 폭발 중심에 자동 조준할 때 이동 방향 벡터가 0이라 핵심 제어가 발동하지 않는 문제가 드러났다. 검수만 완화하지 않고 중심 표적에도 적용되는 SLOW/STUN으로 실제 데이터를 고친 뒤 66종을 재실행했다.',
  '', `Player Maker QA: ${player.done} (${player.date || '시각 미확인'})`,
  `MONSTER_SKILL Maker QA: ${monster.done} (${monster.date || '시각 미확인'})`,
  '', 'QA는 실제 UseSkill/CastSkill 호출, 효과·슬롯·쿨다운 경로의 어댑터 실행 검증이다. 몬스터 66종 각각의 자연 AI 시전, 모든 VFX 프레임의 육안 승인, 실제 전투 체감/밸런스 인증은 아니다.',
  '', '원작 출처는 행별 SourceType/SourceURL 참조. COMMUNITY_WIKI 항목은 공식 Nexon 원문이 아닌 2차 자료이며 발행·업데이트 시점은 미확인이다. PROJECT_ONLY 모티브는 원작 사실로 간주하지 않는다.',
  '', '설정·아트 근거가 빈약한 역할을 목표 수치에 맞추기 위해 억지로 추가하지 않았다. 주 역할 분포의 목표 이탈은 미해결 설계 항목으로 남는다.', ''
].join('\n');
fs.writeFileSync(path.join(out, 'STATUS.md'), summary);
process.stdout.write(JSON.stringify({ out, counts, player: player.done,
  monster: monster.done, playerRows: player.rows.size,
  monsterRows: monster.rows.size }) + '\n');
