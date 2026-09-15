# RESULT INFO — 블록퍼스 / 블록 위장

- input_zip: `AREA_11_IMAGES_INPUT_V2_4(1).zip`
- 기준: `V2.4`
- area: `area_11` / 루더스 호수
- monster_id: `m_bloctopus`
- skill_id: `s_mon_bloctopus`
- production: `NEW_ART`
- user_art_approval: `PENDING`

## Output assets

### ICON
- decision: `NEW_ART`
- runtime_use: `ui`
- frame_count: `1`
- canvas: `256x256 RGBA`
- playback: `static` / frame_seconds `static` / total `static`
- source_monster_image: `bloctopus_MONSTER_IMAGE.png`
- source_sheet: `SOURCE_SHEETS/ICON_master_sheet.png`
- output_files:
  - `ICON/003_m_bloctopus_s_mon_bloctopus_ICON.png`
- split_coordinates:
  - `ICON/003_m_bloctopus_s_mon_bloctopus_ICON.png` <= cell (2, 0) / box (1024, 0, 1536, 512)
- inspection:
  - `ICON/003_m_bloctopus_s_mon_bloctopus_ICON.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN

### REFERENCE_VFX
- decision: `NEW_ART`
- runtime_use: `false`
- frame_count: `6`
- canvas: `256x256 RGBA`
- playback: `preview-only non-loop` / frame_seconds `0.10` / total `0.60`
- source_monster_image: `bloctopus_MONSTER_IMAGE.png`
- source_sheet: `SOURCE_SHEETS/003_m_bloctopus_s_mon_bloctopus_REFERENCE_sheet.png`
- output_files:
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F00.png`
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F01.png`
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F02.png`
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F03.png`
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F04.png`
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F05.png`
- split_coordinates:
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F00.png` <= cell (0, 0) / box (0, 0, 512, 512)
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F01.png` <= cell (1, 0) / box (512, 0, 1024, 512)
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F02.png` <= cell (2, 0) / box (1024, 0, 1536, 512)
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F03.png` <= cell (0, 1) / box (0, 512, 512, 1024)
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F04.png` <= cell (1, 1) / box (512, 512, 1024, 1024)
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F05.png` <= cell (2, 1) / box (1024, 512, 1536, 1024)
- inspection:
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F00.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F01.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F02.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F03.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F04.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN
  - `REFERENCE/003_m_bloctopus_s_mon_bloctopus_REFERENCE_F05.png`: mode=PASS, size=PASS, alpha=PASS, nonempty=PASS, clipping_suspect=WARN

## Review files

- `PREVIEW/labeled_preview.png`

## Notes

- AUTO_VALIDATION covers file presence, RGBA, size, alpha, and empty-frame heuristics only.
- Semantic art quality/fidelity is `NOT_CHECKED` and awaits user review.
- No approved-reuse asset applied for this Area.