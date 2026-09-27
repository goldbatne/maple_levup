// Final design inventory. Reads the frozen pre-change CSV and live SkillTable;
// does not mutate game content or reuse old Maker QA as fresh evidence.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const {parseCsv} = require('./verify-current-content.cjs');
const root = path.resolve(__dirname, '../..');
const output = path.join(root, 'docs/reports/skill-diversity-final-20260925');
const after = process.argv.find(value => value.startsWith('--after='))?.slice(8);
if (!after) throw Error('Pass --after=YYYY-MM-DDTHH:MM:SS for this Maker build');

function read(rel) { return parseCsv(fs.readFileSync(path.join(root, rel), 'utf8')); }
function esc(value) { return '"' + String(value ?? '').replace(/"/g, '""') + '"'; }
const before = read('docs/reports/skill-diversity-rework-20260925/SKILL_66_CURRENT.csv');
const lore = new Map(read('docs/reports/skill-diversity-lore-rework-20260924/LORE_DESIGN_66.csv')
  .map(item => [item.SkillID, item]));
const skills = new Map(read('RootDesk/MyDesk/GameData/SkillTable.csv').map(item => [item.id, item]));
const monsters = new Map(read('RootDesk/MyDesk/GameData/MonsterTable.csv').map(item => [item.id, item]));
if (before.length !== 66 || lore.size !== 66) throw Error('Current/lore baseline is not 66');
const control = new Set(['s_mon_slime','s_mon_rombot','s_mon_timer','s_mon_wooden_dummy',
  's_mon_king_clang','s_mon_tauromacis','s_mon_zeno','s_mon_starfish',
  's_mon_ancient_dark_golem']);
const debuff = new Set(['s_mon_faust','s_mon_fairy','s_mon_homun','s_mon_octopus']);
const areaCorrected = new Set(['s_mon_squid']);
function role(skill) {
  if (skill.behavior === 'SHIELD') return 'DEFENSE';
  if (skill.behavior === 'BUFF') return 'BUFF';
  if (debuff.has(skill.id)) return 'DEBUFF';
  if (control.has(skill.id)) return 'CONTROL';
  if (skill.behavior === 'DASH_STRIKE') return 'DASH';
  if (skill.behavior.includes('PROJECTILE')) return 'PROJECTILE';
  if (skill.behavior === 'DAMAGE_ZONE' || skill.behavior === 'DELAYED_BLAST'
    || areaCorrected.has(skill.id)) return 'AREA';
  return 'DIRECT';
}
const changed = {
  s_mon_mushroom: ['포자 구름은 전방 일격보다 위치를 미리 차지하는 장판으로 읽힌다. 원작의 포자 능력은 확인되지 않은 프로젝트 스킬 설정이다.', 'NO', '현행 포자 구름 8프레임이 0.75초 세 타격 구간을 덮는다.'],
  s_mon_eliza: ['수호자 엘리쟈의 정원 폭풍을 지연 1회 둔화 대신 지속 공간 압박으로 전환했다. 폭풍은 프로젝트 스킬 설정이다.', 'NO', '현행 회오리 12프레임(1.2초)이 0.85초 판정을 덮는다.'],
  s_mon_mutant_stumpy: ['검은 뿌리/묘지라는 프로젝트 소재를 단발 둔화보다 반복 발생하는 뿌리 지대로 해석했다.', 'NO', '현행 뿌리 12프레임(1.2초)이 1.0초 판정을 덮는다.'],
  s_mon_official_knight_c: ['기사의 뇌전 연각은 제자리 넉백보다 몸을 실은 돌진/도착점 공격이 자연스럽다.', 'YES', '현행 시전자 위치의 전방 번개 베기를 돌진 이동 중/도착점에서 이어 보이게 할 위치 연출 검토가 필요하다.'],
  s_mon_memory_monk_trainee: ['시간의 신전 신관과 프로젝트의 기도파 소재를 기도 후 다음 한 번의 타격 강화로 해석했다. 원작의 확정 버프라고 주장하지 않는다.', 'YES', '현행 전방 직선 파동은 자기 강화와 다르게 읽힌다. 다음 VFX 단계에서 시전자 중심 기도 표시가 필요하다.'],
  s_mon_squid: ['기존 세 틱 먹물 장판+둔화는 제어만이 아니라 공간 배치가 주 판단이다. 기능은 보존하고 PrimaryRole 분류 오류를 바로잡았다.', 'NO', '현행 먹물 구름과 지속 영역이 대응한다.']
};
const retained = {
  s_mon_slime:'끈적임 때문에 근접 전방 둔화가 핵심이다.',
  s_mon_starfish:'회전 가시의 주변 밀치기는 포위 탈출 판단을 만든다.',
  s_mon_rombot:'중력파의 자기 중심 당기기는 적을 모을 때 의미가 있다.',
  s_mon_timer:'시계의 짧은 정지는 예고 지점의 행동 차단이 중심이다.',
  s_mon_wooden_dummy:'수련 목인의 제자리 회전은 접근한 무리를 밀어낸다.',
  s_mon_king_clang:'집게 파도의 전방 밀치기는 안전 거리 확보가 핵심이다.',
  s_mon_tauromacis:'낙뢰 예고 후 짧은 기절은 수문장 제어 정체성과 맞는다.',
  s_mon_zeno:'반복 당김 중력장은 적 위치 재배열이 핵심이다.',
  s_mon_ancient_dark_golem:'고대 지진은 예고 후 짧은 기절이 핵심이다.',
  s_mon_snail_dew_trail:'이슬길의 전방 직선은 수평 배치 적을 노리는 판단이다.',
  s_mon_mano:'무지개 파동의 시전자 주변 확산은 근접 압박 때만 가치가 있다.',
  s_mon_mushmom:'포자 충격의 시전자 주변 폭발은 접근 타이밍을 요구한다.',
  s_mon_axe_stump:'도끼 베기는 붙어서 방향을 맞추는 근접 공격이다.',
  s_mon_skeleton_commander:'뼈 무덤의 직선은 앞줄을 관통하는 방향 선택이다.',
  s_mon_fire_boar:'화염 돌풍은 근접 전방에 모인 적을 보는 공격이다.',
  s_mon_jr_wraith:'망령 충격은 접근 후 둔화로 추격/이탈 창을 만든다.',
  s_mon_jr_balrog:'화염 파동은 위험한 전방 근접 폭발이다.',
  s_mon_drake:'용염은 전방에 모인 적을 향한 근접 숨결이다.',
  s_mon_white_fang:'빙설 송곳니는 가까이 붙어 둔화로 거리를 벌린다.',
  s_mon_snow_witch:'눈보라 직선은 좁은 통로와 적 정렬을 고르게 한다.',
  s_mon_pianus:'심해왕 광선은 먼 직선상의 적을 정렬해 노린다.',
  s_mon_white_sand_rabbit:'굴착탄의 직선 경로를 잡아 적을 관통한다.',
  s_mon_blood_harp:'깃울림의 직선은 전방 적 정렬이 핵심이다. 원작의 추가 디버프 근거는 부족하다.',
  s_mon_blue_wyvern:'빙룡 숨결은 접근 후 전방 둔화로 이탈 시간을 번다.',
  s_mon_manon:'용화염은 큰 전방 화염에 적이 모이는 순간을 고른다.',
  s_mon_mecateon:'기계 레이저의 좁은 직선은 정렬/조준이 핵심이다.'
};
const usage = {
  SHIELD:'피해가 들어오기 직전에 자신에게 사용한다.',
  BUFF:'공격을 이어가기 전에 자신에게 사용한다.',
  DASH_STRIKE:'진입/이탈 방향을 고른 뒤 돌진해 도착점에서 타격한다.',
  CENTER_BURST:'적과 가까이 있을 때 시전자 주변을 즉시 공격한다.',
  FRONT_CONE:'접근해 바라보는 방향의 부채꼴을 맞춘다.',
  LINE_STRIKE:'적을 한 직선에 맞춘 뒤 바라보는 방향으로 공격한다.',
  DELAYED_BLAST:'적이 머물 예상 지점을 조준하고 예고 뒤 폭발시킨다.',
  DAMAGE_ZONE:'적 무리의 이동 경로나 좁은 통로에 지속 영역을 배치한다.',
  PROJECTILE:'거리를 벌려 탄환의 진행 경로를 조준한다.',
  PROJECTILE_BLAST:'착탄할 무리의 위치를 조준한다.',
  PIERCING_PROJECTILE:'여러 적을 직선에 겹치게 해 관통시킨다.',
  SPREAD_PROJECTILE:'거리를 조절해 산탄의 퍼짐을 활용한다.'
};
function functionText(skill) {
  const effect = skill.secondary_effect ? ` + ${skill.secondary_effect}(${skill.secondary_value}, ${skill.secondary_duration}초)` : '';
  if (skill.behavior === 'SHIELD') return `자신에게 피해감소 ${skill.effect_value} / ${skill.duration}초`;
  if (skill.behavior === 'BUFF') return `${skill.effect_type} ${skill.effect_value} / ${skill.duration}초; 직접 피해 없음`;
  if (skill.behavior === 'DASH_STRIKE') return `방향 돌진 ${skill.dash_distance} world unit, 도착점 피해 계수 ${skill.coefficient}${effect}`;
  if (skill.behavior === 'DAMAGE_ZONE') return `조준 지점 폭 ${skill.behavior_width} world unit 지속영역, ${skill.behavior_ticks}회 × 계수 ${skill.coefficient}, 간격 ${skill.behavior_interval}초${effect}`;
  if (skill.behavior === 'DELAYED_BLAST') return `조준 지점 ${skill.behavior_delay}초 예고 후 폭 ${skill.behavior_width} world unit, 계수 ${skill.coefficient}${effect}`;
  return `${skill.behavior} / 계수 ${skill.coefficient} / 탐색거리 ${skill.range} world unit / 최대대상 ${skill.max_targets || '무제한'}${effect}`;
}
function makerRows(prefix) {
  try {
    const stdout = cp.execFileSync(process.execPath,
      [path.join(root, 'docs/tools/maker-mcp-call.cjs'), 'maker_logs', '{"kind":"normal"}'],
      { cwd: root, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
        env: { ...process.env, MAKER_QA_LOG_FILTER: prefix } });
    const logs = JSON.parse(stdout).logs || [];
    const ends = logs.filter(item => item.dateTime >= after && item.message?.startsWith(prefix + ' DONE '));
    const end = ends.at(-1);
    if (!end) return new Map();
    const start = logs.findLastIndex(item => item.dateTime <= end.dateTime
      && item.dateTime >= after && item.message?.startsWith(prefix + ' BEGIN '));
    if (start < 0) return new Map();
    const rows = new Map();
    for (const item of logs.slice(start)) {
      if (item.dateTime > end.dateTime) break;
      const match = item.message?.match(/ROW id=(\S+) status=(\S+)/);
      if (match) rows.set(match[1], match[2]);
    }
    return rows;
  } catch { return new Map(); }
}
const player = makerRows('[SkillRework66]');
const monster = makerRows('[MonsterSkillRework66]');
const rows = before.map(old => {
  const skill = skills.get(old.SkillID), evidence = lore.get(old.SkillID);
  const mob = monsters.get(evidence?.MonsterID);
  if (!skill || !evidence || !mob || mob.drop_skill_id !== old.SkillID
    || skill.icon_ruid !== evidence.IconRUID || skill.layer_ruids !== evidence.VFXRUID
    || skill.projectile_ruid !== evidence.ProjectileRUID)
    throw Error('Identity or icon/VFX drift: ' + old.SkillID + ' '
      + JSON.stringify({ skill: !!skill, evidence: !!evidence, mob: !!mob,
        drop: mob?.drop_skill_id, icon: skill?.icon_ruid, expectedIcon: evidence?.IconRUID,
        layers: skill?.layer_ruids, expectedLayers: evidence?.VFXRUID,
        projectile: skill?.projectile_ruid, expectedProjectile: evidence?.ProjectileRUID }));
  const special = changed[skill.id], main = role(skill);
  const playerUse = skill.id === 's_mon_memory_monk_trainee'
    ? '공격 전에 사용하고 12초 안에 다음 적중 한 대상에 강화를 쓴다.'
    : skill.id === 's_mon_drumming_bunny'
      ? '적과 교전하기 직전 사용해 4초 지속 피해 강화를 활용한다.'
      : usage[skill.behavior] + (skill.secondary_effect
        ? ' ' + skill.secondary_effect + ' 상태를 노린다.' : '');
  const monsterUse = skill.behavior === 'SHIELD' || skill.behavior === 'BUFF'
    ? '몬스터 자신에게 적용; 직접 공격 없음'
    : skill.behavior === 'DASH_STRIKE'
      ? '대상 플레이어 방향으로 돌진, 도착점 판정'
      : '대상 플레이어의 방향/위치 기준으로 같은 판정 사용';
  const p = player.get(skill.id) || 'NOT_RUN', m = monster.get(skill.id) || 'NOT_RUN';
  return {
    Monster: old.Monster, SkillID: skill.id, SkillName: skill.name,
    'Lore/Identity 근거': evidence.Evidence,
    BeforePrimaryRole: old.PrimaryRole, FinalPrimaryRole: main,
    SecondaryRole: skill.secondary_effect || (skill.behavior === 'BUFF'
      && skill.effect_type === 'next_attack_boost' ? 'SPECIAL/CONDITIONAL' : 'NONE'),
    '실제 최종 기능': functionText(skill), PlayerUsage: playerUse, MonsterUsage: monsterUse,
    '변경 이유': special?.[0] || (retained[skill.id]
      ? '현행 유지 — ' + retained[skill.id]
      : '현행 유지 — 이번 근거에서 새 기능을 확정할 수 없어 기존 판정 보존'),
    VFX_CHANGE_REQUIRED: special?.[1] || 'NO',
    '필요한 VFX 변경 설명': special?.[2] || '이번 단계에서 변경 확정 없음; 실제 화질/연출 승인은 별도',
    'Runtime PASS/FAIL': p === 'PASS_RUNTIME' && m === 'PASS_RUNTIME'
      ? 'PASS_RUNTIME' : p === 'NOT_RUN' || m === 'NOT_RUN' ? 'NOT_RUN' : 'FAIL_RUNTIME',
    PlayerRuntime: p, MonsterRuntime: m, SourceType: skill.id === 's_mon_memory_monk_trainee'
      ? 'NEXON_REGION_CONFIRMATION_PLUS_PROJECT_INTERPRETATION' : evidence.SourceType,
    SourceURL: skill.id === 's_mon_memory_monk_trainee'
      ? 'https://archive.maplestory.nexon.com/News/Update/76?p=22'
      : evidence.SourceURL,
    Tooltip: skill.description
  };
});
fs.mkdirSync(output, { recursive: true });
const keys = Object.keys(rows[0]);
fs.writeFileSync(path.join(output, 'SKILL_66_FINAL_DESIGN.csv'),
  [keys.map(esc).join(','), ...rows.map(item => keys.map(key => esc(item[key])).join(','))].join('\r\n') + '\r\n');
const counts = Object.fromEntries([...new Set(rows.map(item => item.FinalPrimaryRole))]
  .sort().map(key => [key, rows.filter(item => item.FinalPrimaryRole === key).length]));
const failed = rows.filter(item => item['Runtime PASS/FAIL'] !== 'PASS_RUNTIME');
fs.writeFileSync(path.join(output, 'FINAL_RESULT.md'),
  ['# 66종 스킬 최종 기능 검증', '',
    `기준: SKILL_66_CURRENT.csv / Maker QA 시작 시각 ${after} 이후만 집계`,
    'Maker Refresh: 2026-09-25 23:39:41 KST. Build Error 0; 기존 경고 2건(마노 InputSpeed, 보우마스터 AvatarAttackPlayRate).',
    '격리 Run 시작: 23:41:51. Player DONE: 23:45:10, 66/66 PASS. MONSTER_SKILL DONE: 23:47:55, 66/66 PASS. QA Run abandon: 23:51:33, active=false.',
    'Run 준비 중 23:41:00에 [LEA-3015] 시작 맵 없음 오류 2건이 기록되었다. QA Run 시작 이후 Error 로그는 0건이다. 준비 오류를 숨기고 전체 Runtime Error 0이라고 주장하지 않는다.',
    '외부 근거의 상당수는 커뮤니티 월드 아카이브 사본이다. 공식 Nexon 확인은 추억의 신관의 지역/등장 사실이며, 기도 강화 기능은 프로젝트 스킬명에 근거한 해석이다.',
    '기능 변경 5종: 주황버섯/엘리쟈/변형 스텀피(지속 영역), 정식기사 C(돌진), 추억의 신관(다음 1회 피해 강화). 스퀴드는 현행 지속 장판을 AREA로 재분류했으며 기능은 바꾸지 않았다.',
    '', '## 역할별 수', '',
    ...Object.entries(counts).map(([key,value]) => `- ${key}: ${value}`),
    '', `Player PASS: ${rows.filter(item => item.PlayerRuntime === 'PASS_RUNTIME').length}/66`,
    `MONSTER_SKILL PASS: ${rows.filter(item => item.MonsterRuntime === 'PASS_RUNTIME').length}/66`,
    `미통과/미실행: ${failed.map(item => item.SkillID).join(', ') || '없음'}`,
    '', 'VFX PNG/리소스는 이번 단계에서 수정하지 않았다. YES 표기는 다음 단계의 연출 정합성 작업 후보이며 이번 단계의 아트 PASS가 아니다.',
    'Maker QA는 실제 UseSkill/CastSkill 경로의 자동화 실행이다. 66종 자연 AI 빈도·66종 개별 시각 품질·모든 지형의 수동 플레이까지 증명하지 않는다.',
    'git commit/push는 하지 않았다.', ''].join('\n'));
process.stdout.write(JSON.stringify({ rows: rows.length, counts,
  playerPass: rows.filter(item => item.PlayerRuntime === 'PASS_RUNTIME').length,
  monsterPass: rows.filter(item => item.MonsterRuntime === 'PASS_RUNTIME').length,
  missing: failed.map(item => item.SkillID) }, null, 2) + '\n');
