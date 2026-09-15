# RESULT_INFO — 파란 리본돼지 / m_blue_pig

- input_zip: AREA_05_IMAGES_INPUT_V2_4(1).zip
- 기준: V2.4 (README_START_HERE / PACKAGE_REVISION_V2_4 / FULL_ART_SCOPE / OUTPUT_REQUIREMENTS)
- area: area_05 / 노틸러스
- skill: s_mon_blue_pig / 푸른 리본 매듭 / 패시브
- user_art_approval: PENDING

## Produced roles
- ICON: NEW_ART / runtime_use=ui / files=ICON/002_m_blue_pig_s_mon_blue_pig_ICON.png
- REFERENCE_VFX: NEW_ART / runtime_use=false / files=REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F00.png..._REFERENCE_F05.png

## Files
- ICON: `ICON/002_m_blue_pig_s_mon_blue_pig_ICON.png` / size=256x256 / frame_index=0 / source_sheet=`SOURCE_SHEETS/icons_SOURCE_SHEET.png` / split_box=(256, 0, 512, 256)
- REFERENCE_VFX: `REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F00.png` / size=256x256 / frame_index=0 / source_sheet=`SOURCE_SHEETS/blue_ref_SOURCE_SHEET.png` / split_box=(0, 0, 256, 256)
- REFERENCE_VFX: `REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F01.png` / size=256x256 / frame_index=1 / source_sheet=`SOURCE_SHEETS/blue_ref_SOURCE_SHEET.png` / split_box=(256, 0, 512, 256)
- REFERENCE_VFX: `REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F02.png` / size=256x256 / frame_index=2 / source_sheet=`SOURCE_SHEETS/blue_ref_SOURCE_SHEET.png` / split_box=(512, 0, 768, 256)
- REFERENCE_VFX: `REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F03.png` / size=256x256 / frame_index=3 / source_sheet=`SOURCE_SHEETS/blue_ref_SOURCE_SHEET.png` / split_box=(0, 256, 256, 512)
- REFERENCE_VFX: `REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F04.png` / size=256x256 / frame_index=4 / source_sheet=`SOURCE_SHEETS/blue_ref_SOURCE_SHEET.png` / split_box=(256, 256, 512, 512)
- REFERENCE_VFX: `REFERENCE/002_m_blue_pig_s_mon_blue_pig_REFERENCE_F05.png` / size=256x256 / frame_index=5 / source_sheet=`SOURCE_SHEETS/blue_ref_SOURCE_SHEET.png` / split_box=(512, 256, 768, 512)

## Sources used
- original monster image: `safe/m002/MONSTER_IMAGE.png`
- style / supporting references:
  - `style_refs/blue_icon_ref.png`
- generation original: image_gen sprite sheet output, preserved under `SOURCE_SHEETS/`

## Validation
- ICON: RGBA=PASS / background_alpha=PASS / transparent_corners=PASS / edge_touch_suspect=SUSPECT_TOUCHING_EDGE
- REFERENCE_VFX: RGBA=PASS / background_alpha=PASS / transparent_corners=PASS / edge_touch_suspect=SUSPECT_TOUCHING_EDGE
- empty_frame_check: PASS (all required produced frames had non-empty alpha bbox)
- byte-identity approved reuse: NOT_APPLICABLE
- text contamination / wrong motif manual review: PASS (visual review)
- imported runtime verification: NOT_CHECKED
- cell fragment contamination: NOT_CHECKED
