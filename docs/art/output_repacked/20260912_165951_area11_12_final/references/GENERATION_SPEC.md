# GENERATION SPEC — 킹 블록퍼스 / 왕관 블록탄

## 확정 데이터

- 작업 순번: 004
- 레벨: 108
- Area: `area_11` / 루더스 호수
- monster_id: `m_king_bloctopus`
- 몬스터 이름: 킹 블록퍼스
- monster image RUID: `cb5eb9faaf68477292af0b710e383c9d`
- skill_id: `s_mon_king_bloctopus`
- 최종 스킬 이름: **왕관 블록탄**
- 스킬 타입: **액티브**
- 보스 여부: 일반 몬스터
- 확정 기획 효과(보존 원문): INT 계수 3.5로 단일 대상 피해; 7초 재사용; 5장 보유 시 계수 ×1.8
- 확인된 런타임 효과: INT 계수 3.5; skill.range=6.8wu는 조준/탐색 거리; 0.35초 뒤 착탄점 반경 0.8wu에서 최대 1대상 피해 판정.
- 확인된 런타임 동작: skill.range=6.8wu는 플레이어 조준 거리이며 몬스터 사용 시 4.5356000000000005wu로 대상 탐색한다. projectile_ruid a2da67e687994755a8943c2bcf871902를 시전자+h에서 목표+h로 0.35초 동안 이동·Z회전시킨 뒤, 착탄점 반경 0.8wu에서 최대 1대상 피해를 판정한다. L1 delay=0.22s duration=0.65s offset=(0,0)wu drift=(0,0)wu/s.

## 원작/지역 연결

[P][A] 킹 블록퍼스의 킹/블록 어휘는 반영됐다.

## 시각 번역

- 핵심 소재: 왕관 블록이 회전하며 각진 에너지 조각을 발사하는 탄. ‘킹 블록퍼스 / 왕관 블록탄’ 전용 소재이며 몬스터 본체는 VFX에 직접 넣지 않음
- 주 색상: 왕관 금색 #E9C85B; 핵심 실루엣의 중간톤과 어두운 외곽에 사용
- 보조 색상: 블록 자주 #765A9F; 타격 코어·잔상·소수 입자에만 사용해 같은 Area의 다른 몬스터와 구분
- 런타임 역할: CAST_VFX=발사/준비 연출; PROJECTILE=엔진이 이동시키는 비행체; ICON=UI 식별
- 효과 발생 위치: CAST_VFX는 시전자 원점. PROJECTILE은 시전자에서 조준 위치로 이동한다. 전용 IMPACT VFX 필드는 현재 없다.
- CAST 방향/표현: 우측 기준 제작 후 FlipX는 CAST_VFX에만 적용한다. 왕관 블록과 각진 에너지 조각이 시전자 원점에서 조립되어 발사되는 준비 연출. 기존 CAST layer drift는 엔진 적용: L1 ruid=e53471f0f7114343907be7beb520751f, type=animationclip, style=clip, delay=0.22s, duration=0.65s, scale=0.9, offset=(0,0) world unit, drift=(0,0) world unit/s
- PROJECTILE 방향/표현: 로컬 중심·방향 중립이며 PROJECTILE FlipX나 진행 방향 자동 정렬을 가정하지 않는다. 왕관 블록 핵과 소수의 각진 에너지 조각으로 이루어진 방향 중립 비행체.
- PROJECTILE 국소 애니메이션: 왕관 블록 중심부와 주변 조각의 상대 회전만 표현하고 캔버스 전체 회전은 원화에 넣지 않는다. 엔진이 시전자+h에서 목표+h까지 이동시키고 ZRotation을 적용하므로 그 전체 이동·회전을 이미지 프레임에 중복하지 않는다.
- 대상 표현: 조준 지점은 그림에 캐릭터로 표시하지 않는다. 현재 전용 IMPACT 출력은 요구하지 않는다.
- 화면 점유율: 중간(캐릭터 1.2~2배); 핵심 소재 전체가 캔버스 안전영역 70% 안에 들고 외곽 파편은 85%를 넘지 않음
- 이펙트 밀도: 중간; 대표 형상 1개, 보조 궤적/층 1~3개, 식별용 파편 3~7개만 사용
- 역할별 시간 흐름: CAST는 발사 준비 → 방출 섬광 → 짧은 잔광. PROJECTILE은 F00 형성 → F01 상승 → F02 절정 → F03 안정/잔광을 동일 로컬 중심에서 완결하며 위치 이동은 엔진에 맡긴다.
- 판정 정렬: 투사체가 0.35초 뒤 도착할 때 피해 판정. CAST_VFX는 발사 시점에 시작한다.
- 아이콘 핵심 모티브: 대표 실루엣 1개는 ‘왕관 블록’, 보조 효과 1개는 ‘각진 탄 궤적’. 64px 축소에서도 두 형상의 겹침과 방향이 읽혀야 함
- 몬스터 본체 금지 범위: 몸·얼굴·전신 실루엣은 VFX에 넣지 않는다. 다만 확정 핵심 소재인 인형·손자국·가면·껍질·뿔·장비 파편은 해당 명세대로 유지한다.

