# RESULT_INFO — 플라티안 / 외계 장갑 조종

- INPUT ZIP: `AREA_18_IMAGES_INPUT_V2_4(1).zip`
- 기준: V2.4
- area_id: `area_18`
- monster_id / skill_id: `m_plateon` / `s_mon_plateon`
- skill_type: `패시브`
- production: all required roles = `NEW_ART`
- user_art_approval: `PENDING`

## Output files
- `ICON/002_m_plateon_s_mon_plateon_ICON.png` | 256x256 RGBA | alpha 0~255 | ICON | split `(0, 0, 444, 444)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`
- `REFERENCE/002_m_plateon_s_mon_plateon_REFERENCE_F00.png` | 256x256 RGBA | alpha 0~255 | REFERENCE_VFX | split `(444, 0, 887, 444)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`
- `REFERENCE/002_m_plateon_s_mon_plateon_REFERENCE_F01.png` | 256x256 RGBA | alpha 0~255 | REFERENCE_VFX | split `(887, 0, 1330, 444)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`
- `REFERENCE/002_m_plateon_s_mon_plateon_REFERENCE_F02.png` | 256x256 RGBA | alpha 0~255 | REFERENCE_VFX | split `(1330, 0, 1774, 444)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`
- `REFERENCE/002_m_plateon_s_mon_plateon_REFERENCE_F03.png` | 256x256 RGBA | alpha 0~255 | REFERENCE_VFX | split `(0, 444, 444, 887)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`
- `REFERENCE/002_m_plateon_s_mon_plateon_REFERENCE_F04.png` | 256x256 RGBA | alpha 0~255 | REFERENCE_VFX | split `(444, 444, 887, 887)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`
- `REFERENCE/002_m_plateon_s_mon_plateon_REFERENCE_F05.png` | 256x256 RGBA | alpha 0~255 | REFERENCE_VFX | split `(887, 444, 1330, 887)` from `SOURCE_SHEETS/002_m_plateon_sheet.png`

## Sources
- MONSTER_IMAGE: `monsters/002_m_plateon_플라티안/MONSTER_IMAGE.png`
- generation sheet: `SOURCE_SHEETS/002_m_plateon_sheet.png`
- source style refs: see generation workflow; not bundled as deliverables

## Validation
- frame count / size / RGBA / visible alpha: PASS
- empty frame check: PASS
- checker / opaque square background residue: PASS (pixel alpha inspected)
- sprite-sheet split coordinates recorded: PASS
- user art approval: PENDING