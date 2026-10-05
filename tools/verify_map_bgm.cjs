// Read-only project verification. Temporary Git snapshots are not Maker entries.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { MapBuilder } = require('../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs');
const mapping = require('../docs/reports/map-bgm-mapping-20261005.json');
const catalog = require('../docs/reports/map-bgm-official-catalog-20261005.json');

async function main() {
  const files = fs.readdirSync('map').filter(f => f.endsWith('.map'));
  assert.equal(files.length, 162);
  assert.equal(mapping.maps.length, 162);
  const records = new Map(mapping.maps.map(r => [r.map, r]));
  assert.equal(records.size, 162);
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'msw-bgm-verify-'));
  const snapshotPath = path.join(scratch, 'original.map');
  try {
    for (const file of files) {
      const name = file.slice(0, -4);
      const record = records.get(name);
      const map = MapBuilder.read(path.join('map', file));
      const sound = map.component(name, 'MOD.Core.SoundComponent');
      assert.ok(sound);
      assert.equal(sound.AudioClipRUID, record.ruid);
      for (const flag of ['Bgm', 'KeepBGM', 'Loop', 'PlayOnEnable', 'Enable']) assert.equal(sound[flag], true);
      assert.equal(sound.Mute, false);
      assert.equal(sound.Volume, 0.35);
      assert.equal(sound.Pitch, 1);
      const official = catalog.resources.find(r => r.id === record.ruid);
      assert.equal(official.type, 'bgm');
      assert.ok(official.sourceTags.path.includes(record.path));
      assert.ok(official.sourceTags.subPath.includes(record.track));
      const current = structuredClone(map.build());
      const originalBytes = execFileSync('git', ['show', `HEAD:map/${file}`], { maxBuffer: 32 * 1024 * 1024 });
      fs.writeFileSync(snapshotPath, originalBytes);
      const original = MapBuilder.read(snapshotPath).build();
      const root = current.ContentProto.Entities.find(e => e.path === `/maps/${name}`);
      const oldRoot = original.ContentProto.Entities.find(e => e.path === `/maps/${name}`);
      assert.equal(root.jsonString['@components'].filter(c => c['@type'] === 'MOD.Core.SoundComponent').length, 1);
      root.jsonString['@components'] = root.jsonString['@components'].filter(c => c['@type'] !== 'MOD.Core.SoundComponent');
      root.componentNames = oldRoot.componentNames;
      assert.deepEqual(current, original, `Non-audio difference: ${name}`);
    }
  } finally {
    if (fs.existsSync(snapshotPath)) fs.unlinkSync(snapshotPath);
    fs.rmdirSync(scratch);
  }
  const ids = [...new Set(mapping.maps.map(r => r.ruid))];
  const result = {
    checkedAt: new Date().toISOString(), maps: files.length, uniqueBgm: ids.length,
    missing: 0, nonAudioChanges: 0, mapSettings: 'PASS', sourceMetadata: 'PASS',
    officialLookup: 'NOT_RUN', makerRefresh: 'NOT_RUN', makerBuild: 'NOT_RUN',
    makerPlay: 'NOT_RUN', listenValidation: 'NOT_TESTABLE', nativeVolumeRuntime: 'NOT_RUN',
  };
  if (process.argv.includes('--official')) {
    const api = require('../.agents/skills/msw-search/scripts/msw_resource_api.cjs');
    const response = await api.getResourcesBatch(ids);
    assert.equal(response.items.length, ids.length);
    const returned = new Map(response.items.map(r => [r.id, r]));
    for (const id of ids) assert.equal(returned.get(id)?.type, 'bgm');
    result.officialLookup = `PASS ${returned.size}/${ids.length}`;
    result.officialRuidCount = returned.size;
  }
  fs.writeFileSync('docs/reports/map-bgm-validation-20261005.json', JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
