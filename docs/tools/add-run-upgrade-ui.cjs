// PlayerHud에 Run 강화 현황 버튼/창을 추가한다. .ui는 UIBuilder로만 수정한다.
const fs = require("fs");
const { UIBuilder } = require("../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const file = "ui/PlayerHud.ui";
const b = UIBuilder.load(file);
const root = "/ui/PlayerHud";
const lightPanel = "21691103c9b6f174d8f0a84a5904153f";
const buttonPlate = "129f02486c2baef49a41b31ce16171f6";
const darkPlate = "5413ab8864b870941878f2c46b61b7ba";

function add(method, path, ...args) {
  if (b.find(path) === null) b[method](path, ...args);
}

add("button", `${root}/RunUpgradeButton`, "강화", {
  anchor: "top-right", pos: [-154, -145], pivot: [1, 1], rect_size: [124, 60],
  image_ruid: darkPlate, bg_color: "#5F4C20", alpha: 0.94,
  font_size: 21, color: "#FFF4C2", enable: false,
});
b.patch(`${root}/RunUpgradeButton`, {
  anchor: "top-right", pos: [-154, -145], pivot: [1, 1], rect_size: [124, 60], enable: false,
});
b.patchComponent(`${root}/RunUpgradeButton`, "MOD.Core.TextGUIRendererComponent", {
  Text: "강화", FontSize: 21,
});

add("panel", `${root}/RunUpgradeWindow`, {
  anchor: "top-right", pos: [-20, -214], pivot: [1, 1], rect_size: [470, 410],
  image_ruid: lightPanel, color: "#FAF7F1", alpha: 0.99, raycast: true, enable: false,
});
add("panel", `${root}/RunUpgradeWindow/Dialog`, {
  anchor: "stretch", pos: [0, 0], rect_size: [0, 0],
  image_ruid: lightPanel, color: "#FAF7F1", alpha: 1, raycast: true,
});
add("text", `${root}/RunUpgradeWindow/Dialog/Title`, "RUN 강화", {
  anchor: "top-center", pos: [0, -24], pivot: [0.5, 1], rect_size: [350, 48],
  size: 28, color: "#292D35", alignment: 4, raycast: false,
});
add("text", `${root}/RunUpgradeWindow/Dialog/Hint`, "이번 Run에만 적용됩니다", {
  anchor: "top-center", pos: [0, -72], pivot: [0.5, 1], rect_size: [380, 34],
  size: 17, color: "#777064", alignment: 4, raycast: false,
});
add("text", `${root}/RunUpgradeWindow/Dialog/Body`, "아직 획득한 Run 강화가 없습니다.", {
  anchor: "top-center", pos: [0, -122], pivot: [0.5, 1], rect_size: [400, 230],
  size: 20, color: "#343A43", alignment: 0, raycast: false,
});
add("button", `${root}/RunUpgradeWindow/Dialog/CloseButton`, "닫기", {
  anchor: "bottom-center", pos: [0, 26], pivot: [0.5, 0], rect_size: [180, 52],
  image_ruid: buttonPlate, bg_color: "#D8D1C5", alpha: 1,
  font_size: 21, color: "#343A43",
});

b.write(file, { strict: true, lint: true });
const crlf = fs.readFileSync(file, "utf8").replace(/\r?\n/g, "\r\n");
fs.writeFileSync(file, crlf, "utf8");
console.log("[RunUpgradeUI] PlayerHud Run 강화 버튼/창 생성 완료");
