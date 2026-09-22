# 로그라이트 완료 감사 — 작업 중

대상: `D:/maplestory_levup`. 2026-09-21, HEAD `2eb7498eda8f53440648ef6107d6c933ba55d5c6` + 기존 미커밋 변경 포함. 기준 감사/복원 자료는 변경하지 않는다. 기존 성공 기록은 조건부 증빙이며 전수 PASS가 아니다.

현재 실행 증빙: `seed-before.json` (Maker server_main, 전체 실제 20 Area × 2 Seed × 반복 생성). 그래프 검사이며 이동/완주 검사가 아니다. Area 06 없음.
이전 실행 증빙: `../roguelite-recovery-20260921/LOBBY_RUNTIME_FOLLOWUP.md`, `lobby-runtime-evidence.json`. 이동 보조·서버 직접 사망 호출의 한계는 해당 보고서대로 유지한다.

|2번 번호|요구사항|초기 상태|파일/방법/증빙|남은 검증|
|---|---|---|---|---|
|1|baseline 보호/원본 병합|PARTIAL|기존 merge/recovery 보고서와 작업 트리|최종 변경/보호 해시|
|2|최신 모드 규칙|PARTIAL|GameData, PlayerStats, PlayerSkillSlots|전체 비활성 경로|
|3|Area 단위 Run|PARTIAL|GameData, RoomPortal; 이전 Solo 로그|전체 Area 완료/실패|
|4|기본 전투/고정 능력치|PARTIAL|PlayerAttack, PlayerStats|구세이브 영향 검사|
|5|확정 획득/고정 슬롯|PARTIAL|MonsterCollection, PlayerSkillSlots; 이전 Solo 로그|예외 전수|
|6|교체/포기 후보|PARTIAL|PlayerSkillSlots, SkillBar|동시 요청/전환/종료|
|7|쿨다운|PARTIAL|PlayerAttack SkillReadyAt; 이전 Solo 로그|66종/우회 검사|
|8|랜덤 공급 비활성|PASS_STATIC_ONLY|PlayerSkillSlots StartRandomSupply/Supply/Consume|시간 경과 Runtime|
|9|그래프 레벨 생성|PARTIAL|GameData GenerateRogueliteGraph; seed-before.json|fallback 오류 수정/이동|
|10|생성 유효성|PARTIAL|GameData ValidateRogueliteGraph|주 경로/목표/예산 검증 누락|
|11|Seed 재현|PARTIAL|RogueNextInt; RoomSpawner SpawnOne|초기 스폰이 combat RNG 사용|
|12|Encounter|PARTIAL|RoomSpawner|벽/출구/일회성/예산|
|13|기존 스킬 지형 호환|NOT_RUN|PlayerAttack, MonsterAttack|66종 실제 판정|
|14|목표/Clear|PARTIAL|GameData reach_exit/defeat_final_guardian|전체 Area/유형|
|15|솔로/협동|PARTIAL|GameData 참가자/사망/전환|독립 2–4 client/재접속|
|16|HP scaling|PASS_STATIC_ONLY|GameData GetRunHpScale|1–4 서버 계산/실제 멀티|
|17|협동 능력 획득|PASS_STATIC_ONLY|GameData GrantRunKillRewards|참가/거리/중복/멀티|
|18|UI/기록|PARTIAL|SkillBar, AreaSelect, RoomProgress, PlayerDBManager|레거시 HUD/선택 UI|
|19|저장/서버 판정|PARTIAL|PlayerDBManager, GameData, PlayerSkillSlots|잘못된 타입/권한/재접속|
|20|강제 30초 온보딩 없음|NOT_RUN|실행 스크립트 검색 예정|실제 연결 확인|
|21|기존 맵 재사용|PARTIAL|RoomTable/AreaTable/map; 기존 Instance 전환 기록|실제 사용 pool 분류|
|22|회귀/변경 추적|PARTIAL|이전 recovery 보고서|이번 전체 회귀|
|23|최종 보고|PARTIAL|이 문서는 초기 감사임|최종 매트릭스/결과표|

## 확인된 선행 결함

- Area 01, Seed 2026/92137: fallback 성공으로 표시하지만 `RogueMainPath` 끝은 r_04, `RogueFinalRoomId`는 r_05. 실패한 시도의 MainPath가 남고 fallback은 별도 방을 최종으로 지정한다. 현재 Validate는 이를 검출하지 않는다.
- 초기 몬스터 좌표는 `RoomSpawner.SpawnOne`에서 `_UtilLogic:RandomDouble()`을 사용한다. 그래프 동일성만으로 초기 Layout 전체 재현성을 인증할 수 없다.

## 작업 순서

- [x] 이전 보고서/원본 코드/실제 Maker 생성 감사
- [ ] 생성/fallback/초기 배치 오류 수정 및 동일 Seed 재검증
- [ ] Area 전수 실제 시작/이동/목표/종료
- [ ] 66 Skill/쿨다운/지형/슬롯 예외
- [ ] UI/저장/권한/협동/성장 비활성
- [ ] 전체 회귀와 최종 상태표
