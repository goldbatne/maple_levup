const fs = require('fs');
const path = require('path');
const { getResourcesBatch } = require('../../.agents/skills/msw-search/scripts/msw_resource_api.cjs');

const root = path.resolve(__dirname, '../..');
const dataDir = path.join(root, 'RootDesk', 'MyDesk', 'GameData');
const cacheDir = path.join(root, 'docs', 'art', 'images-input-packages', '_cache');
const rawDir = path.join(cacheDir, 'raw');

function parseCsv(text) {
  const out = []; let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"') {
        if (text[i + 1] === '"') { cell += '"'; i += 1; } else quoted = false;
      } else cell += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(cell); cell = ''; }
    else if (ch === '\n') { row.push(cell.replace(/\r$/, '')); out.push(row); row = []; cell = ''; }
    else cell += ch;
  }
  if (cell || row.length) { row.push(cell.replace(/\r$/, '')); out.push(row); }
  const header = out.shift();
  return out.filter(r => r.some(Boolean)).map(r => Object.fromEntries(header.map((h, i) => [h, r[i] || ''])));
}

function readCsv(name) {
  return parseCsv(fs.readFileSync(path.join(dataDir, name), 'utf8').replace(/^\uFEFF/, ''));
}

function walk(dir, ext, acc = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, ext, acc); else if (e.name.endsWith(ext)) acc.push(p);
  }
  return acc;
}

function firstSprite(node) {
  if (!node || typeof node !== 'object') return '';
  if (node.Name === 'SpriteRUID' && typeof node.Value === 'string' && node.Value) return node.Value;
  for (const v of Object.values(node)) { const r = firstSprite(v); if (r) return r; }
  return '';
}

function addUse(map, ruid, use) {
  if (!/^[0-9a-f]{32}$/i.test(ruid || '')) return;
  if (!map.has(ruid)) map.set(ruid, []);
  map.get(ruid).push(use);
}

function extFrom(url, contentType) {
  const m = String(url || '').match(/\.([a-z0-9]{2,5})(?:\?|$)/i);
  if (m) return m[1].toLowerCase();
  if (/gif/i.test(contentType || '')) return 'gif';
  if (/webp/i.test(contentType || '')) return 'webp';
  if (/jpe?g/i.test(contentType || '')) return 'jpg';
  return 'png';
}

