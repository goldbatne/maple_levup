# REPACK 기준 OUTPUT — 스토리·스킬명 보완 검수

- 실행: `20260912_160012_story_skill_coherence_r5`
- 고정 OUTPUT: `D:\maplestory_levup\docs\art\output_repacked\20260912_153221_v24_repack`
- 고정 조건: 17 ZIP SHA-256 일치, 역할 PNG 839개 바이트 변경 0건인 REPACK 결과만 기존 구조·규격·스타일 검사를 재사용
- 이번 검사: 17 Area / 89 몬스터·스킬의 원작·지역 설정 ↔ 확정 스킬명·효과 ↔ 실제 VFX·ICON 연결
- 재실행하지 않은 검사: 동일 INPUT V2.4와 동일 PNG 해시에 대한 구조·PNG 규격·스타일 전수 검사
- 변경: 원화·ZIP·INPUT·게임 파일 없음

## 결과

- 명백한 추가 불일치: 3건 (스톤골렘 지역, 버블링 지역, ‘발굴지의 석면’ 명칭)
- 사용자 판단: 1건 (킹크랑을 노틸러스 권역에 포함할지)
- 위 4건을 제외한 명백한 문제 없음: 85건
- 완료 17 Area에서 스토리·명칭 때문에 원화 재생성이 필요한 항목: 0건
- 이전 ‘검토 필요’ 정정: 도도의 ‘기억 포식’은 실제 설정과 일치; ‘검은 뿌리의 묘지’는 공식 황혼의 페리온 맵명 ‘칼바람의 묘지’와 충돌하지 않음

## 새로 확인된 불일치·판단 항목

### area_02 / m_stone_golem — 스톤골렘 — 페리온 배치 (`REGION_MISMATCH`)

- [프로젝트 자료] 프로젝트: area_02 페리온, 스킬 ‘암석 피부’. VFX는 암석판 방패와 금빛 균열광.
- [외부 확인 사실] 외부 확인: 스톤골렘은 헤네시스 골렘의 사원 몬스터로 기록됨.
- [출처·시점] https://maplestorywiki.net/w/Golem%27s_Temple_Entrance (편집 시점 불명, 검색 확인 2026-09-12); 넥슨 2011 지역 개편 아카이브(시점 2011-07-07)도 헤네시스 몬스터로 기재.
- [추정·판단] 스킬명·효과·아트는 몬스터와 맞지만 Area 귀속만 원작과 다르다. 원화 재생성 사유는 아니다.
- [미확인] 프로젝트가 페리온의 암석 테마를 우선한 의도적 재배치인지 확정 기록 없음.
- 근거 이미지: `D:\maplestory_levup\docs\art\output_audit\runs\20260912_160012_story_skill_coherence_r5\evidence\AREA_02_m_stone_golem_STORY_SKILL.png`

### area_03 / m_bubbling — 버블링 — 엘리니아 배치 (`REGION_MISMATCH`)

- [프로젝트 자료] 프로젝트: area_03 엘리니아, 패시브 ‘물방울 마력’. 아트는 기포·거품 고리.
- [외부 확인 사실] 외부 확인: 버블링은 커닝시티 지하철 계열 몬스터로 기록됨.
- [출처·시점] https://maplestorywiki.net/w/Kerning_City (편집 시점 불명, 검색 확인 2026-09-12); 넥슨 아카이브 이용자 기록(2008~2010년대)도 지하철 1호선 배치를 반복 기재.
- [추정·판단] 스킬명·효과·아트는 버블링과 자연스럽지만 엘리니아 서사 연결은 약하다. 원화 재생성 사유는 아니다.
- [미확인] 엘리니아로 옮긴 별도 프로젝트 서사는 확인되지 않음.
- 근거 이미지: `D:\maplestory_levup\docs\art\output_audit\runs\20260912_160012_story_skill_coherence_r5\evidence\AREA_03_m_bubbling_STORY_SKILL.png`

### area_05 / m_king_clang — 킹크랑 — 노틸러스/플로리나 경계 (`NEEDS_USER_REVIEW`)

