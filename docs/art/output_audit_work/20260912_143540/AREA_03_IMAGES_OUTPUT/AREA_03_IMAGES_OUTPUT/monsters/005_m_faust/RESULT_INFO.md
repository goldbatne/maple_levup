# RESULT_INFO — 파우스트 / 저주의 인형

- input_zip: `AREA_03_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4`

- monster_id/name: `m_faust` / 파우스트
- skill_id/name/type: `s_mon_faust` / 저주의 인형 / 액티브
- source monster image: `MONSTER_IMAGE.png from input package`

## Roles
### ICON
- production_decision: `NEW_ART`
- files: `monsters/005_m_faust/ICON/005_m_faust_s_mon_faust_ICON.png`
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
- files: `monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F00.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F01.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F02.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F03.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F04.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F05.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F06.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F07.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F08.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F09.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F10.png | monsters/005_m_faust/CAST/005_m_faust_s_mon_faust_CAST_F11.png`
- frame_count: `12`
- canvas: `512x512 RGBA`
- playback: `non-loop one-shot` / frame_seconds=`0.08` / total_seconds=`0.96`
- source_sheet: `monsters/005_m_faust/SOURCE_SHEET/005_m_faust_s_mon_faust_CAST_sheet.png`
- split_coords: `[{"frame": "F00", "x": 0, "y": 0, "w": 512, "h": 512}, {"frame": "F01", "x": 512, "y": 0, "w": 512, "h": 512}, {"frame": "F02", "x": 1024, "y": 0, "w": 512, "h": 512}, {"frame": "F03", "x": 1536, "y": 0, "w": 512, "h": 512}, {"frame": "F04", "x": 0, "y": 512, "w": 512, "h": 512}, {"frame": "F05", "x": 512, "y": 512, "w": 512, "h": 512}, {"frame": "F06", "x": 1024, "y": 512, "w": 512, "h": 512}, {"frame": "F07", "x": 1536, "y": 512, "w": 512, "h": 512}, {"frame": "F08", "x": 0, "y": 1024, "w": 512, "h": 512}, {"frame": "F09", "x": 512, "y": 1024, "w": 512, "h": 512}, {"frame": "F10", "x": 1024, "y": 1024, "w": 512, "h": 512}, {"frame": "F11", "x": 1536, "y": 1024, "w": 512, "h": 512}]`
- inspection:
  - file_count/frame_count: PASS
  - RGBA mode: PASS
  - actual alpha background: PASS
  - blank frame: PASS
  - text/watermark contamination: PASS by visual review
  - semantic correspondence to spec: PASS by visual review
  - USER_ART_APPROVAL: `PENDING`

### PROJECTILE
- production_decision: `NEW_ART`
- files: `monsters/005_m_faust/PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F00.png | monsters/005_m_faust/PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F01.png | monsters/005_m_faust/PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F02.png | monsters/005_m_faust/PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F03.png`
- frame_count: `4`
- canvas: `512x512 RGBA`
- playback: `non-loop complete playback within 0.35s entity lifetime` / frame_seconds=`0.08` / total_seconds=`0.32`
- source_sheet: `monsters/005_m_faust/SOURCE_SHEET/005_m_faust_s_mon_faust_PROJECTILE_sheet.png`
- split_coords: `[{"frame": "F00", "x": 0, "y": 0, "w": 512, "h": 512}, {"frame": "F01", "x": 512, "y": 0, "w": 512, "h": 512}, {"frame": "F02", "x": 0, "y": 512, "w": 512, "h": 512}, {"frame": "F03", "x": 512, "y": 512, "w": 512, "h": 512}]`
- inspection:
  - file_count/frame_count: PASS
  - RGBA mode: PASS
  - actual alpha background: PASS
  - blank frame: PASS
  - text/watermark contamination: PASS by visual review
  - semantic correspondence to spec: PASS by visual review
  - USER_ART_APPROVAL: `PENDING`
