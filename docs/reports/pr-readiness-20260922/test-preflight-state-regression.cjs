'use strict';
// Read-only actual-source mutation coverage. Not a runtime generator result.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../../..');
const file = 'RootDesk/MyDesk/GameData/GameData.mlua';
const source = fs.readFileSync(path.join(root, file), 'utf8');

function methods(text) {
  return new Map([...text.matchAll(/^    method \S+ (\w+)\([^\n]*\)\r?\n([\s\S]*?)^    end\s*$/gm)].map(m => [m[1], m[2]]));
}
function verify(text) {
  const catalog = methods(text);
  const preflight = catalog.get('ValidateRogueliteBeforeRoomCreation');
  assert.ok(preflight, 'Missing preflight');
  const savedTable = preflight.match(/local saved = \{([\s\S]*?)\}/)?.[1];
  assert.ok(savedTable, 'Missing snapshot');
  const snapshots = new Map([...savedTable.matchAll(/(\w+)\s*=\s*self\.(Rogue\w+)/g)].map(m => [m[2], m[1]]));
  const restores = new Map([...preflight.matchAll(/self\.(Rogue\w+)\s*=\s*saved\.(\w+)/g)].map(m => [m[1], m[2]]));
  const visited = new Set();
  const writes = new Set(['RogueAreaId', 'RogueSeed']);
  function inspect(name) {
    if (visited.has(name)) return;
    visited.add(name);
    const body = catalog.get(name);
    assert.ok(body, 'Generator helper not found: ' + name);
    for (const m of body.matchAll(/self\.(Rogue\w+)(?:\[[^\]\n]+\])*\s*(?:\+=|-=|\*=|\/=|=(?!=))/g)) writes.add(m[1]);
    for (const m of body.matchAll(/self:(\w+)\(/g)) inspect(m[1]);
  }
  inspect('GenerateRogueliteGraph');
  for (const field of writes) {
    assert.ok(snapshots.has(field), 'Generator writes unsnapshotted state: ' + field);
    assert.equal(restores.get(field), snapshots.get(field), 'Snapshot restore mismatch: ' + field);
  }
  const generateAt = preflight.indexOf('self:GenerateRogueliteGraph()');
  assert.ok(generateAt > preflight.indexOf('local saved ='));
  for (const field of writes) assert.ok(preflight.indexOf('self.' + field + ' = saved.') > generateAt, 'Restore must follow generation: ' + field);
  return {fields: [...writes].sort(), helpers: visited.size};
}
const coverage = verify(source);
const negatives = [
  source.replace('revision = self.RogueRunRevision,', ''),
  source.replace('self.RogueRunFailed = saved.failed', 'self.RogueRunFailed = saved.complete'),
  source.replace('self.RogueRunRevision += 1', 'self.RogueUnexpectedState = true\n        self.RogueRunRevision += 1')
];
for (const mutated of negatives) assert.throws(() => verify(mutated));
console.log(JSON.stringify({status: 'PASS_STATIC', file, scope: 'generator/helper mutation fields have matching preflight snapshot and restore', ...coverage, negativeTests: negatives.length, runtime: 'NOT_RUN', writes: false}, null, 2));
