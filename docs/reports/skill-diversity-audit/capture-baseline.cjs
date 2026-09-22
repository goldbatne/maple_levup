#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const cp = require('child_process');

const root = path.resolve(__dirname, '..', '..', '..');
const reportRootRel = 'docs/reports/skill-diversity-audit';
const reportRoot = path.join(root, reportRootRel);

function git(args, encoding = 'utf8') {
  return cp.execFileSync('git', args, { cwd: root, encoding, maxBuffer: 128 * 1024 * 1024 });
}
function shaBuffer(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function shaFile(file) { return shaBuffer(fs.readFileSync(file)); }
function normalize(p) { return p.split(path.sep).join('/'); }
function safeRel(p) {
  const rel = normalize(path.relative(root, p));
  if (rel.startsWith('../') || path.isAbsolute(rel)) throw new Error(`outside workspace: ${p}`);
  return rel;
}
function isSensitive(rel) {
  const s = rel.toLowerCase();
  const base = path.posix.basename(s);
  return base === '.env' || base.startsWith('.env.') ||
    /(^|\/)(secrets?|credentials?|auth)(\/|$)/.test(s) ||
    /(^|[-_.])(secret|token|credential|apikey|api_key|private[-_]?key)([-_.]|$)/.test(base) ||
    /\.(pem|p12|pfx|key|keystore|jks)$/.test(base);
}
function csvCell(v) {
  const s = String(v ?? '');
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

fs.mkdirSync(reportRoot, { recursive: true });

const now = new Date();
const timestampUtc = now.toISOString();
const timestampKst = new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
}).format(now).replace(' ', 'T').replace(/:/g, '');
const head = git(['rev-parse', 'HEAD']).trim();
const branch = git(['branch', '--show-current']).trim() || '(detached)';
const upstream = (() => {
  try { return git(['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}']).trim(); }
  catch { return ''; }
})();

const rawStatus = git(['status', '--porcelain=v2', '-z', '--branch', '--untracked-files=all'], 'buffer');
const statusEntries = rawStatus.toString('utf8').split('\0').filter(Boolean);
const filteredStatus = statusEntries.filter(line => {
  const normalized = line.replace(/\\/g, '/');
  return !normalized.includes(` ${reportRootRel}/`) && !normalized.endsWith(` ${reportRootRel}`) &&
    !normalized.startsWith(`? ${reportRootRel}/`);
});

const untracked = git(['ls-files', '--others', '--exclude-standard', '-z'], 'buffer')
  .toString('utf8').split('\0').filter(Boolean)
  .map(x => x.replace(/\\/g, '/'))
  .filter(x => !x.startsWith(`${reportRootRel}/`));
const trackedChanged = git(['diff', '--name-only', '-z', 'HEAD'], 'buffer')
  .toString('utf8').split('\0').filter(Boolean)
  .map(x => x.replace(/\\/g, '/'))
  .filter(x => !x.startsWith(`${reportRootRel}/`));

const fingerprintRecords = [];
for (const rel of [...new Set([...trackedChanged, ...untracked])].sort()) {
  const abs = path.join(root, ...rel.split('/'));
  if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) {
    fingerprintRecords.push({ path: rel, state: 'missing_or_deleted', size: 0, sha256: '' });
    continue;
  }
  const st = fs.statSync(abs);
  fingerprintRecords.push({
    path: rel,
    state: untracked.includes(rel) ? 'untracked' : 'tracked_changed',
    size: st.size,
    sha256: shaFile(abs)
  });
}
const fingerprintInput = JSON.stringify({ head, status: filteredStatus, files: fingerprintRecords });
const workingFingerprint = shaBuffer(Buffer.from(fingerprintInput, 'utf8'));
const baselineId = `skill-audit-${timestampKst}KST-${head.slice(0, 10)}-wt${workingFingerprint.slice(0, 12)}`;
const outDir = path.join(reportRoot, baselineId);
const baselineDir = path.join(outDir, 'baseline');
const untrackedDir = path.join(baselineDir, 'untracked');
fs.mkdirSync(untrackedDir, { recursive: true });

const patchPath = path.join(baselineDir, 'tracked-working-tree.patch');
fs.writeFileSync(patchPath, git(['diff', '--binary', 'HEAD'], 'buffer'));

const copied = [];
const excluded = [];
const nativeEntryExtensions = new Set([
  '.map', '.ui', '.mlua', '.model', '.codeblock', '.userdataset',
  '.tileset', '.directory', '.config', '.behaviourtree', '.material',
]);
for (const rel of untracked) {
  const abs = path.join(root, ...rel.split('/'));
  if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) continue;
  if (isSensitive(rel)) {
    excluded.push({ path: rel, reason: 'sensitive-name-policy', size: fs.statSync(abs).size, sha256: '' });
    continue;
  }
  const extension = path.extname(rel).toLowerCase();
  const snapshotRel = nativeEntryExtensions.has(extension) ? `${rel}.snapshot` : rel;
  const dest = path.join(untrackedDir, ...snapshotRel.split('/'));
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(abs, dest);
  copied.push({
    path: rel,
    snapshot_path: snapshotRel,
    restore_path: rel,
    size: fs.statSync(abs).size,
    sha256: shaFile(abs),
  });
}

