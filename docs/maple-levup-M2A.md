# M2A — 몬스터 테이밍 컬렉션·비전투 동행 프로토타입

> 기준일: 2026-09-17  
> 범위: M2A만. M2B 동행 효과, 전체 맵 개편, 펫 전투 AI는 포함하지 않는다.

## 1. 확정 계약

- 신규 모드의 수집·해금·★성장 원장은 `TamedMonsters[monster_id]` 하나다.
- `OwnedSkills`는 저장·레거시 호출 호환용 미러이며 `SetTamedCount`에서만 단방향 동기화한다.
- 테이밍 확률은 첫 10%, 중복 3%, 천장 없음, ★5 상한이다.
- ★1～★5 액티브 배율은 ×1.0 / ×1.2 / ×1.4 / ×1.6 / ×1.8이다.
- 랜덤 SkillBar는 선택 동행과 무관하게 테이밍한 모든 액티브 몬스터를 종당 Weight 1로 사용한다.
- 패시브 35종도 테이밍·컬렉션·동행은 가능하지만 랜덤 풀과 과거 스탯 효과에는 들어가지 않는다.
- 동행은 시각적 Follow만 한다. 공격·HP·피격·충돌·타겟 AI·스킬 보정·Weight 보정이 없다.

## 2. 실제 데이터 구조

`SavePermanentData` schema v5:

```text
Perm.tamed_monsters: { [monster_id]: integer 1..5 }
Perm.selected_companion_monster_id: string | ""
Perm.owned_skills: { [skill_id]: integer }  # 호환 미러
```

런타임:

```text
PlayerCollection.TamedMonsters              TargetUserSync
PlayerCollection.SelectedCompanionMonsterId TargetUserSync
PlayerCollection.OwnedSkills                TargetUserSync, legacy mirror
```

`GetAbilityStackCount(skill_id)`는 현행 `monster_id ↔ drop_skill_id` 역매핑을 거쳐 `TamedMonsters`를 읽는다. 매핑이 없는 레거시 스킬만 `OwnedSkills`를 직접 읽는다.

## 3. schema v5 마이그레이션

- v1～v4 `owned_skills` 중 현행 MonsterTable의 명시적 일대일 관계가 있는 101종만 `SetTamedCount`로 변환한다.
- `s_mon_snail / 몸통 박치기`는 역매핑에 없으므로 자동 변환하지 않고 레거시 미러로만 보존한다.
- `m_adv_hero`, `m_adv_bowmaster`는 `drop_skill_id`가 없어 테이밍 대상이 아니다.
- 레벨·EXP·인벤토리·장착·보스 기록·처치 기록 등 기존 필드는 기존 직렬화 경로를 유지한다.
- v5 저장 시 `tamed_monsters`를 원장으로 쓰고 `owned_skills`에는 호환용 값을 함께 기록한다.

## 4. 몬스터·스킬 구성

| 구분 | 수 | M2A 처리 |
|---|---:|---|
| MonsterTable 전체 | 103 | 전투 자산 유지 |
| 테이밍 대상 | 101 | 컬렉션·★·동행 가능 |
| 액티브/방어 능력 보유 | 66 | 랜덤 SkillBar 풀 포함 |
| 패시브 스킬 행 연결 | 35 | 수집·동행만, 랜덤 풀/패시브 효과 제외 |
| 히어로/보우마스터 | 2 | 테이밍 제외 |

프로토타입 우선 확인 대상은 `m_mushroom`, `m_red_snail`, `m_blue_snail`이다. 구조 자체는 같은 101종 매핑을 사용한다.

## 5. 컬렉션 UI

기존 `ui/EquipWindow.ui`의 101칸을 재사용한다.

- 제목: 몬스터 컬렉션
- 셀: 실제 몬스터 모델에서 추출한 animationclip thumbnail, 이름, 잠금, ★1～★5
- 상세: 고유 액티브명·설명·배율·TotalMonsterKills
- 패시브 연결 몬스터: `사용 가능한 액티브 능력 없음`
- 기존 장착 버튼 영역 1칸: 선택 몬스터의 동행 선택/해제
- 신규 모드에서 나머지 장착 슬롯과 직접 장착 동작은 숨긴다.
- 기능 플래그 OFF 레거시 모드는 기존 스킬 장착 UI를 유지한다.

