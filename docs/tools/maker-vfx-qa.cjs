// Maker-only visual QA driver. Screenshots are copies of Maker output, not new art.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const report = path.join(root, process.env.VFX_REPORT_DIR || 'docs/reports/skill-vfx-alignment-20260926');
const bridge = path.join(__dirname, 'maker-mcp-call.cjs');
const template = fs.readFileSync(path.join(root, 'docs/reports/skill-vfx-alignment-20260926/visual-repeat-qa.lua'), 'utf8');

function csvRows(source) {
  const rows = [];
  let cell = '', row = [], quoted = false;
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
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const header = rows.shift().map(key => key.replace(/^\uFEFF/, ''));
  return rows.map(values => Object.fromEntries(header.map((key, i) => [key, values[i] || ''])));
}

function maker(tool, args, extraEnv) {
  const out = cp.execFileSync(process.execPath, [bridge, tool, JSON.stringify(args || {})], {
    cwd: root, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
    env: {...process.env, ...extraEnv}, timeout: 40000,
  });
  return JSON.parse(out.trim());
}

async function delay(ms) { await new Promise(resolve => setTimeout(resolve, ms)); }

async function capture(skillId, side) {
  const monsters = csvRows(fs.readFileSync(path.join(root, 'RootDesk/MyDesk/GameData/MonsterTable.csv'), 'utf8'));
  const monster = monsters.find(row => row.drop_skill_id === skillId);
  if (!monster) throw new Error(`No MonsterTable drop_skill_id for ${skillId}`);
  const castCount = Math.max(1, Math.min(24, Number(process.env.VFX_CASTS || 8)));
  const script = template.replace('__SKILL_ID__', skillId)
    .replace('__MONSTER_ID__', monster.id).replace('__SIDE__', side)
    .replace('__CAST_COUNT__', String(castCount));
  const result = maker('maker_execute_script', {script, context: 'server_instance_TestPlayInstance'});
  if (result.status !== 'ok') throw new Error(JSON.stringify(result));
  const destDir = path.join(report, 'evidence', side.toLowerCase());
  fs.mkdirSync(destDir, {recursive: true});
  const shots = Math.max(1, Math.min(6, Number(process.env.VFX_SHOTS || 1)));
  const destinations = [];
  for (let i = 0; i < shots; i++) {
    // Capture before a short 0.8-1.2 s effect disappears after the server QA loop.
    await delay(i === 0 ? 80 : 180);
    const shot = maker('maker_screenshot', {});
    if (shot.status !== 'ok' || !shot.path) throw new Error(JSON.stringify(shot));
    const dest = path.join(destDir, shots === 1 ? `${skillId}.png` : `${skillId}_${i + 1}.png`);
    fs.copyFileSync(shot.path, dest);
    destinations.push(dest);
  }
  // The server test loop waits 0.4 s per cast. Allow a short tail for async logs;
  // the missing-DONE branch below still gives slow sessions another 6 seconds.
  await delay(Math.max(3500, castCount * 450));
  let logs = maker('maker_logs', {kind: 'normal'}, {MAKER_QA_LOG_FILTER: `[SkillVFXQA]`});
  const relevant = logs.logs.filter(item => item.message.includes(`id=${skillId}`)
    && item.message.includes(`side=${side}`));
  let done = relevant.findLast(item => item.message.includes(' DONE '));
  if (!done) {
    await delay(6000);
    logs = maker('maker_logs', {kind: 'normal'}, {MAKER_QA_LOG_FILTER: `[SkillVFXQA]`});
    done = logs.logs.findLast(item => item.message.includes(` DONE side=${side} id=${skillId}`));
  }
  return {skillId, monsterId: monster.id, side, screenshots: destinations,
    done: done?.message || 'NOT_DONE', evidence: relevant.map(item => item.message)};
}

const [skillId, side] = process.argv.slice(2);
if (!skillId || !['PLAYER', 'MONSTER'].includes(side)) {
  process.stderr.write('Usage: node maker-vfx-qa.cjs SKILL_ID PLAYER|MONSTER\n');
  process.exit(2);
}
capture(skillId, side).then(result => process.stdout.write(JSON.stringify(result) + '\n'))
  .catch(error => { process.stderr.write(String(error.stack || error) + '\n'); process.exitCode = 1; });
