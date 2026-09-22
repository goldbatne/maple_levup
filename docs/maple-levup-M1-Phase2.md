# Maple Levup — Phase 2 특성 가중 랜덤 프로토타입

> Parent: `maple-levup-M1-GDD.md` · 검증일: 2026-09-16  
> 범위: 실제 포획 가능한 액티브 66종의 태그·가중 추첨·약한 효과 보정. Phase 1 규칙과 기존 RPG 구조는 유지한다.

## Status

- ✅ 실제 포획 경로가 있는 액티브 66종을 랜덤 풀의 단일 원장으로 사용
- ✅ 기존 필드 기반 복수 `SkillTag` 분류
- ✅ 균형 / 광역 / 투사체 / 전선 특화 4종
- ✅ 기본 1.0, 선호 1.4 가중치와 복수 태그 1회 적용
- ✅ 선호 스킬 피해·방어 효과 1.10배
- ✅ 별도 특성 UI와 마을 전용 변경
- ✅ 선택 특성 영구 저장·구세이브 Balance 이관
- ✅ 4특성 × 10,000회 Maker 서버 RNG 검증
- ✅ 보유 풀 5 / 10 / 20 / 35종 런타임 공급 검증

## 확정 데이터 경계

- `SkillTable`의 몬스터 액티브 정의는 67종이다.
- `MonsterTable.drop_skill_id`로 실제 포획 가능한 액티브는 66종이다.
- 차이 1종인 `s_mon_snail`(몸통 박치기)은 현행 몬스터 드랍 경로가 없는 레거시 정의다. 삭제하지 않되 Phase 2 풀·태그 통계·특성 보너스에서 제외한다.
- 패시브 35종은 `OwnedSkills`와 기존 자동 스탯 보너스를 유지하지만 전투 재고·가중치·특성 효과에서는 제외한다.

## SkillTag 유도 규칙

별도의 스킬 ID 목록을 만들지 않고 기존 `SkillTable` 필드에서 유도한다.

| 기존 필드 | 태그 |
|---|---|
| `skill_kind=defense` | Defense; `effect_type=heal`이면 Heal도 추가 |
| `dash_distance>0` | Rush |
| `projectile_ruid`가 비어 있지 않음 | Projectile |
| `target_mode=area` | Area |
| 그 외 공격 | Single |
| `skill_kind=passive` | 전투 태그 없음 |

현재 66종 태그 개수는 Area 44, Single 19, Projectile 12, Rush 7, Defense 3이다. Heal / AttackBuff / DefenseBuff / Utility는 현재 확정 액티브 동작에 해당 항목이 없어 0종이다. 자동 분류가 애매한 스킬은 없으며, 태그는 실제 필드가 바뀌면 함께 바뀐다.

## 실제 포획 액티브 66종 분류

