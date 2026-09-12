# V2.3 검수 원문 근거

## S1. 전면 신규 제작 원칙

입력: `AREA_03_IMAGES_INPUT_V2_3.zip`
내부 경로: `README_START_HERE.md`

```text
L23: 
L24: ## V2.3 authoritative production scope
L25: 
L26: 1. Read AREA_MANIFEST, FULL_ART_SCOPE, every GENERATION_SPEC/RUNTIME_ROLE_MAP, then OUTPUT_REQUIREMENTS.
L27: 2. Produce every `NEW_ART` role and copy every `AREA00_APPROVED_REUSE` role. Do not create `NO_RUNTIME_ROLE` files.
L28: 3. CAST and PROJECTILE are separate deliverables. The 11 formerly retained projectile artworks are now NEW_ART.
L29: 4. Existing RUIDs are evidence/current bindings, not permission to retain old art. Only the three exact Area 00 approved pairs are reuse exceptions.
L30: 5. Keep gameplay values and motion unchanged. Engine movement and art-local animation are separate.
```

## S2. 현행 파일에 남은 정반대 KEEP 지시

입력: `AREA_03_IMAGES_INPUT_V2_3.zip`
내부 경로: `RUNTIME_CONFLICTS_V2_3.md`

```text
L1: # Runtime and design conflicts — V2.3
L2: 
L3: ## AREA 20 / s_mon_mutant_stone_mask
L4: 
L5: - 확정 데이터: passive_stat=DEF (변경하지 않음).
L6: - GameDataVerify는 STR/DEX/INT/LUK만 허용해 DEF를 오류로 기록한다 (`GameDataVerify.mlua:188-200`).
L7: - PlayerStats.GetCollectionPoints는 전달받은 이름과 passive_stat이 같은 항목을 합산하지만, GetCollectionBonus("DEF")는 DEX 포인트만 사용한다 (`PlayerStats.mlua:527-576`). DEF collection point를 파생 방어력에 더하는 호출은 확인되지 않았다.
L8: - 결론: 현행 계산에서 스킬 passive_stat=DEF는 방어력 보너스로 소비되지 않는 기획/실행 충돌이다. 게임 데이터·검증·계산 코드는 V2.3에서 변경하지 않았다.
L9: - GENERATION_READY는 아트 입력 기준 READY, RUNTIME_VALIDATION은 UNRESOLVED다.
L10: 
L11: ## Current Maker SkillTable
L12: 
L13: - 정상 경로 SkillTable 파일은 삭제 상태이며 Mislocated 후보가 있다. `_DataService:GetTable("SkillTable")` 이름 조회만으로 현재 Maker 등록 EntryKey를 식별할 수 없다.
L14: - V2.3는 기준 커밋 데이터와 V2.1 확정 패키지를 사용하지만 현재 Maker 등록 테이블과 같다고 단정하지 않는다. RUNTIME_VALIDATION=NOT_RUN.
L15: 
L16: ## Six dash skills
L17: 
L18: - 플레이어 피해점은 계산 도착점, PlayCast는 호출 뒤 서버가 보는 caster 위치를 사용하므로 일치가 보장되지 않는다.
L19: - 지연 CAST는 Timer 후 SpawnLayer 실행 시점의 caster 좌표를 읽고, 스폰 뒤 맵 엔티티에 drift가 적용된다.
L20: - 몬스터 공통 CastSkill에는 dash_distance 이동 분기가 없다. 경고를 유지하며 이번에 코드를 바꾸지 않는다.
L21: 
L22: ## Projectile scope
L23: 
L24: - 비행/피해 지연 0.35초와 착탄 반경 0.8wu는 유지했다.
L25: - 스텀피만 PROJECTILE+ICON 교체 계획이다. 나머지 11종 projectile_ruid는 KEEP이며 추가 승인 없이 비행체 아트 범위를 늘리지 않았다.
```

## S3. 파우스트의 신규 역할 및 방향/회전 지시

입력: `AREA_03_IMAGES_INPUT_V2_3.zip`
내부 경로: `monsters/005_m_faust_파우스트/GENERATION_SPEC.md`

