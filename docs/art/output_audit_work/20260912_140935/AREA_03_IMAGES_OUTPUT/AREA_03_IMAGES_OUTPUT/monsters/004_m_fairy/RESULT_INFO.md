# RESULT_INFO — 페어리 / 요정의 마법가루

- input_zip: `AREA_03_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4`

- monster_id/name: `m_fairy` / 페어리
- skill_id/name/type: `s_mon_fairy` / 요정의 마법가루 / 액티브
- source monster image: `MONSTER_IMAGE.png from input package`

## Roles
### ICON
- production_decision: `NEW_ART`
- files: `monsters/004_m_fairy/ICON/004_m_fairy_s_mon_fairy_ICON.png`
- frame_count: `1`
- canvas: `256x256 RGBA`
- playback: `static` / frame_seconds=`static` / total_seconds=`static`
- source_sheet: `N/A (single icon or direct approved reuse copy)`
- inspection:
  - file_count/frame_count: PASS
  - RGBA mode: PASS
  - actual alpha background: PASS
  - blank frame: PASS
  - text/watermark contamination: PASS by visual review
  - semantic correspondence to spec: PASS by visual review
  - USER_ART_APPROVAL: `PENDING`

### CAST_VFX
- production_decision: `NEW_ART`
- files: `monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F00.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F01.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F02.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F03.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F04.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F05.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F06.png | monsters/004_m_fairy/CAST/004_m_fairy_s_mon_fairy_CAST_F07.png`
- frame_count: `8`
- canvas: `384x384 RGBA`
- playback: `non-loop one-shot` / frame_seconds=`0.1` / total_seconds=`0.8`
- source_sheet: `monsters/004_m_fairy/SOURCE_SHEET/004_m_fairy_s_mon_fairy_CAST_sheet.png`
- split_coords: `[{"frame": "F00", "x": 0, "y": 0, "w": 384, "h": 384}, {"frame": "F01", "x": 384, "y": 0, "w": 384, "h": 384}, {"frame": "F02", "x": 768, "y": 0, "w": 384, "h": 384}, {"frame": "F03", "x": 1152, "y": 0, "w": 384, "h": 384}, {"frame": "F04", "x": 0, "y": 384, "w": 384, "h": 384}, {"frame": "F05", "x": 384, "y": 384, "w": 384, "h": 384}, {"frame": "F06", "x": 768, "y": 384, "w": 384, "h": 384}, {"frame": "F07", "x": 1152, "y": 384, "w": 384, "h": 384}]`
- inspection:
  - file_count/frame_count: PASS
  - RGBA mode: PASS
  - actual alpha background: PASS
  - blank frame: PASS
  - text/watermark contamination: PASS by visual review
  - semantic correspondence to spec: PASS by visual review
  - USER_ART_APPROVAL: `PENDING`
