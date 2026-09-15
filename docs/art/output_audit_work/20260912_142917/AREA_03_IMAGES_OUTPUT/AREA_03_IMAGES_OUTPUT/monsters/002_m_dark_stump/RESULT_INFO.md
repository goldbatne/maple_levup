# RESULT_INFO — 다크 스텀프 / 단단한 밑동

- input_zip: `AREA_03_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4`

- monster_id/name: `m_dark_stump` / 다크 스텀프
- skill_id/name/type: `s_mon_dark_stump` / 단단한 밑동 / 버프
- source monster image: `MONSTER_IMAGE.png from input package`

## Roles
### ICON
- production_decision: `NEW_ART`
- files: `monsters/002_m_dark_stump/ICON/002_m_dark_stump_s_mon_dark_stump_ICON.png`
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
- files: `monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F00.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F01.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F02.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F03.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F04.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F05.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F06.png | monsters/002_m_dark_stump/CAST/002_m_dark_stump_s_mon_dark_stump_CAST_F07.png`
- frame_count: `8`
- canvas: `256x256 RGBA`
- playback: `non-loop one-shot` / frame_seconds=`0.1` / total_seconds=`0.8`
- source_sheet: `monsters/002_m_dark_stump/SOURCE_SHEET/002_m_dark_stump_s_mon_dark_stump_CAST_sheet.png`
- split_coords: `[{"frame": "F00", "x": 0, "y": 0, "w": 256, "h": 256}, {"frame": "F01", "x": 256, "y": 0, "w": 256, "h": 256}, {"frame": "F02", "x": 512, "y": 0, "w": 256, "h": 256}, {"frame": "F03", "x": 768, "y": 0, "w": 256, "h": 256}, {"frame": "F04", "x": 0, "y": 256, "w": 256, "h": 256}, {"frame": "F05", "x": 256, "y": 256, "w": 256, "h": 256}, {"frame": "F06", "x": 512, "y": 256, "w": 256, "h": 256}, {"frame": "F07", "x": 768, "y": 256, "w": 256, "h": 256}]`
- inspection:
  - file_count/frame_count: PASS
  - RGBA mode: PASS
  - actual alpha background: PASS
  - blank frame: PASS
  - text/watermark contamination: PASS by visual review
  - semantic correspondence to spec: PASS by visual review
  - USER_ART_APPROVAL: `PENDING`
