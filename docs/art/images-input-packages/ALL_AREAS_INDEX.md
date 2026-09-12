# All Areas ChatGPT Images Input Packages

- 기준 데이터: 현재 MonsterTable / SkillTable / AreaTable / RoomTable
- Area: 20개
- 생성 ZIP: 20개
- 고유 포획 가능 몬스터: 101종
- Area 배치 합계(중복 지역 배치 포함): 104건
- 스타일 라이브러리: 183개 고유 RUID
- RECENT_PRIMARY 0 / RECENT_SECONDARY 20 / LEGACY_REFERENCE 43 / UNKNOWN 120 / EXCLUDE_STYLE 0
- 미확보/경고 자료: 3건

| area_order | area_id | area_name | level_range | monster_count | zip_path | zip_bytes | missing_materials | area_ref_status | validation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | area_00 | 메이플 아일랜드·리스항구 | Lv1~11 | 5 | docs/art/images-input-packages/AREA_00_IMAGES_INPUT.zip | 3138133 | 0 | 확보 | PASS |
| 2 | area_01 | 헤네시스 근교 | Lv1~12 | 5 | docs/art/images-input-packages/AREA_01_IMAGES_INPUT.zip | 2952521 | 1 | 미확보 | PASS |
| 3 | area_03 | 엘리니아 | Lv11~20 | 5 | docs/art/images-input-packages/AREA_03_IMAGES_INPUT.zip | 2911218 | 1 | 미확보 | PASS |
| 4 | area_02 | 페리온 | Lv10~42 | 8 | docs/art/images-input-packages/AREA_02_IMAGES_INPUT.zip | 3217128 | 1 | 미확보 | PASS |
| 5 | area_04 | 커닝시티 | Lv31~40 | 5 | docs/art/images-input-packages/AREA_04_IMAGES_INPUT.zip | 2892438 | 0 | 확보 | PASS |
| 6 | area_05 | 노틸러스 | Lv41~60 | 5 | docs/art/images-input-packages/AREA_05_IMAGES_INPUT.zip | 2949532 | 0 | 확보 | PASS |
| 7 | area_07 | 슬리피우드 | Lv61~70 | 6 | docs/art/images-input-packages/AREA_07_IMAGES_INPUT.zip | 3074152 | 0 | 확보 | PASS |
| 8 | area_08 | 오르비스 | Lv71~80 | 5 | docs/art/images-input-packages/AREA_08_IMAGES_INPUT.zip | 2885947 | 0 | 확보 | PASS |
| 9 | area_09 | 엘나스 산맥 | Lv81~90 | 5 | docs/art/images-input-packages/AREA_09_IMAGES_INPUT.zip | 2843531 | 0 | 확보 | PASS |
| 10 | area_10 | 아쿠아로드 | Lv91~100 | 5 | docs/art/images-input-packages/AREA_10_IMAGES_INPUT.zip | 2891989 | 0 | 확보 | PASS |
| 11 | area_11 | 루더스 호수 | Lv101~110 | 5 | docs/art/images-input-packages/AREA_11_IMAGES_INPUT.zip | 2788460 | 0 | 확보 | PASS |
| 12 | area_12 | 루디브리엄 | Lv111~120 | 5 | docs/art/images-input-packages/AREA_12_IMAGES_INPUT.zip | 2859694 | 0 | 확보 | PASS |
| 13 | area_13 | 니할 사막 | Lv121~130 | 5 | docs/art/images-input-packages/AREA_13_IMAGES_INPUT.zip | 2799414 | 0 | 확보 | PASS |
| 14 | area_14 | 마가티아 | Lv131~140 | 5 | docs/art/images-input-packages/AREA_14_IMAGES_INPUT.zip | 2789776 | 0 | 확보 | PASS |
| 15 | area_15 | 무릉도원 | Lv141~150 | 5 | docs/art/images-input-packages/AREA_15_IMAGES_INPUT.zip | 2972875 | 0 | 확보 | PASS |
| 16 | area_16 | 미나르숲 | Lv151~160 | 5 | docs/art/images-input-packages/AREA_16_IMAGES_INPUT.zip | 2856869 | 0 | 확보 | PASS |
| 17 | area_17 | 시간의 신전 | Lv161~170 | 5 | docs/art/images-input-packages/AREA_17_IMAGES_INPUT.zip | 2802323 | 0 | 확보 | PASS |
| 18 | area_18 | 지구방위본부 | Lv171~180 | 5 | docs/art/images-input-packages/AREA_18_IMAGES_INPUT.zip | 2870109 | 0 | 확보 | PASS |
| 19 | area_19 | 미래의 문 | Lv181~190 | 5 | docs/art/images-input-packages/AREA_19_IMAGES_INPUT.zip | 2853479 | 0 | 확보 | PASS |
| 20 | area_20 | 황혼의 페리온 | Lv191~200 | 5 | docs/art/images-input-packages/AREA_20_IMAGES_INPUT.zip | 3053353 | 0 | 확보 | PASS |

## 패키지 보정 메모

- 기존 확정 데이터와 기본 폴더 구조를 유지한 채 스타일 우선순위, 프레임 분리형 납품 규칙, 몬스터별 시각 번역과 아이콘 지시를 보정했다.
- RECENT_PRIMARY가 비어 있으면 RECENT_SECONDARY가 사실상의 최신 우선 스타일 세트다. UNKNOWN/LEGACY_REFERENCE는 비교·보조용이다.
- VFX 주 납품물은 F00, F01, F02 ... 개별 RGBA PNG이며 contact sheet/sprite sheet는 선택적 검수 미리보기다.
- `area_06`은 현재 AreaTable에 존재하지 않는 예약/결번 ID다. 실제 Area 순서는 `sort_order` 1~20으로 연속이며 누락 패키지가 아니다.
