# Maple Levup — Phase 1 detailed plan

> 🔖 **AI note — resuming?** 새 세션에서 이어갈 때 `msw-planning`을 먼저 로드하고 `Archive/As-built.md`, GDD, Roadmap을 읽어 상태를 재구성한다. 상태 변경 전 `references/build-management.md`를 전부 읽는다.
> Parent doc: `maple-levup-M1-GDD.md` · Goal: 기존 자산을 유지한 채 단일 평타와 서버 랜덤 스킬 핸드의 재미를 비교한다.
> **Skills**: `msw-general`, `msw-ui-system`, `msw-scripting`, `msw-combat-system`, `maplestory-skill-maker`.

## Status checklist

- ✅ 설정값·기능 플래그
- ✅ 최단거리 단일 기본 공격
- ✅ 몬스터 인지/공격 거리 분리
- ✅ 보유 1종부터 서버 랜덤 5슬롯 일회성 재고
- ✅ 성공 소비·소비 시점부터 5초 단일 공급·중복 허용
- ✅ 신규 모드 개별 쿨다운 우회·기존 실행/VFX 보존
- ✅ 보유 UI 장착 비활성화·SkillBar 역할 분리
- ✅ SkillBar 빈 랜덤 슬롯 표시
- ✅ 일반 피격 무경직 정적 확인
- ✅ 정적 검증
- ✅ Maker 빌드/런타임 검증

## Task detail

### 설정과 A/B 플래그
- **Goal**: 한 데이터 값으로 기존 전투와 Phase 1 전투를 비교한다.
- **Data**: GameBalance 숫자 키. `InitialRandomSkillCount`는 금지한다.
- **Done**: 중복 키 없음, 각 값 로드 로그 확인.

### 기본 공격과 몬스터 거리
- **Goal**: 서버가 가장 가까운 한 몬스터만 평타로 타격하며, 몬스터는 넓게 인지하고 좁은 별도 공격 범위에서만 공격한다.
- **Done**: 겹친 두 몬스터 중 한 종만 피해; 인지 범위 안/공격 범위 밖에서는 추적만 수행; 모델별 AttackRange override 확인.

### 랜덤 스킬 전투 재고
- **Goal**: 보유 액티브 수와 무관하게 0칸에서 시작, 최대 5칸까지 5초마다 한 칸 공급, 성공 사용 시 정확한 한 칸 소비.
- **Authority**: 슬롯 생성·소비·공급은 서버만 수행하고 TargetUserSync로 소유자에게 전달한다.
- **Done**: A 1종 25초 5칸, A/B 복원 추출, 풀 확장 시 기존 재고 보존, 동일 A 5연속 사용, 소비 후 5초 재충전.

### UI와 회귀
- **Goal**: 기존 5버튼 UI와 VFX/아이콘을 재사용하고 랜덤 모드 빈칸을 명확히 표시한다.
- **Done**: 슬롯 번호와 키가 이동하지 않으며 direct/projectile/dash/defense가 기존처럼 실행된다.

### 대표 런타임 검증 스킬 15종

`s_mon_snail`, `s_mon_snail_dew_trail`, `s_mon_blue_snail`, `s_mon_red_snail`,
`s_mon_mano`, `s_mon_mushroom`, `s_mon_mushmom`, `s_mon_stone`,
`s_mon_axe_stump`, `s_mon_dark_axe_stump`, `s_mon_wild_boar`,
`s_mon_skeleton_commander`, `s_mon_fire_boar`, `s_mon_stumpy`, `s_mon_slime`.

직접 공격·방어·돌진·투사체를 모두 포함한다. 이는 검증 표본이며 런타임 보유 풀을 이 목록으로 제한하지 않는다.

## Static verification — 2026-09-15

- GameBalance의 Phase 1 키는 기능 플래그·슬롯 상한·공급 주기·공격거리 비율 4개이며 중복 키가 없어야 한다.
- 기존 Monster Skill 액티브 67행(attack 64, defense 3) 유지; SkillTable 변경 없음.
- 규칙/연결 정적 검사: 액티브 필터, 보유 종수 경계 제거, 서버 one-shot 공급,
  성공 소비 4분기, 신규 모드 쿨다운 우회, 최근접 필터, 포획/로드 훅,
  공격 거리 override/비율, 장착 UI 차단, 랜덤 빈 슬롯 UI.
- `git diff --check` 통과.
- `PlayerHit.OnHit`와 `RoomMonster.HandleHitEvent`에 일반 피해 기반 `ChangeState("HIT")`,
  이동 정지, 공격 정지 없음. 사망 시 `DEAD` 전이만 유지.
- Maker build/play/log 검증 완료: 빌드 오류 0, 신규 기능 런타임 오류 0.

## Runtime verification — 2026-09-15

- Case A: A 1종이 5초마다 하나씩 공급되어 25초에 `A/A/A/A/A`; 기존 쿨다운 표식을 강제로 남긴 상태에서도 5연속 사용 성공.
- Case B: A/B 2종으로 `B/A/A/A/A`가 생성되어 독립 추첨·중복 허용 확인.
- Case C: `A/A/A` 상태에서 B를 풀에 추가했을 때 기존 재고는 그대로이고 다음 공급부터 A/B 풀이 적용됨.
- Case D: `A/B/A/C/B`에서 첫 A를 쓰면 그 슬롯만 비었고, 남은 A를 즉시 연속 사용함.
- Case E: 만석에서 소비한 뒤 즉시 보충되지 않았고 4.7초에는 빈칸, 5.4초에는 정확히 한 칸만 보충됨.
- UI: `보유 스킬 / 자동 추첨 풀`로 표시되며 장착 버튼은 숨김. 신규 모드의 서버 장착 요청도 거부됨.
- 기능 플래그 OFF: 기존 MonsterSlots와 개별 쿨다운 차단·사용 경로 복귀 확인.
- 검증으로 변한 EXP/포획 진행도는 원래 값으로 복원한 뒤 저장 완료.

## Risks / cautions

- SyncTable의 빈 키는 배열 길이로 판단하지 않고 항상 1～5 인덱스로 순회한다.
- 소비는 실행 성공 뒤에만 수행한다. 만피 회복/잘못된 슬롯 실패는 소비하지 않는다.
- 신규 모드의 같은 skill_id 슬롯은 서로 쿨다운을 공유하지 않는다. 레거시 모드만 기존 쿨다운을 쓴다.
- 랜덤 핸드는 저장하지 않는다. 영구 원장은 기존 `OwnedSkills` 하나다.
- 기능 플래그 OFF에서 기존 MonsterSlots·티어·쿨다운 동작이 유지돼야 한다.
- 이후 규칙 변경 시 A～E 시나리오와 기능 플래그 OFF 회귀를 함께 다시 실행한다.
