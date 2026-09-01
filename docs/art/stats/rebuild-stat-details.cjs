// T57 후속 — 일반 스탯은 최종 STR/DEX/INT/LUK만, 파생 수치는 왼쪽 상세 창으로 분리한다.
// .ui 원문은 직접 편집하지 않고 UIBuilder로만 쓴다.

const { UIBuilder } = require('../../../.agents/skills/msw-ui-system/scripts/msw_ui_builder.cjs');

const uiPath = 'ui/StatGroup.ui';
const controllerPath = 'RootDesk/MyDesk/UI/StatPanel.mlua';
const b = UIBuilder.load(uiPath);

const root = '/ui/StatGroup';
const window = root + '/Window';
const detail = root + '/DetailWindow';
const toggle = window + '/DetailToggle';
const FRAME_RUID = '21691103c9b6f174d8f0a84a5904153f';
const SLOT_RUID = '129f02486c2baef49a41b31ce16171f6';
const BUTTON_RUID = '2860136c06ab075439721c027de365af';

if (b.find(detail) !== null) b.remove(detail);
if (b.find(toggle) !== null) b.remove(toggle);

// 검은 헤더 배경은 창 전체 폭으로 유지한다. 상세 버튼은 그 위에 파란색으로 올린다.
b.patchComponent(window + '/Title', 'MOD.Core.UITransformComponent', {
  OffsetMax: { x: 250, y: -5 },
  OffsetMin: { x: -250, y: -112 },
  RectSize: { x: 500, y: 107 },
  anchoredPosition: { x: 0, y: -5 },
  Position: { x: 0, y: 435, z: 0 },
});

b.button(toggle, '상세 +', {
  // 검은 헤더 안, 가운데 '스텟' 제목의 왼쪽에 둔다.
  anchor: 'top-left', pos: [16, -15], rect_size: [112, 88], pivot: [0, 1],
  image_ruid: BUTTON_RUID, sprite_type: 1, bg_color: '#4A90D9',
  color: '#FFFFFF', font_size: 18,
});

b.panel(detail, {
  anchor: 'middle-center', pos: [-518, 0], rect_size: [500, 880], pivot: [0.5, 0.5],
  image_ruid: FRAME_RUID, sprite_type: 1, color: '#FAF8F4', alpha: 1,
  raycast: true,
});
b.text(detail + '/Title', '상세 스탯', {
  anchor: 'top-center', pos: [0, -24], rect_size: [440, 64], pivot: [0.5, 1],
  size: 27, color: '#292E38', bold: true,
});

const rows = [
  ['Atk', '물리 공격력'],
  ['Matk', '마법 공격력'],
  ['Def', '방어력'],
  ['Hp', '최대 HP'],
  ['AttackSpeed', '공격 주기'],
  ['MoveSpeed', '이동 속도'],
  ['Capture', '포획률'],
  ['Drop', '드랍 보너스'],
];
const detailBindings = {};
for (let i = 0; i < rows.length; i += 1) {
  const [key, label] = rows[i];
  const row = `${detail}/Row${i}`;
  b.panel(row, {
    anchor: 'top-center', pos: [0, -106 - i * 78], rect_size: [452, 68], pivot: [0.5, 1],
    image_ruid: SLOT_RUID, sprite_type: 1,
    color: i % 2 === 0 ? '#ECE9E3' : '#F3F1ED', alpha: 1,
  });
  b.text(row + '/Label', label, {
    anchor: 'middle-left', pos: [18, 0], rect_size: [210, 48], pivot: [0, 0.5],
    size: 19, color: '#4D5667', bold: true,
  });
  b.text(row + '/Value', '0', {
    anchor: 'middle-right', pos: [-18, 0], rect_size: [196, 48], pivot: [1, 0.5],
    size: 21, color: '#292E38', bold: true, horizontal_alignment: 4,
    best_fit: true, min_size: 15, max_size: 21,
  });
  detailBindings[`detail${key}Label`] = row + '/Label';
  detailBindings[`detail${key}`] = row + '/Value';
}

// 네 스탯의 라벨·값 영역만 누르는 투명 버튼. 오른쪽 + 버튼과 영역을 분리해
// '상세 영향 보기'와 '포인트 분배'가 한 번의 클릭으로 같이 실행되지 않게 한다.
const statRows = [
  ['Str', 3],
  ['Int', 4],
  ['Dex', 5],
  ['Luk', 6],
];
const inspectBindings = {};
for (const [key, rowIndex] of statRows) {
  const inspect = `${window}/Row${rowIndex}/Inspect`;
  if (b.find(inspect) !== null) b.remove(inspect);
  b.button(inspect, '', {
    anchor: 'middle-left', pos: [0, 0], rect_size: [372, 88], pivot: [0, 0.5],
    image_ruid: '', bg_color: '#FFFFFF', alpha: 0,
    color: '#FFFFFF', font_size: 1,
  });
  // 투명 클릭면에는 표시 텍스트가 필요 없다. Text 컴포넌트를 제거하면 실제
  // 라벨·값과의 의도된 겹침을 ui_lint가 '텍스트 충돌'로 오인하지 않는다.
  b.removeComponent(inspect, 'MOD.Core.TextGUIRendererComponent');
  inspectBindings[`btnInspect${key}`] = inspect;
}

b.panel(detail + '/Passive', {
  anchor: 'bottom-center', pos: [0, 24], rect_size: [452, 92], pivot: [0.5, 0],
  image_ruid: SLOT_RUID, sprite_type: 1, color: '#DCE8F5', alpha: 1,
});
b.text(detail + '/Passive/Text', '히든 보스 패시브 없음', {
  anchor: 'middle-center', pos: [0, 0], rect_size: [420, 68], pivot: [0.5, 0.5],
  size: 18, color: '#2E5D8A', bold: true, best_fit: true, min_size: 13, max_size: 18,
});

b.write(uiPath, {
  strict: true,
  lint: true,
  lint_verbose: true,
  bind: {
    mlua: controllerPath,
    props: {
      windowRoot: window,
      btnClose: window + '/BtnClose',
      btnOpen: root + '/OpenBtn',
      levelValue: window + '/Row0/Value',
      expValue: window + '/Row1/Value',
      pointsValue: window + '/Row2/Value',
      strValue: window + '/Row3/Value',
      intValue: window + '/Row4/Value',
      dexValue: window + '/Row5/Value',
      lukValue: window + '/Row6/Value',
      strLabel: window + '/Row3/Label',
      intLabel: window + '/Row4/Label',
      dexLabel: window + '/Row5/Label',
      lukLabel: window + '/Row6/Label',
      btnStr: window + '/Row3/BtnPlus',
      btnInt: window + '/Row4/BtnPlus',
      btnDex: window + '/Row5/BtnPlus',
      btnLuk: window + '/Row6/BtnPlus',
      detailRoot: detail,
      btnDetail: toggle,
      detailPassive: detail + '/Passive/Text',
      ...inspectBindings,
      ...detailBindings,
    },
  },
});
console.log('[T57] 일반/상세 스탯 창 분리 및 바인딩 완료');
