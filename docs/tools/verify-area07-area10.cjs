const fs = require("node:fs");
const path = require("node:path");
const { MapBuilder } = require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const { ModelBuilder } = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const root = path.resolve(__dirname, "../..");
const dataDir = path.join(root, "RootDesk/MyDesk/GameData");
const mapDir = path.join(root, "map");
const modelDir = path.join(root, "RootDesk/MyDesk/Models/Monsters");

function fail(message) { throw new Error(message); }
function rows(file) {
  const text = fs.readFileSync(path.join(dataDir, file), "utf8").replace(/^\uFEFF/, "").trim();
  const [head, ...lines] = text.split(/\r?\n/);
  const headers = head.split(",");
  return lines.filter(Boolean).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((header, i) => [header, values[i] || ""]));
  });
}

const areaIds = ["area_07", "area_08", "area_09", "area_10"];
const tilesets = {
  area_07:"tileset://7a070000-0000-4000-8000-000000000007",
  area_08:"tileset://7a080000-0000-4000-8000-000000000008",
  area_09:"tileset://7a090000-0000-4000-8000-000000000009",
  area_10:"tileset://7a100000-0000-4000-8000-000000000010",
};
const expectedMonsters = {
  area_07:["m_zombie_mushroom","m_copper_drake","m_drake","m_wild_kargo","m_tauromacis"],
  area_08:["m_star_pixie","m_jr_cellion","m_lunar_pixie","m_luster_pixie","m_eliza"],
  area_09:["m_jr_yeti","m_dark_jr_yeti","m_hector","m_white_fang","m_snow_witch"],
  area_10:["m_bubble_fish","m_mask_fish","m_squid","m_shark","m_pianus"],
};
const fileByMonster = {
  m_zombie_mushroom:"ZombieMushroom",m_copper_drake:"CopperDrake",m_drake:"Drake",m_wild_kargo:"WildKargo",m_tauromacis:"Tauromacis",
  m_star_pixie:"StarPixie",m_jr_cellion:"JrCellion",m_lunar_pixie:"LunarPixie",m_luster_pixie:"LusterPixie",m_eliza:"Eliza",
  m_jr_yeti:"JrYeti",m_dark_jr_yeti:"DarkJrYeti",m_hector:"Hector",m_white_fang:"WhiteFang",m_snow_witch:"SnowWitch",
  m_bubble_fish:"BubbleFish",m_mask_fish:"MaskFish",m_squid:"Squid",m_shark:"Shark",m_pianus:"Pianus",
};
const opposite = {north:"south",south:"north",east:"west",west:"east"};
const portalName = {north:"Portal_N",south:"Portal_S",east:"Portal_E",west:"Portal_W"};

const allAreas = rows("AreaTable.csv");
const allRooms = rows("RoomTable.csv");
const allMonsters = rows("MonsterTable.csv");
const allSkills = rows("SkillTable.csv");
const allItems = rows("ItemTable.csv");
const landmarks = rows("LandmarkTable.csv");
const roomById = new Map(allRooms.map((row) => [row.id, row]));
const monsterById = new Map(allMonsters.map((row) => [row.id, row]));
const skillById = new Map(allSkills.map((row) => [row.id, row]));

const sectorText = fs.readFileSync(path.join(root, "Global/SectorConfig.config"), "utf8");
const sectorMissing = [];
const summaries = [];

