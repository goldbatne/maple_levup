// Consolidate the manually inspected 66-skill Maker contact sheets with
// the finalized design and the fresh Player/Monster cast log. Reporting only.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const report = path.join(root, 'docs/reports/skill-vfx-meaning-20260926');

function csvRows(source) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    if (c === '"') {
      if (quoted && source[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { row.push(cell); cell = ''; }
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && source[i + 1] === '\n') i++;
      row.push(cell); cell = '';
      if (row.some(value => value !== '')) rows.push(row);
      row = [];
    } else cell += c;
  }
  if (cell || row.length) rows.push([...row, cell]);
  const keys = rows.shift().map(value => value.replace(/^\uFEFF/, ''));
  return rows.map(values => Object.fromEntries(keys.map((key, index) => [key, values[index] || ''])));
}
function readCsv(relative) { return csvRows(fs.readFileSync(path.join(root, relative), 'utf8')); }
function esc(value) { return `"${String(value ?? '').replaceAll('"', '""')}"`; }

const design = readCsv('docs/reports/skill-diversity-final-20260925/SKILL_66_FINAL_DESIGN.csv');
const previous = readCsv('docs/reports/skill-vfx-alignment-20260926/SKILL_66_VFX_VISUAL_REVIEW.csv');
if (design.length !== 66 || previous.length !== 66) throw new Error('Expected 66 design and prior review rows');
const seen = new Set();
const motifs = [
  '전방의 이슬 액체 직선', '시전자를 감싸는 푸른 껍질', '붉은 껍질의 전진 궤적',
  '시전자 중심 무지개 파동', '전방에 남는 포자 구름', '지면에 퍼지는 대형 포자 충격',
  '시전자를 감싸는 암석 껍질', '도끼 형태 근접 절단', '지면에서 솟는 검은 뿌리',
  '멧돼지 몸통의 전진 궤적', '뼈 기둥이 솟는 타격', '전방의 화염 베기',
  '이동하는 회전 나무탄', '지면에 달라붙는 초록 점액', '시전자 둘레의 밝은 마법가루',
  '시전자를 감싸는 밑동·수피', '대상 방향의 보라색 저주 인형', '시전자 근처 먹물 폭발',
  '유령 손과 푸른 충격', '시전자를 감싸는 어둠 장막', '리본 달린 전진 궤적',
  '불가사리 물 회전 충격', '전방의 화염 횡베기', '용의 전방 화염 타격',
  '검은 발톱의 빠른 이동 궤적', '대상 위 번개 기둥', '별 모양 이동 탄환',
  '달빛 구체 이동 탄환', '지면에 남는 잎바람', '얼음 발톱의 전진 궤적',
  '얼음 송곳 타격', '빙결 조각의 전방 휘두름', '지면에서 솟는 먹물',
  '움직이는 물 상어 형상', '횡방향 물줄기 타격', '시전자 아래의 붉은 북 진동',
  '전진하는 보석 탄환', '시전자 중심 보라 중력 기어', '장난감 바퀴의 이동 궤적',
  '시간편린의 조준 지점 폭발', '시간 장치형 조준 지점 충격', '모래의 전방 나선',
  '모래 분출의 지점 폭발', '지면에 솟는 선인장 가시', '연금 독연기의 대상 구름',
  '기계식 청색 에너지 탄', '이동하는 녹색 독액', '시전자를 감싸는 거대 집게·물결',
  '목각 인형의 회전 충격', '복숭아 과실 탄환', '태륜의 물바람 이동탄',
  '피의 하프의 붉은 깃털 베기', '전방의 냉기 송곳 타격', '마뇽의 화염 전방 타격',
  '시전자 몸의 기도·강화 광휘', '시전자를 감싸는 금빛 보호 문양',
  '이동하는 공허 파편', '움직이는 녹색 에너지 탄', '전방의 분홍 직선 레이저',
  '시전자 중심 보라 흡인 소용돌이', '번개 돌진 경로와 도착 베기',
  '지면에 남는 화염 구역', '넓은 검은 꽃·그림자 구역', '철갑 돌진의 흙먼지 경로',
  '조준 지점의 암흑 지진', '넓은 검은 뿌리 구역',
];
if (motifs.length !== 66) throw new Error(`Expected 66 observed motifs, got ${motifs.length}`);

