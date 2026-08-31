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

const monsters = readCsv("RootDesk/MyDesk/GameData/MonsterTable.csv")
  .filter((monster) => monster.id !== "m_adv_hero");
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
const missingItem = monsters
  .filter((monster) => !items.some((item) => item.drop_from.split("|").includes(monster.id)))
  .map((monster) => monster.id);
const badRuid = [
  ...skills
    .filter((skill) => skill.source === "monster" && skill.icon_ruid.length !== 32)
    .map((skill) => "skill:" + skill.id),
  ...items
    .filter((item) => item.icon_ruid.length !== 32)
    .map((item) => "item:" + item.id),
];
const passiveEffectResidue = skills
  .filter((skill) => skill.skill_kind === "passive")
  .filter((skill) => skill.effect_ruid || skill.effect_style || skill.sfx_ruid
    || skill.projectile_ruid || Number(skill.effect_value) !== 0
    || Number(skill.duration) !== 0 || Number(skill.range) !== 0
    || Number(skill.dash_distance) !== 0)
  .map((skill) => skill.id);
const activeWithoutVisual = skills
  .filter((skill) => skill.source === "monster" && skill.skill_kind !== "passive")
  .filter((skill) => !skill.effect_ruid && !skill.projectile_ruid)
  .map((skill) => skill.id);
const bossRooms = rooms.filter((room) => room.room_type === "boss");
const bossItemMissing = bossRooms
  // 모험가 시험 상대는 장비 대신 직업 스킬 5종을 확정 지급하는 NPC다.
  .filter((room) => room.monster_id !== "m_adv_hero")
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
for (let i = 0; i < 29; i += 1) {
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
const inventoryIconAlphaOk = Array.from({ length: 29 }, (_, i) => {
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

const result = {
  monsters: monsters.length,
  monsterSkills: skills.filter((skill) => skill.source === "monster").length,
  items: items.length,
  missingSkill,
  missingItem,
  badRuid,
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
};

console.log(JSON.stringify(result, null, 2));

if (missingSkill.length || missingItem.length || badRuid.length
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
  || result.inventorySlots !== 29 || !result.bindingsOk || !result.inventoryIconAlphaOk
  || result.equipCells !== 28 || !result.equipCellCountOk
  || result.skillGridColumns !== 5 || !result.skillIconAlphaOk
  || !result.roomProgressDisabled || result.worldMapTop !== -150
  || result.worldMapButtons !== 12 || result.popupEntities !== 18 || !result.popupBindingsOk
  || henesysBoss.monster_id !== "m_mushmom"
  || kerningBoss.monster_id !== "m_shade"
  || bossGate.gate_type !== "key" || bossGate.gate_key !== "s_mon_mushmom"
  || gate.gate_type !== "key" || gate.gate_key !== "s_mon_shade") {
  process.exitCode = 1;
}
