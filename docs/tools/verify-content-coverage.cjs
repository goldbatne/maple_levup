const fs = require("fs");

function readCsv(filepath) {
  const lines = fs.readFileSync(filepath, "utf8")
    .replace(/^\uFEFF/, "")
    .trim()
    .split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line) => Object.fromEntries(
    line.split(",").map((value, index) => [headers[index], value]),
  ));
}

function readUiTransform(filepath, path) {
  const ui = JSON.parse(fs.readFileSync(filepath, "utf8"));
  const entry = ui.ContentProto.Entities.find((entity) => {
    const json = typeof entity.jsonString === "string"
      ? JSON.parse(entity.jsonString) : entity.jsonString;
    return json.path === path;
  });
  if (!entry) return null;
  const json = typeof entry.jsonString === "string"
    ? JSON.parse(entry.jsonString) : entry.jsonString;
  return json["@components"].find(
    (component) => component["@type"] === "MOD.Core.UITransformComponent",
  ) || null;
}

function readUiComponent(filepath, path, type) {
  const ui = JSON.parse(fs.readFileSync(filepath, "utf8"));
  const entry = ui.ContentProto.Entities.find((entity) => {
    const json = typeof entity.jsonString === "string"
      ? JSON.parse(entity.jsonString) : entity.jsonString;
    return json.path === path;
  });
  if (!entry) return null;
  const json = typeof entry.jsonString === "string"
    ? JSON.parse(entry.jsonString) : entry.jsonString;
  return json["@components"].find((component) => component["@type"] === type) || null;
}

const allMonsters = readCsv("RootDesk/MyDesk/GameData/MonsterTable.csv");
const monsters = allMonsters.filter((monster) => monster.id !== "m_adv_hero");
const skills = readCsv("RootDesk/MyDesk/GameData/SkillTable.csv");
const items = readCsv("RootDesk/MyDesk/GameData/ItemTable.csv");
const rooms = readCsv("RootDesk/MyDesk/GameData/RoomTable.csv");
const balanceRows = readCsv("RootDesk/MyDesk/GameData/GameBalance.csv");
const balance = new Map(balanceRows.map((row) => [row.key, Number(row.value)]));
const skillIds = new Set(skills.map((skill) => skill.id));
const skillById = new Map(skills.map((skill) => [skill.id, skill]));

const missingSkill = monsters
  .filter((monster) => !monster.drop_skill_id || !skillIds.has(monster.drop_skill_id))
  .map((monster) => monster.id);
const missingItem = allMonsters
  .filter((monster) => !items.some((item) => item.drop_from.split("|").includes(monster.id)))
  .map((monster) => monster.id);
const validItemIcon = (item) => /^(thumbnail:\/\/)?[0-9a-f]{32}$/.test(item.icon_ruid);
const badRuid = [
  ...skills
    .filter((skill) => skill.source === "monster" && skill.icon_ruid.length !== 32)
    .map((skill) => "skill:" + skill.id),
  ...items
    .filter((item) => !validItemIcon(item))
    .map((item) => "item:" + item.id),
];
const specificItems = items.filter((item) => item.drop_from !== "*");
const badItemTypeMapping = specificItems
  .filter((item) => item.item_type !== "equip" && item.id !== "i_hero_sword")
  .map((item) => item.id);
const validEquipSlots = new Set(["weapon", "armor", "accessory"]);
const badEquipment = specificItems
  .filter((item) => item.item_type === "equip")
  .filter((item) => !validEquipSlots.has(item.slot) || !/원작 아이템 \d+/.test(item.note))
  .map((item) => item.id);
const heroPassive = items.find((item) => item.id === "i_hero_sword");
const heroPassiveOk = heroPassive !== undefined
  && heroPassive.name === "히어로의 검"
  && heroPassive.item_type === "passive"
  && heroPassive.slot === ""
  && heroPassive.passive_stat === "STR"
  && Number(heroPassive.passive_rate) === 0.01
  && Number(heroPassive.stack_max) === 5
  && heroPassive.drop_from === "m_adv_hero";
const heroCombatOnlyOk = skills.filter((skill) => skill.id.startsWith("s_hero_"))
  .every((skill) => skill.source === "boss" && skill.slot_type === "enemy")
  && allMonsters.find((monster) => monster.id === "m_adv_hero")?.combat_skill_ids
    === "s_hero_01|s_hero_def|s_hero_02|s_hero_03|s_hero_04";
