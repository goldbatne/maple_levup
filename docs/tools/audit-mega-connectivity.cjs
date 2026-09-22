const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const outDir = path.join(root, 'docs/reports/mega-area-connectivity-respawn-20260921');
fs.mkdirSync(outDir, { recursive: true });

function csvRows(file) {
  const text = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '').trim();
  const lines = text.split(/\r?\n/);
  const head = lines.shift().split(',');
  return lines.filter(Boolean).map(line => {
    const cells = []; let value = ''; let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (quoted && line[i + 1] === '"') { value += '"'; i++; }
        else quoted = !quoted;
      } else if (ch === ',' && !quoted) { cells.push(value); value = ''; }
      else value += ch;
    }
    cells.push(value);
    return Object.fromEntries(head.map((key, i) => [key, cells[i] ?? '']));
  });
}

function encode(value) {
  const s = value == null ? '' : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function writeCsv(name, header, rows) {
  fs.writeFileSync(path.join(outDir, name), [header, ...rows]
    .map(row => row.map(encode).join(',')).join('\r\n') + '\r\n', 'utf8');
}

function component(entity, type) {
  return (entity.jsonString?.['@components'] || []).find(c => c['@type'] === type);
}

const rooms = csvRows(path.join(root, 'RootDesk/MyDesk/GameData/RoomTable.csv'));
const areas = csvRows(path.join(root, 'RootDesk/MyDesk/GameData/AreaTable.csv'));
const roomById = new Map(rooms.map(r => [r.id, r]));
const roomByMap = new Map(rooms.map(r => [r.map_name, r]));
const areaById = new Map(areas.map(a => [a.id, a]));
const megaSources = {
  mega_01: ['area_00', 'area_01', 'area_03', 'area_02'],
  mega_02: ['area_04', 'area_05', 'area_07', 'area_08'],
  mega_03: ['area_09', 'area_10', 'area_11', 'area_12'],
  mega_04: ['area_13', 'area_14', 'area_15', 'area_16'],
  mega_05: ['area_17', 'area_18', 'area_19', 'area_20'],
};
const megaBossPools = {
  mega_01: ['m_mano','m_mushmom','m_faust','m_stumpy'],
  mega_02: ['m_shade','m_king_clang','m_jr_balrog','m_eliza'],
  mega_03: ['m_snow_witch','m_pianus','m_rombot','m_timer'],
  mega_04: ['m_deo','m_chimera','m_tae_roon','m_manon'],
  mega_05: ['m_dodo','m_zeno','m_cygnus','m_mutant_stumpy'],
};
const megaByArea = new Map();
for (const [mega, ids] of Object.entries(megaSources)) for (const id of ids) megaByArea.set(id, mega);

const mapDir = path.join(root, 'map');
const mapFiles = fs.readdirSync(mapDir).filter(f => f.endsWith('.map')).sort();
const maps = new Map();
for (const file of mapFiles) {
  const name = file.slice(0, -4);
  let parsed;
  try { parsed = JSON.parse(fs.readFileSync(path.join(mapDir, file), 'utf8')); }
  catch (error) { maps.set(name, { file, parseError: error.message, portals: [] }); continue; }
  const entities = parsed.ContentProto?.Entities || [];
  const rootEntity = entities.find(e => e.jsonString?.name === name) || entities[0];
  const mapComp = rootEntity ? component(rootEntity, 'MOD.Core.MapComponent') : null;
  const tileEntity = entities.find(e => component(e, 'MOD.Core.RectTileMapComponent'));
  const tileComp = tileEntity ? component(tileEntity, 'MOD.Core.RectTileMapComponent') : null;
  const tiles = tileComp?.tileMap || [];
  const xs = tiles.map(t => Number(t.position?.x)).filter(Number.isFinite);
  const ys = tiles.map(t => Number(t.position?.y)).filter(Number.isFinite);
  const spawnEntity = entities.find(e => component(e, 'MOD.Core.SpawnLocationComponent'));
  const spawnTransform = spawnEntity ? component(spawnEntity, 'MOD.Core.TransformComponent') : null;
  const portals = [];
  for (const entity of entities) {
    const portal = component(entity, 'script.RoomPortal');
    if (!portal) continue;
    const transform = component(entity, 'MOD.Core.TransformComponent');
    const trigger = component(entity, 'MOD.Core.TriggerComponent');
    portals.push({
      name: entity.jsonString?.name || '', direction: portal.direction || '',
      x: transform?.Position?.x ?? '', y: transform?.Position?.y ?? '',
      trigger: Boolean(trigger), legacyTrigger: trigger?.IsLegacy === true,
    });
  }
  maps.set(name, {
    file, parseError: '', portals,
    tileMode: mapComp?.TileMapMode ?? '', instance: mapComp?.IsInstanceMap === true,
    tileCount: tiles.length,
    minX: xs.length ? Math.min(...xs) : '', maxX: xs.length ? Math.max(...xs) : '',
    minY: ys.length ? Math.min(...ys) : '', maxY: ys.length ? Math.max(...ys) : '',
    spawnX: spawnTransform?.Position?.x ?? '', spawnY: spawnTransform?.Position?.y ?? '',
  });
}

const fullRows = [];
for (const [mapName, info] of maps) {
  const room = roomByMap.get(mapName);
  let classification = 'UNUSED';
  if (mapName === 'maptown') classification = 'TOWN';
  else if (room && megaByArea.has(room.area_id)) classification = room.room_type === 'boss' ? 'SPECIAL_ENCOUNTER' : 'RUN_ROOM_SOURCE';
  else if (room) classification = 'REFERENCE_ONLY';
  fullRows.push([
    mapName, info.file, room?.id || '', room?.area_id || '', megaByArea.get(room?.area_id) || '',
    room?.room_type || '', classification, room ? 'YES' : 'NO', info.parseError ? 'NO' : 'YES',
    info.tileMode, info.instance ? 'YES' : 'NO', info.tileCount,
    info.minX, info.minY, info.maxX, info.maxY, info.spawnX, info.spawnY,
    info.portals.length, info.portals.map(p => p.direction).join('|'),
    info.parseError || (room && info.portals.length === 0 && room.room_type !== 'town' ? 'NO_PORTAL_ENTITY' : ''),
  ]);
}
writeCsv('MAP_FULL_AUDIT.csv', [
  'map_name','map_file','room_id','area_id','mega_area','room_type','classification',
  'in_room_table','map_parse','tile_map_mode','is_instance_map','tile_count',
  'min_x','min_y','max_x','max_y','spawn_x','spawn_y','portal_count','portal_directions','notes'
], fullRows);

const opposite = { north: 'south', south: 'north', east: 'west', west: 'east' };
const portalRows = [];
const unreachable = [];
for (const room of rooms) {
  if (!megaByArea.has(room.area_id)) continue;
  const sourceMap = maps.get(room.map_name);
  for (const dir of Object.keys(opposite)) {
    const targetId = room[`conn_${dir}`];
    if (!targetId) continue;
    const target = roomById.get(targetId);
    const sourcePortal = sourceMap?.portals.find(p => p.direction === dir);
    const targetPortal = target ? maps.get(target.map_name)?.portals.find(p => p.direction === opposite[dir]) : null;
    const reciprocal = target?.[`conn_${opposite[dir]}`] === room.id;
    const mega = megaByArea.get(room.area_id);
    const targetInSameMega = target && megaByArea.get(target.area_id) === mega;
    const sourceUsed = room.room_type !== 'boss' || megaBossPools[mega].includes(room.monster_id);
    let status = 'PASS_STATIC';
    let note = '';
    if (!targetInSameMega) {
      status = 'LEGACY_EXTERNAL_DISABLED';
      note = 'Mega Run 그래프 밖의 마을/레거시 연결이며 RoomPortal.RefreshRunBinding에서 비활성화';
    } else if (!sourceUsed) {
      status = 'NOT_USED_LEGACY_BOSS';
      note = 'Mega BossPool에 없는 레거시 전직/시험 보스방';
    } else if (!(target && sourcePortal && targetPortal && reciprocal)) {
      status = 'FAIL';
      note = 'Run 후보 내부 RoomTable 연결 또는 실제 양방향 포탈 엔티티 불일치';
    }
    portalRows.push([
      mega, room.id, room.map_name, dir, targetId, target?.map_name || '',
      sourcePortal ? 'YES' : 'NO', targetPortal ? 'YES' : 'NO', reciprocal ? 'YES' : 'NO',
      sourcePortal ? `${sourcePortal.x}:${sourcePortal.y}` : '',
      targetPortal ? `${targetPortal.x}:${targetPortal.y}` : '', status, note,
    ]);
  }
}
writeCsv('PORTAL_CONNECTIVITY_AUDIT.csv', [
  'mega_area','source_room','source_map','direction','target_room','target_map',
  'source_portal','target_opposite_portal','roomtable_reciprocal','source_position','target_position','status','notes'
], portalRows);

const graphRows = [];
for (const [mega, areaIds] of Object.entries(megaSources)) {
  const allMegaRooms = rooms.filter(r => areaIds.includes(r.area_id));
  const megaRooms = allMegaRooms.filter(r => r.room_type !== 'boss' || megaBossPools[mega].includes(r.monster_id));
  const megaIds = new Set(megaRooms.map(r => r.id));
  const start = areaById.get(areaIds[0])?.entry_room_id || '';
  const seen = new Set(); const queue = start ? [start] : [];
  while (queue.length) {
    const id = queue.shift(); if (seen.has(id) || !megaIds.has(id)) continue; seen.add(id);
    const room = roomById.get(id);
    const sourceDirs = new Set((maps.get(room.map_name)?.portals || []).map(p => p.direction));
    for (const candidate of megaRooms) {
      if (candidate.id === id || seen.has(candidate.id)) continue;
      const targetDirs = new Set((maps.get(candidate.map_name)?.portals || []).map(p => p.direction));
      let compatible = false;
      for (const dir of sourceDirs) if (targetDirs.has(opposite[dir])) { compatible = true; break; }
      if (compatible) queue.push(candidate.id);
    }
  }
  const missing = megaRooms.filter(r => !seen.has(r.id)).map(r => r.id);
  graphRows.push([
    mega, areaIds.join('|'), start, megaRooms.length, seen.size, missing.length,
    missing.length ? 'FAIL' : 'PASS_STATIC', missing.join('|'),
    'RoomTable 방향 슬롯과 실제 RoomPortal 방향의 호환 가능성을 정적으로 확인. Seed별 생성은 Maker Runtime 별도 검증.'
  ]);
  for (const room of megaRooms) if (!seen.has(room.id)) unreachable.push([mega, room.area_id, room.id, room.map_name, 'STATIC_SOURCE_GRAPH_UNREACHABLE']);
}
writeCsv('MEGA_AREA_GRAPH_AUDIT.csv', [
  'mega_area','source_areas','start_room','candidate_rooms','reachable_rooms','unreachable_count','status','unreachable_rooms','notes'
], graphRows);
writeCsv('UNREACHABLE_MAPS.csv', ['mega_area','area_id','room_id','map_name','reason'], unreachable);

console.log(`Wrote audits to ${outDir}`);
console.log(`maps=${maps.size} rooms=${rooms.length} portal_edges=${portalRows.length} unreachable=${unreachable.length}`);