```text
L1: # GENERATION SPEC — 파우스트 / 저주의 인형
L2: 
L3: ## 확정 데이터
L4: 
L5: - 작업 순번: 005
L6: - 레벨: 20
L7: - Area: `area_03` / 엘리니아
L8: - monster_id: `m_faust`
L9: - 몬스터 이름: 파우스트
L10: - monster image RUID: `9922e94142f9413aa5359297f852a5a2`
L11: - skill_id: `s_mon_faust`
L12: - 최종 스킬 이름: **저주의 인형**
L13: - 스킬 타입: **액티브**
L14: - 보스 여부: 보스
L15: - 확정 기획 효과(보존 원문): INT 계수 1.55로 반경 4 범위 대상 제한 없음 피해; 6초 재사용; 5장 보유 시 계수 ×1.8
L16: - 확인된 런타임 효과: INT 계수 1.55; skill.range=4wu는 조준/탐색 거리; 0.35초 뒤 착탄점 반경 0.8wu에서 제한 없음 피해 판정.
L17: - 확인된 런타임 동작: skill.range=4wu는 플레이어 조준 거리이며 몬스터 사용 시 2.668wu로 대상 탐색한다. projectile_ruid 49b21aaa1d574ba787149841a31bf1a5를 시전자+h에서 목표+h로 0.35초 동안 이동·Z회전시킨 뒤, 착탄점 반경 0.8wu에서 최대 제한 없음 피해를 판정한다. L1 delay=0s duration=0.9s offset=(0,0.1)wu drift=(0,0)wu/s; L2 delay=0.18s duration=0.75s offset=(0,0.05)wu drift=(0,0)wu/s.
L18: 
L19: ## 원작/지역 연결
L20: 
L21: [W1] 파우스트는 이상한 인형에 조종되는 거대 좀비 루팡으로 설명된다.
L22: 
L23: ## 시각 번역
L24: 
L25: - 핵심 소재: 실로 묶인 인형 표식과 아래로 떨어지는 자주색 저주 침. ‘파우스트 / 저주의 인형’ 전용 소재이며 몬스터 본체는 VFX에 직접 넣지 않음
L26: - 주 색상: 저주 자주 #734B91; 핵심 실루엣의 중간톤과 어두운 외곽에 사용
L27: - 보조 색상: 인형 적갈 #A85A61; 타격 코어·잔상·소수 입자에만 사용해 같은 Area의 다른 몬스터와 구분
L28: - 런타임 역할: CAST_VFX=발사/준비 연출; PROJECTILE=엔진이 이동시키는 비행체; ICON=UI 식별
L29: - 효과 발생 위치: CAST_VFX는 시전자 원점. PROJECTILE은 시전자에서 조준 위치로 이동한다. 전용 IMPACT VFX 필드는 현재 없다.
L30: - 진행 방향·엔진 이동: 우측 기준 제작 후 FlipX. PROJECTILE 그림 안에서 캔버스 전체를 좌→우로 이동시키지 않는다(엔진 이동과 중복 금지). layer drift는 엔진 적용: L1 ruid=22444db0645d47f48f300f36b3d90e4b, type=animationclip, style=clip, delay=0s, duration=0.9s, scale=0.55, offset=(0,0.1) world unit, drift=(0,0) world unit/s; L2 ruid=9051254fb84a4a898f3d99a213a896ec, type=animationclip, style=clip, delay=0.18s, duration=0.75s, scale=0.7, offset=(0,0.05) world unit, drift=(0,0) world unit/s
L31: - 대상 표현: 조준 지점은 그림에 캐릭터로 표시하지 않는다. 현재 전용 IMPACT 출력은 요구하지 않는다.
L32: - 화면 점유율: 큼(캐릭터 2~3배, 화면을 가리지 않음); 핵심 소재 전체가 캔버스 안전영역 70% 안에 들고 외곽 파편은 85%를 넘지 않음
L33: - 이펙트 밀도: 높음; 대표 형상 1개, 보조 궤적/층 1~3개, 식별용 파편 3~7개만 사용
L34: - 시간 흐름: CAST는 발사 준비 → 방출 섬광 → 짧은 잔광. PROJECTILE은 동일 중심축에서 자체 회전/맥동만 하며 위치 이동은 엔진에 맡긴다.
L35: - 판정 정렬: 투사체가 0.35초 뒤 도착할 때 피해 판정. CAST_VFX는 발사 시점에 시작한다.
L36: - 아이콘 핵심 모티브: 대표 실루엣 1개는 ‘실 묶인 인형 표식’, 보조 효과 1개는 ‘저주 침’. 64px 축소에서도 두 형상의 겹침과 방향이 읽혀야 함
L37: - 몬스터 본체 금지 범위: 몸·얼굴·전신 실루엣은 VFX에 넣지 않는다. 다만 확정 핵심 소재인 인형·손자국·가면·껍질·뿔·장비 파편은 해당 명세대로 유지한다.
L38: 
L39: ## 해석 주의
L40: 
L41: - 확정 스킬명·타입·효과·동작을 바꾸지 않는다.
L42: - 몬스터 본체를 VFX 안에 직접 그리지 않는다.
L43: - 기존 플레이어 스킬의 무기·캐릭터·실루엣을 복제하지 않는다.
L44: 
L45: ## 출력 프로필
L46: 
L47: - ICON: NEW_ART / ICON/005_m_faust_s_mon_faust_ICON.png / 256x256 RGBA
L48: - CAST_VFX: NEW_ART / CAST/005_m_faust_s_mon_faust_CAST_F00.png..._CAST_F11.png / 12 frames × 512x512 RGBA / 0.08s per frame / non-loop one-shot
L49: - PROJECTILE: NEW_ART / PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F00.png..._PROJECTILE_F03.png / 4 frames × 512x512 RGBA / 0.08s per frame / non-loop complete playback within 0.35s entity lifetime
L50: - 역할별 파일을 섞지 않는다. HIT/PERSISTENT 역할 없음 행은 신규 제작하지 않는다.
L51: 
L52: ## V2.3 전체 아트 제작 계약
L53: 
L54: - required_roles: `ICON|CAST_VFX|PROJECTILE`
L55: - production_decisions: `NEW_ART|NEW_ART|NEW_ART`
L56: - future_targets: `icon_ruid|layer_ruids|projectile_ruid`
L57: - production_ready: `READY`
L58: - import_ready: `NOT_READY_ASSETS_NOT_GENERATED`
L59: 
L60: ### Role inventory
L61: 
L62: - ICON: current=true; decision=NEW_ART; field=icon_ruid; files=ICON/005_m_faust_s_mon_faust_ICON.png; target=icon_ruid
L63: - CAST_VFX: current=true; decision=NEW_ART; field=layer_ruids; files=CAST/005_m_faust_s_mon_faust_CAST_F00.png..._CAST_F11.png; target=layer_ruids
L64: - PROJECTILE: current=true; decision=NEW_ART; field=projectile_ruid; files=PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F00.png..._PROJECTILE_F03.png; target=projectile_ruid
L65: - HIT_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L66: - PERSISTENT_BUFF_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L67: - REFERENCE_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L68: 
L69: ### Shared constraints
L70: 
L71: - CAST와 PROJECTILE은 독립 파일 세트다. 같은 VFX 한 세트로 합치지 않는다.
L72: - PROJECTILE은 4×0.08=0.32초 non-loop로 0.35초 수명 안에 완주하며 엔진 이동·ZRotation을 이미지 안에서 중복하지 않는다.
L73: - 전용 HIT/PERSISTENT 시각 호출이 없으므로 해당 파일을 만들지 않는다.
L74: - 복수 CAST 레이어 통합은 기존 delay/offset/drift의 상대 리듬을 한 로컬 캔버스 clip에 베이크한다. 원본 레이어 정보는 ASSET_BINDING_PLAN에 남긴다.
L75: - targeting_range와 impact_radius는 별개이며 이미지로 조준 거리 전체를 피해 범위처럼 표현하지 않는다.
L76: - PREVIEW/labeled_preview.png와 Area overview는 필수 검수물이고 별도 contact sheet만 선택이다.
```

