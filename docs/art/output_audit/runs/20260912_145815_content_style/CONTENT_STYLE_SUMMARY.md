# Monster Skill OUTPUT Content & Cross-Area Style Review

## 범위와 재사용 근거

- 검수 대상: AREA 01~20 실제 19개(예약 결번 AREA 06 제외), 몬스터/스킬 99쌍.
- 기준: 고정 `BASELINE_INDEX.csv`, `AUDIT_RULES.md`, 승인 INPUT V2.4, AREA 00 승인본.
- 직전 기계 검사는 OUTPUT 19개 ZIP의 SHA-256이 모두 동일한 경우만 재사용했다. 상세는 `REUSED_FILE_CHECKS.csv`.
- 직전 `VISUAL_REVIEW.csv`의 동일 반복 문구는 근거로 재사용하지 않았다. 실제 ICON과 역할별 VFX 전 프레임을 `area_full_frame_boards`로 다시 열고, OUTPUT Area Preview 및 INPUT 핵심 소재·역할·흐름과 대조했다.
- 신규 아트 생성, 알파/크롭 수정, 원본 ZIP 변경, 게임 반입은 수행하지 않았다.

## 판정 집계

| 구분 | 결과 | 수 |
|---|---:|---:|
| 설정 적합성 | NO_OBVIOUS_ISSUE | 97 |
| 설정 적합성 | SPEC_MISMATCH | 1 |
| 설정 적합성 | NEEDS_USER_REVIEW | 1 |
| 스타일 | CONSISTENT_WITH_REFERENCE | 99 |
| 스타일 | STYLE_OUTLIER | 0 |
| Preview | 실제 납품 이미지 일치 | 94 |
| Preview | 이미지 일치·라벨 렌더링 문제 | 5개 몬스터 행(AREA 09 Preview 1개) |

`NO_OBVIOUS_ISSUE`와 `CONSISTENT_WITH_REFERENCE`는 사용자 승인이 아니다.

## 설정 불일치 — 원화 수정 후보

| Area | 몬스터 / 스킬 | 역할 | 판정 | 이유 | 조치 |
|---|---|---|---|---|---|
| AREA 11 | 킹 블록퍼스 / 왕관 블록탄 | CAST_VFX, PROJECTILE | SPEC_MISMATCH | INPUT은 왕관 블록·각진 에너지 조각을 요구하며 본체/얼굴을 금지하지만, 실제 프레임은 왕관·눈·포신이 붙은 축소 몬스터 본체를 반복한다. ICON은 허용 모티브라 제외한다. | REGENERATE_CANDIDATE |

비교 이미지: `docs/art/output_audit/runs/20260912_145815_content_style/issue_comparisons/AREA_11_m_king_bloctopus_CAST_PROJECTILE.png`

## 사용자 판단 필요

| Area | 몬스터 / 스킬 | 역할 | 이유 | 조치 |
|---|---|---|---|---|
| AREA 12 | 장난감 목마 / 태엽 목마 돌진 | CAST_VFX | 휠·태엽은 명세와 맞지만 눈 달린 목마 머리/몸통 조각이 CAST의 금지된 본체 삽입인지, ICON에 허용된 목마 모티브의 확장인지 INPUT만으로 단정하기 어렵다. | USER_REVIEW |

비교 이미지: `docs/art/output_audit/runs/20260912_145815_content_style/issue_comparisons/AREA_12_m_toy_trojan_CAST.png`

## Area 간 스타일 일관성

- 확정 `STYLE_OUTLIER`는 0건이다.
- AREA 00의 저레벨 크기를 고레벨·보스에 강제하지 않고, 비슷한 역할끼리 외곽선·명암·재질·발광·알파 가장자리·입자·소멸·ICON 가독성을 비교했다.
- 99쌍 모두 마감 문법은 AREA 00 승인본과 이어진다. 위 AREA 11 문제는 마감 스타일이 아니라 명세의 WHAT/금지요소 충돌이다.
- AREA 04 스티지, AREA 19 정식기사 D처럼 선형·저밀도인 패시브 REFERENCE_VFX도 역할상 공격 절정을 요구하지 않으며, ICON 및 알파 감쇠는 공통 문법을 유지해 STYLE_OUTLIER로 판정하지 않았다.

전체 비교: `CROSS_AREA_STYLE_BOARD/page_01.png` ~ `page_05.png`  
Area별 전 프레임: `area_full_frame_boards/AREA_XX_ALL_FRAMES.png`

## REPACK_ONLY와 원화 조치의 분리

- 직전 기계 감사에서 19개 Area 모두 파일/Manifest/RESULT_INFO/Preview 구조 중 하나 이상이 실패했으므로 패키지 정리는 모두 `REPACK_ONLY` 대상이다: area_01, area_02, area_03, area_04, area_05, area_07, area_08, area_09, area_10, area_11, area_12, area_13, area_14, area_15, area_16, area_17, area_18, area_19, area_20.
- AREA 09의 `AREA_OVERVIEW_PREVIEW.png`는 실제 ICON/VFX 배열은 일치하지만 한글 라벨이 네모 글리프로 깨진다. Preview 합성만 고칠 `REPACK_ONLY` 항목이며 원화 재생성 사유가 아니다.
- AREA 11 킹 블록퍼스의 CAST_VFX/PROJECTILE만 `REGENERATE_CANDIDATE`다. 사용자 확인 전에는 수정하지 않는다.
- AREA 12 장난감 목마 CAST_VFX는 `USER_REVIEW`이며 재생성 확정이 아니다.
- 그 밖의 원화는 이번 추가 검수에서 재생성 후보로 올리지 않았다.

## 증빙 위치

- 상세 판정: `CONTENT_STYLE_REVIEW.csv`
- 갱신 조치: `ACTION_ITEMS_UPDATED.csv`
- 비교 보드: `CROSS_AREA_STYLE_BOARD/`
- 문제 확대: `issue_comparisons/`
- 긴 Preview 검수용 축소본(원본 무변경): `preview_checks/`