- [프로젝트 자료] 프로젝트: area_05 노틸러스 보스, 스킬 ‘왕게의 집게 파도’. 아트는 붉은 집게와 파도 충격.
- [외부 확인 사실] 외부 확인: 넥슨 2007 업데이트는 킹크랑을 플로리나 비치 마스터 몬스터로 명시.
- [출처·시점] https://archive.maplestory.nexon.com/News/Update/51 (게시 2007-08-16, 검색 확인 2026-09-12); 플로리나 비치는 이후 노틸러스 해변에서 연결된 시기도 있음(시점 자료 혼재).
- [추정·판단] 엄밀한 원작 Area 명칭은 다르지만, 인접 해안·과거 연결 동선과 해양 테마는 자연스럽다. 유지 여부는 지역 단위의 엄밀성 기준에 달림.
- [미확인] 프로젝트가 노틸러스 권역에 플로리나 비치를 포함한다고 정의했는지 명시 문서 미확인.
- 근거 이미지: `D:\maplestory_levup\docs\art\output_audit\runs\20260912_160012_story_skill_coherence_r5\evidence\AREA_05_m_king_clang_STORY_SKILL.png`

### area_20 / m_mutant_stone_mask — 변형된 스톤마스크 — ‘발굴지의 석면’ (`SKILL_NAME_MISMATCH`)

- [프로젝트 자료] 프로젝트: 패시브 ‘발굴지의 석면’. VFX·ICON은 갈색 암석판/가면판이 맞물리는 방호 표현.
- [외부 확인 사실] 외부 확인: ‘석면(石綿)’은 asbestos, 즉 섬유상 규산염 광물류를 뜻한다.
- [출처·시점] https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000472561 (석면안전관리법 시행 2025-10-01); 넥슨 황혼의 페리온 업데이트 2013-02-21은 변형된 스톤마스크와 발굴지역을 확인.
- [추정·판단] 현재 그림은 섬유상 석면이 아니라 돌판/가면 표면을 표현하므로, 이름의 일반적 의미가 시각과 충돌한다. 아트보다 스킬명 검토 대상.
- [미확인] ‘석면’을 ‘돌의 면(面)’이라는 창작 합성어로 의도했는지 기록 없음.
- 근거 이미지: `D:\maplestory_levup\docs\art\output_audit\runs\20260912_160012_story_skill_coherence_r5\evidence\AREA_20_m_mutant_stone_mask_STORY_SKILL.png`

## AREA 11·12 보류

### AREA 11

- 킹 블록퍼스의 ICON과 다른 정상 에셋은 유지한다.
- CAST·PROJECTILE만 위 수정 계약으로 원화 수정 후보를 유지한다.
- 근거/수정 방향: `D:\maplestory_levup\docs\art\output_audit\runs\20260912_160012_story_skill_coherence_r5\evidence\AREA_11_KING_BLOCTOPUS_CORRECTION_DIRECTION.png`

### AREA 12

- 현행 문구만 적용하면 실제 CAST는 명시적 금지 위반이다. 목마 머리 허용은 ICON 항목에만 있다.
- 사용자 판단은 ‘눈 달린 머리/상체를 장난감 부품 예외로 허용하도록 명세를 바꿀 것인가’에만 남는다. 현행 명세를 유지하면 CAST 원화 수정 후보이다.
- 나란히 비교: `D:\maplestory_levup\docs\art\output_audit\runs\20260912_160012_story_skill_coherence_r5\evidence\AREA_12_TOY_TROJAN_SPEC_VS_CAST.png`

## 출처 신뢰도와 시점

- 우선: 넥슨 공식 업데이트/아카이브(게시일 기록).
- 보조: MapleStory Wiki/StrategyWiki(편집 시점이 표시되거나 시점 불명인 경우 그대로 기록).
- 프로젝트 창작 스킬은 동일한 공식 스킬명의 존재를 요구하지 않았다.
- 외부 근거가 없는 능력 서사는 ‘창작’으로만 분류했으며, 몬스터·지역·실제 아트와 충돌하지 않으면 오류로 올리지 않았다.

## 상태 경계

이 검수는 재생성 결정을 위한 자료다. USER_APPROVED, 런타임 PASS, 게임 반입 완료를 의미하지 않는다.
