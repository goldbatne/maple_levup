# RESULT_INFO — 004 / 상급기사 B / 상급기사의 이프리트 화염

- input_zip: `AREA_19_IMAGES_INPUT_V2_4(2).zip`
- basis_revision: `V2.4 current contract`
- monster_id: `m_advanced_knight_b` / monster_name: `상급기사 B`
- skill_id: `s_mon_advanced_knight_b` / skill_name: `상급기사의 이프리트 화염` / skill_type: `액티브`
- production: `NEW_ART`
- user_art_approval: `PENDING`
- preview_file: `PREVIEW/labeled_preview.png`

## Output roles

| role | decision | runtime_use | files | frame_count | canvas | playback |
|---|---|---|---|---:|---|---|
| CAST_VFX | NEW_ART | true | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F00.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F01.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F02.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F03.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F04.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F05.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F06.png | CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F07.png` | 8 | 384x384 RGBA | non-loop one-shot |
| ICON | NEW_ART | ui | `ICON/004_m_advanced_knight_b_s_mon_advanced_knight_b_ICON.png` | 1 | 256x256 RGBA | static |

## Source provenance

- source monster image: `monsters/004_m_advanced_knight_b/MONSTER_IMAGE.png`
- generated source sheet: `SOURCE_SHEETS/004_m_advanced_knight_b_s_mon_advanced_knight_b_SOURCE_SHEET.png`
- source of generated originals: image generation based on current INPUT V2.4 package and monster-specific GENERATION_SPEC

## Split coordinates from source sheet

| role | frame | cell_index | source_box(x0,y0,x1,y1) | output_path |
|---|---:|---:|---|---|
| CAST_VFX | 0 | 0 | `(0, 0, 418, 418)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F00.png` |
| CAST_VFX | 1 | 1 | `(418, 0, 836, 418)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F01.png` |
| CAST_VFX | 2 | 2 | `(836, 0, 1254, 418)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F02.png` |
| CAST_VFX | 3 | 3 | `(0, 418, 418, 836)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F03.png` |
| CAST_VFX | 4 | 4 | `(418, 418, 836, 836)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F04.png` |
| CAST_VFX | 5 | 5 | `(836, 418, 1254, 836)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F05.png` |
| CAST_VFX | 6 | 6 | `(0, 836, 418, 1254)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F06.png` |
| CAST_VFX | 7 | 7 | `(418, 836, 836, 1254)` | `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F07.png` |
| ICON | 0 | 8 | `(836, 836, 1254, 1254)` | `ICON/004_m_advanced_knight_b_s_mon_advanced_knight_b_ICON.png` |

## Validation

| file | mode | size | alpha_min | alpha_max | visible_pixels | status |
|---|---|---|---:|---:|---:|---|
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F00.png` | RGBA | 384x384 | 0 | 250 | 48248 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F01.png` | RGBA | 384x384 | 0 | 252 | 63154 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F02.png` | RGBA | 384x384 | 0 | 253 | 80161 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F03.png` | RGBA | 384x384 | 0 | 255 | 96588 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F04.png` | RGBA | 384x384 | 0 | 254 | 114288 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F05.png` | RGBA | 384x384 | 0 | 253 | 94097 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F06.png` | RGBA | 384x384 | 0 | 255 | 83331 | PASS |
| `CAST/004_m_advanced_knight_b_s_mon_advanced_knight_b_CAST_F07.png` | RGBA | 384x384 | 0 | 252 | 76470 | PASS |
| `ICON/004_m_advanced_knight_b_s_mon_advanced_knight_b_ICON.png` | RGBA | 256x256 | 0 | 253 | 37644 | PASS |

## Checks and notes

- actual alpha background: PASS
- frame count / numbering / canvas size: PASS
- empty required frame: PASS
- text contamination: PASS (manual visual check)
- cell fragment mixing: PASS (manual visual check)
- byte-preserving approved reuse: NOT_APPLICABLE
- runtime/import validation: NOT_CHECKED
- unmet items: none