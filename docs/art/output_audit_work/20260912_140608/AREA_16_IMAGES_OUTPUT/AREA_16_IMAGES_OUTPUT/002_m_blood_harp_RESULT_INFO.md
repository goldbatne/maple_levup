# RESULT INFO — 블러드 하프 (m_blood_harp)

- Input ZIP: `AREA_16_IMAGES_INPUT_V2_4(1).zip`
- 기준: V2.4 현행 명세
- Area: `area_16` / 미나르숲
- Skill: `s_mon_blood_harp` / 핏빛 깃울림 / 액티브
- Production: NEW_ART
- USER_ART_APPROVAL: PENDING
- Source monster image: `monsters/002_m_blood_harp_블러드_하프/MONSTER_IMAGE.png`

## Output files

### ICON
- frame_count: 1
- canvas: 256x256 RGBA
- playback: static
- frame_seconds: static
  - `ICON/002_m_blood_harp_s_mon_blood_harp_ICON.png`
- source_sheet: `SOURCE_SHEETS/a_clean_transparent_background_game_icon_sprite_sh_1.png` / sheet_size=1536x1024 / grid=3x2
  - split cell: box (512, 0, 1024, 512)

### CAST
- frame_count: 8
- canvas: 384x384 RGBA
- playback: non-loop one-shot
- frame_seconds: 0.10
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F00.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F01.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F02.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F03.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F04.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F05.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F06.png`
  - `CAST/002_m_blood_harp_s_mon_blood_harp_CAST_F07.png`
- source_sheet: `SOURCE_SHEETS/a_clean_transparent_background_no_text_no_border_4_batch_1.png` / sheet_size=1774x887 / grid=4x2
  - split F00: box (0, 0, 444, 444)
  - split F01: box (444, 0, 887, 444)
  - split F02: box (887, 0, 1330, 444)
  - split F03: box (1330, 0, 1774, 444)
  - split F04: box (0, 444, 444, 887)
  - split F05: box (444, 444, 887, 887)
  - split F06: box (887, 444, 1330, 887)
  - split F07: box (1330, 444, 1774, 887)

## Inspection

- ICON: PASS — All files RGBA, exact size, alpha present, non-empty
- CAST: PASS — All files RGBA, exact size, alpha present, non-empty

## Preview

- `PREVIEW/002_m_blood_harp/labeled_preview.png`
