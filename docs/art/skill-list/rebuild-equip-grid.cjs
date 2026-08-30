// T52 — 몬스터 스킬 28종을 모두 포획해도 장착 창에서 잘리지 않게 한다.
// .ui 원문은 편집하지 않고 UIBuilder로 기존 스크롤 격자에 Cell21~28을 추가한다.

const { UIBuilder } = require("../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");
const fs = require("fs");

const uiPath = "ui/EquipWindow.ui";
const grid = "/ui/EquipWindow/Window/Grid";
const b = UIBuilder.load(uiPath);

for (let i = 21; i <= 28; i += 1) {
  const cell = `${grid}/Cell${i}`;
  if (b.find(cell) === null) {
    b.button(cell, "", {
      rect_size: [150, 126],
      image_ruid: "129f02486c2baef49a41b31ce16171f6",
      sprite_type: 1,
      bg_color: "#262B38",
      color: "#292E38",
      font_size: 16,
    });
  }
  if (b.find(`${cell}/Icon`) === null) {
    b.sprite(`${cell}/Icon`, {
      anchor: "top-center",
      pos: [0, -10],
      rect_size: [56, 56],
      pivot: [0.5, 1],
      image_ruid: "2860136c06ab075439721c027de365af",
      raycast: false,
    });
  }
  if (b.find(`${cell}/Name`) === null) {
    b.text(`${cell}/Name`, "", {
      anchor: "bottom-center",
      pos: [0, 8],
      rect_size: [142, 44],
      pivot: [0.5, 0],
      color: "#292E38",
      font_size: 16,
      horizontal_alignment: 2,
      vertical_alignment: 512,
      best_fit: true,
      min_size: 11,
      max_size: 16,
      raycast: false,
    });
  }

  // 빌더의 공통 옵션 기본값은 새 UI용(아이콘 반투명·텍스트 24px)이다.
  // 이 창의 기존 Cell20과 같은 렌더링 값으로 명시 패치한다.
  b.patchComponent(cell, "MOD.Core.SpriteGUIRendererComponent", {
    Color: { r: 0.15, g: 0.17, b: 0.22, a: 1 },
  });
  b.patchComponent(`${cell}/Icon`, "MOD.Core.SpriteGUIRendererComponent", {
    Color: { r: 1, g: 1, b: 1, a: 1 },
  });
  b.patchComponent(`${cell}/Name`, "MOD.Core.TextGUIRendererComponent", {
    BestFit: true,
    FontSize: 16,
    MinSize: 11,
    MaxSize: 16,
    HorizontalAlignment: 2,
    VerticalAlignment: 512,
  });
}

b.write(uiPath, { strict: true, lint: true });
// Maker가 저장한 기존 파일의 CRLF를 유지해 8칸 추가가 전 파일 재직렬화로 보이지 않게 한다.
const serialized = fs.readFileSync(uiPath, "utf8").replace(/\r?\n/g, "\r\n");
fs.writeFileSync(uiPath, serialized, "utf8");
console.log("[T52] EquipWindow 스킬 격자 28칸 생성 및 검증 완료");
