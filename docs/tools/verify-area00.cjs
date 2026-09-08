const fs = require("node:fs");
const path = require("node:path");

const {
  MapBuilder,
} = require("../../.agents/skills/msw-general/scripts/map/msw_map_builder.cjs");
const {
  ModelBuilder,
} = require("../../.agents/skills/msw-general/scripts/model/msw_model_builder.cjs");

const root = path.resolve(__dirname, "../..");
const dataDir = path.join(root, "RootDesk/MyDesk/GameData");

function rows(file) {
  const text = fs.readFileSync(path.join(dataDir, file), "utf8").replace(/^\uFEFF/, "").trim();
  const [headerLine, ...lines] = text.split(/\r?\n/);
  const headers = headerLine.split(",");
  return lines.map((line) => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, values[index] || ""]));
  });
}

function fail(message) {
  throw new Error(message);
}

const directions = {
  north: "south",
  south: "north",
  east: "west",
  west: "east",
};

const allRooms = rows("RoomTable.csv");
const roomById = new Map(allRooms.map((room) => [room.id, room]));
const areaRooms = allRooms.filter((room) => room.area_id === "area_00");
if (areaRooms.length !== 8) fail(`area_00 room count: ${areaRooms.length}`);

const expectedTileKinds = {
  map001: [0, 1, 3],
  map002: [0, 1, 3],
  map003: [0, 1],
  map00a: [0, 1],
  map004: [2, 3],
  map005: [0, 3],
  map006: [0, 1],
  map007: [0, 1, 3],
};

for (const room of areaRooms) {
  const map = MapBuilder.read(path.join(root, "map", `${room.map_name}.map`));
  const info = map.getMapInfo();
  if (info.TileMapMode !== 1) fail(`${room.map_name}: TileMapMode ${info.TileMapMode}`);
  if (info.tileCount !== 448) fail(`${room.map_name}: tile count ${info.tileCount}`);

  const tileKinds = [...new Set(map.getTiles().map((tile) => tile.tileIndex))].sort();
  if (JSON.stringify(tileKinds) !== JSON.stringify(expectedTileKinds[room.map_name])) {
    fail(`${room.map_name}: tile kinds ${tileKinds.join("/")}`);
  }
  const shouldHaveWater = tileKinds.includes(3);
  const hasWaterBoundary = Boolean(
    map.component(room.map_name, "script.NautilusWaterBoundary"),
  );
  if (shouldHaveWater !== hasWaterBoundary) {
    fail(`${room.map_name}: water boundary mismatch`);
  }

  const entityNames = new Set(map.listEntities().map((entity) => entity.name));
  for (const direction of Object.keys(directions)) {
    const targetId = room[`conn_${direction}`];
    const portalName = `Portal_${direction[0].toUpperCase()}`;
    if (Boolean(targetId) !== entityNames.has(portalName)) {
      fail(`${room.id}: ${direction} connection/portal mismatch`);
    }
    if (!targetId || !roomById.has(targetId) || roomById.get(targetId).area_id !== "area_00") continue;
    const target = roomById.get(targetId);
    const opposite = directions[direction];
    if (target[`conn_${opposite}`] !== room.id) {
      fail(`${room.id} -> ${targetId}: reverse ${opposite} mismatch`);
    }
  }

  const hasReturn = entityNames.has("Portal_Return");
  if ((room.room_type === "boss") !== hasReturn) {
    fail(`${room.id}: boss return portal mismatch`);
  }
}

for (const name of ["RedSnail", "Mano"]) {
  const model = ModelBuilder.read(path.join(root, "RootDesk/MyDesk/Models/Monsters", `${name}.model`));
  const errors = model.validate().filter((finding) => finding.severity === "error");
  if (errors.length) fail(`${name}: ${JSON.stringify(errors)}`);
}

const areas = rows("AreaTable.csv");
const areaOrder = areas.slice(0, 6).map((area) => `${area.sort_order}:${area.id}`);
const expectedOrder = ["1:area_00", "2:area_01", "3:area_03", "4:area_02", "5:area_04", "6:area_05"];
if (JSON.stringify(areaOrder) !== JSON.stringify(expectedOrder)) {
  fail(`area order mismatch: ${areaOrder.join(", ")}`);
}

const landmarks = rows("LandmarkTable.csv")
  .filter((landmark) => landmark.reward_type === "area")
  .map((landmark) => `${landmark.level}:${landmark.reward_value}`);
const expectedLandmarks = ["10:area_01", "20:area_03", "30:area_02", "40:area_04", "50:area_05"];
if (JSON.stringify(landmarks) !== JSON.stringify(expectedLandmarks)) {
  fail(`landmark mismatch: ${landmarks.join(", ")}`);
}

const sectorText = fs.readFileSync(path.join(root, "Global/SectorConfig.config"), "utf8");
const sectorMissing = areaRooms
  .map((room) => `map://${room.map_name}`)
  .filter((entry) => !sectorText.includes(`"${entry}"`));

console.log(JSON.stringify({
  areaRooms: areaRooms.length,
  maps: areaRooms.map((room) => room.map_name),
  tileMapMode: 1,
  tileCountEach: 448,
  reciprocalConnections: true,
  models: ["redsnail", "mano"],
  areaOrder,
  landmarks,
  sectorMissing,
}, null, 2));

if (sectorMissing.length) {
  console.warn("Maker Refresh 후 SectorConfig 저장이 필요합니다.");
}
