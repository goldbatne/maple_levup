// MapBuilder-only BGM authoring. Run without --write for a dry run.
// All selections are resolved against downloaded official original-map tags.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { MapBuilder } = require('../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs');
const { preserveFormat } = require('./preserve_map_number_format.cjs');

const project = path.resolve(__dirname, '..');
const catalog = require('../docs/reports/map-bgm-official-catalog-20261005.json');
const defaults = {
  area_00: ['sound/bgm34.img', 'MapleLeaf'],
  area_01: ['sound/bgm01.img', 'CavaBien'],
  area_02: ['sound/bgm01.img', 'HighlandStar'],
  area_03: ['sound/bgm01.img', 'MoonlightShadow'],
  area_04: ['sound/bgm03.img', 'Subway'],
  area_05: ['sound/bgm15.img', 'Nautilus'],
  area_07: ['sound/bgm01.img', 'AncientMove'],
  area_08: ['sound/bgm04.img', "Shinin'Harbor"],
  area_09: ['sound/bgm04.img', 'WarmRegard'],
  area_10: ['sound/bgm11.img', 'BlueWorld'],
  area_11: ['sound/bgm07.img', 'FunnyTimeMaker'],
  area_12: ['sound/bgm06.img', 'FantasticThinking'],
  area_13: ['sound/bgm14.img', 'HotDesert'],
  area_14: ['sound/bgm12.img', 'Dispute'],
  area_15: ['sound/bgm15.img', 'MureungHill'],
  area_16: ['sound/bgm13.img', "Minar'sDream"],
  area_17: ['sound/bgm16.img', 'Remembrance'],
  area_18: ['sound/bgm08.img', 'LetsHuntAliens'],
  area_19: ['sound/bgm25.img', 'knightsStronghold'],
  area_20: ['sound/bgm25.img', 'destructionPerion'],
};
const overrides = {
  maptown: ['sound/bgm00.img', 'FloralLife'],
  map005: ['sound/bgm02.img', 'AboveTheTreetops'],
  map007: ['sound/bgm02.img', 'AboveTheTreetops'],
  map05: ['sound/bgm00.img', 'FloralLife'],
  map041: ['sound/bgm01.img', 'BadGuys'],
  map042: ['sound/bgm01.img', 'BadGuys'],
  map24: ['sound/bgm02.img', 'MissingYou'],
  map27: ['sound/bgm02.img', 'MissingYou'],
  map05a: ['sound/bgm15.img', 'inNautilus'],
  map071: ['sound/bgm00.img', 'SleepyWood'],
  map074: ['sound/bgm02.img', 'EvilEyes'],
  map075: ['sound/bgm02.img', 'EvilEyes'],
  map07a: ['sound/bgm02.img', 'EvilEyes'],
  map103: ['sound/bgm12.img', 'DeepSee'],
  map104: ['sound/bgm12.img', 'DeepSee'],
  map107: ['sound/bgm12.img', 'DeepSee'],
  map10a: ['sound/bgm12.img', 'DeepSee'],
  map105: ['sound/bgm12.img', 'AquaCave'],
  map123: ['sound/bgm07.img', 'WaltzForWork'],
  map127: ['sound/bgm07.img', 'WaltzForWork'],
  map124: ['sound/bgm07.img', 'WhereverYouAre'],
  map125: ['sound/bgm07.img', 'WhereverYouAre'],
  map12a: ['sound/bgm07.img', 'WhereverYouAre'],
  map134: ['sound/bgm15.img', 'SunsetDesert'],
  map135: ['sound/bgm15.img', 'SunsetDesert'],
  map137: ['sound/bgm15.img', 'SunsetDesert'],
  map153: ['sound/bgm15.img', 'MureungForest'],
  map154: ['sound/bgm15.img', 'MureungForest'],
  map157: ['sound/bgm15.img', 'MureungForest'],
  map15a: ['sound/bgm15.img', 'MureungForest'],
  map163: ['sound/bgm14.img', 'DragonNest'],
  map164: ['sound/bgm14.img', 'DragonNest'],
  map167: ['sound/bgm14.img', 'DragonNest'],
  map165: ['sound/bgm13.img', 'AcientForest'],
  map16a: ['sound/bgm13.img', 'AcientForest'],
  map185: ['sound/bgm08.img', 'ForTheGlory'],
  map195: ['sound/bgm25.img', 'CygnusGarden'],
};

function readRows(filename) {
  const lines = fs.readFileSync(path.join(project, 'RootDesk/MyDesk/GameData', filename), 'utf8')
    .replace(/^\uFEFF/, '').trim().split(/\r?\n/);
  const headers = lines.shift().split(',');
  return lines.map(line => {
    const cells = line.split(',');
    assert.equal(cells.length, headers.length, `Unexpected CSV format in ${filename}`);
    return Object.fromEntries(headers.map((key, i) => [key, cells[i]]));
  });
}

