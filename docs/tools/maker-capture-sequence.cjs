// Rapid sequential screenshots through one persistent Maker MCP connection.
// Copies Maker's captures only; it does not create or alter game art.
const {spawn} = require('node:child_process');
const {copyFileSync, mkdirSync} = require('node:fs');
const path = require('node:path');

const label = process.argv[2];
const count = Math.max(1, Math.min(80, Number(process.argv[3] || 30)));
if (!label || !/^[a-zA-Z0-9_-]+$/.test(label)) {
  process.stderr.write('Usage: node maker-capture-sequence.cjs LABEL [COUNT]\n');
  process.exit(2);
}
const outDir = path.resolve(__dirname, '../reports/skill-vfx-alignment-20260926/evidence/sequences', label);
mkdirSync(outDir, {recursive: true});
const exe = process.env.MSW_MAKER_MCP_EXE || 'D:/nexon/MapleStory Worlds/MakerMCP/MakerMCP.exe';
const child = spawn(exe, [], {stdio: ['pipe', 'pipe', 'pipe']});
let buffer = '', captured = 0, failed = false;
const startedAt = Date.now();
const timeout = setTimeout(() => finish(2, 'MCP capture timed out'), 120000);
function send(id, method, params) {
  child.stdin.write(JSON.stringify({jsonrpc: '2.0', id, method, params}) + '\n');
}
function finish(code, reason) {
  if (failed) return;
  failed = true;
  clearTimeout(timeout);
  if (reason) process.stderr.write(reason + '\n');
  process.stdout.write(JSON.stringify({label, captured, durationMs: Date.now() - startedAt,
    outputDir: outDir}) + '\n');
  child.kill();
  process.exitCode = code;
}
child.on('error', error => finish(2, error.message));
child.stderr.on('data', data => process.stderr.write(data));
child.stdout.on('data', data => {
  buffer += data.toString();
  let index;
  while ((index = buffer.indexOf('\n')) !== -1) {
    const line = buffer.slice(0, index);
    buffer = buffer.slice(index + 1);
    let response;
    try { response = JSON.parse(line); } catch { continue; }
    if (response.id === 1) {
      child.stdin.write(JSON.stringify({jsonrpc: '2.0', method: 'notifications/initialized'}) + '\n');
      send(2, 'tools/call', {name: 'maker_screenshot', arguments: {}});
    } else if (response.id >= 2 && !failed) {
      let result;
      try { result = JSON.parse(response.result.content.find(item => item.type === 'text').text); }
      catch (error) { finish(1, `Bad screenshot response: ${error.message}`); return; }
      if (result.status !== 'ok' || !result.path) { finish(1, JSON.stringify(result)); return; }
      const dest = path.join(outDir, String(captured + 1).padStart(3, '0') + '.png');
      copyFileSync(result.path, dest);
      captured++;
      if (captured >= count) finish(0);
      else send(response.id + 1, 'tools/call', {name: 'maker_screenshot', arguments: {}});
    }
  }
});
send(1, 'initialize', {protocolVersion: '2025-03-26', capabilities: {},
  clientInfo: {name: 'codex-maker-vfx-film', version: '1.0'}});
