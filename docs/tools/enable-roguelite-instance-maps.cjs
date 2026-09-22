const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { MapBuilder } = require('../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs');

const root = path.resolve(__dirname, '../..');
const roomTable = path.join(root, 'RootDesk/MyDesk/GameData/RoomTable.csv');
// Maker can register native MSW extensions anywhere below the project root.
// Store backup bytes with a non-native suffix so they never become duplicate
// or mislocated entries.
const backupRoot = path.join(root, 'docs/reports/roguelite-merge-20260921/preinstance-map-snapshots');

function parseCsvLine(line) {
  const out = [];
  let value = '';
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      if (quoted && line[i + 1] === '"') {
        value += '"';
        i += 1;
      } else {
        quoted = !quoted;
      }
    } else if (ch === ',' && !quoted) {
      out.push(value);
      value = '';
    } else {
      value += ch;
    }
  }
  out.push(value);
  return out;
}

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

const lines = fs.readFileSync(roomTable, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/).filter(Boolean);
const headers = parseCsvLine(lines[0]);
const mapIndex = headers.indexOf('map_name');
const areaIndex = headers.indexOf('area_id');
if (mapIndex < 0 || areaIndex < 0) throw new Error('RoomTable columns missing');

const mapNames = [...new Set(lines.slice(1).map(parseCsvLine)
  .filter(row => (row[areaIndex] || '').trim() !== '')
  .map(row => (row[mapIndex] || '').trim())
  .filter(Boolean))].sort();

fs.mkdirSync(backupRoot, { recursive: true });
const report = [];
for (const mapName of mapNames) {
  const file = path.join(root, 'map', `${mapName}.map`);
  if (!fs.existsSync(file)) {
    report.push({ map: mapName, status: 'MISSING' });
    continue;
  }
  const before = sha256(file);
  const map = MapBuilder.read(file);
  const info = map.getMapInfo();
  if (info.TileMapMode !== 1) {
    report.push({ map: mapName, status: 'WRONG_TILE_MODE', mode: info.TileMapMode, before });
    continue;
  }
  if (info.IsInstanceMap === true) {
    report.push({ map: mapName, status: 'ALREADY_INSTANCE', mode: info.TileMapMode, before, after: before });
    continue;
  }
  const backup = path.join(backupRoot, `${mapName}.map.snapshot`);
  if (!fs.existsSync(backup)) fs.copyFileSync(file, backup);
  map.patchComponent(mapName, 'MOD.Core.MapComponent', { IsInstanceMap: true }).write(file);
  const after = sha256(file);
  const verified = MapBuilder.read(file).getMapInfo();
  report.push({
    map: mapName,
    status: verified.IsInstanceMap === true ? 'UPDATED' : 'VERIFY_FAIL',
    mode: verified.TileMapMode,
    before,
    after,
  });
}

const output = path.join(root, 'docs/reports/roguelite-merge-20260921/INSTANCE_MAP_MIGRATION.json');
fs.writeFileSync(output, `${JSON.stringify({ mapCount: mapNames.length, report }, null, 2)}\n`, 'utf8');
const counts = report.reduce((acc, item) => {
  acc[item.status] = (acc[item.status] || 0) + 1;
  return acc;
}, {});
console.log(JSON.stringify({ mapCount: mapNames.length, counts, output }, null, 2));
