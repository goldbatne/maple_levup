const fs = require("node:fs");
const path = require("node:path");
const { MapBuilder } = require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const { ModelBuilder, vector2 } = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const root = path.resolve(__dirname, "../..");
const dataDir = path.join(root, "RootDesk/MyDesk/GameData");
const modelDir = path.join(root, "RootDesk/MyDesk/Models/Monsters");
const mapDir = path.join(root, "map");

function readCsv(file) {
  const full = path.join(dataDir, file);
  const text = fs.readFileSync(full, "utf8").replace(/^\uFEFF/, "").trimEnd();
  const [head, ...lines] = text.split(/\r?\n/);
  const headers = head.split(",");
  const rows = lines.filter(Boolean).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, values[index] || ""]));
  });
  return { full, headers, rows };
}

function mutateCsv(file, changes) {
  const csv = readCsv(file);
  for (const change of changes) {
    const index = csv.rows.findIndex((row) => row.id === change.id);
    if (index >= 0) csv.rows[index] = { ...csv.rows[index], ...change };
    else csv.rows.push(Object.fromEntries(csv.headers.map((header) => [header, String(change[header] ?? "")])));
  }
  const lines = csv.rows.map((row) => csv.headers.map((header) => String(row[header] ?? "")).join(","));
  fs.writeFileSync(csv.full, `\uFEFF${csv.headers.join(",")}\r\n${lines.join("\r\n")}\r\n`);
}

mutateCsv("AreaTable.csv", [
  { id: "area_05", note: "지역 20칸의 여섯 번째 (Lv51~60). 노틸러스 해안과 갑판을 지나 플로리나 비치에서 건너온 킹크랑을 상대한다" },
  { id: "area_07", note: "지역 20칸의 일곱 번째 (Lv61~70). 늪과 개미굴을 지나 주니어 발록의 금지된 제단에 닿는다" },
]);

mutateCsv("RoomTable.csv", [
  { id: "r_055", name: "킹크랑이 덮친 노틸러스 갑판", monster_id: "m_king_clang", monster_level: 60 },
  { id: "r_07a", gate_type: "key", gate_key: "s_mon_king_clang", gate_value: "" },
  { id: "r_074", name: "황소 수문장의 회랑", monster_id: "m_tauromacis", monster_count: 5, monster_level: 68 },
  { id: "r_075", name: "주니어 발록의 제단", monster_id: "m_jr_balrog", monster_count: 1, monster_level: 70 },
  { id: "r_08a", gate_type: "key", gate_key: "s_mon_jr_balrog", gate_value: "" },
]);

mutateCsv("MonsterTable.csv", [
  { id: "m_jr_balrog", name: "주니어 발록", level: 70, hp: 2504, def: 1391, exp: 3590, drop_skill_id: "s_mon_jr_balrog", model_id: "jrbalrog", combat_skill_ids: "" },
  { id: "m_king_clang", name: "킹크랑", level: 60, hp: 2162, def: 1201, exp: 1384, drop_skill_id: "s_mon_king_clang", model_id: "kingclang", combat_skill_ids: "" },
]);

mutateCsv("SkillTable.csv", [
  {
    id: "s_mon_jr_balrog",
    description: "금지된 제단의 주니어 발록처럼 날개 아래에서 화염 파동을 터뜨려 주변의 적을 휩쓴다",
  },
  { id: "s_mon_tauromacis", is_key_skill: "false" },
  {
    id: "s_mon_king_clang", name: "왕게의 집게 파도", source: "monster", scaling_stat: "ATK", coefficient: 2.65,
    slot_type: "monster", effect_type: "damage", is_key_skill: "true", cooldown: 8, skill_kind: "attack",
    target_mode: "area", max_targets: 0, effect_value: 0, duration: 0, range: 5.2, dash_distance: 0, tier: 0,
    icon_ruid: "thumbnail://cddcc91429d24abbb0c071135ace8b39", icon_ratio: "1.00", effect_ruid: "", effect_style: "", sfx_ruid: "", projectile_ruid: "",
    passive_stat: "", passive_value: "",
    description: "모래 해변의 왕게 킹크랑이 양 집게로 파도를 끌어모아 주변을 크게 내려친다",
    layer_ruids: "c57b15ccc8dd408b98c627617144d3cd|8394705c13394b78a8b9a38e1313cb22",
    layer_types: "animationclip|animationclip", layer_styles: "clip|clip", layer_delays: "0|0.16",
    layer_durations: "0.64|0.78", layer_scales: "1.0|1.3", layer_offsets_x: "0|0", layer_offsets_y: "0|0",
    layer_drifts_x: "0|0", layer_drifts_y: "0|0",
  },
]);

