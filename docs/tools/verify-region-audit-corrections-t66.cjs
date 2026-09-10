const fs = require("node:fs");
const path = require("node:path");
const { MapBuilder } = require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const { ModelBuilder } = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const root = path.resolve(__dirname, "../..");
const dataDir = path.join(root, "RootDesk/MyDesk/GameData");
const fail = (message) => { throw new Error(message); };
function rows(file) {
  const text = fs.readFileSync(path.join(dataDir, file), "utf8").replace(/^\uFEFF/, "").trim();
  const [head, ...lines] = text.split(/\r?\n/);
  const headers = head.split(",");
  return lines.filter(Boolean).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, values[index] || ""]));
  });
}

const monsters = rows("MonsterTable.csv");
const skills = rows("SkillTable.csv");
const items = rows("ItemTable.csv");
const rooms = rows("RoomTable.csv");
const byId = (list, id) => list.find((row) => row.id === id);

const king = byId(monsters, "m_king_clang");
if (!king || king.name !== "킹크랑" || Number(king.level) !== 60 || Number(king.hp) !== 2162 || king.model_id !== "kingclang") fail("킹크랑 몬스터 데이터 불일치");
const balrog = byId(monsters, "m_jr_balrog");
if (!balrog || Number(balrog.level) !== 70 || Number(balrog.hp) !== 2504) fail("주니어 발록 Lv70 보정 불일치");
const kingSkill = byId(skills, "s_mon_king_clang");
if (!kingSkill || kingSkill.is_key_skill !== "true" || kingSkill.skill_kind !== "attack" || kingSkill.layer_ruids.split("|").length !== 2) fail("킹크랑 스킬 불일치");
if (byId(skills, "s_mon_tauromacis").is_key_skill !== "false") fail("타우로마시스 열쇠 잔존");
const kingItem = byId(items, "i_king_clang_yellow_umbrella");
if (!kingItem || kingItem.name !== "노란 우산" || kingItem.drop_from !== "m_king_clang" || kingItem.icon_ruid !== "thumbnail://8668230e7f024e21997ad7f0518db3e3") fail("킹크랑 장비 불일치");
if (Number(byId(items, "i_tauromacis_sledge").drop_rate) !== 0.03) fail("타우로마시스 일반 드롭률 불일치");

const roomChecks = {
  r_055: ["m_king_clang", "boss", ""],
  r_07a: ["m_wild_kargo", "hunt", "s_mon_king_clang"],
  r_074: ["m_tauromacis", "hunt", "STAT_TOTAL"],
  r_075: ["m_jr_balrog", "boss", ""],
  r_08a: ["m_luster_pixie", "hunt", "s_mon_jr_balrog"],
};
for (const [id, [monsterId, roomType, gateKey]] of Object.entries(roomChecks)) {
  const room = byId(rooms, id);
  if (!room || room.monster_id !== monsterId || room.room_type !== roomType || room.gate_key !== gateKey) fail(`${id}: 보스 이동/게이트 불일치`);
}

const model = ModelBuilder.read(path.join(root, "RootDesk/MyDesk/Models/Monsters/KingClang.model"));
const modelErrors = model.validate().filter((finding) => finding.severity === "error");
if (modelErrors.length) fail(`KingClang.model 오류 ${JSON.stringify(modelErrors)}`);

const tilesets = [
  ["RectTileData_Sleepywood.tileset", "Sleepywood_lava_fissure", "1b14ae7d99984a8f87e070ebfbe4d79d", true],
  ["RectTileData_Orbis.tileset", "Orbis_eliza_moon_garden", "66a9ca3a9668407882ed8e6c79ebd913", false],
  ["RectTileData_ElNath.tileset", "Nihal_oasis_water", "525db3dd32cc4652bf1af4b508dbe6bf", true],
];
for (const [file, name, ruid, collidable] of tilesets) {
  const data = JSON.parse(fs.readFileSync(path.join(root, "RootDesk/MyDesk", file), "utf8")).ContentProto.Json.datas;
  const index = data.findIndex((tile) => tile.Name === name);
  if (index !== 8 || data[index].Id !== ruid || data[index].IsCollidable !== collidable) fail(`${file}: T66 타일 인덱스/충돌 불일치`);
}

const tileCounts = {};
for (const mapName of ["map077", "map085", "map13a"]) {
  const map = MapBuilder.read(path.join(root, "map", `${mapName}.map`));
  if (map.getMapInfo().tileCount !== 448) fail(`${mapName}: 448칸 불일치`);
  const count = map.getTiles("RectTileMap").filter((tile) => tile.tileIndex === 8).length;
  if (count < 8) fail(`${mapName}: T66 타일이 너무 적음 ${count}`);
  tileCounts[mapName] = count;
}

const totals={monsters:monsters.filter((monster)=>!monster.id.startsWith("m_adv_")).length,monsterSkills:skills.filter((skill)=>skill.source==="monster").length,items:items.length};
if(totals.monsters<71||totals.monsterSkills<71||totals.items<74)fail("T66 이후 콘텐츠가 기준 수보다 줄어듦");
console.log(JSON.stringify({kingClang:"공식 리소스 모델",bossPlacement:{nautilus:"킹크랑",sleepywood:"주니어 발록"},tileCounts,totals},null,2));
