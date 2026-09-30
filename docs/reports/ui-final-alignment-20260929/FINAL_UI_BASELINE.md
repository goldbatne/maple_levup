# FINAL UI BASELINE — 정렬 마감

- 기준 ID: `ui-final-alignment-20260930`
- 대상: `D:/maplestory_levup` 원본. 별도 작업본 없음.
- 검증 해상도: **844×475**. 저장한 28개 PNG의 실제 크기 확인.
- 브랜치: `codex/monster-taming-meta-20260927`
- HEAD: `c68d379e14d921526dc87053c99f14f9ed5ef984`
- 미커밋 변경이 있는 작업 트리 기준이다. 이전 작업의 변경을 포함하며 새 커밋을 뜻하지 않는다.
- 14개 UI/표시 어댑터 파일의 최종 SHA256: `FINAL_UI_BASELINE_MANIFEST.json`.

## 범위와 결과

승인된 Monster Collection 스타일과 화면 구조를 유지했다. 수정 범위는 좌표·크기·padding·텍스트 정렬·표시 레이어·기존 프레임의 종횡비·짧은 알림 문구다. 게임 규칙, 보상, 가격, 구매, 저장, AI, 스킬 효과, 공급, 포탈 로직은 변경하지 않았다. commit/push 하지 않았다.

`ALIGNMENT_AUDIT.csv`에는 실제 변경 94행만 기록했다. UI 좌표는 1920×1080 기준의 UI 단위이며 844×475 화면에서는 약 0.44배다. 그룹 행의 0 좌표는 좌표가 없는 속성 변경 또는 각 요소의 기존 Y를 유지한 X-only 변경을 뜻한다. 크기·padding·anchor 변경은 ChangeReason을 함께 읽어야 한다. 원본 before/after 값은 `alignment_*_changes.json`에 보존했다. 모든 값이 물리 화면 px라는 뜻은 아니다.

### 주요 수정

- Run 우상단 메뉴를 같은 baseline과 간격으로 맞추고 MSW 기본 메뉴를 피했다.
- Collection 우측 몬스터·텍스트·강화 버튼·비용 축을 맞췄다. 좌측 4열과 하단 3편성 구조는 유지했다.
- Collection/Run Skill이 공유하는 native Grid의 cell geometry 캐시와 anchor 재계산 때문에 생긴 겹침을 표시 어댑터에서 수정했다. Run의 미사용 UI cell은 레이아웃에서 제외하고 Collection 복귀 시 101칸을 복원한다.
- Run Skill 아이콘/이름, 선택 상세 이미지/설명, 하단 슬롯의 padding과 간격을 정리했다.
- Solo 모험 시작 CTA를 중앙에 맞췄다. Party 행/조작 버튼, Shop 상품 2·3의 이름/메타 시작 X를 통일했다.
- Companion portrait가 배경에 가려지던 표시 순서를 수정했다.
- Drop의 기존 39×100 프레임 스프라이트를 44×44 표시 크기에 맞췄다. 월드 위치와 획득 판정은 그대로다.
- Boss 무제한시간 이름을 HP 바 중앙에 맞췄다. Result는 초상화가 없을 때 본문도 중앙으로 온다.
- 확인창 ×, 전체 dim, popup 레이어, native 버튼의 중복 bevel을 정리했다.
- Ability Toast를 Boss HUD 아래로 옮겨 약 8px 간격을 확보하고 긴 획득 문구 잘림을 줄였다.

## 20개 범주 육안 확인

| 범주 | 증거 | 확인 방식/제한 |
|---|---|---|
| Lobby | 01_lobby.png, 17_return_lobby.png | 실제 로비, 정상 창 닫기 후 복귀 |
| Monster Collection | 02_monster.png | 실제 보유 데이터; 4열 정렬 |
| Monster Detail | 02_monster.png | 달팽이 선택, 이름/레벨/비용/능력 |
| Companion Formation | 02_monster.png | 기존 3편성 표시; 편성 변경 없음 |
| Adventure | 03_adventure.png | Solo 지역 선택 UI, CTA 중앙 |
| Party | 04_party.png, 04_party_4p_QA_SCREEN.png | Solo 실제 / 4인 표시 fixture. 멀티 실행 아님 |
| Shop | 05_shop.png | 기존 상품 표시, 구매/선택권 사용 없음 |
| Run HUD | 06_run_hud.png | 실제 시작한 Run 화면 |
| Random 5 SkillBar | 06_run_hud.png, 08_run_skill_filled.png | 빈칸/획득 후 표시, 동일 슬롯 geometry |
| Companion Status | 06_run_hud.png | portrait 표시 순서, 3칸 크기 |
| Run Skill Window | 07_run_skill_empty.png, 08_run_skill_filled.png | 실제 Run UI, empty/filled, native Grid 캐시 수정 확인 |
| Run Upgrade | 09_run_upgrade_empty.png, 09_run_upgrade.png | Empty 실제; Filled 3행 QA_SCREEN 표시-only. 강화 보상 지급 없음 |
| World Skill Drop | 10_skill_drop.png | 기존 QA spawn 경로로 생성한 drop; 실제 E 입력 획득. 자연 처치 드롭이라고 주장하지 않음 |
| Boss HUD | 11_boss.png | QA_SCREEN client 표시 fixture; 실제 Boss 전투 아님 |
| Result | 12_result.png, 12_result_fail_QA_SCREEN.png | CLEAR/FAIL QA_SCREEN; 보상/클리어 기록 변경 없음. ABANDON은 정상 요청으로 로비 복귀, 결과창 강제 표시 없음 |
| Confirm Modal | 13_modal.png | 기존 확인창, 전체 dim/닫기/버튼 간격 |
| Generic Popup | 14_generic_popup_QA_SCREEN.png | 기존 native popup 표시 preview, Run Skill보다 앞 |
| Toast | 15_toast_boss_QA_SCREEN.png, 18_native_toast_QA_SCREEN.png | Boss+Toast 합성 상태 및 기존 ToastGroup 표시 preview |
| Close Button | 02/03/04/05/07/09/13 | 공통 크기·padding, 닫은 뒤 dim 제거 |
| Scrollbar | 02_monster_scroll_bottom.png, 08_run_skill_filled.png | Collection 아래 끝, Run unused cells 제외, 경계 간격 |

