# 파일·보고서 정리 기록 — 2026-09-22

## 목적

대규모 로그라이트 개편 작업을 커밋하기 전에 Maker가 사용하는 파일 위치를 복구하고, 현재 정본과 과거 기록을 구분하며, 명백히 불완전한 대용량 산출물을 제거했다. 게임 기획·밸런스·스킬 효과는 변경하지 않았다.

## 정리한 항목

- Maker 변환 실패 중 `Mislocated/MyDesk/UI`로 이동된 UI 스크립트와 디렉터리 메타데이터를 `RootDesk/MyDesk/UI`로 되돌렸다.
- `Mislocated/MyDesk/GameData`에 남아 있던 `GameBalance.csv`와 `GameBalance.userdataset`을 실제 로드 위치인 `RootDesk/MyDesk/GameData`로 되돌렸다.
- `PlayerHud.mlua`에 중복 삽입된 Run/파티 UI 컨트롤러 블록을 제거하고 저장소 기준 구현으로 복구했다. 실제 컨트롤러는 `GameData.mlua`에 유지한다.
- `docs/reports/README.md`를 추가해 최신 보고서, 이력, 복구자료, 스킬 감사 기준본을 구분했다.
- `docs/README.md`에서 현행 로그라이트 보고서를 우선 경로로 지정하고 M1/M2 랜덤 공급·테이밍 문서를 역사 자료로 명시했다.
- `docs/tools/README.md`에 로그라이트 UI builder와 감사/이관 도구의 용도를 기록했다.

## 제거한 항목

다음 두 파일은 확정 baseline이 아닌 중단된 스킬 감사 실행에서 생성된 불완전 파일이었다.

- `docs/reports/skill-diversity-audit/skill-audit-2026-09-20T173637KST-2eb7498eda-wtfe5fd560ce4c/baseline/repository-head.bundle` — 약 1,613.99 MB
- `docs/reports/skill-diversity-audit/skill-audit-2026-09-20T173743KST-2eb7498eda-wtfe5fd560ce4c/baseline/repository-head.bundle.lock` — 약 210.38 MB

총 약 1,824.37 MB를 제거했다. 두 파일은 Git에 추적되지 않은 실패 산출물이므로 Git 복구 대상이 아니다. 같은 패턴의 파일이 다시 커밋 후보로 들어오지 않도록 `.gitignore`에 정확한 패턴을 추가했다.

## 보존한 항목

- 확정 스킬 감사 baseline `skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`
- baseline의 HTML, JSON, Markdown, patch, 해시 목록
- `workspace-entry-cleanup-20260921`의 소형 복원 ZIP과 manifest
- Maker Runtime 증거와 최종 CSV/JSON/PNG
- 과거 M1/M2 문서와 재현 스크립트. 감사 baseline과 복구 manifest가 원래 경로를 참조하므로 이동하지 않았다.

## 검증

- Maker Refresh: 성공
- Build: Error 0
- Build Warning: 기존 마노 `MovementComponent.InputSpeed`, 보우마스터 `AvatarAttackPlayRate` 2건만 유지
- Play Runtime: Error 0
- `PlayerHud` 시작 로그 및 `GameData` 기반 Run/파티 UI 컨트롤러 준비 로그 확인
- 변환 실패 팝업 재발 없음

## 커밋 전 남은 주의사항

- 작업 트리는 여러 단계의 의도된 코드·데이터·맵·UI 변경을 함께 포함한다. 이 기록은 전체 변경을 자동 승인하지 않는다.
- `Mislocated`에는 디렉터리 메타데이터 4개만 남아 있다. 과거 엔트리 이동과 연결된 추적 삭제/수정은 별도 diff 검토 대상이다.
- 보고서의 과거 `Mislocated/...` 경로 표기는 당시 실행 기록이다. 현재 실제 로드 경로는 `RootDesk/MyDesk/...`다.
- 이 정리 단계에서는 커밋을 만들지 않았다.

## 커밋 준비 시점 작업 트리 요약

- 브랜치/HEAD: `codex/art-packages-cleanup-20260915` / `2eb7498`
- Staged 파일: 0개
- Tracked 수정: 230개
- Tracked 삭제: 26개
- `git status`의 untracked 그룹: 37개, 실제 untracked 파일: 184개
- Untracked 총용량: 약 62.21 MB
- `docs/reports`: 148개 파일, 약 61.68 MB
- 20 MB 이상 untracked 파일: `roguelite-recovery-20260921/pre-lobby-save-20260921.tar` 1개(약 24.54 MB). 엔트리 복구 원본이므로 유지했다.
- 임시 확장자(`.tmp`, `.bak`, `.old`, `.lock`, `.orig`, `.rej`)의 untracked 파일: 0개

변경의 큰 묶음은 `map/` 160개, `RootDesk/` tracked 51개와 untracked 12개, `ui/` tracked 11개와 untracked 1개, `Mislocated/`의 이전 엔트리 정리, 문서·검증 산출물이다. `map/`과 런타임 코드는 이전 개편 작업 결과이므로 이번 파일 정리 단계에서 되돌리거나 축소하지 않았다.
