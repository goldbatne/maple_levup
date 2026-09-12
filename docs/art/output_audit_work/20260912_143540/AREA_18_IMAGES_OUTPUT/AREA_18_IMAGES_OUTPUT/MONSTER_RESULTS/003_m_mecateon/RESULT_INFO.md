# RESULT_INFO — 메카티안 / 기계화 레이저

- INPUT ZIP: `AREA_18_IMAGES_INPUT_V2_4(1).zip`
- 기준: V2.4
- area_id: `area_18`
- monster_id / skill_id: `m_mecateon` / `s_mon_mecateon`
- skill_type: `액티브`
- production: all required roles = `NEW_ART`
- user_art_approval: `PENDING`

## Output files
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F00.png` | 384x384 RGBA | alpha 0~254 | CAST_VFX | split `(418, 0, 836, 418)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F01.png` | 384x384 RGBA | alpha 0~255 | CAST_VFX | split `(836, 0, 1254, 418)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F02.png` | 384x384 RGBA | alpha 0~255 | CAST_VFX | split `(0, 418, 418, 836)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F03.png` | 384x384 RGBA | alpha 0~254 | CAST_VFX | split `(418, 418, 836, 836)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F04.png` | 384x384 RGBA | alpha 0~255 | CAST_VFX | split `(836, 418, 1254, 836)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F05.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(0, 836, 418, 1254)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F06.png` | 384x384 RGBA | alpha 0~255 | CAST_VFX | split `(418, 836, 836, 1254)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `CAST/003_m_mecateon_s_mon_mecateon_CAST_F07.png` | 384x384 RGBA | alpha 0~255 | CAST_VFX | split `(836, 836, 1254, 1254)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- `ICON/003_m_mecateon_s_mon_mecateon_ICON.png` | 256x256 RGBA | alpha 0~255 | ICON | split `(0, 0, 418, 418)` from `SOURCE_SHEETS/003_m_mecateon_sheet.png`

## Sources
- MONSTER_IMAGE: `monsters/003_m_mecateon_메카티안/MONSTER_IMAGE.png`
- generation sheet: `SOURCE_SHEETS/003_m_mecateon_sheet.png`
- source style refs: see generation workflow; not bundled as deliverables

## Validation
- frame count / size / RGBA / visible alpha: PASS
- empty frame check: PASS
- checker / opaque square background residue: PASS (pixel alpha inspected)
- sprite-sheet split coordinates recorded: PASS
- user art approval: PENDING