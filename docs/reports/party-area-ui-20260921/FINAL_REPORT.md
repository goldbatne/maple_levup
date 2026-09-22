# 로그라이트 Area 선택·파티 입장·던전 나가기 최종 보고

- 대상 프로젝트: `D:/maplestory_levup`
- 검증일: 2026-09-21 (KST)
- 범위: Area 선택 UI, 명시적 파티 구성, Run 입장 조건, Run 메뉴의 던전 나가기, Run 상태 정리
- 비범위: 신규 게임 기획, 스킬/밸런스 변경, 실제 2~4개 독립 클라이언트 동시 실행

## 결론

싱글 플레이의 Area 선택 → Run 시작 → 던전 나가기 취소 → 던전 나가기 확정 → 로비 복귀 → 다음 Run 초기화 흐름을 Maker Runtime에서 확인했다. Area 선택 화면은 왼쪽의 MEGA 1~5 목록과 오른쪽의 Run 옵션(일반/몬스터 스킬, Solo/Party, 준비/시작)으로 분리했다.

파티는 근처 플레이어 자동 합류가 아니라 생성·참가 코드 기반의 명시적 상태로 관리한다. 파티 최대 인원은 4명이고 파티 Run은 2~4명 및 전원 준비를 요구한다. 2/3/4인 서버 상태 시뮬레이션은 통과했으나, 현재 Maker에 독립 클라이언트를 동시에 띄울 수 있는 실행 수단이 없어 실제 멀티클라이언트 Runtime은 `BLOCKED_RUNTIME_MULTIPLAYER`다.

## 구현 요약

- Area 선택: `MEGA 1`~`MEGA 5`만 선택 목록에 노출
- Run 옵션: `일반` / `몬스터 스킬`, `Solo` / `Party`
- 파티: 생성, 참가 코드, 나가기, 해체, 리더 위임, 리더 Area/모드 선택, 전원 준비
- 파티 Run: 2~4명, 전원 준비 완료, 리더만 시작 가능
- 파티 유지: Run 종료 또는 개인 던전 나가기와 파티 탈퇴를 분리
- 던전 나가기: 우측 상단 `RUN` 메뉴 → 확인창 → `ABANDONED`
- 정리: InstanceRoom, 슬롯, pending, HP/임시 상태, Objective/Boss/Portal/Graph/Damage 상태 정리
- 다음 Run: 새 seed, 빈 슬롯, 빈 pending, 기본 HP, Objective 미완료 상태 확인

## 실제 Runtime 결과

| 항목 | 결과 | 근거 |
|---|---|---|
| Maker Refresh | PASS | 변경 엔트리 재로딩 성공 |
| Build | PASS | Error 0; 기존 모델 경고 2건만 유지 |
| Area 선택 화면 | PASS_RUNTIME | `evidence/area_select_solo.png`, `area_select_normal.png`, `area_select_monster_skill.png`, `area_select_party.png` |
| 파티 창 1인 상태 | PASS_RUNTIME | `evidence/party_window.png` |
| 1인 파티 Run 시작 차단 | PASS_RUNTIME | 실제 1인 파티에서 시작 거부 확인 |
| 던전 나가기 취소 | PASS_RUNTIME | `evidence/dungeon_leave_cancelled.png`, `[QA_CANCEL] active=true;confirm=false` |
| 던전 나가기 확정 | PASS_RUNTIME | `[RogueAbandon] ABANDONED ... remaining=0 moved=1` |
| 로비 복귀 | PASS_RUNTIME | Instance context 종료 후 `server_main/client`만 유지 |
| 다음 Run 초기화 | PASS_RUNTIME | `[QA_NEXT_RUN] active=true;slots=0;pending=0;hp=1000/1000;objective=false` |
| 2P 파티 상태 | PASS_STATIC/SERVER_SIM | `members=2`, `hpScale=1.25`, leader/ready/snapshot/abandon PASS |
| 3P 파티 상태 | PASS_STATIC/SERVER_SIM | `members=3`, `hpScale=1.50`, leader/ready/snapshot/abandon PASS |
| 4P 파티 상태 | PASS_STATIC/SERVER_SIM | `members=4`, `hpScale=1.75`, leader/ready/snapshot/abandon PASS |
| 2~4P 실제 동시 실행 | BLOCKED_RUNTIME_MULTIPLAYER | Maker 실행 컨텍스트에 독립 클라이언트 1개만 제공 |

## 파티 상태 규칙

- 파티 생성/가입은 서버 권한 RPC로 확정한다.
- 리더만 Area와 Run 모드를 바꾸고 Run을 시작한다.
- 리더를 포함한 모든 참가자가 준비해야 시작할 수 있다.
- 개인이 던전을 나가도 파티 소속은 유지되며, 해당 플레이어의 Run 참가 상태만 정리한다.
- 마지막 Run 참가자가 이탈할 때 공유 InstanceRun을 정리한다.
- 파티 탈퇴/해체는 별도 명시적 동작이다.

## 던전 나가기 결과

확인창의 `취소`는 마스크와 입력 차단을 해제하고 전투 상태를 유지한다. `나가기`는 `ABANDONED`로 처리하며 Clear/Boss Clear/영구 보상을 기록하지 않고 결과 화면을 강제하지 않는다. Run 관련 UI도 닫고 `maptown`으로 복귀한다.

## 수정 파일

- `RootDesk/MyDesk/GameData/GameData.mlua`
- `RootDesk/MyDesk/UI/AreaSelectPanel.mlua`
- `ui/AreaSelect.ui`
- `ui/PlayerHud.ui`
- `docs/tools/rebuild-party-area-ui.cjs`
- `docs/reports/party-area-ui-20260921/*`

## Build / Runtime

- Build Error: 0
- 기존 경고: 마노 `MovementComponent.InputSpeed`, 보우마스터 `MonsterAttack.AvatarAttackPlayRate`
- 최종 확인 시 신규 Runtime Error: 0

## BLOCKED

실제 2P/3P/4P 독립 클라이언트 동시 실행은 현재 Maker 도구가 단일 클라이언트 컨텍스트만 제공해 수행하지 못했다. 서버 파티 상태와 HP 배율은 시뮬레이션으로 검증했지만 실제 네트워크 동기화 PASS로 간주하지 않는다.
