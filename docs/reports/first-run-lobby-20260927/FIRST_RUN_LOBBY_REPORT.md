# 최초 실행·로비 흐름 점검 (2026-09-27)

대상: `D:/maplestory_levup`. 이 보고서는 변경·검증 결과이며 Fresh 계정 또는 레거시 RPG 저장의 실제 런타임 검증을 대신하지 않는다.

## 원인과 수정

- 기본 입장 설정 `Global/defaultuserenterleavelogic.logic`이 삭제된 `/maps/map01`을 가리켰다. 존재하는 `/maps/maptown`으로 변경했다. Maker의 편집 맵에서 시작하는 Play와 배포 첫 접속은 동일한 시험이 아니므로, 배포 Fresh 시작의 최종 보장은 미검증이다.
- `PlayerDBManager.mlua`는 기존부터 로그라이트 모드에서 RPG `Run.current_room` 복원을 건너뛰고 별도 `RoguelitePermanentV1` 저장을 읽는다. 이 경로는 수정하지 않았다. Maker 테스트 저장은 `MakerTest_RoguelitePermanentV1`로 분리된다.
- `RoomProgressHud.mlua`는 실제 Run 활성 상태·플레이어 슬롯 상태·현재 맵을 확인한 뒤에만 목표를 표시한다. 로비에서는 숨긴다.
- `SkillBar.mlua`는 Run 전/종료 후 빈 전투 슬롯과 획득 오버레이를 숨긴다. Active Run에서는 기존 5칸을 복구한다.
- `EquipPanel.mlua`는 로비의 레거시 `스킬` 버튼을 숨기고, Run 중 보유 능력 창만 사용할 수 있게 한다.
- 신규 모드에서 레거시 Stat/Inventory/Trait/WorldMap, Rebirth/Goddess NPC 비활성화는 기존 코드와 Maker 로그로 확인했다. 저장 데이터와 레거시 코드는 삭제하지 않았다.

## 실제 Maker 확인

| 항목 | 결과 | 근거 |
|---|---|---|
| 기존 테스트 저장 시작 | PASS_RUNTIME | `maptown`, `MakerTest_RoguelitePermanentV1` 로드, 레거시 방 복원 생략 로그. [`existing_profile_lobby.png`](existing_profile_lobby.png) |
| 로비 HUD | PASS_RUNTIME | Run 목표·Boss HP·빈 SkillBar·레거시 스킬 버튼 미표시. |
| Mega Area 선택창 | PASS_RUNTIME | 실제 방향키 이동으로 TownGate에 닿아 열림. [`area_select.png`](area_select.png) |
| Run 시작 | PARTIAL_RUNTIME | UI의 `StartSelectedRun()` 콜백을 Maker 실행 스크립트로 호출. 엔진 UI 버튼 실제 클릭은 Maker MCP가 지원하지 않아 검증하지 못함. `mega_01`, NORMAL, seed `796643`, 참가자 1명, Instance 생성. [`run_entry.png`](run_entry.png) |
| 자동공격 | PASS_RUNTIME | 실제 이동·전투에서 0.55초 주기, 기본공격 36 damage 로그. [`first_combat.png`](first_combat.png) |
| Skill Drop | PASS_RUNTIME | `m_skeleton_commander` 처치 후 World Drop, 실제 E 입력으로 `s_mon_skeleton_commander` 획득 성공 로그. |
| Portal 이동 | PASS_RUNTIME | 실제 방향키 이동으로 map001→map004→map003 진행. |
| Fail 후 로비 | PASS_RUNTIME | 전투 사망, `RUN_FAILED` 정리, `maptown` 복귀, HP 1000/1000, Run UI 미표시. [`return_to_lobby.png`](return_to_lobby.png) |
| Dungeon Leave 후 로비 | PARTIAL_RUNTIME | `ConfirmRogueliteAbandonUi()` 스크립트 호출로 ABANDONED 정리·maptown 복귀 확인. UI 버튼 실제 클릭은 미확인. |
| Build | PASS | Maker build log: Error 0, Warning 2(마노 InputSpeed, 보우마스터 AvatarAttackPlayRate). |
| 최종 Play Runtime | PASS_WITH_WARNINGS | 최종 maptown 세션에 신규 Error 0. Town portal Legacy Trigger/RoomBounds 관련 Warning은 남음. 과거 실험에서 발생한 오류는 누적 콘솔에 남아 있어 전체 콘솔 Error 0을 주장하지 않음. |

## 미검증 및 제한

- `fresh_start_lobby.png`: **미제공**. 임시 격리 저장 키로 2회 시험했지만 Maker가 수정된 키 대신 기존 `MakerTest_RoguelitePermanentV1`을 계속 로드했다. 원래 소스로 복귀했으며 새 계정 시작을 PASS로 세지 않았다.
- `legacy_save_start.png`: **미제공**. 실제 구 RPG 위치를 담은 격리 저장 프로필을 Maker에서 생성·선택할 수 없어 레거시 저장 시작은 정적 코드 확인만 했다. 기존 저장 삭제나 덮어쓰기는 하지 않았다.
- Run 상자는 생성 로그(`REGISTER`, `AVAILABLE`)와 종료 시 정리는 확인했다. 추가 자연 이동 시험에서 상자가 있는 `map006`까지 도달했으나 상자에 접근하기 전에 전투 사망했다. 따라서 Chest Open Regression은 **NOT_RUN**이다.
- Boss Kill Clear 및 Boss HUD의 실제 전환은 이번 세션에서 **NOT_RUN**이다.
- Active Run의 모든 레거시 UI 열기 경로와 배포된 Fresh 계정의 첫 접속은 이번 Maker Play만으로 완전 검증되지 않았다.

## 스크린샷

- 수정 전 로비: [`lobby_before.png`](lobby_before.png)
- 기존 테스트 저장 로비: [`existing_profile_lobby.png`](existing_profile_lobby.png)
- 선택창: [`area_select.png`](area_select.png)
- Run 시작: [`run_entry.png`](run_entry.png)
- 첫 전투: [`first_combat.png`](first_combat.png)
- Fail 후 로비: [`return_to_lobby.png`](return_to_lobby.png)

Git commit/push는 수행하지 않았다. 일시적인 테스트 저장 키 변경은 모두 되돌렸다.
