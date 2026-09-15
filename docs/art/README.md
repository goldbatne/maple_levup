# 아트 자료 안내

이 폴더는 게임 실행 리소스 자체가 아니라, 몬스터 스킬·UI·타일 아트의 제작 입력과 검수 근거를 보관한다. MSW가 직접 읽는 `RootDesk/`, `map/`, `ui/`, `Global/`, `Mislocated/`는 등록 경로이므로 지역별 하위 폴더로 임의 이동하지 않는다.

## 현재 정본

| 용도 | 경로 | 원칙 |
|---|---|---|
| 이미지 생성 INPUT | `images-input-packages/` | Area 00~20의 현행 단일 정본. 예약 결번 Area 06은 없다. |
| 받은 OUTPUT | `output/` | 사용자가 전달한 원본 ZIP. 덮어쓰거나 이미지 내용을 수정하지 않는다. |
| 규격 정리 OUTPUT | `output_repacked/` | 원화 PNG 바이트를 보존한 REPACK 결과. 실행별 폴더를 유지한다. |
| 스킬 반입 기록 | `import-runs/` | Sprite·AnimationClip·ICON RUID와 런타임 연결 검증의 근거. |
| 타일 원본·검수 자료 | `tiles/` | 지역 타일 제작 원본과 비교 자료. 실제 맵 적용 파일은 `map/`과 tileset 원위치에 둔다. |

`images-input-packages-v2`, `images-input-packages-v2_1`~`v2_4`는 현행 제작 지시가 아니다. 2026-09-13 정리 이후 `images-input-packages/`에 필요한 내용이 통합됐으며, 과거 revision은 Git 이력에서 조회한다. 로컬 보존본의 해시는 `INPUT_DIRECTORY_CLEANUP_20260913.json`에 기록돼 있다.

현행 20개 ZIP의 최종 command-system 해시는 `skill_reference_collection/ALL_AREA_COMMAND_SYSTEM_VALIDATION.json`에 고정돼 있으며, `docs/tools/verify-area-images-input-packages.py`가 이를 기준으로 재검증한다.

## 검수와 전달

| 용도 | 경로 |
|---|---|
| OUTPUT 자동·시각 검수 | `output_audit/` |
| 검사 중간 작업 공간 | `output_audit_work/` |
| 사용자 전달 후보 | `deliveries/` |
| 설정·스타일 전수 검토 | `design-review-00-05/`, `design-review-07-20/` |
| 스타일 문제 원인 분석 | `output_style_diagnosis/` |
| 공통 레퍼런스 수집 도구·채택 자료 | `skill_reference_collection/` |

검수 보고서와 실제 납품물은 보존한다. `PASS`는 해당 보고서에 적힌 검사 범위만 뜻하며 사용자 아트 승인이나 Maker 런타임 통과로 확대 해석하지 않는다.

## 로컬 작업 전용

다음 폴더는 생성 도중 생기는 원시 실행본·후보·다운로드 캐시라 Git 추적 대상에서 제외한다. 최종 채택물이 생기면 위의 정식 경로로 복사하고 출처·해시·판정을 기록한다.

- `chatgpt-work-runs/`
- `current-skill-reference-cache/`
- `images-input-packages_archive/`
- `refinement-batches/`
- `area00_refinement/`
- `output_style_unified_batches/`
- `skill_reference_collection/MSW_SKILL_REFERENCE_LIBRARY_PARTIAL.zip`
- `skill_reference_collection/backups/`
- 프로젝트 루트 `tmp/`

## 새 파일 배치 규칙

1. 새 INPUT은 revision 폴더를 다시 늘리지 말고 `images-input-packages/`의 빌드 절차로 갱신한다.
2. 사용자가 준 원본 OUTPUT은 `output/`에 보존하고, 수정·재포장 결과는 별도 실행 폴더에 둔다.
3. 자동 검사와 비교 이미지는 `output_audit/runs/<실행시각>/`에 둔다.
4. Resource Storage 반입 결과는 `import-runs/<범위>_<실행시각>/`에 둔다.
5. 최종 후보와 원시 작업 파일을 같은 폴더에 섞지 않는다.
6. Python `__pycache__`, `.pyc`, 임시 추출본은 커밋하지 않는다.

## 2026-09-15 정리 범위

- 현행 INPUT 정본을 `images-input-packages/` 하나로 고정했다.
- 과거 `images-input-packages-v2*` 중복 디렉터리는 현행 트리에서 제거 대상으로 유지했다.
- 원시 생성·보정 실행본과 캐시를 Git 추적 대상에서 분리했다.
- 게임 실행 경로와 기존 최종·검수·반입 산출물은 이동하거나 삭제하지 않았다.
