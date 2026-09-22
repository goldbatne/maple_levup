# 프로젝트 지식 인덱스

> 갱신: 2026-09-22 · 상태: 로그라이트 개편 이후 현행 진입점

이 파일은 에이전트가 매번 읽는 얇은 진입점이다. 모든 문서를 한꺼번에 읽지 말고 요청에 맞는 경로만 따라간다.

## 권위 순서

충돌할 때 아래에서 위로 덮어쓰지 않는다.

1. MSW 공식 지식과 작업 규칙: 루트 `AGENTS.md`, 설치된 MSW Skill, Maker/MCP가 반환한 사실
2. 실행 정본: `RootDesk/`, `map/`, `ui/`, `Global/`의 현재 데이터·스크립트·리소스
3. 자동 검증과 Maker 런타임 증거
4. 현행 로그라이트 설계·검증: `docs/reports/README.md`가 안내하는 최신 보고서
5. 이 폴더의 기존 RPG 문서와 M1/M2 문서: 구현 이력 및 비교 자료
6. `docs/archive/`: 더 오래된 결정과 작업 보고서

`docs/archive/` 및 아래의 M1/M2 문서는 설명 자료이지 현재 로그라이트 구현 지시가 아니다.

## 현재 로그라이트 정본

현재 실행 구조를 확인할 때는 다음 순서로 읽는다.

1. `CURRENT_GAME_STATE.md` — 현재 Mega Area 랜덤 재고 구현과 검증 범위
2. `reports/mega-area-random-encounter-20260921/FINAL_MIGRATION_SUMMARY.md`
3. `reports/mega-area-connectivity-respawn-20260921/FINAL_REPORT.md`
4. `reports/party-area-ui-20260921/FINAL_REPORT.md`
5. 실제 `RootDesk/`, `map/`, `ui/`, `GameData`와 Maker 로그

전체 보고서 분류와 스킬 감사 기준본 위치는 `reports/README.md`에서 확인한다. 보고서에 적힌 과거 경로보다 현재 작업 트리의 실제 경로가 우선한다.

`current-design-audit`와 `roguelite-completion`은 Mega Area 랜덤 재고 전환 전 기록이다. 고정 슬롯·쿨다운·공급 없음 판정을 현재 모드의 PASS로 재사용하지 않는다.

## 요청별 최소 읽기 경로

| 요청 | 먼저 읽기 | 이어서 읽기 |
|---|---|---|
| 현재 로그라이트 상태·다음 작업 | `CURRENT_GAME_STATE.md` | `reports/README.md` |
| 로그라이트 게임 규칙·완료 범위 | `CURRENT_GAME_STATE.md` | `reports/mega-area-random-encounter-20260921/FINAL_MIGRATION_SUMMARY.md` |
| 최신 UI·파티·던전 나가기 | `reports/party-area-ui-20260921/FINAL_REPORT.md` | 실제 UI/스크립트와 Maker 로그 |
| 개편 전 RPG 상태 | `프로젝트_현황.md` | `인수인계_현재상태.md` |
| 개편 전 게임 규칙·방향 | `게임기획서_v0.3.md` | `결정기록.md` |
| 전투·성장 수치 | `밸런스_확정수치.md` | 실제 GameData CSV |
| 지역·맵 확장 | `지역설계_area04-area20.md` | `인수인계_현재상태.md` |
| 구현·수정 | 위 정본 중 하나 | 관련 `.mlua/.csv/.model/.map/.ui`와 공식 Skill |
| 검증·런타임 | `검증가이드.md` | Maker MCP 로그·화면 |
| 과거 판단 이유 | `결정기록.md` | 필요한 `archive/` 파일 하나 |

## 개편 전 문서의 역할

- `프로젝트_현황.md`: 이미 존재하고 검증된 것만 요약한다.
- `인수인계_현재상태.md`: 현재 브랜치의 미완료·미검증·바로 다음 행동만 둔다.
- `게임기획서_v0.3.md`: 사용자 경험과 시스템 계약을 기록한다. 파일명은 기존 링크 호환을 위해 유지한다.
- `밸런스_확정수치.md`: 계산식과 상수의 사람용 정본이다. 최종 값은 GameData와 대조한다.
- `지역설계_area04-area20.md`: 지역 순서, 레벨 대역, 구현 상태와 미래 후보를 관리한다.
- `결정기록.md`: 현재도 유효한 결정과 폐기된 대안을 짧게 연결한다.
- `검증가이드.md`: 정적 검사와 Maker 검사가 각각 무엇을 증명하는지 정의한다.
- `지식체계_운영.md`: 이 구조를 유지하는 규칙이다.

## 과거 M1/M2 문서

다음 파일은 M1/M2 랜덤 공급·테이밍·동행을 검토하던 중간 단계 기록이다. 현재 Mega Area에도 랜덤 공급이 존재하지만 영구 테이밍/성장 등 당시 전체 규칙이 복구된 것은 아니다. 현행 계약은 `CURRENT_GAME_STATE.md`로 확인한다.

- `maple-levup-M1-GDD.md`
- `maple-levup-M1-Phase1.md` ~ `maple-levup-M1-Phase4.md`
- `maple-levup-M2A.md`
- `maple-levup-Roadmap.md`
- `Roguelite-Recovery-Phase.md`

이 파일들은 확정 스킬 감사 baseline과 복구 manifest에서 원래 경로를 참조하므로 현재는 이동하지 않고 보존한다. 관련 `.cjs`는 당시 검증/맵 파일럿 재현 도구이며 현행 빌드 단계에서 자동 실행하지 않는다.

## 폴더 규칙

이 저장소는 기존 도구와 링크 호환을 위해 소문자 `docs/`를 사용한다. 대소문자만 다른 `Docs/`를 새로 만들지 않는다. 공식 AI Skill 설치물인 `.agents/`, `.codex/`는 문서 정본이 아니며 Git에서 제외한다.
