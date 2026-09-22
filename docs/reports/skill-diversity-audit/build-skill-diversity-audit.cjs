#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const root = path.resolve(__dirname, '..', '..', '..');
const reportRoot = path.resolve(__dirname);
const latest = fs.readFileSync(path.join(reportRoot, 'LATEST_BASELINE.txt'), 'utf8').trim().split(/\r?\n/);
const baselineId = latest[0];
const outDir = path.join(root, latest[1]);
const baseline = JSON.parse(fs.readFileSync(path.join(outDir, 'baseline', 'baseline.json'), 'utf8'));

function abs(rel) { return path.join(root, ...rel.replace(/\\/g, '/').split('/')); }
function rel(p) { return path.relative(root, p).split(path.sep).join('/'); }
function exists(relPath) { return fs.existsSync(abs(relPath)); }
function read(relPath) { return fs.readFileSync(abs(relPath), 'utf8'); }
function sha(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function csvCell(v) { const s=String(v??''); return /[",\r\n]/.test(s)?`"${s.replace(/"/g,'""')}"`:s; }
function parseCsv(text) {
  const rows=[]; let row=[], field='', quoted=false;
  for (let i=0;i<text.length;i++) {
    const c=text[i];
    if (quoted) {
      if (c==='"' && text[i+1]==='"') { field+='"'; i++; }
      else if (c==='"') quoted=false;
      else field+=c;
    } else if (c==='"') quoted=true;
    else if (c===',') { row.push(field); field=''; }
    else if (c==='\n') { row.push(field.replace(/\r$/,'')); rows.push(row); row=[]; field=''; }
    else field+=c;
  }
  if (field || row.length) { row.push(field.replace(/\r$/,'')); rows.push(row); }
  if (!rows.length) return [];
  const headers=rows[0].map(x=>x.replace(/^\uFEFF/,''));
  return rows.slice(1).filter(r=>r.some(v=>v!=='')).map((r,index)=>{
    const o={__line:index+2}; headers.forEach((h,i)=>o[h]=r[i]??''); return o;
  });
}
function num(v, fallback=0) { const n=Number(v); return Number.isFinite(n)?n:fallback; }
function splitIds(v) { return String(v||'').split(/[|,;]/).map(x=>x.trim()).filter(Boolean); }
function lineOf(text, needle) { const i=text.split(/\r?\n/).findIndex(x=>x.includes(needle)); return i>=0?i+1:0; }
function cite(p, line, detail) { return { path:p, line, detail, level:'코드/데이터 확인' }; }
function dataUri(file) {
  if (!file || !fs.existsSync(file)) return '';
  const ext=path.extname(file).toLowerCase();
  const mime=ext==='.png'?'image/png':ext==='.jpg'||ext==='.jpeg'?'image/jpeg':'application/octet-stream';
  return `data:${mime};base64,${fs.readFileSync(file).toString('base64')}`;
}
function walk(dir, out=[]) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir,{withFileTypes:true})) {
    const p=path.join(dir,e.name);
    if (e.isDirectory()) walk(p,out); else out.push(p);
  }
  return out;
}

const skillPath='Mislocated/MyDesk/GameData/SkillTable.csv';
const monsterPath='RootDesk/MyDesk/GameData/MonsterTable.csv';
const balancePath='RootDesk/MyDesk/GameData/GameBalance.csv';
const skills=parseCsv(read(skillPath));
const monsters=parseCsv(read(monsterPath));
const balanceRows=parseCsv(read(balancePath));
const balance=Object.fromEntries(balanceRows.map(x=>[x.key,num(x.value)]));
const skillById=new Map(skills.map(x=>[x.id,x]));
const monstersByDrop=new Map();
const monstersByCombat=new Map();
for (const m of monsters) {
  if (m.drop_skill_id) {
    if (!monstersByDrop.has(m.drop_skill_id)) monstersByDrop.set(m.drop_skill_id,[]);
    monstersByDrop.get(m.drop_skill_id).push(m);
  }
  for (const id of splitIds(m.combat_skill_ids)) {
    if (!monstersByCombat.has(id)) monstersByCombat.set(id,[]);
    monstersByCombat.get(id).push(m);
  }
}

const codePaths={
  gameData:'RootDesk/MyDesk/GameData/GameData.mlua',
  collection:'RootDesk/MyDesk/Progress/PlayerCollection.mlua',
  slots:'RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua',
  playerAttack:'RootDesk/MyDesk/PlayerAttack.mlua',
  monsterAttack:'RootDesk/MyDesk/MonsterAttack.mlua',
  skillEffect:'RootDesk/MyDesk/Combat/SkillEffect.mlua',
  projectile:'RootDesk/MyDesk/Combat/SkillProjectile.mlua',
  skillBar:'RootDesk/MyDesk/UI/SkillBar.mlua',
  equipPanel:'RootDesk/MyDesk/UI/EquipPanel.mlua',
  stats:'RootDesk/MyDesk/Player/PlayerStats.mlua'
};
const code={}; for (const [k,p] of Object.entries(codePaths)) code[k]=read(p);

// Imported icon/frame evidence. A row is used as an image only when it resolves to a real local file.
const importRows=exists('docs/art/import-runs/ALL_AREAS_20260914_151243/SKILL_IMPORT_MAP.csv')
  ? parseCsv(read('docs/art/import-runs/ALL_AREAS_20260914_151243/SKILL_IMPORT_MAP.csv')) : [];
const importBySkill=new Map();
for (const r of importRows) {
  const local=path.isAbsolute(r.path)?r.path:abs(r.path);
  if (!fs.existsSync(local)) continue;
  if (!importBySkill.has(r.skill_id)) importBySkill.set(r.skill_id,[]);
  importBySkill.get(r.skill_id).push({...r,local});
}
const area00Map=exists('docs/art/area00-images-output/AREA_00_IMAGES_RESOURCE_MAP.csv')
  ? parseCsv(read('docs/art/area00-images-output/AREA_00_IMAGES_RESOURCE_MAP.csv')) : [];
const area00Received=abs('docs/art/output_audit/area00_received_20260913/received/AREA_00_IMAGES_OUTPUT');
const area00Files=walk(area00Received);

// Proven monster-image candidates from the approved/audited INPUT/OUTPUT working sets.
const monsterImageRoots=[
  abs('docs/art/output_audit_work/20260912_153221_v24_repack/STAGING'),
  abs('docs/art/output_audit/runs/20260912_192803_area00_intent_quality_review/sources')
];
const allMonsterImages=monsterImageRoots.flatMap(d=>walk(d)).filter(p=>/MONSTER_IMAGE\.png$/i.test(p));
function findMonsterImage(monsterId) {
  const re=new RegExp(`(^|[\\\\/_])${monsterId.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}([\\\\/_]|$)`,'i');
  const found=allMonsterImages.filter(p=>re.test(p));
  if (!found.length) return null;
  found.sort((a,b)=>a.length-b.length||a.localeCompare(b));
  return found[0];
}
function findSkillImages(skill, linked) {
  let icon=null, frame=null, source='';
  const rows=importBySkill.get(skill.id)||[];
  const iconRow=rows.find(r=>r.role==='ICON' && r.ruid===skill.icon_ruid) || rows.find(r=>r.role==='ICON');
  if (iconRow) { icon=iconRow.local; source=rel(icon); }
  const frameRow=rows.find(r=>['VFX','CAST','PROJECTILE','REFERENCE'].includes(r.role) && String(r.frame)==='0');
  if (frameRow) frame=frameRow.local;
  if ((!icon||!frame) && linked.length) {
    const m=linked[0];
    const map=area00Map.find(r=>r.skill_id===skill.id && r.monster_id===m.id);
    if (map) {
      if (!icon) icon=area00Files.find(p=>new RegExp(`${skill.id}.*ICON\\.png$`,'i').test(p.replace(/\\/g,'/')))||null;
      if (!frame) frame=area00Files.find(p=>new RegExp(`${skill.id}.*F00\\.png$`,'i').test(p.replace(/\\/g,'/')))||null;
      if (icon) source=rel(icon);
    }
  }
  return {icon,frame,source};
}

const flagOn=(balance.phase1_random_combat_enabled||0)>=0.5;
const simplifiedOn=(balance.phase3_simplified_growth_enabled||0)>=0.5;
const playerAttackLines={
  use:lineOf(code.playerAttack,'method boolean UseSkill('),
  defense:lineOf(code.playerAttack,'method boolean UseDefenseSkill('),
  throw:lineOf(code.playerAttack,'method boolean ThrowSkill('),
  dash:lineOf(code.playerAttack,'method boolean DashSkill('),
  throwHit:lineOf(code.playerAttack,'method void ResolveThrowHit('),
  dashHit:lineOf(code.playerAttack,'method void ResolveDashHit('),
  calc:lineOf(code.playerAttack,'method integer CalcDamage(')
};
const slotLines={
  pool:lineOf(code.slots,'method table GetOwnedActiveSkillIds('),
  pick:lineOf(code.slots,'method string PickRandomOwnedActive('),
  supply:lineOf(code.slots,'method boolean SupplyOneRandomSkill('),
  consume:lineOf(code.slots,'method boolean ConsumeRandomSlot(')
};
const collectionLines={capture:lineOf(code.collection,'method boolean TryCapture('), multiplier:lineOf(code.collection,'method number GetAbilityMultiplier(')};

function classify(skill, linkedDrop, linkedCombat) {
  const activePlayer = flagOn && linkedDrop.length>0 && skill.source==='monster' && skill.slot_type==='monster' && skill.skill_kind!=='passive';
  if (activePlayer) return ['A','현재 모드에서 테이밍 후 플레이어가 획득·사용 가능'];
  if (linkedDrop.length>0 && skill.skill_kind==='passive') return ['C','현재 신규 모드에서 수집은 가능하지만 패시브 효과·랜덤 풀은 비활성'];
  if (linkedCombat.length>0) return ['D','MonsterTable.combat_skill_ids를 통해 몬스터/보스가 사용'];
  if (skill.slot_type==='monster' && skill.skill_kind!=='passive') return ['B','PlayerAttack 실행 형식은 호환되지만 현재 MonsterTable 획득 연결이 없음'];
  return ['E','정의는 있으나 현재 획득/실행 연결을 확인하지 못함'];
}
function groupFor(skill, cls) {
  if (skill.skill_kind==='passive') return {id:'G07',name:'비활성 패시브 스탯',similarity:'A',basis:'현재 신규 모드에서는 실제 효과가 0이며 랜덤 풀에서도 제외'};
  if (skill.skill_kind==='defense' && skill.effect_type==='shield') return {id:'G05',name:'자기 실드',similarity:'B',basis:'즉시 자기 대상 방어 효과; 수치·지속시간 차이'};
  if (skill.skill_kind==='defense' && skill.effect_type==='heal') return {id:'G06',name:'자기 회복',similarity:'D',basis:'HP를 회복하는 별도 기능'};
  if (num(skill.dash_distance)>0) return {id:'G04',name:'8방향 돌진 후 착지 판정',similarity:'C',basis:'이동과 도착 지점 피해를 결합해 거리·위험 판단이 달라짐'};
  if (cls==='D' && /^s_bow_/.test(skill.id)) return {id:'G08',name:'보우마스터 전용 투사체 패턴',similarity:'D',basis:'전용 분기에서 다발·지속 재조준·연사 패턴을 실행'};
  if (skill.projectile_ruid) return {id:'G03',name:'8방향 조준 투사체/지연 착탄',similarity:'C',basis:'가까운 적 자동 조준 또는 허공 발사, 비행 후 위치 판정'};
  if (skill.target_mode==='single' || num(skill.max_targets)===1) return {id:'G01',name:'중심 원형 단일 피해',similarity:'B',basis:'플레이어 중심 원 판정에서 최대 1대상; 계수·반경 차이'};
  if (skill.skill_kind==='attack') return {id:'G02',name:'중심 원형 다수 피해',similarity:'B',basis:'플레이어 중심 원 판정에서 다수/무제한 대상; 계수·반경 차이'};
  return {id:'G09',name:'구현 불명',similarity:'D',basis:'현재 공통 실행 분기와 일치 여부 불명'};
}
function inputFor(skill, cls) {
  if (cls==='D') return '몬스터 AI 자동/조건부 발동';
  if (cls==='C') return '현재 발동 없음(레거시 패시브 데이터)';
  if (cls==='E') return '정보 부족';
  if (skill.skill_kind==='defense') return 'SkillBar 직접 사용 · 자기 대상';
  if (num(skill.dash_distance)>0) return 'SkillBar 직접 사용 · 8방향 지정';
  if (skill.projectile_ruid) return 'SkillBar 직접 사용 · 8방향 지정 후 부채꼴 내 최근접 자동 조준';
  return 'SkillBar 직접 사용 · 방향 입력은 연출에만 사용, 실제 판정은 시전자 중심';
}
function effectsFor(skill, cls) {
  const tags=[]; const roles=[];
  if (skill.skill_kind==='passive') { tags.push('현재 효과 없음'); roles.push('레거시/컬렉션'); }
  else if (skill.skill_kind==='defense') {
    if (skill.effect_type==='shield') { tags.push('방어','강화'); roles.push('생존','피해 완화'); }
    else if (skill.effect_type==='heal') { tags.push('회복'); roles.push('생존','회복'); }
  } else {
    tags.push('피해');
    if (num(skill.dash_distance)>0) { tags.push('플레이어 이동','지연 판정'); roles.push('접근','거리 조절','순간 화력'); }
    else if (skill.projectile_ruid) { tags.push('투사체','지연 판정'); roles.push('원거리','회피 가능한 압박'); }
    else if (skill.target_mode==='single'||num(skill.max_targets)===1) roles.push('단일전','순간 화력');
    else roles.push('다수전','순간 화력');
  }
  if (cls==='D') roles.push('적 패턴');
  return {tags:[...new Set(tags)],roles:[...new Set(roles)]};
}
function actualEffect(skill, cls) {
  const r=num(skill.range)>0?num(skill.range):num(balance.player_attack_range,1.2);
  const targets=num(skill.max_targets)>0?`최대 ${Math.floor(num(skill.max_targets))}명`:'제한 없음';
  if (skill.skill_kind==='passive') return simplifiedOn?'신규 단순 성장 모드에서는 능력치 효과가 적용되지 않으며 랜덤 SkillBar에서도 제외된다.':'레거시 모드의 보유형 패시브 데이터.';
  if (skill.skill_kind==='defense') {
    if (skill.effect_type==='shield') return `자기에게 ${Math.round(num(skill.effect_value)*100)}% 피해 감소 실드를 ${num(skill.duration)}초 적용한다. 테이밍 중복 배율이 효과량에 곱해진다.`;
    if (skill.effect_type==='heal') return `자기 HP를 ${num(skill.effect_value)}만큼 회복한다. 만피면 실패하여 슬롯을 소비하지 않는다.`;
    return '방어 분기는 있으나 effect_type을 처리하는 코드를 확인하지 못했다.';
  }
  if (skill.projectile_ruid) {
    const impact=skill.target_mode==='area'?`기본 ${num(balance.projectile_hit_radius,0.8)} 이상, 사거리의 40%·최대 2.5`:String(num(balance.projectile_hit_radius,0.8));
    return `8방향 입력의 ±${num(balance.projectile_aim_degrees,22.5)}° 안 최근접 적을 조준하고, 없으면 사거리 끝으로 발사한다. ${num(balance.projectile_seconds,0.35)}초 후 착탄 원(반경 ${impact})에서 ${targets}에게 1회 피해 판정한다.`;
  }
  if (num(skill.dash_distance)>0) return `지정한 8방향으로 ${num(skill.dash_distance)}유닛 돌진 연출 후 ${num(balance.skill_dash_seconds,0.2)}초에 계산된 도착점 중심 반경 ${r} 원에서 ${targets}에게 1회 피해 판정한다.`;
  return `사용 즉시 플레이어 중심(세로 +0.5) 반경 ${r} 원에서 ${targets}에게 1회 피해 판정한다. 방향 입력은 적중 위치 선정이 아니라 이펙트 방향/허공 연출에만 쓰인다.`;
}
function mismatchFor(skill, cls) {
  const issues=[]; const d=skill.description||'';
  if (skill.skill_kind==='passive' && simplifiedOn) issues.push('툴팁은 능력치 상승을 설명하지만 신규 모드 실제 계산에서는 효과가 비활성이다.');
  if (!skill.projectile_ruid && num(skill.dash_distance)<=0 && skill.skill_kind==='attack' && /(전방|정면|부채꼴|직선|앞의)/.test(d)) issues.push('툴팁은 방향성 판정을 암시하지만 실제 피해 판정은 플레이어 중심 원형이다.');
  if (!/^s_bow_/.test(skill.id) && skill.skill_kind==='attack' && !skill.projectile_ruid && num(skill.dash_distance)<=0 && /(세 번|여러 번|연속|다단)/.test(d)) issues.push('툴팁은 다회 타격을 암시하지만 공통 실행 코드는 1회 Attack 호출이다.');
  if (skill.skill_kind==='attack' && /(기절|빙결|둔화|중독|화상|속박|침묵)/.test(d)) issues.push('툴팁의 상태이상 표현에 대응하는 실제 상태이상 적용 코드를 확인하지 못했다.');
  return issues;
}

const records=[];
for (const s of skills) {
  const linkedDrop=monstersByDrop.get(s.id)||[];
  const linkedCombat=monstersByCombat.get(s.id)||[];
  const [primaryClass,state]=classify(s,linkedDrop,linkedCombat);
  const actorTags=[];
  if (primaryClass==='A'||primaryClass==='B') actorTags.push('플레이어');
  if (linkedCombat.length) actorTags.push('몬스터/보스');
  if (!actorTags.length && primaryClass==='C') actorTags.push('수집 데이터');
  const group=groupFor(s,primaryClass);
  const eff=effectsFor(s,primaryClass);
  const imgs=findSkillImages(s,linkedDrop);
  const monsterImage=linkedDrop.length?findMonsterImage(linkedDrop[0].id):null;
  const isAttack=s.skill_kind==='attack';
  const primaryFunction=s.skill_kind==='passive'?'판정 불가':(isAttack?'공격 중심':(s.skill_kind==='defense'?'비공격 중심':'판정 불가'));
  const acquisition=primaryClass==='A'||primaryClass==='C'
    ? `연결 몬스터 처치 시 자동 테이밍 판정: 최초 ${Math.round(num(balance.first_capture_rate,0.1)*100)}%, 중복 ${Math.round(num(balance.duplicate_capture_rate,0.03)*100)}%, 최대 ${Math.floor(num(balance.skill_stack_max,5))}`
    : primaryClass==='D'?'플레이어 획득 경로 없음':primaryClass==='B'?'현재 획득 연결 없음':'정보 부족';
  const reuse=primaryClass==='A'
    ? `개별 쿨다운 무시. 성공 시 해당 일회성 슬롯 소비, 빈칸은 ${num(balance.random_skill_supply_interval,5)}초마다 1개 공급.`
    : primaryClass==='D'?`몬스터 AI가 SkillTable cooldown(${num(s.cooldown)}초)과 내부 사용 주기를 적용.`
    : primaryClass==='C'?'현재 발동/재사용 없음':`SkillTable cooldown=${num(s.cooldown)}초 데이터는 존재하나 현재 획득 경로 없음.`;
  const evidence=[cite(skillPath,s.__line,`SkillTable 원본 행: ${s.id}`)];
  for (const m of linkedDrop) evidence.push(cite(monsterPath,m.__line,`drop_skill_id로 연결: ${m.id}`));
  for (const m of linkedCombat) evidence.push(cite(monsterPath,m.__line,`combat_skill_ids로 연결: ${m.id}`));
  if (primaryClass==='A') {
    evidence.push(cite(codePaths.slots,slotLines.pool,'테이밍된 액티브 스킬 풀 구성'));
    evidence.push(cite(codePaths.playerAttack,playerAttackLines.use,'플레이어 공통 스킬 실행 분기'));
    evidence.push(cite(codePaths.slots,slotLines.consume,'성공 사용 슬롯 소비'));
  } else if (primaryClass==='D') evidence.push(cite(codePaths.monsterAttack,lineOf(code.monsterAttack,'method boolean CastSkill('),'몬스터 공통 스킬 실행'));
  const verification='코드/데이터 확인';
  const expression={
    icon_ruid:s.icon_ruid||'', vfx_ruids:s.layer_ruids||s.effect_ruid||'', projectile_ruid:s.projectile_ruid||'',
    icon_image:imgs.icon?dataUri(imgs.icon):'', icon_source:imgs.icon?rel(imgs.icon):'',
    vfx_image:imgs.frame?dataUri(imgs.frame):'', vfx_source:imgs.frame?rel(imgs.frame):'',
    monster_image:monsterImage?dataUri(monsterImage):'', monster_image_source:monsterImage?rel(monsterImage):''
  };
  records.push({
    skill_id:s.id,name:s.name,source:s.source,primary_class:primaryClass,state,actor_tags:actorTags,
    acquisition,linked_monsters:linkedDrop.map(m=>({id:m.id,name:m.name,level:num(m.level),collection_icon_ruid:m.collection_icon_ruid,model_id:m.model_id})),
    combat_users:linkedCombat.map(m=>({id:m.id,name:m.name})),
    expression,tooltip:s.description||'',tooltip_source:`${skillPath}:${s.__line}`,tooltip_mismatch:mismatchFor(s,primaryClass),
    input_method:inputFor(s,primaryClass),targeting:s.skill_kind==='defense'?'자기 대상':s.projectile_ruid?'8방향 입력 + 부채꼴 최근접 자동 조준':num(s.dash_distance)>0?'8방향 이동/도착점':'시전자 중심 원형',
    cast_time:s.projectile_ruid?`${num(balance.projectile_seconds,0.35)}초 비행 후 판정`:num(s.dash_distance)>0?`${num(balance.skill_dash_seconds,0.2)}초 돌진 후 판정`:'명시적 준비시간 없음',
    action_restriction:num(s.dash_distance)>0?'돌진 이동을 실행하나 별도 시전 잠금은 이 경로에서 확인되지 않음':'별도 시전 중 이동 제한 코드 확인 없음',
    reuse_limit:reuse,trigger:primaryClass==='D'?'자동/조건부':primaryClass==='C'?'현재 비활성':'직접 사용',
    primary_function:primaryFunction,effect_tags:eff.tags,combat_roles:eff.roles,actual_effect:actualEffect(s,primaryClass),
    numeric:{coefficient:num(s.coefficient),range:num(s.range),max_targets:num(s.max_targets),duration:num(s.duration),effect_value:num(s.effect_value),dash_distance:num(s.dash_distance),cooldown:num(s.cooldown)},
    shape_difference:s.projectile_ruid?'투사체 비행 + 원형 착탄':num(s.dash_distance)>0?'플레이어 이동 + 도착점 원형':s.skill_kind==='defense'?'자기 효과':'시전자 중심 원형',
    tactical_difference:group.similarity==='C'||group.similarity==='D'?group.basis:(primaryClass==='A'?'전술적 차이는 주로 대상 수·반경·계수이며, 동일 그룹 내부 판단 차이는 런타임 미확인':'전술적 차이 미확인'),
    similarity_group:group.id,similarity_name:group.name,similarity_grade:group.similarity,similarity_basis:group.basis,
    original_basis:'프로젝트 내부에 현행 원작 출처가 연결된 근거 문서를 확인하지 못함',
    project_identity:linkedDrop.length?`${linkedDrop.map(m=>m.name).join(', ')}의 이름/외형 모티브를 SkillTable 설명과 VFX로 변환한 프로젝트 창작 연결`:'연결 몬스터 정보 부족',
    verification_level:verification,runtime_status:'NOT_RUN',evidence,
    missing_info:[...(monsterImage?[]:['몬스터 이미지 미확보']),...(imgs.icon?[]:['스킬 아이콘 PNG 미확보']), '개별 SkillID 런타임 실행 미확인', '원작 특징의 외부 공식 근거 미확인']
  });
}

const classLabels={A:'현재 플레이어 획득·사용',B:'실행 경로 있으나 획득 없음',C:'비활성/레거시',D:'몬스터·보스 전용',E:'정의/구현 불명'};
function tally(items,key) { const o={}; for(const x of items){const v=typeof key==='function'?key(x):x[key];o[v]=(o[v]||0)+1;} return o; }
const current=records.filter(r=>r.primary_class==='A');
const groups=[...new Map(records.map(r=>[r.similarity_group,{id:r.similarity_group,name:r.similarity_name,grade:r.similarity_grade,basis:r.similarity_basis}])).values()]
  .sort((a,b)=>a.id.localeCompare(b.id)).map(g=>({...g,skills:records.filter(r=>r.similarity_group===g.id).map(r=>({id:r.skill_id,name:r.name,primary_class:r.primary_class}))}));
const stats={
  total_unique_skills:records.length,
  by_primary_class:tally(records,'primary_class'),
  current_player_usable:current.length,
  primary_function_current:tally(current,'primary_function'),
  input_method_current:tally(current,'input_method'),
  effect_tags_current:tally(current.flatMap(r=>r.effect_tags.map(t=>({tag:t}))),'tag'),
  verification_all:tally(records,'verification_level'),
  runtime:{NOT_RUN:records.length},
  image_coverage:{monster:records.filter(r=>r.expression.monster_image).length,icon:records.filter(r=>r.expression.icon_image).length,vfx:records.filter(r=>r.expression.vfx_image).length},
  tooltip_mismatch_skills:records.filter(r=>r.tooltip_mismatch.length).length
};
const attackCount=current.filter(r=>r.primary_function==='공격 중심').length;
const conclusion=current.length===0?'판정 보류':attackCount/current.length>=0.85?'상당히 편중됨':attackCount/current.length>=0.65?'일부 유형에 편중됨':'충분히 다양함';

const data={
  schema:'skill-diversity-audit-v1',baseline_id:baselineId,generated_at_utc:new Date().toISOString(),
  baseline:{branch:baseline.branch,head_commit:baseline.head_commit,dirty:baseline.dirty,working_tree_fingerprint_sha256:baseline.working_tree_fingerprint_sha256,preservation:baseline.preservation},
  runtime:{status:'NOT_RUN',reason:'현재 세션에 Maker MCP play/logs 도구가 제공되지 않아 기준본을 수정하지 않는 정적 분석만 수행'},
  active_mode:{phase1_random_combat_enabled:flagOn,phase3_simplified_growth_enabled:simplifiedOn,skill_slot_max:num(balance.skill_slot_max,5),random_skill_supply_interval:num(balance.random_skill_supply_interval,5),cooldown_policy:flagOn?'신규 랜덤 모드에서는 무시':'레거시 쿨다운 적용',acquisition_source:'MonsterTable.drop_skill_id → PlayerCollection.TryCapture → TamedMonsters',use_source:'TamedMonsters 액티브 → PlayerSkillSlots 랜덤 재고 → PlayerAttack.UseSkill'},
  loaded_sources:[
    {dataset:'SkillTable',path:skillPath,loader:`${codePaths.gameData}:${lineOf(code.gameData,'method void LoadSkills(')}`,sha256:sha(abs(skillPath))},
    {dataset:'MonsterTable',path:monsterPath,loader:`${codePaths.gameData}:${lineOf(code.gameData,'method void LoadMonsters(')}`,sha256:sha(abs(monsterPath))},
    {dataset:'GameBalance',path:balancePath,loader:`${codePaths.gameData}:${lineOf(code.gameData,'method void LoadBalance(')}`,sha256:sha(abs(balancePath))}
  ],
  methodology:{
    population:'모든 SkillTable 고유 SkillID. 주 결론은 primary_class=A만 사용.',
    expression_vs_function:'이름·색·VFX는 표현 차이, 계수·반경·대상 수는 수치/형태 차이, 조준·이동·지연·방어 판단 변화만 전투 판단 차이로 분리.',
    group_rule:'실제 PlayerAttack/MonsterAttack 실행 분기와 판정 위치/시점/효과를 우선하여 G01~G09로 묶음. A=거의 동일, B=같은 구조의 수치 변형, C=같은 역할이나 운용 차이, D=별개 기능.',
    original_setting:'프로젝트 안에서 현행성과 출처가 확인되는 자료만 인정. 이번 기준본에는 개별 스킬의 공식 원작 출처 연결이 없어 정보 부족으로 기록.'
  },
  stats,conclusion:`구현 구조 기준 잠정 결론: ${conclusion}`,
  skills:records,similarity_groups:groups
};

fs.writeFileSync(path.join(outDir,'skill-diversity-data.json'),JSON.stringify(data,null,2)+'\n');

const baselineMd=`# Skill Diversity Audit Baseline\n\n- baseline_id: \`${baselineId}\`\n- 분석 시작: ${baseline.analysis_started_kst}\n- 브랜치: \`${baseline.branch}\`\n- HEAD: \`${baseline.head_commit}\`\n- 미커밋 변경: **${baseline.dirty?'있음':'없음'}**\n- 작업 트리 지문(SHA-256): \`${baseline.working_tree_fingerprint_sha256}\`\n- 보존 위치: \`${rel(path.join(outDir,'baseline'))}\`\n- 런타임: **NOT_RUN** — Maker MCP play/logs 도구가 이 세션에 없음\n\n## 현재 활성 모드\n\n- phase1_random_combat_enabled: ${flagOn?1:0}\n- phase3_simplified_growth_enabled: ${simplifiedOn?1:0}\n- SkillBar: 최대 ${num(balance.skill_slot_max,5)}칸, ${num(balance.random_skill_supply_interval,5)}초마다 빈 슬롯 1개 공급\n- 획득: MonsterTable.drop_skill_id → 처치 시 테이밍 → TamedMonsters\n- 사용: 테이밍된 액티브 전체가 동일 가중치 랜덤 풀, 성공 사용 시 슬롯 소비\n- 재사용: 신규 랜덤 모드에서 SkillTable cooldown을 검사하지 않음. 레거시 모드 데이터는 유지.\n- 장착: 신규 모드에서는 MonsterSlots를 사용하지 않음.\n\n## 실제 로드 원본\n\n${data.loaded_sources.map(x=>`- ${x.dataset}: \`${x.path}\` (loader \`${x.loader}\`, SHA-256 \`${x.sha256}\`)`).join('\n')}\n\n## 기준본 재현\n\n${baseline.preservation.reconstruction.map((x,i)=>`${i+1}. ${x}`).join('\n')}\n\n민감 파일명 정책에 해당한 파일 내용은 기준본에 넣지 않았다. 이번 기준본은 보고서 디렉터리 자체를 작업 트리 지문에서 제외했다.\n`;
fs.writeFileSync(path.join(outDir,'skill-audit-baseline.md'),baselineMd);

const embedded=JSON.stringify(data).replace(/</g,'\\u003c');
const html=`<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>스킬 다양성 감사 · ${esc(baselineId)}</title>
<style>
:root{color-scheme:dark;--bg:#0c1018;--panel:#151c28;--line:#2c3b50;--muted:#9cb0c8;--text:#edf4ff;--accent:#66d0ff;--ok:#70d89a;--warn:#ffc66d;--bad:#ff7b86}*{box-sizing:border-box}body{margin:0;background:linear-gradient(145deg,#0b0f17,#101827);color:var(--text);font:14px/1.5 system-ui,-apple-system,"Malgun Gothic",sans-serif}header{padding:28px 32px;border-bottom:1px solid var(--line);background:#0d1420ee;position:sticky;top:0;z-index:3}h1{margin:0 0 8px;font-size:25px}h2{margin:28px 0 12px}.meta,.muted{color:var(--muted)}main{padding:22px 28px 60px;max-width:1800px;margin:auto}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.card,.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}.card b{font-size:24px;display:block;color:var(--accent)}.filters{display:grid;grid-template-columns:2fr repeat(6,minmax(120px,1fr));gap:8px;margin:16px 0;position:sticky;top:104px;z-index:2;background:#0c111bcc;padding:10px;border-radius:10px;backdrop-filter:blur(8px)}input,select{width:100%;background:#111a27;color:var(--text);border:1px solid #34465e;border-radius:7px;padding:9px}.skill{display:grid;grid-template-columns:220px 1fr;gap:16px;margin:10px 0}.visuals{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.visual{background:#090d14;border:1px solid #26354a;border-radius:8px;min-height:86px;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden}.visual img{width:100%;height:90px;object-fit:contain;background:repeating-conic-gradient(#161c26 0 25%,#202836 0 50%) 50%/14px 14px}.visual small{padding:3px 4px;color:var(--muted)}.title{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.badge{padding:2px 7px;border-radius:999px;background:#233148;border:1px solid #3c526f;font-size:12px}.A{background:#153d30}.B{background:#3b3420}.C{background:#3a283c}.D{background:#3b2429}.E{background:#333}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;margin-top:9px}.kv{background:#101722;border-radius:7px;padding:8px}.kv b{display:block;color:#a9c7e8;font-size:12px}.issues{color:var(--warn)}details{margin-top:7px}.evidence{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#bdd0e6}.hidden{display:none!important}.groupTable{width:100%;border-collapse:collapse}.groupTable td,.groupTable th{border:1px solid var(--line);padding:7px;text-align:left}.notice{border-left:4px solid var(--warn);padding-left:12px}.nowrap{white-space:nowrap}@media(max-width:900px){header{position:static}.filters{position:static;grid-template-columns:1fr 1fr}.skill{grid-template-columns:1fr}}
</style></head><body><header><h1>현재 프로젝트 전체 스킬 다양성 감사</h1><div class="meta">baseline_id <code>${esc(baselineId)}</code> · ${esc(baseline.analysis_started_kst)} · 런타임 NOT_RUN</div></header><main>
<section class="notice panel"><b>${esc(data.conclusion)}</b><br>주 결론 모집단은 현재 모드에서 실제 획득·사용 가능한 A 분류 ${current.length}종입니다. 표현 차이와 수치 차이는 전투 판단 차이와 분리했습니다. USER_APPROVED 또는 런타임 검증을 뜻하지 않습니다.</section>
<h2>상단 통계</h2><div class="cards" id="stats"></div>
<section class="panel"><b>모집단·통계 주의</b><p>A/B/C/D/E는 중복 없는 주 분류입니다. 효과 태그는 복수 태그라 중복 집계입니다. 원작 근거는 프로젝트 안에서 출처가 확인된 자료만 인정했으며, 개별 공식 근거가 없는 항목은 정보 부족입니다. 현재 HTML은 외부 fetch/CDN 없이 내장 데이터로 작동합니다.</p></section>
<h2>유사 스킬 그룹</h2><div class="panel"><table class="groupTable"><thead><tr><th>ID</th><th>그룹</th><th>유사도</th><th>기준</th><th>소속</th></tr></thead><tbody id="groups"></tbody></table></div>
<h2>전체 스킬</h2><div class="filters"><input id="q" placeholder="몬스터/스킬/ID 검색"><select id="cls"><option value="">전체 상태</option></select><select id="func"><option value="">전체 주 기능</option></select><select id="input"><option value="">전체 사용 방법</option></select><select id="verify"><option value="">전체 검증 수준</option></select><select id="missing"><option value="">정보 부족 전체</option><option value="yes">정보 부족 있음</option><option value="no">정보 부족 없음</option></select><select id="group"><option value="">전체 그룹</option></select></div><div id="count" class="meta"></div><div id="skills"></div>
<script>const DATA=${embedded};
const $=s=>document.querySelector(s), uniq=a=>[...new Set(a)].sort(), opt=(sel,vals,labels={})=>{for(const v of vals){const o=document.createElement('option');o.value=v;o.textContent=labels[v]||v;sel.appendChild(o)}};
const classLabels=${JSON.stringify(classLabels)};opt($('#cls'),Object.keys(classLabels),classLabels);opt($('#func'),uniq(DATA.skills.map(x=>x.primary_function)));opt($('#input'),uniq(DATA.skills.map(x=>x.input_method)));opt($('#verify'),uniq(DATA.skills.map(x=>x.verification_level)));opt($('#group'),DATA.similarity_groups.map(x=>x.id),Object.fromEntries(DATA.similarity_groups.map(x=>[x.id,x.id+' · '+x.name])));
const cards=[['전체 고유 정의',DATA.stats.total_unique_skills],['현재 획득·사용(A)',DATA.stats.current_player_usable],['비활성/레거시(C)',DATA.stats.by_primary_class.C||0],['몬스터·보스 전용(D)',DATA.stats.by_primary_class.D||0],['실행만/획득 없음(B)',DATA.stats.by_primary_class.B||0],['상태 불명(E)',DATA.stats.by_primary_class.E||0],['공격 중심(A 모집단)',DATA.stats.primary_function_current['공격 중심']||0],['툴팁 불일치 후보',DATA.stats.tooltip_mismatch_skills],['아이콘 PNG 확보',DATA.stats.image_coverage.icon],['몬스터 PNG 확보',DATA.stats.image_coverage.monster],['런타임 확인',0],['코드/데이터 확인',DATA.stats.verification_all['코드/데이터 확인']||0]];$('#stats').innerHTML=cards.map(x=>'<div class="card"><b>'+x[1]+'</b>'+x[0]+'</div>').join('');
$('#groups').innerHTML=DATA.similarity_groups.map(g=>'<tr><td>'+g.id+'</td><td>'+g.name+'</td><td>'+g.grade+'</td><td>'+g.basis+'</td><td>'+g.skills.map(s=>s.id+' '+s.name).join('<br>')+'</td></tr>').join('');
const img=(src,label,ruid)=>'<div class="visual">'+(src?'<img src="'+src+'" alt="'+label+'">':'<small>이미지 미확보<br>'+((ruid||'').slice(0,18)||'RUID 없음')+'</small>')+'<small>'+label+'</small></div>';
function render(){const q=$('#q').value.toLowerCase(),c=$('#cls').value,f=$('#func').value,i=$('#input').value,v=$('#verify').value,m=$('#missing').value,g=$('#group').value;const rows=DATA.skills.filter(x=>{const hay=[x.skill_id,x.name,...x.linked_monsters.flatMap(y=>[y.id,y.name])].join(' ').toLowerCase();return(!q||hay.includes(q))&&(!c||x.primary_class===c)&&(!f||x.primary_function===f)&&(!i||x.input_method===i)&&(!v||x.verification_level===v)&&(!g||x.similarity_group===g)&&(!m||(m==='yes'?x.missing_info.length>0:x.missing_info.length===0))});$('#count').textContent=rows.length+'개 표시';$('#skills').innerHTML=rows.map(x=>'<article class="skill panel"><div><div class="visuals">'+img(x.expression.monster_image,'몬스터',x.linked_monsters[0]?.collection_icon_ruid)+img(x.expression.icon_image,'스킬 아이콘',x.expression.icon_ruid)+img(x.expression.vfx_image,'VFX F00',x.expression.vfx_ruids)+'</div><small class="muted">'+[x.expression.monster_image_source,x.expression.icon_source,x.expression.vfx_source].filter(Boolean).join('<br>')+'</small></div><div><div class="title"><h3>'+x.name+'</h3><code>'+x.skill_id+'</code><span class="badge '+x.primary_class+'">'+x.primary_class+' '+classLabels[x.primary_class]+'</span><span class="badge">'+x.similarity_group+' '+x.similarity_name+'</span></div><div class="grid"><div class="kv"><b>연결 몬스터</b>'+(x.linked_monsters.map(y=>y.name+' ('+y.id+')').join(', ')||'없음')+'</div><div class="kv"><b>사용 주체/상태</b>'+x.actor_tags.join(', ')+' · '+x.state+'</div><div class="kv"><b>획득</b>'+x.acquisition+'</div><div class="kv"><b>입력/대상</b>'+x.input_method+'<br>'+x.targeting+'</div><div class="kv"><b>실제 효과</b>'+x.actual_effect+'</div><div class="kv"><b>재사용 제한</b>'+x.reuse_limit+'</div><div class="kv"><b>효과/역할 태그</b>'+x.effect_tags.join(', ')+' / '+x.combat_roles.join(', ')+'</div><div class="kv"><b>전술 차이 판정</b>'+x.tactical_difference+'</div></div><details><summary>원문 툴팁·불일치</summary><p>'+x.tooltip+'</p><p class="issues">'+(x.tooltip_mismatch.length?x.tooltip_mismatch.join('<br>'):'명백한 불일치 자동 탐지 없음')+'</p></details><details><summary>근거·검증·정보 부족</summary><div class="evidence">'+x.evidence.map(e=>e.path+':'+e.line+' · '+e.detail).join('<br>')+'</div><p>검증 수준: '+x.verification_level+' / 런타임: '+x.runtime_status+'</p><p class="muted">'+x.missing_info.join(' · ')+'</p><p>원작: '+x.original_basis+'<br>프로젝트 변환: '+x.project_identity+'</p></details></div></article>').join('')}
for(const el of document.querySelectorAll('.filters input,.filters select'))el.addEventListener('input',render);render();
</script></main></body></html>`;
fs.writeFileSync(path.join(outDir,'skill-diversity-audit.html'),html);

const summaryRows=[['metric','value'],['baseline_id',baselineId],['total_unique',records.length],['current_A',current.length],['class_B',stats.by_primary_class.B||0],['class_C',stats.by_primary_class.C||0],['class_D',stats.by_primary_class.D||0],['class_E',stats.by_primary_class.E||0],['runtime','NOT_RUN'],['conclusion',data.conclusion]];
fs.writeFileSync(path.join(outDir,'audit-summary.csv'),summaryRows.map(r=>r.map(csvCell).join(',')).join('\n')+'\n');

const htmlCheck=fs.readFileSync(path.join(outDir,'skill-diversity-audit.html'),'utf8');
const validation={
  baseline_id:baselineId,
  unique_skill_ids:new Set(records.map(x=>x.skill_id)).size,
  source_skill_rows:skills.length,
  no_external_fetch:!(/fetch\s*\(|https?:\/\/(?!www\.w3\.org)/i.test(htmlCheck)),
  embedded_data:htmlCheck.includes(`"baseline_id":"${baselineId}"`),
  json_roundtrip:JSON.parse(fs.readFileSync(path.join(outDir,'skill-diversity-data.json'),'utf8')).skills.length===records.length,
  existing_game_files_modified_by_builder:false,
  note:'검증 스크립트는 보고서 디렉터리만 생성한다.'
};
fs.writeFileSync(path.join(outDir,'AUDIT_VALIDATION.json'),JSON.stringify(validation,null,2)+'\n');
if (validation.unique_skill_ids!==skills.length || !validation.no_external_fetch || !validation.embedded_data || !validation.json_roundtrip) {
  throw new Error(`audit validation failed: ${JSON.stringify(validation)}`);
}
console.log(JSON.stringify({baseline_id:baselineId,output:rel(outDir),stats,conclusion:data.conclusion,validation},null,2));
