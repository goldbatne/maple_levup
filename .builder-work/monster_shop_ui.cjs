const {UIBuilder} = require('../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs');
const b = UIBuilder.load('ui/PlayerHud.ui');
b.button('ShopOpenButton', '상점', {
  anchor: 'top-right', pos: [-20, -218], rect_size: [124, 88],
  font_size: 25, bg_color: '#273846', enable: false,
});
b.panel('MonsterShopWindow', {
  anchor: 'stretch', pos: [0, 0], rect_size: [1920, 1080],
  color: {r: 0, g: 0, b: 0, a: 0.55}, enable: false,
});
b.panel('MonsterShopWindow/Dialog', {
  anchor: 'middle-center', pos: [0, 0], rect_size: [690, 590],
  color: '#202b39',
});
b.text('MonsterShopWindow/Dialog/Title', '몬스터 성장 상점', {
  anchor: 'top-center', pos: [-45, -26], rect_size: [410, 48], size: 32, bold: true,
});
b.button('MonsterShopWindow/Dialog/CloseButton', '닫기', {
  anchor: 'top-right', pos: [-18, -20], rect_size: [100, 88], font_size: 23,
});
for (let i = 1; i <= 3; i++) {
  const y = -110 - (i-1)*105;
  b.button(`MonsterShopWindow/Dialog/Product${i}`, '상품', {
    anchor: 'top-center', pos: [0, y], rect_size: [620, 88], font_size: 25,
    bg_color: '#334c5c',
  });
}
b.button('MonsterShopWindow/Dialog/UseTicketButton', '선택권 사용 · 몬스터 선택', {
  anchor: 'bottom-center', pos: [0, 102], rect_size: [620, 88],
  font_size: 25, bg_color: '#557047',
});
b.text('MonsterShopWindow/Dialog/StatusText', '상품은 Maker에서 DEV TEST로 검증합니다.', {
  anchor: 'bottom-center', pos: [0, 28], rect_size: [620, 52],
  size: 21,
});
b.write('ui/PlayerHud.ui', {lint_verbose: true});
