# 로그라이트 개편 원본 병합 및 Maker 런타임 검증 보고

- 대상 프로젝트: `D:/maplestory_levup`
- 기준 baseline: `skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`
- 기준 커밋: `2eb7498eda8f53440648ef6107d6c933ba55d5c6`
- 작업 브랜치: `codex/art-packages-cleanup-20260915`
- 개편 원본: `C:/Users/dddd/.codex/visualizations/2026/08/30/01a05014-afc4-7e12-839e-e3f24707e98b/roguelite-rework`
- 최종 실행 프로젝트: `D:/maplestory_levup`
- 검증일: 2026-09-21 KST

## [원본에 병합한 파일]

작업본의 23개 변경 파일을 원본의 대응 파일과 SHA-256으로 먼저 대조했다. 병합 직전 원본은 기록된 baseline 해시와 23/23 일치했으며, 각 파일의 원본은 `premerge/` 아래에 보존한 뒤 개편본을 반영했다.

1. `RootDesk/MyDesk/PlayerAttack.mlua`
2. `RootDesk/MyDesk/PlayerHit.mlua`
3. `RootDesk/MyDesk/Combat/RoomMonster.mlua`
4. `RootDesk/MyDesk/GameData/GameBalance.csv`
5. `RootDesk/MyDesk/GameData/GameData.mlua`
6. `RootDesk/MyDesk/Player/PlayerStats.mlua`
7. `RootDesk/MyDesk/Progress/PlayerCollection.mlua`
8. `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`
9. `RootDesk/MyDesk/Room/RoomPortal.mlua`
10. `RootDesk/MyDesk/Room/RoomSpawner.mlua`
11. `RootDesk/MyDesk/Save/PlayerDBManager.mlua`
12. `RootDesk/MyDesk/Save/SavePermanentData.mlua`
13. `RootDesk/MyDesk/UI/AreaSelectPanel.mlua`
14. `RootDesk/MyDesk/UI/EquipPanel.mlua`
15. `RootDesk/MyDesk/UI/GoddessPanel.mlua`
16. `RootDesk/MyDesk/UI/InventoryPanel.mlua`
17. `RootDesk/MyDesk/UI/ItemQuickSlotBar.mlua`
18. `RootDesk/MyDesk/UI/PlayerHud.mlua`
19. `RootDesk/MyDesk/UI/RebirthConfirmPanel.mlua`
20. `RootDesk/MyDesk/UI/RoomProgressHud.mlua`
21. `RootDesk/MyDesk/UI/SkillBar.mlua`
22. `RootDesk/MyDesk/UI/StatPanel.mlua`
23. `RootDesk/MyDesk/UI/WorldMapPanel.mlua`

원본 환경 통합 과정에서 `RootDesk/MyDesk/MonsterAttack.mlua`도 신규 Run 기본 방어력 적용을 위해 최소 보완했다. Area Run에 쓰이는 159개 `.map`은 `IsInstanceMap=true`로 전환했으며, 파일 수정에 그치지 않고 Maker에서 159개 전부 열기/저장을 수행해 내부 맵 레지스트리도 동기화했다. 실패 맵은 0개다.

병합/검증 보조 산출물:

- `docs/tools/enable-roguelite-instance-maps.cjs`
- `docs/tools/set-area-instance-mode.cjs`
- `docs/reports/roguelite-merge-20260921/INSTANCE_MAP_MIGRATION.json`
- `docs/reports/roguelite-merge-20260921/rework-plan/`

## [병합 충돌 및 처리]