for (let areaIndex = 0; areaIndex < areaIds.length; areaIndex++) {
  const areaId = areaIds[areaIndex];
  const area = allAreas.find((row) => row.id === areaId);
  if (!area) fail(`${areaId}: AreaTable 누락`);
  if (Number(area.sort_order) !== areaIndex + 7) fail(`${areaId}: sort_order ${area.sort_order}`);
  const expectedUnlock = (areaIndex + 6) * 10;
  if (!landmarks.some((row) => Number(row.level) === expectedUnlock && row.reward_value === areaId)) fail(`${areaId}: Lv${expectedUnlock} 랜드마크 누락`);

  const areaRooms = allRooms.filter((room) => room.area_id === areaId);
  if (areaRooms.length !== 8) fail(`${areaId}: 방 ${areaRooms.length}개`);
  const actualMonsterIds = [...new Set(areaRooms.map((room) => room.monster_id))].sort();
  const expectedIds = expectedMonsters[areaId].slice().sort();
  if (JSON.stringify(actualMonsterIds) !== JSON.stringify(expectedIds)) fail(`${areaId}: 몬스터 구성 불일치 ${actualMonsterIds}`);

  const areaSkills = expectedIds.map((monsterId) => {
    const monster = monsterById.get(monsterId);
    if (!monster) fail(`${monsterId}: MonsterTable 누락`);
    const level = Number(monster.level);
    const hp = Math.round(144 + 34.2 * (level - 1));
    const def = Math.round((80 + 19 * (level - 1)) * 10) / 10;
    const exp = Math.round(5 * Math.pow(1.10, level - 1));
    if (Number(monster.hp) !== hp || Number(monster.def) !== def || Number(monster.exp) !== exp) fail(`${monsterId}: 공식 수치 불일치`);
    const skill = skillById.get(monster.drop_skill_id);
    if (!skill) fail(`${monsterId}: 포획 스킬 누락`);
    if (!skill.icon_ruid) fail(`${skill.id}: 아이콘 누락`);
    if (skill.skill_kind !== "passive" && !skill.layer_ruids && !skill.projectile_ruid) fail(`${skill.id}: 액티브 연출 누락`);
    const drops = allItems.filter((item) => item.drop_from === monsterId);
    if (drops.length !== 1) fail(`${monsterId}: 장비 드랍 ${drops.length}개`);
    if (drops[0].item_type !== "equip" || !drops[0].icon_ruid.startsWith("thumbnail://")) fail(`${monsterId}: 장비 형식 불일치`);

    const model = ModelBuilder.read(path.join(modelDir, `${fileByMonster[monsterId]}.model`));
    const errors = model.validate().filter((finding) => finding.severity === "error");
    if (errors.length) fail(`${monsterId}: 모델 오류 ${JSON.stringify(errors)}`);
    return skill;
  });
  const passives = areaSkills.filter((skill) => skill.skill_kind === "passive").length;
  if (passives !== 2 || areaSkills.length - passives !== 3) fail(`${areaId}: 액티브/패시브 ${areaSkills.length-passives}/${passives}`);

  for (const room of areaRooms) {
    const map = MapBuilder.read(path.join(mapDir, `${room.map_name}.map`));
    const info = map.getMapInfo();
    if (info.TileMapMode !== 1 || info.tileCount !== 448) fail(`${room.map_name}: mode/tile ${info.TileMapMode}/${info.tileCount}`);
    const tileMap = map.component("RectTileMap", "MOD.Core.RectTileMapComponent");
    if (!tileMap || tileMap.TileSetRUID !== tilesets[areaId]) fail(`${room.map_name}: tileset 불일치`);
    const tileKinds = [...new Set(map.getTiles().map((tile) => tile.tileIndex))];
    const hasHazard = tileKinds.includes(3);
    const hasBoundary = Boolean(map.component(room.map_name, "script.NautilusWaterBoundary"));
    if (hasHazard !== hasBoundary) fail(`${room.map_name}: 위험 타일 경계 ${hasHazard}/${hasBoundary}`);
    const names = new Set(map.listEntities().map((entity) => entity.name));
    for (const dir of Object.keys(opposite)) {
      const target = room[`conn_${dir}`];
      if (Boolean(target) !== names.has(portalName[dir])) fail(`${room.id}: ${dir} 포탈 불일치`);
      if (target && roomById.has(target) && roomById.get(target).area_id === areaId) {
        if (roomById.get(target)[`conn_${opposite[dir]}`] !== room.id) fail(`${room.id}->${target}: 역연결 누락`);
      }
    }
    if ((room.room_type === "boss") !== names.has("Portal_Return")) fail(`${room.id}: 보스 귀환 포탈 불일치`);
    if (!sectorText.includes(`\"map://${room.map_name}\"`)) sectorMissing.push(room.map_name);
  }
  summaries.push({areaId,rooms:areaRooms.length,monsters:actualMonsterIds,active:3,passive:2});
}

console.log(JSON.stringify({summaries,totalRooms:32,totalMonsters:20,totalSkills:20,totalItems:20,tileCountEach:448,reciprocalConnections:true,hazardBoundaries:true,sectorMissing}, null, 2));
if (sectorMissing.length) console.warn("Maker Refresh와 Save 뒤 SectorConfig 등록을 다시 확인해야 합니다.");
