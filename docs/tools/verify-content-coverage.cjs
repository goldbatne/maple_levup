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

const monsters = readCsv("RootDesk/MyDesk/GameData/MonsterTable.csv")
  .filter((monster) => monster.id !== "m_adv_hero");
const skills = readCsv("RootDesk/MyDesk/GameData/SkillTable.csv");
const items = readCsv("RootDesk/MyDesk/GameData/ItemTable.csv");
const rooms = readCsv("RootDesk/MyDesk/GameData/RoomTable.csv");
const skillIds = new Set(skills.map((skill) => skill.id));

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

function kinds(ids) {
  return ids.map((id) => {
    const skill = skills.find((one) => one.id === "s_mon_" + id);
    return skill === undefined ? "missing" : skill.skill_kind;
  });
}

const gate = rooms.find((room) => room.id === "r_05a");
const ui = JSON.parse(fs.readFileSync("ui/Inventory.ui", "utf8"));
const entities = ui.ContentProto.Entities.map((entity) => ({
  id: entity.id,
  path: (typeof entity.jsonString === "string"
    ? JSON.parse(entity.jsonString)
    : entity.jsonString).path,
}));
const mlua = fs.readFileSync("RootDesk/MyDesk/UI/InventoryPanel.mlua", "utf8");
const bindings = [];
for (let i = 0; i < 29; i += 1) {
  const match = mlua.match(new RegExp(
    "property ButtonComponent itemRow" + i + " = \"([^\"]+)\"",
  ));
  const expectedPath = "/ui/Inventory/Window/Box/ItemScroll/ItemRow" + i;
  bindings.push(match !== null && entities.some(
    (entity) => entity.id === match[1] && entity.path === expectedPath,
  ));
}

const result = {
  monsters: monsters.length,
  monsterSkills: skills.filter((skill) => skill.source === "monster").length,
  items: items.length,
  missingSkill,
  missingItem,
  badRuid,
  area04Kinds: kinds(["octopus", "stirge", "jr_wraith", "shade", "wraith"]),
  area05Kinds: kinds(["ribbon_pig", "blue_pig", "starfish", "jellyfish", "jr_balrog"]),
  nautilusGate: [gate.gate_type, gate.gate_key, gate.gate_value],
  scrollRows: entities.filter((entity) => /ItemScroll\/ItemRow\d+$/.test(entity.path)).length,
  bindingsOk: bindings.every(Boolean),
};

console.log(JSON.stringify(result, null, 2));

if (missingSkill.length || missingItem.length || badRuid.length
  || result.scrollRows !== 29 || !result.bindingsOk
  || gate.gate_type !== "key" || gate.gate_key !== "s_mon_wraith") {
  process.exitCode = 1;
}
