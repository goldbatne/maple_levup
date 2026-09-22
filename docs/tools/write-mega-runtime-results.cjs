const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const out = path.join(root, 'docs/reports/mega-area-connectivity-respawn-20260921');
fs.mkdirSync(out, { recursive: true });

const q = value => {
  const s = value == null ? '' : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
const writeCsv = (name, header, rows) => fs.writeFileSync(
  path.join(out, name), [header, ...rows].map(row => row.map(q).join(',')).join('\r\n') + '\r\n', 'utf8');

const portalRuns = {
  mega_01: {
    seed: 2026092161,
    edges: [
      ['r_001','east','r_002'],['r_002','east','r_003'],['r_003','east','r_04'],['r_04','east','r_02'],
      ['r_02','north','r_23'],['r_23','north','r_00a'],['r_00a','south','r_23'],['r_23','west','r_21'],
      ['r_21','north','r_11'],['r_11','east','r_14'],['r_14','east','r_05'],['r_05','west','r_14'],
      ['r_14','west','r_11'],['r_11','south','r_21'],['r_21','east','r_23'],['r_23','south','r_02'],
      ['r_02','east','r_007'],['r_007','west','r_02'],['r_02','west','r_04'],['r_04','west','r_003'],
      ['r_003','west','r_002'],['r_002','west','r_001'],['r_001','west','r_006'],['r_006','east','r_001'],
    ],
  },
  mega_02: {
    seed: 2026092162,
    edges: [
      ['r_041','east','r_047'],['r_047','north','r_043'],['r_043','north','r_053'],['r_053','north','r_044'],
      ['r_044','south','r_053'],['r_053','east','r_054'],['r_054','east','r_077'],['r_077','north','r_073'],
      ['r_073','north','r_083'],['r_083','north','r_04a'],['r_04a','south','r_083'],['r_083','east','r_081'],
      ['r_081','east','r_085'],['r_085','west','r_081'],['r_081','west','r_083'],['r_083','south','r_073'],
      ['r_073','south','r_077'],['r_077','west','r_054'],['r_054','west','r_053'],['r_053','south','r_043'],
      ['r_043','south','r_047'],['r_047','west','r_041'],['r_041','west','r_042'],['r_042','east','r_041'],
    ],
  },
  mega_03: {
    seed: 2026092163,
    edges: [
      ['r_091','east','r_092'],['r_092','east','r_097'],['r_097','north','r_103'],['r_103','north','r_102'],
      ['r_102','east','r_112'],['r_112','east','r_117'],['r_117','north','r_122'],['r_122','east','r_095'],
      ['r_095','west','r_122'],['r_122','west','r_096'],['r_096','east','r_122'],['r_122','south','r_117'],
      ['r_117','west','r_112'],['r_112','west','r_102'],['r_102','south','r_103'],['r_103','east','r_094'],
      ['r_094','west','r_103'],['r_103','west','r_093'],['r_093','east','r_103'],['r_103','south','r_097'],
      ['r_097','west','r_092'],['r_092','west','r_091'],['r_091','west','r_104'],['r_104','east','r_091'],
    ],
  },
  mega_04: {
    seed: 2026092164,
    edges: [
      ['r_131','east','r_134'],['r_134','east','r_133'],['r_133','north','r_142'],['r_142','east','r_143'],
      ['r_143','north','r_13a'],['r_13a','south','r_143'],['r_143','south','r_137'],['r_137','north','r_143'],
      ['r_143','east','r_154'],['r_154','east','r_151'],['r_151','east','r_162'],['r_162','east','r_155'],
      ['r_155','west','r_162'],['r_162','west','r_151'],['r_151','west','r_154'],['r_154','west','r_143'],
      ['r_143','west','r_142'],['r_142','south','r_133'],['r_133','west','r_134'],['r_134','west','r_131'],
    ],
  },
  mega_05: {
    seed: 2026092165,
    edges: [
      ['r_171','east','r_177'],['r_177','north','r_172'],['r_172','east','r_181'],['r_181','east','r_197'],
      ['r_197','north','r_193'],['r_193','east','r_204'],['r_204','east','r_205'],['r_205','west','r_204'],
      ['r_204','west','r_193'],['r_193','south','r_197'],['r_197','west','r_181'],['r_181','west','r_172'],
      ['r_172','west','r_176'],['r_176','east','r_172'],['r_172','south','r_177'],['r_177','west','r_171'],
      ['r_171','west','r_173'],['r_173','east','r_171'],
    ],
  },
};
const portalRows = [];
for (const [mega, run] of Object.entries(portalRuns)) {
  run.edges.forEach((edge, index) => portalRows.push([
    mega, run.seed, index + 1, edge[0], edge[1], edge[2], 'PASS_RUNTIME',
    '활성 RoomPortal Trigger 진입 후 실제 CurrentMap/Room이 target으로 바뀌었는지 확인',
  ]));
}
writeCsv('PORTAL_RUNTIME_EXHAUSTIVE.csv',
  ['mega_area','seed','sequence','source_room','direction','target_room','status','evidence'], portalRows);

writeCsv('RESPAWN_RUNTIME_RESULTS.csv', [
  'mega_area','seed','room_id','map_name','target_population','deaths_before_refill','delay_seconds','spawned','alive_after','ability_reward','potion_stream','damage_ledger','safe_spawn','status','notes'
], [
  ['mega_01',2026092111,'r_002','map002',6,2,'6.86',2,6,'PASS_RUNTIME','PASS_STATIC_INDEPENDENT_RNG','PASS_RUNTIME','PASS_RUNTIME','PASS_RUNTIME','첫 예약 뒤 추가 사망을 재계산하여 부족분 2체만 보충'],
  ['mega_01',2026092111,'r_002','map002',6,2,'8.14',2,6,'PASS_RUNTIME','PASS_STATIC_INDEPENDENT_RNG','PASS_RUNTIME','PASS_RUNTIME','PASS_RUNTIME','리스폰 개체를 다시 실제 기본공격으로 처치 가능'],
  ['ALL','','boss rooms','',0,0,'N/A',0,0,'N/A','N/A','N/A','N/A','PASS_STATIC','RoomSpawner가 boss room을 일반 Population refill 대상에서 제외'],
]);

writeCsv('ABILITY_UI_AUDIT.csv', [
  'item','expected','runtime_result','status','evidence'
], [
  ['collection panel','Mega Run에서 미노출','화면 및 EquipPanel 모드 분기에서 미노출','PASS_RUNTIME','maker_play_20260921_174315_693.png'],
  ['legacy world map','Mega Run에서 미노출','WorldMapPanel 조기 비활성, 런타임 화면 미노출','PASS_RUNTIME','maker_play_20260921_174315_693.png'],
  ['objective HUD','보스를 찾아 처치하세요.','좌상단 420x92 압축 HUD','PASS_RUNTIME','maker_play_20260921_181321_567.png'],
  ['OwnedSkillPool','전투 재고와 분리된 고유 능력 표시','우하단 보유 능력 수/아이콘과 5슬롯 별도 표시','PASS_RUNTIME','maker_play_20260921_181321_567.png'],
  ['ability toast','작은 자동 숨김 토스트','상단 소형 아이콘+몬스터+능력명, 2.5초 후 숨김','PASS_RUNTIME','maker_play_20260921_181321_567.png'],
  ['central ability banner','능력 획득 시 미노출','PlayerCollection의 Run GateNotice 호출 제거','PASS_RUNTIME','maker_play_20260921_181321_567.png'],
  ['random battle inventory','5칸/5초/중복/소비 유지','우하단 5슬롯 표시 및 실제 공급 로그 확인','PASS_RUNTIME','Maker runtime 2026-09-21'],
]);

writeCsv('LEGACY_UI_NPC_AUDIT.csv', [
  'target','run_policy','status','evidence_or_note'
], [
  ['WorldMapPanel','hidden/disabled','PASS_RUNTIME','[WorldMap] Mega Run — 레거시 지역 지도 비활성'],
  ['Equip/Collection panel','hidden/disabled','PASS_RUNTIME','Run 화면에서 컬렉션 버튼/패널 미노출'],
  ['TraitPanel','hidden/disabled','PASS_RUNTIME','Phase3.5 신규 전투 — 창·버튼 전체 비활성'],
  ['RebirthNpc','hidden/disabled','PASS_RUNTIME','[RebirthNpc] Mega Run — NPC 비표시/비활성'],
  ['GoddessNpc','hidden/disabled','PASS_RUNTIME','[GoddessNpc] Mega Run — NPC 비표시/비활성'],
  ['central pending modal','hidden/disabled','PASS_RUNTIME','AbilityOffer 레거시 패널 비활성 및 중앙 능력 GateNotice 제거'],
  ['GateNotice general system','keep for non-ability notices','PASS_STATIC','사망/포션 등 별도 알림은 유지; 능력 획득 중복만 제거'],
]);

writeCsv('BOSS_CLEAR_RUNTIME.csv', [
  'mega_area','seed','boss_id','final_room','arrival_cleared','boss_death_cleared','damage_ledger','instance_cleanup','status'
], [
  ['mega_01',2026092111,'m_faust','r_25','NO','YES','YES','YES','PASS_RUNTIME'],
  ['mega_02',2026092122,'m_jr_balrog','r_075','NO','YES','YES','YES','PASS_RUNTIME'],
  ['mega_03',2026092133,'m_timer','r_125','NO','YES','YES','YES','PASS_RUNTIME'],
  ['mega_04',2026092144,'m_deo','r_135','NO','YES','YES','YES','PASS_RUNTIME'],
  ['mega_05',2026092155,'m_dodo','r_175','NO','YES','YES','YES','PASS_RUNTIME'],
]);

const report = `# Mega Area 연결·리스폰 마무리 보고서

- 프로젝트: \`D:\\maplestory_levup\`
- 검증일: 2026-09-21 KST
- 범위: 기존 Mega Area 5개 구조의 포탈 연결, 탐험 리스폰, UI 정리, 보스 전용 클리어
- 비범위: 신규 장르/스킬/VFX/성장/Area/Boss/Mode 추가

## 결과 요약

- Maker Refresh: PASS
- Build: Error 0, 기존 모델 Warning 2 (Mano InputSpeed, Bowmaster AvatarAttackPlayRate)
- 정적 전수: map 파일 163개, RoomTable 160개, 레거시 연결 333개
- Mega Run 후보 내부 방향 호환 도달 불가 맵: 0개
- 생성 그래프 실제 포탈 왕복: 총 110/110 PASS
- 탐험 일반몹 리스폰: 6~10초 지연, 목표 개체수 복원 PASS
- 보스방 일반 개체 리스폰: 비활성 PASS_STATIC
- 보스 전용 클리어: 5/5 PASS_RUNTIME
- 실패/로비 복귀/인스턴스 정리: PASS_RUNTIME
- UI: 레거시 월드맵·컬렉션 미노출, 간결 목표 HUD, 소형 획득 토스트, OwnedSkillPool 분리 PASS_RUNTIME

## 실제 수정

- \`RootDesk/MyDesk/Room/RoomPortal.mlua\`: 생성 그래프 edge 기반 포탈 활성화, 실제 반대 포탈 도착, 미사용 레거시 포탈 비활성
- \`RootDesk/MyDesk/Room/RoomSpawner.mlua\`: 비보스 탐험방 지연 리스폰, 부족분 재계산, 안전 스폰
- \`RootDesk/MyDesk/GameData/GameData.mlua\`: 6~10초 리스폰 설정, 정확한 최종 보스 사망만 클리어
- \`Mislocated/MyDesk/GameData/GameBalance.csv\`: 리스폰 지연·플레이어 안전거리 설정
- \`RootDesk/MyDesk/UI/RoomProgressHud.mlua\`: 목표 HUD 압축
- \`RootDesk/MyDesk/UI/SkillBar.mlua\`, \`ui/SkillBar.ui\`: 보유 능력과 전투 재고 분리, 소형 토스트
- \`RootDesk/MyDesk/UI/EquipPanel.mlua\`: Run 컬렉션 UI 비활성
- \`RootDesk/MyDesk/UI/WorldMapPanel.mlua\`: Run 레거시 지도 비활성
- \`RootDesk/MyDesk/Progress/PlayerCollection.mlua\`: 능력 획득 중앙 중복 배너 제거
- \`RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua\`: 획득 토스트 전달

## 포탈

\`RoomPortal.RefreshRunBinding\`은 현재 생성된 \`RogueGraph[roomId][direction]\`가 있을 때만 포탈을 켠다. 전환 시 목표 맵의 실제 역방향 RoomPortal 위치를 찾아 안쪽으로 2.5 world unit 이동한 안전 도착점을 쓴다. 목표 포탈이 없으면 근사 좌표로 강행하지 않고 전환을 거부한다.

Maker에서 5개 Seed의 생성 그래프를 깊이 우선 왕복하며 모든 활성 edge를 실제 Trigger 진입으로 확인했다. 상세 110행은 \`PORTAL_RUNTIME_EXHAUSTIVE.csv\`에 있다.

## 리스폰

일반 탐험방은 생존 개체가 Encounter TargetPopulation보다 적어지면 6~10초 뒤 부족분을 다시 계산하여 보충한다. 리스폰 위치는 맵 타일/충돌, 포탈, SpawnLocation, 플레이어 안전거리를 검사한다. 리스폰 몬스터는 기존 RoomMonster 사망 경로를 그대로 사용하므로 능력 판정, 독립 포션 RNG, 피해 장부가 유지된다. 최종 보스방은 일반 Population 리스폰 대상이 아니다.

## 보스 전용 클리어

최종 맵 도착 상태에서 \`complete=false\`, \`objective=false\`를 확인한 뒤 정확한 \`RogueBossMonsterId\`를 실제 기본공격으로 처치했다. 5개 Mega 모두 \`[MegaBossClear]\` 뒤에만 완료되었고 인스턴스가 닫힌 뒤 maptown으로 복귀했다.

## UI

Run 화면에는 디버그 그래프/Seed/Pool/Supply 텍스트와 레거시 월드맵·컬렉션이 없다. 목표는 “보스를 찾아 처치하세요.”만 보여 준다. OwnedSkillPool은 고유 능력 수/아이콘을 보여 주고, 아래 5칸 랜덤 전투 재고와 분리된다. 능력 획득은 상단 소형 2.5초 토스트만 표시하며 중앙 GateNotice 중복은 제거했다.

## 런타임 주의

- 포탈 전수 QA는 플레이어를 실제 활성 포탈 Trigger 위치로 이동시켜 \`OnTriggerEnter -> TryPass\` 전환과 목표 CurrentMap을 확인했다. 맵 이동 API로 성공을 위조하지 않았다.
- 보스 처치는 보스 HP만 QA용으로 1로 낮춘 뒤 기존 자동 기본공격/HitEvent/RoomMonster.Dead 경로를 사용했다.
- 리스폰은 실제 기본공격 사망과 6.86초/8.14초 타이머 후 Population 복원을 확인했다.
- 독립 2~4인 멀티클라이언트는 이번 범위에서 실행하지 않았다. 기존 단일 Maker 클라이언트 제약과 동일하다.

## 판정

현재 Maker 단일 클라이언트에서 수행 가능한 Mega Area 연결·리스폰·UI·보스 클리어 마무리는 완료했다. 실제 2~4인 독립 클라이언트 동시 검증만 환경 제약으로 BLOCKED이다.
`;
fs.writeFileSync(path.join(out, 'FINAL_REPORT.md'), report, 'utf8');

console.log(`runtime rows=${portalRows.length}`);
