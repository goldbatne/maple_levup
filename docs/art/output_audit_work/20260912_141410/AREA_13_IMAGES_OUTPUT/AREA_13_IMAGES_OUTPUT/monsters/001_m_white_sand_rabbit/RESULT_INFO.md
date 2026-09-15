# RESULT_INFO — 흰 모래토끼 / 사막 굴착탄

- input_zip: `AREA_13_IMAGES_INPUT_V2_4(1).zip`
- 기준 문서: `PACKAGE_REVISION_V2_4.md` / `FULL_ART_SCOPE.csv` / `OUTPUT_REQUIREMENTS.csv`
- area: `area_13` / 니할 사막
- monster: `m_white_sand_rabbit` / 흰 모래토끼
- skill: `s_mon_white_sand_rabbit` / 사막 굴착탄 / 액티브
- production_decision: `NEW_ART`
- runtime_roles delivered: `ICON` + `CAST_VFX`
- monster_image_source: `MONSTER_IMAGE.png` (input package reference only; preview에 그대로 합성)
- generated_art_source: `image_gen` 신규 제작
- source_sheet: `SOURCE_SHEETS/001_m_white_sand_rabbit_s_mon_white_sand_rabbit_CAST_SOURCE_SHEET.png`
- source_sheet_exact_size: `1536x768 RGBA`
- split_coordinates: `[{"frame": "F00", "box": [0, 0, 384, 384]}, {"frame": "F01", "box": [384, 0, 768, 384]}, {"frame": "F02", "box": [768, 0, 1152, 384]}, {"frame": "F03", "box": [1152, 0, 1536, 384]}, {"frame": "F04", "box": [0, 384, 384, 768]}, {"frame": "F05", "box": [384, 384, 768, 768]}, {"frame": "F06", "box": [768, 384, 1152, 768]}, {"frame": "F07", "box": [1152, 384, 1536, 768]}]`
- user_art_approval: `PENDING`

## Delivered files

- `ICON/001_m_white_sand_rabbit_s_mon_white_sand_rabbit_ICON.png` / 1 frame / 256x256 RGBA / static
- `CAST/001_m_white_sand_rabbit_s_mon_white_sand_rabbit_CAST_FF00....png` / 8 frames / 384x384 RGBA / 0.10s per frame / non-loop one-shot
- `PREVIEW/labeled_preview.png`

## Inspection

- ICON: mode=RGBA / size=256x256 / alpha=0~255 / visible=PASS / crop_edge_touch=PASS
- CAST_VFX: frames=8 / size=384x384 / alpha=0~255 observed / visible_frames=PASS / crop_edge_touch=WARN
- 텍스트/워터마크 혼입: PASS (수동 시각 검수)
- 승인 재사용 바이트 유지: 해당 없음 (전 항목 NEW_ART)
- USER_ART_APPROVAL: PENDING

## Notes

- runtime_use for `CAST_VFX`: `true`
- 핵심 소재 대응: 모래 원뿔탄 + 굴착 궤적
- 미충족 사항: 없음
- 정보 부족: 원본 다운로드 시각/초기 선택 프레임 메타데이터는 input provenance 기준 미보존.
