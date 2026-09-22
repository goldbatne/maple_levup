# Area 선택 UI 감사

## 최종 구조

- 왼쪽: `MEGA 1`~`MEGA 5` Area 카드
- 오른쪽: 선택 Area 정보와 Run 옵션
- 난이도/획득 모드: `일반`, `몬스터 스킬`
- 입장 형태: `Solo`, `Party`
- Party 선택 시: 파티 상태, 준비 상태, 시작 조건 표시

기존 Area 자산을 삭제하거나 Area 데이터를 재구성하지 않았다. 화면은 Mega Area 선택 단위만 노출하고 세부 Run 생성은 기존 서버 Run 경로로 전달한다.

## 기능 판정

| 검사 | 판정 | 실제 확인 |
|---|---|---|
| MEGA 1~5 표시 | PASS_RUNTIME | `evidence/area_select_solo.png` |
| 일반 모드 선택 | PASS_RUNTIME | `evidence/area_select_normal.png` |
| 몬스터 스킬 모드 선택 | PASS_RUNTIME | `evidence/area_select_monster_skill.png` |
| Solo 선택 | PASS_RUNTIME | Solo Run 실제 생성 |
| Party 선택 | PASS_RUNTIME | `evidence/area_select_party.png` |
| 파티 1인 시작 차단 | PASS_RUNTIME | 1/4 상태에서 시작 거부 |
| 리더 Area/모드 권한 | PASS_STATIC/SERVER_SIM | 비리더 변경 거부 포함 시뮬레이션 통과 |
| 전원 준비 조건 | PASS_STATIC/SERVER_SIM | 2~4인 전원 준비 통과 |

## 시각 회귀 확인

- Area 목록과 옵션 패널을 좌우로 분리해 선택 대상과 입장 규칙을 동시에 확인할 수 있다.
- `Party` 선택 시 준비 대기 상태를 명시한다.
- 전투 HUD에 새 대형 버튼을 추가하지 않았다.
- 실제 2~4인 파티원 표시와 동시 준비 조작은 멀티클라이언트 제약으로 `NOT_RUN`이다.

## 증거 이미지

- `evidence/area_select_solo.png`
- `evidence/area_select_normal.png`
- `evidence/area_select_monster_skill.png`
- `evidence/area_select_party.png`
- `evidence/party_window.png`

