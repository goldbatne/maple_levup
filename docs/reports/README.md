# 보고서 인덱스

이 디렉터리는 구현 코드와 분리된 감사·검증·복원 자료를 보관한다. 보고서의 `PASS_RUNTIME`, `PASS_STATIC`, `SERVER_SIM`, `BLOCKED` 표기를 서로 같은 의미로 해석하지 않는다.

## 현재 확인에 우선 사용할 보고서

| 주제 | 경로 | 용도 |
|---|---|---|
| PR 제출 전 추가 Runtime 검증 | `pr-readiness-20260922/PR_READINESS_REPORT.md` | 현행 66종 발동, 5개 Mega Area, 타이머·포탈·포기·검사기 보정 및 남은 제한 |
| 커밋·PR 준비 최종 정리 | `commit-preparation-20260922/CLEANUP_REPORT.md` | 문서/검증기 정리, 보호 해시, Maker 시작 검사와 PR 판단 |
| 현재 UI·파티·던전 나가기 | `party-area-ui-20260921/FINAL_REPORT.md` | 가장 최근 UI/파티 입장 및 Solo Runtime 결과 |
| 현행 게임 규칙 | `../CURRENT_GAME_STATE.md` | Mega Area 랜덤 재고와 현행 검증 범위 |
| Mega Area 개편 | `mega-area-random-encounter-20260921/FINAL_MIGRATION_SUMMARY.md` | 5개 Mega Area, 랜덤 공급·슬롯 소비 |
| 개편 전 고정 슬롯 완료 감사 | `roguelite-completion-20260921/FINAL_COMPLETION_AUDIT.md` | 역사 기록. 당시 66스킬 실행은 현재 공급/소비 검증을 대신하지 않음 |
| Mega Area 연결/리스폰 | `mega-area-connectivity-respawn-20260921/FINAL_REPORT.md` | 포탈 연결, 도달성, 리스폰 결과 |
| 이전 설계 감사 | `current-design-audit-20260921/CURRENT_DESIGN_AUDIT.md` | Mega Area 전환 이전 비교 기준 |
| 스킬 다양성 기준본 | `skill-diversity-audit/LATEST_BASELINE.txt` | 개편 전 스킬 분석 기준본 위치 |
| 파일·보고서 정리 | `FILE_AND_REPORT_CLEANUP_20260922.md` | Maker 로드 위치 복구, 대용량 실패 산출물 제거, 보존 범위 |

## 이력 및 보존 자료

| 폴더 | 상태 | 설명 |
|---|---|---|
| `roguelite-merge-20260921/` | 이력 | 별도 작업본에서 원본 프로젝트로 병합한 기록 |
| `roguelite-recovery-20260921/` | 이력/복원 | Maker 엔트리 복구와 로비 Runtime 증거 |
| `mega-area-random-encounter-20260921/` | 현행 기반 | Mega Area·랜덤 조우 매핑과 정책. 이후 UI/포탈 보정 보고서를 함께 확인 |
| `workspace-entry-cleanup-20260921/` | 복원 | Mislocated/엔트리 정리 전후 해시와 소형 복원 ZIP |
| `ROGUELITE_RECOVERY_RISKS_20260921.md` | 참고 | 복구 시 주의할 위험 목록 |

## 스킬 다양성 기준본

- 확정 baseline: `skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`
- 최종 HTML: `skill-diversity-audit.html`
- 분석 데이터: `skill-diversity-data.json`
- 재현 자료: `baseline/tracked-working-tree.patch`, SHA-256 목록, `workspace-entry-cleanup-20260921/skill-audit-174133-untracked.zip`
- 중단된 `173637`, `173743` 생성 시도의 대용량 `repository-head.bundle*`은 확정 기준본이 아니며 커밋 대상에서 제거했다.

## 보존 원칙

- 최종 Markdown/CSV/JSON과 직접 연결된 증거 PNG는 유지한다.
- Maker Runtime을 실제 수행하지 않은 항목은 `PASS_RUNTIME`으로 승격하지 않는다.
- `pre-*` 백업은 복구 이력이 명시된 폴더에서만 유지한다.
- 새 대용량 Git bundle/lock은 `.gitignore`로 제외한다.
- 보고서 경로를 바꾸면 내부 상대 경로와 `LATEST_*` 포인터도 함께 갱신한다.
