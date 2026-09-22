# 메이플 레벨업

MapleStory Worlds의 RectTile 기반 실시간 Mega Area 로그라이트다. Run에서 능력 풀을 늘리고, 5초마다 공급되는 최대 5칸의 일회성 스킬을 소비하며 보스를 공략한다. 동일 스킬 중복 공급을 허용하고 Run 플레이어의 개별 쿨다운은 적용하지 않는다.

기존 20개 지역(AREA 06 예약 결번)을 5개 Mega Area로 묶는다. 솔로 실행 증거와 파티 서버 구현은 있으나 실제 2~4클라이언트 협동 완료를 주장하지 않는다. [현재 구현 기준](docs/CURRENT_GAME_STATE.md)에 실행 구조와 검증 한계를 정리했다.

## 문서 읽기

에이전트와 개발자는 먼저 [문서 인덱스](docs/README.md)를 읽는다. 거기서 작업에 필요한 정본만 골라 읽고, `docs/archive/`는 과거 판단의 이유가 필요할 때만 조회한다.

- 현재 구현과 미검증 범위: [현재 구현 기준](docs/CURRENT_GAME_STATE.md)
- 검증 기록의 적용 시점: [보고서 인덱스](docs/reports/README.md)
- 현재 데이터 검사: `node docs/tools/verify-content-coverage.cjs`
- 검사기 회귀 테스트: `node docs/tools/test-current-content.cjs`
- 과거 RPG 기획·밸런스·인수인계: [문서 인덱스](docs/README.md)의 역사 자료

## 개발 원칙

- MSW 플랫폼·파일·Maker 작업 규칙은 루트 `AGENTS.md`가 최우선이다.
- 실제 동작은 `.csv`, `.mlua`, `.model`, `.map`, `.ui`와 검증 결과를 기준으로 판단한다.
- 구조화 파일은 공식 빌더와 Maker Refresh 흐름을 따른다.
- `.agents/`, `.codex/`, `.mswai/`는 재설치 가능한 AI ToolKit 산출물이므로 Git에 넣지 않는다.
