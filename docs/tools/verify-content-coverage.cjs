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
const monsters = allMonsters.filter((monster) => !monster.id.startsWith("m_adv_"));
const skills = readCsv("RootDesk/MyDesk/GameData/SkillTable.csv");
const items = readCsv("RootDesk/MyDesk/GameData/ItemTable.csv");
const rooms = readCsv("RootDesk/MyDesk/GameData/RoomTable.csv");
const balanceRows = readCsv("RootDesk/MyDesk/GameData/GameBalance.csv");
const balance = new Map(balanceRows.map((row) => [row.key, Number(row.value)]));
const skillIds = new Set(skills.map((skill) => skill.id));
const skillById = new Map(skills.map((skill) => [skill.id, skill]));
const splitPipe = (value) => value ? value.split("|") : [];

const missingSkill = monsters
  .filter((monster) => !monster.drop_skill_id || !skillIds.has(monster.drop_skill_id))
  .map((monster) => monster.id);
const missingItem = allMonsters
  .filter((monster) => !items.some((item) => item.drop_from.split("|").includes(monster.id)))
  .map((monster) => monster.id);
const validItemIcon = (item) => /^(thumbnail:\/\/)?[0-9a-f]{32}$/.test(item.icon_ruid);
const validSkillIcon = (value) => /^(thumbnail:\/\/)?[0-9a-f]{32}$/.test(value);
const badRuid = [
  ...skills
    .filter((skill) => skill.source === "monster" && !validSkillIcon(skill.icon_ruid))
    .map((skill) => "skill:" + skill.id),
  ...items
    .filter((item) => !validItemIcon(item))
    .map((item) => "item:" + item.id),
];
const specificItems = items.filter((item) => item.drop_from !== "*");
const badItemTypeMapping = specificItems
  .filter((item) => item.item_type !== "equip" && item.item_type !== "passive")
  .map((item) => item.id);
const validEquipSlots = new Set(["weapon", "armor", "accessory"]);
const validAvatarCategories = new Set([
  "cap", "coat", "glove", "longcoat", "pants", "shoes", "cape", "shield",
  "onehandedweapon", "twohandedweapon", "earaccessory",
]);
const badEquipment = specificItems
  .filter((item) => item.item_type === "equip")
  .filter((item) => !validEquipSlots.has(item.slot)
    || (!/원작 아이템 \d+/.test(item.note) && !/원작 MSW 아바타 아이템/.test(item.note)))
  .map((item) => item.id);
const badAvatarCategories = items
  .filter((item) => item.item_type === "equip"
    ? !validAvatarCategories.has(item.avatar_category)
    : item.avatar_category !== "")
  .map((item) => item.id);
const heroPassive = items.find((item) => item.id === "i_hero_sword");
const heroPassiveOk = heroPassive !== undefined
  && heroPassive.name === "히어로의 검"
  && heroPassive.item_type === "passive"
  && heroPassive.slot === ""
  && heroPassive.passive_stat === "STR"
  && Number(heroPassive.passive_value) === 10
  && Number(heroPassive.stack_max) === 5
  && heroPassive.drop_from === "m_adv_hero";
const heroCombatOnlyOk = skills.filter((skill) => skill.id.startsWith("s_hero_"))
  .every((skill) => skill.source === "boss" && skill.slot_type === "enemy")
  && allMonsters.find((monster) => monster.id === "m_adv_hero")?.combat_skill_ids
    === "s_hero_01|s_hero_def|s_hero_02|s_hero_03|s_hero_04";
const bowmasterPassive = items.find((item) => item.id === "i_bowmaster_bow");
const bowmasterPassiveOk = bowmasterPassive !== undefined
  && bowmasterPassive.name === "보우마스터의 활"
  && bowmasterPassive.item_type === "passive"
  && bowmasterPassive.slot === ""
  && bowmasterPassive.passive_stat === "DEX"
  && Number(bowmasterPassive.passive_value) === 10
  && Number(bowmasterPassive.stack_max) === 5
  && bowmasterPassive.drop_from === "m_adv_bowmaster";
