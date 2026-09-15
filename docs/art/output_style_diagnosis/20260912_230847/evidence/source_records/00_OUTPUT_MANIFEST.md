# AREA_00_IMAGES_OUTPUT Manifest

## Area Identification

- 입력 ZIP 파일명: `AREA_00_IMAGES_INPUT(2).zip`
- 입력 ZIP 루트 폴더명: `AREA_00_IMAGES_INPUT/`
- 식별한 Area ID: `area_00`
- 출력 폴더명: `AREA_00_IMAGES_OUTPUT/`
- Area 이름: 메이플 아일랜드·리스항구
- 레벨 범위: Lv1~11
- 처리 대상 몬스터 수: 5종
- 참조 자료 사용: AREA_MANIFEST, monsters/*/MONSTER_IMAGE, GENERATION_SPEC, MONSTER_INFO, global_skill_style_library/STYLE_INDEX 및 skills/*/preview, OUTPUT_NAMING_SPEC, OUTPUT_FORMAT_SPEC, CHATGPT_IMAGES_MASTER_PROMPT
- 비고: 패키지 내 `STYLE_ATLAS` 파일은 확인되지 않아, `STYLE_INDEX`와 개별 `skills/*/preview`를 기준으로 스타일 문법을 판단했습니다.

## 결과 요약

- 001. 달팽이 (`m_snail`) / 이슬 미끄럼길 (`s_mon_snail_dew_trail`) / 액티브 / VFX 8프레임 / ICON 1장
- 002. 파란 달팽이 (`m_blue_snail`) / 푸른 껍질 (`s_mon_blue_snail`) / 버프 / VFX 8프레임 / ICON 1장
- 003. 빨간 달팽이 (`m_red_snail`) / 붉은 껍질 돌진 (`s_mon_red_snail`) / 액티브 / VFX 8프레임 / ICON 1장
- 004. 마노 (`m_mano`) / 마노의 무지개 파동 (`s_mon_mano`) / 액티브 / VFX 12프레임 / ICON 1장
- 005. 슬라임 (`m_slime`) / 끈적한 몸통 (`s_mon_slime`) / 액티브 / VFX 8프레임 / ICON 1장

## 파일 구조

```text
AREA_00_IMAGES_OUTPUT/
├─ OUTPUT_MANIFEST.md
├─ OUTPUT_MANIFEST.csv
└─ monsters/
   ├─ 001_m_snail_달팽이/
   │  ├─ VFX/
   │  │  ├─ 001_m_snail_s_mon_snail_dew_trail_F00.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 001_m_snail_s_mon_snail_dew_trail_ICON.png
   │  ├─ PREVIEW/
   │  │  ├─ labeled_preview.png
   │  │  └─ ...
   │  └─ RESULT_INFO.md
   ├─ 002_m_blue_snail_파란_달팽이/
   │  ├─ VFX/
   │  │  ├─ 002_m_blue_snail_s_mon_blue_snail_F00.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 002_m_blue_snail_s_mon_blue_snail_ICON.png
   │  ├─ PREVIEW/
   │  │  ├─ labeled_preview.png
   │  │  └─ ...
   │  └─ RESULT_INFO.md
   ├─ 003_m_red_snail_빨간_달팽이/
   │  ├─ VFX/
   │  │  ├─ 003_m_red_snail_s_mon_red_snail_F00.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 003_m_red_snail_s_mon_red_snail_ICON.png
   │  ├─ PREVIEW/
   │  │  ├─ labeled_preview.png
   │  │  └─ ...
   │  └─ RESULT_INFO.md
   ├─ 004_m_mano_마노/
   │  ├─ VFX/
   │  │  ├─ 004_m_mano_s_mon_mano_F00.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 004_m_mano_s_mon_mano_ICON.png
   │  ├─ PREVIEW/
   │  │  ├─ labeled_preview.png
   │  │  └─ ...
   │  └─ RESULT_INFO.md
   ├─ 005_m_slime_슬라임/
   │  ├─ VFX/
   │  │  ├─ 005_m_slime_s_mon_slime_F00.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 005_m_slime_s_mon_slime_ICON.png
   │  ├─ PREVIEW/
   │  │  ├─ labeled_preview.png
   │  │  └─ ...
   │  └─ RESULT_INFO.md
```

## 생성 소스

- VFX 원본 생성물: image_gen으로 생성한 contact/sprite preview 이미지를 균등 분할 후 OUTPUT_FORMAT_SPEC에 맞춰 각 프레임 PNG로 저장
- ICON 원본 생성물: image_gen으로 생성한 투명 아이콘을 256×256 RGBA로 정리
- 검수용 표시 자료: Python으로 labeled preview 이미지를 구성
