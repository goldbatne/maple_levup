const path = require("node:path");

const {
  MapBuilder,
} = require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const {
  ModelBuilder,
  vector2,
} = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const projectRoot = path.resolve(__dirname, "../..");
const monsterDir = path.join(projectRoot, "RootDesk/MyDesk/Models/Monsters");
const mapDir = path.join(projectRoot, "map");

function modelPath(name) {
  return path.join(monsterDir, `${name}.model`);
}

function mapPath(name) {
  return path.join(mapDir, `${name}.map`);
}

function buildMonster({
  template,
  name,
  modelId,
  monsterId,
  actions,
  spriteRuid,
  speed,
  hitbox,
  offset,
}) {
  const model = ModelBuilder.read(modelPath(template));
  model.renameModel(name, modelId);
  model.value("MOD.Core.StateAnimationComponent", "ActionSheet", actions);
  model.value("MOD.Core.SpriteRendererComponent", "SpriteRUID", spriteRuid);
  model.value("MOD.Core.MovementComponent", "InputSpeed", speed);
  model.value("MOD.Core.HitComponent", "BoxSize", vector2(hitbox[0], hitbox[1]));
  model.value("MOD.Core.HitComponent", "ColliderOffset", vector2(offset[0], offset[1]));
  model.value("script.RoomMonster", "MonsterId", monsterId);
  model.write(modelPath(name));
}

function cloneMap({ template, name, remove = [] }) {
  const map = MapBuilder.fromTemplate(mapPath(template), name);
  for (const entityName of remove) {
    map.remove(entityName);
  }
  map.write(mapPath(name));
}

function rethemeTiles(name, mapTileIndex, removeWaterBoundary = false) {
  const map = MapBuilder.read(mapPath(name));
  for (const tile of map.getTiles()) {
    tile.tileIndex = mapTileIndex(tile.tileIndex);
  }
  if (removeWaterBoundary) {
    map.removeComponent(name, "script.NautilusWaterBoundary");
  }
  map.write(mapPath(name));
}

buildMonster({
  template: "Snail",
  name: "RedSnail",
  modelId: "redsnail",
  monsterId: "m_red_snail",
  actions: {
    stand: "ffb9e9fba641457c818e9bf9d724461a",
    move: "4f8eab1a9fbf4a35b28f986c4fa12f48",
    attack: "6b6bac121ef1497f985ddf339fc6ed7d",
    hit: "a9c736c7e74544c18740d6eb36b2f103",
    die: "d5fad1d29d4d4254855d8ee1c4bda507",
    jump: "2c77fefa65b3413d8f30f402a452c5c2",
  },
  spriteRuid: "ffb9e9fba641457c818e9bf9d724461a",
  speed: 1.6,
  hitbox: [0.45, 0.36],
  offset: [0, 0.18],
});

buildMonster({
  template: "Mushmom",
  name: "Mano",
  modelId: "mano",
  monsterId: "m_mano",
  actions: {
    stand: "e035bb90c053401b88de2159dfa230eb",
    move: "3dcd0dc63d2d491b9b8d39b3b9d0a214",
    attack: "c05453dd21fd4ed581d193930ab4c331",
    hit: "452cb740ddcb4837a46b75d7935e2ffc",
    die: "f430051f6fc34f2eb56fe5e62b346eac",
  },
  spriteRuid: "e035bb90c053401b88de2159dfa230eb",
  speed: 1.0,
  hitbox: [1.05, 0.96],
  offset: [0, 0.48],
});

// Maker에서 저장·검증된 노틸러스 해안 패턴을 같은 포탈 구조끼리 복제한다.
// 타일 배열은 새로 만들거나 직접 손대지 않는다.
cloneMap({ template: "map051", name: "map001" });
cloneMap({ template: "map052", name: "map002" });
cloneMap({ template: "map053", name: "map003" });
cloneMap({
  template: "map053",
  name: "map00a",
  remove: ["Portal_E", "Portal_N", "Portal_W"],
});
cloneMap({ template: "map054", name: "map004" });
cloneMap({ template: "map055", name: "map005" });
cloneMap({ template: "map056", name: "map006" });
cloneMap({ template: "map057", name: "map007" });

// 방의 장소성에 맞춰 노틸러스 해안 패턴을 메이플 아일랜드/리스항구로
// 정리한다. 0/1은 모래 두 종류, 2는 갑판, 3은 바다다.
const sandOnly = (tileIndex) => (tileIndex === 1 ? 1 : 0);
for (const name of ["map003", "map00a", "map006"]) {
  rethemeTiles(name, sandOnly, true);
}

// 리스항구 보스방은 갑판이 아니라 해안가다. 바다는 남기고 갑판만
// 마른 모래로 바꾼다.
rethemeTiles("map005", (tileIndex) => (tileIndex === 2 ? 0 : tileIndex));
rethemeTiles("map007", (tileIndex) => (tileIndex === 2 ? 0 : tileIndex));

console.log("area_00 models and maps generated");
