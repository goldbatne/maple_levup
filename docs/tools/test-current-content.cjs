#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const {load, validate, parseCsv} = require('./verify-current-content.cjs');
const original = load();
assert.equal(validate(original).status, 'PASS_STATIC');
const cases = {
  duplicateSkill: d => d.SkillTable.push({...d.SkillTable[0]}),
  missingAbility: d => { d.MonsterTable[0].drop_skill_id = 'not_a_skill'; },
  brokenRoom: d => { d.RoomTable[0].conn_north = 'missing_room'; },
  layerMismatch: d => { d.SkillTable.find(s => s.layer_ruids).layer_durations = ''; },
  invalidRuid: d => { d.SkillTable[0].icon_ruid = 'not-a-resource'; },
  zeroDuration: d => { const s = d.SkillTable.find(s => s.layer_ruids); s.layer_durations = s.layer_durations.replace(/^[^|]+/, '0'); },
  supplyDrift: d => { d.GameBalance.find(r => r.key === 'run_skill_supply_interval').value = '2'; },
  invalidNumeric: d => { const s = d.SkillTable.find(s => s.layer_ruids); s.layer_offsets_x = 'NaN'; }
};
for (const table of ['MonsterTable', 'SkillTable', 'RoomTable', 'AreaTable', 'GameBalance']) {
  cases['empty' + table] = d => { d[table] = []; };
  cases['missing' + table] = d => { delete d[table]; };
}
for (const table of ['MonsterTable', 'SkillTable', 'RoomTable', 'AreaTable']) {
  cases['missingName' + table] = d => { delete d[table][0].name; };
  cases['blankName' + table] = d => { d[table][0].name = '   '; };
}
const requiredNumeric = {
  MonsterTable: ['level', 'hp', 'def', 'exp'],
  SkillTable: ['coefficient', 'cooldown', 'max_targets', 'effect_value', 'duration', 'range', 'dash_distance', 'tier', 'icon_ratio'],
  RoomTable: ['monster_count', 'portal_x', 'portal_y'],
  AreaTable: ['sort_order'], GameBalance: ['value']
};
for (const [table, fields] of Object.entries(requiredNumeric)) for (const field of fields) {
  for (const value of ['not-a-number', '', 'Infinity']) cases[`${table}.${field}=${value}`] = d => { d[table][0][field] = value; };
  cases[`${table}.${field}=missing`] = d => { delete d[table][0][field]; };
}
for (const [table, fields] of Object.entries({SkillTable: ['passive_value'], RoomTable: ['gate_value', 'monster_level']})) for (const field of fields) {
  cases[`${table}.${field}=invalid`] = d => { d[table][0][field] = 'not-a-number'; };
  cases[`${table}.${field}=missing`] = d => { delete d[table][0][field]; };
  const data = structuredClone(original); data[table][0][field] = ''; assert.equal(validate(data).status, 'PASS_STATIC', `${table}.${field} permits blank default`);
}
for (const [name, mutate] of Object.entries(cases)) { const data = structuredClone(original); mutate(data); assert.equal(validate(data).status, 'FAIL', name); }
const zeroCooldown = structuredClone(original);
zeroCooldown.SkillTable.find(s => s.skill_kind === 'attack').cooldown = '0';
assert.equal(validate(zeroCooldown).status, 'PASS_STATIC', 'zero cooldown must not be rebalanced by this integrity check');
assert.equal(parseCsv('id,name\r\na,"comma, and ""quote"""\r\n')[0].name, 'comma, and "quote"');
assert.throws(() => parseCsv('id,name\na,b,c\n'));
console.log(`PASS: current data + ${Object.keys(cases).length} negative in-memory mutations + optional blank/zero cooldown compatibility + CSV quoting/width checks. No game files written.`);
