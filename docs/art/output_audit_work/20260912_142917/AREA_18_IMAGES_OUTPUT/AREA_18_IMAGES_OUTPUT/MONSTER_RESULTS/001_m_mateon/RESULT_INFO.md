# RESULT_INFO — 마티안 / 마티안 광선탄

- INPUT ZIP: `AREA_18_IMAGES_INPUT_V2_4(1).zip`
- 기준: V2.4
- area_id: `area_18`
- monster_id / skill_id: `m_mateon` / `s_mon_mateon`
- skill_type: `액티브`
- production: all required roles = `NEW_ART`
- user_art_approval: `PENDING`

## Output files
- `CAST/001_m_mateon_s_mon_mateon_CAST_F00.png` | 384x384 RGBA | alpha 0~251 | CAST_VFX | split `(314, 0, 627, 314)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F01.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(627, 0, 940, 314)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F02.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(940, 0, 1254, 314)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F03.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(0, 314, 314, 627)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F04.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(314, 314, 627, 627)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F05.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(627, 314, 940, 627)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F06.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(940, 314, 1254, 627)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `CAST/001_m_mateon_s_mon_mateon_CAST_F07.png` | 384x384 RGBA | alpha 0~253 | CAST_VFX | split `(0, 627, 314, 940)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `ICON/001_m_mateon_s_mon_mateon_ICON.png` | 256x256 RGBA | alpha 0~253 | ICON | split `(0, 0, 314, 314)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `PROJECTILE/001_m_mateon_s_mon_mateon_PROJECTILE_F00.png` | 384x384 RGBA | alpha 0~241 | PROJECTILE | split `(314, 627, 627, 940)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `PROJECTILE/001_m_mateon_s_mon_mateon_PROJECTILE_F01.png` | 384x384 RGBA | alpha 0~253 | PROJECTILE | split `(627, 627, 940, 940)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `PROJECTILE/001_m_mateon_s_mon_mateon_PROJECTILE_F02.png` | 384x384 RGBA | alpha 0~253 | PROJECTILE | split `(940, 627, 1254, 940)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`
- `PROJECTILE/001_m_mateon_s_mon_mateon_PROJECTILE_F03.png` | 384x384 RGBA | alpha 0~253 | PROJECTILE | split `(0, 940, 314, 1254)` from `SOURCE_SHEETS/001_m_mateon_sheet.png`

## Sources
- MONSTER_IMAGE: `monsters/001_m_mateon_마티안/MONSTER_IMAGE.png`
- generation sheet: `SOURCE_SHEETS/001_m_mateon_sheet.png`
- source style refs: see generation workflow; not bundled as deliverables

## Validation
- frame count / size / RGBA / visible alpha: PASS
- empty frame check: PASS
- checker / opaque square background residue: PASS (pixel alpha inspected)
- sprite-sheet split coordinates recorded: PASS
- user art approval: PENDING