#!/usr/bin/env node
'use strict';
// Report-only derivation. Never edits game data or prior audit evidence.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const reportDir = path.join(root, 'docs/reports/skill-diversity-lore-rework-20260924');
function csv(file) {
  const text = fs.readFileSync(path.join(root, file), 'utf8').replace(/^\uFEFF/, '');
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i=0; i<text.length; i++) {
    const c=text[i];
    if(c==='"') { if(quoted && text[i+1]==='"') {cell+='"'; i++;} else quoted=!quoted; }
    else if(c===',' && !quoted) {row.push(cell); cell='';}
    else if((c==='\r'||c==='\n') && !quoted) {
      if(c==='\r' && text[i+1]==='\n') i++;
      row.push(cell); if(row.some(Boolean)) rows.push(row); row=[]; cell='';
    } else cell+=c;
  }
  if(cell || row.length) {row.push(cell); rows.push(row);}
  const keys=rows.shift();
  return rows.map(values=>Object.fromEntries(keys.map((key,i)=>[key,values[i]??''])));
}
const lore=csv('docs/reports/skill-diversity-lore-rework-20260924/LORE_DESIGN_66.csv');
const original=new Map(csv('docs/reports/skill-diversity-rework-20260922/SKILL_BEFORE.csv').map(r=>[r.SkillID,r]));
const current=new Map(csv('RootDesk/MyDesk/GameData/SkillTable.csv').map(r=>[r.id,r]));
if(lore.length!==66 || new Set(lore.map(r=>r.SkillID)).size!==66) throw new Error('Expected 66 unique skill designs');
const monsterUsage = {
  CENTER_BURST:'몬스터 자신을 중심으로 즉시 공격',
  FRONT_CONE:'플레이어를 향한 전방 부채꼴 공격',
  LINE_STRIKE:'플레이어 방향의 직선 판정',
  DELAYED_BLAST:'시전 시점 플레이어 위치를 예고하고 지연 폭발',
  DAMAGE_ZONE:'시전 시점 플레이어 위치에 지속 영역',
  PROJECTILE:'플레이어 방향으로 투사체 발사',
  PROJECTILE_BLAST:'플레이어 방향으로 투사체 발사 후 착탄 폭발',
  PIERCING_PROJECTILE:'플레이어 방향으로 관통 투사체 발사',
  SPREAD_PROJECTILE:'플레이어 방향으로 확산 투사체 발사',
  DASH_STRIKE:'플레이어를 향해 돌진한 뒤 공격',
  SHIELD:'몬스터 자신에게 방어 효과'
};
const esc = value=>String(value??'').replace(/\|/g,'\\|').replace(/\r?\n/g,' ');
const roleDecision={
  LINE_STRIKE:'공격 · 좁은 직선에 적을 정렬해 조준',
  FRONT_CONE:'공격 · 적을 전방에 모으고 접근 각도 선택',
  CENTER_BURST:'공격 · 적에게 접근해 자신 주변에서 발동',
  DELAYED_BLAST:'공격 · 예고 지점과 발동 시점 선택',
  DAMAGE_ZONE:'공격 · 지속 영역의 위치와 적 체류 시간 판단',
  DASH_STRIKE:'공격+이동 · 접근 경로와 도착 위치 판단',
  PROJECTILE:'공격 · 탄도/거리와 단일 목표 조준',
  PROJECTILE_BLAST:'공격 · 탄도와 착탄 위치 판단',
  PIERCING_PROJECTILE:'공격 · 여러 목표가 겹치는 직선 선택',
  SPREAD_PROJECTILE:'공격 · 산탄 방향과 적 분포 판단',
  SHIELD:'방어 · 피해가 예상되는 시점에 사용'
};
const secondaryDecision={SLOW:'감속',WEAKEN:'공격 약화',STUN:'행동 정지',PULL:'끌어당김',KNOCKBACK:'밀어냄'};
const rows=[];
for(const r of lore) {
  const old=original.get(r.SkillID), now=current.get(r.SkillID);
  if(!old || !now || !monsterUsage[r.AfterBehavior]) throw new Error(`Missing evidence/behavior: ${r.SkillID}`);
  let reason='기존 개편 판정 유지. 몬스터/프로젝트 외형 근거를 실제 사용법에 연결';
  if(r.BeforeBehavior!==r.AfterBehavior) reason='원작 행동과 기존 승인 VFX의 방향·시점이 직전 판정보다 더 일치하도록 보정';
  const source=r.SourceType==='PROJECT_ONLY'?'프로젝트 모델·아트·스킬명':`[커뮤니티 위키](${r.SourceURL}) + 프로젝트 자료`;
  const targetLimit=r.AfterBehavior.includes('PROJECTILE') && now.max_targets==='1' ? ' (최대 1명)' : '';
  const role=roleDecision[r.AfterBehavior]+(r.AfterSecondary ? ` + ${secondaryDecision[r.AfterSecondary]||r.AfterSecondary}` : '');
  const verdict=r.SkillID==='s_mon_blood_harp'?'설정 특징 미반영·현행 명중 규칙과 충돌':r.BeforeBehavior!==r.AfterBehavior?'확인된 불일치 보정':'정적 대조에서 확정 충돌 없음';
  rows.push(`| ${esc(r.MonsterName)} / \`${r.SkillID}\` | ${source}; ${esc(r.Evidence)} | ${esc(old.BeforeBehavior)} → ${esc(r.AfterBehavior)}${r.AfterSecondary ? ` + ${esc(r.AfterSecondary)}` : ''} | ${esc(role)} | ${esc(verdict)} | ${esc(reason)} | ${esc(r.AfterTooltip)} | ${esc(monsterUsage[r.AfterBehavior])}${targetLimit} | NOT_RUN / NOT_RUN |`);
}
const behaviorCounts={}; for(const r of lore) behaviorCounts[r.AfterBehavior]=(behaviorCounts[r.AfterBehavior]||0)+1;
const md = [
  '# 66종 몬스터 능력: 원작·프로젝트 근거와 실행 계약',
  '',
  '기준 프로젝트: `D:/maplestory_levup` · 기준 HEAD: `5bd7f4de9dbda5ed5b99af4d77a1d5046be26ac5` · 조사/보정: 2026-09-24.',
  '이 문서는 이전 다양성 감사를 반복하지 않는다. 원래 판정은 이전 `SKILL_BEFORE.csv`, 직전 개편은 `LORE_DESIGN_66.csv`의 Before, 현행은 SkillTable의 After이다.',
  '',
  '공식 Nexon의 개별 몬스터 설정 페이지를 확보하지 못한 항목은 커뮤니티 위키의 World Archive 전사·몬스터 문서와 프로젝트의 몬스터 모델/아트를 구분해 적었다. 위키 페이지 발행·원작 업데이트 시점은 미확인이다. 링크는 능력 전체의 공식 인증이 아니며, 프로젝트가 만든 스킬 모티브를 원작 사실로 바꾸어 말하지 않는다.',
  '',
  'Player 사용법은 현행 툴팁이다. MONSTER_SKILL 사용법은 `MonsterAttack.CastSkill`의 시전자/플레이어 상대 방향·지연 지점 계약을 요약했다. 개별 66종 새 Maker 실행 결과는 없다. 과거 2026-09-23 전수 QA는 이번 6개 판정 보정 이전이므로 현재 변경분의 검증으로 재사용하지 않는다.',
  '',
  '행동 유형 11개는 대부분 공격의 형태 차이이며, 역할 다양성의 합격 판정이 아니다. 주 기능은 공격 63·방어 3, 공격 중 보조 효과 겸용 20이다. 아래 역할/판단은 코드·데이터에서 가능한 선택의 정적 해석이며 실제 플레이 체감으로 인증하지 않았다.',
  '',
  '| 몬스터 / SkillID | 조사 근거 | 원래 → 현행 판정 | 전투 역할·사용 판단 | 설정 적합성 | 변경 이유 | Player 사용법 | Monster 사용법 | Player/Monster 새 런타임 |',
  '|---|---|---|---|---|---|---|---|---|',
  ...rows,
  '',
  `현행 11종 판정 분포: ${Object.entries(behaviorCounts).sort().map(([k,v])=>`${k} ${v}`).join(', ')}.`,
  '',
  '주의: SkillTable의 `range`·계수·대상 수·보조 효과·모든 RUID·SkillID/Monster 연결은 이번 보정에서 유지했다. 근거가 확인된 6개 판정과 해당 6개 툴팁만 데이터 변경했다. 나머지 60개 툴팁은 기존 문구를 유지했다. Maker 결과는 NOT_RUN이다.',
  ''
].join('\n');
fs.mkdirSync(reportDir,{recursive:true});
fs.writeFileSync(path.join(reportDir,'MONSTER_66_DESIGN.md'),md,'utf8');
console.log(`REPORT_OK rows=${rows.length} file=${path.join(reportDir,'MONSTER_66_DESIGN.md')}`);