지역 보상 팝업도 신규 모드의 수집 단위에 맞춰 스킬 대신 테이밍 대상 몬스터와 첫/중복 확률을 표시한다.

## 6. 동행 구현

`RootDesk/MyDesk/Models/Companions/CompanionVisual.model`은 다음 두 컴포넌트만 가진다.

- `TransformComponent`
- `SpriteRendererComponent`

선택 요청은 서버가 테이밍 여부와 시각 RUID를 검증한다. 서버는 현재 맵 아래에 사용자별 이름으로 하나만 생성하고 0.1초 간격으로 플레이어 뒤를 보간 추적한다. 거리가 4 world units 이상 벌어지면 안전 위치 보정을 한다. 맵 이름 변경이나 엔티티 소멸을 감지하면 이전 동행을 제거하고 현재 맵에 하나만 다시 생성한다.

## 7. 변경 파일

- `RootDesk/MyDesk/GameData/GameData.mlua`
- `RootDesk/MyDesk/GameData/GameDataVerify.mlua`
- `RootDesk/MyDesk/GameData/MonsterTable.csv`
- `RootDesk/MyDesk/GameData/GameBalance.csv`
- `RootDesk/MyDesk/Progress/PlayerCollection.mlua`
- `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`
- `RootDesk/MyDesk/PlayerAttack.mlua`
- `RootDesk/MyDesk/Save/SavePermanentData.mlua`
- `RootDesk/MyDesk/Save/PlayerDBManager.mlua`
- `RootDesk/MyDesk/UI/EquipPanel.mlua`
- `RootDesk/MyDesk/UI/WorldMapPanel.mlua`
- `RootDesk/MyDesk/Models/Companions/CompanionVisual.model`
- `docs/maple-levup-M2A-verify.cjs`

## 8. 정적 검증

실행:

```text
node docs/maple-levup-M2A-verify.cjs
```

현재 결과:

```text
M2A STATIC VERIFY: PASS
monsters=103 tameable=101 active=66 passive=35
mappings=101 legacy_snail=excluded hero_bowmaster=excluded collection_cells=101
```

추가 확인:

- CompanionVisual 모델에 Body/Collider/Trigger/Attack/MonsterAI/Hit 컴포넌트 없음
- 101종 모두 컬렉션·동행 RUID 존재
- 주황버섯/빨간 달팽이/파란 달팽이 매핑 고정
- 플레이어 공격의 ★배율 조회가 `GetAbilityStackCount` 공통 경로 사용
- 랜덤 풀은 `GetTamedCount`를 사용하고 선택 동행/★수는 보지 않음

## 9. Maker 검증 상태

현재 세션에는 Maker의 refresh/play/log/screenshot 도구가 노출되지 않아 실제 빌드와 플레이 검증을 수행하지 못했다. 아래 항목은 정적 구현 완료와 별개로 모두 `NOT_RUN`이다.

1. 기존 OwnedSkills → TamedMonsters 마이그레이션
2. 자연 확률 10% 테이밍
3. 컬렉션 등록 및 ★1
4. 액티브 랜덤 풀과 5초 공급
5. 중복 테이밍 ★2와 ×1.2
6. 동행 선택·Follow·비전투성
7. 맵 이동 중복 생성/잔류 방지
8. 동행 변경·해제
9. 재접속 저장 복원
10. 패시브 몬스터 테이밍·동행 및 랜덤 풀 제외
11. 히어로/보우마스터 제외
12. 기존 랜덤 5슬롯과 구세이브 무손실

Maker MCP가 연결된 세션에서 refresh → build log → Play → 위 시나리오 → runtime log → stop 순으로 검증하기 전에는 M2B로 넘어가지 않는다.

## 10. 보존·비범위

- `map003_p4b`, `map003_p4c`, `map077_p4c`와 Phase 4.1 연구 결과는 변경하지 않는다.
- 동행 효과 3종, 펫 전투, HP, 피격, 충돌, 성장 경험치, 장비, 먹이, 진화는 구현하지 않았다.
- 신규 보스·탑·레이드·전체 맵 개편은 시작하지 않았다.
