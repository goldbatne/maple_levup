# Maple Levup — 몬스터 테이밍 수집형 액션 RPG 설계서 (GDD)

> 🔖 **AI note — resuming?** 새 세션에서 이어갈 때 `msw-planning`을 먼저 로드하고 `maple-levup-Roadmap.md`와 `Archive/As-built.md`를 읽어 상태를 재구성한다. 체크리스트 상태를 바꾸기 전 `references/build-management.md`를 전부 읽는다.
> Last updated: 2026-09-17 / Stage: M2A taming collection + visual companion prototype

## 1. One-line concept

> 몬스터를 테이밍하고 성장시켜 그 몬스터의 능력을 플레이어가 직접 사용하며, 수집한 능력으로 강력한 보스를 공략하는 RectTile 탑다운 수집형 액션 RPG.

## 2. Key decisions (immutable baseline)

| Item | Decision | Notes |
|---|---|---|
| Camera/map mode | RectTile(1) + KinematicbodyComponent | 기존 160개 맵 구조 유지 |
| Player | 기존 DefaultPlayer 기반 | 기존 전투/VFX/수집 컴포넌트 재사용 |
| Player count | 기존 공유 멀티 구조 유지 | M1은 솔로 전투 루프 검증 우선 |
| Feature rollout | `phase1_random_combat_enabled` 데이터 플래그 | 0이면 기존 고정 슬롯/광역 평타/접촉 공격 범위로 비교 |
| TamedMonsters | 신규 모드의 수집·해금·★성장 단일 원장 | monster_id → 1～5; 101종, 패시브 35종 포함 |
| OwnedSkills | 구세이브/레거시 코드 호환 미러 | TamedMonsters 변경 뒤 단방향 동기화; 신규 로직의 독립 원장으로 사용 금지 |
| Combat inventory | 서버 권한 5슬롯 일회성 재고 | 보유 종수와 무관하게 같은 규칙, 중복 허용 |
| Initial inventory | 신규 모드 시작 시 0칸 | `InitialRandomSkillCount`나 즉시 5칸 지급 없음 |
| Supply | 보유 액티브가 있고 빈칸이면 5초마다 정확히 하나 공급 | 가득 차면 타이머 정지, 성공 소비 시점부터 5초 재시작 |
| Acquisition | 새 몬스터 테이밍은 컬렉션과 대응 액티브 풀을 확장 | 기존 전투 재고 유지, 즉시 삽입·재추첨 없음 |
| Cooldown | 신규 모드에서는 검사·시작하지 않음 | 같은 skill_id 재고도 독립 사용; 플래그 OFF 레거시만 기존 쿨다운 사용 |
| Basic attack | 가장 가까운 살아 있는 몬스터 1종 | 스킬 광역 판정은 유지 |
| Monster range | 인지와 공격 거리 분리 | 기본 공격 반경 = 플레이어 평타 반경 × 데이터 비율; 모델별 override 가능 |
| Hit reaction | 일반 피해는 행동 중단 없음 | 명시적 스턴/넉백은 향후 별도 효과 |
| SkillTag | 실제 SkillTable 필드에서 복수 태그 유도 | 스킬 ID 하드코딩 없음; 실제 포획 액티브 66종 기준 |
| Trait | 신규 랜덤 전투에서 사용하지 않음 | TraitTable·selected_trait·구현은 레거시 보존, Weight·효과 모두 1.0 |
| Taming | 첫 테이밍 10% / 중복 3% 순수 확률 | 신규 모드 천장 없음, ★5 상한, 패시브도 수집·동행 가능 |
| Companion | 테이밍한 몬스터 1종의 비전투 시각 동행 | 공격·HP·피격·충돌·타겟 AI·효과·Weight 보정 없음 |

## 3. Core loop (one session)

