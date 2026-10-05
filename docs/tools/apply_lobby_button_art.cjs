// Replace only the two primary lobby-button visuals via UIBuilder.
// The clickable ButtonComponent entities and their UUIDs remain unchanged.
const { UIBuilder } = require('../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs');

const designs = [
  {
    file: 'ui/PlayerHud.ui', root: 'PartyMenuButton',
    ruid: 'ce3839f975614ba09733de23b4842869',
    label: '파티 찾기', labelX: 13,
  },
  {
    file: 'ui/AreaSelect.ui', root: 'LobbyDungeonButton',
    ruid: '01f27ca538c14de88bac61490c668d1d',
    label: '모험 시작', labelX: -9,
  },
];

for (const design of designs) {
  const b = UIBuilder.read(design.file);
  const root = design.root;
  if (!b.find(root)) throw new Error(`Missing lobby button: ${design.file}/${root}`);
  const fullRoot = `${b.root_path}/${root}/`;
  for (const child of b.listEntities().filter(e => e.path.startsWith(fullRoot))) {
    b.remove(child.path);
  }
  b.patchComponent(root, 'MOD.Core.SpriteGUIRendererComponent', {
    Color: { r: 1, g: 1, b: 1, a: 0 }, OutlineWidth: 0,
  });
  b.patchComponent(root, 'MOD.Core.TextGUIRendererComponent', {
    FontColor: { r: 1, g: 1, b: 1, a: 0 },
  });
  b.sprite(`${root}/ButtonArt`, {
    image_ruid: design.ruid, color: '#ffffff',
    pos: [0, 0], rect_size: [220, 76], sprite_type: 0, raycast: false,
  });
  b.text(`${root}/LobbyLabel`, design.label, {
    pos: [design.labelX, 0], rect_size: [142, 54],
    size: 24, bold: true, color: '#ffffff', alignment: 4,
  });
  b.write(design.file);
}
