# RESULT_INFO — 001 / 정식기사 C / 기사단 뇌전 연각

- input_zip: `AREA_19_IMAGES_INPUT_V2_4(2).zip`
- basis_revision: `V2.4 current contract`
- monster_id: `m_official_knight_c` / monster_name: `정식기사 C`
- skill_id: `s_mon_official_knight_c` / skill_name: `기사단 뇌전 연각` / skill_type: `액티브`
- production: `NEW_ART`
- user_art_approval: `PENDING`
- preview_file: `PREVIEW/labeled_preview.png`

## Output roles

| role | decision | runtime_use | files | frame_count | canvas | playback |
|---|---|---|---|---:|---|---|
| CAST_VFX | NEW_ART | true | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F00.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F01.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F02.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F03.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F04.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F05.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F06.png | CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F07.png` | 8 | 384x384 RGBA | non-loop one-shot |
| ICON | NEW_ART | ui | `ICON/001_m_official_knight_c_s_mon_official_knight_c_ICON.png` | 1 | 256x256 RGBA | static |

## Source provenance

- source monster image: `monsters/001_m_official_knight_c/MONSTER_IMAGE.png`
- generated source sheet: `SOURCE_SHEETS/001_m_official_knight_c_s_mon_official_knight_c_SOURCE_SHEET.png`
- source of generated originals: image generation based on current INPUT V2.4 package and monster-specific GENERATION_SPEC

## Split coordinates from source sheet

| role | frame | cell_index | source_box(x0,y0,x1,y1) | output_path |
|---|---:|---:|---|---|
| CAST_VFX | 0 | 0 | `(0, 0, 418, 418)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F00.png` |
| CAST_VFX | 1 | 1 | `(418, 0, 836, 418)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F01.png` |
| CAST_VFX | 2 | 2 | `(836, 0, 1254, 418)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F02.png` |
| CAST_VFX | 3 | 3 | `(0, 418, 418, 836)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F03.png` |
| CAST_VFX | 4 | 4 | `(418, 418, 836, 836)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F04.png` |
| CAST_VFX | 5 | 5 | `(836, 418, 1254, 836)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F05.png` |
| CAST_VFX | 6 | 6 | `(0, 836, 418, 1254)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F06.png` |
| CAST_VFX | 7 | 7 | `(418, 836, 836, 1254)` | `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F07.png` |
| ICON | 0 | 8 | `(836, 836, 1254, 1254)` | `ICON/001_m_official_knight_c_s_mon_official_knight_c_ICON.png` |

## Validation

| file | mode | size | alpha_min | alpha_max | visible_pixels | status |
|---|---|---|---:|---:|---:|---|
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F00.png` | RGBA | 384x384 | 0 | 255 | 58760 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F01.png` | RGBA | 384x384 | 0 | 253 | 77369 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F02.png` | RGBA | 384x384 | 0 | 253 | 98140 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F03.png` | RGBA | 384x384 | 0 | 252 | 88364 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F04.png` | RGBA | 384x384 | 0 | 253 | 106728 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F05.png` | RGBA | 384x384 | 0 | 255 | 115704 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F06.png` | RGBA | 384x384 | 0 | 254 | 84949 | PASS |
| `CAST/001_m_official_knight_c_s_mon_official_knight_c_CAST_F07.png` | RGBA | 384x384 | 0 | 243 | 65260 | PASS |
| `ICON/001_m_official_knight_c_s_mon_official_knight_c_ICON.png` | RGBA | 256x256 | 0 | 255 | 37464 | PASS |

## Checks and notes

- actual alpha background: PASS
- frame count / numbering / canvas size: PASS
- empty required frame: PASS
- text contamination: PASS (manual visual check)
- cell fragment mixing: PASS (manual visual check)
- byte-preserving approved reuse: NOT_APPLICABLE
- runtime/import validation: NOT_CHECKED
- unmet items: none