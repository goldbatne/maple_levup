# RESULT_INFO — 버블링 / 물방울 마력

- input_zip: `AREA_03_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4`

- monster_id/name: `m_bubbling` / 버블링
- skill_id/name/type: `s_mon_bubbling` / 물방울 마력 / 패시브
- source monster image: `MONSTER_IMAGE.png from input package`

## Roles
### ICON
- production_decision: `NEW_ART`
- files: `monsters/003_m_bubbling/ICON/003_m_bubbling_s_mon_bubbling_ICON.png`
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

### REFERENCE_VFX
- production_decision: `NEW_ART`
- files: `monsters/003_m_bubbling/REFERENCE/003_m_bubbling_s_mon_bubbling_REFERENCE_F00.png | monsters/003_m_bubbling/REFERENCE/003_m_bubbling_s_mon_bubbling_REFERENCE_F01.png | monsters/003_m_bubbling/REFERENCE/003_m_bubbling_s_mon_bubbling_REFERENCE_F02.png | monsters/003_m_bubbling/REFERENCE/003_m_bubbling_s_mon_bubbling_REFERENCE_F03.png | monsters/003_m_bubbling/REFERENCE/003_m_bubbling_s_mon_bubbling_REFERENCE_F04.png | monsters/003_m_bubbling/REFERENCE/003_m_bubbling_s_mon_bubbling_REFERENCE_F05.png`
- frame_count: `6`
- canvas: `256x256 RGBA`
- playback: `preview-only non-loop` / frame_seconds=`0.1` / total_seconds=`0.6`
- source_sheet: `monsters/003_m_bubbling/SOURCE_SHEET/003_m_bubbling_s_mon_bubbling_REFERENCE_sheet.png`
- split_coords: `[{"frame": "F00", "x": 0, "y": 0, "w": 256, "h": 256}, {"frame": "F01", "x": 256, "y": 0, "w": 256, "h": 256}, {"frame": "F02", "x": 512, "y": 0, "w": 256, "h": 256}, {"frame": "F03", "x": 0, "y": 256, "w": 256, "h": 256}, {"frame": "F04", "x": 256, "y": 256, "w": 256, "h": 256}, {"frame": "F05", "x": 512, "y": 256, "w": 256, "h": 256}]`
- inspection:
  - file_count/frame_count: PASS
  - RGBA mode: PASS
  - actual alpha background: PASS
  - blank frame: PASS
  - text/watermark contamination: PASS by visual review
  - semantic correspondence to spec: PASS by visual review
  - USER_ART_APPROVAL: `PENDING`
