#!/usr/bin/env node
'use strict';

// Static contract only. This cannot certify Maker build, art, geometry, or play.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const game = path.join(root, 'RootDesk/MyDesk');
const reports = path.join(root, 'docs/reports/skill-diversity-rework-20260922');
function csv(file) {
  const text = fs.readFileSync(file,'utf8').replace(/^\uFEFF/,'');
  const records=[]; let row=[], cell='', quoted=false;
  for(let i=0;i<text.length;i++) {
    const c=text[i];
    if(c==='"') { if(quoted&&text[i+1]==='"'){cell+='"';i++;} else quoted=!quoted; }
    else if(c===','&&!quoted){row.push(cell);cell='';}
    else if((c==='\r'||c==='\n')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(Boolean))records.push(row);row=[];cell='';}
    else cell+=c;
  }
  if(cell||row.length){row.push(cell);records.push(row);}
  const fields=records.shift();
  return records.map(r=>Object.fromEntries(fields.map((f,i)=>[f,r[i]??''])));
}
const skillRows=csv(path.join(game,'GameData/SkillTable.csv'));
const monsterRows=csv(path.join(game,'GameData/MonsterTable.csv'));
const before=csv(path.join(reports,'SKILL_BEFORE.csv'));
const matrix=csv(path.join(reports,'SKILL_REDESIGN_MATRIX.csv'));
const after=csv(path.join(reports,'SKILL_AFTER.csv'));
const comparison=csv(path.join(reports,'SKILL_BEFORE_AFTER.csv'));
const tooltips=csv(path.join(reports,'TOOLTIP_AUDIT.csv'));
const playerRuntime=csv(path.join(reports,'PLAYER_SKILL_RUNTIME.csv'));
const monsterRuntime=csv(path.join(reports,'MONSTER_SKILL_RUNTIME.csv'));
const playerRuntimeFinal=csv(path.join(reports,'PLAYER_SKILL_RUNTIME_FINAL_20260923.csv'));
const monsterRuntimeFinal=csv(path.join(reports,'MONSTER_SKILL_RUNTIME_FINAL_20260923.csv'));
const errors=[];
function check(ok,message){if(!ok)errors.push(message);}
const skills=new Map(skillRows.map(r=>[r.id,r]));
const monsters=new Map(monsterRows.map(r=>[r.id,r]));
const bySkill=new Map(monsterRows.map(r=>[r.drop_skill_id,r]));
check(skills.size===skillRows.length,'duplicate SkillID in live SkillTable');
check(monsters.size===monsterRows.length,'duplicate MonsterID in live MonsterTable');
const allowed=new Set(['SHIELD','BUFF','DASH_STRIKE','PROJECTILE','PROJECTILE_BLAST',
  'PIERCING_PROJECTILE','SPREAD_PROJECTILE','CENTER_BURST','FRONT_CONE',
  'LINE_STRIKE','DELAYED_BLAST','DAMAGE_ZONE']);