필드 탐험 → 몬스터 처치·테이밍 → 몬스터 컬렉션과 대응 능력 해금 → 중복 테이밍으로 ★ 성장 → 테이밍한 모든 액티브 몬스터의 능력을 5칸 일회성 재고로 공급 → 장비와 수집 능력으로 지역 보스 공략

## 4. Core systems

- 기본 공격: 서버가 현재 방의 살아 있는 몬스터 중 사거리 내 최단거리 한 종만 지정한다.
- 수집 원장: `PlayerCollection.TamedMonsters[monster_id]`만 해금·★단계·강화 배율의 근거로 사용한다.
- 보유 풀: 테이밍한 101종 중 `skill_kind!=passive`인 66종의 `drop_skill_id`만 사용하며 동행 선택과 ★수는 Weight에 영향을 주지 않는다.
- 신규 모드: 보유 액티브가 1종뿐이어도 서버 동기화 5칸 일회성 재고를 사용한다.
- 소비: 공격·방어·투사체·돌진 실행이 성공한 경우에만 현재 슬롯을 비운다.
- 공급: 서버 one-shot 타이머가 5초마다 빈 슬롯 중 앞쪽 한 칸에 무작위 스킬 하나를 넣고, 빈칸이 남을 때만 다음 타이머를 예약한다.
- 중복: 추첨마다 전체 보유 풀을 다시 사용하므로 동일 스킬이 여러 칸에 들어갈 수 있다.
- 쿨다운: 신규 모드에서는 `SkillReadyAt`을 검사·갱신하지 않는다. 레거시 기능 플래그 OFF 경로에는 기존 코드를 보존한다.
- UI: SkillBar는 빈칸을 포함한 5칸 전투 재고이고, 기존 101칸 UI는 몬스터 이미지·잠금·★·고유 능력·배율·처치·동행 선택을 보여 준다.
- 동행: 별도 `CompanionVisual.model`은 Transform+SpriteRenderer만 가지며 서버가 선택·맵당 단일 생성을 관리하고 10Hz로 플레이어 뒤를 따라온다.

## 5. System ↔ MSW mapping

| Game system | MSW implementation |
|---|---|
| 기본 공격 | `PlayerAttack` AttackComponent, 서버 판정 |
| 영구 몬스터 컬렉션 | `PlayerCollection.TamedMonsters` TargetUserSync + schema v5 저장 |
| 레거시 스킬 미러 | `PlayerCollection.OwnedSkills`, TamedMonsters에서 단방향 동기화 |
| 비전투 동행 | `CompanionVisual.model` + `PlayerCollection` 서버 선택/Follow |
| 실시간 랜덤 핸드 | `PlayerSkillSlots.RandomSlots` TargetUserSync, 서버 타이머 |
| 스킬 실행 | 기존 `PlayerAttack.UseSkill` 및 `_SkillEffect` 분기 |
| 몬스터 추적 | `AIChaseComponent.DetectionRange` |
| 몬스터 공격 | `MonsterAttack`의 별도 공격 Shape |
| UI | 기존 `ui/SkillBar.ui` + `UI/SkillBar.mlua`; UI 원본 구조 변경 없음 |
| 밸런스 | 기존 GameBalance UserDataSet/CSV |
| 검증 | 정적 검사 후 Maker refresh → build logs → play → runtime logs → stop |

## 6. Roadmap (Phases)

### Phase 1 — 랜덤 핸드 전투가 실제로 작동한다

- ✅ Phase 1 설정값과 기능 플래그 데이터화
- ✅ 기본 공격 최단거리 단일 대상화
- ✅ 몬스터 인지/공격 거리 분리
- ✅ 보유 1종부터 랜덤 5슬롯·중복·성공 소비·5초 공급
- ✅ 신규 모드 개별 쿨다운 우회, 레거시 쿨다운·기존 실행·VFX 보존
- ✅ 일반 피격 무경직 정적/런타임 확인
- ✅ SkillBar 랜덤 빈 슬롯 표시
- ✅ 정적 검증 및 Maker 빌드·런타임 검증

