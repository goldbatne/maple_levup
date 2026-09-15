# OUTPUT_MANIFEST

- input_zip: `AREA_13_IMAGES_INPUT_V2_4(1).zip`
- 기준: V2.4 (`PACKAGE_REVISION_V2_4.md`, `FULL_ART_SCOPE.csv`, `OUTPUT_REQUIREMENTS.csv`)
- area: `area_13` / 니할 사막
- 몬스터 수: 5
- NEW_ART: 10 role outputs (ICON 5 + CAST 3 + REFERENCE_VFX 2)
- AREA00_APPROVED_REUSE: 0
- USER_ART_APPROVAL: 전체 `PENDING`

## Deliverables summary

| work_order | monster | skill | role | production | files | size / timing |
|---|---|---|---|---|---|---|
| 001 | 흰 모래토끼 (`m_white_sand_rabbit`) | 사막 굴착탄 (`s_mon_white_sand_rabbit`) | ICON | NEW_ART | `ICON/001_m_white_sand_rabbit_s_mon_white_sand_rabbit_ICON.png` | 256x256 static |
| 001 | 흰 모래토끼 (`m_white_sand_rabbit`) | 사막 굴착탄 (`s_mon_white_sand_rabbit`) | CAST_VFX | NEW_ART | `CAST/001_m_white_sand_rabbit_s_mon_white_sand_rabbit_CAST_FF00....png` | 8f / 384x384 / 0.10s / non-loop one-shot |
| 002 | 목도리 프릴드 (`m_scarf_plead`) | 목도리의 사막감각 (`s_mon_scarf_plead`) | ICON | NEW_ART | `ICON/002_m_scarf_plead_s_mon_scarf_plead_ICON.png` | 256x256 static |
| 002 | 목도리 프릴드 (`m_scarf_plead`) | 목도리의 사막감각 (`s_mon_scarf_plead`) | REFERENCE_VFX | NEW_ART | `REFERENCE/002_m_scarf_plead_s_mon_scarf_plead_REFERENCE_FF00....png` | 6f / 256x256 / 0.10s / preview-only non-loop |
| 003 | 미요캐츠 (`m_meercat`) | 미요캐츠의 모래매복 (`s_mon_meercat`) | ICON | NEW_ART | `ICON/003_m_meercat_s_mon_meercat_ICON.png` | 256x256 static |
| 003 | 미요캐츠 (`m_meercat`) | 미요캐츠의 모래매복 (`s_mon_meercat`) | CAST_VFX | NEW_ART | `CAST/003_m_meercat_s_mon_meercat_CAST_FF00....png` | 8f / 384x384 / 0.10s / non-loop one-shot |
| 004 | 모래난쟁이 (`m_sand_dwarf`) | 사막 대장장이의 체력 (`s_mon_sand_dwarf`) | ICON | NEW_ART | `ICON/004_m_sand_dwarf_s_mon_sand_dwarf_ICON.png` | 256x256 static |
| 004 | 모래난쟁이 (`m_sand_dwarf`) | 사막 대장장이의 체력 (`s_mon_sand_dwarf`) | REFERENCE_VFX | NEW_ART | `REFERENCE/004_m_sand_dwarf_s_mon_sand_dwarf_REFERENCE_FF00....png` | 6f / 256x256 / 0.10s / preview-only non-loop |
| 005 | 데우 (`m_deo`) | 잠든 선인장의 폭발 (`s_mon_deo`) | ICON | NEW_ART | `ICON/005_m_deo_s_mon_deo_ICON.png` | 256x256 static |
| 005 | 데우 (`m_deo`) | 잠든 선인장의 폭발 (`s_mon_deo`) | CAST_VFX | NEW_ART | `CAST/005_m_deo_s_mon_deo_CAST_FF00....png` | 12f / 512x512 / 0.08s / non-loop one-shot |

## Included review files

- `AREA_OVERVIEW_PREVIEW.png`
- `monsters/*/PREVIEW/labeled_preview.png`
- `monsters/*/RESULT_INFO.md`
- `SOURCE_SHEETS/*.png`

## Validation summary

- RGBA 모드: PASS
- 실제 alpha 존재: PASS
- 빈 프레임: PASS
- 텍스트/워터마크 혼입: PASS (수동 시각 검수)
- 승인 재사용 바이트 유지: 해당 없음
- 잘림 의심(edge touch): 일부 프레임/아이콘은 안전영역 근접 가능성으로 RESULT_INFO에 `crop_edge_touch` 기록. 자동 FAIL 아님.
- 사용자 아트 승인: 전 항목 `PENDING`

## Warnings / information gaps

- 원본 몬스터 리소스의 다운로드 시각 및 선택 프레임 index는 INPUT provenance 상 미보존.
- 신규 아트는 생성형 출력 후 규격 시트로 정규화(resize)하여 분할했다; 분할용 source sheet는 출력물에 포함.