## S4. 역할별 방향의 현행 공통 계약

입력: `AREA_03_IMAGES_INPUT_V2_3.zip`
내부 경로: `OUTPUT_FORMAT_SPEC.md`

```text
L1: # Output Format Spec — V2.3
L2: 
L3: - `FULL_ART_SCOPE.csv` defines every actual/new/reused/absent role; `OUTPUT_REQUIREMENTS.csv` mirrors it.
L4: - Primary art delivery is frame-separated RGBA PNG. Same role means identical canvas/pivot/scale.
L5: - CAST uses the existing skill profile recorded in GENERATION_SPEC.
L6: - Every actual PROJECTILE is newly produced as 4 frames × 0.08s = 0.32s non-loop within unchanged 0.35s entity life. Stumpy remains this exact contract.
L7: - PROJECTILE artwork is direction-neutral and does not duplicate engine translation/ZRotation. Current code has no PROJECTILE FlipX/travel alignment.
L8: - ICON is 256×256 RGBA. Passive REFERENCE is preview-only and runtime_use=false.
L9: - No dedicated HIT/PERSISTENT visual path exists; do not generate those roles.
L10: - targeting_range is not impact_radius. Do not depict target-search range as impact damage coverage.
L11: - PACKAGE_VALIDATION/PRODUCTION_READY/IMPORT_READY/RUNTIME_VALIDATION/ART_APPROVAL remain separate.
```

## S5. 스텀피 명세

입력: `AREA_02_IMAGES_INPUT_V2_3.zip`
내부 경로: `monsters/008_m_stumpy_스텀피/GENERATION_SPEC.md`

