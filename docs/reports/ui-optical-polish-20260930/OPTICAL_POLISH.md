# FINAL UI — Optical Polish

기준: `../ui-final-alignment-20260929/FINAL_UI_BASELINE.md` (`ui-final-alignment-20260930`). 원본 `D:/maplestory_levup`, 2026-09-30 KST. 기존 미커밋 변경을 보존했으며 commit/push하지 않았다. 새 스타일이나 전체 좌표 감사는 수행하지 않았다.

## 적용한 최소 보정

- 상단 보유/정수/코어와 선택 몬스터 누적 처치를 같은 Y baseline에 배치했다. 기존 표시 코드가 숨기던 누적 처치 caption을 Collection에서만 표시했다.
- HP/공격 label과 value의 두 열을 동일하게 맞추고, 묶음의 중심을 오른쪽 상세 중심에 맞췄다. 작은 label/value의 글자를 소폭 조정했다.
- 고유 능력 이름을 UI 단위 4만큼 아래로 조정하고 설명의 높이/중앙 정렬/글자 크기를 소폭 조정했다. 아이콘/박스 위치는 그대로다.
- 화면의 대표 16칸과 동행 3칸에서는 명백한 sprite 치우침을 발견하지 못했다. per-monster offset을 추가하지 않았다. 101종 모든 프레임의 optical center를 전수 검증했다는 뜻은 아니다.
- 이름/Lv 위치, 성장 버튼과 비용, 동행 3슬롯은 이미 균형적이어서 변경하지 않았다.

MSW UIBuilder 및 클라이언트 표시 어댑터 지침을 적용했다. 실제 변경은 `ui/EquipWindow.ui`, `RootDesk/MyDesk/UI/EquipPanel.mlua` 두 파일뿐이다. 기준 manifest의 다른 12파일 hash는 작업 시작과 동일하다. 전체 창 크기, Grid/Scroll, 버튼/비용/편성 bounds, 색상/프레임 규칙, 다른 UI와 게임 로직은 변경하지 않았다. UIBuilder가 수정한 stat 노드의 오래된 Transform 보조 필드도 정규화했으며 실제 위치는 anchoredPosition으로 확인했다. 구체적인 before/after는 `OPTICAL_FINAL_MANIFEST.json` 참조.

## 육안 spot check

| 화면 | 확인 | 결과/제한 |
|---|---|---|
| Lobby | 새 Maker Play에서 창 닫기 및 Run 포기 후 로비 화면 | 표시 PASS |
| Monster | 실제 보유 달팽이 Lv10/+3, 4열 대표 스프라이트, 3편성 | 상단/상세/비용/편성 정렬 PASS |
| Adventure | 실제 선택 UI | 기존 구조 유지, 명백한 잘림/경계 접촉 없음 |
| Party | 실제 Solo 파티창 | 정렬 PASS; 멀티 검증 아님 |
| Shop | 실제 상품 목록, 구매하지 않음 | 정렬 PASS; 기존 DEV TEST 표시 유지 |
| Run HUD | 실제 NORMAL Run; 서버 뷰 재전달 후 | 광학 정렬 PASS / 자동 진입 상태 전달 PARTIAL, 아래 참조 |
| Run Skill | 새 세션 empty 표시 + 기준본 filled 스크린샷 재검토 | 표시 PASS; 이번 세션 능력 지급 안 함 |
| Run Upgrade | 새 세션 empty 표시 + 기준본 filled QA_SCREEN 재검토 | 표시 PASS; 강화 지급 안 함 |
| Result | 기준본 CLEAR/FAIL QA_SCREEN 재검토 | 표시 검토만; 이번 세션 실제 CLEAR/FAIL NOT_RUN |

기존 컨트롤러를 Maker Execute Script로 열어 확인했다. 마우스로만 모든 흐름을 검증한 것은 아니다. 기준본의 이미지를 다시 본 항목은 신규 Runtime 재현으로 집계하지 않았다. 확인한 화면에서 새 text 잘림/Border 중첩을 발견하지 못했다. 모든 데이터 길이/상태를 보증하지 않는다.

## 별도 발견: Run 표시 상태 전달

01:56:44 client: `gameRun=false slotRun=true map=map001`.
01:58:01 instance server: `active=true result=ACTIVE`.
목표/HP/Companion HUD가 누락된 상태였다. 01:58:14 기존 서버 메서드 `BroadcastRogueliteView()`를 호출하여 실제 권한 상태를 다시 보낸 후 HUD가 정상 표시됐다. 임의 active 값이나 보상/전투 데이터를 넣지 않았다.

따라서 `run_hud_after_optical.png`는 **서버 뷰 재전달 후 실제 Run HUD**이며, 자동 Run 진입 회귀가 무조건 PASS라는 증거가 아니다. 상태 전달 경합의 정확한 원인은 이번 광학 마감에서 확정하지 않았다. 관련 GameData/Run HUD 파일은 작업 시작 hash와 동일하며 이번에 수정하지 않았다. 이 문제는 별도 기능 확인 사항으로 남긴다. 정상 ABANDON 요청으로 로비에 복귀했고 02:00:32 `map=maptown active=false` 확인했다.

## Build / Runtime

- Stop → Refresh → Maker Build 로그 확인 → 새 Play 수행.
- Build Error **0**, Warning **4** (기존 RunChest ColliderType/CircleRadius, 마노 InputSpeed, 보우마스터 AvatarAttackPlayRate). 50개 Info를 Error로 집계하지 않았다.
- **2026-09-30 01:50 이후 새 Optical 검증 구간, 02:00:32 종료까지 Runtime Error 0**, Runtime Warning **73**. 과거 누적 Console 전체가 오류 0이었다는 뜻이 아니다.
- 기존 Trigger Legacy, RoomPortal/TownGate, RoomBounds 유형 경고가 재발했다. 새 UI 경고 유형을 확인하지 못했다. 경고 0이라고 보고하지 않는다. `session-evidence.json`에 이 구간 증거 보존.
- UI lint: 수정 전/후 각각 Error 0, Warning 5072, Info 249. 기존 대규모 경고를 이번 범위에서 전체 수정하지 않았다.
- `git diff --check`: PASS.
- 이번 도구 orchestration JS의 괄호 오타 1회는 재호출로 수정했다. Maker Runtime 오류와 구분한다.

## 비교 이미지 (각 844×475)

- `monster_before_optical.png`: 수정 전, 같은 달팽이 선택.
- `monster_after_optical.png`: 수정 후, 같은 보유/성장/편성 상태.
- `run_hud_after_optical.png`: 위 서버 뷰 재전달 후.
- `shop_after_optical.png`: 새 세션, 상품/가격/구매 동작 변경 없음.

요청된 보고서용 캡처는 이 4장만 보관한다. 기존 증거는 삭제하지 않았다. Maker 자체 screenshot 임시 파일은 도구가 생성한 것으로 별도 보고서에 다량 복제하지 않았다.

## 종료

시각적 Optical Polish는 이 상태로 FINAL 고정하고 추가 스타일/정렬 패스를 시작하지 않는다. 단, 자동 Run 진입 HUD 상태 전달의 PARTIAL을 포함해 전체 UI 동작이 무결하다고 선언하지 않는다. 이번 범위를 넘는 기능 수정은 수행하지 않았다.