const adjustments = {
  s_mon_fairy: {
    issue: '적 공격력 약화인데 밝은 가루가 시전자 몸을 감싸 자기 강화처럼 읽힘',
    change: '기존 마법가루 시퀀스를 전방 대상 쪽으로 이동하고 약화 표식은 실제 피격 대상에만 재생',
  },
  s_mon_octopus: {
    issue: '먹물 약화가 시전자 발밑에서 폭발해 자기 공격/광역 폭발처럼 읽힘',
    change: '기존 먹물 시퀀스를 전방으로 옮기고 약화 표식은 실제 피격 대상에만 재생',
  },
  s_mon_drumming_bunny: {
    issue: '자기 공격 강화인데 큰 붉은 지면 충격파가 범위 공격처럼 읽힘',
    change: '기존 북·별 프레임을 0.62배로 줄이고 시전자 몸 쪽으로 올려 자기 강화 맥동으로 정리',
  },
  s_mon_king_clang: {
    issue: '전방 넉백인데 거대한 집게가 시전자를 둘러싸 방어막처럼 읽힘',
    change: '기존 집게·파도 시퀀스를 전방으로 이동해 밀어내는 방향을 강조',
  },
  s_mon_cygnus: {
    issue: '시전자와 목표에 별도 거대 구역이 생기고 반복 틱마다 중첩되어 유효 위치를 오해할 수 있음',
    change: '목표 지점에만 1회 재생하고 실제 틱 지속시간 동안 유지; 알파 0.72로 캐릭터 가시성 확보',
  },
  s_mon_mutant_stumpy: {
    issue: '시전자와 목표에 별도 거대 구역이 생기고 반복 틱마다 중첩되어 유효 위치를 오해할 수 있음',
    change: '목표 지점에만 1회 재생하고 실제 틱 지속시간 동안 유지; 알파 0.72로 캐릭터 가시성 확보',
  },
};
// All 15 skills using the delayed/zone VFX route, including five whose
// primary role is CONTROL or DEBUFF rather than AREA.
const areaIds = new Set([
  's_mon_mushroom', 's_mon_dark_axe_stump', 's_mon_eliza',
  's_mon_squid', 's_mon_chronos', 's_mon_meercat', 's_mon_deo',
  's_mon_advanced_knight_b', 's_mon_cygnus', 's_mon_mutant_stumpy',
  's_mon_tauromacis', 's_mon_timer', 's_mon_homun', 's_mon_zeno',
  's_mon_ancient_dark_golem',
]);
const finalMeaning = {
  s_mon_fairy: '전방 적중점의 마법가루와 피해 대상 위 보라 약화 표식',
  s_mon_octopus: '전방 적중점의 먹물과 피해 대상 위 보라 약화 표식',
  s_mon_drumming_bunny: '시전자 몸 가까이에 모이는 북·별의 강화 맥동',
  s_mon_king_clang: '시전자 앞쪽으로 뻗는 집게·물결 밀치기',
};
for (const id of areaIds) {
  if (!adjustments[id]) adjustments[id] = {
    issue: '실제 조준 지점과 별개로 시전자 위치에도 이펙트가 뜨고 타격 시 다시 겹침',
    change: '기존 프레임을 조준 지점에 1회만 재생하고 효과 시점까지 표시; 피해·제어 판정은 유지',
  };
}