## 해석 주의

- 확정 스킬명·타입·효과·동작을 바꾸지 않는다.
- 몬스터 본체를 VFX 안에 직접 그리지 않는다.
- 기존 플레이어 스킬의 무기·캐릭터·실루엣을 복제하지 않는다.

## 출력 프로필

- ICON: NEW_ART / ICON/004_m_king_bloctopus_s_mon_king_bloctopus_ICON.png / 256x256 RGBA
- CAST_VFX: NEW_ART / CAST/004_m_king_bloctopus_s_mon_king_bloctopus_CAST_F00.png..._CAST_F07.png / 8 frames × 384x384 RGBA / 0.10s per frame / non-loop one-shot
- PROJECTILE: NEW_ART / PROJECTILE/004_m_king_bloctopus_s_mon_king_bloctopus_PROJECTILE_F00.png..._PROJECTILE_F03.png / 4 frames × 384x384 RGBA / 0.08s per frame / non-loop complete playback within 0.35s entity lifetime
- 역할별 파일을 섞지 않는다. HIT/PERSISTENT 역할 없음 행은 신규 제작하지 않는다.

## V2.4 전체 아트 제작 계약

- required_roles: `ICON|CAST_VFX|PROJECTILE`
- production_decisions: `NEW_ART|NEW_ART|NEW_ART`
- future_targets: `icon_ruid|layer_ruids|projectile_ruid`
- production_ready: `READY`
- import_ready: `NOT_READY_ASSETS_NOT_GENERATED`

### Role inventory

- ICON: current=true; decision=NEW_ART; field=icon_ruid; files=ICON/004_m_king_bloctopus_s_mon_king_bloctopus_ICON.png; target=icon_ruid
- CAST_VFX: current=true; decision=NEW_ART; field=layer_ruids; files=CAST/004_m_king_bloctopus_s_mon_king_bloctopus_CAST_F00.png..._CAST_F07.png; target=layer_ruids
- PROJECTILE: current=true; decision=NEW_ART; field=projectile_ruid; files=PROJECTILE/004_m_king_bloctopus_s_mon_king_bloctopus_PROJECTILE_F00.png..._PROJECTILE_F03.png; target=projectile_ruid
- HIT_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
- PERSISTENT_BUFF_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none
- REFERENCE_VFX: current=false; decision=NO_RUNTIME_ROLE; field=none; files=none; target=none

### Shared constraints

- PROJECTILE 제작 계약: 4×0.08=0.32초 non-loop로 0.35초 수명 안에 완주한다. targeting_range와 현재 착탄 피해 반경 0.8wu를 구분하며 게임 수치는 변경하지 않는다.

- CAST와 PROJECTILE은 독립 파일 세트다. 같은 VFX 한 세트로 합치지 않는다.
- PROJECTILE은 4×0.08=0.32초 non-loop로 0.35초 수명 안에 완주하며 엔진 이동·ZRotation을 이미지 안에서 중복하지 않는다.
- 전용 HIT/PERSISTENT 시각 호출이 없으므로 해당 파일을 만들지 않는다.
- 복수 CAST 레이어 통합은 기존 delay/offset/drift의 상대 리듬을 한 로컬 캔버스 clip에 베이크한다. 원본 레이어 정보는 ASSET_BINDING_PLAN에 남긴다.
- targeting_range와 impact_radius는 별개이며 이미지로 조준 거리 전체를 피해 범위처럼 표현하지 않는다.
- PREVIEW/labeled_preview.png와 Area overview는 필수 검수물이고 별도 contact sheet만 선택이다.
