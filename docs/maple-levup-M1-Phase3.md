# Maple Levup — Phase 3 RPG 구조 단순화 결과

> 날짜: 2026-09-16  
> 상태: 구현 완료, Maker Play 검증 완료  
> 범위: 자동 레벨 성장·레거시 RPG 비활성화·자유 지역 진입·저장 마이그레이션

## 이번 Phase에서 구현한 내용

- Lv1~200 `LevelGrowthTable`을 추가하고 HP/물리·마법 공격력/방어력을 레벨에서 자동 계산한다.
- 신규 성장 모드에서는 직접 STR/DEX/INT/LUK 분배, 환생, 티어 제한, 전직 진행, 지역·방 게이트를 사용하지 않는다.
- 기존 레거시 필드와 콘텐츠 자산은 삭제하지 않았다. 기능 플래그 OFF 경로와 이전 저장을 위해 보존한다.
- 사망·시작 마을 귀환 책임을 `PlayerTravel`로 분리했다.
- 장비는 투자 스탯을 거치지 않고 최종 ATK/MATK/DEF에 더한다. 기존 포인트 상당 환산 계수는 유지해 장비 전투력이 급락하지 않게 했다.
- 포획률과 드랍률에서 LUK를 제거하고 전역 배율·몬스터별 보정 확장 지점을 데이터화했다.
- 포획 패시브 35종과 히어로/보우마스터 패시브 장비의 스탯 효과를 신규 모드에서 0으로 만들되 보유 기록·아이콘·데이터는 보존했다.
- 모든 일반 지역을 처음부터 열고 기존 지역 선택 UI에 권장 레벨 범위와 주요 몬스터를 표시한다.
- 영구/런 저장 스키마를 각각 3/2로 올리고 기존 진행 데이터와 레거시 필드를 함께 왕복 저장한다.

## 변경한 데이터

### LevelGrowthTable

| Level | BaseMaxHP | BaseAttack / BaseMagicAttack | BaseDefense |
|---:|---:|---:|---:|
| 1 | 1,000 | 80 | 200 |
| 10 | 1,900 | 251 | 272 |
| 30 | 3,900 | 631 | 432 |
| 50 | 5,900 | 1,011 | 592 |
| 100 | 10,900 | 1,961 | 992 |
| 150 | 15,900 | 2,911 | 1,392 |
| 200 | 20,900 | 3,861 | 1,792 |

초안 곡선은 `HP = 1000 + 100 × (Lv-1)`, `Attack = 80 + 19 × (Lv-1)`, `Defense = 200 + 8 × (Lv-1)`을 200행으로 풀어 쓴 것이다. 실제 계산은 공식 하드코딩이 아니라 표의 행을 읽는다.

### GameBalance

- `phase3_simplified_growth_enabled = 1`
- `capture_rate_global_multiplier = 1`
- `capture_monster_modifier_default = 1`
- `drop_rate_global_multiplier = 1`

포획 기본 3%와 40회 천장은 아직 최종 밸런스로 확정한 값이 아니다. 기존 체감을 유지하는 호환 기본값으로만 남겼다.

## 기존 포획·드랍 공식과 신규 후보

### 기존 포획

`capture_base_rate + TotalLUK × capture_luk_bonus`, 실패 40회째 천장. 현재 데이터는 기본 0.03, LUK당 0.001이다.

### 신규 포획 후보

`capture_base_rate × capture_rate_global_multiplier × monster.capture_modifier`, 실패 천장은 기존 값을 유지한다. 현재 MonsterTable에는 전용 컬럼이 없으므로 기본 modifier 1만 적용한다. 몬스터별 수치를 승인하기 전까지 임의 값은 넣지 않았다.

### 기존 드랍

`item.drop_rate × (1 + TotalLUK × 0.005)`.

### 신규 드랍

`item.drop_rate × drop_rate_global_multiplier`. 기본 배율 1이므로 LUK 0 계정의 기존 실질 확률과 같다. 과거 LUK N 계정은 기존 대비 상대적으로 `N × 0.5%` 보정이 사라진다.

## STR/DEX/INT/LUK 의존 장비 점검