```text
L1: # GENERATION SPEC — 스텀피 / 고목의 생기탄
L2: 
L3: ## 확정 데이터
L4: 
L5: - 작업 순번: 008
L6: - 레벨: 42
L7: - Area: `area_02` / 페리온
L8: - monster_id: `m_stumpy`
L9: - 몬스터 이름: 스텀피
L10: - monster image RUID: `0b6c2f6faccc44da980ce832ab636bf6`
L11: - skill_id: `s_mon_stumpy`
L12: - 최종 스킬 이름: **고목의 생기탄**
L13: - 스킬 타입: **액티브**
L14: - 보스 여부: 보스
L15: - 확정 기획 효과(보존 원문): INT 계수 1.9로 반경 5 범위 대상 제한 없음 피해; 7초 재사용; 5장 보유 시 계수 ×1.8
L16: - 확인된 런타임 효과: INT 계수 1.9; skill.range=5wu는 조준/탐색 거리; 0.35초 뒤 착탄점 반경 0.8wu에서 제한 없음 피해 판정.
L17: - 확인된 런타임 동작: skill.range=5wu는 플레이어 조준 거리이며 몬스터 사용 시 3.335wu로 대상 탐색한다. projectile_ruid c6b3f052e977479ea5ad5329ce0981ca를 시전자+h에서 목표+h로 0.35초 동안 이동·Z회전시킨 뒤, 착탄점 반경 0.8wu에서 최대 제한 없음 피해를 판정한다. CAST 레이어 없음.
L18: 
L19: ## 원작/지역 연결
L20: 
L21: [P][A] 고목형 몬스터와 생기는 연결 가능하나 ‘빼앗은 생기’와 생기탄은 확인되지 않았다.
L22: 
L23: ## 해석 주의
L24: 
L25: - 확정 스킬명·타입·효과·동작을 바꾸지 않는다.
L26: - 몬스터 본체를 VFX 안에 직접 그리지 않는다.
L27: - 기존 플레이어 스킬의 무기·캐릭터·실루엣을 복제하지 않는다.
L28: 
L29: ## 시각 번역
L30: 
L31: - 핵심 소재: 고목 나이테에서 싹이 돋아 응축된 생기탄. 몬스터 본체는 넣지 않는다.
L32: - 주 색상: 고목 갈색 #75533A / 보조 색상: 생기 연두 #8ED35B.
L33: - 효과 발생 위치: 움직이는 projectile entity의 로컬 중심.
L34: - 진행 방향: 원화 자체는 방향 중립. 엔진은 위치 보간과 Z축 회전만 하며 FlipX·진행 방향 자동 정렬은 하지 않는다.
L35: - 대상 표현: 타깃 캐릭터와 조준 범위를 이미지에 넣지 않는다. 전용 IMPACT VFX도 만들지 않는다.
L36: - 화면 점유율: 핵심 소재 70%, 외곽 파편 85% 이내. 이펙트 밀도는 보스 체급이되 투사체 실루엣을 흐리지 않는다.
L37: - 시간 흐름: F00 응축 → F01 발광 상승 → F02 절정 → F03 안정/잔광. 0.32초 안에 한 번 완결된다.
L38: - 아이콘 핵심 모티브: 싹튼 나이테 + 작은 생기 코어. 64px에서도 두 형상이 읽혀야 한다.
L39: 
L40: ## 출력 프로필
L41: 
L42: - ICON: NEW_ART / ICON/008_m_stumpy_s_mon_stumpy_ICON.png / 256x256 RGBA
L43: - PROJECTILE: NEW_ART / PROJECTILE/008_m_stumpy_s_mon_stumpy_PROJECTILE_F00.png..._PROJECTILE_F03.png / 4 frames × 512x512 RGBA / 0.08s per frame / non-loop complete playback within 0.35s entity lifetime
L44: - 역할별 파일을 섞지 않는다. HIT/PERSISTENT 역할 없음 행은 신규 제작하지 않는다.
L45: 
L46: ## V2.3 전체 아트 제작 계약
L47: 
L48: - required_roles: `ICON|PROJECTILE`
L49: - production_decisions: `NEW_ART|NEW_ART`
L50: - future_targets: `icon_ruid|projectile_ruid`
L51: - production_ready: `READY`
L52: - import_ready: `NOT_READY_ASSETS_NOT_GENERATED`
L53: 
L54: ### Role inventory
L55: 
L56: - ICON: current=true; decision=NEW_ART; field=icon_ruid; files=ICON/008_m_stumpy_s_mon_stumpy_ICON.png; target=icon_ruid
L57: - CAST_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L58: - PROJECTILE: current=true; decision=NEW_ART; field=projectile_ruid; files=PROJECTILE/008_m_stumpy_s_mon_stumpy_PROJECTILE_F00.png..._PROJECTILE_F03.png; target=projectile_ruid
L59: - HIT_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L60: - PERSISTENT_BUFF_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L61: - REFERENCE_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
L62: 
L63: ### Shared constraints
L64: 
L65: - CAST와 PROJECTILE은 독립 파일 세트다. 같은 VFX 한 세트로 합치지 않는다.
L66: - PROJECTILE은 4×0.08=0.32초 non-loop로 0.35초 수명 안에 완주하며 엔진 이동·ZRotation을 이미지 안에서 중복하지 않는다.
L67: - 전용 HIT/PERSISTENT 시각 호출이 없으므로 해당 파일을 만들지 않는다.
L68: - 복수 CAST 레이어 통합은 기존 delay/offset/drift의 상대 리듬을 한 로컬 캔버스 clip에 베이크한다. 원본 레이어 정보는 ASSET_BINDING_PLAN에 남긴다.
L69: - targeting_range와 impact_radius는 별개이며 이미지로 조준 거리 전체를 피해 범위처럼 표현하지 않는다.
L70: - PREVIEW/labeled_preview.png와 Area overview는 필수 검수물이고 별도 contact sheet만 선택이다.
```

## S6. 파란 달팽이 역할별 필요 파일과 RUID

입력: `AREA_01_IMAGES_INPUT_V2_3.zip`
내부 경로: `FULL_ART_SCOPE.csv`

