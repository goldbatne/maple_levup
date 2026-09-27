#!/usr/bin/env node
'use strict';
// Static contracts only. This cannot certify Maker build or runtime behavior.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
function readCsv(relative) {
  const text = fs.readFileSync(path.join(root, relative), 'utf8').replace(/^\uFEFF/, '');
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i=0; i<text.length; i++) {
    const c=text[i];
    if (c==='"') { if (quoted && text[i+1]==='"') { cell+='"'; i++; } else quoted=!quoted; }
    else if (c===',' && !quoted) { row.push(cell); cell=''; }
    else if ((c==='\r' || c==='\n') && !quoted) {
      if (c==='\r' && text[i+1]==='\n') i++;
      row.push(cell); if (row.some(Boolean)) rows.push(row); row=[]; cell='';
    } else cell+=c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const headers=rows.shift();
  return rows.map(values => Object.fromEntries(headers.map((h,i)=>[h,values[i]??''])));
}
const skill=readCsv('RootDesk/MyDesk/GameData/SkillTable.csv');
const monsters=readCsv('RootDesk/MyDesk/GameData/MonsterTable.csv');
const prior=readCsv('docs/reports/skill-diversity-rework-20260922/SKILL_AFTER.csv');
const report=readCsv('docs/reports/skill-diversity-lore-rework-20260924/LORE_DESIGN_66.csv');
const byId=new Map(skill.map(s=>[s.id,s]));
const byMonster=new Map(monsters.map(m=>[m.id,m]));
const priorById=new Map(prior.map(r=>[r.SkillID,r]));
const failures=[];
const requireIt=(ok,message)=>{if(!ok) failures.push(message);};
const playerCode=fs.readFileSync(path.join(root,'RootDesk/MyDesk/PlayerAttack.mlua'),'utf8');
const monsterCode=fs.readFileSync(path.join(root,'RootDesk/MyDesk/MonsterAttack.mlua'),'utf8');
const gameDataCode=fs.readFileSync(path.join(root,'RootDesk/MyDesk/GameData/GameData.mlua'),'utf8');
requireIt(report.length===66,`report count ${report.length}`);
requireIt(new Set(report.map(r=>r.SkillID)).size===66,'duplicate SkillID in lore report');
let behaviorChanges=0, secondaryChanges=0, tooltipChanges=0;
for(const r of report) {
  const s=byId.get(r.SkillID), m=byMonster.get(r.MonsterID), p=priorById.get(r.SkillID);
  requireIt(!!s && !!m && !!p,`missing linked data ${r.SkillID}`);
  if(!s || !m || !p) continue;
  requireIt(m.drop_skill_id===s.id,`monster→skill mismatch ${r.SkillID}`);
  requireIt(m.name===r.MonsterName && s.name===r.SkillName,`identity mismatch ${r.SkillID}`);
  requireIt(['attack','defense'].includes(s.skill_kind),`ineligible kind ${r.SkillID}`);
  requireIt(s.behavior===r.AfterBehavior && s.secondary_effect===r.AfterSecondary,`behavior mismatch ${r.SkillID}`);
  if(r.BeforeBehavior!==r.AfterBehavior && !r.AfterBehavior.includes('PROJECTILE')) {
    requireIt(s.projectile_ruid==='' && Number(s.dash_distance)===0,`spatial change bypassed by projectile/dash dispatch ${r.SkillID}`);
    requireIt(Number(s.behavior_width)>0,`spatial width missing ${r.SkillID}`);
  }
  if(r.AfterBehavior==='DELAYED_BLAST' && r.BeforeBehavior!==r.AfterBehavior)
    requireIt(Number(s.behavior_delay)>0 && Number(s.behavior_ticks)===1,`delayed blast contract ${r.SkillID}`);
  if(r.BeforeSecondary!==r.AfterSecondary)
    requireIt(Number(s.secondary_value)>0 && Number(s.secondary_duration)>0,`secondary effect magnitude ${r.SkillID}`);
  requireIt(s.description===r.AfterTooltip,`tooltip mismatch ${r.SkillID}`);
  requireIt(s.icon_ruid===r.IconRUID && s.icon_ruid===p.IconRUID,`icon changed ${r.SkillID}`);
  const vfx=s.layer_ruids || s.effect_ruid;
  const priorVfx=s.projectile_ruid ? `${s.projectile_ruid}|${vfx}` : vfx;
  requireIt(vfx===r.VFXRUID && priorVfx===p.VFX,`VFX changed ${r.SkillID}`);
  requireIt(s.projectile_ruid===r.ProjectileRUID,`projectile changed ${r.SkillID}`);
  for(const [now,old] of [['coefficient','Coefficient'],['range','Range'],['max_targets','MaxTargets']])
    requireIt(s[now]===p[old],`${now} changed ${r.SkillID}`);
  requireIt(r.SourceType==='PROJECT_ONLY' || r.SourceURL.startsWith('https://maplestorywiki.net/w/'),`unclassified source ${r.SkillID}`);
  requireIt(r.MakerPlayer==='NOT_RUN' && r.MakerMonster==='NOT_RUN',`unearned runtime PASS ${r.SkillID}`);
  if(r.BeforeBehavior!==r.AfterBehavior) behaviorChanges++;
  if(r.BeforeSecondary!==r.AfterSecondary) secondaryChanges++;
  if(r.BeforeTooltip!==r.AfterTooltip) tooltipChanges++;
  if(r.BeforeBehavior===r.AfterBehavior && r.BeforeSecondary===r.AfterSecondary)
    requireIt(r.BeforeTooltip===r.AfterTooltip,`unjustified tooltip edit ${r.SkillID}`);
}
requireIt(behaviorChanges===6,`expected 6 confirmed behavior changes, got ${behaviorChanges}`);
requireIt(secondaryChanges===0,`unexpected secondary changes: ${secondaryChanges}`);
requireIt(tooltipChanges===6,`expected 6 confirmed tooltip changes, got ${tooltipChanges}`);
requireIt(byId.get('s_mon_shark')?.behavior==='PROJECTILE_BLAST' && byId.get('s_mon_shark')?.max_targets==='1',
  'shark single-target impact contract changed');
requireIt(byId.get('s_mon_mateon')?.behavior==='PROJECTILE' && byId.get('s_mon_mateon')?.max_targets==='1',
  'mateon single-projectile contract changed');
for(const field of ['behavior','behavior_width','behavior_delay','behavior_ticks','secondary_effect','secondary_value','secondary_duration'])
  requireIt(gameDataCode.includes(`GetItem("${field}")`),`GameData does not load ${field}`);
for(const behavior of ['FRONT_CONE','DELAYED_BLAST','DAMAGE_ZONE']) {
  requireIt(playerCode.includes(`"${behavior}"`),`Player adapter missing ${behavior}`);
  requireIt(monsterCode.includes(`"${behavior}"`),`Monster adapter missing ${behavior}`);
}
requireIt(playerCode.includes('ApplySecondaryEffects(skill, hits, point)'), 'Player secondary path missing');
requireIt(monsterCode.includes('ApplyPlayerSecondaryEffects(skill, hits, point)'), 'Monster secondary path missing');
const result={status:failures.length?'FAIL':'PASS_STATIC_ONLY',skills:report.length,behaviorChanges,secondaryChanges,tooltipChanges,
  makerBuild:'NOT_RUN',playerRuntime:'NOT_RUN',monsterRuntime:'NOT_RUN',failures};
console.log(JSON.stringify(result,null,2));
if(failures.length) process.exitCode=1;