const allowedSecondary=new Set(['','SLOW','STUN','WEAKEN','KNOCKBACK','PULL']);
const source={
  data:fs.readFileSync(path.join(game,'GameData/GameData.mlua'),'utf8'),
  player:fs.readFileSync(path.join(game,'PlayerAttack.mlua'),'utf8'),
  monster:fs.readFileSync(path.join(game,'MonsterAttack.mlua'),'utf8'),
  control:fs.readFileSync(path.join(game,'Combat/RoomMonster.mlua'),'utf8'),
  dash:fs.readFileSync(path.join(game,'Player/PlayerDash.mlua'),'utf8'),
  ui:fs.readFileSync(path.join(game,'UI/EquipPanel.mlua'),'utf8')
};
const eligible=monsterRows.filter(m=>{
  const s=skills.get(m.drop_skill_id);
  return s&&['attack','defense','buff'].includes(s.skill_kind);
});
check(skillRows.length===112,'SkillTable expected 112 rows');
check(eligible.length===66,'expected 66 eligible abilities');
for(const [name,rows] of Object.entries({before,matrix,after,comparison,tooltips,
  playerRuntime,monsterRuntime,playerRuntimeFinal,monsterRuntimeFinal})) {
  const key=name.includes('Runtime')?'skill_id':'SkillID';
  const ids=rows.map(r=>r[key]);
  check(rows.length===66,`${name} row count ${rows.length}`);
  check(new Set(ids).size===66,`${name} duplicate or wrong id key`);
  const expected=new Set(eligible.map(m=>m.drop_skill_id));
  check(ids.every(id=>expected.has(id)),`${name} includes a non-eligible SkillID`);
}
for(const [name,rows] of Object.entries({playerRuntime,monsterRuntime,
  playerRuntimeFinal,monsterRuntimeFinal})) {
  check(rows.every(r=>r.status==='PASS_RUNTIME'),`${name} contains non-passing report rows`);
  check(rows.every(r=>r.vfx==='ACTUAL_PATH_NOT_VISUAL_CERTIFICATION'),
    `${name} misstates VFX visual certification`);
}
check(JSON.stringify(playerRuntime)===JSON.stringify(playerRuntimeFinal),
  'player mandatory and final-dated report differ');
check(JSON.stringify(monsterRuntime)===JSON.stringify(monsterRuntimeFinal),
  'monster mandatory and final-dated report differ');
for(const m of eligible){
  const s=skills.get(m.drop_skill_id), id=s.id;
  check(allowed.has(s.behavior),`${id} invalid behavior ${s.behavior}`);
  check(allowedSecondary.has(s.secondary_effect),`${id} invalid secondary`);
  check(s.icon_ruid!==''&&s.description!=='',`${id} icon/tooltip missing`);
  check(s.effect_ruid!==''||s.layer_ruids!==''||s.projectile_ruid!=='',`${id} VFX missing`);
  check(Number.isFinite(Number(s.coefficient)),`${id} coefficient invalid`);
  check(Number(s.enemy_control_scale)>0&&Number(s.enemy_control_scale)<=1,`${id} enemy scale invalid`);
  check(Number(s.boss_control_scale)>0&&Number(s.boss_control_scale)<=1,`${id} boss scale invalid`);
  if(s.behavior==='SHIELD') check(s.skill_kind==='defense'&&s.effect_type==='shield',`${id} shield role mismatch`);
  if(s.behavior==='SHIELD') check(Number(s.coefficient)===0&&Number(s.effect_value)>0
    &&Number(s.duration)>0,`${id} shield must be non-damaging and timed`);
  if(s.behavior==='BUFF') check(s.skill_kind==='buff'
    &&['attack_boost','next_attack_boost'].includes(s.effect_type)
    &&Number(s.effect_value)>0&&Number(s.duration)>0,`${id} buff role mismatch`);
  if(s.behavior==='BUFF') check(Number(s.coefficient)===0,`${id} buff must not masquerade as a damage skill`);
  if(s.behavior==='DASH_STRIKE') check(Number(s.dash_distance)>0,`${id} no dash distance`);
  if(s.behavior.includes('PROJECTILE')) check(s.projectile_ruid!=='',`${id} projectile RUID missing`);
  if(['DELAYED_BLAST','DAMAGE_ZONE'].includes(s.behavior))
    check(Number(s.behavior_delay)>=0&&Number(s.behavior_ticks)>=1,`${id} invalid timing`);
  if(s.secondary_effect!=='')
    check(Number(s.secondary_value)>0&&Number(s.secondary_duration)>0,`${id} invalid secondary values`);
  check(bySkill.get(id)?.id===m.id,`${id} monster mapping mismatch`);
}
const currentRoleContracts={
  s_mon_shade:['SHIELD','', 'defense'],
  s_mon_slime:['FRONT_CONE','SLOW','attack'],
  s_mon_starfish:['CENTER_BURST','KNOCKBACK','attack'],
  s_mon_eliza:['DAMAGE_ZONE','','attack'],
  s_mon_ancient_dark_golem:['DELAYED_BLAST','STUN','attack'],
  s_mon_mutant_stumpy:['DAMAGE_ZONE','','attack'],
  s_mon_drumming_bunny:['BUFF','','buff'],
  s_mon_chief_memory_guardian:['SHIELD','','defense']
};
for(const [id,contract] of Object.entries(currentRoleContracts)) {
  const s=skills.get(id);
  check(s!=null&&s.behavior===contract[0]&&s.secondary_effect===contract[1]
    &&s.skill_kind===contract[2],`${id} current role contract mismatch`);
}
for(const behavior of allowed){
  check(source.player.includes(`"${behavior}"`)||['SHIELD','BUFF','DASH_STRIKE'].includes(behavior),
    `player adapter missing ${behavior}`);
  check(source.monster.includes(`"${behavior}"`)||['SHIELD','BUFF','DASH_STRIKE'].includes(behavior),
    `monster adapter missing ${behavior}`);
}
for(const kind of ['SLOW','STUN','WEAKEN','KNOCKBACK','PULL'])
  check(source.player.includes(`"${kind}"`)&&source.monster.includes(`"${kind}"`),`effect adapter missing ${kind}`);
