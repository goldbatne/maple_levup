const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const cp = require('child_process');

const root = path.resolve(__dirname, '../../..');
const reportPrefix = 'docs/reports/skill-diversity-audit/';
const latest = fs.readFileSync(path.join(__dirname, 'LATEST_BASELINE.txt'), 'utf8').trim();
const outDir = path.join(root, latest);
const baseline = JSON.parse(fs.readFileSync(path.join(outDir, 'baseline/baseline.json'), 'utf8'));

function statusWithoutReports(lines) {
  return lines.filter(Boolean).filter(line => !line.includes(reportPrefix)).sort();
}

const currentRaw = cp.execFileSync('git', ['status', '--porcelain=v2', '--branch', '--untracked-files=all'], {
  cwd: root,
  encoding: 'utf8'
}).replace(/\r/g, '').split('\n');
const before = statusWithoutReports(baseline.git_status_porcelain_v2);
const after = statusWithoutReports(currentRaw);
const beforeSet = new Set(before);
const afterSet = new Set(after);
const added = after.filter(line => !beforeSet.has(line));
const removed = before.filter(line => !afterSet.has(line));
const payload = {
  baseline_id: baseline.baseline_id,
  checked_at_utc: new Date().toISOString(),
  report_root_ignored: reportPrefix,
  unchanged_outside_report_root: added.length === 0 && removed.length === 0,
  added_status_records: added,
  removed_status_records: removed,
  baseline_status_sha256: crypto.createHash('sha256').update(before.join('\n')).digest('hex'),
  current_status_sha256: crypto.createHash('sha256').update(after.join('\n')).digest('hex')
};
fs.writeFileSync(path.join(outDir, 'WORKTREE_INTEGRITY.json'), JSON.stringify(payload, null, 2) + '\n');
console.log(JSON.stringify(payload, null, 2));
if (!payload.unchanged_outside_report_root) process.exitCode = 1;