```text
L1: area_id,area_name,work_order,monster_id,monster_name,skill_id,skill_name,skill_type,pivot,targeting_range,impact_radius,impact_delay,effect_role,current_use,current_field_or_layer,current_resource,production_decision,required_file_set,frame_count,canvas,frame_seconds,total_seconds,playback_mode,direction_and_engine_motion,future_target,consolidation_strategy,runtime_use,unresolved,evidence
L2: area_01,헤네시스 근교,001,m_snail,달팽이,s_mon_snail_dew_trail,이슬 미끄럼길,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,ICON,true,icon_ruid,c0699b32529049c68de3d13022479bf9,AREA00_APPROVED_REUSE,approved_reuse/AREA_00/001_m_snail_달팽이/ICON/001_m_snail_s_mon_snail_dew_trail_ICON.png|approved_reuse/AREA_00/001_m_snail_달팽이/PREVIEW/001_m_snail_s_mon_snail_dew_trail_CONTACT_PREVIEW.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F00.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F01.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F02.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F03.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F04.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F05.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F06.png|approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F07.png,1,256x256 RGBA,static,static,static,none,icon_ruid,n/a,ui,none,SkillTable.icon_ruid; Area00 resource map/hash
L7: area_01,헤네시스 근교,001,m_snail,달팽이,s_mon_snail_dew_trail,이슬 미끄럼길,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,REFERENCE_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none,SkillTable visual fields + PlayerAttack/MonsterAttack/SkillEffect code
L8: area_01,헤네시스 근교,002,m_blue_snail,파란 달팽이,s_mon_blue_snail,푸른 껍질,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,ICON,true,icon_ruid,73c1bdafcb7e42bc8db0041883226449,AREA00_APPROVED_REUSE,approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/ICON/002_m_blue_snail_s_mon_blue_snail_ICON.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/PREVIEW/002_m_blue_snail_s_mon_blue_snail_CONTACT_PREVIEW.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F00.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F01.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F02.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F03.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F04.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F05.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F06.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F07.png,1,256x256 RGBA,static,static,static,none,icon_ruid,n/a,ui,none,SkillTable.icon_ruid; Area00 resource map/hash
L9: area_01,헤네시스 근교,002,m_blue_snail,파란 달팽이,s_mon_blue_snail,푸른 껍질,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,CAST_VFX,true,layer_ruids,"L1:566b0886b4cf4f3997a29ecd3a1954b5 animationclip/clip delay=0s duration=0.85s scale=0.65 offset=(0,0)wu drift=(0,0)wu/s; L2:86734a2715504c10b1e50ae810609e25 animationclip/clip delay=0.12s duration=0.7s scale=0.75 offset=(0,0)wu drift=(0,0)wu/s",AREA00_APPROVED_REUSE,approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/ICON/002_m_blue_snail_s_mon_blue_snail_ICON.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/PREVIEW/002_m_blue_snail_s_mon_blue_snail_CONTACT_PREVIEW.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F00.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F01.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F02.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F03.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F04.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F05.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F06.png|approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F07.png,8,256x256 RGBA,0.1,0.8,approved existing,SkillEffect applies FlipX for directional attacks; delayed layer samples caster position at SpawnLayer execution; map entity then applies drift,approved existing layer_ruids,AREA00 approved mapping unchanged,true,none,SkillTable layer/effect fields; SkillEffect.PlayCast/SpawnLayer
L10: area_01,헤네시스 근교,002,m_blue_snail,파란 달팽이,s_mon_blue_snail,푸른 껍질,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,PROJECTILE,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none,SkillTable visual fields + PlayerAttack/MonsterAttack/SkillEffect code
L11: area_01,헤네시스 근교,002,m_blue_snail,파란 달팽이,s_mon_blue_snail,푸른 껍질,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,HIT_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none; no dedicated hit/impact visual field or Spawn call in current common projectile path,PlayerAttack.ResolveThrowHit; MonsterAttack.ResolveThrowHit; SkillEffect has no hit asset argument
L12: area_01,헤네시스 근교,002,m_blue_snail,파란 달팽이,s_mon_blue_snail,푸른 껍질,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,PERSISTENT_BUFF_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none; defense mechanics may persist but current visual is one-shot CAST only,MonsterAttack defense branch + SkillEffect.PlayCast; no persistent visual entity field
L13: area_01,헤네시스 근교,002,m_blue_snail,파란 달팽이,s_mon_blue_snail,푸른 껍질,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,REFERENCE_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none,SkillTable visual fields + PlayerAttack/MonsterAttack/SkillEffect code
L14: area_01,헤네시스 근교,003,m_mushroom,주황 버섯,s_mon_mushroom,포자 살포,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,ICON,true,icon_ruid,6923ce8064e4445d8e63176645943fb1,NEW_ART,ICON/003_m_mushroom_s_mon_mushroom_ICON.png,1,256x256 RGBA,static,static,static,none,icon_ruid,n/a,ui,none,SkillTable.icon_ruid
```

## S7. 슬라임 역할별 필요 파일과 RUID

입력: `AREA_03_IMAGES_INPUT_V2_3.zip`
내부 경로: `FULL_ART_SCOPE.csv`

