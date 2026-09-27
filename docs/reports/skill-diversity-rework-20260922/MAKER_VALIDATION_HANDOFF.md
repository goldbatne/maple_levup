# Maker 검증 재개 지점 (2026-09-24)

이 문서는 실행 결과가 아니다. 현재 Codex 세션의 도구 목록에서 Maker Play/Stop/로그/스크립트 호출이 제공되지 않아, 직전 Play 세션 이후의 검증을 이어서 실행하지 못한 상태를 기록한다.

- 마지막 게임 코드 변경: 투사체 착탄/관통의 벽 뒤 피해 차단 (`GameData`, `PlayerAttack`, `MonsterAttack`). 마지막 Maker Refresh/Build는 Error 0, 기존 모델 Warning 2건이었다.
- 변경 후 플레이어 66종: 실제 `PlayerAttack.UseSkill` 재실행 66/66, 로그 `observed=66 pass=66 fail=0 notRun=0 ... seconds=159.232` (2026-09-23 21:40:16~21:42:53).
- 변경 후 몬스터 66종: **미실행**. 보관된 `MONSTER_SKILL_RUNTIME*.csv`의 66/66은 벽 가림 수정 전 소스에 대한 결과다. 대표 몬스터 투사체는 별도 Maker Play에서 벽 뒤 무피해/같은 편 피해를 확인했다.
- 직전에는 MONSTER_SKILL QA용 Play가 시작되어 있었다. 접속 복구 후 우선 현재 Play 상태를 확인하고 **QA Run을 정상 Stop/Abandon**해야 한다. 임시 검사 스크립트는 리스폰 타이머 등을 격리하며 `CLEANUP QA_RUN_ABANDON_REQUIRED`를 출력한다. 이 QA Run을 일반 플레이 검증 결과로 사용하지 않는다.

재개 순서: Maker 연결 확인 → 현재 QA Play 정리 → Stop/Refresh/Build 로그 → 새 MONSTER_SKILL Run에서 `monster-66-runtime-qa.lua`를 실제 MonsterAttack 경로로 실행 → 해당 구간 로그/Error 분리 → 결과 CSV와 본문 갱신 → NORMAL/MONSTER_SKILL 자연 Run 각 3회 및 지형·UI 회귀. Maker에서 실행하지 않은 단계는 `NOT_RUN`으로 유지한다.

정적 확인은 `node docs/tools/verify-skill-diversity-rework.cjs`로 다시 실행할 수 있다. 이 명령의 `PASS_STATIC`은 Maker Build/Runtime 통과를 뜻하지 않는다.