const correctedPassiveEquipment = new Map([
  ["i_maple_spear", { name: "메이플 스피어", slot: "weapon", stat_atk: 5, itemId: "1432012", ruid: "a911d7794deb4d04a32188b55eda32ab" }],
  ["i_bronze_crusader_helm", { name: "브론즈 크루세이더 헬름", slot: "armor", stat_def: 6, itemId: "1002086", ruid: "1147bf323fb74b949312a89dc350f506" }],
  ["i_maple_sword", { name: "메이플 소드", slot: "weapon", stat_luk: 5, itemId: "1302020", ruid: "4668b7ab224449fc94805e2e6cb0f6f5" }],
  ["i_work_glove", { name: "노가다 목장갑", slot: "armor", stat_luk: 7, itemId: "1082002", ruid: "2e58683f2f094f099a0813c36e278dd5" }],
  ["i_maple_lama_staff", { name: "메이플 라마 스태프", slot: "weapon", stat_int: 7, itemId: "1382012", ruid: "be49540382d54da6a01fefcc4cd10e83" }],
  ["i_steel_mail", { name: "스틸 메일", slot: "armor", stat_def: 8, itemId: "1051000", ruid: "d936956da3ec44079be5dcb6bf08a69f" }],
  ["i_dragon_halberd", { name: "구룡도", slot: "weapon", stat_int: 8, itemId: "1442005", ruid: "46424df07a1c4f139784aa859051b4bd" }],
]);
const legacyMaterialIds = new Set([
  "i_sword_iron",
  "i_iron_hoof",
  "i_bubbling_orb",
  "i_stirge_wing",
  "i_wraith_soul",
  "i_blue_ribbon",
  "i_cool_jelly",
]);
const legacyMaterialResidue = items
  .filter((item) => legacyMaterialIds.has(item.id))
  .map((item) => item.id);
const badCorrectedPassiveEquipment = [];
for (const [id, expected] of correctedPassiveEquipment) {
  const item = items.find((candidate) => candidate.id === id);
  if (!item || item.name !== expected.name || item.item_type !== "equip" || item.slot !== expected.slot
    || Number(item.stack_max) !== 5
    || Number(item.stat_atk) !== (expected.stat_atk || 0)
    || Number(item.stat_int) !== (expected.stat_int || 0)
    || Number(item.stat_def) !== (expected.stat_def || 0)
    || Number(item.stat_luk) !== (expected.stat_luk || 0)
    || item.icon_ruid !== `thumbnail://${expected.ruid}`
    || !item.note.includes(`원작 아이템 ${expected.itemId}`)) {
    badCorrectedPassiveEquipment.push(id);
  }
}
const passiveEffectResidue = skills
  .filter((skill) => skill.skill_kind === "passive")
  .filter((skill) => skill.effect_ruid || skill.effect_style || skill.sfx_ruid
    || skill.projectile_ruid || Number(skill.effect_value) !== 0
    || Number(skill.duration) !== 0 || Number(skill.range) !== 0
    || Number(skill.dash_distance) !== 0)
  .map((skill) => skill.id);
const activeWithoutVisual = skills
  .filter((skill) => (skill.source === "monster" || skill.source === "boss") && skill.skill_kind !== "passive")
  .filter((skill) => !skill.effect_ruid && !skill.projectile_ruid)
  .map((skill) => skill.id);
const bossRooms = rooms.filter((room) => room.room_type === "boss");
const bossItemMissing = bossRooms
  .filter((room) => !items.some((item) => item.drop_from.split("|").includes(room.monster_id)))
  .map((room) => room.id + ":" + room.monster_id);

function kinds(ids) {
  return ids.map((id) => {
    const skill = skills.find((one) => one.id === "s_mon_" + id);
    return skill === undefined ? "missing" : skill.skill_kind;
  });
}

const gate = rooms.find((room) => room.id === "r_05a");
const henesysBoss = rooms.find((room) => room.id === "r_05");
const kerningBoss = rooms.find((room) => room.id === "r_045");
const bossGate = rooms.find((room) => room.id === "r_29");
const gateSkills = [gate, bossGate]
  .filter((room) => room && room.gate_type === "key")
  .map((room) => room.gate_key);
const badGateSkills = gateSkills
  .filter((id) => !skillById.has(id) || skillById.get(id).is_key_skill !== "true");
