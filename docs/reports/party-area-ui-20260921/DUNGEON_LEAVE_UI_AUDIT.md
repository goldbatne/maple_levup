# 던전 나가기 UI 감사

## UI 위치

전투 HUD 우측 상단의 `RUN` 메뉴에 `던전 나가기`를 배치했다. 전투 화면에 별도 대형 나가기 버튼은 추가하지 않았다.

## 확인창

- 제목/행동: 현재 Run 포기
- 안내: 이번 Run의 능력과 진행 상태가 사라짐
- 버튼: `나가기`, `취소`
- 확인 단계: 1회

## Runtime 결과

| 시나리오 | 판정 | 결과 |
|---|---|---|
| Run 메뉴 열기 | PASS_RUNTIME | 메뉴 정상 표시 |
| 확인창 열기 | PASS_RUNTIME | 마스크/버튼 표시 |
| 취소 | PASS_RUNTIME | 확인창 및 마스크 제거, Run active 유지 |
| 다시 열기 | PASS_RUNTIME | 중복 패널 없이 정상 표시 |
| 나가기 확정 | PASS_RUNTIME | `ABANDONED`, InstanceRoom 종료, 로비 복귀 |
| 다음 Run | PASS_RUNTIME | 슬롯/pending/objective 초기화, HP 기본값 복구 |
| Clear 기록 방지 | PASS_STATIC + Runtime state | ABANDONED 분기에서 Clear 보상/기록 경로 미실행 |
| Boss 전투 중 호출 가능 | PASS_STATIC | 위치/Objective/Boss 조건 없이 요청 가능 |
| 개인 이탈로 파티 해체 방지 | PASS_STATIC/SERVER_SIM | 파티와 Run participant 상태 분리 |

## 정리 대상

- Monster Respawn scheduler
- Skill Supply/legacy timer
- Pending spawn/event
- OwnedSkillPool 및 Battle SkillBar
- HP와 임시 상태
- Potion Run 상태
- Boss/Objective/Portal/Run Graph
- Run Effective Damage
- InstanceRoom 참가 상태
- 열려 있는 Skill Window/Popup/Toast

## 경쟁 상태

서버가 Run/참가자 최종 상태를 한 번만 확정한다. 이미 Clear된 Run을 ABANDONED로 덮어쓰지 않고, 이미 이탈한 참가자는 이후 Clear 보상 대상에 재포함하지 않는다.

## 증거 이미지

- `evidence/dungeon_run_menu.png`
- `evidence/dungeon_leave_confirm.png`
- `evidence/dungeon_leave_cancelled.png`

