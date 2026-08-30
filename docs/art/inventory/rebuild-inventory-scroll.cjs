const { UIBuilder } = require("../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs");

const uiPath = "ui/Inventory.ui";
const controllerPath = "RootDesk/MyDesk/UI/InventoryPanel.mlua";
const box = "/ui/Inventory/Window/Box";
const list = box + "/ItemScroll";

const b = UIBuilder.load(uiPath);

for (let i = 0; i < 6; i += 1) {
  const oldPath = box + "/ItemRow" + i;
  if (b.find(oldPath) !== null) b.remove(oldPath);
}
if (b.find(list) !== null) b.remove(list);

b.scrollLayout(list, {
  anchor: "top-center",
  pos: [0, -486],
  rect_size: [648, 430],
  pivot: [0.5, 1],
  layout_type: 1,
  spacing: 6,
  cell_size: [620, 88],
  padding: [4, 24, 4, 4],
  use_scroll: true,
  scroll_bar_visible: 1,
  scroll_bar_thickness: 14,
  scroll_bar_bg_color: "#C7C1B8",
  scroll_bar_handle_color: "#6C7588",
});

const bindings = {};
for (let i = 0; i < 29; i += 1) {
  const row = list + "/ItemRow" + i;
  b.button(row, "", {
    rect_size: [600, 88],
    image_ruid: "129f02486c2baef49a41b31ce16171f6",
    sprite_type: 1,
    bg_color: "#E9E6E1",
    color: "#292E38",
    font_size: 20,
  });
  b.sprite(row + "/Icon", {
    anchor: "middle-left",
    pos: [12, 0],
    rect_size: [64, 64],
    pivot: [0, 0.5],
    image_ruid: "234aca1a4ce946119b68e3717991e775",
    preserve_aspect: true,
    raycast: false,
  });
  bindings["itemRow" + i] = row;
}

b.write(uiPath, {
  strict: true,
  lint: true,
  bind: {
    mlua: controllerPath,
    props: bindings,
  },
});
