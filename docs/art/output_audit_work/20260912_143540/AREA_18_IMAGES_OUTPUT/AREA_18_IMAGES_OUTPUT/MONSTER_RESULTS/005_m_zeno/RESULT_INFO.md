# RESULT_INFO — 제노 / 제노의 중력장

- INPUT ZIP: `AREA_18_IMAGES_INPUT_V2_4(1).zip`
- 기준: V2.4
- area_id: `area_18`
- monster_id / skill_id: `m_zeno` / `s_mon_zeno`
- skill_type: `액티브`
- production: all required roles = `NEW_ART`
- user_art_approval: `PENDING`

## Output files
- `CAST/005_m_zeno_s_mon_zeno_CAST_F00.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(314, 0, 627, 314)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F01.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(627, 0, 940, 314)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F02.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(940, 0, 1254, 314)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F03.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(0, 314, 314, 627)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F04.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(314, 314, 627, 627)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F05.png` | 512x512 RGBA | alpha 0~255 | CAST_VFX | split `(627, 314, 940, 627)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F06.png` | 512x512 RGBA | alpha 0~254 | CAST_VFX | split `(940, 314, 1254, 627)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F07.png` | 512x512 RGBA | alpha 0~255 | CAST_VFX | split `(0, 627, 314, 940)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F08.png` | 512x512 RGBA | alpha 0~255 | CAST_VFX | split `(314, 627, 627, 940)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F09.png` | 512x512 RGBA | alpha 0~254 | CAST_VFX | split `(627, 627, 940, 940)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F10.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(940, 627, 1254, 940)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `CAST/005_m_zeno_s_mon_zeno_CAST_F11.png` | 512x512 RGBA | alpha 0~253 | CAST_VFX | split `(0, 940, 314, 1254)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`
- `ICON/005_m_zeno_s_mon_zeno_ICON.png` | 256x256 RGBA | alpha 0~253 | ICON | split `(0, 0, 314, 314)` from `SOURCE_SHEETS/005_m_zeno_sheet.png`

## Sources
- MONSTER_IMAGE: `monsters/005_m_zeno_제노/MONSTER_IMAGE.png`
- generation sheet: `SOURCE_SHEETS/005_m_zeno_sheet.png`
- source style refs: see generation workflow; not bundled as deliverables

## Validation
- frame count / size / RGBA / visible alpha: PASS
- empty frame check: PASS
- checker / opaque square background residue: PASS (pixel alpha inspected)
- sprite-sheet split coordinates recorded: PASS
- user art approval: PENDING