UI preview는 Maker Play 안에서 기존 UI 컨트롤러와 client 표시 상태를 호출했다. 모든 화면을 마우스로만 열었다고 주장하지 않는다. Party 2~4인 동시접속, 자연 Boss CLEAR/FAIL, 모든 업그레이드 획득·구매 동작은 이번 정렬 검사 범위에서 NOT_RUN이다. `09_run_upgrade.png`, `11_boss.png`, `12_result.png`는 요청된 파일명을 유지했지만 **QA_SCREEN**이다. Preview는 원래 상태로 되돌리고 실제 Run은 ABANDON하여 로비로 돌아왔다.

## Build / Runtime

- 최종 Stop → Refresh → Build 검사 → Play 수행 후 표시 회귀 확인.
- Maker Build Error **0**, Warning **4**. 기존 RunChest ColliderType/CircleRadius, 마노 InputSpeed, 보우마스터 AvatarAttackPlayRate 경고이며 2026-09-29 21:36:43 기록이 남아 있다.
- 최종 UI 검증 구간: **2026-09-30 01:17 KST 이후**, `ALIGN_FINAL_END`까지.
- 해당 구간 Runtime Error **0**. Runtime Warning **73**: TriggerComponent Legacy LWA-3019 **67**, RoomPortal/TownGate 중복 책임 안내 **3**, RoomBounds/RectTileMap 미발견 **3**.
- 위 경고 유형은 모두 2026-09-29 21:37부터 있던 유형이다. 새 UI 오류/경고 유형은 발견하지 못했다. 경고 0이라고 판정하지 않는다. Portal/맵 로직은 이번 범위를 벗어나 수정하지 않았다.
- `final-session-evidence.json`은 해당 구간 오류·경고와 ALIGN 체크 로그를 보존한다. raw/decoded LWA-3019를 합산하여 67건이다. 전체 과거 로그가 오류 0이라는 뜻이 아니다. Console을 지우지 않았다.
- Collection 복귀 로그: `cell101=true columns=4 cell=(111.000, 102.000)`.
- 닫기 로그: `ALIGN_FINAL_RUN_DIM_CLOSED false`, 최종 `all QA display overlays closed; lobby restored`.
- `git diff --check` PASS. 보고서 생성 스크립트의 일시적인 JS 괄호 오류는 수정 후 정상 생성 확인했으며 Maker 코드/Runtime 오류와 별개다.

## 이번에 손댄 실제 프로젝트 파일

UIBuilder 사용: `ui/PlayerHud.ui`, `ui/EquipWindow.ui`, `ui/AreaSelect.ui`, `ui/SkillBar.ui`, `ui/RoomProgress.ui`, `ui/PopupGroup.ui`, `ui/ToastGroup.ui`.

표시 어댑터: `RootDesk/MyDesk/UI/EquipPanel.mlua`, `RoomProgressHud.mlua`, `PlayerHud.mlua`, `AreaSelectPanel.mlua`, `SkillBar.mlua`; `RootDesk/MyDesk/Inventory/SkillDrop.mlua`의 frame child scale; `Mislocated/MyDesk/GameData/GameData.mlua`의 client RunUpgrade text alignment만.

작업 전부터 같은 파일에 있던 기능 변경은 이번 정렬 작업으로 간주하지 않는다. 전체 Git diff는 이전 미커밋 변경까지 포함하므로 이 보고서와 audit의 범위를 기준으로 구분해야 한다.

## 결론

캡처한 844×475 화면에서 정렬·간격·겹침·레이어 회귀 확인을 마쳤다. 현재 스타일을 **FINAL UI BASELINE**으로 기록한다. 이는 현재 파일 hash와 확인한 UI 상태에 대한 기준이며 모든 몬스터 이미지·모든 텍스트 길이·멀티플레이 게임 흐름의 전수 보증은 아니다. 추가 스타일 확장/재설계 없이 여기서 종료한다.
