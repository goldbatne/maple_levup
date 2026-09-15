# RESULT_INFO — 목도리 프릴드 / 목도리의 사막감각

- input_zip: `AREA_13_IMAGES_INPUT_V2_4(1).zip`
- 기준 문서: `PACKAGE_REVISION_V2_4.md` / `FULL_ART_SCOPE.csv` / `OUTPUT_REQUIREMENTS.csv`
- area: `area_13` / 니할 사막
- monster: `m_scarf_plead` / 목도리 프릴드
- skill: `s_mon_scarf_plead` / 목도리의 사막감각 / 패시브
- production_decision: `NEW_ART`
- runtime_roles delivered: `ICON` + `REFERENCE_VFX`
- monster_image_source: `MONSTER_IMAGE.png` (input package reference only; preview에 그대로 합성)
- generated_art_source: `image_gen` 신규 제작
- source_sheet: `SOURCE_SHEETS/002_m_scarf_plead_s_mon_scarf_plead_REFERENCE_SOURCE_SHEET.png`
- source_sheet_exact_size: `768x512 RGBA`
- split_coordinates: `[{"frame": "F00", "box": [0, 0, 256, 256]}, {"frame": "F01", "box": [256, 0, 512, 256]}, {"frame": "F02", "box": [512, 0, 768, 256]}, {"frame": "F03", "box": [0, 256, 256, 512]}, {"frame": "F04", "box": [256, 256, 512, 512]}, {"frame": "F05", "box": [512, 256, 768, 512]}]`
- user_art_approval: `PENDING`

## Delivered files

- `ICON/002_m_scarf_plead_s_mon_scarf_plead_ICON.png` / 1 frame / 256x256 RGBA / static
- `REFERENCE/002_m_scarf_plead_s_mon_scarf_plead_REFERENCE_FF00....png` / 6 frames / 256x256 RGBA / 0.10s per frame / preview-only non-loop
- `PREVIEW/labeled_preview.png`

## Inspection

- ICON: mode=RGBA / size=256x256 / alpha=0~255 / visible=PASS / crop_edge_touch=PASS
- REFERENCE_VFX: frames=6 / size=256x256 / alpha=0~255 observed / visible_frames=PASS / crop_edge_touch=WARN
- 텍스트/워터마크 혼입: PASS (수동 시각 검수)
- 승인 재사용 바이트 유지: 해당 없음 (전 항목 NEW_ART)
- USER_ART_APPROVAL: PENDING

## Notes

- runtime_use for `REFERENCE_VFX`: `false`
- 핵심 소재 대응: 휘날린 목도리 + 바람 감지선
- 미충족 사항: 없음
- 정보 부족: 원본 다운로드 시각/초기 선택 프레임 메타데이터는 input provenance 기준 미보존.
