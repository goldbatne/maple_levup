#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', '..');
const failures = [];

function fail(message) {
  failures.push(message);
}

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8').replace(/^\uFEFF/, '');
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (char === '"') {
      if (quoted && text[index + 1] === '"') {
        cell += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === ',' && !quoted) {
      row.push(cell);
      cell = '';
    } else if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && text[index + 1] === '\n') index += 1;
      row.push(cell);
      if (row.some((value) => value.length > 0)) rows.push(row);
      row = [];
      cell = '';
    } else {
      cell += char;
    }
  }

  if (cell.length > 0 || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }

  const headers = rows.shift() || [];
  return rows.map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] || ''])));
}

function walkMarkdown(directory, output = []) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'archive') continue;
      walkMarkdown(fullPath, output);
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      output.push(fullPath);
    }
  }
  return output;
}

const requiredDocuments = [
  'README.md',
  'CLAUDE.md',
  'docs/README.md',
  'docs/지식체계_운영.md',
  'docs/프로젝트_현황.md',
  'docs/인수인계_현재상태.md',
  'docs/게임기획서_v0.3.md',
  'docs/밸런스_확정수치.md',
  'docs/지역설계_area04-area20.md',
  'docs/결정기록.md',
  'docs/검증가이드.md',
  'docs/archive/README.md',
];

for (const document of requiredDocuments) {
  if (!exists(document)) fail(`필수 문서 없음: ${document}`);
}

const archivedDocuments = [
  'docs/archive/legacy/CLAUDE_legacy_T0-T58.md',
  'docs/archive/legacy/README_legacy_T0-T58.md',
  'docs/archive/legacy/프로젝트_현황_legacy_T0-T58.md',
  'docs/archive/legacy/인수인계_legacy_T0-T58.md',
  'docs/archive/legacy/게임기획서_v0.3_2026-08-04.md',
  'docs/archive/legacy/밸런스_확정수치_legacy_T0-T58.md',
  'docs/archive/legacy/작업지시서_v2.0_T0-T10.md',
  'docs/archive/legacy/지역설계_area00-area20_legacy.md',
  'docs/archive/legacy/프로젝트_재정리_개발운영_가이드_v1.0.md',
  'docs/archive/reports/몬스터_매칭_감사_T52.md',
  'docs/archive/reports/보스전_T53.md',
  'docs/archive/reports/보우마스터_히든보스_T57.md',
];

for (const document of archivedDocuments) {
  if (!exists(document)) fail(`역사 보관 누락: ${document}`);
}

const balanceRows = parseCsv(read('RootDesk/MyDesk/GameData/GameBalance.csv'));
const balance = Object.fromEntries(balanceRows.map((row) => [row.key, Number(row.value)]));
const monsters = parseCsv(read('RootDesk/MyDesk/GameData/MonsterTable.csv'));
const skills = parseCsv(read('RootDesk/MyDesk/GameData/SkillTable.csv'));
const items = parseCsv(read('RootDesk/MyDesk/GameData/ItemTable.csv'));
const rooms = parseCsv(read('RootDesk/MyDesk/GameData/RoomTable.csv'));
const areas = parseCsv(read('RootDesk/MyDesk/GameData/AreaTable.csv'));

const expectedBalance = {
  exp_base: 60,
  exp_ratio: 1.105,
  boss_hp_multiplier: 10,
  boss_def_multiplier: 1,
  boss_atk_multiplier: 1.5,
  boss_time_limit_seconds: 300,
  skill_stack_max: 5,
};

for (const [key, expected] of Object.entries(expectedBalance)) {
  if (balance[key] !== expected) fail(`GameBalance 불일치: ${key}=${balance[key]} (예상 ${expected})`);
}

const monsterSkills = skills.filter((row) => row.source === 'monster');
const capturableMonsters = monsters.filter((row) => row.drop_skill_id.length > 0);
const bossRooms = rooms.filter((row) => row.room_type === 'boss');
const passiveItems = items.filter((row) => row.item_type === 'passive');
const areaOrder = areas
  .slice()
  .sort((a, b) => Number(a.sort_order) - Number(b.sort_order))
  .map((row) => row.id);
