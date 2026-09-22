'use strict';
// Read-only source contracts plus a pure state policy model; NOT Maker runtime.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../../..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const game = read('RootDesk/MyDesk/GameData/GameData.mlua');
const collection = read('RootDesk/MyDesk/Progress/PlayerCollection.mlua');
const slots = read('RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua');
const db = read('RootDesk/MyDesk/Save/PlayerDBManager.mlua');
function method(source, name) {
  const match = source.match(new RegExp('^    method \\S+ ' + name + '\\([^\\n]*\\)\\r?\\n([\\s\\S]*?)^    end\\s*$', 'm'));
  assert.ok(match, 'Missing method ' + name); return match[1];
}
function checkSource(g, c, s, d) {
  const grant = method(c, 'GrantRogueliteAbility');
  assert.doesNotMatch(grant, /self\.RogueDiscovered(?:Monsters|Abilities)\[/);
  assert.match(grant, /_GameData:StageRogueliteDiscovery\(self.Entity.PlayerComponent.UserId, monsterId, ""\)/);
  assert.match(grant, /if acquired then _GameData:StageRogueliteDiscovery/);
  assert.match(grant, /self.TotalMonsterKills\[monsterId\] = self:GetTotalMonsterKills\(monsterId\) \+ 1/);
  const stage = method(g, 'StageRogueliteDiscovery');
  assert.match(stage, /RogueRunResult ~= "ACTIVE"/);
  assert.match(stage, /self:IsRunParticipant\(userId\) == false/);
  assert.match(stage, /RogueParticipantResults\[userId\] == "ABANDONED"/);
  assert.match(stage, /self.RoguePendingDiscoveries\[userId\] = pending/);
  const settle = method(c, 'FinalizeRogueliteDiscoveries');
  assert.match(settle, /RogueParticipantResults\[userId\] == "ABANDONED"/);
  assert.match(settle, /result ~= "CLEAR" and result ~= "FAILED"/);
  assert.match(settle, /_GameData.RogueRunResult ~= result/);
  assert.match(settle, /_GameData:IsRunParticipant\(userId\) == false/);
  assert.match(settle, /self.RogueDiscoveredMonsters\[monsterId\] = 1/);
  assert.match(settle, /self.RogueDiscoveredAbilities\[skillId\] = 1/);
  assert.doesNotMatch(settle, /RogueDiscovered(?:Monsters|Abilities)\[.*\] = nil|RogueSavedPayload\s*=/);
  assert.match(settle, /DiscardRogueliteDiscoveries\(userId\)/);
  assert.match(settle, /self:MarkSave\(/);
  const clear = method(g, 'CompleteRogueliteRun');
  const fail = method(g, 'CheckRogueliteRunFailure');
  for (const [body, result] of [[clear, 'CLEAR'], [fail, 'FAILED']]) {
    assert.ok(body.indexOf('self.RogueRunResult = "' + result + '"') < body.indexOf('self:FinalizeRogueliteParticipantDiscoveries("' + result + '")'));
    assert.match(body, /self:FinalizeRogueliteParticipantDiscoveries\(/);
  }
  const abandon = method(g, 'AbandonRogueliteParticipant');
  assert.match(abandon, /self.RogueRunResult ~= "ACTIVE"/);
  assert.ok(abandon.indexOf('self.RogueParticipantResults[userId] = "ABANDONED"') < abandon.indexOf('self:DiscardRogueliteDiscoveries(userId)'));
  assert.match(method(s, 'EndRogueliteRun'), /_GameData:DiscardRogueliteDiscoveries/);
  assert.match(method(g, 'GenerateRogueliteGraph'), /self.RoguePendingDiscoveries = \{\}/);
  assert.match(method(g, 'RegisterRunParticipant'), /collection:FinalizeRogueliteDiscoveries\(self.RogueRunResult\)/);
  // SaveNow, settings dirty and UserLeave ultimately use GatherRogueliteRecords.
  // Pending must not enter any DB serialization source, even temporarily.
  assert.doesNotMatch(d, /RoguePendingDiscoveries/);
  assert.match(method(d, 'GatherRogueliteRecords'), /local payload = self.RogueSavedPayload/);
}
checkSource(game, collection, slots, db);
assert.throws(() => checkSource(game, collection.replace('_GameData:StageRogueliteDiscovery(self.Entity.PlayerComponent.UserId, monsterId, "")', 'self.RogueDiscoveredMonsters[monsterId] = 1'), slots, db));
assert.throws(() => checkSource(game, collection, slots, db + '\n-- RoguePendingDiscoveries serialized here'));

// Explicit policy reference model. This verifies state expectations separately
// from the source structure assertions above, not engine execution or storage I/O.
function world() {
  return {result: 'ACTIVE', members: new Set(['a', 'b']), abandoned: new Set(), pending: {}, dirty: {},
    permanent: {a: {monsters: {old: 1, unknown_future: 1}, abilities: {old_ability: 1}}, b: {monsters: {}, abilities: {}}}};
}
function stage(w, id, monster, ability) {
  if (w.result !== 'ACTIVE' || !w.members.has(id) || w.abandoned.has(id)) return;
  const p = w.pending[id] ||= {monsters: {}, abilities: {}};
  p.monsters[monster] = 1; if (ability) p.abilities[ability] = 1;
}
function settle(w, id, result) {
  if (w.abandoned.has(id)) { delete w.pending[id]; return; }
  if (!['CLEAR', 'FAILED'].includes(result) || w.result !== result || !w.members.has(id)) return;
  const p = w.pending[id]; if (!p) return;
  Object.assign(w.permanent[id].monsters, p.monsters);
  Object.assign(w.permanent[id].abilities, p.abilities);
  delete w.pending[id]; w.dirty[id] = (w.dirty[id] || 0) + 1;
}
function abandon(w, id) {
  if (w.result !== 'ACTIVE' || !w.members.has(id)) return;
  w.abandoned.add(id); w.members.delete(id); delete w.pending[id];
  if (!w.members.size) w.result = 'ABANDONED';
}
const tested = [];
function test(name, fn) { fn(); tested.push(name); }
test('autosave/settings-save/leave-save omit pending', () => {
  const w = world(), before = JSON.stringify(w.permanent.a);
  stage(w, 'a', 'new_monster', 'new_ability');
  for (const reason of ['autosave', 'settings', 'SaveNow', 'UserLeave']) assert.equal(JSON.stringify(w.permanent.a), before, reason);
});
test('abandon preserves all old/future IDs; late clear cannot add pending', () => {
  const w = world(), before = structuredClone(w.permanent.a);
  stage(w, 'a', 'new_monster', 'new_ability'); abandon(w, 'a');
  w.result = 'CLEAR'; settle(w, 'a', 'CLEAR');
  assert.deepEqual(w.permanent.a, before); assert.equal(w.pending.a, undefined);
});
for (const result of ['CLEAR', 'FAILED']) test(result + ' additive and idempotent', () => {
  const w = world(); stage(w, 'a', 'new_monster', 'new_ability');
  w.result = result; settle(w, 'a', result); settle(w, 'a', result);
  assert.equal(w.permanent.a.monsters.new_monster, 1); assert.equal(w.permanent.a.abilities.new_ability, 1);
  assert.equal(w.permanent.a.monsters.unknown_future, 1); assert.equal(w.dirty.a, 1); assert.equal(w.pending.a, undefined);
});
test('clear first cannot be overwritten by abandon', () => {
  const w = world(); stage(w, 'a', 'new', 'ability'); w.result = 'CLEAR'; settle(w, 'a', 'CLEAR'); abandon(w, 'a');
  assert.equal(w.result, 'CLEAR'); assert.equal(w.abandoned.has('a'), false); assert.equal(w.permanent.a.monsters.new, 1);
});
test('one participant abandonment leaves other pending intact', () => {
  const w = world(); stage(w, 'a', 'a_mon', 'a_skill'); stage(w, 'b', 'b_mon', 'b_skill');
  abandon(w, 'a'); assert.equal(w.result, 'ACTIVE'); assert.equal(w.pending.b.monsters.b_mon, 1);
  w.result = 'CLEAR'; settle(w, 'b', 'CLEAR'); assert.equal(w.permanent.a.monsters.a_mon, undefined); assert.equal(w.permanent.b.monsters.b_mon, 1);
});
test('entity recreation retains pending only in live server Run', () => {
  const w = world(); stage(w, 'a', 'new', 'ability');
  w.permanent.a = JSON.parse(JSON.stringify(w.permanent.a));
  assert.equal(w.permanent.a.monsters.new, undefined); assert.equal(w.pending.a.monsters.new, 1);
});
test('new Run resets transient pending; no old permanent deletion', () => {
  const w = world(); stage(w, 'a', 'new', 'ability'); w.pending = {};
  assert.deepEqual(w.pending, {}); assert.equal(w.permanent.a.monsters.old, 1);
});
console.log(JSON.stringify({status: 'PASS_STATIC_AND_POLICY_MODEL', sourceNegativeTests: 2, policyModelTests: tested, runtime: 'NOT_RUN', storageWrites: false}, null, 2));
