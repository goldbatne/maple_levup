// 로그라이트 공용 Player HUD 정리.
// 모든 맵에서 공유되는 PlayerHud에서 레거시 RPG 레벨/EXP 표시를 숨기고,
// 플레이어 이름과 HP만 화면 하단 중앙에 남긴다.
const fs = require("fs");
const { UIBuilder } = require("../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const file = "ui/PlayerHud.ui";
const b = UIBuilder.load(file);
const root = "/ui/PlayerHud/Info";

// 이름 40 + 간격 2 + HP 30 = 72px.
b.patch(root, {
  anchor: "bottom-center", pos: [0, 8], pivot: [0.5, 0], rect_size: [334, 72], enable: true,
});
b.patch(`${root}/info_top`, {
  anchor: "top-center", pos: [0, 0], pivot: [0.5, 1], rect_size: [334, 40], enable: true,
});
b.patch(`${root}/info_top/text_name_bg`, {
  anchor: "middle-center", pos: [0, 0], pivot: [0.5, 0.5], rect_size: [334, 40], enable: true,
});
b.patch(`${root}/info_top/text_name`, {
  anchor: "middle-center", pos: [0, 0], pivot: [0.5, 0.5], rect_size: [334, 40], enable: true,
});
b.patchComponent(`${root}/info_top/text_name`, "MOD.Core.TextGUIRendererComponent", {
  HorizontalAlignment: 2,
  VerticalAlignment: 512,
  FontSize: 22,
});

// 레벨/EXP 데이터는 레거시 저장 호환을 위해 남기되, 신규 모드 HUD에서는 렌더링하지 않는다.
b.patch(`${root}/info_top/text_level`, { enable: false });
b.patch(`${root}/info_bottom`, {
  anchor: "bottom-center", pos: [0, 0], pivot: [0.5, 0], rect_size: [334, 30], enable: true,
});
b.patch(`${root}/info_bottom/Hp`, {
  anchor: "top-center", pos: [0, 0], pivot: [0.5, 1], rect_size: [334, 30], enable: true,
});
b.patch(`${root}/info_bottom/Exp`, { enable: false });

b.write(file, { strict: true, lint: true });
const crlf = fs.readFileSync(file, "utf8").replace(/\r?\n/g, "\r\n");
fs.writeFileSync(file, crlf, "utf8");
console.log("[RoguelitePlayerHud] level/EXP hidden; centered name + HP layout applied");