const expectedAreaOrder = [
  'area_00', 'area_01', 'area_03', 'area_02', 'area_04', 'area_05',
  'area_07', 'area_08', 'area_09', 'area_10', 'area_11', 'area_12',
  'area_13', 'area_14', 'area_15', 'area_16', 'area_17', 'area_18',
];
const oppositeDirection = { north: 'south', south: 'north', east: 'west', west: 'east' };
const roomsById = new Map(rooms.map((room) => [room.id, room]));
const roomConnectionIssues = [];
for (const room of rooms) {
  for (const [direction, opposite] of Object.entries(oppositeDirection)) {
    const targetId = room[`conn_${direction}`];
    if (!targetId) continue;
    // r_town is a shared world-map hub. Multiple region entrances intentionally
    // point to it, so a single opposite field cannot represent every return path.
    if (room.id === 'r_town' || targetId === 'r_town' || room.id.startsWith('r_job_')) continue;
    const target = roomsById.get(targetId);
    if (!target) {
      roomConnectionIssues.push(`${room.id} ${direction} → ${targetId}: 대상 없음`);
    } else if (target[`conn_${opposite}`] !== room.id) {
      roomConnectionIssues.push(`${room.id} ${direction} → ${targetId}: ${opposite} 역연결 불일치`);
    }
  }
}

if (capturableMonsters.length !== 91) fail(`포획 대상 몬스터 수 불일치: ${capturableMonsters.length} (예상 91)`);
if (monsterSkills.length !== 91) fail(`몬스터 스킬 수 불일치: ${monsterSkills.length} (예상 91)`);
if (items.length !== 94) fail(`아이템 수 불일치: ${items.length} (예상 94)`);
if (bossRooms.length !== 20) fail(`보스방 수 불일치: ${bossRooms.length} (예상 20)`);
if (passiveItems.length !== 2) fail(`전직 패시브 수 불일치: ${passiveItems.length} (예상 2)`);
if (areaOrder.join(',') !== expectedAreaOrder.join(',')) {
  fail(`지역 순서 불일치: ${areaOrder.join(' → ')}`);
}

const heroPassive = passiveItems.find((row) => row.id === 'i_hero_sword');
const bowmasterPassive = passiveItems.find((row) => row.id === 'i_bowmaster_bow');
if (!heroPassive || heroPassive.passive_stat !== 'STR' || Number(heroPassive.passive_value) !== 10 || Number(heroPassive.stack_max) !== 5) {
  fail('히어로 패시브 정본 불일치');
}
if (!bowmasterPassive || bowmasterPassive.passive_stat !== 'DEX' || Number(bowmasterPassive.passive_value) !== 10 || Number(bowmasterPassive.stack_max) !== 5) {
  fail('보우마스터 패시브 정본 불일치');
}

const status = read('docs/프로젝트_현황.md');
const balanceDocument = read('docs/밸런스_확정수치.md');
const handoff = read('docs/인수인계_현재상태.md');
const requiredStatusClaims = ['91종', '94종', '20개', 'HP ×10', '300초', '최대 5장', 'STR +10', 'DEX +10'];
for (const claim of requiredStatusClaims) {
  if (!status.includes(claim)) fail(`프로젝트 현황의 필수 사실 누락: ${claim}`);
}
if (!balanceDocument.includes('60 × 1.105^(Lv-1)')) fail('밸런스 문서의 필요 EXP 공식 불일치');

const sectorConfig = read('Global/SectorConfig.config');
const area00Maps = ['map001', 'map002', 'map003', 'map00a', 'map004', 'map005', 'map006', 'map007'];
const missingSectorMaps = area00Maps.filter((mapId) => !sectorConfig.includes(mapId));
if (missingSectorMaps.length > 0 && !handoff.includes('SectorConfig')) {
  fail('area_00 SectorConfig 누락이 인수인계에 기록되지 않음');
}
for (const issue of roomConnectionIssues) {
  const signature = issue.split(':')[0];
  if (!handoff.includes(signature)) fail(`방 연결 이슈가 인수인계에 기록되지 않음: ${issue}`);
}

const ignore = read('.gitignore');
for (const ignoredPath of ['.agents/', '.codex/', '.mswai/', '.mcp.json']) {
  if (!ignore.split(/\r?\n/).includes(ignoredPath)) fail(`AI ToolKit/비밀정보 ignore 누락: ${ignoredPath}`);
}