async function main() {
  fs.mkdirSync(rawDir, { recursive: true });
  const monsters = readCsv('MonsterTable.csv').filter(m => m.drop_skill_id && Number(m.level) <= 200);
  const skills = readCsv('SkillTable.csv');
  const modelRuid = new Map();
  for (const file of walk(path.join(root, 'RootDesk', 'MyDesk', 'Models', 'Monsters'), '.model')) {
    try {
      const obj = JSON.parse(fs.readFileSync(file, 'utf8'));
      const id = String(obj.EntryKey || '').replace(/^model:\/\//, '');
      if (id && !modelRuid.has(id)) modelRuid.set(id, firstSprite(obj));
    } catch (_) {}
  }

  const uses = new Map();
  for (const m of monsters) addUse(uses, modelRuid.get(m.model_id), { kind: 'monster', monster_id: m.id, name: m.name });
  const fields = ['icon_ruid', 'effect_ruid', 'projectile_ruid', 'layer_ruids'];
  for (const s of skills) {
    for (const field of fields) {
      for (const ruid of String(s[field] || '').split('|').filter(Boolean)) {
        addUse(uses, ruid, { kind: 'style', skill_id: s.id, skill_name: s.name, field });
      }
    }
  }

  const supplementary = {
    'd96be74e6b014ce884413a98c139a136': '공식 검색 후보: 6차 오리진 스킬',
    'c912850a22804b7ab7fee10252397397': '공식 검색 후보: 6차 오리진 스킬',
    'f4b476d028ea4c95b7bb26247954cdcf': '공식 검색 후보: 6차 오리진 스킬',
    'f8a5f012719d401c9281b0a81617aafb': '공식 검색 후보: 6차 오리진 스킬',
    '55fd196846694198bd65c59356de0830': '공식 검색 후보: 6차 오리진 스킬',
    '623d68d21e784ac9949fd7941ab53f67': '공식 검색 후보: 6차 오리진 스킬',
    'a6696166fce347e7b6394508f83dd687': '공식 검색 후보: 6차 오리진 스킬',
    '6486822ba9284f41b5c8c3a240d3a52b': '공식 검색 후보: 6차 오리진 스킬',
    '6611bd12f23d4f3e8c45689533ff6e1d': '공식 검색 후보: 6차 오리진 스킬',
    '5518aba1defc4a53b7593109b09959b4': '공식 검색 후보: 6차 오리진 스킬',
    '7d1673d31f0d48ba96061c8a840c64af': '공식 검색 후보: HEXA 스킬',
    'beabe4fd1d6d442dafe41d0d086e622e': '공식 검색 후보: HEXA 스킬',
    '30afd80ab7a34a3d978efd8e83a6eb31': '공식 검색 후보: HEXA 스킬',
    '9520049ad5844acb847351928c162169': '공식 검색 후보: HEXA 스킬',
    '27e15f18340044509dc75492c362c865': '공식 검색 후보: HEXA 스킬',
    '7e11c40b5fcf4d688c40b539b71350a3': '공식 검색 후보: HEXA 스킬',
    'd8cbacc0ed7545d4afa1a948fafca99b': '공식 검색 후보: HEXA 스킬',
    '67a9ec7922374ed79f28d6bb3096aff4': '공식 검색 후보: HEXA 스킬',
    '2d3a1370a91d4da99ecfb42d7cced7c5': '공식 검색 후보: HEXA 스킬',
    '86c80043cbfa4a17ae2df502318f96e8': '공식 검색 후보: HEXA 스킬',
    '2643498ff2bb4b4a8a55c480f00373a4': '공식 검색 후보: 초보자 스킬',
    '12b8ddbe34324edf81ba40fc36f4ad56': '공식 검색 후보: 초보자 스킬',
    '5a19a94eb91e49428d698172dcc6b060': '공식 검색 후보: 초보자 스킬',
    '2f4311e974a44f218bedd1011a561310': '공식 검색 후보: 초보자 스킬',
    '5bc3cb66370a45ae9ba7349672a7cf2b': '공식 검색 후보: 초보자 스킬'
  };
  for (const [ruid, note] of Object.entries(supplementary)) addUse(uses, ruid, { kind: 'style', skill_id: '', skill_name: note, field: 'supplementary_search' });

  const ids = [...uses.keys()].sort();
  const metadata = {};
  for (let i = 0; i < ids.length; i += 40) {
    const batch = ids.slice(i, i + 40);
    try {
      const result = await getResourcesBatch(batch);
      const list = Array.isArray(result) ? result : (result.items || result.results || []);
      for (const item of list) if (item && item.id) metadata[item.id] = item;
    } catch (e) {
      console.error('[batch-failed]', i, e.message);
    }
  }

  let downloaded = 0, missing = 0;
  for (const ruid of ids) {
    const item = metadata[ruid];
    const url = item && item.payload && item.payload.thumbnail;
    if (!url) { missing += 1; continue; }
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const buf = Buffer.from(await res.arrayBuffer());
      const ext = extFrom(url, res.headers.get('content-type'));
      const target = path.join(rawDir, ruid + '.' + ext);
      fs.writeFileSync(target, buf);
      metadata[ruid]._download = { status: 'ok', file: path.relative(cacheDir, target).replace(/\\/g, '/'), bytes: buf.length, contentType: res.headers.get('content-type') || '' };
      downloaded += 1;
    } catch (e) {
      metadata[ruid]._download = { status: 'failed', error: e.message };
      missing += 1;
    }
  }

  fs.writeFileSync(path.join(cacheDir, 'resource_metadata.json'), JSON.stringify(metadata, null, 2));
  fs.writeFileSync(path.join(cacheDir, 'resource_uses.json'), JSON.stringify(Object.fromEntries(uses), null, 2));
  fs.writeFileSync(path.join(cacheDir, 'fetch_summary.json'), JSON.stringify({ total: ids.length, metadata: Object.keys(metadata).length, downloaded, missing }, null, 2));
  console.log(JSON.stringify({ total: ids.length, metadata: Object.keys(metadata).length, downloaded, missing }, null, 2));
}

main().catch(e => { console.error(e); process.exit(1); });