- 원본 23개 파일은 기록된 baseline과 모두 일치해 텍스트 충돌 없이 병합했다.
- 원본 작업 트리의 다른 미커밋 변경은 reset/revert하지 않았다.
- `GameBalance.csv`가 Refresh 중 Mislocated로 이동한 문제는 백업 후 원래 경로로 복구했고, Run 핵심 설정에는 안전한 fallback을 추가했다.
- Maker에서 파일의 `IsInstanceMap=true`만으로는 내부 등록값이 갱신되지 않아 Area 00의 `map002`에서 `[LEA-3002] instance map` 오류가 발생했다. 159개 대상 맵 전부를 Maker에서 열고 저장하여 해결했다.
- 구 세이브의 로그라이트 영구 필드가 table이 아닌 값인 경우 `ApplyPerm`이 중단되는 문제를 실제 재접속에서 발견했다. `SavePermanentData`와 `PlayerDBManager`에 타입 가드를 추가해 구 저장값을 안전하게 빈 표로 취급했다.
- 새 Run 입장 직후 레거시 RPG의 `current_room=map005`가 복원되어 시작방을 덮어쓰는 문제를 발견했다. 로그라이트 모드에서는 레거시 방 값을 보존하되 이동·방 기록에는 사용하지 않도록 분리했다.
- 완료 목표는 `RoomMonster.Dead -> GrantRunKillRewards -> OnRunMonsterDefeated` 한 경로에서만 진행하도록 중복 콜백을 제거했다.
- 신규 cross-component 메서드 메타데이터가 준비되지 않은 세션에서 nil 호출이 발생하던 완료/정리 경로는 이미 존재하는 속성 기반 처리로 정리했다.

## [Maker Refresh 결과]

- 최종 프로젝트 `D:/maplestory_levup`에서 Refresh 성공.
- Area 00 8개 맵과 나머지 151개 맵, 합계 159개를 Maker에서 직접 열고 저장했다.
- Area 00 실제 InstanceRoom 생성 성공 후 Area 01도 별도 Seed로 교차 검증했다.
- Refresh 뒤 `GameBalance`는 정상 원위치에 있고 Mislocated 사본은 실행 원본으로 사용되지 않는다.

## [Build 결과]

- 최종 Build Error: **0**
- Build Warning: **2**
  - `model://mano`의 `MovementComponent.InputSpeed`
  - `model://bowmaster`의 `MonsterAttack.AvatarAttackPlayRate`
- 두 Warning은 이번 로그라이트 병합 전부터 존재한 모델 설정 경고이며 컴파일을 막지 않는다.

## [Solo Runtime 결과]

- `maptown`에서 1인 준비 후 실제 `CreateInstanceRoom` 경로로 Run 시작 성공.
- 생성 컨텍스트: `server_instance_rogue~area_00~424242~1~20372000905997288`
- `participants=1`, `moved=1` 확인.
- Run HP는 1000/1000, 기본 공격은 신규 Run ATK 35를 사용함을 로그로 확인.
- 실제 자동 기본 공격으로 달팽이를 처치했고, 처치 로그와 능력 획득 로그가 이어졌다.
- 완료 후 `maptown` 복귀를 화면으로 확인했다.
- 다음 Run은 레거시 저장방이 아니라 `map001`에서 시작하도록 수정 후 재검증했다.

화면 근거:

- Area 00 실제 인스턴스 시작/획득: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260921_010947_389.png`
- Area 00 최종 목표방: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260921_011244_412.png`
- Area 00 클리어 후 로비: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260921_011319_831.png`
- Area 01 교차 검증: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260921_014241_733.png`

## [절차생성 Runtime 결과]

- Area 00, Seed `424242`: 2회 시도 후 PASS.
- 주 경로: `r_001 > r_002 > r_004 > r_005`, 가지 2개.
- 동일 Seed를 다시 초기화했을 때 같은 경로가 재현됐다.
- 다음 Run Seed `777777`: `r_001 > r_003 > r_002 > r_005`, 가지 1개.
- 수정 후 Seed `888888`: `r_001 > r_003 > r_006 > r_007 > r_002 > r_005`, 가지 0개. 첫 맵 `map001` 확인.
- Area 01, Seed `999999`: 1회 시도 PASS, `r_01 > r_04 > r_02 > r_05`, 가지 0개.
- Area 00과 Area 01 모두 실제 InstanceRoom 컨텍스트 생성과 `valid=true`를 확인했다.