const keyInputs = [
  'Mislocated/MyDesk/GameData/SkillTable.csv',
  'Mislocated/MyDesk/GameData/SkillTable.userdataset',
  'RootDesk/MyDesk/GameData/MonsterTable.csv',
  'RootDesk/MyDesk/GameData/MonsterTable.userdataset',
  'RootDesk/MyDesk/GameData/GameBalance.csv',
  'RootDesk/MyDesk/GameData/GameBalance.userdataset',
  'RootDesk/MyDesk/GameData/GameData.mlua',
  'RootDesk/MyDesk/Progress/PlayerCollection.mlua',
  'RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua',
  'RootDesk/MyDesk/PlayerAttack.mlua',
  'RootDesk/MyDesk/MonsterAttack.mlua',
  'RootDesk/MyDesk/Combat/SkillEffect.mlua',
  'RootDesk/MyDesk/Combat/SkillProjectile.mlua',
  'RootDesk/MyDesk/UI/SkillBar.mlua',
  'RootDesk/MyDesk/UI/EquipPanel.mlua',
  'RootDesk/MyDesk/Save/PlayerDBManager.mlua',
  'RootDesk/MyDesk/Save/SavePermanentData.mlua',
  'docs/art/import-runs/ALL_AREAS_20260914_151243/RESOURCE_MAP.jsonl',
  'docs/art/area00-images-output/AREA_00_IMAGES_RESOURCE_MAP.csv'
];
const keyManifest = keyInputs.map(rel => {
  const abs = path.join(root, ...rel.split('/'));
  if (!fs.existsSync(abs)) return { path: rel, exists: false, size: 0, sha256: '' };
  return { path: rel, exists: true, size: fs.statSync(abs).size, sha256: shaFile(abs) };
});

const metadata = {
  baseline_id: baselineId,
  analysis_started_utc: timestampUtc,
  analysis_started_kst: timestampKst.replace('T', ' ') + ' KST',
  repository_root: normalize(root),
  branch,
  head_commit: head,
  upstream,
  dirty: filteredStatus.some(x => !x.startsWith('# ')),
  working_tree_fingerprint_sha256: workingFingerprint,
  report_root_excluded_from_fingerprint: reportRootRel,
  git_status_porcelain_v2: filteredStatus,
  changed_file_manifest: fingerprintRecords,
  untracked_snapshot: {
    copied_count: copied.length,
    excluded_sensitive_count: excluded.length,
    copied,
    excluded
  },
  key_input_manifest: keyManifest,
  preservation: {
    head_commit: head,
    repository_note: '기존 저장소의 HEAD 객체를 기준으로 재현한다. 전체 git bundle은 대용량 저장소에서 장시간 고정되는 문제 때문에 만들지 않았다.',
    tracked_patch: safeRel(patchPath),
    untracked_copy_root: safeRel(untrackedDir),
    reconstruction: [
      `동일 저장소에서 git checkout ${head}로 기준 커밋을 체크아웃한다.`,
      'git apply --binary tracked-working-tree.patch를 적용한다.',
      'baseline/untracked 아래 파일을 copied[].restore_path로 복사한다. .snapshot 접미사는 복원 시 제거한다.',
      '민감 이름 정책으로 제외된 파일은 보고서에 내용이 포함되지 않으므로 원래 안전 저장소에서 별도로 복구한다.'
    ]
  }
};
fs.writeFileSync(path.join(baselineDir, 'baseline.json'), JSON.stringify(metadata, null, 2) + '\n');
fs.writeFileSync(path.join(baselineDir, 'working-tree-status.txt'), filteredStatus.join('\n') + '\n');
const rows = [['state','path','size','sha256'], ...fingerprintRecords.map(x => [x.state,x.path,x.size,x.sha256])];
fs.writeFileSync(path.join(baselineDir, 'changed-files-sha256.csv'), rows.map(r => r.map(csvCell).join(',')).join('\n') + '\n');
const keyRows = [['path','exists','size','sha256'], ...keyManifest.map(x => [x.path,x.exists,x.size,x.sha256])];
fs.writeFileSync(path.join(baselineDir, 'key-inputs-sha256.csv'), keyRows.map(r => r.map(csvCell).join(',')).join('\n') + '\n');
fs.writeFileSync(path.join(reportRoot, 'LATEST_BASELINE.txt'), `${baselineId}\n${normalize(path.relative(root, outDir))}\n`);

console.log(JSON.stringify({ baseline_id: baselineId, output: safeRel(outDir), dirty: metadata.dirty,
  changed: fingerprintRecords.length, untracked_copied: copied.length, sensitive_excluded: excluded.length }, null, 2));
