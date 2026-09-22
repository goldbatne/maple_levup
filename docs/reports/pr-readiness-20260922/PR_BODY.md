## 변경 내용

- 원본 프로젝트의 누적 Mega Area 개편, 혼합 조우, Run 능력 풀·랜덤 5재고, 파티/입장/나가기 UI와 RPG HUD 정리를 함께 정리합니다.
- Mislocated 엔트리 복구와 기존 데이터·맵·UI 변경을 포함합니다. 스킬 감사 baseline, 승인 아트, 맵 비교본은 보존합니다.
- 추가 사용으로 공급 시간이 밀리는 문제, 마지막 생존자 포기 후 Run 잔류, 포탈 안내 RPC의 맵 수명 문제, 생성 사전검사 상태 복원 누락을 수정했습니다.
- 사용자 확인에 따라 ABANDON 시 이번 Run의 새 도감 발견도 폐기합니다. 기존 영구 기록은 유지하며 새 발견은 서버 Run 임시 원장에만 두어 자동저장 누출을 막습니다.
- 현재 데이터 기준 검사와 오류 주입 회귀를 보강하고 기존/현재 보고서의 적용 범위를 구분했습니다.
- 제한시간이 없는 Run 보스 HUD의 레거시 00:00 표시를 숨겼습니다. 실제 보스 화면에서 이름·HP 유지와 시간 숨김을 재확인했습니다.

## 실제 검증

- Maker Refresh 및 새 Build: Error 0, 기존 Warning 2.
- 현행 66종 실제 PlayerAttack 발동 132회: 실제 피해/방어 상태, 중복 재고 연속 사용, 해당 슬롯 소비, 플레이어 cooldown 우회 확인.
- 5개 Mega Area 포탈 연결·보스 격파·Clear·로비 복귀. QA 위치 보조를 사용했으며 모든 지형을 사람 입력으로 걸어 완주한 검증은 아닙니다.
- 자연 첫 능력 획득, 5초 공급, 공급 타이머 보존, 창 취소, Abandon, Fail 및 다음 Run 초기화 확인.
- 5 Area × 2 Seed = 10건의 서버 생성/재현/상태 복원 통과.
- 별도 MakerTest QA 저장 키에 저장·재조회하여 pending 미직렬화, Abandon 폐기, Fail/Clear 정산, 기존 기록 보존 확인.
- 정적 검사와 104개 데이터 음성 회귀, 포탈·생성 상태·발견 정산 회귀 통과.

## 검증 한계 — 완료로 표현하지 않음

- 실제 2~4개의 독립 클라이언트 Runtime은 환경상 BLOCKED. 서버 상태/정책 모델을 실제 협동 통과로 계산하지 않습니다.
- 66종 VFX의 전수 미술 승인, 모든 벽/통로 조합, 모든 Seed 사람 입력 완주 NOT_RUN.
- 동일 Run 서버 메모리가 소멸한 이후 오프라인 참가자의 임시 발견 복원·전달은 미구현입니다.
- 수정 전 오류와 QA 관측 코드 오류 2건은 기록에 보존했습니다. QA 주입/정적 검사/실제 실행을 구분합니다.
- 전체 staged 공백 검사는 보존 패치·과거 보고서의 경고 528건으로 미통과입니다(충돌 마커 없음). baseline 해시를 유지하며 역사 자료를 재작성하지 않았습니다. 현재 소스·도구·이번 보고서 범위는 별도 검사합니다.

## 리뷰 자료

- [현재 게임 규칙](https://github.com/goldbatne/maple_levup/blob/codex/mega-area-pr-readiness-20260922/docs/CURRENT_GAME_STATE.md)
- [최종 추가 검증 보고서](https://github.com/goldbatne/maple_levup/blob/codex/mega-area-pr-readiness-20260922/docs/reports/pr-readiness-20260922/PR_READINESS_REPORT.md)
- [66종 관측 행](https://github.com/goldbatne/maple_levup/blob/codex/mega-area-pr-readiness-20260922/docs/reports/pr-readiness-20260922/SKILL_RUNTIME_OBSERVED.json)
- [독립 패키지 점검](https://github.com/goldbatne/maple_levup/blob/codex/mega-area-pr-readiness-20260922/docs/reports/pr-readiness-20260922/PACKAGE_READONLY_RECHECK.md)

이 PR은 리뷰 요청이며 사용자 아트 승인이나 독립 승인자의 APPROVED를 의미하지 않습니다. 자동 병합하지 않습니다.
