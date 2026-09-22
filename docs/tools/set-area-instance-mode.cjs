const fs = require('fs');
const path = require('path');
const { MapBuilder } = require('../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs');

const root = path.resolve(__dirname, '../..');
const areaId = process.argv[2];
const enabled = process.argv[3] === 'true';
if (!areaId || !['true', 'false'].includes(process.argv[3])) {
  throw new Error('usage: node set-area-instance-mode.cjs <area_id> <true|false>');
}

const lines = fs.readFileSync(path.join(root, 'RootDesk/MyDesk/GameData/RoomTable.csv'), 'utf8')
  .replace(/^\uFEFF/, '').split(/\r?\n/).filter(Boolean);
const headers = lines[0].split(',');
const areaIndex = headers.indexOf('area_id');
const mapIndex = headers.indexOf('map_name');
const names = [...new Set(lines.slice(1).map(line => line.split(','))
  .filter(row => row[areaIndex] === areaId)
  .map(row => row[mapIndex]).filter(Boolean))].sort();

for (const name of names) {
  const file = path.join(root, 'map', `${name}.map`);
  const map = MapBuilder.read(file);
  if (map.getMapInfo().TileMapMode !== 1) throw new Error(`${name}: expected RectTile`);
  map.patchComponent(name, 'MOD.Core.MapComponent', { IsInstanceMap: enabled }).write(file);
}
console.log(JSON.stringify({ areaId, enabled, maps: names }, null, 2));
