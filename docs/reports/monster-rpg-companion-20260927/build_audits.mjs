import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '../../..');
const out = import.meta.dirname;
function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') { field += '"'; i++; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { row.push(field); field = ''; }
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); field = '';
      if (row.some(x => x !== '')) rows.push(row);
      row = [];
    } else field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  const header = rows.shift();
  return rows.map(cells => Object.fromEntries(header.map((h, i) => [h, cells[i] ?? ''])));
}
function csvCell(value) {
  const text = String(value ?? '');
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}
function write(name, headers, rows) {
  const body = [headers, ...rows.map(row => headers.map(h => row[h] ?? ''))]
    .map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n';
  fs.writeFileSync(path.join(out, name), '\ufeff' + body, 'utf8');
}
const monsters = parseCsv(fs.readFileSync(path.join(root,
  'Mislocated/MyDesk/GameData/MonsterTable.csv'), 'utf8').replace(/^\ufeff/, ''));
const skills = parseCsv(fs.readFileSync(path.join(root,
  'Mislocated/MyDesk/GameData/SkillTable.csv'), 'utf8').replace(/^\ufeff/, ''));
const balance = parseCsv(fs.readFileSync(path.join(root,
  'Mislocated/MyDesk/GameData/GameBalance.csv'), 'utf8').replace(/^\ufeff/, ''));
const value = Object.fromEntries(balance.map(row => [row.key, row.value]));
const byId = new Map(skills.map(s => [s.id, s]));
const tameable = monsters.filter(m => m.drop_skill_id && byId.has(m.drop_skill_id));
const linked = tameable.map(m => ({ monster: m, skill: byId.get(m.drop_skill_id) }));
const active = linked.filter(({skill}) => skill.source === 'monster'
  && skill.slot_type === 'monster' && skill.skill_kind !== 'passive');
const duplicateSkills = linked.map(x => x.skill.id).filter((id, i, all) => all.indexOf(id) !== i);
if (tameable.length !== 101 || active.length !== 66 || duplicateSkills.length) {
  throw new Error(`expected 101/66/unique, got ${tameable.length}/${active.length}/${duplicateSkills.length}`);
}
const code = Object.fromEntries([
  'collection','combat','save','ui'].map((kind, i) => [kind, fs.readFileSync(path.join(root, [
    'RootDesk/MyDesk/Progress/PlayerCollection.mlua',
    'RootDesk/MyDesk/Combat/CompanionCombat.mlua',
    'RootDesk/MyDesk/Save/PlayerDBManager.mlua',
    'RootDesk/MyDesk/UI/EquipPanel.mlua'][i]), 'utf8')]));
const checks = {
  team_slots: code.collection.includes('RequestEquipCompanion(integer slot'),
  team_unique: code.collection.includes('i ~= slot and self:GetEquippedCompanion(i) == monsterId'),
  own_skill: code.combat.includes('_GameData:GetMonster(monsterId)')
    && code.combat.includes('_GameData:GetSkill(monster.drop_skill_id)'),
  legacy_loadout_inactive: code.collection.includes('if _GameData:GetBalance("roguelite_run_mode_enabled") >= 0.5 then return end'),
  level_save: code.save.includes('payload.monster_levels[monsterId] = level'),
  enhance_save: code.save.includes('payload.monster_enhances[monsterId] = enhance'),
  three_slot_ui: code.ui.includes('collection:RequestEquipCompanion(index,'),
  balance_rows: ['monster_level_cap','monster_enhance_cap','monster_essence_per_kill',
    'monster_essence_per_boss_kill','companion_formation_radius'].every(k=>value[k]!==undefined)
};
if (Object.values(checks).some(v=>!v)) throw new Error(JSON.stringify(checks));
const growthRows = linked.map(({monster:m,skill:s}) => ({
  MonsterID:m.id, MonsterName:m.name, OwnSkillID:s.id,
  HasActiveSkill:active.some(x=>x.monster.id===m.id)?'YES':'NO',
  BaseStats:`Run companion HP ${value.companion_base_hp}; ATK ${value.companion_base_attack}; monster source HP ${m.hp}; DEF ${m.def}`,
  Level:'ACCOUNT_SPECIFIC_NOT_EXPORTED', Enhance:'ACCOUNT_SPECIFIC_NOT_EXPORTED',
  TameRate:`first ${value.first_capture_rate}; duplicate ${value.duplicate_capture_rate}`,
  CompanionEligible:m.companion_visual_ruid?'YES':'NO',
  StaticMapping:'PASS', Runtime:'NOT_RUN'
}));
write('MONSTER_GROWTH_AUDIT.csv', Object.keys(growthRows[0]), growthRows);
const ownRows = active.map(({monster:m,skill:s}) => ({
  MonsterID:m.id, MonsterName:m.name, OwnSkillID:s.id, SkillName:s.name,
  SkillKind:s.skill_kind, Behavior:s.behavior, SkillCooldown:s.cooldown,
  IconRUID:s.icon_ruid, EffectRUID:s.effect_ruid, ProjectileRUID:s.projectile_ruid,
  CompanionVisualRUID:m.companion_visual_ruid,
  OwnSkillCodePath:'CompanionCombat.Configure -> MonsterTable.drop_skill_id',
  StaticMapping:'PASS', PlayerRuntime:'NOT_RUN', CompanionRuntime:'NOT_RUN'
}));
write('MONSTER_OWN_SKILL_AUDIT.csv', Object.keys(ownRows[0]), ownRows);
for (const [name, scenarios] of Object.entries({
  'COMPANION_3_FORMATION_TEST.csv': ['3 unique slots','3 spawn','0/120/240 formation',
    'moving follow','independent target','own skill only','target death return','portal respawn','boss','4P load'],
  'MONSTER_LEVEL_ENHANCE_TEST.csv': ['first tame Lv1','duplicate tame level','kill essence',
    'enhance cost','separate level/enhance','self HP/attack/skill growth','player unchanged'],
  'SAVE_MIGRATION_TEST.csv': ['schema2 to schema3','star to level','selected to slot1',
    'legacy loadout preserved but inactive','currency persist','three slots persist','reconnect'],
  'REGRESSION_TEST.csv': ['Random5','5s supply','Skill Drop','OwnedSkillPool',
    'Run chest','Mega Area','Portal','Boss','Run reset','Build errors','Runtime errors']
})) write(name, ['Scenario','StaticResult','MakerRuntime','Evidence'],
  scenarios.map(Scenario=>({Scenario,StaticResult:'PENDING_REVIEW',MakerRuntime:'NOT_RUN',Evidence:''})));
console.log(JSON.stringify({tameable:tameable.length,active:active.length,
  passiveOrUnavailable:tameable.length-active.length,duplicateSkills:duplicateSkills.length,checks}));
