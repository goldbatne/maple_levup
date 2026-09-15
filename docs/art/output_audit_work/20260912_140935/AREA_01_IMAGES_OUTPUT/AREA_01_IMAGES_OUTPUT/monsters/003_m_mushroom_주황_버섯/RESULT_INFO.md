# RESULT_INFO — 주황 버섯 / 포자 살포

- INPUT ZIP: `AREA_01_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4`
- area_id: `area_01` / 헤네시스 근교
- monster_id: `m_mushroom` / 주황 버섯
- skill_id: `s_mon_mushroom` / 포자 살포
- skill_type: `액티브`
- preview: `PREVIEW/labeled_preview.png`

## Roles
### ICON
- production_decision: `NEW_ART`
- runtime_use: `ui`
- frame_count: `1`
- canvas: `256x256 RGBA`
- playback: `static` / frame_seconds=static / total=static
- files:
  - `ICON/003_m_mushroom_s_mon_mushroom_ICON.png`
- source: image_gen generated icon
- source_origin: image_gen original art + python split/resize
- user_art_approval: `PENDING`
- auto_validation: alpha=PASS / blank_frame=PASS / unchecked_items=none

### CAST
- production_decision: `NEW_ART`
- runtime_use: `true`
- frame_count: `8`
- canvas: `384x384 RGBA`
- playback: `non-loop one-shot` / frame_seconds=0.10 / total=0.80
- source_sheet: `monsters/003_m_mushroom_주황_버섯/SOURCE_SHEET/003_m_mushroom_s_mon_mushroom_CAST_SOURCE_SHEET.png`
- split_coords: `[{"frame": 0, "box": [0, 0, 384, 384]}, {"frame": 1, "box": [384, 0, 768, 384]}, {"frame": 2, "box": [768, 0, 1152, 384]}, {"frame": 3, "box": [1152, 0, 1536, 384]}, {"frame": 4, "box": [0, 384, 384, 768]}, {"frame": 5, "box": [384, 384, 768, 768]}, {"frame": 6, "box": [768, 384, 1152, 768]}, {"frame": 7, "box": [1152, 384, 1536, 768]}]`
- files:
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F00.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F01.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F02.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F03.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F04.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F05.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F06.png`
  - `CAST/003_m_mushroom_s_mon_mushroom_CAST_F07.png`
- source: monsters/003_m_mushroom_주황_버섯/SOURCE_SHEET/003_m_mushroom_s_mon_mushroom_CAST_SOURCE_SHEET.png
- source_origin: image_gen original art + python split/resize
- user_art_approval: `PENDING`
- auto_validation: alpha=PASS / blank_frame=PASS / unchecked_items=none
