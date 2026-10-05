const fs = require("fs");
const { UIBuilder } = require("../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const lightPanel = "21691103c9b6f174d8f0a84a5904153f";
const flatPanel = "2860136c06ab075439721c027de365af";

function add(builder, method, path, ...args) {
  if (builder.find(path) === null) builder[method](path, ...args);
}

function writeCrlf(builder, file) {
  builder.write(file, { strict: true, lint: true });
  const source = fs.readFileSync(file, "utf8");
  fs.writeFileSync(file, source.replace(/\r?\n/g, "\r\n"), "utf8");
}

// Lobby: keep four existing buttons and match the two main actions in scale.
// Their UI roots are separate canvases, so a shared background panel would cover
// siblings in another root. Remove that panel if an earlier run added it.
{
  const file = "ui/PlayerHud.ui";
  const b = UIBuilder.load(file);
  const root = "/ui/PlayerHud";
  const dock = `${root}/LobbyMenuDock`;
  if (b.find(dock) !== null) b.remove(dock);

  b.patch(`${root}/PartyMenuButton`, {
    anchor: "top-right", pos: [-248, -210], pivot: [1, 1], rect_size: [220, 76],
  });
  for (const [name, pos, size] of [
    ["LobbyFrameBody", [14, 0], [180, 70]],
    ["LobbyFrameBadge", [-76, 0], [54, 54]],
    ["LobbyFillBody", [14, 0], [172, 62]],
    ["LobbyFillBadge", [-76, 0], [48, 48]],
    ["LobbyLabel", [18, 0], [150, 54]],
  ]) b.patch(`${root}/PartyMenuButton/${name}`, { pos, rect_size: size });
  b.patchComponent(`${root}/PartyMenuButton/LobbyLabel`, "MOD.Core.TextGUIRendererComponent", {
    FontSize: 26, FontColor: { r: 0.17, g: 0.28, b: 0.36, a: 1 },
  });
  writeCrlf(b, file);
}

{
  const file = "ui/AreaSelect.ui";
  const b = UIBuilder.load(file);
  const root = "/ui/AreaSelect/LobbyDungeonButton";
  b.patch(root, {
    anchor: "top-right", pos: [-18, -210], pivot: [1, 1], rect_size: [220, 76],
  });
  for (const [name, pos, size] of [
    ["LobbyFrameBody", [-14, 0], [180, 70]],
    ["LobbyFrameTip", [76, 0], [54, 54]],
    ["LobbyFillBody", [-14, 0], [172, 62]],
    ["LobbyFillTip", [76, 0], [48, 48]],
    ["LobbyLabel", [-18, 0], [150, 54]],
  ]) b.patch(`${root}/${name}`, { pos, rect_size: size });
  b.patchComponent(`${root}/LobbyLabel`, "MOD.Core.TextGUIRendererComponent", {
    FontSize: 26,
  });
  b.patch("/ui/AreaSelect/Window/Box/OptionsPanel/SelectedAreaText", {
    rect_size: [450, 70],
  });
  b.patchComponent("/ui/AreaSelect/Window/Box/OptionsPanel/SelectedAreaText",
    "MOD.Core.TextGUIRendererComponent", { FontSize: 20 });
  writeCrlf(b, file);
}

// Run minimap: reserve the header for floor/zone/time and one clear room-name line.
// Source badges and the boss compass text are intentionally hidden; the graph remains.
{
  const file = "ui/RoomProgress.ui";
  const b = UIBuilder.load(file);
  const root = "/ui/RoomProgress/Minimap";
  b.patch(`${root}/Title`, {
    pos: [0, 112], rect_size: [404, 54], enable: true,
  });
  b.patchComponent(`${root}/Title`, "MOD.Core.TextGUIRendererComponent", {
    Font: "Maple", FontSize: 24, BestFit: false,
    HorizontalAlignment: 2,
  });
  b.patch(`${root}/Room`, {
    pos: [0, 66], rect_size: [392, 31], enable: true,
  });
  b.patchComponent(`${root}/Room`, "MOD.Core.TextGUIRendererComponent", {
    Font: "Maple", FontSize: 20, HorizontalAlignment: 1,
  });
  b.patch(`${root}/BossHint`, { enable: false });
  for (let i = 1; i <= 4; i += 1) b.patch(`${root}/Zone${i}`, { enable: false });
  writeCrlf(b, file);
}

console.log(JSON.stringify({
  lobbyDock: "removed (canvas overlap)",
  partyAdventurePrimarySize: [220, 76],
  runMinimapTimerHeader: true,
  hidden: ["BossHint", "Zone1", "Zone2", "Zone3", "Zone4"],
}, null, 2));
