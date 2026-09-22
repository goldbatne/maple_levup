// 로그라이트 Run 포기 UX. 플랫폼 기본 우측 상단 시스템 메뉴는 사용자 항목을
// 삽입하는 공개 API가 없어, 그 옆에 작은 RUN 메뉴 버튼을 두고 확인창을 연다.
// PlayerHud.ui는 반드시 UIBuilder로만 수정한다.
const fs = require("fs");
const { UIBuilder } = require("../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const file = "ui/PlayerHud.ui";
const b = UIBuilder.load(file);
const plate = "5413ab8864b870941878f2c46b61b7ba";

function add(method, path, ...args) {
  if (b.find(path) === null) b[method](path, ...args);
}

// 플랫폼 기본 ... 메뉴 바로 왼쪽의 작은 프로젝트 메뉴 진입점.
add("button", "/ui/PlayerHud/RunMenuButton", "RUN", {
  anchor: "top-right", pos: [-20, -145], pivot: [1, 1], rect_size: [124, 60],
  image_ruid: plate, bg_color: "#18212D", alpha: 0.9,
  font_size: 21, color: "#FFFFFF", enable: false,
});
b.patch("/ui/PlayerHud/RunMenuButton", {
  anchor: "top-right", pos: [-20, -145], pivot: [1, 1], rect_size: [124, 60], enable: false,
});
b.patchComponent("/ui/PlayerHud/RunMenuButton", "MOD.Core.TextGUIRendererComponent", {
  Text: "RUN", FontSize: 21,
});

add("panel", "/ui/PlayerHud/RunMenuPanel", {
  anchor: "top-right", pos: [-20, -214], pivot: [1, 1], rect_size: [250, 82],
  image_ruid: plate, color: "#111820", alpha: 0.96, raycast: true, enable: false,
});
b.patch("/ui/PlayerHud/RunMenuPanel", {
  anchor: "top-right", pos: [-20, -214], pivot: [1, 1], rect_size: [250, 82], enable: false,
});
add("button", "/ui/PlayerHud/RunMenuPanel/AbandonButton", "던전 나가기", {
  anchor: "middle-center", pos: [0, 0], rect_size: [226, 58],
  image_ruid: plate, bg_color: "#2A3442", alpha: 1,
  font_size: 22, color: "#FFFFFF",
});
b.patch("/ui/PlayerHud/RunMenuPanel/AbandonButton", { rect_size: [226, 58] });
b.patchComponent("/ui/PlayerHud/RunMenuPanel/AbandonButton", "MOD.Core.TextGUIRendererComponent", {
  Text: "던전 나가기", FontSize: 22,
});

// 확인 중에만 전체 화면 입력을 막는다. 닫을 때 Entity.Enable=false로 전체 트리를 끈다.
add("panel", "/ui/PlayerHud/AbandonConfirm", {
  anchor: "stretch", pos: [0, 0], rect_size: [0, 0], pivot: [0.5, 0.5],
  image_ruid: plate, color: "#000000", alpha: 0.55, raycast: true, enable: false,
});
add("panel", "/ui/PlayerHud/AbandonConfirm/Dialog", {
  anchor: "middle-center", pos: [0, 0], rect_size: [650, 310],
  image_ruid: plate, color: "#151B24", alpha: 0.99, raycast: true,
});
add("text", "/ui/PlayerHud/AbandonConfirm/Dialog/Title", "던전 나가기", {
  anchor: "top-center", pos: [0, -34], pivot: [0.5, 1], rect_size: [560, 44],
  size: 28, color: "#FFFFFF", alignment: 4, raycast: false,
});
add("text", "/ui/PlayerHud/AbandonConfirm/Dialog/Message",
  "현재 Run을 포기하고 나가시겠습니까?\n\n이번 Run에서 획득한 능력과 진행상황은 사라집니다.", {
    anchor: "middle-center", pos: [0, 18], rect_size: [570, 112],
    size: 20, color: "#D8DEE8", alignment: 4, raycast: false,
  });
add("button", "/ui/PlayerHud/AbandonConfirm/Dialog/ConfirmButton", "나가기", {
  anchor: "bottom-center", pos: [-108, 34], pivot: [0.5, 0], rect_size: [190, 54],
  image_ruid: plate, bg_color: "#B84747", alpha: 1,
  font_size: 22, color: "#FFFFFF",
});
add("button", "/ui/PlayerHud/AbandonConfirm/Dialog/CancelButton", "취소", {
  anchor: "bottom-center", pos: [108, 34], pivot: [0.5, 0], rect_size: [190, 54],
  image_ruid: plate, bg_color: "#394657", alpha: 1,
  font_size: 22, color: "#FFFFFF",
});

add("button", "/ui/PlayerHud/AbandonConfirm/Dialog/CloseButton", "×", {
  anchor: "top-right", pos: [-18, -16], pivot: [1, 1], rect_size: [52, 52],
  image_ruid: plate, bg_color: "#DED8CE", alpha: 1,
  font_size: 30, color: "#38404A",
});
b.patch("/ui/PlayerHud/AbandonConfirm/Dialog/CloseButton", { rect_size: [52, 52] });
b.patchComponent("/ui/PlayerHud/AbandonConfirm/Dialog/CloseButton", "MOD.Core.TextGUIRendererComponent", {
  Text: "×", FontSize: 30,
});

b.write(file, { strict: true, lint: true });
const crlf = fs.readFileSync(file, "utf8").replace(/\r?\n/g, "\r\n");
fs.writeFileSync(file, crlf, "utf8");
console.log("[RunAbandonUI] PlayerHud run menu and one-step confirmation rebuilt");