| Lv | skill_id | 태그 | Lv | skill_id | 태그 |
|---:|---|---|---:|---|---|
| 1 | s_mon_snail_dew_trail | Area | 3 | s_mon_blue_snail | Defense |
| 5 | s_mon_red_snail | Rush + Single | 5 | s_mon_mushroom | Area |
| 10 | s_mon_mano | Area | 10 | s_mon_mushmom | Area |
| 10 | s_mon_stone | Defense | 11 | s_mon_slime | Single |
| 13 | s_mon_dark_stump | Defense | 18 | s_mon_axe_stump | Area |
| 18 | s_mon_fairy | Area | 20 | s_mon_faust | Projectile + Area |
| 22 | s_mon_dark_axe | Area | 26 | s_mon_wild_boar | Rush + Single |
| 30 | s_mon_skeleton_commander | Area | 31 | s_mon_octopus | Area |
| 32 | s_mon_fire_boar | Area | 35 | s_mon_jr_wraith | Area |
| 40 | s_mon_shade | Area | 41 | s_mon_ribbon_pig | Rush + Single |
| 42 | s_mon_stumpy | Projectile + Area | 45 | s_mon_starfish | Area |
| 60 | s_mon_king_clang | Area | 65 | s_mon_drake | Area |
| 68 | s_mon_wild_kargo | Rush + Single | 70 | s_mon_tauromacis | Area |
| 70 | s_mon_jr_balrog | Area | 71 | s_mon_star_pixie | Projectile + Single |
| 75 | s_mon_lunar_pixie | Projectile + Single | 80 | s_mon_eliza | Area |
| 85 | s_mon_hector | Rush + Single | 88 | s_mon_white_fang | Area |
| 90 | s_mon_snow_witch | Area | 95 | s_mon_squid | Area |
| 98 | s_mon_shark | Projectile + Single | 100 | s_mon_pianus | Area |
| 103 | s_mon_drumming_bunny | Area | 108 | s_mon_king_bloctopus | Projectile + Single |
| 110 | s_mon_rombot | Area | 113 | s_mon_toy_trojan | Rush + Single |
| 118 | s_mon_chronos | Single | 120 | s_mon_timer | Area |
| 121 | s_mon_white_sand_rabbit | Single | 125 | s_mon_meercat | Area |
| 130 | s_mon_deo | Area | 135 | s_mon_homun | Area |
| 138 | s_mon_roid | Projectile + Single | 140 | s_mon_chimera | Projectile + Area |
| 143 | s_mon_wooden_dummy | Area | 145 | s_mon_peach_monkey | Projectile + Single |
| 150 | s_mon_tae_roon | Projectile + Area | 153 | s_mon_blood_harp | Area |
| 155 | s_mon_blue_wyvern | Single | 160 | s_mon_manon | Area |
| 163 | s_mon_memory_monk_trainee | Single | 168 | s_mon_chief_memory_guardian | Area |
| 170 | s_mon_dodo | Projectile + Area | 171 | s_mon_mateon | Projectile + Single |
| 175 | s_mon_mecateon | Area | 180 | s_mon_zeno | Area |
| 181 | s_mon_official_knight_c | Area | 188 | s_mon_advanced_knight_b | Area |
| 190 | s_mon_cygnus | Area | 193 | s_mon_mutant_iron_hog | Rush + Single |
| 198 | s_mon_ancient_dark_golem | Area | 200 | s_mon_mutant_stumpy | Area |

## 특성 원장과 계산

`TraitTable`이 이름, 선호 태그, 등장 배율, 효과 배율, 표시 순서를 가진다.

| id | 표시명 | 선호 태그 | Weight | Effect |
|---|---|---|---:|---:|
| balance | 균형 | 없음 | 1.0 | 1.0 |
| area | 광역 특화 | Area | 1.4 | 1.1 |
| projectile | 투사체 특화 | Projectile | 1.4 | 1.1 |
| frontline | 전선 특화 | Single / Rush / Defense | 1.4 | 1.1 |

초안의 `지원 특화`는 현재 지원 태그가 Defense 3종뿐이고 Heal/Buff/Utility가 0종이라 표본이 지나치게 작다. 특성 수를 늘리지 않고 29개 태그 슬롯을 포괄하는 `전선 특화`로 교체했다. 복수 태그가 여러 선호 태그와 맞아도 1.4를 한 번만 적용한다.

가중치는 매 공급 시 보유한 실제 포획 액티브 전체에 대해 서버가 계산한다. 어떤 특성에서도 비선호 스킬은 Weight 1.0을 유지하므로 0%가 되지 않는다. 현재 손패는 특성 변경으로 재추첨하지 않으며 다음 공급부터 새 가중치를 쓴다.

효과 보너스는 기존 실행 경로에서 안전하게 공통 적용할 수 있는 피해 계수와 방어 스킬 `effect_value`에만 1.10배를 적용한다. 사거리·지속시간·투사체 비행·돌진 거리는 변경하지 않는다. 비선호 스킬은 정확히 기존 1.0배다.

## 패시브 35종 현행 효과

현재 패시브 행의 `passive_value`는 비어 있으며, 기존 컬렉션 규칙이 첫 보유 `+1`, 중복 1회당 `+0.25`를 해당 `passive_stat`에 더한다. 이번 Phase에서는 그대로 둔다.

| 스탯 | 수 | 몬스터(레벨) |
|---|---:|---|
| STR | 9 | 뿔버섯12, 카파 드레이크63, 주니어 샐리온73, 주니어 예티81, 모래 두더지128, 다크 와이번158, 기억의 수호병165, 플라티안173, 변형된 스텀프191 |
| DEX | 10 | 아이언 호그28, 파란 리본돼지43, 러스터 픽시78, 라츠101, 브라운테니111, 미스릴 뮤테133, 훈련용 짚인형141, 하프151, 정식기사D183, 변형된 아이언 보어193 |
| INT | 8 | 버블링15, 레이스33, 쿨 젤리피쉬48, 좀비버섯61, 버블피쉬91, 큐브슬라임131, 호문쿨루135, 기억의 수도승161 |
| LUK | 7 | 스티지33, 다크 주니어 예티83, 마스크피쉬93, 블록퍼스105, 목도리 플리드123, 푸른 꽃뱀148, 상급기사A185 |
| DEF | 1 | 변형된 스톤 마스크195 |

