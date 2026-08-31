// T54 — 상시 획득 HUD를 월드맵 클릭 정보로 옮기고,
// 가방/스킬 창을 메이플스토리식 슬롯 중심 구조로 맞춘다.
// 구조화 UI는 원문 JSON을 직접 수정하지 않고 UIBuilder로만 쓴다.

const { UIBuilder } = require("../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const FRAME_RUID = "2860136c06ab075439721c027de365af";
const SLOT_RUID = "129f02486c2baef49a41b31ce16171f6";
const EMPTY_ICON_RUID = "234aca1a4ce946119b68e3717991e775";

function rebuildWorldMap() {
  const uiPath = "ui/WorldMap.ui";
  const controllerPath = "RootDesk/MyDesk/UI/WorldMapPanel.mlua";
  const b = UIBuilder.load(uiPath);
  const panel = "/ui/WorldMap/Panel";
  const board = panel + "/Board";
  const popup = "/ui/WorldMap/RoomInfoPopup";

  // 없어진 획득 현황 창의 자리로 지도를 올린다.
  b.patch(panel, { anchor: "top-right", pos: [-24, -150], rect_size: [440, 370], pivot: [1, 1] });

  // 지도 방 칸 자체를 클릭 대상으로 만든다. 그림은 기존 것을 보존한다.
  for (let i = 1; i <= 12; i += 1) {
    const cell = `${board}/Cell${i}`;
    if (!b.hasComponent(cell, "MOD.Core.ButtonComponent")) {
      b.addComponent(cell, "MOD.Core.ButtonComponent", UIBuilder._buttonComponent());
    }
    b.patchComponent(cell, "MOD.Core.SpriteGUIRendererComponent", { RaycastTarget: true });
  }

  const itemBindings = {};
  if (b.find(popup) === null) {
    b.panel(popup, {
    anchor: "middle-center",
    pos: [0, 0],
    rect_size: [620, 520],
    pivot: [0.5, 0.5],
    image_ruid: FRAME_RUID,
    sprite_type: 1,
    color: "#F4F2EE",
    alpha: 0.98,
    raycast: true,
    enable: false,
    });
    b.text(popup + "/Title", "방 정보", {
    anchor: "top-center", pos: [0, -28], rect_size: [470, 54], pivot: [0.5, 1],
    size: 28, color: "#292E38", bold: true, best_fit: true, min_size: 18, max_size: 28,
    });
    b.button(popup + "/Close", "X", {
    anchor: "top-right", pos: [-20, -18], rect_size: [56, 56], pivot: [1, 1],
    image_ruid: SLOT_RUID, sprite_type: 1, bg_color: "#D8D3CB", color: "#292E38", font_size: 24,
    });
    b.panel(popup + "/MonsterCard", {
    anchor: "top-center", pos: [0, -96], rect_size: [548, 92], pivot: [0.5, 1],
    image_ruid: SLOT_RUID, sprite_type: 1, color: "#DCE8F5", alpha: 1,
    });
    b.text(popup + "/MonsterCard/Monster", "몬스터", {
    anchor: "middle-center", pos: [0, 0], rect_size: [510, 62], pivot: [0.5, 0.5],
    size: 24, color: "#292E38", bold: true, best_fit: true, min_size: 16, max_size: 24,
    });
    b.text(popup + "/DropLabel", "획득 가능한 아이템", {
    anchor: "top-left", pos: [38, -204], rect_size: [360, 42], pivot: [0, 1],
    size: 20, color: "#4D5667", bold: true,
    });

    for (let i = 1; i <= 4; i += 1) {
      const row = `${popup}/Drop${i}`;
      b.panel(row, {
      anchor: "top-center", pos: [0, -246 - (i - 1) * 66], rect_size: [548, 58], pivot: [0.5, 1],
      image_ruid: SLOT_RUID, sprite_type: 1, color: i % 2 === 1 ? "#E9E6E1" : "#F0EEEA", alpha: 1,
      });
      b.sprite(row + "/Icon", {
      anchor: "middle-left", pos: [14, 0], rect_size: [46, 46], pivot: [0, 0.5],
      image_ruid: EMPTY_ICON_RUID, preserve_aspect: false, raycast: false,
      });
      b.text(row + "/Text", "아이템", {
      anchor: "middle-left", pos: [76, 0], rect_size: [450, 46], pivot: [0, 0.5],
      size: 18, color: "#292E38", best_fit: true, min_size: 13, max_size: 18,
      });
    }
  }
  for (let i = 1; i <= 4; i += 1) {
    const row = `${popup}/Drop${i}`;
    itemBindings[`popupDrop${i}`] = row + "/Text";
    itemBindings[`popupIcon${i}`] = row + "/Icon";
  }

  b.write(uiPath, {
    strict: true,
    lint: true,
    bind: {
      mlua: controllerPath,
      props: {
        panel,
        board,
        titleText: panel + "/Title",
        popup,
        popupClose: popup + "/Close",
        popupTitle: popup + "/Title",
        popupMonster: popup + "/MonsterCard/Monster",
        popupRow1: popup + "/Drop1",
        popupRow2: popup + "/Drop2",
        popupRow3: popup + "/Drop3",
        popupRow4: popup + "/Drop4",
        ...itemBindings,
      },
    },
  });
}

function rebuildInventory() {
  const uiPath = "ui/Inventory.ui";
  const controllerPath = "RootDesk/MyDesk/UI/InventoryPanel.mlua";
  const b = UIBuilder.load(uiPath);
  const box = "/ui/Inventory/Window/Box";
  const oldGrid = box + "/ItemScroll";
  const gridBg = box + "/ItemGridBg";

  // 착용 장비는 위쪽 3칸으로 모은다.
  b.patch(box + "/EquipLabel", { anchor: "top-center", pos: [0, -112], rect_size: [648, 34], pivot: [0.5, 1] });
  for (let i = 0; i < 3; i += 1) {
    const row = `${box}/EquipRow${i}`;
    b.patch(row, { anchor: "top-center", pos: [-216 + i * 216, -158], rect_size: [202, 104], pivot: [0.5, 1] });
    b.patchComponent(row, "MOD.Core.TextGUIRendererComponent", {
      FontSize: 15, BestFit: true, MinSize: 11, MaxSize: 15,
    });
    b.patch(row + "/Icon", { anchor: "middle-left", pos: [12, 0], rect_size: [54, 54], pivot: [0, 0.5] });
    b.patchComponent(row + "/Icon", "MOD.Core.SpriteGUIRendererComponent", {
      PreserveSprite: 0, Color: { r: 1, g: 1, b: 1, a: 1 },
    });
    if (b.find(row + "/Name") === null) {
      b.text(row + "/Name", "", {
        anchor: "middle-left", pos: [76, 0], rect_size: [114, 78], pivot: [0, 0.5],
        size: 14, color: "#292E38", best_fit: true, min_size: 10, max_size: 14,
      });
    }
  }
  b.patch(box + "/BagLabel", { anchor: "top-center", pos: [0, -276], rect_size: [648, 34], pivot: [0.5, 1] });

  if (b.find(oldGrid) !== null) b.remove(oldGrid);
  if (b.find(gridBg) === null) {
    b.panel(gridBg, {
      anchor: "top-center", pos: [0, -316], rect_size: [648, 456], pivot: [0.5, 1],
      image_ruid: FRAME_RUID, sprite_type: 1, color: "#F4F2EE", alpha: 1,
    });
  }

  const bindings = {};
  const cols = 6;
  for (let i = 0; i < 29; i += 1) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const cell = `${box}/ItemRow${i}`;
    if (b.find(cell) === null) {
      b.button(cell, "", {
      anchor: "top-center",
      pos: [-250 + col * 100, -324 - row * 88],
      rect_size: [88, 80],
      pivot: [0.5, 1],
      image_ruid: SLOT_RUID,
      sprite_type: 1,
      bg_color: "#E9E6E1",
      color: "#292E38",
      font_size: 13,
      });
      b.sprite(cell + "/Icon", {
        anchor: "middle-center", pos: [0, -2], rect_size: [62, 62], pivot: [0.5, 0.5],
        image_ruid: EMPTY_ICON_RUID, preserve_aspect: false, raycast: false,
        color: "#FFFFFF", alpha: 1,
      });
      b.text(cell + "/Count", "", {
      anchor: "bottom-right", pos: [-4, 3], rect_size: [54, 24], pivot: [1, 0],
      size: 15, color: "#FFFFFF", bold: true, outline: true, outline_color: "#252932", outline_width: 2,
      best_fit: true, min_size: 11, max_size: 15,
      });
    }
    b.patchComponent(cell + "/Icon", "MOD.Core.SpriteGUIRendererComponent", {
      PreserveSprite: 0,
      Color: { r: 1, g: 1, b: 1, a: 1 },
    });
    bindings[`itemRow${i}`] = cell;
  }

  const detail = box + "/ItemDetail";
  if (b.find(detail) === null) {
    b.panel(detail, {
    anchor: "top-center", pos: [0, -786], rect_size: [648, 132], pivot: [0.5, 1],
    image_ruid: SLOT_RUID, sprite_type: 1, color: "#EEEAE4", alpha: 1,
    });
    b.text(detail + "/Title", "아이템을 선택해 주세요", {
    anchor: "top-left", pos: [18, -12], rect_size: [610, 34], pivot: [0, 1],
    size: 19, color: "#292E38", bold: true, best_fit: true, min_size: 14, max_size: 19,
    });
    b.text(detail + "/Body", "한 번 누르면 설명 · 같은 슬롯을 한 번 더 누르면 사용/장착", {
    anchor: "top-left", pos: [18, -50], rect_size: [610, 66], pivot: [0, 1],
    size: 16, color: "#4D5667", best_fit: true, min_size: 12, max_size: 16,
    });
  }
  b.patch(box + "/Hint", { anchor: "bottom-center", pos: [0, 18], rect_size: [648, 34], pivot: [0.5, 0] });

  b.write(uiPath, {
    strict: true,
    lint: true,
    bind: {
      mlua: controllerPath,
      props: {
        panel: "/ui/Inventory/Window",
        openBtn: "/ui/Inventory/OpenBtn",
        closeBtn: box + "/BtnClose",
        hintText: box + "/Hint",
        equipRow0: box + "/EquipRow0",
        equipRow1: box + "/EquipRow1",
        equipRow2: box + "/EquipRow2",
        detailTitle: detail + "/Title",
        detailBody: detail + "/Body",
        ...bindings,
      },
    },
  });
}