const ui = JSON.parse(fs.readFileSync("ui/Inventory.ui", "utf8"));
const entities = ui.ContentProto.Entities.map((entity) => ({
  id: entity.id,
  path: (typeof entity.jsonString === "string"
    ? JSON.parse(entity.jsonString)
    : entity.jsonString).path,
}));
const mlua = fs.readFileSync("RootDesk/MyDesk/UI/InventoryPanel.mlua", "utf8");
const equipUi = JSON.parse(fs.readFileSync("ui/EquipWindow.ui", "utf8"));
const equipEntities = equipUi.ContentProto.Entities.map((entity) => ({
  path: (typeof entity.jsonString === "string"
    ? JSON.parse(entity.jsonString)
    : entity.jsonString).path,
}));
const equipMlua = fs.readFileSync("RootDesk/MyDesk/UI/EquipPanel.mlua", "utf8");
const playerHudUi = JSON.parse(fs.readFileSync("ui/PlayerHud.ui", "utf8"));
const playerHudEntities = playerHudUi.ContentProto.Entities.map((entity) => ({
  id: entity.id,
  path: (typeof entity.jsonString === "string"
    ? JSON.parse(entity.jsonString)
    : entity.jsonString).path,
}));
const playerHudMlua = fs.readFileSync("RootDesk/MyDesk/UI/PlayerHud.mlua", "utf8");
const roomSpawnerMlua = fs.readFileSync("RootDesk/MyDesk/Room/RoomSpawner.mlua", "utf8");
const itemDropMlua = fs.readFileSync("RootDesk/MyDesk/Inventory/ItemDrop.mlua", "utf8");
const playerStatsMlua = fs.readFileSync("RootDesk/MyDesk/Player/PlayerStats.mlua", "utf8");
const playerInventoryMlua = fs.readFileSync("RootDesk/MyDesk/Inventory/PlayerInventory.mlua", "utf8");
const roomMonsterMlua = fs.readFileSync("RootDesk/MyDesk/Combat/RoomMonster.mlua", "utf8");
const playerCollectionMlua = fs.readFileSync("RootDesk/MyDesk/Progress/PlayerCollection.mlua", "utf8");
const monsterAttackMlua = fs.readFileSync("RootDesk/MyDesk/MonsterAttack.mlua", "utf8");
const playerDbMlua = fs.readFileSync("RootDesk/MyDesk/Save/PlayerDBManager.mlua", "utf8");
const topMenuTransforms = [
  ["stat", "ui/StatGroup.ui", "/ui/StatGroup/OpenBtn", -478],
  ["skill", "ui/EquipWindow.ui", "/ui/EquipWindow/OpenBtn", -354],
  ["bag", "ui/Inventory.ui", "/ui/Inventory/OpenBtn", -230],
].map(([name, file, path, expectedRight]) => {
  const transform = readUiTransform(file, path);
  return [name, transform, expectedRight];
});
const topMenuWidths = topMenuTransforms.map(([name, transform]) => [
  name, transform === null ? null : transform.RectSize.x,
]);
const topMenuRightEdges = topMenuTransforms.map(([name, transform]) => [
  name, transform === null ? null : transform.anchoredPosition.x,
]);
const bindings = [];
for (let i = 0; i < 30; i += 1) {
  const match = mlua.match(new RegExp(
    "property ButtonComponent itemRow" + i + " = \"([^\"]+)\"",
  ));
  const expectedPath = "/ui/Inventory/Window/Box/ItemRow" + i;
  bindings.push(match !== null && entities.some(
    (entity) => entity.id === match[1] && entity.path === expectedPath,
  ));
}

const bossBindingPaths = {
  bossRoot: "/ui/PlayerHud/BossHud",
  bossBarRoot: "/ui/PlayerHud/BossHudBar",
  bossFill: "/ui/PlayerHud/BossHudFill",
  bossNameText: "/ui/PlayerHud/BossHudName",
  bossHpText: "/ui/PlayerHud/BossHudHpText",
  bossTimeText: "/ui/PlayerHud/BossHudTime",
};
const bossBindingsOk = Object.entries(bossBindingPaths).every(([property, path]) => {
  const match = playerHudMlua.match(new RegExp(
    "property (?:Entity|UITransformComponent|TextGUIRendererComponent) "
      + property + " = \"([^\"]+)\"",
  ));
  return match !== null && playerHudEntities.some(
    (entity) => entity.id === match[1] && entity.path === path,
  );
});