```text
L1: area_id,area_name,work_order,monster_id,monster_name,skill_id,skill_name,skill_type,pivot,targeting_range,impact_radius,impact_delay,effect_role,current_use,current_field_or_layer,current_resource,production_decision,required_file_set,frame_count,canvas,frame_seconds,total_seconds,playback_mode,direction_and_engine_motion,future_target,consolidation_strategy,runtime_use,unresolved,evidence
L2: area_03,엘리니아,001,m_slime,슬라임,s_mon_slime,끈적한 몸통,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,ICON,true,icon_ruid,72d1dd0939714240bddc0b6865eb93ce,AREA00_APPROVED_REUSE,approved_reuse/AREA_00/005_m_slime_슬라임/ICON/005_m_slime_s_mon_slime_ICON.png|approved_reuse/AREA_00/005_m_slime_슬라임/PREVIEW/005_m_slime_s_mon_slime_CONTACT_PREVIEW.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F00.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F01.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F02.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F03.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F04.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F05.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F06.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F07.png,1,256x256 RGBA,static,static,static,none,icon_ruid,n/a,ui,none,SkillTable.icon_ruid; Area00 resource map/hash
L3: area_03,엘리니아,001,m_slime,슬라임,s_mon_slime,끈적한 몸통,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,CAST_VFX,true,layer_ruids,"L1:2c12c1e835a04c2a9ec1c5724846a7b6 animationclip/clip delay=0s duration=0.62s scale=0.48 offset=(0.18,0)wu drift=(0.35,0)wu/s; L2:69656381a8e04edcbb8a2c8599567ab3 animationclip/clip delay=0.12s duration=0.52s scale=0.55 offset=(0.5,0)wu drift=(0,0)wu/s",AREA00_APPROVED_REUSE,approved_reuse/AREA_00/005_m_slime_슬라임/ICON/005_m_slime_s_mon_slime_ICON.png|approved_reuse/AREA_00/005_m_slime_슬라임/PREVIEW/005_m_slime_s_mon_slime_CONTACT_PREVIEW.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F00.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F01.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F02.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F03.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F04.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F05.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F06.png|approved_reuse/AREA_00/005_m_slime_슬라임/VFX/005_m_slime_s_mon_slime_F07.png,8,256x256 RGBA,0.1,0.8,approved existing,SkillEffect applies FlipX for directional attacks; delayed layer samples caster position at SpawnLayer execution; map entity then applies drift,approved existing layer_ruids,AREA00 approved mapping unchanged,true,none,SkillTable layer/effect fields; SkillEffect.PlayCast/SpawnLayer
L4: area_03,엘리니아,001,m_slime,슬라임,s_mon_slime,끈적한 몸통,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,PROJECTILE,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none,SkillTable visual fields + PlayerAttack/MonsterAttack/SkillEffect code
L5: area_03,엘리니아,001,m_slime,슬라임,s_mon_slime,끈적한 몸통,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,HIT_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none; no dedicated hit/impact visual field or Spawn call in current common projectile path,PlayerAttack.ResolveThrowHit; MonsterAttack.ResolveThrowHit; SkillEffect has no hit asset argument
L6: area_03,엘리니아,001,m_slime,슬라임,s_mon_slime,끈적한 몸통,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,PERSISTENT_BUFF_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none; defense mechanics may persist but current visual is one-shot CAST only,MonsterAttack defense branch + SkillEffect.PlayCast; no persistent visual entity field
L7: area_03,엘리니아,001,m_slime,슬라임,s_mon_slime,끈적한 몸통,액티브,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,REFERENCE_VFX,false,none,,NO_RUNTIME_ROLE,none,0,n/a,n/a,n/a,n/a,n/a,none,n/a,false,none,SkillTable visual fields + PlayerAttack/MonsterAttack/SkillEffect code
L8: area_03,엘리니아,002,m_dark_stump,다크 스텀프,s_mon_dark_stump,단단한 밑동,버프,"normalized (0.5,0.5); no autocrop/recenter",n/a,n/a,n/a,ICON,true,icon_ruid,8061aa7a332b4e7ba783b3cd582ebb4b,NEW_ART,ICON/002_m_dark_stump_s_mon_dark_stump_ICON.png,1,256x256 RGBA,static,static,static,none,icon_ruid,n/a,ui,none,SkillTable.icon_ruid
```

## S8. 새로운 CSV와 맞지 않는 설명 문서

입력: `AREA_03_IMAGES_INPUT_V2_3.zip`
내부 경로: `ASSET_BINDING_PLAN.md`

```text
L1: # ASSET BINDING PLAN
L2: 
L3: CSV가 연결 계획의 원장이다. KEEP은 승인 전 현행 보존, REPLACE_PLANNED는 아트 승인 후 교체 계획, APPROVED_REUSE는 Area 00 승인본, REFERENCE_ONLY는 런타임 미사용이다. 신규 RUID 부재는 오류가 아니다.
```

## S9. 재사용 정책·해시 원문

입력: `AREA_01_IMAGES_INPUT_V2_3.zip`
내부 경로: `approved_reuse/AREA_00_REUSE_MANIFEST.md`

