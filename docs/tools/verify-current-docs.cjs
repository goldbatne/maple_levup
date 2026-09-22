#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {load,validate} = require('./verify-current-content.cjs');
const root = path.resolve(__dirname,'../..');
const files = ['README.md','docs/README.md','docs/CURRENT_GAME_STATE.md','docs/reports/README.md','docs/tools/README.md'];
function main() {
  const errors = []; const checked = [];
  for (const file of files) {
    const text = fs.readFileSync(path.join(root,file),'utf8');
    for (const match of text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
      let target = match[1].replace(/^<|>$/g,'').split('#')[0];
      if (!target || /^(https?:|mailto:|codex:)/.test(target)) continue;
      target = decodeURIComponent(target).replace(/:\d+$/,'');
      checked.push({file,target});
      if (!fs.existsSync(path.resolve(root,path.dirname(file),target))) errors.push(`${file}: missing link ${target}`);
    }
  }
  const current = fs.readFileSync(path.join(root,'docs/CURRENT_GAME_STATE.md'),'utf8');
  for (const token of ['OwnedSkillPool','ConsumeRandomSlot','66개','35개','NOT_RUN']) if (!current.includes(token)) errors.push('Current documentation missing: '+token);
  const data = validate(load()); errors.push(...data.errors);
  console.log(JSON.stringify({status:errors.length?'FAIL':'PASS_STATIC',scope:'Current entry documents and data; historical reports are not current acceptance claims',documents:files.length,links:checked.length,errors},null,2));
  process.exitCode=errors.length?1:0;
}
module.exports={main};
if(require.main===module)main();
