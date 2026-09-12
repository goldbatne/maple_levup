# RESULT_INFO — 002 / 정식기사 D / 기사단의 바람 조준

- input_zip: `AREA_19_IMAGES_INPUT_V2_4(2).zip`
- basis_revision: `V2.4 current contract`
- monster_id: `m_official_knight_d` / monster_name: `정식기사 D`
- skill_id: `s_mon_official_knight_d` / skill_name: `기사단의 바람 조준` / skill_type: `패시브`
- production: `NEW_ART`
- user_art_approval: `PENDING`
- preview_file: `PREVIEW/labeled_preview.png`

## Output roles

| role | decision | runtime_use | files | frame_count | canvas | playback |
|---|---|---|---|---:|---|---|
| REFERENCE_VFX | NEW_ART | false | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F00.png | REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F01.png | REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F02.png | REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F03.png | REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F04.png | REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F05.png` | 6 | 256x256 RGBA | preview-only non-loop |
| ICON | NEW_ART | ui | `ICON/002_m_official_knight_d_s_mon_official_knight_d_ICON.png` | 1 | 256x256 RGBA | static |

## Source provenance

- source monster image: `monsters/002_m_official_knight_d/MONSTER_IMAGE.png`
- generated source sheet: `SOURCE_SHEETS/002_m_official_knight_d_s_mon_official_knight_d_SOURCE_SHEET.png`
- source of generated originals: image generation based on current INPUT V2.4 package and monster-specific GENERATION_SPEC

## Split coordinates from source sheet

| role | frame | cell_index | source_box(x0,y0,x1,y1) | output_path |
|---|---:|---:|---|---|
| REFERENCE_VFX | 0 | 0 | `(0, 0, 444, 444)` | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F00.png` |
| REFERENCE_VFX | 1 | 1 | `(444, 0, 887, 444)` | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F01.png` |
| REFERENCE_VFX | 2 | 2 | `(887, 0, 1330, 444)` | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F02.png` |
| REFERENCE_VFX | 3 | 3 | `(1330, 0, 1774, 444)` | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F03.png` |
| REFERENCE_VFX | 4 | 4 | `(0, 444, 444, 887)` | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F04.png` |
| REFERENCE_VFX | 5 | 5 | `(444, 444, 887, 887)` | `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F05.png` |
| ICON | 0 | 6 | `(887, 444, 1330, 887)` | `ICON/002_m_official_knight_d_s_mon_official_knight_d_ICON.png` |

## Validation

| file | mode | size | alpha_min | alpha_max | visible_pixels | status |
|---|---|---|---:|---:|---:|---|
| `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F00.png` | RGBA | 256x256 | 0 | 252 | 18092 | PASS |
| `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F01.png` | RGBA | 256x256 | 0 | 253 | 21202 | PASS |
| `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F02.png` | RGBA | 256x256 | 0 | 252 | 22054 | PASS |
| `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F03.png` | RGBA | 256x256 | 0 | 253 | 23947 | PASS |
| `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F04.png` | RGBA | 256x256 | 0 | 253 | 23840 | PASS |
| `REFERENCE/002_m_official_knight_d_s_mon_official_knight_d_REFERENCE_F05.png` | RGBA | 256x256 | 0 | 250 | 22316 | PASS |
| `ICON/002_m_official_knight_d_s_mon_official_knight_d_ICON.png` | RGBA | 256x256 | 0 | 253 | 22109 | PASS |

## Checks and notes

- actual alpha background: PASS
- frame count / numbering / canvas size: PASS
- empty required frame: PASS
- text contamination: PASS (manual visual check)
- cell fragment mixing: PASS (manual visual check)
- byte-preserving approved reuse: NOT_APPLICABLE
- runtime/import validation: NOT_CHECKED
- unmet items: none