const bowmasterCombatOnlyOk = skills.filter((skill) => skill.id.startsWith("s_bow_"))
  .every((skill) => skill.source === "boss" && skill.slot_type === "enemy")
  && allMonsters.find((monster) => monster.id === "m_adv_bowmaster")?.combat_skill_ids
    === "s_bow_01|s_bow_02|s_bow_03|s_bow_04|s_bow_05";
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
    || skill.layer_ruids
    || skill.projectile_ruid || Number(skill.effect_value) !== 0
    || Number(skill.duration) !== 0 || Number(skill.range) !== 0
    || Number(skill.dash_distance) !== 0)
  .map((skill) => skill.id);
const activeWithoutVisual = skills
  .filter((skill) => (skill.source === "monster" || skill.source === "boss") && skill.skill_kind !== "passive")
  .filter((skill) => !skill.effect_ruid && !skill.layer_ruids && !skill.projectile_ruid)
  .map((skill) => skill.id);
const currentAreaLayerExpected = new Map([
  ["s_mon_snail", 2],
  ["s_mon_blue_snail", 2],
  ["s_mon_red_snail", 3],
  ["s_mon_mano", 3],
  ["s_mon_mushroom", 3],
  ["s_mon_mushmom", 3],
  ["s_mon_stone", 2],
  ["s_mon_axe_stump", 2],
  ["s_mon_dark_axe_stump", 2],
  ["s_mon_wild_boar", 2],
  ["s_mon_skeleton_commander", 3],
  ["s_mon_fire_boar", 2],
  ["s_mon_stumpy", 0],
  ["s_mon_slime", 2],
  ["s_mon_fairy", 2],
  ["s_mon_dark_stump", 2],
  ["s_mon_faust", 2],
  ["s_mon_octopus", 2],
  ["s_mon_jr_wraith", 2],
  ["s_mon_shade", 2],
  ["s_mon_ribbon_pig", 2],
  ["s_mon_starfish", 2],
  ["s_mon_jr_balrog", 2],
]);
const badLayerRecipes = [];
const retiredCustomEffectRuids = new Set([
  "66dcf54b85cc464281802bda30682582",
  "bb1f9e3df5a443caa1294d9fd99113cc",
  "2a60b28f01304a9888471c7031941215",
  "7985d900fb03443899423346524299a7",
  "fec296b7e8cf4ef183406057bde99edf",
  "7c0e1db74ae842e7a8993ac201f16aac",
  "fbd3aeb0e0db414c80a3274d7911692f",
  "d4685527e09f4a9ea6d7b638dadd6372",
  "192a64d82f5d477091da5c3adaf8646c",
  "89d24de320c543ef9c35f9cc8df3819d",
  "9715c20ca72843c6954c141013450db7",
  "e1177263c19345eabf79ed2eb7e17953",
  "d4e1db4566ea40a09b1225fd3f880cfc",
  "89680de9a55d406680a912ed40f388d2",
]);
const rejectedMismatchedEffectRuids = new Set([
  "b31a0bcf3c52492d8fa87f2966b6fa9d",
  "566b088cd671483f88c7a4872169a0ae",
  "4a1d12f80bd944d68367c3f84f0262fa",
  "7a488c25a3fa47ca9f14969ec4733b26",
  "3c022a4a28814662a55bcde364ee408c",
  "34cee7428d694e3a91e8a4aca8dd04ac",
  "1505be9fc1e74745ba10cb9a6fe3efbf",
  "c518100d6f3a4304adcb39141b89e454",
  "df9c5e9be1b94116b235c0e3b9fdee94",
  "e0e06d06af1746daae3555058c7dfa1e",
  "6c1613a0baf84cce8f49573a3ef55819",
  "04239429a94347fc8d7df4f37e8c35bc",
  "3448ba941413425bb8622c9c5059842f",
  "2e939c67b21b4dc39d87f4f79d09ef43",
  "c352a53aeeb74c4ea673ae18aa535fbd",
  "ea6cf9aba01943ec9ba17ed6d8bb18cd",
  "057044acf27b474f9ca6a4b6fe3f7400",
  "41505d7e27f948fb969d8c1215a27f66",
]);
const retiredCustomEffectResidue = [];
const materialSpriteRuids = new Set([
  "927d463a046b48869cffa1eeaf8e3f5a",
  "968c504c03dd404495602c46c56365c9",
  "b0c221e18dc546f0ac516895fb5704d0",
  "3eb056d03f034a29b52bfa917319d71a",
  "606b873258264a8291238074f707f5c3",
  "5d8f687d1a5143bbb51d1fb431154f30",
  "b1c0fd8c12b245958131db55e4d502e4",
  "65585470f07d4dfd829653265aba64cc",
  "2202746413d64700bb6e09b6b9a8f4e0",
  "89ff14273d9940eebe8d44b003563915",
  "186d4a28cc5344a8bcc381c80db8d426",
  "0c2847f2816d47f092f8348122008d7b",
  "3fd574fd98b248dbaee5c3d281483ece",
]);
const materialSpriteEffectResidue = [];
const rejectedMismatchedEffectResidue = [];
for (const [id, expectedCount] of currentAreaLayerExpected) {
  const skill = skillById.get(id);
  if (!skill) {
    badLayerRecipes.push(`${id}:missing`);
    continue;
  }
  const fields = [
    "layer_ruids", "layer_types", "layer_styles", "layer_delays", "layer_durations",
    "layer_scales", "layer_offsets_x", "layer_offsets_y", "layer_drifts_x", "layer_drifts_y",
  ];
  const lists = Object.fromEntries(fields.map((field) => [field, splitPipe(skill[field])]));
  if (fields.some((field) => lists[field].length !== expectedCount)) {
    badLayerRecipes.push(`${id}:length`);
    continue;
  }
  if (expectedCount === 0) continue;
  if (lists.layer_ruids.some((ruid) => !/^[0-9a-f]{32}$/.test(ruid))
    || lists.layer_types.some((type) => type !== "sprite" && type !== "animationclip")
    || lists.layer_delays.some((value) => !Number.isFinite(Number(value)) || Number(value) < 0)
    || lists.layer_durations.some((value) => !Number.isFinite(Number(value)) || Number(value) <= 0)
    || lists.layer_scales.some((value) => !Number.isFinite(Number(value)) || Number(value) <= 0)) {
    badLayerRecipes.push(`${id}:value`);
  }
  if (lists.layer_ruids.some((ruid) => retiredCustomEffectRuids.has(ruid))) {
    retiredCustomEffectResidue.push(id);
  }
  if (lists.layer_types.some((type) => type === "sprite")
    || lists.layer_ruids.some((ruid) => materialSpriteRuids.has(ruid))) {
    materialSpriteEffectResidue.push(id);
  }
  if (lists.layer_ruids.some((ruid) => rejectedMismatchedEffectRuids.has(ruid))) {
    rejectedMismatchedEffectResidue.push(id);
  }
}
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
const statUi = JSON.parse(fs.readFileSync("ui/StatGroup.ui", "utf8"));
const statEntities = statUi.ContentProto.Entities.map((entity) => {
  const json = typeof entity.jsonString === "string"
    ? JSON.parse(entity.jsonString) : entity.jsonString;
  return { id: entity.id, path: json.path };
});
const statPanelMlua = fs.readFileSync("RootDesk/MyDesk/UI/StatPanel.mlua", "utf8");
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
for (let i = 0; i < 36; i += 1) {
  const match = mlua.match(new RegExp(
    "property ButtonComponent itemRow" + i + " = \"([^\"]+)\"",
  ));
  const expectedPath = "/ui/Inventory/Window/Box/ItemRow" + i;
  bindings.push(match !== null && entities.some(
    (entity) => entity.id === match[1] && entity.path === expectedPath,
  ));
}
const inventoryCategoryPaths = {
  filterWeapon: "/ui/Inventory/Window/Box/FilterWeapon",
  filterArmor: "/ui/Inventory/Window/Box/FilterArmor",
  filterAccessory: "/ui/Inventory/Window/Box/FilterAccessory",
  filterPassive: "/ui/Inventory/Window/Box/FilterPassive",
  filterConsume: "/ui/Inventory/Window/Box/FilterConsume",
};
const inventoryCategoryBindingsOk = Object.entries(inventoryCategoryPaths).every(([property, path]) => {
  const match = mlua.match(new RegExp(
    "property ButtonComponent " + property + " = \"([^\"]+)\"",
  ));
  return match !== null && entities.some(
    (entity) => entity.id === match[1] && entity.path === path,
  );
});
const skillSourceTabsRemoved = !equipEntities.some(
  (entity) => entity.path === "/ui/EquipWindow/Window/TabMonster"
    || entity.path === "/ui/EquipWindow/Window/TabNpc",
) && !/property ButtonComponent tab(?:Monster|Npc)/.test(equipMlua);

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

