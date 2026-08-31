// T53 — 보스 HUD와 겹치지 않도록 상단 스탯·스킬·가방 버튼의 폭만 줄인다.
// 가방은 기존 위치를 유지하고 스킬·스탯을 오른쪽으로 당긴다.
// 버튼끼리는 12px, 보스 HUD와 메뉴 묶음 사이는 70px 간격이다.

const { UIBuilder } = require("../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");
const fs = require("fs");

const BUTTON_WIDTH = 112;
const BUTTON_HEIGHT = 88;

const targets = [
  { file: "ui/StatGroup.ui", path: "/ui/StatGroup/OpenBtn", right: -478 },
  { file: "ui/EquipWindow.ui", path: "/ui/EquipWindow/OpenBtn", right: -354 },
  { file: "ui/Inventory.ui", path: "/ui/Inventory/OpenBtn", right: -230 },
];

for (const target of targets) {
  const b = UIBuilder.load(target.file);
  b.patchComponent(target.path, "MOD.Core.UITransformComponent", {
    AlignmentOption: 5,
    AnchorsMax: { x: 1, y: 1 },
    AnchorsMin: { x: 1, y: 1 },
    OffsetMax: { x: target.right, y: -28 },
    OffsetMin: { x: target.right - BUTTON_WIDTH, y: -116 },
    Pivot: { x: 1, y: 1 },
    RectSize: { x: BUTTON_WIDTH, y: BUTTON_HEIGHT },
    anchoredPosition: { x: target.right, y: -28 },
    Position: { x: 960 + target.right, y: 512, z: 0 },
  });
  b.write(target.file, { strict: true, lint: true, lint_verbose: true });

  // Maker가 저장한 기존 UI와 같은 CRLF를 유지한다.
  const serialized = fs.readFileSync(target.file, "utf8").replace(/\r?\n/g, "\r\n");
  fs.writeFileSync(target.file, serialized, "utf8");
}

console.log("[T53] 상단 메뉴 버튼 3개 폭 112, 우측 정렬, 버튼 간격 12");
