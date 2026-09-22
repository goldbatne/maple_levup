const crypto = require('crypto');
const fs = require('fs');
const { MapBuilder } = require('../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs');

function fileSha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function assertSourceUnchanged(sourcePath, sourceHash) {
  const currentHash = fileSha256(sourcePath);
  if (currentHash !== sourceHash) {
    throw new Error(`Source map changed while building candidate: ${sourcePath}`);
  }
}

function cropRectTiles(builder, bounds) {
  const doc = builder.build();
  const tileEntity = doc.ContentProto.Entities.find((entity) =>
    entity.jsonString.path.endsWith('/RectTileMap'));
  if (!tileEntity) throw new Error('RectTileMap entity not found');

  const rect = tileEntity.jsonString['@components'].find((component) =>
    component['@type'] === 'MOD.Core.RectTileMapComponent');
  if (!rect || !Array.isArray(rect.tileMap)) {
    throw new Error('RectTileMapComponent.tileMap not found');
  }

  rect.tileMap = rect.tileMap.filter((tile) => {
    const { x, y } = tile.position;
    return x >= bounds.minX && x <= bounds.maxX
      && y >= bounds.minY && y <= bounds.maxY;
  });
}

function verifyPilot(out, expectedName) {
  const verify = MapBuilder.read(out);
  const info = verify.getMapInfo();
  const bounds = verify.getTileBounds();
  if (verify.getTileMapMode() !== 1 || info.tileCount !== 350
      || bounds.minX !== -12 || bounds.maxX !== 12
      || bounds.minY !== -6 || bounds.maxY !== 7) {
    throw new Error(`${expectedName} verification failed: ${JSON.stringify({ info, bounds })}`);
  }
  console.log(JSON.stringify({ out, info, bounds }, null, 2));
}

function buildMap003C() {
  const source = 'map/map003.map';
  const sourceHash = fileSha256(source);
  const out = 'map/map003_p4c.map';
  const map = MapBuilder.fromTemplate(source, 'map003_p4c')
    .patch('Portal_W', { pos: [-11, 1, 0] })
    .patch('Portal_E', { pos: [11, 1, 0] })
    .patch('Portal_N', { pos: [0, 6, 0] })
    .patch('Portal_S', { pos: [0, -5, 0] })
    .patchComponent('map003_p4c', 'script.RoomSpawner', {
      SpawnMinX: -8.5,
      SpawnMaxX: 8.5,
      SpawnMinY: -3.5,
      SpawnMaxY: 4.5,
    });

  cropRectTiles(map, { minX: -12, maxX: 12, minY: -6, maxY: 7 });
  map.write(out);
  assertSourceUnchanged(source, sourceHash);
  verifyPilot(out, 'map003_p4c');
}

function buildMap077C() {
  const source = 'map/map077.map';
  const sourceHash = fileSha256(source);
  const out = 'map/map077_p4c.map';
  const map = MapBuilder.fromTemplate(source, 'map077_p4c')
    .patch('Portal_W', { pos: [-11, 1, 0] })
    .patch('Portal_N', { pos: [0, 6, 0] })
    .patchComponent('map077_p4c', 'script.RoomSpawner', {
      SpawnMinX: -8.5,
      SpawnMaxX: 8.5,
      SpawnMinY: -3.5,
      SpawnMaxY: 4.5,
    });

  cropRectTiles(map, { minX: -12, maxX: 12, minY: -6, maxY: 7 });
  map.write(out);
  assertSourceUnchanged(source, sourceHash);
  verifyPilot(out, 'map077_p4c');
}

const target = process.argv[2] || 'all';
if (target === 'map003' || target === 'all') buildMap003C();
if (target === 'map077' || target === 'all') buildMap077C();
