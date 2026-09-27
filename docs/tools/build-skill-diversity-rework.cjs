#!/usr/bin/env node
'use strict';

// Current 66-ability redesign ledger and deterministic SkillTable transformer.
// Default is read-only report generation. Pass --apply only after reviewing the matrix.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const dataDir = path.join(root, 'RootDesk/MyDesk/GameData');
const outDir = path.join(root, 'docs/reports/skill-diversity-rework-20260922');

function parseCsv(text) {
  const rows = []; let row = [], cell = '', quoted = false;
  text = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { row.push(cell); cell = ''; }
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); if (row.some(Boolean)) rows.push(row); row = []; cell = '';
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const headers = rows.shift();
  return {headers, rows: rows.map(v => Object.fromEntries(headers.map((h, i) => [h, v[i] ?? ''])))};
}
function q(v) { v = String(v ?? ''); return /[",\r\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
function writeCsv(file, headers, rows) {
  fs.writeFileSync(file, '\uFEFF' + headers.map(q).join(',') + '\r\n'
    + rows.map(r => headers.map(h => q(r[h])).join(',')).join('\r\n') + '\r\n', 'utf8');
}

const groups = {
  SHIELD: ['s_mon_blue_snail','s_mon_stone','s_mon_dark_stump'],
  DASH_STRIKE: ['s_mon_red_snail','s_mon_wild_boar','s_mon_ribbon_pig','s_mon_wild_kargo','s_mon_hector','s_mon_toy_trojan','s_mon_mutant_iron_hog'],
  PROJECTILE: ['s_mon_star_pixie','s_mon_roid'],
  PROJECTILE_BLAST: ['s_mon_stumpy','s_mon_faust','s_mon_lunar_pixie','s_mon_king_bloctopus','s_mon_peach_monkey','s_mon_dodo'],
  PIERCING_PROJECTILE: ['s_mon_shark','s_mon_tae_roon','s_mon_mateon'],
  SPREAD_PROJECTILE: ['s_mon_chimera'],
  CENTER_BURST: ['s_mon_mano','s_mon_mushmom','s_mon_starfish','s_mon_jr_balrog','s_mon_tauromacis','s_mon_rombot','s_mon_wooden_dummy','s_mon_manon'],
  FRONT_CONE: ['s_mon_mushroom','s_mon_axe_stump','s_mon_fire_boar','s_mon_slime','s_mon_fairy','s_mon_octopus','s_mon_jr_wraith','s_mon_drake','s_mon_white_fang','s_mon_king_clang','s_mon_blue_wyvern','s_mon_official_knight_c'],
  LINE_STRIKE: ['s_mon_snail_dew_trail','s_mon_skeleton_commander','s_mon_snow_witch','s_mon_pianus','s_mon_white_sand_rabbit','s_mon_blood_harp','s_mon_memory_monk_trainee','s_mon_mecateon'],
  DELAYED_BLAST: ['s_mon_dark_axe_stump','s_mon_eliza','s_mon_chronos','s_mon_timer','s_mon_meercat','s_mon_ancient_dark_golem','s_mon_mutant_stumpy'],
  DAMAGE_ZONE: ['s_mon_shade','s_mon_squid','s_mon_drumming_bunny','s_mon_deo','s_mon_homun','s_mon_chief_memory_guardian','s_mon_zeno','s_mon_advanced_knight_b','s_mon_cygnus']
};
const secondary = {
  s_mon_mushroom: ['SLOW',0.25,1.5], s_mon_fairy: ['WEAKEN',0.18,2.0],
  s_mon_jr_wraith: ['SLOW',0.3,1.4], s_mon_faust: ['SLOW',0.3,1.8],
  s_mon_lunar_pixie: ['SLOW',0.25,1.5], s_mon_white_fang: ['SLOW',0.35,1.4],
  s_mon_snow_witch: ['SLOW',0.35,2.0], s_mon_timer: ['STUN',1,0.7],
  s_mon_chronos: ['SLOW',0.3,1.5], s_mon_homun: ['WEAKEN',0.2,2.2],
  s_mon_chimera: ['SLOW',0.25,1.8], s_mon_blue_wyvern: ['SLOW',0.3,1.6],
  s_mon_zeno: ['PULL',1.6,0.2], s_mon_dodo: ['PULL',1.4,0.2],
  s_mon_rombot: ['PULL',1.2,0.2], s_mon_king_clang: ['KNOCKBACK',1.4,0.2],
  s_mon_wooden_dummy: ['KNOCKBACK',1.2,0.2], s_mon_tauromacis: ['STUN',1,0.55],
  s_mon_official_knight_c: ['KNOCKBACK',1.1,0.2], s_mon_chief_memory_guardian: ['SLOW',0.3,1.8]
};
const defaults = {
  SHIELD: {width:0,delay:0,ticks:1,interval:0,role:'생존',target:'자기 대상'},
  DASH_STRIKE: {width:0,delay:0.2,ticks:1,interval:0,role:'접근·위치 조절',target:'8방향 돌진'},
  PROJECTILE: {width:0,delay:0.35,ticks:1,interval:0,role:'원거리 단일전',target:'8방향 부채꼴 자동 조준'},
  PROJECTILE_BLAST: {width:2.2,delay:0.35,ticks:1,interval:0,role:'원거리 착탄 광역',target:'8방향 부채꼴 자동 조준'},
  PIERCING_PROJECTILE: {width:1.25,delay:0.35,ticks:1,interval:0,role:'직선 다수전',target:'8방향 직선'},
  SPREAD_PROJECTILE: {width:18,delay:0.35,ticks:3,interval:0,role:'전방 분산 공격',target:'8방향 확산'},
  CENTER_BURST: {width:0,delay:0,ticks:1,interval:0,role:'포위 대응',target:'시전자 중심'},
  FRONT_CONE: {width:75,delay:0,ticks:1,interval:0,role:'전방 다수전',target:'현재 8방향 부채꼴'},
  LINE_STRIKE: {width:1.5,delay:0,ticks:1,interval:0,role:'직선 관통',target:'현재 8방향 직선'},
  DELAYED_BLAST: {width:2.4,delay:0.55,ticks:1,interval:0,role:'예측·타이밍',target:'현재 방향의 대상 지점'},
  DAMAGE_ZONE: {width:2.6,delay:0.15,ticks:3,interval:0.45,role:'지속 압박·공간 제어',target:'현재 방향의 대상 지점'}
};
const behaviorOf = new Map();
for (const [behavior, ids] of Object.entries(groups)) for (const id of ids) {
  if (behaviorOf.has(id)) throw new Error('duplicate redesign id ' + id);
  behaviorOf.set(id, behavior);
}
function beforeBehavior(s) {
  if (s.skill_kind === 'defense') return 'SHIELD';
  if (Number(s.dash_distance) > 0) return 'DASH_STRIKE';
  if (s.projectile_ruid) return 'PROJECTILE';
  return 'CENTER_DIRECT';
}
function afterTooltip(s, behavior, sec) {
  const action = {
    SHIELD:'자신에게 방어 효과를 건다', DASH_STRIKE:'현재 방향으로 돌진해 도착점의 적을 공격한다',
    PROJECTILE:'현재 방향의 적에게 탄환을 발사한다', PROJECTILE_BLAST:'탄환을 발사해 착탄 지점을 폭발시킨다',
    PIERCING_PROJECTILE:'현재 방향으로 관통 탄환을 발사한다', SPREAD_PROJECTILE:'현재 방향에 세 갈래 탄환을 펼친다',
    CENTER_BURST:'자신을 중심으로 즉시 폭발시킨다', FRONT_CONE:'현재 방향의 부채꼴 범위를 공격한다',
    LINE_STRIKE:'현재 방향의 좁고 긴 직선을 관통한다', DELAYED_BLAST:'현재 방향의 지점을 예고한 뒤 폭발시킨다',
    DAMAGE_ZONE:'현재 방향에 잠시 남는 피해 영역을 만든다'
  }[behavior];
  const extra = !sec ? '' : ({SLOW:' 적의 이동을 잠시 늦춘다.',STUN:' 적의 행동을 짧게 멈춘다.',
    KNOCKBACK:' 적을 밀어낸다.',PULL:' 적을 중심으로 끌어당긴다.',WEAKEN:' 적의 공격을 잠시 약화한다.'}[sec[0]] || '');
  return action + '.' + extra;
}

const skillPath = path.join(dataDir, 'SkillTable.csv');
const monsterPath = path.join(dataDir, 'MonsterTable.csv');
const skillTable = parseCsv(fs.readFileSync(skillPath, 'utf8'));
const monsterTable = parseCsv(fs.readFileSync(monsterPath, 'utf8'));
const skillById = new Map(skillTable.rows.map(s => [s.id, s]));
const active = monsterTable.rows.map(m => ({m, s: skillById.get(m.drop_skill_id)}))
  .filter(x => x.s && ['attack','defense'].includes(x.s.skill_kind));
if (active.length !== 66) throw new Error('expected 66 active abilities, got ' + active.length);
for (const {s} of active) if (!behaviorOf.has(s.id)) throw new Error('redesign missing ' + s.id);
if (behaviorOf.size !== 66) throw new Error('redesign contains ' + behaviorOf.size + ' ids');
if (process.argv.includes('--apply') && active.some(({s}) => s.behavior)) {
  throw new Error('SkillTable already has redesign behavior data; refusing non-idempotent --apply');
}

fs.mkdirSync(outDir, {recursive:true});
const beforeHeaders = ['SkillID','SkillName','MonsterID','MonsterName','IconRUID','VFX','Tooltip','BeforeBehavior','Damage','Range','MaxTargets','Move','Delay','BeforeRole','SimilarGroup'];
const beforeRows = active.map(({m,s}) => ({SkillID:s.id,SkillName:s.name,MonsterID:m.id,MonsterName:m.name,
  IconRUID:s.icon_ruid,VFX:[s.effect_ruid,s.projectile_ruid,s.layer_ruids].filter(Boolean).join('|'),Tooltip:s.description,
  BeforeBehavior:beforeBehavior(s),Damage:s.coefficient,Range:s.range,MaxTargets:s.max_targets,
  Move:Number(s.dash_distance)>0?'YES':'NO',Delay:s.projectile_ruid||Number(s.dash_distance)>0?'YES':'NO',
  BeforeRole:s.skill_kind==='defense'?'생존':Number(s.dash_distance)>0?'접근·순간화력':s.projectile_ruid?'원거리 피해':'시전자 중심 피해',
  SimilarGroup:beforeBehavior(s)}));
if (!fs.existsSync(path.join(outDir,'SKILL_BEFORE.csv')))
  writeCsv(path.join(outDir,'SKILL_BEFORE.csv'),beforeHeaders,beforeRows);

const matrixHeaders = ['SkillID','Monster','SkillName','BeforeBehavior','BeforeRole','KeepOrChange','AfterPrimaryBehavior','AfterSecondaryEffects','AfterRole','PlayerTargeting','MonsterModeTargeting','VFXReusePlan','ReasonForChange','SimilarSkillsBefore','SimilarSkillsAfter'];
const matrixRows = active.map(({m,s}) => {
  const before=beforeBehavior(s), after=behaviorOf.get(s.id), sec=secondary[s.id];
  return {SkillID:s.id,Monster:m.name,SkillName:s.name,BeforeBehavior:before,
    BeforeRole:beforeRows.find(r=>r.SkillID===s.id).BeforeRole,KeepOrChange:before===after||['SHIELD','DASH_STRIKE'].includes(after)?'KEEP':'CHANGE',
    AfterPrimaryBehavior:after,AfterSecondaryEffects:sec?`${sec[0]} value=${sec[1]} duration=${sec[2]}`:'NONE',AfterRole:defaults[after].role,
    PlayerTargeting:defaults[after].target,MonsterModeTargeting:defaults[after].target.replace('현재 8방향','대상 플레이어 방향').replace('현재 방향','대상 플레이어 방향'),
    VFXReusePlan:'기존 icon/layer/effect/projectile RUID 유지; 판정 위치·회전만 behavior에 맞춤',
    ReasonForChange:before===after||['SHIELD','DASH_STRIKE'].includes(after)?'이미 독립적인 소비 판단을 제공함':'기존 시전자 중심 원형 판정을 이름·VFX가 암시하는 공간 행동으로 정합화',
    SimilarSkillsBefore:before,SimilarSkillsAfter:after};
});
if (!fs.existsSync(path.join(outDir,'SKILL_REDESIGN_MATRIX.csv')))
  writeCsv(path.join(outDir,'SKILL_REDESIGN_MATRIX.csv'),matrixHeaders,matrixRows);

if (process.argv.includes('--apply')) {
  const newFields = ['behavior','behavior_width','behavior_delay','behavior_ticks','behavior_interval','secondary_effect','secondary_value','secondary_duration','enemy_control_scale','boss_control_scale'];
  for (const f of newFields) if (!skillTable.headers.includes(f)) skillTable.headers.push(f);
  for (const {s} of active) {
    const behavior=behaviorOf.get(s.id), d=defaults[behavior], sec=secondary[s.id];
    s.behavior=behavior; s.behavior_width=String(d.width); s.behavior_delay=String(d.delay);
    s.behavior_ticks=String(d.ticks); s.behavior_interval=String(d.interval);
    s.secondary_effect=sec?sec[0]:''; s.secondary_value=sec?String(sec[1]):'0'; s.secondary_duration=sec?String(sec[2]):'0';
    s.enemy_control_scale='0.6'; s.boss_control_scale='0.35'; s.description=afterTooltip(s,behavior,sec);
    // Three damage-zone ticks preserve the original approximate total damage. Spread can hit up to three rays.
    if (behavior==='DAMAGE_ZONE') s.coefficient=(Number(s.coefficient)/3).toFixed(3).replace(/0+$/,'').replace(/\.$/,'');
    if (behavior==='SPREAD_PROJECTILE') s.coefficient=(Number(s.coefficient)/2).toFixed(3).replace(/0+$/,'').replace(/\.$/,'');
  }
  writeCsv(skillPath, skillTable.headers, skillTable.rows);
}

const counts = Object.fromEntries(Object.keys(groups).map(k => [k, groups[k].length]));
if (!fs.existsSync(path.join(outDir,'REDESIGN_SUMMARY.json')))
  fs.writeFileSync(path.join(outDir,'REDESIGN_SUMMARY.json'), JSON.stringify({active:active.length,counts,secondary:Object.keys(secondary).length,applied:process.argv.includes('--apply')},null,2)+'\n');

// Post-implementation tables are derived from the preserved pre-change CSV and
// the current SkillTable. Never reconstruct the baseline from modified data.
if (!process.argv.includes('--apply')) {
  const savedBefore = parseCsv(fs.readFileSync(path.join(outDir,'SKILL_BEFORE.csv'),'utf8')).rows;
  const beforeById = new Map(savedBefore.map(row => [row.SkillID,row]));
  if (savedBefore.length !== 66 || beforeById.size !== 66) throw new Error('invalid preserved baseline');
  const afterHeaders = ['SkillID','SkillName','MonsterID','MonsterName','SkillKind','PrimaryBehavior',
    'SecondaryEffect','Coefficient','Range','MaxTargets','Move','Delay','Ticks','Interval',
    'IconRUID','VFX','Tooltip','PlayerTargeting','MonsterModeTargeting','EvidenceLevel'];
  const after = active.map(({m,s}) => {
    const before = beforeById.get(s.id);
    if (!before || before.MonsterID !== m.id || before.SkillName !== s.name)
      throw new Error('baseline identity mismatch '+s.id);
    const vfx = [s.effect_ruid,s.projectile_ruid,s.layer_ruids].filter(Boolean).join('|');
    if (before.IconRUID !== s.icon_ruid || before.VFX !== vfx)
      throw new Error('art reference changed '+s.id);
    if (s.behavior !== behaviorOf.get(s.id)) throw new Error('behavior mismatch '+s.id);
    if (!s.description || s.description !== afterTooltip(s,s.behavior,secondary[s.id]))
      throw new Error('tooltip mismatch '+s.id);
    return {SkillID:s.id,SkillName:s.name,MonsterID:m.id,MonsterName:m.name,
      SkillKind:s.skill_kind,PrimaryBehavior:s.behavior,SecondaryEffect:s.secondary_effect || 'NONE',
      Coefficient:s.coefficient,Range:s.range,MaxTargets:s.max_targets,
      Move:Number(s.dash_distance)>0?'YES':'NO',Delay:s.behavior_delay,
      Ticks:s.behavior_ticks,Interval:s.behavior_interval,IconRUID:s.icon_ruid,VFX:vfx,
      Tooltip:s.description,PlayerTargeting:defaults[s.behavior].target,
      MonsterModeTargeting:defaults[s.behavior].target.replace('현재 8방향','대상 플레이어 방향').replace('현재 방향','대상 플레이어 방향'),
      EvidenceLevel:'CODE_DATA; runtime see separate CSV'};
  });
  writeCsv(path.join(outDir,'SKILL_AFTER.csv'),afterHeaders,after);
  const comparisonHeaders = ['SkillID','Monster','SkillName','BeforeBehavior','AfterBehavior',
    'BeforeRole','AfterRole','BeforeCoefficient','AfterCoefficient','BeforeRange','AfterRange',
    'BeforeTooltip','AfterTooltip','SecondaryEffect','IconAndVFXPreserved'];
  writeCsv(path.join(outDir,'SKILL_BEFORE_AFTER.csv'),comparisonHeaders,
    after.map(a=>{const b=beforeById.get(a.SkillID);return {SkillID:a.SkillID,Monster:a.MonsterName,
      SkillName:a.SkillName,BeforeBehavior:b.BeforeBehavior,AfterBehavior:a.PrimaryBehavior,
      BeforeRole:b.BeforeRole,AfterRole:defaults[a.PrimaryBehavior].role,
      BeforeCoefficient:b.Damage,AfterCoefficient:a.Coefficient,BeforeRange:b.Range,AfterRange:a.Range,
      BeforeTooltip:b.Tooltip,AfterTooltip:a.Tooltip,SecondaryEffect:a.SecondaryEffect,
      IconAndVFXPreserved:'YES'};}));
  writeCsv(path.join(outDir,'TOOLTIP_AUDIT.csv'),
    ['SkillID','SkillName','BeforeTooltip','CurrentTooltip','CodeDataMatch','CooldownShownInRunTooltip','RuntimeVerified'],
    after.map(a=>({SkillID:a.SkillID,SkillName:a.SkillName,
      BeforeTooltip:beforeById.get(a.SkillID).Tooltip,CurrentTooltip:a.Tooltip,
      CodeDataMatch:'PASS_STATIC',CooldownShownInRunTooltip:'NO_CODE_PATH',RuntimeVerified:'NOT_RUN_AFTER_LATEST_EDIT'})));
  if (!fs.existsSync(path.join(outDir,'MONSTER_SKILL_RUNTIME.csv')))
    writeCsv(path.join(outDir,'MONSTER_SKILL_RUNTIME.csv'),
    ['SkillID','Monster','SkillName','Behavior','Secondary','CurrentBuildStatus','PriorAttempt','Cast','VFX','DamageOrShield','Cooldown','CastLimit','RuntimeError','Note'],
    after.map(a=>({SkillID:a.SkillID,Monster:a.MonsterName,SkillName:a.SkillName,
      Behavior:a.PrimaryBehavior,Secondary:a.SecondaryEffect,
      CurrentBuildStatus:'NOT_RUN',PriorAttempt:'57/66 observed in interrupted batch; per-row evidence incomplete',
      Cast:'NOT_RUN',VFX:'NOT_RUN',DamageOrShield:'NOT_RUN',Cooldown:'NOT_RUN',
      CastLimit:'NOT_RUN',RuntimeError:'NOT_RUN',
      Note:'Maker execution connector unavailable after model/tool change; do not infer PASS'})));
  const beforeCounts = Object.fromEntries(['CENTER_DIRECT','PROJECTILE','DASH_STRIKE','SHIELD']
    .map(k=>[k,savedBefore.filter(x=>x.BeforeBehavior===k).length]));
  const afterCounts = Object.fromEntries(Object.keys(groups).map(k=>[k,after.filter(x=>x.PrimaryBehavior===k).length]));
  fs.writeFileSync(path.join(outDir,'DIVERSITY_BEFORE_AFTER.md'),
    '# 스킬 다양성 개편 전후 (코드/데이터 기준)\n\n'
    + '모집단: 현재 플레이어 획득 가능 액티브/방어 66종. 표현이 아니라 판정 구조를 집계한다.\n\n'
    + '| 구분 | 개편 전 | 개편 후 |\n|---|---:|---:|\n'
    + `| Primary 구조 종류 | ${Object.values(beforeCounts).filter(Boolean).length} | ${Object.values(afterCounts).filter(Boolean).length} |\n`
    + `| 가장 큰 동일 구조 그룹 | ${Math.max(...Object.values(beforeCounts))} | ${Math.max(...Object.values(afterCounts))} |\n`
    + `| 시전자 중심 즉발 | ${beforeCounts.CENTER_DIRECT} | ${afterCounts.CENTER_BURST} |\n`
    + `| 투사체 계열 | ${beforeCounts.PROJECTILE} | ${afterCounts.PROJECTILE+afterCounts.PROJECTILE_BLAST+afterCounts.PIERCING_PROJECTILE+afterCounts.SPREAD_PROJECTILE} |\n`
    + `| 이동 공격 | ${beforeCounts.DASH_STRIKE} | ${afterCounts.DASH_STRIKE} |\n`
    + `| 방어 | ${beforeCounts.SHIELD} | ${afterCounts.SHIELD} |\n`
    + `| 제어/약화 복합 | 0 (기존 공통 실행 기준) | ${after.filter(x=>x.SecondaryEffect!=='NONE').length} |\n`
    + `| 지연·지속 영역 | 0 | ${afterCounts.DELAYED_BLAST+afterCounts.DAMAGE_ZONE} |\n\n`
    + '개편 후 세부 분포: '+Object.entries(afterCounts).map(([k,v])=>`${k} ${v}`).join(', ')+'.\n\n'
    + '잠정 판정: 일부 편중. 44종의 공통 원형 즉발은 분화했으나, 여러 스킬은 같은 primitive의 수치·소재 변형이다. '
    + '게임 플레이 체감과 지형/몬스터 모드 검증을 마치기 전에는 다양성 충분으로 확정하지 않는다.\n', 'utf8');
}
console.log(JSON.stringify({status:'PASS',active:active.length,counts,secondary:Object.keys(secondary).length,applied:process.argv.includes('--apply')}));
