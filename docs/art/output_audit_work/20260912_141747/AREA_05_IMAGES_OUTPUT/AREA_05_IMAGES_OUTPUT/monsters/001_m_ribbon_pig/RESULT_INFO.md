# RESULT_INFO — 리본 돼지 / m_ribbon_pig

- input_zip: AREA_05_IMAGES_INPUT_V2_4(1).zip
- 기준: V2.4 (README_START_HERE / PACKAGE_REVISION_V2_4 / FULL_ART_SCOPE / OUTPUT_REQUIREMENTS)
- area: area_05 / 노틸러스
- skill: s_mon_ribbon_pig / 리본 돌진 / 액티브
- user_art_approval: PENDING

## Produced roles
- ICON: NEW_ART / runtime_use=ui / files=ICON/001_m_ribbon_pig_s_mon_ribbon_pig_ICON.png
- CAST_VFX: NEW_ART / runtime_use=true / files=CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F00.png..._CAST_F07.png

## Files
- ICON: `ICON/001_m_ribbon_pig_s_mon_ribbon_pig_ICON.png` / size=256x256 / frame_index=0 / source_sheet=`SOURCE_SHEETS/icons_SOURCE_SHEET.png` / split_box=(0, 0, 256, 256)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F00.png` / size=384x384 / frame_index=0 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(0, 0, 384, 384)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F01.png` / size=384x384 / frame_index=1 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(384, 0, 768, 384)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F02.png` / size=384x384 / frame_index=2 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(768, 0, 1152, 384)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F03.png` / size=384x384 / frame_index=3 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(1152, 0, 1536, 384)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F04.png` / size=384x384 / frame_index=4 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(0, 384, 384, 768)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F05.png` / size=384x384 / frame_index=5 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(384, 384, 768, 768)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F06.png` / size=384x384 / frame_index=6 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(768, 384, 1152, 768)
- CAST_VFX: `CAST/001_m_ribbon_pig_s_mon_ribbon_pig_CAST_F07.png` / size=384x384 / frame_index=7 / source_sheet=`SOURCE_SHEETS/ribbon_cast_SOURCE_SHEET.png` / split_box=(1152, 384, 1536, 768)

## Sources used
- original monster image: `safe/m001/MONSTER_IMAGE.png`
- style / supporting references:
  - `style_refs/ribbon_cast_l1.png`
  - `style_refs/ribbon_cast_l2.png`
  - `style_refs/ribbon_icon_ref.png`
- generation original: image_gen sprite sheet output, preserved under `SOURCE_SHEETS/`

## Validation
- ICON: RGBA=PASS / background_alpha=PASS / transparent_corners=PASS / edge_touch_suspect=SUSPECT_TOUCHING_EDGE
- CAST_VFX: RGBA=PASS / background_alpha=PASS / transparent_corners=PASS,WARN / edge_touch_suspect=SUSPECT_TOUCHING_EDGE
- empty_frame_check: PASS (all required produced frames had non-empty alpha bbox)
- byte-identity approved reuse: NOT_APPLICABLE
- text contamination / wrong motif manual review: PASS (visual review)
- imported runtime verification: NOT_CHECKED
- cell fragment contamination: NOT_CHECKED