const worldMapUi = JSON.parse(fs.readFileSync("ui/WorldMap.ui", "utf8"));
const worldMapEntities = worldMapUi.ContentProto.Entities.map((entity) => {
  const json = typeof entity.jsonString === "string"
    ? JSON.parse(entity.jsonString) : entity.jsonString;
  return { id: entity.id, path: json.path, components: json["@components"] };
});
const worldMapMlua = fs.readFileSync("RootDesk/MyDesk/UI/WorldMapPanel.mlua", "utf8");
const roomProgressMlua = fs.readFileSync("RootDesk/MyDesk/UI/RoomProgressHud.mlua", "utf8");
const worldMapTransform = readUiTransform("ui/WorldMap.ui", "/ui/WorldMap/Panel");
const worldMapButtons = worldMapEntities.filter((entity) => (
  /\/Board\/Cell\d+$/.test(entity.path)
  && entity.components.some((component) => component["@type"] === "MOD.Core.ButtonComponent")
)).length;
const popupBindingPaths = {
  popup: "/ui/WorldMap/RoomInfoPopup",
  popupClose: "/ui/WorldMap/RoomInfoPopup/Close",
  popupTitle: "/ui/WorldMap/RoomInfoPopup/Title",
  popupMonster: "/ui/WorldMap/RoomInfoPopup/MonsterCard/Monster",
  popupRow1: "/ui/WorldMap/RoomInfoPopup/Drop1",
  popupRow2: "/ui/WorldMap/RoomInfoPopup/Drop2",
  popupRow3: "/ui/WorldMap/RoomInfoPopup/Drop3",
  popupRow4: "/ui/WorldMap/RoomInfoPopup/Drop4",
};
const popupBindingsOk = Object.entries(popupBindingPaths).every(([property, path]) => {
  const match = worldMapMlua.match(new RegExp(
    "property (?:Entity|ButtonComponent|TextGUIRendererComponent) "
      + property + " = \"([^\"]+)\"",
  ));
  return match !== null && worldMapEntities.some(
    (entity) => entity.id === match[1] && entity.path === path,
  );
});
const inventoryIconAlphaOk = Array.from({ length: 30 }, (_, i) => {
  const path = "/ui/Inventory/Window/Box/ItemRow" + i + "/Icon";
  const sprite = readUiComponent("ui/Inventory.ui", path, "MOD.Core.SpriteGUIRendererComponent");
  const transform = readUiTransform("ui/Inventory.ui", path);
  return sprite !== null && sprite.Color.a === 1
    && transform !== null && transform.anchoredPosition.x === 0;
}).every(Boolean);
const skillGrid = readUiComponent(
  "ui/EquipWindow.ui", "/ui/EquipWindow/Window/Grid", "MOD.Core.ScrollLayoutGroupComponent",
);
const skillIconAlphaOk = Array.from({ length: 28 }, (_, i) => {
  const sprite = readUiComponent(
    "ui/EquipWindow.ui", `/ui/EquipWindow/Window/Grid/Cell${i + 1}/Icon`,
    "MOD.Core.SpriteGUIRendererComponent",
  );
  return sprite !== null && sprite.Color.a === 1;
}).every(Boolean);

const popupRewardTitle = readUiComponent(
  "ui/WorldMap.ui",
  "/ui/WorldMap/RoomInfoPopup/DropLabel",
  "MOD.Core.TextGUIRendererComponent",
);