```text
L2: 
L3: 아래 파일은 AREA 00 승인 OUTPUT의 바이트 복사본이다. 호환되는 동일 monster_id + skill_id에만 재사용하며 다시 생성하지 않는다.
L4: 
L5: ## m_snail / s_mon_snail_dew_trail
L6: 
L8: - files:
L9:   - `approved_reuse/AREA_00/001_m_snail_달팽이/ICON/001_m_snail_s_mon_snail_dew_trail_ICON.png` — SHA-256 `9e4c5c2bf3f0edd39e3de4855d0eb2c16a049d879a88fe104fb91e5eb76a5446`
L10:   - `approved_reuse/AREA_00/001_m_snail_달팽이/PREVIEW/001_m_snail_s_mon_snail_dew_trail_CONTACT_PREVIEW.png` — SHA-256 `fb8219560516c240f9a18a7744b483ebcf487e895a8c8a7f6fd28c21e7bdc98e`
L11:   - `approved_reuse/AREA_00/001_m_snail_달팽이/PREVIEW/labeled_preview.png` — SHA-256 `b2848ad484da3d67b10a3a1616be47fd2c9cd85659e617b429ac08b52cda5d32`
L12:   - `approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F00.png` — SHA-256 `b7e74d47734d5b6bbcdbe3c68d99ed67b360eff4c6c73bcf4b141ba69b4d3525`
L13:   - `approved_reuse/AREA_00/001_m_snail_달팽이/VFX/001_m_snail_s_mon_snail_dew_trail_F01.png` — SHA-256 `41302b32898fa0136beeba6c6959da7694f35bab7bf6c63a4f6b0f9a45e94b7b`
L20: 
L21: ## m_blue_snail / s_mon_blue_snail
L22: 
L24: - files:
L25:   - `approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/ICON/002_m_blue_snail_s_mon_blue_snail_ICON.png` — SHA-256 `defd113ea3c59d8b570f73a79533b4253b5e72f789347e13aaa6cdbfefe65d27`
L26:   - `approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/PREVIEW/002_m_blue_snail_s_mon_blue_snail_CONTACT_PREVIEW.png` — SHA-256 `ae99795e61bc6eb9e14c0396fcaa576cda252dbf9ec738a1902bebfbf30c2424`
L27:   - `approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/PREVIEW/labeled_preview.png` — SHA-256 `31869bf284cf60325a6c2a833d1ea993c1593b36796977843760bad3858a44ea`
L28:   - `approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F00.png` — SHA-256 `d7b55014803cf9feed39d079ceb5deef7bf7f2780bfbbca351f8b3f6c00d8b7c`
L29:   - `approved_reuse/AREA_00/002_m_blue_snail_파란_달팽이/VFX/002_m_blue_snail_s_mon_blue_snail_F01.png` — SHA-256 `cfac5775668a4cbc3538bc0bf5d3128c156420b4b10154719e7b40b2f3e954c8`
```

## S10. 이전에 제공된 AREA 00 승인 연결표

입력: `INPUT_V2_1_EVIDENCE.zip`
내부 경로: `INPUT_V2_1_EVIDENCE/area00_approval/AREA_00_IMAGES_RESOURCE_MAP.csv`
V2.3에서 재사용한 그림의 RUID 판정 근거.

```csv
monster_id,skill_id,skill_name,icon_ruid,animationclip_ruid,frame_count,canvas_rgba,frame_seconds,total_seconds,frame_sprite_ruids
m_snail,s_mon_snail_dew_trail,이슬 미끄럼길,c0699b32529049c68de3d13022479bf9,6097484d513a4fde82ad15557fdc81d3,8,384x384 RGBA,0.1,0.8,b23e5b681ff9406d92fdc0f1f70a5a9a|082b3c6ef149443ca3d3ec4cb47138de|4207b2fc18ef4beb8036e9c36ad7be75|c7559a6bbb094dd6be42a270f151df9e|538e7814b00f417d95a622235cda10aa|a367a0f2116441f3affbdfaa3015dfcf|e629a1d5081e420d95a047feafce731a|1b07ed19b7274ed8917c1a847abf8e06
m_blue_snail,s_mon_blue_snail,푸른 껍질,6e7da13ea5924763bebb7aa4b851eb96,f1fc98b763c24a0bb99d8ce8453a4c8f,8,256x256 RGBA,0.1,0.8,67d130ff8cf348baaaa8b5b82aea85c5|c41282607dbd4ce0a883978a76940a0d|cde85252be8e45c4a13e257bfa876865|66631abd26f648b0b3daea8e79788432|b5255e0b14e044b4bf33000ef0b4c501|95349175b489445ca7f3d613457b3dc7|17eaca36217d49329aca30dede462aa2|a251a69e389f4d03850bbc02c77a1a5d
m_red_snail,s_mon_red_snail,붉은 껍질 돌진,12d807f89a284616a966513250bc3b7c,b61e270e3118440680f2a51d12255693,8,256x256 RGBA,0.1,0.8,fea38079e8ee43d580fef757784a3f70|81911b1961704788a534958e499fcd55|22ab27608b014456907b1919961df2a5|5f6fba23db4e4a8db84c9786742d3ad0|10b8ad4f71a24f158e440680ba8ac825|e1bfc7ff930144aea284ef24112eae8d|a86bd71cf2514b65a561a6ab1542bf4d|748896b796bc4e44a8458fe94127a621
m_mano,s_mon_mano,마노의 무지개 파동,0cf7d9ac7fa4460a897c5f5e8ce47c51,b71327c616e64d678ee1ab4e60512ea2,12,512x512 RGBA,0.1,1.2,18c388414a71435c9175691be18dd103|8cc1e0df0ab744f6be1aaa17f716a734|cdfd8644fe974b8c8615f1fbc584cdc2|a5c42d7f87a24579a6c9704cd3952c04|2cb68a091e7142cbbc31334b599e2b49|05f0f48c0c47422f939be99fd6495af8|c5277807489f449db45d814cf81399b5|fa19ebe222824853a2c6c651b25f2bf6|f5434f7cabf7498e8ce78fb1b94bf798|aa9c56bfdd4b44f680afa584aa6e3d41|72f1133aaa564ac48da35a4900f4292b|e633f606a5104dd788fc2be7d82a3f0a
m_slime,s_mon_slime,끈적한 몸통,79543e5ad88d423ba676e55d69aa432c,0ea4bec10d4c43f3aaded74dec60ca44,8,256x256 RGBA,0.1,0.8,e391a4d0e3f44f338782433dd17b74af|18cb10eff1e54c8f890dae03926f9bbe|fbdb98e19f2c4e9fa2322ead88affa35|7ee83b952f4c4b5d9e3d13e8ca5df164|5256cc5176e446ae87ce8597d4483038|10df075f432b4c8d886f4653a612abdf|9a52c8e028ca4403b160a6a9bde92ca3|e5e1c511d5344244aab7e2f4fe9d7b95
```

