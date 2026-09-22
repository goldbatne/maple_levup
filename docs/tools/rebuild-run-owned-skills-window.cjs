// 로그라이트 전투 HUD의 상시 OwnedPool을 제거하고, 기존 EquipWindow를
// "이번 Run 보유 능력" 읽기 전용 창으로 재사용한다. UI 원문은 직접 편집하지 않는다.

const { UIBuilder } = require("../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");
const fs = require("fs");

function keepCrlf(file) {
  const serialized = fs.readFileSync(file, "utf8").replace(/\r?\n/g, "\r\n");
  fs.writeFileSync(file, serialized, "utf8");
}

const skillBarPath = "ui/SkillBar.ui";
const skillBar = UIBuilder.load(skillBarPath);
if (skillBar.find("/ui/SkillBar/OwnedPool") !== null) {
  skillBar.remove("/ui/SkillBar/OwnedPool");
}
skillBar.write(skillBarPath, { strict: true, lint: true });
keepCrlf(skillBarPath);

const equipPath = "ui/EquipWindow.ui";
const equip = UIBuilder.load(equipPath);

// 창 바깥의 투명 전체 화면 루트가 닫힌 뒤 입력을 가로채지 않게 한다.
// 실제 버튼/창 Sprite의 RaycastTarget은 그대로이므로 열린 창의 조작은 유지된다.
equip.patchComponent("/ui/EquipWindow", "MOD.Core.CanvasGroupComponent", {
  BlocksRaycasts: true,
});

// 상세 설명 왼쪽에 실제 스킬 아이콘과 해당 몬스터 썸네일을 나란히 표시한다.
for (const [name, x] of [["DetailSkillIcon", 42], ["DetailMonsterIcon", 112]]) {
  const path = `/ui/EquipWindow/Window/${name}`;
  if (equip.find(path) === null) {
    equip.sprite(path, {
      anchor: "top-left",
      pos: [x, -850],
      rect_size: [58, 58],
      pivot: [0, 1],
      image_ruid: "",
      raycast: false,
      color: "#FFFFFF",
      alpha: 1,
      enable: false,
    });
  }
  equip.patchComponent(path, "MOD.Core.SpriteGUIRendererComponent", {
    RaycastTarget: false,
    Color: { r: 1, g: 1, b: 1, a: 1 },
  });
}

const empty = "/ui/EquipWindow/Window/EmptyState";
if (equip.find(empty) === null) {
  equip.text(empty, "아직 획득한 능력이 없습니다.", {
    anchor: "top-center",
    pos: [0, -550],
    rect_size: [580, 64],
    pivot: [0.5, 1],
    size: 24,
    color: "#707782",
    alignment: 2,
    raycast: false,
    enable: false,
  });
}

equip.patchComponent("/ui/EquipWindow/Window/LblDesc", "MOD.Core.TextGUIRendererComponent", {
  HorizontalAlignment: 1,
  Padding: { left: 164, right: 12, top: 0, bottom: 0 },
});

equip.write(equipPath, { strict: true, lint: true });
keepCrlf(equipPath);

console.log("[RunOwnedSkillsUI] OwnedPool removed; read-only Run skill window rebuilt and linted");