function resolveTrack(selection) {
  assert.ok(selection, 'No original-map BGM policy for this room');
  const [sourcePath, track] = selection;
  const matches = catalog.resources.filter(r =>
    r.type === 'bgm' && r.sourceTags.path?.includes(sourcePath) && r.sourceTags.subPath?.includes(track));
  assert.equal(matches.length, 1, `Original BGM must have exactly one RUID: ${sourcePath}/${track}`);
  assert.match(matches[0].id, /^[a-f0-9]{32}$/);
  return matches[0];
}

function compareNonAudio(before, after, rootPath) {
  const clean = structuredClone(after);
  const originalRoot = before.ContentProto.Entities.find(e => e.path === rootPath);
  const changedRoot = clean.ContentProto.Entities.find(e => e.path === rootPath);
  changedRoot.jsonString['@components'] = changedRoot.jsonString['@components']
    .filter(c => c['@type'] !== 'MOD.Core.SoundComponent');
  const originalAudio = originalRoot.jsonString['@components']
    .find(c => c['@type'] === 'MOD.Core.SoundComponent');
  if (originalAudio) changedRoot.jsonString['@components'].push(structuredClone(originalAudio));
  changedRoot.componentNames = originalRoot.componentNames;
  assert.deepEqual(clean, before, `Non-audio map data changed: ${rootPath}`);
}

function main() {
  const rooms = readRows('RoomTable.csv');
  const areas = readRows('AreaTable.csv');
  const byMap = new Map(rooms.map(row => [row.map_name, row]));
  const areaNames = new Map(areas.map(row => [row.id, row.name]));
  const files = fs.readdirSync(path.join(project, 'map')).filter(name => name.endsWith('.map')).sort();
  const pending = [];
  for (const file of files) {
    const name = file.slice(0, -4);
    const sourceName = name.replace(/_p4[bc]$/, '');
    const room = byMap.get(sourceName);
    assert.ok(room, `No RoomTable parent for ${name}`);
    const track = resolveTrack(overrides[sourceName] || defaults[room.area_id]);
    const filepath = path.join(project, 'map', file);
    const map = MapBuilder.read(filepath);
    assert.equal(map.getTileMapMode(), 1, `Unexpected map type: ${name}`);
    const before = structuredClone(map.build());
    const audio = {
      AudioClipRUID: track.id, Bgm: true, KeepBGM: true,
      Loop: true, Mute: false, Pitch: 1, PlayOnEnable: true,
      SetCameraAsListener: false, Volume: 0.35, Enable: true,
    };
    map.upsertComponent(name, 'MOD.Core.SoundComponent', audio);
    compareNonAudio(before, map.build(), `/maps/${name}`);
    pending.push({ map, filepath, before, row: {
      map: name, room: room.name, area: areaNames.get(room.area_id) || '메인 마을',
      path: track.sourceTags.path[0], track: track.sourceTags.subPath[0],
      ruid: track.id, originalMapTags: track.sourceTags.ko,
      prototype: name !== sourceName,
    } });
  }
  // Validate every map before the first write; preserve Maker newline/BOM formatting.
  if (process.argv.includes('--write')) {
    for (const entry of pending) {
      const previous = fs.readFileSync(entry.filepath, 'utf8');
      entry.map.write(entry.filepath);
      const written = fs.readFileSync(entry.filepath, 'utf8');
      const newline = previous.includes('\r\n') ? '\r\n' : '\n';
      fs.writeFileSync(entry.filepath, preserveFormat(previous,
        (previous.startsWith('\uFEFF') ? '\uFEFF' : '') + written.replace(/\r?\n/g, newline)), 'utf8');
      compareNonAudio(entry.before, MapBuilder.read(entry.filepath).build(), `/maps/${entry.row.map}`);
    }
    fs.writeFileSync(path.join(project, 'docs/reports/map-bgm-mapping-20261005.json'),
      JSON.stringify({ volume: 0.35, maps: pending.map(entry => entry.row) }, null, 2) + '\n');
  }
  console.log(JSON.stringify({
    mode: process.argv.includes('--write') ? 'WRITE' : 'DRY_RUN',
    maps: pending.length, tableMaps: byMap.size,
    prototypeMaps: pending.filter(entry => entry.row.prototype).length,
    uniqueBgm: new Set(pending.map(entry => entry.row.ruid)).size,
    nonAudioChanges: 0,
  }, null, 2));
}

main();
