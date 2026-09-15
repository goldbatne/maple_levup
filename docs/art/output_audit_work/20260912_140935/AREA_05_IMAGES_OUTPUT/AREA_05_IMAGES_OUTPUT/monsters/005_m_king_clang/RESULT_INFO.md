# RESULT_INFO — 킹크랑 / m_king_clang

- input_zip: AREA_05_IMAGES_INPUT_V2_4(1).zip
- 기준: V2.4 (README_START_HERE / PACKAGE_REVISION_V2_4 / FULL_ART_SCOPE / OUTPUT_REQUIREMENTS)
- area: area_05 / 노틸러스
- skill: s_mon_king_clang / 왕게의 집게 파도 / 액티브
- user_art_approval: PENDING

## Produced roles
- ICON: NEW_ART / runtime_use=ui / files=ICON/005_m_king_clang_s_mon_king_clang_ICON.png
- CAST_VFX: NEW_ART / runtime_use=true / files=CAST/005_m_king_clang_s_mon_king_clang_CAST_F00.png..._CAST_F11.png

## Files
- ICON: `ICON/005_m_king_clang_s_mon_king_clang_ICON.png` / size=256x256 / frame_index=0 / source_sheet=`SOURCE_SHEETS/icons_SOURCE_SHEET.png` / split_box=(256, 256, 512, 512)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F00.png` / size=512x512 / frame_index=0 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(0, 0, 512, 512)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F01.png` / size=512x512 / frame_index=1 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(512, 0, 1024, 512)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F02.png` / size=512x512 / frame_index=2 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(1024, 0, 1536, 512)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F03.png` / size=512x512 / frame_index=3 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(1536, 0, 2048, 512)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F04.png` / size=512x512 / frame_index=4 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(0, 512, 512, 1024)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F05.png` / size=512x512 / frame_index=5 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(512, 512, 1024, 1024)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F06.png` / size=512x512 / frame_index=6 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(1024, 512, 1536, 1024)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F07.png` / size=512x512 / frame_index=7 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(1536, 512, 2048, 1024)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F08.png` / size=512x512 / frame_index=8 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(0, 1024, 512, 1536)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F09.png` / size=512x512 / frame_index=9 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(512, 1024, 1024, 1536)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F10.png` / size=512x512 / frame_index=10 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(1024, 1024, 1536, 1536)
- CAST_VFX: `CAST/005_m_king_clang_s_mon_king_clang_CAST_F11.png` / size=512x512 / frame_index=11 / source_sheet=`SOURCE_SHEETS/king_cast_SOURCE_SHEET.png` / split_box=(1536, 1024, 2048, 1536)

## Sources used
- original monster image: `safe/m005/MONSTER_IMAGE.png`
- style / supporting references:
  - `style_refs/king_cast_l1.png`
  - `style_refs/king_cast_l2.png`
- generation original: image_gen sprite sheet output, preserved under `SOURCE_SHEETS/`

## Validation
- ICON: RGBA=PASS / background_alpha=PASS / transparent_corners=PASS / edge_touch_suspect=SUSPECT_TOUCHING_EDGE
- CAST_VFX: RGBA=PASS / background_alpha=PASS / transparent_corners=PASS,WARN / edge_touch_suspect=SUSPECT_TOUCHING_EDGE
- empty_frame_check: PASS (all required produced frames had non-empty alpha bbox)
- byte-identity approved reuse: NOT_APPLICABLE
- text contamination / wrong motif manual review: PASS (visual review)
- imported runtime verification: NOT_CHECKED
- cell fragment contamination: NOT_CHECKED