function rebuildSkills() {
  const uiPath = "ui/EquipWindow.ui";
  const b = UIBuilder.load(uiPath);
  const root = "/ui/EquipWindow/Window";
  const grid = root + "/Grid";

  // 현재 메이플 인벤토리의 촘촘한 슬롯 밀도를 따라 5열로 정리한다.
  b.patchComponent(grid, "MOD.Core.ScrollLayoutGroupComponent", {
    CellSize: { x: 116, y: 108 },
    ConstraintCount: 5,
    GridSpacing: { x: 10, y: 10 },
    Padding: { left: 8, right: 24, top: 8, bottom: 8 },
    ScrollBarThickness: 12,
  });
  b.patchComponent(grid, "MOD.Core.SpriteGUIRendererComponent", {
    Color: { r: 0.94, g: 0.93, b: 0.92, a: 1 },
  });

  for (let i = 1; i <= 28; i += 1) {
    const cell = `${grid}/Cell${i}`;
    b.patch(cell, { rect_size: [116, 108] });
    b.patchComponent(cell, "MOD.Core.SpriteGUIRendererComponent", {
      Color: { r: 0.88, g: 0.94, b: 0.91, a: 1 },
    });
    b.patch(cell + "/Icon", { anchor: "top-center", pos: [0, -8], rect_size: [54, 54], pivot: [0.5, 1] });
    b.patchComponent(cell + "/Icon", "MOD.Core.SpriteGUIRendererComponent", {
      PreserveSprite: 0,
      Color: { r: 1, g: 1, b: 1, a: 1 },
    });
    b.patch(cell + "/Name", { anchor: "bottom-center", pos: [0, 7], rect_size: [108, 36], pivot: [0.5, 0] });
    b.patchComponent(cell + "/Name", "MOD.Core.TextGUIRendererComponent", {
      BestFit: true, FontSize: 14, MinSize: 10, MaxSize: 14,
    });
  }

  b.write(uiPath, { strict: true, lint: true });
}

rebuildWorldMap();
rebuildInventory();
rebuildSkills();
console.log("[T54] 월드맵 정보 팝업 + 슬롯형 가방/스킬 UI 생성 완료");