const logFile = path.join(report, 'maker-visual-runs.jsonl');
const captures = new Map();
if (fs.existsSync(logFile)) {
  for (const line of fs.readFileSync(logFile, 'utf8').trim().split(/\r?\n/)) {
    if (!line) continue;
    const item = JSON.parse(line);
    if (item.done && item.done.includes('qaOk=true') && item.done.includes('accepted=')) {
      captures.set(`${item.skillId}:${item.side}`, item);
    }
  }
}
const afterRoot = path.join(report, 'after_final');
const afterCaptures = new Map();
const afterLog = path.join(afterRoot, 'maker-visual-runs.jsonl');
if (fs.existsSync(afterLog)) {
  for (const line of fs.readFileSync(afterLog, 'utf8').trim().split(/\r?\n/)) {
    if (!line) continue;
    const item = JSON.parse(line);
    if (item.done && item.done.includes('qaOk=true'))
      afterCaptures.set(`${item.skillId}:${item.side}`, item);
  }
}
const header = ['Monster', 'SkillID', 'SkillName', 'FinalPrimaryRole', '실제 기능',
  '현재 VFX 의미', '의도 일치 여부(YES/NO)', '문제점', '조치(KEEP/ADJUST/REWORK)',
  '수정 내용', 'Story·Identity 근거', 'Player PASS', 'Monster PASS'];
const rows = design.map((item, index) => {
  if (seen.has(item.SkillID)) throw new Error(`Duplicate SkillID ${item.SkillID}`);
  seen.add(item.SkillID);
  const old = previous.find(row => row.SkillID === item.SkillID);
  if (!old) throw new Error(`Missing prior review for ${item.SkillID}`);
  const adjust = adjustments[item.SkillID];
  const pass = side => {
    const initial = captures.get(`${item.SkillID}:${side}`);
    if (!initial || !initial.screenshots?.every(file => fs.existsSync(file))) return 'NOT_RUN';
    if (adjust) {
      const repeated = afterCaptures.get(`${item.SkillID}:${side}`);
      const after = path.join(afterRoot, 'evidence', side.toLowerCase(), `${item.SkillID}_1.png`);
      if (!repeated || !fs.existsSync(after)) return 'BEFORE_ONLY';
    }
    return 'PASS_SAMPLED';
  };
  return {
    Monster: item.Monster, SkillID: item.SkillID, SkillName: item.SkillName,
    FinalPrimaryRole: item.FinalPrimaryRole, '실제 기능': item['실제 최종 기능'],
    '현재 VFX 의미': finalMeaning[item.SkillID] || (areaIds.has(item.SkillID)
      ? motifs[index] + ' — 조준 지점에만 표시' : motifs[index]),
    '의도 일치 여부(YES/NO)': pass('PLAYER') === 'PASS_SAMPLED' && pass('MONSTER') === 'PASS_SAMPLED' ? 'YES' : 'NO',
    '문제점': adjust?.issue || '확인한 시전 장면에서 기능과 반대 의미가 보이지 않음',
    '조치(KEEP/ADJUST/REWORK)': adjust ? 'ADJUST' : 'KEEP',
    '수정 내용': adjust?.change || '기존 RUID·프레임·배치 유지',
    'Story·Identity 근거': `${item['Lore/Identity 근거']} [${item.SourceType || 'PROJECT'}: ${item.SourceURL || '프로젝트 내부'}]`,
    'Player PASS': pass('PLAYER'), 'Monster PASS': pass('MONSTER'),
  };
});
fs.mkdirSync(report, {recursive: true});
fs.writeFileSync(path.join(report, 'SKILL_66_VFX_MEANING_REVIEW.csv'),
  header.map(esc).join(',') + '\n' + rows.map(row => header.map(key => esc(row[key])).join(',')).join('\n') + '\n');
const counts = rows.reduce((out, row) => {
  const key = row['조치(KEEP/ADJUST/REWORK)']; out[key] = (out[key] || 0) + 1; return out;
}, {});
process.stdout.write(JSON.stringify({rows: rows.length, counts,
  player: rows.reduce((a, x) => (a[x['Player PASS']] = (a[x['Player PASS']] || 0) + 1, a), {}),
  monster: rows.reduce((a, x) => (a[x['Monster PASS']] = (a[x['Monster PASS']] || 0) + 1, a), {})}) + '\n');