const playerUseSkill=source.player.split('method boolean UseSkill(')[1]
  ?.split('method Vector2 ResolveSkillDirection')[0]||'';
const monsterCastSkill=source.monster.split('method boolean CastSkill(')[1]
  ?.split('method boolean UseSpatialMonsterSkill')[0]||'';
check(playerUseSkill.includes('skill.skill_kind == "buff"')
  &&playerUseSkill.includes('self:UseBuffSkill(skill)')
  &&playerUseSkill.includes('ConsumeRandomSlot(activeIndex, skillId)'),
  'player buff must be handled in UseSkill before spatial attack');
check(monsterCastSkill.includes('skill.skill_kind == "buff"')
  &&monsterCastSkill.includes('monster:ApplyAttackBoost('),
  'monster buff must be handled in CastSkill before spatial attack');
check(source.player.includes('coefficient * (1 + self.OutgoingBoostRatio)')
  &&source.control.includes('multiplier * (1 + self.AttackBoostRatio)'),
  'buff must affect actual player and monster damage calculations');
check(source.player.includes('ConsumeRandomSlot'),'slot consumption path absent');
check(source.ui.includes('RenderRunSkillDesc')&&source.ui.includes('skill.description'),'Run tooltip path absent');
check(source.control.includes('SlowSerial')&&source.control.includes('StunSerial')&&source.control.includes('ImpulseSerial'),
  'independent control timer guards missing');
check(source.monster.includes('monster.StunUntil then return'),
  'stun does not gate monster attack timer');
check(source.player.includes('self.EnemyStunUntil then return false')
  && source.monster.includes('attack:ApplyEnemyStun(seconds)'),
  'enemy STUN does not gate player server attack');
check(source.dash.includes('ApplyEnemyControl'),'player control adapter missing');
check(source.data.includes('method boolean IsSkillLineUnblocked(')
  && source.data.includes('self:TraceSkillEndpoint(map, fromPos, toPos)'),
  'projectile terrain line guard missing from GameData');
for(const side of ['player','monster']) {
  const code=source[side];
  check(code.includes('self.projectileTerrainCheck = true')
    && code.includes('self.projectileTerrainCheck = false')
    && code.includes('_GameData:IsSkillLineUnblocked(self.Entity.CurrentMap,'),
    `${side} projectile impact/pierce terrain guard missing`);
}
const result={status:errors.length?'FAIL_STATIC':'PASS_STATIC',scope:'66 identity/data/adapter/report contracts only',
  makerBuild:'NOT_EVALUATED_BY_STATIC_SCRIPT',makerRuntime:'NOT_EVALUATED_BY_STATIC_SCRIPT',
  runtimeEvidence:'Read the current dated Maker logs and QA report separately; this script does not evaluate runtime.',
  counts:{skills:skillRows.length,monsters:monsters.size,eligible:eligible.length,behaviors:allowed.size},errors};
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=1;