const statBindingPaths = {
  windowRoot: "/ui/StatGroup/Window",
  btnClose: "/ui/StatGroup/Window/BtnClose",
  btnOpen: "/ui/StatGroup/OpenBtn",
  levelValue: "/ui/StatGroup/Window/Row0/Value",
  expValue: "/ui/StatGroup/Window/Row1/Value",
  pointsValue: "/ui/StatGroup/Window/Row2/Value",
  strValue: "/ui/StatGroup/Window/Row3/Value",
  intValue: "/ui/StatGroup/Window/Row4/Value",
  dexValue: "/ui/StatGroup/Window/Row5/Value",
  lukValue: "/ui/StatGroup/Window/Row6/Value",
  strLabel: "/ui/StatGroup/Window/Row3/Label",
  intLabel: "/ui/StatGroup/Window/Row4/Label",
  dexLabel: "/ui/StatGroup/Window/Row5/Label",
  lukLabel: "/ui/StatGroup/Window/Row6/Label",
  btnStr: "/ui/StatGroup/Window/Row3/BtnPlus",
  btnInt: "/ui/StatGroup/Window/Row4/BtnPlus",
  btnDex: "/ui/StatGroup/Window/Row5/BtnPlus",
  btnLuk: "/ui/StatGroup/Window/Row6/BtnPlus",
  btnInspectStr: "/ui/StatGroup/Window/Row3/Inspect",
  btnInspectInt: "/ui/StatGroup/Window/Row4/Inspect",
  btnInspectDex: "/ui/StatGroup/Window/Row5/Inspect",
  btnInspectLuk: "/ui/StatGroup/Window/Row6/Inspect",
  detailRoot: "/ui/StatGroup/DetailWindow",
  btnDetail: "/ui/StatGroup/Window/DetailToggle",
  detailPassive: "/ui/StatGroup/DetailWindow/Passive/Text",
};
for (const [index, key] of ["Atk", "Matk", "Def", "Hp", "AttackSpeed", "MoveSpeed", "Capture", "Drop"].entries()) {
  statBindingPaths[`detail${key}Label`] = `/ui/StatGroup/DetailWindow/Row${index}/Label`;
  statBindingPaths[`detail${key}`] = `/ui/StatGroup/DetailWindow/Row${index}/Value`;
}
const statBindingsOk = Object.entries(statBindingPaths).every(([property, path]) => {
  const match = statPanelMlua.match(new RegExp(
    "property (?:ButtonComponent|SpriteGUIRendererComponent|TextGUIRendererComponent) "
      + property + " = \\\"([^\\\"]+)\\\"",
  ));
  return match !== null && statEntities.some(
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
const inventoryIconAlphaOk = Array.from({ length: 36 }, (_, i) => {
  const path = "/ui/Inventory/Window/Box/ItemRow" + i + "/Icon";
  const sprite = readUiComponent("ui/Inventory.ui", path, "MOD.Core.SpriteGUIRendererComponent");
  const transform = readUiTransform("ui/Inventory.ui", path);
  return sprite !== null && sprite.Color.a === 1
    && transform !== null && transform.anchoredPosition.x === 0;
}).every(Boolean);
const inventoryClickTargetsOk = Array.from({ length: 36 }, (_, i) => {
  const path = "/ui/Inventory/Window/Box/ItemRow" + i;
  const button = readUiComponent("ui/Inventory.ui", path, "MOD.Core.ButtonComponent");
  const sprite = readUiComponent("ui/Inventory.ui", path, "MOD.Core.SpriteGUIRendererComponent");
  const icon = readUiComponent("ui/Inventory.ui", path + "/Icon", "MOD.Core.SpriteGUIRendererComponent");
  return button !== null && button.Enable === true
    && sprite !== null && sprite.RaycastTarget === true
    && icon !== null && icon.RaycastTarget === false;
}).every(Boolean);
const inventoryGridBackground = readUiComponent(
  "ui/Inventory.ui", "/ui/Inventory/Window/Box/ItemGridBg", "MOD.Core.SpriteGUIRendererComponent",
);
const inventoryGridDoesNotBlockClicks = inventoryGridBackground !== null
  && inventoryGridBackground.RaycastTarget === false;
const inventoryPlaceholdersEmpty = Array.from({ length: 36 }, (_, i) => {
  const path = "/ui/Inventory/Window/Box/ItemRow" + i + "/Icon";
  const sprite = readUiComponent("ui/Inventory.ui", path, "MOD.Core.SpriteGUIRendererComponent");
  return sprite !== null && sprite.ImageRUID.DataId === "";
}).every(Boolean);
const skillGrid = readUiComponent(
  "ui/EquipWindow.ui", "/ui/EquipWindow/Window/Grid", "MOD.Core.ScrollLayoutGroupComponent",
);
const skillIconAlphaOk = Array.from({ length: 30 }, (_, i) => {
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
  bowmasterPassiveOk,
  bowmasterCombatOnlyOk,
  heroPassiveWiringOk: /method number GetPassiveItemStatBonus/.test(playerStatsMlua)
    && /GetPassiveItemStatBonus\("STR"\)/.test(playerStatsMlua)
    && /GetPassiveItemBonus\("ATK"\)/.test(playerStatsMlua)
    && /record\.item_type == "passive"/.test(playerInventoryMlua)
    && /stats:ApplyMaxHp\(\)/.test(playerInventoryMlua),
  finalStatsIntegerOk: /return math\.floor\(points \+ self:GetPassiveItemStatBonus\(statName\) \+ 0\.5\)/.test(playerStatsMlua)
    && /return math\.floor\(total \+ 0\.5\)/.test(playerStatsMlua),
  collectionStackCapOk: balance.get("skill_stack_max") === 5
    && /if self:GetOwnedCount\(skillId\) >= stackMax then/.test(playerCollectionMlua)
    && /if n > stackMax then return stackMax end/.test(playerCollectionMlua)
    && /if owned > stackMax then/.test(playerDbMlua)
    && /local n = collection:GetOwnedCount\(id\)/.test(playerDbMlua),
  heroRewardSeparationOk: !/GrantNpcSkills/.test(roomMonsterMlua)
    && !/GrantNpcSkills/.test(playerCollectionMlua)
    && /GetCombatSkillIds/.test(monsterAttackMlua)
    && /skill\.source == "monster"/.test(playerDbMlua),
  badItemTypeMapping,
  badEquipment,
  badAvatarCategories,
  avatarEquipmentWiringOk: /method void RefreshAvatarEquipment/.test(playerInventoryMlua)
    && /@ExecSpace\("Client"\)\s+method void RefreshAvatarEquipmentClient/.test(playerInventoryMlua)
    && /self:RefreshAvatarEquipmentClient\(/.test(playerInventoryMlua)
    && /CostumeManagerComponent/.test(playerInventoryMlua)
    && /string\.sub\(ruid, 1, 12\) == "thumbnail:\/\/"/.test(playerInventoryMlua)
    && /inventory:RefreshAvatarEquipment\(\)/.test(playerDbMlua),
  badCorrectedPassiveEquipment,
  legacyMaterialResidue,
  passiveEffectResidue,
  activeWithoutVisual,
  currentAreaLayerCounts: Object.fromEntries(Array.from(currentAreaLayerExpected.keys()).map((id) => [
    id, splitPipe(skillById.get(id)?.layer_ruids).length,
  ])),
  badLayerRecipes,
  retiredCustomEffectResidue,
  materialSpriteEffectResidue,
  rejectedMismatchedEffectResidue,
  bossRooms: bossRooms.map((room) => room.id + ":" + room.monster_id),
  bossItemMissing,
  bossHpMultiplier: balance.get("boss_hp_multiplier"),
  bossTimeLimitSeconds: balance.get("boss_time_limit_seconds"),
  bossHudEntities: playerHudEntities.filter((entity) => entity.path.startsWith("/ui/PlayerHud/BossHud")).length,
  bossBindingsOk,
  statBindingsOk,
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
  inventoryClickTargetsOk,
  inventoryGridDoesNotBlockClicks,
  inventoryPlaceholdersEmpty,
  inventoryCategoryBindingsOk,
  inventoryCategoryFilterOk: /method boolean MatchesCategory/.test(mlua)
    && /item\.item_type == "equip" and item\.slot == self\.currentCategory/.test(mlua)
    && /self:SelectCategory\("passive"\)/.test(mlua),
  inventoryThumbnailCacheOk: /property table rowIconRuids = \{\}/.test(mlua)
    && /self\.rowIconRuids\[rowIndex\] ~= item\.icon_ruid/.test(mlua)
    && /if index == 36 then return self\.itemRow35 end/.test(mlua),
  inventoryTwoClickEquipOk: /local wasSelected = self\.selectedItemId == itemId/.test(mlua)
    && /if item\.item_type == "consume" then\s+if wasSelected == false then/.test(mlua)
    && /if item\.item_type == "passive" then[\s\S]+?return\s+end\s+\s*if wasSelected == false then\s+self:Refresh\(\)\s+return\s+end/.test(mlua)
    && /log\("\[Inventory창\] 장착 요청 " .. item\.slot/.test(mlua),
  equipCells: equipEntities.filter((entity) => /EquipWindow\/Window\/Grid\/Cell\d+$/.test(entity.path)).length,
  equipCellCountOk: /property integer cellCount = 50\b/.test(equipMlua),
  skillGridColumns: skillGrid === null ? null : skillGrid.ConstraintCount,
  skillIconAlphaOk,
  skillSourceTabsRemoved,
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

if (monsters.length !== 50 || skills.filter((skill) => skill.source === "monster").length !== 50
  || specificItems.filter((item) => item.item_type === "equip").length !== 50
  || missingSkill.length || missingItem.length || badRuid.length
  || badItemTypeMapping.length || badEquipment.length || badAvatarCategories.length
  || badCorrectedPassiveEquipment.length
  || !heroPassiveOk || !heroCombatOnlyOk || !bowmasterPassiveOk || !bowmasterCombatOnlyOk
  || !result.heroPassiveWiringOk || !result.finalStatsIntegerOk || !result.collectionStackCapOk
  || !result.heroRewardSeparationOk
  || legacyMaterialResidue.length
  || passiveEffectResidue.length || activeWithoutVisual.length || badLayerRecipes.length
  || retiredCustomEffectResidue.length || materialSpriteEffectResidue.length
  || rejectedMismatchedEffectResidue.length
  || badGateSkills.length
  || bossRooms.length !== 12 || bossItemMissing.length
  || balance.get("boss_hp_multiplier") !== 10
  || balance.get("boss_time_limit_seconds") !== 300
  || result.bossHudEntities !== 6 || !result.bossBindingsOk || !result.statBindingsOk
  || !result.bossTimerWiringOk || !result.bossGuaranteedDropWiringOk
  || topMenuWidths.some(([, width]) => width !== 112)
  || topMenuTransforms.some(([, transform, expectedRight]) => (
    transform === null || transform.anchoredPosition.x !== expectedRight
  ))
  || result.inventorySlots !== 36 || !result.bindingsOk || !result.inventoryIconAlphaOk
  || !result.inventoryClickTargetsOk || !result.inventoryGridDoesNotBlockClicks
  || !result.inventoryPlaceholdersEmpty || !result.inventoryThumbnailCacheOk
  || !result.inventoryCategoryBindingsOk || !result.inventoryCategoryFilterOk
  || !result.inventoryTwoClickEquipOk
  || !result.avatarEquipmentWiringOk
  || result.equipCells !== 50 || !result.equipCellCountOk
  || result.skillGridColumns !== 5 || !result.skillIconAlphaOk || !result.skillSourceTabsRemoved
  || !result.roomProgressDisabled || result.worldMapTop !== -150
  || result.worldMapButtons !== 12 || result.popupEntities !== 18 || !result.popupBindingsOk
  || !result.popupRewardTitleOk || !result.worldMapRewardWiringOk
  || henesysBoss.monster_id !== "m_mushmom"
  || kerningBoss.monster_id !== "m_shade"
  || bossGate.gate_type !== "key" || bossGate.gate_key !== "s_mon_mushmom"
  || gate.gate_type !== "key" || gate.gate_key !== "s_mon_shade") {
  process.exitCode = 1;
}
