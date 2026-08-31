// T53 — 모든 보스방에 공통으로 쓰는 상단 HP/제한시간 HUD.
// .ui 원문은 편집하지 않고 기존 PlayerHud에 BossHud 하위 트리를 추가한다.

const { UIBuilder } = require("../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");
const fs = require("fs");

const uiPath = "ui/PlayerHud.ui";
const controllerPath = "RootDesk/MyDesk/UI/PlayerHud.mlua";
const root = "/ui/PlayerHud/BossHud";
const name = "/ui/PlayerHud/BossHudName";
const time = "/ui/PlayerHud/BossHudTime";
const bar = "/ui/PlayerHud/BossHudBar";
const fill = "/ui/PlayerHud/BossHudFill";
const hpText = "/ui/PlayerHud/BossHudHpText";
const b = UIBuilder.load(uiPath);

if (b.find(root) !== null) b.remove(root);
for (const path of [name, time, bar, fill, hpText]) {
  if (b.find(path) !== null) b.remove(path);
}

b.panel(root, {
  anchor: "top-center",
  pos: [0, -18],
  rect_size: [600, 92],
  pivot: [0.5, 1],
  image_ruid: "129f02486c2baef49a41b31ce16171f6",
  sprite_type: 1,
  bg_color: "#171820F2",
  raycast: false,
});

b.text(name, "BOSS", {
  anchor: "top-center",
  pos: [-280, -28],
  rect_size: [350, 30],
  pivot: [0, 1],
  color: "#171820",
  font_size: 23,
  horizontal_alignment: 1,
  vertical_alignment: 256,
  best_fit: true,
  min_size: 16,
  max_size: 23,
  raycast: false,
});

b.text(time, "남은 시간  05:00", {
  anchor: "top-center",
  pos: [280, -28],
  rect_size: [190, 30],
  pivot: [1, 1],
  color: "#171820",
  font_size: 21,
  horizontal_alignment: 4,
  vertical_alignment: 256,
  raycast: false,
});

b.sprite(bar, {
  anchor: "top-center",
  pos: [0, -82],
  rect_size: [560, 32],
  pivot: [0.5, 0.5],
  image_ruid: "129f02486c2baef49a41b31ce16171f6",
  sprite_type: 1,
  bg_color: "#08090D",
  raycast: false,
});

b.sprite(fill, {
  anchor: "top-center",
  pos: [-276, -82],
  rect_size: [552, 24],
  pivot: [0, 0.5],
  image_ruid: "129f02486c2baef49a41b31ce16171f6",
  sprite_type: 1,
  bg_color: "#D62839",
  raycast: false,
});

b.text(hpText, "0 / 0", {
  anchor: "top-center",
  pos: [0, -82],
  rect_size: [540, 28],
  pivot: [0.5, 0.5],
  color: "#08090D",
  font_size: 18,
  horizontal_alignment: 2,
  vertical_alignment: 512,
  raycast: false,
});

// 공통 옵션 기본값 대신 이 HUD의 실제 색·글자 크기를 네이티브 필드에 고정한다.
b.patchComponent(root, "MOD.Core.SpriteGUIRendererComponent", {
  Color: { r: 0.09, g: 0.095, b: 0.125, a: 0.95 },
});
b.patchComponent(name, "MOD.Core.TextGUIRendererComponent", {
  FontColor: { r: 1, g: 0.86, b: 0.34, a: 1 },
  FontSize: 23,
  BestFit: true,
  MinSize: 16,
  MaxSize: 23,
  HorizontalAlignment: 1,
  VerticalAlignment: 256,
});
b.patchComponent(time, "MOD.Core.TextGUIRendererComponent", {
  FontColor: { r: 1, g: 0.94, b: 0.86, a: 1 },
  FontSize: 21,
  HorizontalAlignment: 4,
  VerticalAlignment: 256,
});
b.patchComponent(bar, "MOD.Core.SpriteGUIRendererComponent", {
  Color: { r: 0.035, g: 0.04, b: 0.055, a: 1 },
});
b.patchComponent(fill, "MOD.Core.SpriteGUIRendererComponent", {
  Color: { r: 0.84, g: 0.08, b: 0.13, a: 1 },
});
b.patchComponent(hpText, "MOD.Core.TextGUIRendererComponent", {
  FontColor: { r: 1, g: 1, b: 1, a: 1 },
  FontSize: 18,
  HorizontalAlignment: 2,
  VerticalAlignment: 512,
});

b.write(uiPath, {
  strict: true,
  lint: true,
  lint_verbose: true,
  bind: {
    mlua: controllerPath,
    props: {
      bossRoot: root,
      bossBarRoot: bar,
      bossFill: fill,
      bossNameText: name,
      bossHpText: hpText,
      bossTimeText: time,
    },
  },
});

// Maker가 저장한 기존 파일의 CRLF를 유지해 새 HUD만 diff에 보이게 한다.
const serialized = fs.readFileSync(uiPath, "utf8").replace(/\r?\n/g, "\r\n");
fs.writeFileSync(uiPath, serialized, "utf8");
console.log("[T53] PlayerHud 보스 HP/제한시간 HUD 생성 및 바인딩 완료");
