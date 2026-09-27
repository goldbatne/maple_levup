#!/usr/bin/env node
'use strict';
// One-time, guarded mechanical cleanup of this task's over-broad tooltip edits.
// Does not touch SkillID, art, mechanics, coefficients, or unrelated rows.
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const skillPath=path.join(root,'RootDesk/MyDesk/GameData/SkillTable.csv');
const evidencePath=path.join(root,'docs/reports/skill-diversity-lore-rework-20260924/LORE_DESIGN_66.csv');
function read(file) {
  const text=fs.readFileSync(file,'utf8').replace(/^\uFEFF/,'');
  const data=[];let row=[],cell='',quoted=false;
  for(let i=0;i<text.length;i++) {
    const c=text[i];
    if(c==='"') {if(quoted&&text[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}
    else if(c===','&&!quoted){row.push(cell);cell='';}
    else if((c==='\r'||c==='\n')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(Boolean))data.push(row);row=[];cell='';}
    else cell+=c;
  }
  if(cell||row.length){row.push(cell);data.push(row);}
  const headers=data.shift();
  return {headers,rows:data.map(values=>Object.fromEntries(headers.map((h,i)=>[h,values[i]??''])))};
}
function write(file,table){
  const quote=v=>/[",\r\n]/.test(String(v??''))?'"'+String(v??'').replace(/"/g,'""')+'"':String(v??'');
  fs.writeFileSync(file,'\uFEFF'+table.headers.map(quote).join(',')+'\r\n'+table.rows.map(r=>table.headers.map(h=>quote(r[h])).join(',')).join('\r\n')+'\r\n');
}
const skill=read(skillPath), evidence=read(evidencePath);
if(evidence.rows.length!==66) throw new Error('Expected exactly 66 evidence rows');
const byId=new Map(skill.rows.map(r=>[r.id,r]));
let restored=0,changed=0;
for(const r of evidence.rows){
  const s=byId.get(r.SkillID);
  if(!s||s.description!==r.AfterTooltip||s.behavior!==r.AfterBehavior) throw new Error(`Concurrent change or mismatch: ${r.SkillID}`);
  if(r.BeforeBehavior===r.AfterBehavior&&r.BeforeSecondary===r.AfterSecondary){
    s.description=r.BeforeTooltip;
    r.AfterTooltip=r.BeforeTooltip;
    restored++;
  }else changed++;
}
if(restored!==60||changed!==6) throw new Error(`Unsafe scope ${restored}/${changed}`);
write(skillPath,skill);write(evidencePath,evidence);
console.log(`SCOPE_OK restored_existing_tooltips=${restored} corrected_skills=${changed}`);
