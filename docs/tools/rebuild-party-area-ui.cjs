// Mega Area 선택/Run 옵션 분리 + 로비 파티 UI + 파티 Run HUD.
// 구조화 UI는 반드시 UIBuilder를 통해 수정한다.
const fs = require("fs");
const { UIBuilder } = require("../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const lightPanel = "21691103c9b6f174d8f0a84a5904153f";
const flatPanel = "2860136c06ab075439721c027de365af";
const buttonPlate = "129f02486c2baef49a41b31ce16171f6";
const darkPlate = "5413ab8864b870941878f2c46b61b7ba";

function add(builder, method, path, ...args) {
  if (builder.find(path) === null) builder[method](path, ...args);
}

function writeCrlf(builder, file) {
  builder.write(file, { strict: true, lint: true });
  const crlf = fs.readFileSync(file, "utf8").replace(/\r?\n/g, "\r\n");
  fs.writeFileSync(file, crlf, "utf8");
}

// ---------------------------------------------------------------------------
// AreaSelect: 왼쪽 Area 5장 / 오른쪽 Run 옵션을 한 화면에서 분리한다.
// ---------------------------------------------------------------------------
{
  const file = "ui/AreaSelect.ui";
  const b = UIBuilder.load(file);
  const box = "/ui/AreaSelect/Window/Box";
  const list = `${box}/List`;

  b.patch(box, { anchor: "middle-center", pos: [0, 0], rect_size: [1160, 720] });
  b.patch(`${box}/Title`, {
    anchor: "top-center", pos: [0, -8], pivot: [0.5, 1], rect_size: [1120, 82],
  });
  b.patchComponent(`${box}/Title`, "MOD.Core.TextGUIRendererComponent", {
    Text: "MEGA AREA RUN", FontSize: 38,
  });

  add(b, "text", `${box}/AreaHeader`, "AREA 선택", {
    anchor: "top-center", pos: [-300, -92], pivot: [0.5, 1], rect_size: [500, 44],
    size: 25, color: "#29313C", alignment: 4, raycast: false,
  });
  add(b, "text", `${box}/OptionsHeader`, "RUN 옵션", {
    anchor: "top-center", pos: [300, -92], pivot: [0.5, 1], rect_size: [500, 44],
    size: 25, color: "#29313C", alignment: 4, raycast: false,
  });

  b.patch(list, {
    anchor: "top-center", pos: [-300, -140], pivot: [0.5, 1], rect_size: [500, 470],
  });
  b.patchComponent(list, "MOD.Core.ScrollLayoutGroupComponent", {
    CellSize: { x: 460, y: 76 },
    GridSpacing: { x: 0, y: 10 },
    Padding: { left: 14, right: 14, top: 14, bottom: 14 },
    ScrollBarVisible: 0,
    UseScroll: false,
  });
  for (let i = 1; i <= 20; i++) {
    const p = `${list}/Slot${i}`;
    b.patch(p, { rect_size: [460, 76] });
    b.patchComponent(p, "MOD.Core.TextGUIRendererComponent", { FontSize: 25 });
  }

  add(b, "panel", `${box}/OptionsPanel`, {
    anchor: "top-center", pos: [300, -140], pivot: [0.5, 1], rect_size: [500, 470],
    image_ruid: flatPanel, color: "#ECE8E1", alpha: 1, raycast: false,
  });
  add(b, "text", `${box}/OptionsPanel/SelectedAreaText`, "선택 Area  ·  MEGA 1", {
    anchor: "top-center", pos: [0, -20], pivot: [0.5, 1], rect_size: [450, 42],
    size: 23, color: "#28313D", alignment: 4, raycast: false,
  });
  add(b, "text", `${box}/OptionsPanel/ModeLabel`, "전투 모드", {
    anchor: "top-left", pos: [24, -78], pivot: [0, 1], rect_size: [180, 34],
    size: 21, color: "#4A5564", alignment: 3, raycast: false,
  });
  add(b, "button", `${box}/OptionsPanel/NormalButton`, "NORMAL\n기본 공격 중심", {
    anchor: "top-center", pos: [-116, -120], pivot: [0.5, 1], rect_size: [214, 84],
    image_ruid: buttonPlate, bg_color: "#D7E7D2", alpha: 1,
    font_size: 19, color: "#243027",
  });
  add(b, "button", `${box}/OptionsPanel/MonsterSkillButton`, "MONSTER SKILL\n몬스터 고유 스킬 사용", {
    anchor: "top-center", pos: [116, -120], pivot: [0.5, 1], rect_size: [214, 84],
    image_ruid: buttonPlate, bg_color: "#E1DDD5", alpha: 1,
    font_size: 18, color: "#343B45",
  });
  add(b, "text", `${box}/OptionsPanel/PartySummaryText`, "파티  ·  SOLO", {
    anchor: "top-left", pos: [24, -226], pivot: [0, 1], rect_size: [452, 74],
    size: 21, color: "#303946", alignment: 3, raycast: false,
  });
  add(b, "text", `${box}/OptionsPanel/RoleHintText`, "Solo는 바로 시작할 수 있습니다.", {
    anchor: "top-left", pos: [24, -302], pivot: [0, 1], rect_size: [452, 54],
    size: 17, color: "#67717F", alignment: 3, raycast: false,
  });
  add(b, "button", `${box}/OptionsPanel/ReadyButton`, "준비", {
    anchor: "bottom-center", pos: [-114, 26], pivot: [0.5, 0], rect_size: [214, 64],
    image_ruid: buttonPlate, bg_color: "#DBD5C9", alpha: 1,
    font_size: 23, color: "#2F3742", enable: false,
  });
  add(b, "button", `${box}/OptionsPanel/StartButton`, "RUN 시작", {
    anchor: "bottom-center", pos: [114, 26], pivot: [0.5, 0], rect_size: [214, 64],
    image_ruid: buttonPlate, bg_color: "#CFE3C8", alpha: 1,
    font_size: 23, color: "#263329",
  });

  b.patch(`${box}/BtnClose`, {
    anchor: "bottom-center", pos: [0, 24], pivot: [0.5, 0], rect_size: [240, 66],
  });
  b.patchComponent(`${box}/BtnClose`, "MOD.Core.TextGUIRendererComponent", { Text: "닫기", FontSize: 24 });
  writeCrlf(b, file);
}

// ---------------------------------------------------------------------------
// PlayerHud: RUN/파티 진입점, 파티 관리창, 협동 Run 소형 HUD, 던전 나가기 정돈.
// ---------------------------------------------------------------------------
{
  const file = "ui/PlayerHud.ui";
  const b = UIBuilder.load(file);
  const root = "/ui/PlayerHud";

  // 전역 PlayerHud 이름은 엔진 기본 객체와 충돌할 수 있다. 로그라이트용 입력/UI는
  // 별도 Client Component를 UI 루트에 붙여 생성·정리 수명을 명확히 한다.
  if (JSON.stringify(b.find(root)).includes('"@type":"script.PlayerHud"')) {
    b.removeComponent(root, "script.PlayerHud");
  }
  if (JSON.stringify(b.find(root)).includes('"@type":"script.RogueHudController"')) {
    b.removeComponent(root, "script.RogueHudController");
  }

  // 플랫폼 기본 UI를 가리지 않도록 두 프로젝트 버튼을 나란히 배치한다.
  b.patch(`${root}/RunMenuButton`, {
    anchor: "top-right", pos: [-20, -145], pivot: [1, 1], rect_size: [124, 60], enable: false,
  });
  b.patchComponent(`${root}/RunMenuButton`, "MOD.Core.TextGUIRendererComponent", { Text: "RUN", FontSize: 21 });
  b.patch(`${root}/RunMenuPanel`, {
    anchor: "top-right", pos: [-20, -214], pivot: [1, 1], rect_size: [250, 82], enable: false,
  });
  b.patchComponent(`${root}/RunMenuPanel`, "MOD.Core.SpriteGUIRendererComponent", {
    ImageRUID: { DataId: lightPanel }, Color: { r: 0.98, g: 0.97, b: 0.95, a: 1 },
  });
  b.patchComponent(`${root}/RunMenuPanel/AbandonButton`, "MOD.Core.TextGUIRendererComponent", {
    Text: "던전 나가기", FontSize: 22, FontColor: { r: 0.31, g: 0.16, b: 0.16, a: 1 },
  });
  b.patch(`${root}/RunMenuPanel/AbandonButton`, { rect_size: [226, 58] });
  b.patchComponent(`${root}/RunMenuPanel/AbandonButton`, "MOD.Core.SpriteGUIRendererComponent", {
    ImageRUID: { DataId: buttonPlate }, Color: { r: 0.93, g: 0.85, b: 0.82, a: 1 },
  });

  // 던전 나가기 확인창을 기존 밝은 창 계열로 통일한다.
  b.patch(`${root}/AbandonConfirm/Dialog`, { rect_size: [650, 320] });
  b.patchComponent(`${root}/AbandonConfirm/Dialog`, "MOD.Core.SpriteGUIRendererComponent", {
    ImageRUID: { DataId: lightPanel }, Color: { r: 0.98, g: 0.97, b: 0.95, a: 1 },
  });
  b.patchComponent(`${root}/AbandonConfirm/Dialog/Title`, "MOD.Core.TextGUIRendererComponent", {
    Text: "던전 나가기", FontColor: { r: 0.16, g: 0.18, b: 0.22, a: 1 }, FontSize: 28,
  });
  b.patchComponent(`${root}/AbandonConfirm/Dialog/Message`, "MOD.Core.TextGUIRendererComponent", {
    Text: "현재 Run을 포기하고 나가시겠습니까?\n\n이번 Run에서 획득한 능력과 진행상황은 사라집니다.",
    FontColor: { r: 0.25, g: 0.28, b: 0.33, a: 1 }, FontSize: 20,
  });
  b.patchComponent(`${root}/AbandonConfirm/Dialog/ConfirmButton`, "MOD.Core.SpriteGUIRendererComponent", {
    ImageRUID: { DataId: buttonPlate }, Color: { r: 0.75, g: 0.31, b: 0.29, a: 1 },
  });
  b.patchComponent(`${root}/AbandonConfirm/Dialog/CancelButton`, "MOD.Core.SpriteGUIRendererComponent", {
    ImageRUID: { DataId: buttonPlate }, Color: { r: 0.78, g: 0.79, b: 0.80, a: 1 },
  });
  add(b, "button", `${root}/AbandonConfirm/Dialog/CloseButton`, "×", {
    anchor: "top-right", pos: [-18, -16], pivot: [1, 1], rect_size: [52, 52],
    image_ruid: buttonPlate, bg_color: "#DED8CE", alpha: 1,
    font_size: 30, color: "#38404A",
  });
  b.patch(`${root}/AbandonConfirm/Dialog/CloseButton`, { rect_size: [52, 52] });
  b.patchComponent(`${root}/AbandonConfirm/Dialog/CloseButton`, "MOD.Core.TextGUIRendererComponent", {
    Text: "×", FontSize: 30,
  });

  add(b, "button", `${root}/PartyMenuButton`, "파티", {
    anchor: "top-right", pos: [-20, -145], pivot: [1, 1], rect_size: [124, 60],
    image_ruid: darkPlate, bg_color: "#18212D", alpha: 0.9,
    font_size: 21, color: "#FFFFFF",
  });
  b.patch(`${root}/PartyMenuButton`, {
    anchor: "top-right", pos: [-20, -145], pivot: [1, 1], rect_size: [124, 60],
  });
  b.patchComponent(`${root}/PartyMenuButton`, "MOD.Core.TextGUIRendererComponent", {
    Text: "파티", FontSize: 21,
  });

  add(b, "panel", `${root}/PartyWindow`, {
    anchor: "stretch", pos: [0, 0], rect_size: [0, 0], pivot: [0.5, 0.5],
    image_ruid: flatPanel, color: "#000000", alpha: 0.48, raycast: true, enable: false,
  });
  add(b, "panel", `${root}/PartyWindow/Dialog`, {
    anchor: "middle-center", pos: [0, 0], rect_size: [720, 620],
    image_ruid: lightPanel, color: "#FAF7F1", alpha: 1, raycast: true,
  });
  add(b, "text", `${root}/PartyWindow/Dialog/Title`, "PARTY", {
    anchor: "top-center", pos: [0, -24], pivot: [0.5, 1], rect_size: [580, 50],
    size: 31, color: "#242C36", alignment: 4, raycast: false,
  });
  add(b, "button", `${root}/PartyWindow/Dialog/CloseButton`, "×", {
    anchor: "top-right", pos: [-22, -20], pivot: [1, 1], rect_size: [52, 52],
    image_ruid: buttonPlate, bg_color: "#DED8CE", alpha: 1,
    font_size: 30, color: "#38404A",
  });
  b.patch(`${root}/PartyWindow/Dialog/CloseButton`, { rect_size: [52, 52] });
  b.patchComponent(`${root}/PartyWindow/Dialog/CloseButton`, "MOD.Core.TextGUIRendererComponent", {
    Text: "×", FontSize: 30,
  });
  add(b, "text", `${root}/PartyWindow/Dialog/StatusText`, "현재 SOLO 상태입니다.", {
    anchor: "top-center", pos: [0, -88], pivot: [0.5, 1], rect_size: [620, 50],
    size: 21, color: "#495464", alignment: 4, raycast: false,
  });

  add(b, "panel", `${root}/PartyWindow/Dialog/NoPartyPanel`, {
    anchor: "top-center", pos: [0, -152], pivot: [0.5, 1], rect_size: [620, 360],
    image_ruid: flatPanel, color: "#EEEAE2", alpha: 1, raycast: false,
  });
  add(b, "text", `${root}/PartyWindow/Dialog/NoPartyPanel/Guide`,
    "파티는 2~4인이 같은 Run에 입장합니다.\n가까운 플레이어가 자동 합류하지 않습니다.", {
      anchor: "top-center", pos: [0, -24], pivot: [0.5, 1], rect_size: [560, 72],
      size: 19, color: "#596270", alignment: 4, raycast: false,
    });
  add(b, "button", `${root}/PartyWindow/Dialog/NoPartyPanel/CreateButton`, "파티 만들기", {
    anchor: "top-center", pos: [0, -114], pivot: [0.5, 1], rect_size: [280, 70],
    image_ruid: buttonPlate, bg_color: "#CFE3C8", alpha: 1,
    font_size: 24, color: "#263329",
  });
  b.patch(`${root}/PartyWindow/Dialog/NoPartyPanel/CreateButton`, {
    pos: [0, -114], rect_size: [280, 70],
  });
  b.patchComponent(`${root}/PartyWindow/Dialog/NoPartyPanel/CreateButton`, "MOD.Core.TextGUIRendererComponent", {
    Text: "파티 만들기", FontSize: 24,
  });
  add(b, "text", `${root}/PartyWindow/Dialog/NoPartyPanel/JoinLabel`, "참가 코드", {
    anchor: "top-left", pos: [56, -222], pivot: [0, 1], rect_size: [120, 36],
    size: 19, color: "#4D5664", alignment: 3, raycast: false,
  });
  add(b, "textInput", `${root}/PartyWindow/Dialog/NoPartyPanel/JoinCodeInput`, {
    anchor: "top-left", pos: [164, -208], pivot: [0, 1], rect_size: [238, 64],
    image_ruid: flatPanel, color: "#FFFFFF", alpha: 1,
    font_size: 23, text_color: "#28313C", placeholder: "6자리 코드",
    character_limit: 6, line_type: 0,
  });
  b.patch(`${root}/PartyWindow/Dialog/NoPartyPanel/JoinCodeInput`, {
    pos: [164, -208], rect_size: [238, 64],
  });
  add(b, "button", `${root}/PartyWindow/Dialog/NoPartyPanel/JoinButton`, "참가", {
    anchor: "top-right", pos: [-42, -208], pivot: [1, 1], rect_size: [148, 64],
    image_ruid: buttonPlate, bg_color: "#D6E0EA", alpha: 1,
    font_size: 23, color: "#2C3947",
  });
  b.patch(`${root}/PartyWindow/Dialog/NoPartyPanel/JoinButton`, {
    pos: [-42, -208], rect_size: [148, 64],
  });
  b.patchComponent(`${root}/PartyWindow/Dialog/NoPartyPanel/JoinButton`, "MOD.Core.TextGUIRendererComponent", {
    Text: "참가", FontSize: 23,
  });

  add(b, "panel", `${root}/PartyWindow/Dialog/InPartyPanel`, {
    anchor: "top-center", pos: [0, -140], pivot: [0.5, 1], rect_size: [620, 402],
    image_ruid: flatPanel, color: "#EEEAE2", alpha: 1, raycast: false, enable: false,
  });
  add(b, "text", `${root}/PartyWindow/Dialog/InPartyPanel/PartyCodeText`, "참가 코드  ------", {
    anchor: "top-center", pos: [0, -18], pivot: [0.5, 1], rect_size: [560, 40],
    size: 21, color: "#303946", alignment: 4, raycast: false,
  });
  add(b, "text", `${root}/PartyWindow/Dialog/InPartyPanel/MembersTitle`, "파티원", {
    anchor: "top-left", pos: [32, -72], pivot: [0, 1], rect_size: [180, 32],
    size: 19, color: "#596270", alignment: 3, raycast: false,
  });
  for (let i = 1; i <= 4; i++) {
    add(b, "text", `${root}/PartyWindow/Dialog/InPartyPanel/Member${i}`, `${i}. 빈 자리`, {
      anchor: "top-left", pos: [42, -108 - (i - 1) * 48], pivot: [0, 1], rect_size: [536, 40],
      size: 20, color: "#303946", alignment: 3, raycast: false,
    });
  }
  add(b, "button", `${root}/PartyWindow/Dialog/InPartyPanel/ReadyButton`, "준비", {
    anchor: "bottom-center", pos: [-192, 20], pivot: [0.5, 0], rect_size: [178, 64],
    image_ruid: buttonPlate, bg_color: "#D6E0EA", alpha: 1,
    font_size: 22, color: "#2C3947",
  });
  b.patch(`${root}/PartyWindow/Dialog/InPartyPanel/ReadyButton`, {
    pos: [-192, 20], rect_size: [178, 64],
  });
  add(b, "button", `${root}/PartyWindow/Dialog/InPartyPanel/LeaveButton`, "파티 나가기", {
    anchor: "bottom-center", pos: [0, 20], pivot: [0.5, 0], rect_size: [178, 64],
    image_ruid: buttonPlate, bg_color: "#E4D9CD", alpha: 1,
    font_size: 20, color: "#4B342A",
  });
  b.patch(`${root}/PartyWindow/Dialog/InPartyPanel/LeaveButton`, {
    pos: [0, 20], rect_size: [178, 64],
  });
  add(b, "button", `${root}/PartyWindow/Dialog/InPartyPanel/DisbandButton`, "파티 해체", {
    anchor: "bottom-center", pos: [192, 20], pivot: [0.5, 0], rect_size: [178, 64],
    image_ruid: buttonPlate, bg_color: "#E5C9C7", alpha: 1,
    font_size: 20, color: "#542D2D",
  });
  b.patch(`${root}/PartyWindow/Dialog/InPartyPanel/DisbandButton`, {
    pos: [192, 20], rect_size: [178, 64],
  });

  add(b, "panel", `${root}/PartyRunHud`, {
    anchor: "top-left", pos: [24, -190], pivot: [0, 1], rect_size: [310, 190],
    image_ruid: darkPlate, color: "#18212D", alpha: 0.84, raycast: false, enable: false,
  });
  add(b, "text", `${root}/PartyRunHud/Title`, "PARTY", {
    anchor: "top-left", pos: [16, -12], pivot: [0, 1], rect_size: [278, 30],
    size: 18, color: "#FFFFFF", alignment: 3, raycast: false,
  });
  for (let i = 1; i <= 4; i++) {
    add(b, "text", `${root}/PartyRunHud/Member${i}`, "", {
      anchor: "top-left", pos: [18, -48 - (i - 1) * 34], pivot: [0, 1], rect_size: [274, 30],
      size: 17, color: "#E7ECF2", alignment: 3, raycast: false,
    });
  }

  writeCrlf(b, file);
}

console.log("[PartyAreaUI] AreaSelect, Party window/HUD, Run abandon visuals rebuilt");
