// Sequential Maker visual QA for finalized 66 skills. Does not edit game assets.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const report = path.join(root, process.env.VFX_REPORT_DIR || 'docs/reports/skill-vfx-alignment-20260926');
const csv = fs.readFileSync(path.join(root,
  'docs/reports/skill-diversity-final-20260925/SKILL_66_FINAL_DESIGN.csv'), 'utf8');
const ids = [...csv.matchAll(/^"[^"]+","(s_mon_[^"]+)"/gm)].map(m => m[1]);
if (ids.length !== 66 || new Set(ids).size !== 66) throw new Error(`Expected 66 unique IDs, got ${ids.length}`);
const logPath = path.join(report, 'maker-visual-runs.jsonl');
const sides = ['PLAYER', 'MONSTER'];
const start = Number(process.argv[2] || 0);
const end = Math.min(ids.length, Number(process.argv[3] || ids.length));
const selected = process.env.VFX_IDS ? new Set(process.env.VFX_IDS.split(',').map(x => x.trim())) : null;
const args = {cwd: root, encoding: 'utf8', maxBuffer: 4 * 1024 * 1024,
  env: {...process.env, VFX_SHOTS: process.env.VFX_SHOTS || '2', VFX_CASTS: process.env.VFX_CASTS || '8'}, timeout: 70000};

function call(command, argv, options = args) {
  return cp.execFileSync(command, argv, options).trim();
}

function waitForPlay() {
  for (let attempt = 1; attempt <= 10; attempt++) {
    try {
      const result = JSON.parse(call(process.execPath,
        [path.join(__dirname, 'maker-mcp-call.cjs'), 'maker_screenshot']));
      if (result.status === 'ok' && result.mode === 'play') return;
    } catch {}
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 2000);
  }
  throw new Error('Maker Play did not become ready after 10 checks');
}

waitForPlay();

for (let index = start; index < end; index++) {
  const skillId = ids[index];
  if (selected && !selected.has(skillId)) continue;
  for (const side of sides) {
    const evidenceDir = path.join(report, 'evidence', side.toLowerCase());
    const existing = path.join(evidenceDir, `${skillId}_1.png`);
    if (fs.existsSync(existing)) {
      process.stdout.write(`SKIP ${index + 1}/66 ${skillId} ${side} existing screenshot\n`);
      continue;
    }
    const startedAt = new Date().toISOString();
    let result;
    try {
      result = JSON.parse(call(process.execPath,
        [path.join(__dirname, 'maker-vfx-qa.cjs'), skillId, side]));
      process.stdout.write(`${index + 1}/66 ${skillId} ${side} ${result.done}\n`);
    } catch (error) {
      const output = String(error.stdout || error.message || error);
      result = {skillId, side, error: output.slice(0, 800)};
      process.stderr.write(`FAIL ${index + 1}/66 ${skillId} ${side} ${result.error}\n`);
      if (output.includes('Not in play mode')) throw new Error('Maker Play unavailable; batch stopped');
    }
    fs.appendFileSync(logPath, JSON.stringify({startedAt, ...result}) + '\n');
  }
  if ((index + 1) % 10 === 0 && index + 1 < end) {
    try {
      call(process.execPath, [path.join(__dirname, 'maker-mcp-call.cjs'), 'maker_stop']);
      call(process.execPath, [path.join(__dirname, 'maker-mcp-call.cjs'), 'maker_play']);
      waitForPlay();
      // The screenshot can enter Play mode before the server instance accepts scripts.
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 6000);
      process.stdout.write(`MAKER_RESET after ${index + 1}/66\n`);
    } catch (error) {
      process.stderr.write(`MAKER_RESET_FAIL ${String(error.message || error)}\n`);
    }
  }
}
process.stdout.write(`BATCH_COMPLETE ${start}-${end} of 66\n`);
