# RESULT_INFO — 003 / 상급기사 A / 그림자 기사의 민첩

- input_zip: `AREA_19_IMAGES_INPUT_V2_4(2).zip`
- basis_revision: `V2.4 current contract`
- monster_id: `m_advanced_knight_a` / monster_name: `상급기사 A`
- skill_id: `s_mon_advanced_knight_a` / skill_name: `그림자 기사의 민첩` / skill_type: `패시브`
- production: `NEW_ART`
- user_art_approval: `PENDING`
- preview_file: `PREVIEW/labeled_preview.png`

## Output roles

| role | decision | runtime_use | files | frame_count | canvas | playback |
|---|---|---|---|---:|---|---|
| REFERENCE_VFX | NEW_ART | false | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F00.png | REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F01.png | REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F02.png | REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F03.png | REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F04.png | REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F05.png` | 6 | 256x256 RGBA | preview-only non-loop |
| ICON | NEW_ART | ui | `ICON/003_m_advanced_knight_a_s_mon_advanced_knight_a_ICON.png` | 1 | 256x256 RGBA | static |

## Source provenance

- source monster image: `monsters/003_m_advanced_knight_a/MONSTER_IMAGE.png`
- generated source sheet: `SOURCE_SHEETS/003_m_advanced_knight_a_s_mon_advanced_knight_a_SOURCE_SHEET.png`
- source of generated originals: image generation based on current INPUT V2.4 package and monster-specific GENERATION_SPEC

## Split coordinates from source sheet

| role | frame | cell_index | source_box(x0,y0,x1,y1) | output_path |
|---|---:|---:|---|---|
| REFERENCE_VFX | 0 | 0 | `(0, 0, 444, 444)` | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F00.png` |
| REFERENCE_VFX | 1 | 1 | `(444, 0, 887, 444)` | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F01.png` |
| REFERENCE_VFX | 2 | 2 | `(887, 0, 1330, 444)` | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F02.png` |
| REFERENCE_VFX | 3 | 3 | `(1330, 0, 1774, 444)` | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F03.png` |
| REFERENCE_VFX | 4 | 4 | `(0, 444, 444, 887)` | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F04.png` |
| REFERENCE_VFX | 5 | 5 | `(444, 444, 887, 887)` | `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F05.png` |
| ICON | 0 | 6 | `(887, 444, 1330, 887)` | `ICON/003_m_advanced_knight_a_s_mon_advanced_knight_a_ICON.png` |

## Validation

| file | mode | size | alpha_min | alpha_max | visible_pixels | status |
|---|---|---|---:|---:|---:|---|
| `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F00.png` | RGBA | 256x256 | 0 | 255 | 9189 | PASS |
| `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F01.png` | RGBA | 256x256 | 0 | 255 | 15952 | PASS |
| `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F02.png` | RGBA | 256x256 | 0 | 255 | 22996 | PASS |
| `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F03.png` | RGBA | 256x256 | 0 | 255 | 27823 | PASS |
| `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F04.png` | RGBA | 256x256 | 0 | 255 | 17905 | PASS |
| `REFERENCE/003_m_advanced_knight_a_s_mon_advanced_knight_a_REFERENCE_F05.png` | RGBA | 256x256 | 0 | 223 | 15343 | PASS |
| `ICON/003_m_advanced_knight_a_s_mon_advanced_knight_a_ICON.png` | RGBA | 256x256 | 0 | 255 | 22002 | PASS |

## Checks and notes

- actual alpha background: PASS
- frame count / numbering / canvas size: PASS
- empty required frame: PASS
- text contamination: PASS (manual visual check)
- cell fragment mixing: PASS (manual visual check)
- byte-preserving approved reuse: NOT_APPLICABLE
- runtime/import validation: NOT_CHECKED
- unmet items: none