- 전직 패시브: `i_hero_sword`(STR +10), `i_bowmaster_bow`(DEX +10). 신규 모드에서는 효과 0, 데이터·보유 기록 유지.
- LUK 전용 장비: `i_amulet_luck`, `i_maple_sword`, `i_work_glove`, `i_red_ribbon`, `i_star_blue_moon`, `i_dark_wyvern_flying_cape`, `i_chief_gray_strange_glasses`. LUK가 제거되어 신규 직접 효과를 임의 배정하지 않았고 현재 전투 보너스는 0이다.
- 올스탯 장비: `i_ring_all`, `i_mano_helm`, `i_stumpy_sapling`, `i_faust_tail`, `i_shade_charm`, `i_balrog_soul`, `i_eliza_cloud_cape`, `i_hector_warm_cape`, `i_bubble_goggles`, `i_robo_blue_watch`, `i_deo_silent_legend`, `i_roid_zenumist_cape`, `i_tae_blue_panda_glove`, `i_harp_music_earrings`, `i_mateon_alien_earrings`, `i_official_d_guard_cape`, `i_cygnus_dress`. 기존 ATK/MATK/DEF 환산은 유지하고 제거된 LUK 부분만 적용하지 않는다.

## 저장 마이그레이션

- 유지: Level, EXP, OwnedSkills, Inventory, EquippedItems, BossRoomsCleared, selected_trait.
- 레거시 보존·신규 계산 제외: StatStr/Dex/Int/Luk, UnspentPoints, RebirthCount, BestRebirthLevel, BestTier, MonsterSlots.
- `UnlockedAreas`는 저장하되 신규 지역 접근 판정에서는 사용하지 않는다.
- 기존 저장 로드 → 신규 스키마 저장 → 재접속 후 수집·장비·특성·레벨/EXP와 레거시 필드가 유지되는 것을 Maker에서 확인했다.

## Maker Play 검증 결과

- 신규/기존 저장 로드, 자동 성장표 200행 및 7개 기준 레벨 검증 통과.
- Lv21 기존 계정의 과거 STR 61·미분배 279가 저장에는 남고 신규 전투 계산에서는 제외됨을 확인했다.
- 직접 스탯 투자 요청은 거부되고 값이 변하지 않았다.
- 장비 3종의 보너스가 자동 기본 능력치 위에 적용되었다.
- 랜덤 SkillBar는 5초 공급, 성공 사용 시 해당 슬롯만 소비, 다음 공급 때 재충전되는 Phase 1 동작을 유지했다.
- 선택 특성 `balance` 저장 유지, 다른 특성의 Weight 1.4 / Effect 1.10 데이터가 변하지 않았다.
- Area 20에 Lv21로 자유 입장했고 변형된 다크 스텀프가 실제 스폰됐다. 플레이어 ATK보다 DEF가 높고 적 공격 2회에 사망해 권장 난이도만 유지되는 것을 확인했다.
- 사망 시 `PlayerTravel`로 시작 마을에 정상 부활·귀환했다.
- 지역 20/20과 방 게이트가 모두 통과되고 지역 선택 UI에 권장 레벨·주요 몬스터가 표시됐다.
- 환생 판정 false, 전직 NPC는 신규 모드에서 진행 창을 열지 않는 경로로 분기한다.
- 기존 모델 경고 2건(`mano` InputSpeed, `bowmaster` AvatarAttackPlayRate)은 Phase 3 이전 경고다.

## 아직 남은 충돌·결정

- LUK 전용 장비 7종에 어떤 직접 전투 수치를 줄지는 별도 기획 결정이 필요하다.
- 포획 기본 확률과 천장 수치는 데이터화만 완료했으며 최종 밸런스는 미확정이다.
- UI 원본에는 레거시 컨트롤이 남아 있고 신규 모드에서 런타임으로 숨긴다. 기능 플래그 OFF 호환을 위해 삭제하지 않았다.
- `Mislocated` 아래의 기존 중복 EntryKey 파일은 사용자 자산이라 이번 Phase에서 삭제하지 않았다. 현재 RootDesk의 Phase 3 데이터셋은 정상 위치로 복구했다.
- 맵 축소·탑·레이드는 범위 밖이며 Phase 4 이후에 진행한다.

## Phase 4 진행 판단

자동 성장, 자유 입장, 저장 왕복, 사망 귀환과 Phase 1/2 회귀가 동작하므로 대표 사냥터 한 곳을 대상으로 한 맵 축소 검증으로 넘어갈 수 있다. 단, LUK 전용 장비 재배정과 포획 최종 수치는 Phase 4를 막는 선행 조건은 아니며 별도 밸런스 결정으로 남긴다.