mutateCsv("ItemTable.csv", [
  { id: "i_tauromacis_sledge", drop_rate: 0.03 },
  {
    id: "i_king_clang_yellow_umbrella", name: "노란 우산", item_type: "equip", slot: "weapon",
    stat_atk: 0, stat_int: 10, stat_def: 0, stat_luk: 0, stat_all: 0, heal_hp: 0, stack_max: 5,
    drop_from: "m_king_clang", drop_rate: 0.02, icon_ruid: "thumbnail://8668230e7f024e21997ad7f0518db3e3",
    note: "킹크랑의 과거 실제 장비 드랍. 원작 아이템 1302016", passive_stat: "", passive_value: "", avatar_category: "onehandedweapon",
  },
]);

const kingClang = ModelBuilder.read(path.join(modelDir, "JrBalrog.model"));
kingClang.renameModel("KingClang", "kingclang");
kingClang.value("MOD.Core.StateAnimationComponent", "ActionSheet", {
  stand: "cddcc91429d24abbb0c071135ace8b39",
  move: "edb7787a772d43f180767aaf60947486",
  jump: "5a79966cdda24c1c8208ccbba1c8ff2f",
  attack: "603c65e397ea419e8d62898c05db8a9b",
  hit: "6c85c55936544707a57c2667c49a606d",
  die: "8ce0f378582c4b17926e37cfb9c552f2",
});
kingClang.value("MOD.Core.SpriteRendererComponent", "SpriteRUID", "cddcc91429d24abbb0c071135ace8b39");
kingClang.value("MOD.Core.MovementComponent", "InputSpeed", 0.95);
kingClang.value("MOD.Core.HitComponent", "BoxSize", vector2(1.8, 1.3));
kingClang.value("MOD.Core.HitComponent", "ColliderOffset", vector2(0, 0.65));
kingClang.value("script.RoomMonster", "MonsterId", "m_king_clang");
kingClang.write(path.join(modelDir, "KingClang.model"));

const tileSpecs = [
  ["RectTileData_Sleepywood.tileset", { Id: "1b14ae7d99984a8f87e070ebfbe4d79d", Name: "Sleepywood_lava_fissure", IsCollidable: true }],
  ["RectTileData_Orbis.tileset", { Id: "66a9ca3a9668407882ed8e6c79ebd913", Name: "Orbis_eliza_moon_garden", IsCollidable: false }],
  ["RectTileData_ElNath.tileset", { Id: "525db3dd32cc4652bf1af4b508dbe6bf", Name: "Nihal_oasis_water", IsCollidable: true }],
];

for (const [file, spec] of tileSpecs) {
  const full = path.join(root, "RootDesk/MyDesk", file);
  const tileSet = JSON.parse(fs.readFileSync(full, "utf8"));
  const datas = tileSet.ContentProto.Json.datas;
  const existing = datas.findIndex((data) => data.Name === spec.Name);
  if (existing >= 0) datas[existing] = spec;
  else datas.push(spec);
  fs.writeFileSync(full, `${JSON.stringify(tileSet, null, 2)}\n`);
}

function position(tile) {
  return { x: Number(tile.position.x), y: Number(tile.position.y) };
}

function repaint(mapName, resetIndex, predicate) {
  const full = path.join(mapDir, `${mapName}.map`);
  const map = MapBuilder.read(full);
  const tiles = map.getTiles("RectTileMap");
  for (const tile of tiles) if (tile.tileIndex === 8) tile.tileIndex = resetIndex;
  let painted = 0;
  for (const tile of tiles) {
    const pos = position(tile);
    if (predicate(tile, pos)) {
      tile.tileIndex = 8;
      painted += 1;
    }
  }
  if (painted === 0) throw new Error(`${mapName}: T66 전용 타일을 한 칸도 칠하지 못함`);
  map.write(full);
  return { mapName, painted, bounds: map.getTileBounds("RectTileMap") };
}

const painting = [
  repaint("map077", 3, (tile, { x, y }) => (
    ((x === -10 || x === -9) && y >= -2 && y <= 3)
    || ((x === 9 || x === 10) && y >= -1 && y <= 4)
    || (y === -2 && ((x >= -7 && x <= -5) || (x >= 5 && x <= 7)))
  )),
  repaint("map085", 2, (tile, { x, y }) => tile.tileIndex === 2 && (
    ((x + 2 * y) % 7 === 0 && y >= -2 && y <= 4)
    || ((x - y) % 11 === 0 && y >= -1 && y <= 3)
  )),
  repaint("map13a", 6, (_tile, { x, y }) => {
    const dx = (x - 4) / 5;
    const dy = (y - 1) / 2.5;
    return dx * dx + dy * dy <= 1;
  }),
];

console.log(JSON.stringify({
  kingClang: { level: 60, hp: 2162, def: 1201, exp: 1384, item: "노란 우산 (1302016)" },
  movedBoss: { room: "r_075", monster: "m_jr_balrog", level: 70 },
  painting,
}, null, 2));