## S11. V2.2의 승인 연결값 보존 여부

입력: `AREA_01_IMAGES_INPUT_V2_2.zip`, `AREA_03_IMAGES_INPUT_V2_2.zip` / `ASSET_BINDING_PLAN.csv`

```json
[
  {
    "area_id": "area_01",
    "monster_id": "m_blue_snail",
    "skill_id": "s_mon_blue_snail",
    "skill_type": "버프",
    "effect_role": "APPROVED_REUSE_CAST_VFX+ICON",
    "current_field": "layer_ruids|icon_ruid",
    "current_layer": "approved single layer",
    "current_ruid": "f1fc98b763c24a0bb99d8ce8453a4c8f|6e7da13ea5924763bebb7aa4b851eb96",
    "decision": "APPROVED_REUSE",
    "new_file_set": "approved_reuse/AREA_00/* (byte-identical)",
    "target_field": "layer_ruids|icon_ruid",
    "target_layer": "approved mapping only",
    "attach_to": "caster",
    "player_behavior": "AREA 00 report: left/right playback verified",
    "monster_behavior": "AREA 00 report: monster caster playback verified",
    "delay_seconds": "0",
    "duration_seconds": "0.8",
    "loop": "false",
    "frame_timing": "8 frames × 0.10s; same 256×256 RGBA canvas",
    "coordinate_unit": "runtime offset=world unit; drift=world unit/s; art=pixel canvas; pivot=normalized",
    "direction": "approved left/right behavior",
    "flip_x": "approved runtime behavior",
    "scale": "1",
    "pivot": "(0.5,0.5) planned registration pivot; no autocrop/recenter",
    "offset": "(0,0) approved",
    "image_internal_vs_engine": "approved frames preserved; no regeneration",
    "source_evidence": "runtime_evidence/RUNTIME_CODE_EVIDENCE.md; ASSET_BINDING_PLAN.md",
    "notes": "신규 생성 금지; reuse manifest SHA must match",
    "generation_required": "false",
    "runtime_use": "true",
    "targeting_range": "n/a",
    "monster_targeting_range": "n/a",
    "impact_radius": "n/a",
    "impact_delay": "n/a",
    "max_targets": "n/a",
    "contract_status": "READY"
  },
  {
    "area_id": "area_03",
    "monster_id": "m_slime",
    "skill_id": "s_mon_slime",
    "skill_type": "액티브",
    "effect_role": "APPROVED_REUSE_CAST_VFX+ICON",
    "current_field": "layer_ruids|icon_ruid",
    "current_layer": "approved single layer",
    "current_ruid": "0ea4bec10d4c43f3aaded74dec60ca44|79543e5ad88d423ba676e55d69aa432c",
    "decision": "APPROVED_REUSE",
    "new_file_set": "approved_reuse/AREA_00/* (byte-identical)",
    "target_field": "layer_ruids|icon_ruid",
    "target_layer": "approved mapping only",
    "attach_to": "caster",
    "player_behavior": "AREA 00 report: left/right playback verified",
    "monster_behavior": "AREA 00 report: monster caster playback verified",
    "delay_seconds": "0",
    "duration_seconds": "0.8",
    "loop": "false",
    "frame_timing": "8 frames × 0.10s; same 256×256 RGBA canvas",
    "coordinate_unit": "runtime offset=world unit; drift=world unit/s; art=pixel canvas; pivot=normalized",
    "direction": "approved left/right behavior",
    "flip_x": "approved runtime behavior",
    "scale": "1",
    "pivot": "(0.5,0.5) planned registration pivot; no autocrop/recenter",
    "offset": "(0,0) approved",
    "image_internal_vs_engine": "approved frames preserved; no regeneration",
    "source_evidence": "runtime_evidence/RUNTIME_CODE_EVIDENCE.md; ASSET_BINDING_PLAN.md",
    "notes": "신규 생성 금지; reuse manifest SHA must match",
    "generation_required": "false",
    "runtime_use": "true",
    "targeting_range": "n/a",
    "monster_targeting_range": "n/a",
    "impact_radius": "n/a",
    "impact_delay": "n/a",
    "max_targets": "n/a",
    "contract_status": "READY"
  }
]
```