### Phase 2 — 수집 풀이 커져도 특성으로 랜덤을 조금 기울인다

- ✅ 실제 포획 가능한 액티브 66종과 레거시 `s_mon_snail` 경계 확정
- ✅ Single / Area / Projectile / Rush / Defense 복수 태그 유도
- ✅ 균형 / 광역 / 투사체 / 전선 특성 데이터와 별도 UI
- ✅ 선호 Weight 1.4, 선호 효과 1.10, 비선호 Weight·효과 유지
- ✅ 특성 영구 저장과 구세이브 Balance 이관
- ✅ 4특성 10,000회 통계 및 5/10/20/35종 Maker 공급 검증

### Phase 3 — 레벨·장비·수집 중심으로 RPG 구조를 단순화한다

- ✅ Lv1~200 자동 HP/공격/방어 성장표와 최종 장비 보너스 연결
- ✅ 전직·티어·환생·직접 4스탯 투자를 신규 플레이에서 비활성화
- ✅ 사망·부활·귀환을 환생에서 `PlayerTravel`로 분리
- ✅ 포획·드랍의 LUK 의존 제거와 데이터 배율 구조
- ✅ 패시브 포획 35종과 전직 패시브 장비의 신규 모드 효과 비활성화
- ✅ 모든 일반 지역 자유 입장과 권장 레벨·주요 몬스터 표시
- ✅ 저장 스키마 3/2 마이그레이션과 레거시 필드 무손실 왕복
- ✅ Maker에서 고레벨 지역 난이도, 사망 귀환, Phase 1/2 회귀 검증

### Phase 3.5 — 첫 체험을 앞당기고 Trait를 신규 전투에서 걷어낸다

- 🔄 Trait UI 전체 숨김, 추첨 Weight 1.0, 효과 배율 1.0
- 🔄 첫 획득 10%·20킬 천장 / 중복 3%·40킬 천장
- 🔄 중복 강화 ×1.0～×1.8 유지, 보유 장수와 추첨 확률 분리
- 🔄 패시브 35종 신규 포획·알림 제외, 기존 저장·아이콘·행 보존

### Phase 3.6 — 천장을 제거하고 실제 첫 포획 경로를 확정한다

- ✅ 첫 획득 10% / 중복 3%의 순수 확률 판정
- ✅ `SpeciesKills`는 레거시 실패 카운터로 보존하고 `TotalMonsterKills`를 신규 누적 통계로 분리
- ✅ 컬렉션 배율 Hook·몬스터 배율·최종 확률 상한을 데이터 공식으로 연결
- ✅ 실제 10% 자연 포획 → 알림 → 랜덤 풀 → 5초 공급 → 저장/재접속 검증

### Phase 4 — 대표 사냥터 한 곳에서 전투 밀도를 검증한다

- ✅ `map003` 원본 보존 + `map003_p4b` 22×13 비교 맵 생성
- ✅ 타일 면적 63.8% 유지, 목표 스폰 5마리 유지, 포탈·스폰 범위 재배치
- ✅ fresh-session Maker A/B: 첫 피해 7.29→5.00초, 10킬 119.54→59.38초
- ✅ 인지 반경 체류 67.4→92.6%, 후보 포탈·경계·포획·사망 복귀 회귀 확인
- ✅ 완화안 `map003_p4c` 25×14(면적 78.1%) 추가, A/B/C 각 3회 반복 검증
- ✅ A/B/C 전투 비율 55.03% / 94.74% / 84.03%, 10킬 평균 85.08 / 26.20 / 37.88초
- ✅ `map003` 최종 추천은 C 완화안. B보다 느리지만 판단·포지셔닝 여유와 결과 안정성을 우선
- ✅ 통로형 `map077` 원본/78.1% 후보 비교로 단순 crop의 한계 확인
- ⏸ 전체 일괄 crop은 금지. 평지형은 C 원칙, 통로·절벽·해안은 유형별 수동 파일럿 뒤 확대

