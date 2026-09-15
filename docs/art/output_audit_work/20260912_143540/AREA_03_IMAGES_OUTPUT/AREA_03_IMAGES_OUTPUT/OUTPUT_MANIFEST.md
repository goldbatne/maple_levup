# OUTPUT_MANIFEST — AREA 03 엘리니아

- input_zip: `AREA_03_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4 current package spec`
- processed_monsters: `5`
- role_count_new_art: `9`
- role_count_approved_reuse: `2`

## Warnings
- 신규 아트 9개 역할의 USER_ART_APPROVAL = PENDING
- 승인 재사용 2개 역할은 Area 00 승인 파일을 byte-preserving copy

## Deliverables
- `AREA_OVERVIEW_PREVIEW.png`
- `monsters/001_m_slime/PREVIEW/labeled_preview.png`
- `monsters/002_m_dark_stump/PREVIEW/labeled_preview.png`
- `monsters/003_m_bubbling/PREVIEW/labeled_preview.png`
- `monsters/004_m_fairy/PREVIEW/labeled_preview.png`
- `monsters/005_m_faust/PREVIEW/labeled_preview.png`

## Role Summary
### 001 슬라임 / 끈적한 몸통
- ICON: AREA00_APPROVED_REUSE / 1 files / 256x256 RGBA / static
- CAST_VFX: AREA00_APPROVED_REUSE / 8 files / 256x256 RGBA / approved existing
### 002 다크 스텀프 / 단단한 밑동
- ICON: NEW_ART / 1 files / 256x256 RGBA / static
- CAST_VFX: NEW_ART / 8 files / 256x256 RGBA / non-loop one-shot
### 003 버블링 / 물방울 마력
- ICON: NEW_ART / 1 files / 256x256 RGBA / static
- REFERENCE_VFX: NEW_ART / 6 files / 256x256 RGBA / preview-only non-loop
### 004 페어리 / 요정의 마법가루
- ICON: NEW_ART / 1 files / 256x256 RGBA / static
- CAST_VFX: NEW_ART / 8 files / 384x384 RGBA / non-loop one-shot
### 005 파우스트 / 저주의 인형
- ICON: NEW_ART / 1 files / 256x256 RGBA / static
- CAST_VFX: NEW_ART / 12 files / 512x512 RGBA / non-loop one-shot
- PROJECTILE: NEW_ART / 4 files / 512x512 RGBA / non-loop complete playback within 0.35s entity lifetime

상세 파일 경로·분할 좌표·검사 결과는 `OUTPUT_MANIFEST.csv`와 각 몬스터의 `RESULT_INFO.md` 참조.