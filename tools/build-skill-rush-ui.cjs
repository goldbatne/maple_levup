// Additive, idempotent UIBuilder migration; preserves all existing buttons/bindings.
const path = require('node:path');
const { UIBuilder } = require('../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs');
const file = path.resolve(__dirname, '../ui/SkillBar.ui');
const b = UIBuilder.read(file);
const existing = new Set(b.listEntities().map(e => e.path));
for (let i = 1; i <= 5; i++) {
  const name = `Skill${i}/RushBorder`;
  // Use the existing button's native outline: the icon/background stay intact.
  if (existing.has(`/ui/SkillBar/${name}`)) b.remove(name);
}
if (!existing.has('/ui/SkillBar/RushHud')) {
  b.text('RushHud', '', {
    anchor: 'bottom-right', pivot: [1,0], pos: [-20,116], rect_size:[480,36],
    size:24, bold:true, color:'#FFD16A', outline:false, outline_color:'#342B1F',
    outline_width:0.12, enable:false,
  });
  b.addComponent('RushHud', 'MOD.Core.CanvasGroupComponent', {
    GroupAlpha:1, Interactable:false, BlocksRaycasts:false, Enable:true,
  });
}
b.patchComponent('RushHud', 'MOD.Core.TextGUIRendererComponent', {OutlineWidth:0.12});
const hudText = b.getComponent('RushHud', 'MOD.Core.TextGUIRendererComponent');
delete hudText.Outline; // Text uses OutlineWidth, not SpriteGUIRenderer's Outline flag.
b.upsertComponent('RushHud', 'MOD.Core.TextGUIRendererComponent', hudText);
b.write(file);
console.log('Skill Rush: noninteractive HUD written; native slot outlines used at runtime.');
