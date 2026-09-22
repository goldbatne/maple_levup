#!/usr/bin/env node
'use strict';
// Current Mega Area data integrity gate. Does not execute or modify MSW files.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');

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
  if (quoted) throw new Error('Unterminated quoted CSV cell');
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const headers = rows.shift() || [];
  if (new Set(headers).size !== headers.length) throw new Error('Duplicate CSV header');
  return rows.map((values, i) => {
    if (values.length !== headers.length) throw new Error(`CSV row ${i + 2}: ${values.length} cells, expected ${headers.length}`);
    return Object.fromEntries(headers.map((h, j) => [h, values[j]]));
  });
}
function load(base = root) {
  return Object.fromEntries(['MonsterTable', 'SkillTable', 'RoomTable', 'AreaTable', 'GameBalance'].map(name =>
    [name, parseCsv(fs.readFileSync(path.join(base, 'RootDesk/MyDesk/GameData', name + '.csv'), 'utf8'))]));
}
function validate(data) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  const requiredTables = ['MonsterTable', 'SkillTable', 'RoomTable', 'AreaTable', 'GameBalance'];
  for (const name of requiredTables) check(Array.isArray(data[name]) && data[name].length > 0, `${name}: missing or empty required table`);
  if (errors.length) return {status: 'FAIL', scope: 'CSV identity/link/reference integrity and current configuration only', runtime: 'NOT_RUN', counts: {}, errors};
  // Current CSV contracts: validate representation, not gameplay balance.
  // Zero cooldown/range/effect values are valid; optional legacy/default fields
  // retain their existing blank-cell behavior in GameData.ToNumber.
  const numericFields = {
    MonsterTable: ['level', 'hp', 'def', 'exp'],
    SkillTable: ['coefficient', 'cooldown', 'max_targets', 'effect_value', 'duration', 'range', 'dash_distance', 'tier', 'icon_ratio'],
    RoomTable: ['monster_count', 'portal_x', 'portal_y'],
    AreaTable: ['sort_order'],
    GameBalance: ['value']
  };
  const optionalNumericFields = {SkillTable: ['passive_value'], RoomTable: ['gate_value', 'monster_level']};
  for (const [name, rows] of Object.entries(data)) {
    const key = name === 'GameBalance' ? 'key' : 'id';
    const ids = rows.map(r => r[key]);
    check(ids.every(id => typeof id === 'string' && id.trim() !== ''), `${name}: missing ID`);
    check(new Set(ids).size === ids.length, `${name}: duplicate ID`);
    for (const row of rows) {
      const label = `${name}:${row[key] || '<missing ID>'}`;
      if (name !== 'GameBalance') check(typeof row.name === 'string' && row.name.trim() !== '', `${label}: missing name`);
      for (const field of [...(numericFields[name] || []), ...(optionalNumericFields[name] || [])]) {
        const present = typeof row[field] === 'string';
        const value = present ? row[field].trim() : '';
        const optionalBlank = (optionalNumericFields[name] || []).includes(field) && value === '';
        check(present && (optionalBlank || (value !== '' && Number.isFinite(Number(value)))), `${label}: missing or nonnumeric ${field}`);
      }
    }
  }
  const skills = new Map(data.SkillTable.map(s => [s.id, s]));
  const monsters = new Map(data.MonsterTable.map(m => [m.id, m]));
  const areas = new Set(data.AreaTable.map(a => a.id));
  const rooms = new Set(data.RoomTable.map(r => r.id));
  const linked = new Set();
  for (const m of data.MonsterTable) {
    if (m.drop_skill_id) {
      check(skills.has(m.drop_skill_id), `${m.id}: missing drop skill ${m.drop_skill_id}`);
      linked.add(m.drop_skill_id);
    }
    for (const id of (m.combat_skill_ids || '').split('|').filter(Boolean)) check(skills.has(id), `${m.id}: missing combat skill ${id}`);
  }
  for (const r of data.RoomTable) {
    if (r.monster_id) check(monsters.has(r.monster_id), `${r.id}: missing monster`);
    if (r.area_id) check(areas.has(r.area_id), `${r.id}: missing area`);
    for (const d of ['north', 'south', 'east', 'west']) if (r['conn_' + d]) check(rooms.has(r['conn_' + d]), `${r.id}: missing connected room`);
  }
  const active = [...linked].map(id => skills.get(id)).filter(s => s && ['attack', 'defense'].includes(s.skill_kind));
  const passive = [...linked].map(id => skills.get(id)).filter(s => s?.skill_kind === 'passive');
  const legacy = data.SkillTable.filter(s => s.source === 'monster' && !linked.has(s.id));
  check(linked.size === 101, `linked monster abilities: ${linked.size}, expected 101`);
  check(active.length === 66, `linked usable abilities: ${active.length}, expected 66`);
  check(passive.length === 35, `linked passive abilities: ${passive.length}, expected 35`);
  check(legacy.length === 1 && legacy[0].id === 's_mon_snail', 'Unexpected unlinked monster skill (only legacy s_mon_snail is documented)');
  const fields = ['layer_ruids', 'layer_types', 'layer_styles', 'layer_delays', 'layer_durations', 'layer_scales', 'layer_offsets_x', 'layer_offsets_y', 'layer_drifts_x', 'layer_drifts_y'];
  const ruid = /^(thumbnail:\/\/)?[0-9a-f]{32}$/;
  for (const s of data.SkillTable) {
    if (s.source === 'monster' || s.source === 'boss') check(ruid.test(s.icon_ruid), `${s.id}: invalid icon RUID`);
    const lists = Object.fromEntries(fields.map(f => [f, s[f] ? s[f].split('|') : []]));
    const n = lists.layer_ruids.length;
    for (const f of fields) check(lists[f].length === n, `${s.id}: ${f} length mismatch`);
    for (let i = 0; i < n; i++) {
      // GameData parses comma-separated frame RUIDs inside a pipe-separated
      // sprite_sequence layer; SkillEffect assigns duration / frame count.
      const type = lists.layer_types[i];
      const frames = type === 'sprite_sequence' ? lists.layer_ruids[i].split(',') : [lists.layer_ruids[i]];
      for (const value of frames) check(/^[0-9a-f]{32}$/.test(value), `${s.id}: invalid layer/frame RUID`);
      check(['sprite', 'animationclip', 'sprite_sequence'].includes(type), `${s.id}: invalid layer type`);
      if (type === 'sprite_sequence') check(lists.layer_styles[i] === 'sequence', `${s.id}: sequence style mismatch`);
    }
    for (const f of fields.slice(3)) for (const value of lists[f]) {
      const number = Number(value);
      check(value.trim() !== '' && Number.isFinite(number), `${s.id}: nonnumeric ${f}`);
      if (['layer_durations', 'layer_scales'].includes(f)) check(number > 0, `${s.id}: nonpositive ${f}`);
      if (f === 'layer_delays') check(number >= 0, `${s.id}: negative delay`);
    }
    for (const f of ['effect_ruid', 'projectile_ruid', 'sfx_ruid']) if (s[f]) check(ruid.test(s[f]), `${s.id}: invalid ${f}`);
    if (s.skill_kind !== 'passive' && ['monster', 'boss'].includes(s.source)) check(n > 0 || s.effect_ruid || s.projectile_ruid, `${s.id}: missing VFX reference`);
  }
  const balance = Object.fromEntries(data.GameBalance.map(r => [r.key, Number(r.value)]));
  for (const [key, expected] of Object.entries({roguelite_run_mode_enabled: 1, run_skill_slot_max: 5, run_skill_supply_interval: 5, run_ability_acquire_rate: 0.1, run_party_max: 4}))
    check(balance[key] === expected, `${key}: ${balance[key]}, expected ${expected}`);
  return {status: errors.length ? 'FAIL' : 'PASS_STATIC', scope: 'CSV identity/link/reference integrity and current configuration only', runtime: 'NOT_RUN', counts: {monsterDefinitions: data.MonsterTable.length, skillDefinitions: data.SkillTable.length, monsterSkillDefinitions: data.SkillTable.filter(s => s.source === 'monster').length, linkedMonsterAbilities: linked.size, usableAbilities: active.length, inactivePassiveAbilities: passive.length, legacyUnlinked: legacy.map(s => s.id), areas: areas.size, rooms: rooms.size}, errors};
}
function main() {
  try { const result = validate(load()); console.log(JSON.stringify(result, null, 2)); process.exitCode = result.errors.length ? 1 : 0; }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = {parseCsv, load, validate, main};
if (require.main === module) main();
