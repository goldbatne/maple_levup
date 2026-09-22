# 로그라이트 복구·UI·런타임 검증

사용자 승인: 2026-09-21, 위험 목록 R01~R14 전체 순차 처리.
최종 사양은 사용자 로그라이트 지시 및 `reports/roguelite-merge-20260921/rework-plan/ROGUELITE-GDD.md`를 따르며 과거 M1/M2 기획은 복구하지 않는다.
실행 프로젝트: D:/maplestory_levup. 스킬 고유 효과/수치/VFX 및 감사 baseline 보존.
상태는 msw-planning/references/build-management.md 기준으로 코드 완료와 실측을 구분한다.

|작업|상태|검증 조건|
|---|---|---|
|R01/R02 저장 격리·데이터 실패 보호|🟡|전용 키/실패 보호/빈 JSON 오류 수정, Maker 발견 기록 저장·재로드 확인. 운영 이관 미검증|
|R03/R04 엔트리·테이블 안정성|⬜|등록/필수 열/저장 후 위치 유지|
|R08/R09 UI 정리|🟡|레거시 숨김/독립 획득패널/서버 뷰/목표 HUD 수정. 메뉴·준비·입력 회귀 남음|
|R05 획득 후보 유지/요청 중복 방지|🟡|대기열·revision 구현, 2후보/중복 요청 Maker 통합 검증. 자연 연속 처치 전수 아님|
|R06/R07 목표 지정·목표 종류|🟡|목표 ID 검사/도달형 00·01 구현, 위치 보조 도달 완료·저장 확인|
|R10 종료·다음 Run 초기화|🟡|maptown 기동 후 실제 인스턴스 입장/실패·클리어 로비 복귀 moved=1, 다음 Run 빈 슬롯 확인. 자연 사망·부활 등 추가 회귀 남음|
|R11 생성·지형 및 Area 검증|🟡|그래프 검사 추가. 전체 Seed 집계/실제 지형·스킬 검증 미완료|
|R12 실제 협동|🟡|NOT_RUN: 클라이언트 1개만 확인. 실제 2/3/4인 필요|
|R13/R14 경고·기록 정리|🟡|Error 0, 과거 Warning 2 잔존. 현재 증빙/미완료 보고서 작성|

최신 증빙: [RECOVERY_STATUS.md](reports/roguelite-recovery-20260921/RECOVERY_STATUS.md).

## 전체 완료 감사 후속 — 진행 중

|작업|상태|현재 증거 및 남은 조건|
|---|---|---|
|생성 실패 fallback/시작 전 검사|🟡|상한 있는 경로 탐색·역할 재구성·Instance 생성 전 사전 검사. 전체 20 Area×2 Seed 그래프 통과; 실제 전수 이동 별도|
|Area 02 Instance 등록 불일치|✅|map11/12/13/16/17 Maker Save 정규화. Area 02 실제 입장 및 map11→12→17→14 이동|
|VFX 초기화 오류|🟡|Playing 초기화 guard 후 66×2회 실제 UseSkill Error 0. 장기/지형 회귀 남음|
|66개 스킬 발동/쿨다운|🟡|전 종 두 차례 실제 발동, 즉시 재사용 차단/슬롯 유지, 전 종 최소 1회 피해/방어 효과 확인. 시각·벽·교체 전수 미완료|
|Run 중 레거시 컬렉션 버튼·투명 입력 차단|🟡|로비 컬렉션 유지, Run 중 숨김, 닫힌 창 Enable=false. 실제 Run 화면 버튼 비노출 확인, 로비 열기/닫기 회귀 남음|
|사망/관전 공격 차단|🟡|PlayerAttack 서버 생존/Run/참가자 guard 추가, 빌드 Error 0. 권한 음성 테스트 남음|

증빙 디렉터리: `reports/roguelite-completion-20260921/`. 정상 플레이와 HP 보조 traversal QA는 별도 기록하며, 위 부분 결과는 전체 완료를 뜻하지 않는다.
2026-09-21 후속 승인으로 Maker Save → maptown 전환을 실행했다. 실제 인스턴스 입장 및 실패/클리어 후 로비 복귀 moved=1 확인. Run 내부 재시작 차단/중복 시작 잠금은 실제 요청 회귀 통과. 최신 상세 증빙은 [LOBBY_RUNTIME_FOLLOWUP.md](reports/roguelite-recovery-20260921/LOBBY_RUNTIME_FOLLOWUP.md). 전체 복구 완료는 아님.
