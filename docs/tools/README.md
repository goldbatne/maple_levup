# 문서·아트 도구 안내

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

도구를 실행하기 전에는 대상 경로와 쓰기 산출물을 확인한다. Maker 런타임 검증이 필요한 작업은 별도 MSW
검증 절차로 수행하며, 파일 검사 결과만으로 런타임 통과를 주장하지 않는다.
