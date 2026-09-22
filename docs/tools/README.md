# 문서·아트 도구 안내

## 현재 커밋 전 검사

- `node docs/tools/verify-content-coverage.cjs`: 현행 Mega Area CSV 연결/개별 프레임 레시피, 필수 테이블·이름·실행 숫자 열 검사. `verify-current-content.cjs`로 위임한다.
- `node docs/tools/test-current-content.cjs`: 정상 데이터와 104개 오류 주입 복사본 회귀 테스트. 선택적 숫자 빈칸과 `cooldown=0`의 기존 호환성도 확인한다. 게임 파일에 쓰지 않는다.
- `node docs/tools/verify-knowledge-base.cjs`: 현행 문서 입구와 링크/데이터 검사. `verify-current-docs.cjs`로 위임한다.
- `node docs/tools/prepare-commit-inventory.cjs`: 보존 해시와 커밋 그룹 보고서 갱신. `--capture`는 최초 보존 목록이며 덮어쓰기를 거절한다.

기존 RPG 검증 조건은 두 진입 명령의 `--legacy-rpg` 옵션으로 보존했다. 실패 기록을 현행 PASS와 혼합하지 않는다. 과거 content CSV 파서는 따옴표 안 쉼표가 있는 `sprite_sequence`를 지원하지 않는다. 현행 데이터 검사는 리소스의 실제 재생이나 과거 RPG 장비 UI의 정상 동작을 인증하지 않는다.

이 폴더에는 현재 사용하는 도구와 이전 패키지 revision을 재현하기 위한 이력 도구가 함께 있다.
파일명에 `v2`, `v2_1`, `v2_2`, `v2_3`, `v2_4`가 들어간 도구는 당시 산출물의 근거 보존용이며,
현재 `docs/art/images-input-packages/`를 대상으로 실행하지 않는다.

## 현행 Area 이미지 INPUT 도구

- `rebuild-current-area-images-input-packages.py`
  - 현재 기준 패키지를 다시 구성하는 도구다.
  - 네트워크 자료 수집과 ZIP 재생성을 포함하므로, 기준 갱신 작업에서만 실행한다.
- `verify-area-images-input-packages.py`
  - 현재 기준 패키지 20개(AREA 06 예약 결번)의 구조·해시·핵심 문서를 검증한다.
  - 결과는 `docs/art/images-input-packages/PACKAGE_VALIDATION_REPORT.{json,md}`에 기록한다.

현재 기준과 디렉터리 역할은 `docs/art/README.md`와 `docs/art/AGENTS.md`를 먼저 읽는다.

## 이력 보존 도구

아래 이름 패턴은 과거 revision 전용이다.

- `*v2*.py`
- `*v2_1*.py`
- `*v2_2*.py`
- `*v2_3*.py`
- `*v2_4*.py`

이 도구들은 삭제된 현재 작업 폴더를 복구하기 위한 도구가 아니다. 당시 revision을 조사하거나 재현해야 할 때
Git 이력의 해당 패키지와 함께 사용한다. 현재 기준을 바꾸기 위해 과거 스크립트의 경로 상수를 수정하지 않는다.

## 기타 도구

- `generate-area*.cjs`, `verify-area*.cjs`: 지역·타일 제작과 검증 이력
- `audit_*`, `build_*_audit.py`, `finalize_*`: OUTPUT 감사와 보고서 생성
- `prepare-*`: 한정 파일럿 입력 준비
- `discover-*`: MSW 리소스 후보 조사 기록

## 로그라이트 현행 재현·감사 도구

다음 도구는 2026-09-21 로그라이트 개편과 UI 정리를 재현하거나 검사하기 위한 현행 도구다.

- `rebuild-party-area-ui.cjs`: Area 선택/파티 UI를 builder로 재생성한다.
- `rebuild-run-abandon-ui.cjs`: Run 메뉴의 던전 나가기 확인 UI를 builder로 재생성한다.
- `rebuild-run-owned-skills-window.cjs`: Run 보유 능력 창을 builder로 재생성한다.
- `audit-mega-connectivity.cjs`: Mega Area 연결 데이터를 정적으로 감사한다.
- `write-mega-runtime-results.cjs`: 수집한 Mega Runtime 결과를 보고서 형식으로 정리한다.
- `enable-roguelite-instance-maps.cjs`, `set-area-instance-mode.cjs`: 맵 instance 플래그 이관 도구다. 현재 데이터를 다시 바꾸는 일반 실행 도구가 아니므로 대상과 dry-run 여부를 확인한 뒤 사용한다.

UI 파일은 원시 JSON을 직접 수정하지 않고 위 builder 또는 해당 UI 생성 스크립트로 재현한다. 감사·보고 도구의 PASS는 Maker Runtime PASS를 대신하지 않는다.

도구를 실행하기 전에는 대상 경로와 쓰기 산출물을 확인한다. Maker 런타임 검증이 필요한 작업은 별도 MSW
검증 절차로 수행하며, 파일 검사 결과만으로 런타임 통과를 주장하지 않는다.
