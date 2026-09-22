const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const errors = [];
const check = (condition, message) => {
  if (!condition) errors.push(message);
};

function parseSimpleCsv(relative) {
  const source = read(relative).replace(/^\uFEFF/, "").trim();
  const records = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    if (char === '"') {
      if (quoted && source[index + 1] === '"') {
        field += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && source[index + 1] === "\n") index += 1;
      row.push(field);
      records.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  row.push(field);
  records.push(row);

  const header = records[0];
  return records.slice(1).map((values, index) => {
    check(values.length === header.length,
      `${relative}:${index + 2} column count ${values.length} != ${header.length}`);
    const out = {};
    header.forEach((key, column) => { out[key] = values[column] ?? ""; });
    return out;
  });
}

const monsters = parseSimpleCsv("RootDesk/MyDesk/GameData/MonsterTable.csv");
const skills = parseSimpleCsv("Mislocated/MyDesk/GameData/SkillTable.csv");
const skillById = new Map(skills.map((row) => [row.id, row]));
const tameable = monsters.filter((row) => row.drop_skill_id !== "");
const mapping = new Map();
const modelSources = new Map();
let active = 0;
let passive = 0;

function collectModels(relative) {
  const absolute = path.join(root, relative);
  if (!fs.existsSync(absolute)) return;
  for (const entry of fs.readdirSync(absolute, { withFileTypes: true })) {
    const nextRelative = path.join(relative, entry.name);
    if (entry.isDirectory()) {
      collectModels(nextRelative);
    } else if (entry.name.endsWith(".model")) {
      try {
        const text = read(nextRelative);
        const json = JSON.parse(text);
        const modelId = json?.ContentProto?.Json?.Id;
        if (modelId) modelSources.set(modelId, { relative: nextRelative, text });
      } catch (_) {
        // M2A only needs valid source models for its 101 explicit ids.
      }
    }
  }
}

for (const relative of ["RootDesk", "Global", "Mislocated"]) collectModels(relative);

for (const monster of tameable) {
  const skill = skillById.get(monster.drop_skill_id);
  check(Boolean(skill), `${monster.id}: missing skill ${monster.drop_skill_id}`);
  check(!mapping.has(monster.drop_skill_id),
    `${monster.drop_skill_id}: duplicate monster mapping (${mapping.get(monster.drop_skill_id)}, ${monster.id})`);
  mapping.set(monster.drop_skill_id, monster.id);
  check(/^[0-9a-f]{32}$/i.test(monster.collection_icon_ruid),
    `${monster.id}: invalid collection_icon_ruid`);
  check(/^[0-9a-f]{32}$/i.test(monster.companion_visual_ruid),
    `${monster.id}: invalid companion_visual_ruid`);
  const modelSource = modelSources.get(monster.model_id);
  check(Boolean(modelSource), `${monster.id}: source model ${monster.model_id} not found`);
  if (modelSource) {
    check(modelSource.text.includes(monster.collection_icon_ruid),
      `${monster.id}: collection icon RUID not found in ${modelSource.relative}`);
    check(modelSource.text.includes(monster.companion_visual_ruid),
      `${monster.id}: companion RUID not found in ${modelSource.relative}`);
  }
  if (skill) {
    if (skill.skill_kind === "passive") passive += 1;
    else active += 1;
  }
}

check(monsters.length === 103, `MonsterTable rows ${monsters.length} != 103`);
check(tameable.length === 101, `tameable rows ${tameable.length} != 101`);
check(mapping.size === 101, `unique monster-skill mappings ${mapping.size} != 101`);
check(active === 66, `active tameable ${active} != 66`);
check(passive === 35, `passive tameable ${passive} != 35`);
check(!mapping.has("s_mon_snail"), "legacy s_mon_snail must not migrate");

for (const id of ["m_adv_hero", "m_adv_bowmaster"]) {
  const row = monsters.find((monster) => monster.id === id);
  check(Boolean(row), `${id}: missing excluded boss row`);
  check(row?.drop_skill_id === "", `${id}: must not be tameable`);
}

for (const [monsterId, skillId] of [
  ["m_mushroom", "s_mon_mushroom"],
  ["m_red_snail", "s_mon_red_snail"],
  ["m_blue_snail", "s_mon_blue_snail"],
]) {
  const row = monsters.find((monster) => monster.id === monsterId);
  check(row?.drop_skill_id === skillId, `${monsterId}: prototype mapping must be ${skillId}`);
}

const permanent = read("RootDesk/MyDesk/Save/SavePermanentData.mlua");
const db = read("RootDesk/MyDesk/Save/PlayerDBManager.mlua");
const collection = read("RootDesk/MyDesk/Progress/PlayerCollection.mlua");
const slots = read("RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua");
const attack = read("RootDesk/MyDesk/PlayerAttack.mlua");

check(permanent.includes("property integer schema_version = 5"), "save schema is not v5");
check(permanent.includes("property table tamed_monsters = {}"), "missing tamed_monsters save field");
check(permanent.includes("selected_companion_monster_id"), "missing companion save field");
check(db.includes("perm.schema_version < 5 and monsterId ~= \"\""),
  "v1-v4 explicit-mapping migration guard missing");
check(collection.includes("self:SetTamedCount(monsterId, owned)"),
  "new tame path does not use SetTamedCount");
check(collection.includes("self:MirrorOwnedSkillFromTamed(monsterId)"),
  "one-way OwnedSkills mirror missing");
check(collection.includes("method integer GetAbilityStackCount(string skillId)"),
  "TamedMonsters ability stack accessor missing");
check(collection.includes("method number GetAbilityMultiplier(string skillId)"),
  "shared tame multiplier accessor missing");
check(slots.includes("collection:GetTamedCount(monsterId) > 0"),
  "random pool is not based on TamedMonsters");
check(attack.includes("collection:GetAbilityStackCount(attackInfo)"),
  "player damage does not use the common tame stack accessor");
check(attack.includes("collection:GetAbilityMultiplier(skill.id)"),
  "defense/heal effects do not use the common tame multiplier accessor");

const companionModel = JSON.parse(read("RootDesk/MyDesk/Models/Companions/CompanionVisual.model"));
const modelText = JSON.stringify(companionModel);
for (const forbidden of [
  "HitComponent", "MonsterAI", "AttackComponent", "RigidbodyComponent",
  "KinematicbodyComponent", "TriggerComponent", "ColliderComponent",
]) {
  check(!modelText.includes(forbidden), `companion model contains forbidden combat/physics component: ${forbidden}`);
}
check(modelText.includes("SpriteRendererComponent"), "companion model missing SpriteRendererComponent");
check(modelText.includes("TransformComponent"), "companion model missing TransformComponent");

const ui = JSON.parse(read("ui/EquipWindow.ui"));
let collectionCells = 0;
const visit = (value) => {
  if (Array.isArray(value)) return value.forEach(visit);
  if (!value || typeof value !== "object") return;
  const name = typeof value.name === "string" ? value.name : value.Name;
  if (typeof name === "string" && /^Cell\d+$/.test(name)) collectionCells += 1;
  Object.values(value).forEach(visit);
};
visit(ui);
check(collectionCells === 101, `EquipWindow collection cells ${collectionCells} != 101`);

if (errors.length) {
  console.error("M2A STATIC VERIFY: FAIL");
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log("M2A STATIC VERIFY: PASS");
console.log(`monsters=${monsters.length} tameable=${tameable.length} active=${active} passive=${passive}`);
console.log(`mappings=${mapping.size} legacy_snail=excluded hero_bowmaster=excluded collection_cells=${collectionCells}`);