### M2A — 몬스터 테이밍 컬렉션과 비전투 동행을 검증한다

- ✅ `TamedMonsters[monster_id]`를 신규 모드 Single Source of Truth로 도입
- ✅ schema v5에서 현행 101개 명시적 매핑만 변환하고 `s_mon_snail`·히어로·보우마스터 제외
- ✅ 66 액티브는 전체 랜덤 풀, 35 패시브는 컬렉션·동행만 허용
- ✅ 기존 101칸 UI를 몬스터 컬렉션과 동행 선택 화면으로 재사용
- ✅ 주황버섯·빨간 달팽이·파란 달팽이를 포함한 전 101종 표시/동행 리소스 매핑
- ✅ 공격·HP·피격·충돌·AI·효과가 없는 시각 동행 모델과 맵 전환 단일 생성 구조
- ✅ 정적 계약 검증 (`maple-levup-M2A-verify.cjs`)
- ⏳ Maker 빌드·20항목 런타임 검증
- ⛔ M2B 동행 효과는 미구현

## 7. Data-driven

GameBalance에 기능 플래그, 슬롯 최대치, 공급 주기, 몬스터 공격 거리 비율, 첫/중복 테이밍률, 전역·컬렉션·몬스터 배율과 확률 상한, ★상한·단계 배율을 둔다. MonsterTable의 명시적 `monster_id → drop_skill_id`와 컬렉션/동행 RUID가 M2A 매핑 원장이다. 신규 모드는 천장을 쓰지 않으며 옛 천장 키는 레거시 모드 호환용으로만 남긴다. TraitTable은 레거시 자료로 보존하지만 신규 랜덤 전투 계산에는 쓰지 않는다. Lv1~200 기본 HP/공격/방어는 LevelGrowthTable에 둔다.

## 8. Decisions (this milestone)

| Item | Status |
|---|---|
| 신규 모드 초기 재고 | Decided: 0칸에서 시작해 5초마다 1개 공급 |
| 랜덤 슬롯 중복 | Decided: 기본 허용 |
| 랜덤 모드 쿨다운 | Decided: 검사·시작하지 않음; 각 슬롯은 독립 1회권 |
| Phase 1 테스트 스킬 | Decided: 기존 액티브 중 공격·방어·투사체·돌진을 포함한 10～15종을 검증 시나리오로 사용; 런타임 풀 자체를 임의 제한하지 않음 |
| 신규 수집 단위 | Decided: skill_id가 아닌 monster_id; TamedMonsters가 유일한 원장 |
| 패시브 몬스터 | Decided: 테이밍·컬렉션·동행 가능, 액티브 풀·과거 패시브 효과에는 포함하지 않음 |
| M2A 동행 | Decided: 시각적 Follow만, 전투/보정 효과 없음 |

## 9. Plan changes