> 이름은 현행 MonsterTable 표기를 따르며, 패시브 스탯 지원 여부를 재설계하지 않았다.

## UI와 저장

- 기존 보유 스킬 UI와 별개인 `TraitWindow`를 추가했다.
- 현재 특성, 선호 태그, 등장 배율, 효과 배율, 설명과 네 선택 버튼만 표시한다.
- 서버는 시작 마을인지 다시 확인해 전투 필드 변경을 거부한다.
- 선택 변경 시 현재 5칸은 유지한다.
- 영구 세이브 schema 2에 `selected_trait`를 기록한다. 기존 schema에는 필드가 없으므로 `balance`로 읽는다.
- 실제 Maker에서 `projectile` 저장 → Play 재시작 → `projectile` 복원 → 테스트 종료 후 `balance` 재저장을 확인했다.

## Maker 통계 검증

대상은 실제 포획 액티브 66종, 서버 RNG 10,000회다.

| 특성 | 선호 추첨 수 | 관측 선호 비율 | 이론 선호 비율 | 개별 최소～최대 | 0회 스킬 |
|---|---:|---:|---:|---:|---:|
| 균형 | 해당 없음 | 해당 없음 | 해당 없음 | 118～181 | 0 |
| 광역 | 7,415 | 74.15% | 73.68% | 93～209 | 0 |
| 투사체 | 2,368 | 23.68% | 23.73% | 117～213 | 0 |
| 전선 | 4,059 | 40.59% | 41.18% | 105～214 | 0 |

비선호 스킬의 이론상 최소 개별 확률은 풀 66종 기준 광역 `1/83.6 = 1.196%`, 투사체 `1/70.8 = 1.412%`, 전선 `1/77.6 = 1.289%`다. Balance는 `1/66 = 1.515%`다.

## Maker 플레이·공급 검증

- 5종: 실제 저장 풀로 5초 공급, 중복 손패, UI 사용과 기존 VFX 실행을 확인했다(Phase 1 회귀 포함).
- 10종 / 균형: 25초에 5칸, `distinct=5`; 공급 간격과 복원 추출 유지.
- 20종 / 광역: 25초에 5칸, 표본 손패 중 광역 3칸. 비광역 2칸도 정상 유지.
- 35종 / 투사체: 25초에 5칸, 한 표본 손패에서 투사체 0칸과 동일 스킬 3중복이 발생. 특화는 보장이 아니라 약한 기울기이며 중복 규칙도 유지됨을 확인했다.
- 체감: 풀 20종부터 5칸의 예측성이 낮아지고, 35종은 같은 특화에서도 짧은 한 손패만으로 선호가 안 보일 수 있다. 1.4배는 장기적으로 분명하지만 순간 보장은 하지 않아 현재 목표와 일치한다.
- 5초 결합: 특성이 바뀌어도 공급 속도와 슬롯 소비 규칙은 변하지 않았다. 현재 손패 보존도 Maker 로그로 확인했다.

## 검증 결과와 남은 판단

- Maker 빌드 오류 0. 신규 런타임 오류 0.
- 특성 UI 열기와 `광역 특화` 실제 클릭·표시 갱신·저장을 확인했다.
- 선호 공격 효과 1.10, 비선호 1.00을 서버에서 확인했다.
- 가장 강해 보이는 특성: 광역. 66종 중 Area가 44종이라 기본 분포부터 넓고, 1.4배 적용 시 전체 손패의 약 74%를 차지한다.
- 가장 약해 보이는 특성: 투사체. 12종이라 특화 후에도 장기 선호 비율이 약 24%이며 한 손패에서 0개일 수 있다.
- 설계 문제: 현행 데이터에는 회복·버프·유틸 액티브가 없어 지원 플레이를 특성으로 검증할 수 없다. 또한 5초 고정 공급과 5칸만으로 풀 30종 이상에서 특정 스킬을 체감상 자주 보기는 어렵다.
- 판정: Phase 2의 구현·통계·Maker 런타임은 통과했다. Phase 3 진행은 가능하지만, `광역 44종` 쏠림과 지원 액티브 부재는 이후 데이터 재분류/콘텐츠 결정 항목으로 유지한다.