## [스킬 획득/고정 슬롯/쿨다운 결과]

- 실제 달팽이 처치 후 `s_mon_snail_dew_trail`이 1번 빈 슬롯에 장착됐다.
- 슬롯은 사용 후 유지됐다.
- 첫 사용 성공, 0.35초 뒤 재요청은 `4.7초 남음`으로 차단, 5.5초 뒤 재사용 성공을 확인했다.
- 5칸을 채운 뒤 6번째 `s_mon_mushmom`은 pending 후보가 되었고, 2번 슬롯의 `s_mon_red_snail`과 명시적으로 교체됐다.
- `s_mon_mano` 후보는 포기 처리됐다.
- 같은 `s_mon_snail_dew_trail` 재획득은 이미 장착된 중복으로 거부되어 동일 SkillID 중복 장착이 발생하지 않았다.
- 랜덤 5초 공급 및 사용 시 슬롯 소비는 실행되지 않았다.

## [Objective/Clear 결과]

- 실제 InstanceRoom의 `map005` 최종 목표방에서 보스 마노 1개체 스폰과 보스 HUD를 확인했다.
- 보스 사망 처리 후 다음 로그를 확인했다.
  - `완료 후처리 시작 participants=1`
  - `완료 참가자 처리`
  - `Area 클리어 기록 area_00`
  - `COMPLETE area=area_00 seed=424242`
- InstanceRoom이 종료되고 사용자가 `maptown`으로 복귀했다.
- 다음 Run 직전 `active=false`와 슬롯 정리를 확인했다.
- 별도 Seed Run에서 `OnRunPlayerDied` 실제 서버 경로를 호출해 `FAILED — 전원 사망/이탈`과 전투 상태 정리를 확인했다.

## [멀티 Runtime 결과]

- Maker에서 사용 가능한 실제 클라이언트는 1개뿐이었다.
- 서버 컨텍스트는 `server_main + client + server_instance_*`까지 확인했으나, 2~4개의 독립 클라이언트를 동시에 만들 수 없어 실제 협동 플레이는 실행하지 않았다.
- 정적 구현에는 1~4인 준비, 시작 인원 고정, 개인 슬롯/쿨다운, 참여자별 획득 기회, HP 배율 `1 + 0.25 * (인원-1)`가 존재한다. 이는 실제 멀티 통과를 의미하지 않는다.

## [FAIL]

- 필수 Solo Run 경로에서 남은 런타임 Error는 확인되지 않았다.
- 최종 Build Error는 0이다.
- 단, 기존 상단 `스탯/스킬/가방` 버튼의 시각 요소 일부가 여전히 보인다. 관련 성장 패널 기능은 신규 모드에서 비활성화되어 있으나 최종 HUD 정리 항목으로 남는다.

## [NOT_RUN]

- 2인, 3인, 4인 실제 멀티클라이언트 동시 플레이.
- 협동 중 일부 사망 후 안전 지점 재합류, 연결 끊김 유예, 재접속 복귀.
- Area 02~20 각각의 전체 시작→목표→클리어 플레이. 맵 레지스트리는 159개 모두 동기화했지만 실제 인스턴스 교차 실행은 Area 00과 Area 01만 수행했다.
- 모든 기존 플레이어 스킬의 새 지형 충돌/관통/VFX 전수 실행. 이번 병합에서는 달팽이 획득 스킬과 고정 슬롯·쿨다운 경로를 대표 검증했다.

## 최종 상태

별도 작업본은 참고/복원용으로만 남아 있으며 최종 실행 프로젝트가 아니다. Maker가 읽고 실행한 프로젝트는 `D:/maplestory_levup`이다. 분석 baseline과 병합 전 파일은 보고서/백업 폴더에 보존되어 있다.
