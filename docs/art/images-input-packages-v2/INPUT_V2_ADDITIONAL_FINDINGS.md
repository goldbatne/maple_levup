# INPUT V2 ADDITIONAL FINDINGS

| 구분 | 범위 | 발견·근거 | 영향/처리 |
|---|---|---|---|
| 확인된 INPUT 오류 | 공통 | OUTPUT_NAMING_SPEC의 루트가 AREA_XX_IMAGES_INPUT_IMAGES_OUTPUT로 잘못됨 | 전 Area에서 AREA_XX_IMAGES_OUTPUT로 수정 |
| 확인된 INPUT 오류 | 공통 | RECENT_PRIMARY가 비면 근거 없는 RECENT_SECONDARY를 최신으로 승격 | 자동 승격 제거, 시기 미확인 유지 |
| 확인된 INPUT 오류 | 공통 | 효과 위치/방향이 '시전자 또는 지정점', '방사 또는 수직' 템플릿으로 실제 코드와 불일치 | 시전자/도착점/엔진 이동/판정 시점별 명세로 교체 |
| 확인된 INPUT 오류 | 공통 | 패시브 VFX가 런타임 적용처럼 오인될 수 있음 | 기존 제작 범위는 보존하되 REFERENCE_VFX·자동 반입 금지로 명시 |
| 확인된 INPUT 오류 | 공통 | Style corpus의 몬스터·캐릭터 본체/장면 RUID가 효과 레퍼런스와 같은 우선순위 | MONSTER_CHARACTER 10개와 SCENE 5개를 EXCLUDE_STYLE로 분리 |
| 확인된 사실 | AREA 01~20 | 99개 MONSTER_IMAGE를 4장 contact sheet로 독립 시각 대조 | 잘못된 개체·스타일 이미지 혼입 0건; 원본 교체 0건, audit-previews/monsters에 근거 보존 |
| 기존 감사 판단 정정 | area_01/area_03 | 방 배치의 히어로·보우마스터가 INPUT 누락처럼 보일 수 있음 | drop_skill_id가 없는 히든 직업 보스라 포획 스킬 아트 INPUT 대상 아님 |
| 게임 데이터 또는 기획 판단 필요 | 공통 | 작업 트리에서 SkillTable.csv/.userdataset 삭제 | 복구·수정하지 않고 HEAD 및 AREA00 승인 런타임 증거로 교차검증; 관련 불확실성 기록 |
| 근거 부족 | 공통 | 기존 raw 다운로드/cache/selected frame 기록 부재 | RUID·모델 경로·현재 PNG SHA/캔버스/alpha는 기록, 선택 frame index는 미확인 |
| 근거 부족 | 공통 | 요청에 명시된 감사 3개 파일을 프로젝트/첨부 저장소에서 찾지 못함 | 감사 주장을 적용하지 않고 현재 파일·코드로 독립 감사 |

## Area별 상태

| Area | 수정 | 추가 발견 | 원본 교체 | 기획 변경 | 미확인·충돌 | 상태 | ZIP |
|---|---|---|---:|---|---|---|---|
| area_01 | AREA 00 승인 재사용 자산 2종 포함; 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 방 배치에는 있으나 포획 대상이 아닌 히든 직업 보스 제외: m_adv_hero | 0 | 없음 | s_mon_snail_dew_trail: 작업 트리 SkillTable 삭제로 행 직접 재조회 불가; AREA 00 승인 런타임/manifest와 일치하여 승인 재사용만 허용 | READY | `docs/art/images-input-packages-v2/AREA_01_IMAGES_INPUT_V2.zip` |
| area_02 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_stumpy: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_02_IMAGES_INPUT_V2.zip` |
| area_03 | AREA 00 승인 재사용 자산 1종 포함; 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 방 배치에는 있으나 포획 대상이 아닌 히든 직업 보스 제외: m_adv_bowmaster; m_faust: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_03_IMAGES_INPUT_V2.zip` |
| area_04 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_04_IMAGES_INPUT_V2.zip` |
| area_05 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_05_IMAGES_INPUT_V2.zip` |
| area_07 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_07_IMAGES_INPUT_V2.zip` |
| area_08 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_star_pixie: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존; m_lunar_pixie: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_08_IMAGES_INPUT_V2.zip` |
| area_09 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_09_IMAGES_INPUT_V2.zip` |
| area_10 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_shark: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_10_IMAGES_INPUT_V2.zip` |
| area_11 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_king_bloctopus: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_11_IMAGES_INPUT_V2.zip` |
| area_12 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_12_IMAGES_INPUT_V2.zip` |
| area_13 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_13_IMAGES_INPUT_V2.zip` |
| area_14 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_roid: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존; m_chimera: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_14_IMAGES_INPUT_V2.zip` |
| area_15 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_peach_monkey: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존; m_tae_roon: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_15_IMAGES_INPUT_V2.zip` |
| area_16 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_16_IMAGES_INPUT_V2.zip` |
| area_17 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_dodo: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_17_IMAGES_INPUT_V2.zip` |
| area_18 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | m_mateon: 엔진 이동 projectile_ruid는 실제 사용처를 명시하고 기존 제작 범위대로 보존 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_18_IMAGES_INPUT_V2.zip` |
| area_19 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_19_IMAGES_INPUT_V2.zip` |
| area_20 | 공통 스타일 시기/역할 규칙 보정; 실제 런타임 역할·엔진 이동·판정 시점 명시; OUTPUT 루트/manifest/alpha 검증 규칙 통일; 몬스터 원본 출처·SHA-256 기록 | 없음 | 0 | 없음 | 없음 | READY | `docs/art/images-input-packages-v2/AREA_20_IMAGES_INPUT_V2.zip` |
