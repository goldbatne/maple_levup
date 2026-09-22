# 커밋·PR 준비 정리 — 2026-09-22

## 판정

**검토용 Draft PR 준비 가능. 즉시 병합 승인 아님.** 커밋·push·PR 생성은 이번 작업에서 수행하지 않았다. staged 파일은 0개다.

- 대상: `D:/maplestory_levup`
- 브랜치: `codex/art-packages-cleanup-20260915`
- 기준 HEAD: `2eb7498eda8f53440648ef6107d6c933ba55d5c6`
- 기존 미커밋 개편을 포함하는 대규모 변경이다. 이번 정리만의 diff로 오해하지 않는다.

## 이번에 정리한 내용

1. README와 문서 인덱스의 현행 기준을 `docs/CURRENT_GAME_STATE.md`로 통일했다. 현재는 Mega Area / Run OwnedSkillPool / 랜덤 5칸 재고 / 5초 공급 / 사용 슬롯 소비 / Run cooldown 우회다.
2. 고정 슬롯·개별 쿨다운 시대의 완료 보고서와 RPG 문서에는 역사 기록임을 표시했다. 당시 Runtime 결과를 현행 전투의 검증으로 재사용하지 않는다. 원래 보고서 본문은 보존했다.
3. CSV의 인용된 쉼표와 프레임 시퀀스를 읽는 현행 데이터 검사기를 추가했다. 기존 RPG 검사는 `--legacy-rpg`로 보존한다. 과거 실패를 현행 PASS로 바꾼 것이 아니라 검사의 모집단과 기대 사양을 분리했다.
4. 정상 데이터와 오류 주입 8종, CSV 인용/열 수 회귀 검사를 추가했다. 테스트는 메모리 사본만 사용한다.
5. `.gitattributes`에서 Maker map의 CRLF 작업 파일과 LF 저장 형식을 명시했다. 게임 파일 바이트는 변경하지 않았으며 전체 renormalize/stage도 하지 않았다. CRLF 자체와 실제 후행 공백을 구분한다.
6. 파일별 커밋 분류 및 SHA-256 목록을 만들었다. 생성 목록 자신의 해시는 자기참조를 피하려 제외한다.

## 데이터 및 정적 검사

| 검사 | 실제 결과 | 범위 |
|---|---|---|
| `node docs/tools/verify-content-coverage.cjs` | exit 0, PASS_STATIC | ID/연결/CSV/VFX 레이어 형식/설정 |
| `node docs/tools/test-current-content.cjs` | exit 0 | 정상 + 8개 음성 테스트 + CSV 테스트 |
| `node docs/tools/verify-knowledge-base.cjs` | exit 0, PASS_STATIC | 현행 진입 문서/링크/데이터 |
| `node docs/tools/audit-mega-connectivity.cjs` | exit 0, unreachable 0 | map 163 / room 160 / portal edge 333 정적 연결 |
| 보호 파일 SHA-256 | 484개, 변경 0 / 추가 0 | 게임 소스·맵·UI·모델 및 스킬 감사 기준본 |
| `git diff --check` | exit 2 | 아래 후행 공백 10곳 남음 |

SkillTable 112개 = monster source 102 + boss source 10. 실제 drop 연결 101개 = 사용 가능한 액티브/방어 66 + 비활성 패시브 35. 연결 없는 `s_mon_snail`은 레거시다. 정의 수와 현재 플레이어 사용 가능 수를 섞지 않는다.

후행 공백 위치: `RootDesk/MyDesk/UI/AreaSelectPanel.mlua` 57, 68, 86, 87, 149, 159, 288, 297, 308, 317행. 모두 빈 줄의 탭이며 기능 오류라는 증거는 없다. 스킬 지침 재로딩 호출이 프로젝트의 Skill 도구 규칙을 이유로 자동 승인 검토에서 거절되어 이번 정리에서는 게임 실행 파일 수정까지 진행하지 않았다. 검사를 약화하거나 이 실패를 삭제하지 않았다.

추적 파일 diff는 줄바꿈 잡음 정리 전 약 +637,291/-619,209에서 검사 시점 +83,023/-64,899로 감소했다. 이는 기능을 대량 삭제한 것이 아니라 map 줄바꿈 차이의 정규화다. 미추적 파일은 이 diff 통계에 포함되지 않는다.

## Maker 실제 확인

- Maker Refresh: `status=ok`.
- Play: `edit_to_play` 성공. 시작 로그 시각 `2026-09-22T14:08:35`.
- 시작 전 normal 로그 4,461개 → 시작 후 5,670개, 추가 1,209개. 확인한 로그의 Error 0.
- Build 콘솔: Error 0, Warning 2, Info 5. Warning은 마노 `MovementComponent.InputSpeed`, 보우마스터 `MonsterAttack.AvatarAttackPlayRate`다.
- Build 콘솔의 최신 Info는 13:42:17, Warning은 12:07:15다. Refresh/Play는 이번에 실행했지만 새 컴파일 시각이 갱신됐다는 증거로 표현하지 않는다.
- 테스트 종료 후 Stop 성공 (`play_to_edit`).
- 이번 Runtime 범위는 시작 smoke test다. 모든 Mega Area 완주, 전체 스킬 발동, UI 전체 조작을 새로 실행했다고 주장하지 않는다. 실제 2~4인 협동도 이번에 실행하지 않았다.
- 계정 저장 내용·인증 정보·개인 식별 로그는 이 보고서에 싣지 않았다.

## 보존 및 기존 삭제 항목

이번에는 새로 삭제한 파일이 없다. 기존 사용자 변경을 reset/revert하거나 커밋하지 않았다. 보호 목록은 [PROTECTED_FILES_BEFORE.json](PROTECTED_FILES_BEFORE.json), 현재 분류·해시는 [COMMIT_INVENTORY.json](COMMIT_INVENTORY.json), 파일 그룹은 [COMMIT_GROUPS.md](COMMIT_GROUPS.md)에서 확인한다.

기존 작업 트리의 삭제 26개 중 24개는 RootDesk에 대응 파일이 존재한다. 나머지 2개는 디렉터리 메타데이터다. 대응 파일 존재는 내용 완전 동일의 증명이 아니며, 기존 엔트리 이동 복원 보고서와 함께 리뷰해야 한다. 기준본·승인 아트·맵 연구 자료를 불필요 파일로 분류해 삭제하지 않았다.

## 커밋 및 PR 권장 경계

- 엔트리 이동/복구, 게임 런타임·데이터, 맵, UI, 문서·검사 도구를 의미별로 분리한다. 관련 파일 쌍은 함께 포함한다.
- `COMMIT_GROUPS.md`는 경로 분류이며 독립 커밋의 빌드 성공을 보장하는 의존성 분석 결과는 아니다.
- Draft PR: 가능. 대규모 기존 변경과 현재 테스트 한계를 명시하여 리뷰를 시작할 수 있다.
- 즉시 병합: 아직 권하지 않는다. 후행 공백 10곳 정리, 대규모 실제 diff 리뷰, 현행 Mega Area 플레이 회귀 확인이 남는다. 2~4인 미검증을 협동 완료로 표시하지 않는다.
- 게임 사양을 이번 문서 정리를 이유로 다시 바꾸거나 스킬 효과·밸런스를 수정하지 않았다.
