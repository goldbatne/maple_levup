// Local QA bridge for the Maker MCP stdio server when the active Codex task
// has not refreshed its tool list. This does not edit the game or Maker state
// except through the explicitly requested MCP tool.
const { spawn } = require('node:child_process');
const { readFileSync } = require('node:fs');

const name = process.argv[2];
const args = process.argv[3]?.startsWith('@')
  ? { script: readFileSync(process.argv[3].slice(1), 'utf8'),
      ...(process.argv[4] ? { context: process.argv[4] } : {}) }
  : process.argv[3] ? JSON.parse(process.argv[3]) : {};
if (!name) {
  process.stderr.write('Usage: node maker-mcp-call.cjs TOOL [JSON_ARGS|@SCRIPT_FILE]\n');
  process.exit(2);
}

const exe = process.env.MSW_MAKER_MCP_EXE || 'D:/nexon/MapleStory Worlds/MakerMCP/MakerMCP.exe';
const child = spawn(exe, [], { stdio: ['pipe', 'pipe', 'pipe'] });
let buffer = '';
let finished = false;
const timeout = setTimeout(() => finish(2, 'Maker MCP request timed out'), 30000);

function send(id, method, params) {
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
}

function finish(code, message) {
  if (finished) return;
  finished = true;
  clearTimeout(timeout);
  if (message) process.stderr.write(message + '\n');
  child.kill();
  process.exitCode = code;
}

child.on('error', (error) => finish(2, error.message));
child.stderr.on('data', (data) => process.stderr.write(data));
child.stdout.on('data', (data) => {
  buffer += data.toString();
  let index;
  while ((index = buffer.indexOf('\n')) !== -1) {
    const line = buffer.slice(0, index);
    buffer = buffer.slice(index + 1);
    let response;
    try { response = JSON.parse(line); } catch { continue; }
    if (response.id === 1) {
      child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
      if (name === 'list_tools') send(2, 'tools/list', {});
      else send(2, 'tools/call', { name, arguments: args });
    } else if (response.id === 2) {
      if (response.error) {
        process.stdout.write(JSON.stringify(response.error) + '\n');
        finish(1);
      } else if (name === 'list_tools') {
        process.stdout.write(JSON.stringify(response.result?.tools || []) + '\n');
        finish(0);
      } else {
        let text = response.result?.content?.filter((item) => item.type === 'text').map((item) => item.text).join('\n');
        const filter = process.env.MAKER_QA_LOG_FILTER;
        if (name === 'maker_logs' && filter && text) {
          try {
            const parsed = JSON.parse(text);
            const selected = (parsed.logs || []).filter(item => String(item.message || '').includes(filter));
            text = JSON.stringify({ status: parsed.status, kind: parsed.kind,
              totalCount: parsed.count, selectedCount: selected.length, logs: selected });
          } catch {}
        }
        process.stdout.write((text || JSON.stringify(response.result)) + '\n');
        finish(response.result?.isError ? 1 : 0);
      }
    }
  }
});

send(1, 'initialize', {
  protocolVersion: '2025-03-26',
  capabilities: {},
  clientInfo: { name: 'codex-maker-qa', version: '1.0' },
});