| When | Type | What changed | Reason | Impact |
|---|---|---|---|---|
| 2026-09-15 | Modify | `InitialRandomSkillCount=3` 제거, 1～5 직접 표시/6+ 즉시 5칸 규칙 확정 | 사용자의 확정 기획 반영 | 랜덤 핸드 초기화·UI·검증 시나리오 변경 |
| 2026-09-15 | Modify | 보유 종수 전환을 폐기하고 1종부터 5초 공급되는 일회성 재고로 통일; 신규 모드 쿨다운 제거 | 장착 슬롯이 아닌 독립 사용권이라는 사용자 정정 | 공급 타이머·소비·컬렉션 UI·쿨다운 분기 변경 |
| 2026-09-16 | Add | 실제 포획 액티브 66종을 기존 필드로 태그화하고 4개 특성의 1.4 Weight / 1.10 Effect 적용 | 수집량 증가 시 원하는 방향으로 랜덤을 약하게 기울이는 Phase 2 검증 | 공급 선택·피해/방어 효과·UI·영구 세이브 확장 |
| 2026-09-16 | Modify | 레벨 자동 성장, 전직·환생·직접 스탯·지역 제한의 신규 모드 비활성화와 저장 마이그레이션 | 랜덤 스킬 판단에 불필요한 RPG 누적 구조 단순화 | `maple-levup-M1-Phase3.md`에 구현·공식·검증 기록 |
| 2026-09-16 | Modify | Trait 신규 모드 비활성, 첫 획득 10%·20킬 / 중복 3%·40킬, 패시브 신규 포획 제외 | 첫 스킬 체험을 앞당기고 보유 장수와 랜덤 슬롯 확률을 분리 | `maple-levup-M1-Phase3.5.md`에 계약·검증 기록 |
| 2026-09-16 | Modify | 신규 모드 천장 제거, 첫 10%·중복 3% 순수 확률과 독립 누적 처치 원장 도입 | 첫 포획 경로를 명확히 하고 과거 실패 카운터를 통계로 오해하지 않기 위함 | `maple-levup-M1-Phase3.6.md`에 구현·검증 기록 |
| 2026-09-16 | Add | `map003`을 보존하고 면적 63.8%의 `map003_p4b`로 전투 밀도 A/B 파일럿 | 전체 160맵을 건드리기 전에 이동 공백 감소가 실제 전투 시간을 줄이는지 확인 | `maple-levup-M1-Phase4.md`에 구조·측정·보류 조건 기록 |
| 2026-09-17 | Modify | `map003` 78.1% 완화안과 통로형 `map077` 후보를 추가해 압축 강도·유형별 위험 검증 | 가장 빠른 안보다 전투 여유·랜덤 판단·지역 구조를 함께 보존 | `maple-levup-M1-Phase4.md` Phase 4.1에 9회 본 시험과 2차 지형 결과 기록 |
| 2026-09-17 | Modify | 신규 모드 수집 원장을 `TamedMonsters`로 전환하고 101종 몬스터 컬렉션·비전투 동행 M2A 도입 | 스킬 획득보다 몬스터 테이밍·성장이라는 수집 판타지를 전면에 두기 위함 | schema v5, 단방향 OwnedSkills 미러, 컬렉션 UI, CompanionVisual, 랜덤 풀/강화 조회 변경 |

## 10. Maker runtime verification — 2026-09-15

- 보유 A 1종: 빈 재고에서 실제 5초 간격으로 `0→1→2→3→4→5`, 25초 뒤 `A/A/A/A/A` 확인.
- 동일 A 5연속: 기존 `SkillReadyAt`에 미래 시각을 넣어도 신규 모드에서 5회 모두 성공하고 매번 선택한 슬롯 하나만 소비됨.
- 보유 A/B 2종: 25초 결과 `B/A/A/A/A`; 복원 추출과 중복 허용 확인.
- 풀 확장: `A/A/A` 재고에서 B를 획득해도 기존 세 칸은 보존되고, 다음 공급에서 B가 추첨됨.
- 재충전: 만석에서 한 칸 소비 직후에는 비어 있고 4.7초에도 유지, 5.4초 시점에 정확히 한 칸만 공급됨.
- 보유 스킬 UI: 제목 `보유 스킬`, 구분 `자동 추첨 풀`, 레거시 장착 버튼 5개 비표시. 서버 직접 장착 요청도 거부됨.
- 기능 플래그 OFF: 레거시 `MonsterSlots`와 동일 skill_id 쿨다운 차단/해제 후 성공 경로가 모두 복귀함.
- Maker 빌드: 오류 0, 기존 모델 경고 2건(`mano`, `bowmaster`)만 존재. 신규 기능 런타임 오류 0.
- 테스트 후 EXP와 포획 진행도를 검증 전 값으로 복원해 DataStorage 저장 완료.
