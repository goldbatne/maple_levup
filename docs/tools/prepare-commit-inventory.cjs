#!/usr/bin/env node
'use strict';
// Metadata/hashes only. No account storage, credentials, or private config read.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const out = path.join(root, 'docs/reports/commit-preparation-20260922');
const git = args => execFileSync('git', args, {cwd: root, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024});
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function walk(dir, list = []) {
  if (!fs.existsSync(dir)) return list;
  for (const e of fs.readdirSync(dir, {withFileTypes: true})) {
    const p = path.join(dir, e.name);
    if (e.isSymbolicLink()) throw new Error('Symlink requires separate review: ' + p);
    if (e.isDirectory()) walk(p, list); else if (e.isFile()) list.push(p);
  }
  return list;
}
function protectedFiles() {
  return ['RootDesk', 'map', 'ui', 'Global', 'Mislocated', 'docs/reports/skill-diversity-audit']
    .flatMap(d => walk(path.join(root, d))).map(p => {
      const bytes = fs.readFileSync(p);
      return {path: path.relative(root, p).replaceAll('\\', '/'), bytes: bytes.length, sha256: hash(bytes)};
    }).sort((a,b) => a.path.localeCompare(b.path));
}
fs.mkdirSync(out, {recursive: true});
const before = path.join(out, 'PROTECTED_FILES_BEFORE.json');
if (process.argv.includes('--capture')) {
  if (fs.existsSync(before)) throw new Error('Refusing to overwrite preservation manifest');
  fs.writeFileSync(before, JSON.stringify({createdAt: new Date().toISOString(), head: git(['rev-parse','HEAD']).trim(), files: protectedFiles()}, null, 2) + '\n');
  console.log('Preservation hashes captured');
} else {
  const old = JSON.parse(fs.readFileSync(before, 'utf8'));
  const current = protectedFiles(); const byPath = new Map(current.map(f => [f.path,f]));
  const changes = old.files.filter(f => byPath.get(f.path)?.sha256 !== f.sha256).map(f => ({path:f.path,before:f.sha256,after:byPath.get(f.path)?.sha256 || 'MISSING'}));
  const added = current.filter(f => !old.files.some(x => x.path === f.path)).map(f=>f.path);
  const tracked = git(['diff','--name-only','-z']).split('\0').filter(Boolean);
  const untracked = git(['ls-files','--others','--exclude-standard','-z']).split('\0').filter(Boolean);
  const deleted = new Set(git(['diff','--name-only','--diff-filter=D','-z']).split('\0').filter(Boolean));
  // Generated inventory outputs cannot meaningfully contain their own hashes.
  const generatedOutputs = new Set(['docs/reports/commit-preparation-20260922/COMMIT_INVENTORY.json', 'docs/reports/commit-preparation-20260922/COMMIT_GROUPS.md']);
  const files = [...new Set([...tracked,...untracked])].filter(p => !generatedOutputs.has(p)).sort().map(p => {
    const full = path.join(root,p); const exists = fs.existsSync(full);
    const group = p.startsWith('Mislocated/') ? 'entry-relocation' : /^(RootDesk|Global)\//.test(p) ? 'runtime-data' : p.startsWith('map/') ? 'maps' : p.startsWith('ui/') ? 'ui' : p.startsWith('docs/tools/') ? 'tooling' : /^(docs|Archive)\//.test(p) ? 'documentation-evidence' : 'repository';
    let replacement = '';
    if (deleted.has(p) && p.startsWith('Mislocated/MyDesk/')) replacement = p.replace('Mislocated/MyDesk/', 'RootDesk/MyDesk/');
    return {path:p,group,status:deleted.has(p)?'DELETED':untracked.includes(p)?'UNTRACKED':'MODIFIED',bytes:exists?fs.statSync(full).size:0,sha256:exists?hash(fs.readFileSync(full)):null,replacement:replacement || null,replacementExists:replacement?fs.existsSync(path.join(root,replacement)):null};
  });
  const result = {checkedAt:new Date().toISOString(),branch:git(['branch','--show-current']).trim(),head:git(['rev-parse','HEAD']).trim(),protectedFiles:current.length,protectedChanges:changes,protectedAdded:added,files};
  fs.writeFileSync(path.join(out,'COMMIT_INVENTORY.json'),JSON.stringify(result,null,2)+'\n');
  fs.writeFileSync(path.join(out,'COMMIT_GROUPS.md'),'# 커밋 파일 분류\n\n이 목록은 파일을 stage/commit하지 않는다. 내용 해시는 COMMIT_INVENTORY.json에 있다.\n\n'+Object.entries(Object.groupBy(files,f=>f.group)).map(([g,rows])=>'## '+g+' ('+rows.length+')\n\n'+rows.map(f=>'- `'+f.path+'` — '+f.status).join('\n')).join('\n\n')+'\n');
  console.log(JSON.stringify({protectedFiles:current.length,protectedChanges:changes,protectedAdded:added,groups:Object.fromEntries(Object.entries(Object.groupBy(files,f=>f.group)).map(([k,v])=>[k,v.length])),bytes:files.reduce((n,f)=>n+f.bytes,0),deletions:files.filter(f=>f.status==='DELETED').map(f=>({path:f.path,replacement:f.replacement,exists:f.replacementExists}))},null,2));
}
