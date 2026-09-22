# Skill Diversity Audit Baseline

- baseline_id: `skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`
- 분석 시작: 2026-09-20 174133 KST
- 브랜치: `codex/art-packages-cleanup-20260915`
- HEAD: `2eb7498eda8f53440648ef6107d6c933ba55d5c6`
- 미커밋 변경: **있음**
- 작업 트리 지문(SHA-256): `fe5fd560ce4c992e562fcc91c0ed6c5cc07443de9224eccd4dc428269b351d82`
- 보존 위치: `docs/reports/skill-diversity-audit/skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c/baseline`
- 런타임: **NOT_RUN** — Maker MCP play/logs 도구가 이 세션에 없음

## 현재 활성 모드

- phase1_random_combat_enabled: 1
- phase3_simplified_growth_enabled: 1
- SkillBar: 최대 5칸, 5초마다 빈 슬롯 1개 공급
- 획득: MonsterTable.drop_skill_id → 처치 시 테이밍 → TamedMonsters
- 사용: 테이밍된 액티브 전체가 동일 가중치 랜덤 풀, 성공 사용 시 슬롯 소비
- 재사용: 신규 랜덤 모드에서 SkillTable cooldown을 검사하지 않음. 레거시 모드 데이터는 유지.
- 장착: 신규 모드에서는 MonsterSlots를 사용하지 않음.

## 실제 로드 원본

- SkillTable: `Mislocated/MyDesk/GameData/SkillTable.csv` (loader `RootDesk/MyDesk/GameData/GameData.mlua:213`, SHA-256 `3a84b837edc8615e423dcc1da6a89a0237a36d3c481f310338fbe016a211023b`)
- MonsterTable: `RootDesk/MyDesk/GameData/MonsterTable.csv` (loader `RootDesk/MyDesk/GameData/GameData.mlua:370`, SHA-256 `6783014b6990f67988b4d17d5ae3b0b741896433fcefe3849449b7e06073b5e2`)
- GameBalance: `RootDesk/MyDesk/GameData/GameBalance.csv` (loader `RootDesk/MyDesk/GameData/GameData.mlua:181`, SHA-256 `cf4070af15c35af12902c859a9ec6f638bda4fbf9ba15f5b865ddb5b02d38245`)

## 기준본 재현

1. 동일 저장소에서 git checkout 2eb7498eda8f53440648ef6107d6c933ba55d5c6로 기준 커밋을 체크아웃한다.
2. git apply --binary tracked-working-tree.patch를 적용한다.
3. baseline/untracked 아래 파일을 저장된 상대 경로로 복사한다.
4. 민감 이름 정책으로 제외된 파일은 보고서에 내용이 포함되지 않으므로 원래 안전 저장소에서 별도로 복구한다.

민감 파일명 정책에 해당한 파일 내용은 기준본에 넣지 않았다. 이번 기준본은 보고서 디렉터리 자체를 작업 트리 지문에서 제외했다.