const activeMarkdown = [path.join(root, 'README.md'), path.join(root, 'CLAUDE.md'), ...walkMarkdown(path.join(root, 'docs'))];
const canonicalForStaleScan = [
  'README.md',
  'CLAUDE.md',
  'docs/프로젝트_현황.md',
  'docs/인수인계_현재상태.md',
  'docs/게임기획서_v0.3.md',
  'docs/밸런스_확정수치.md',
  'docs/지역설계_area04-area20.md',
].map((relativePath) => ({ relativePath, text: read(relativePath) }));

const stalePatterns = [
  { pattern: /필요 EXP\(Lv\)\s*=\s*20\s*[×x]\s*1\.12/, label: '과거 EXP 공식' },
  { pattern: /T52 기준\s*\*\*28종\*\*/, label: '과거 몬스터 28종' },
  { pattern: /보스방\s*6(?:개|곳)/, label: '과거 보스방 6개' },
  { pattern: /전직 패시브[^\n]{0,80}\+1%/, label: '과거 패시브 +1%' },
];

for (const { relativePath, text } of canonicalForStaleScan) {
  for (const { pattern, label } of stalePatterns) {
    if (pattern.test(text)) fail(`${relativePath}: ${label}`);
  }
}

for (const markdownPath of activeMarkdown) {
  const text = fs.readFileSync(markdownPath, 'utf8');
  const linkPattern = /\[[^\]]*\]\(([^)]+)\)/g;
  for (const match of text.matchAll(linkPattern)) {
    let target = match[1].trim().replace(/^<|>$/g, '').split('#')[0];
    if (!target || /^(?:https?:|mailto:|codex:)/i.test(target)) continue;
    target = decodeURIComponent(target).replace(/:\d+$/, '');
    const resolved = path.resolve(path.dirname(markdownPath), target);
    if (!fs.existsSync(resolved)) {
      fail(`깨진 로컬 링크: ${path.relative(root, markdownPath)} → ${target}`);
    }
  }
}

const paragraphOwners = new Map();
for (const markdownPath of activeMarkdown) {
  const relativePath = path.relative(root, markdownPath).replace(/\\/g, '/');
  const text = fs.readFileSync(markdownPath, 'utf8');
  const paragraphs = text.split(/\r?\n\s*\r?\n/);
  for (const paragraph of paragraphs) {
    const normalized = paragraph
      .split(/\r?\n/)
      .filter((line) => !/^\s*(?:#|>|\||```|[-*]\s|\d+\.\s)/.test(line))
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim();
    if (normalized.length < 180) continue;
    const owners = paragraphOwners.get(normalized) || new Set();
    owners.add(relativePath);
    paragraphOwners.set(normalized, owners);
  }
}

for (const owners of paragraphOwners.values()) {
  if (owners.size > 1) fail(`활성 문서 장문 중복: ${Array.from(owners).join(', ')}`);
}

const activeLines = activeMarkdown.reduce((sum, markdownPath) => sum + fs.readFileSync(markdownPath, 'utf8').split(/\r?\n/).length, 0);
const archiveRoot = path.join(root, 'docs', 'archive');
const archiveMarkdown = [];
function walkAllMarkdown(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) walkAllMarkdown(fullPath);
    else if (entry.name.endsWith('.md')) archiveMarkdown.push(fullPath);
  }
}
walkAllMarkdown(archiveRoot);
const archiveLines = archiveMarkdown.reduce((sum, markdownPath) => sum + fs.readFileSync(markdownPath, 'utf8').split(/\r?\n/).length, 0);

const summary = {
  activeDocuments: activeMarkdown.length,
  activeLines,
  archivedDocuments: archiveMarkdown.length,
  archiveLines,
  monsterTableRows: monsters.length,
  capturableMonsters: capturableMonsters.length,
  monsterSkills: monsterSkills.length,
  items: items.length,
  bosses: bossRooms.length,
  areaOrder,
  roomConnectionIssues,
  area00SectorStatus: missingSectorMaps.length === 0 ? 'registered' : `pending: ${missingSectorMaps.join(', ')}`,
};

if (failures.length > 0) {
  console.error('KNOWLEDGE BASE VERIFY: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  console.error(JSON.stringify(summary, null, 2));
  process.exit(1);
}

console.log('KNOWLEDGE BASE VERIFY: PASS');
console.log(JSON.stringify(summary, null, 2));