const result = {
  monsters: monsters.length,
  monsterSkills: skills.filter((skill) => skill.source === "monster").length,
  items: items.length,
  missingSkill,
  missingItem,
  badRuid,
  equipmentItems: specificItems.filter((item) => item.item_type === "equip").length,
  passiveItems: specificItems.filter((item) => item.item_type === "passive").length,
  heroPassiveOk,
  heroCombatOnlyOk,
  heroPassiveWiringOk: /method number GetPassiveItemRate/.test(playerStatsMlua)
    && /GetPassiveItemRate\("STR"\)/.test(playerStatsMlua)
    && /GetPassiveItemBonus\("ATK"\)/.test(playerStatsMlua)
    && /record\.item_type == "passive"/.test(playerInventoryMlua)
    && /stats:ApplyMaxHp\(\)/.test(playerInventoryMlua),
  heroRewardSeparationOk: !/GrantNpcSkills/.test(roomMonsterMlua)
    && !/GrantNpcSkills/.test(playerCollectionMlua)
    && /GetCombatSkillIds/.test(monsterAttackMlua)
    && /skill\.source == "monster"/.test(playerDbMlua),
  badItemTypeMapping,
  badEquipment,
  badCorrectedPassiveEquipment,
  legacyMaterialResidue,
  passiveEffectResidue,
  activeWithoutVisual,
  bossRooms: bossRooms.map((room) => room.id + ":" + room.monster_id),
  bossItemMissing,
  bossHpMultiplier: balance.get("boss_hp_multiplier"),
  bossTimeLimitSeconds: balance.get("boss_time_limit_seconds"),
  bossHudEntities: playerHudEntities.filter((entity) => entity.path.startsWith("/ui/PlayerHud/BossHud")).length,
  bossBindingsOk,
  bossTimerWiringOk: /BossRemainingSeconds/.test(roomSpawnerMlua)
    && /FinishBossTimeOver/.test(roomSpawnerMlua)
    && /ExpireBoss/.test(roomSpawnerMlua),
  bossGuaranteedDropWiringOk: /guaranteedBossItem/.test(itemDropMlua)
    && /item\.drop_from ~= "\*"/.test(itemDropMlua),
  topMenuWidths: Object.fromEntries(topMenuWidths),
  topMenuRightEdges: Object.fromEntries(topMenuRightEdges),
  badGateSkills,
  area04Kinds: kinds(["octopus", "stirge", "jr_wraith", "shade", "wraith"]),
  area05Kinds: kinds(["ribbon_pig", "blue_pig", "starfish", "jellyfish", "jr_balrog"]),
  henesysBoss: henesysBoss.monster_id,
  kerningBoss: kerningBoss.monster_id,
  henesysGate: [bossGate.gate_type, bossGate.gate_key, bossGate.gate_value],
  nautilusGate: [gate.gate_type, gate.gate_key, gate.gate_value],
  inventorySlots: entities.filter((entity) => /Inventory\/Window\/Box\/ItemRow\d+$/.test(entity.path)).length,
  bindingsOk: bindings.every(Boolean),
  inventoryIconAlphaOk,
  equipCells: equipEntities.filter((entity) => /EquipWindow\/Window\/Grid\/Cell\d+$/.test(entity.path)).length,
  equipCellCountOk: /property integer cellCount = 28\b/.test(equipMlua),
  skillGridColumns: skillGrid === null ? null : skillGrid.ConstraintCount,
  skillIconAlphaOk,
  roomProgressDisabled: /T54 비활성/.test(roomProgressMlua),
  worldMapTop: worldMapTransform === null ? null : worldMapTransform.anchoredPosition.y,
  worldMapButtons,
  popupEntities: worldMapEntities.filter((entity) => entity.path.startsWith("/ui/WorldMap/RoomInfoPopup")).length,
  popupBindingsOk,
  popupRewardTitleOk: popupRewardTitle?.Text === "획득 가능한 보상"
    || (/popupRewardTitle/.test(worldMapMlua)
      && /popupRewardTitle\.Text = "획득 가능한 보상"/.test(worldMapMlua)),
  worldMapRewardWiringOk: /monster\.drop_skill_id/.test(worldMapMlua)
    && /item\.item_type ~= "consume"/.test(worldMapMlua)
    && /공통 소비 아이템 제외/.test(worldMapMlua)
    && !/popupMonster\.Text[\s\S]{0,180}room\.monster_count/.test(worldMapMlua),
};

console.log(JSON.stringify(result, null, 2));

if (missingSkill.length || missingItem.length || badRuid.length
  || badItemTypeMapping.length || badEquipment.length || badCorrectedPassiveEquipment.length
  || !heroPassiveOk || !heroCombatOnlyOk
  || !result.heroPassiveWiringOk || !result.heroRewardSeparationOk
  || legacyMaterialResidue.length
  || passiveEffectResidue.length || activeWithoutVisual.length || badGateSkills.length
  || bossRooms.length !== 6 || bossItemMissing.length
  || balance.get("boss_hp_multiplier") !== 10
  || balance.get("boss_time_limit_seconds") !== 300
  || result.bossHudEntities !== 6 || !result.bossBindingsOk
  || !result.bossTimerWiringOk || !result.bossGuaranteedDropWiringOk
  || topMenuWidths.some(([, width]) => width !== 112)
  || topMenuTransforms.some(([, transform, expectedRight]) => (
    transform === null || transform.anchoredPosition.x !== expectedRight
  ))
  || result.inventorySlots !== 30 || !result.bindingsOk || !result.inventoryIconAlphaOk
  || result.equipCells !== 28 || !result.equipCellCountOk
  || result.skillGridColumns !== 5 || !result.skillIconAlphaOk
  || !result.roomProgressDisabled || result.worldMapTop !== -150
  || result.worldMapButtons !== 12 || result.popupEntities !== 18 || !result.popupBindingsOk
  || !result.popupRewardTitleOk || !result.worldMapRewardWiringOk
  || henesysBoss.monster_id !== "m_mushmom"
  || kerningBoss.monster_id !== "m_shade"
  || bossGate.gate_type !== "key" || bossGate.gate_key !== "s_mon_mushmom"
  || gate.gate_type !== "key" || gate.gate_key !== "s_mon_shade") {
  process.exitCode = 1;
}
