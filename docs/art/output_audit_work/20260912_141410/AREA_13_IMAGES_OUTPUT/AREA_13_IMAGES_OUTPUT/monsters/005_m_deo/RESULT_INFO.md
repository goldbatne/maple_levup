# RESULT_INFO — 데우 / 잠든 선인장의 폭발

- input_zip: `AREA_13_IMAGES_INPUT_V2_4(1).zip`
- 기준 문서: `PACKAGE_REVISION_V2_4.md` / `FULL_ART_SCOPE.csv` / `OUTPUT_REQUIREMENTS.csv`
- area: `area_13` / 니할 사막
- monster: `m_deo` / 데우
- skill: `s_mon_deo` / 잠든 선인장의 폭발 / 액티브
- production_decision: `NEW_ART`
- runtime_roles delivered: `ICON` + `CAST_VFX`
- monster_image_source: `MONSTER_IMAGE.png` (input package reference only; preview에 그대로 합성)
- generated_art_source: `image_gen` 신규 제작
- source_sheet: `SOURCE_SHEETS/005_m_deo_s_mon_deo_CAST_SOURCE_SHEET.png`
- source_sheet_exact_size: `2048x1536 RGBA`
- split_coordinates: `[{"frame": "F00", "box": [0, 0, 512, 512]}, {"frame": "F01", "box": [512, 0, 1024, 512]}, {"frame": "F02", "box": [1024, 0, 1536, 512]}, {"frame": "F03", "box": [1536, 0, 2048, 512]}, {"frame": "F04", "box": [0, 512, 512, 1024]}, {"frame": "F05", "box": [512, 512, 1024, 1024]}, {"frame": "F06", "box": [1024, 512, 1536, 1024]}, {"frame": "F07", "box": [1536, 512, 2048, 1024]}, {"frame": "F08", "box": [0, 1024, 512, 1536]}, {"frame": "F09", "box": [512, 1024, 1024, 1536]}, {"frame": "F10", "box": [1024, 1024, 1536, 1536]}, {"frame": "F11", "box": [1536, 1024, 2048, 1536]}]`
- user_art_approval: `PENDING`

## Delivered files

- `ICON/005_m_deo_s_mon_deo_ICON.png` / 1 frame / 256x256 RGBA / static
- `CAST/005_m_deo_s_mon_deo_CAST_FF00....png` / 12 frames / 512x512 RGBA / 0.08s per frame / non-loop one-shot
- `PREVIEW/labeled_preview.png`

## Inspection

- ICON: mode=RGBA / size=256x256 / alpha=0~255 / visible=PASS / crop_edge_touch=PASS
- CAST_VFX: frames=12 / size=512x512 / alpha=0~255 observed / visible_frames=PASS / crop_edge_touch=WARN
- 텍스트/워터마크 혼입: PASS (수동 시각 검수)
- 승인 재사용 바이트 유지: 해당 없음 (전 항목 NEW_ART)
- USER_ART_APPROVAL: PENDING

## Notes

- runtime_use for `CAST_VFX`: `true`
- 핵심 소재 대응: 선인장 가시핵 + 모래 폭발
- 미충족 사항: 없음
- 정보 부족: 원본 다운로드 시각/초기 선택 프레임 메타데이터는 input provenance 기준 미보존.
