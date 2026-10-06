# 메이플 스킬 러시

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

## 최근 변경 — 2026-10-07

- UI를 RUN 목표창·스킬 아이콘과 어울리는 평면 스타일로 통일했다. 장식용 입체선·그림자를 제거하고 선택 상태 등 기능성 표시는 유지한다.
- 모험 시작은 초록, 파티 찾기는 파랑으로 구분한다. 몬스터 컬렉션의 **강화 +1은 파랑, 레벨업은 초록**이며, 튜토리얼은 검정 테두리의 원형을 유지한다.
- 파티·채널 창과 목록 행을 확대하고 채널 안내를 짧게 정리해 텍스트 잘림을 줄였다.
- 상점 구매창 취소 후 다른 상품을 선택할 수 있도록 사전 조회 잠금을 구매창 호출 후 해제한다. 상품 지급·영수증 검증은 기존 구매 콜백에서 처리한다.
- RUN의 기본 몬스터 스킬 드랍 확률은 **50%**, 일반·보스 테이밍 확률은 **5%**다. 최초 스킬 드랍 보장과 엘리트 확률 규칙은 유지한다. 이전 imported GameBalance가 남아 있어도 해당 RUN 확률이 적용된다.
- 등록 당시 SHA-256과 일치하는 120×120 상품 PNG를 복원했다: [파란 코어](docs/reports/live-worldshop-link-20261001/product-icons/growth_core_bundle.png), [주황 점수](docs/reports/live-worldshop-link-20261001/product-icons/growth_score_bundle.png). 실제 플랫폼 상품 이미지도 코어 100코인=파랑, 점수 200코인=주황으로 조회·확인했다. 플랫폼 상품 설정은 Git 변경과 별개다.

검증: Maker에서 상점·컬렉션 열림, 평면 스타일과 강화/레벨업 색상, RUN 확률 값을 확인했다. 확인한 빌드·실행 로그에 오류는 없었으나 기존 경고는 남아 있다. 실제 월드코인 결제·취소 재구매 및 모든 기기 화면의 회귀 검증은 별도 확인이 필요하다.

정적 검사 참고: `verify-content-coverage.cjs`는 연결된 사용 가능 스킬 **64개 / 기대값 66개** 불일치로 실패하며, `test-current-content.cjs`도 같은 선행 검사에서 실패한다. 이번 변경에서는 해당 스킬 CSV와 검사기를 수정하지 않았다.
