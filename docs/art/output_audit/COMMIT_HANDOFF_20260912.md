# 몬스터 스킬 아트 제작·검수 자료와 현재 프로젝트 변경 전체 보존

몬스터 스킬 아트의 제작 입력, 승인 출력, 검수 증빙과 REPACK 결과를 저장소에 함께 보존하여 다른 작업자도 동일한 파일과 근거에서 작업을 이어갈 수 있게 한다. 이번 PR은 사용자가 요청한 현재 작업 디렉터리 전체 스냅샷이다.

## 포함 범위

- 달팽이 및 AREA 00 파일럿 반입 보고서·리소스 매핑·원본 자료, AREA 01 직접 생성 파일럿 기록.
- AREA 01~20 실제 19개 지역의 INPUT 제작·보정 이력과 V2.4 패키지(AREA 06 예약 결번).
- 원본 OUTPUT ZIP, 파일·설정·스타일·스토리 검수 결과, 비교 이미지, 검사/생성/REPACK 스크립트와 검사 작업 자료.
- 17개 Area의 V2.4 REPACK ZIP 및 `BASELINE_OUTPUT_INDEX.csv`에 기록된 고정 경로·SHA-256.
- 기존 미커밋 변경: 달팽이 드랍 스킬 연결, 작업 원장, map006/map205, EquipWindow/Inventory, Mislocated 및 중첩 RootDesk 파일. 이 PR 작성 중 게임 파일을 복구하거나 재설계하지 않았다.

## 검증 및 완료 범위

- 이전 REPACK 검사: 17 Area 파일 검증 PASS, 원화 역할 PNG 839개 바이트 변경 0. 고정 OUTPUT ZIP 17개 해시 재확인.
- 스토리·스킬명 보완 검수: 89개 중 85개에서 명백한 문제 없음. 동일 INPUT·PNG 해시로 연결되는 기존 검사 결과를 재사용했다.
- AREA 02 스톤골렘 / AREA 03 버블링의 지역 귀속, AREA 05 킹크랑의 노틸러스·플로리나 포함 범위, AREA 20 `발굴지의 석면` 명칭은 검토 사항으로 남긴다. 명칭·지역 검수만으로 완료 17 Area의 원화 재생성을 요구하지 않는다.
- 위 스토리 검수 이후의 후속 작업도 포함한다: `20260912_165951_area11_12_final/PACKAGING_STATUS.md`가 패키징 최신 상태다. 기존 `LATEST_REPORT.md`/`LATEST_REPACK.md`는 이전 단계만 가리키므로 후속 기록을 함께 읽어야 한다.
- AREA 11: 후속 작업은 CAST·ICON을 유지하고 PROJECTILE 네 프레임만 왕관 블록 형태로 수정했다. 생성 결과가 실제 알파 없이 RGB 체크무늬로 나와 납품 PNG로 채택되지 않았으며, 수정 완료 ZIP은 없다(`BLOCKED_ALPHA_NO_CORRECTED_PACKAGE`). 기존 기록에는 기술적 배경 제거에 관한 사용자 응답 대기가 명시돼 있다. 이번 커밋 작업은 이를 실행하지 않는다.
- AREA 12: `AREA_12_IMAGES_OUTPUT_V2_4_FINAL_CANDIDATE.zip`이 작성됐으며, 기록상 역할 PNG 45개 바이트 보존·CRC/경로/역할/프레임/문서 검사 및 재추출이 완료됐다. 사용자 아트 승인은 PENDING, 런타임은 NOT_RUN이다. 이전 목마 CAST 해석 쟁점과 최종 아트 승인 여부를 패키징 성공과 혼동하지 않는다.
- 이 커밋·PR 작업에서 Maker 실행, 새로운 이미지 생성, 게임 반입은 수행하지 않았다. 패키지 검증은 사용자 아트 승인 또는 런타임 PASS가 아니다.

## 머지 전 확인할 기존 작업 상태

`RootDesk/MyDesk/GameData/SkillTable.csv`와 `.userdataset`은 작업 디렉터리에서 삭제 상태였으며 `Mislocated/MyDesk/GameData/`에 같은 이름의 후보 파일이 있다. 위치 변경/복사 흔적을 포함해 현재 상태를 보존했으며, Maker에서 어느 후보를 등록·사용하는지는 이번 커밋 작업에서 검증하지 않았다. 미검증 게임 변경을 포함하므로 런타임 정상 완료 PR로 해석하면 안 된다.

## 인수인계 시작점

- `docs/art/output_audit/BASELINE_OUTPUT_INDEX.csv`
- `docs/art/output_audit/LATEST_REPORT.md`
- `docs/art/output_audit/runs/20260912_160012_story_skill_coherence_r5/STORY_SKILL_SUMMARY.md`
- `docs/art/output_repacked/20260912_153221_v24_repack/`
- `docs/art/output_repacked/20260912_165951_area11_12_final/PACKAGING_STATUS.md`
- `docs/art/output_repacked/20260912_165951_area11_12_final/CANDIDATE_ZIP_INDEX.csv`

원본 및 검수 작업 자료까지 포함하는 대규모 스냅샷이며, 다음 수정에서는 고정 기준 해시를 대조하고 변경된 항목만 재검사한다.
