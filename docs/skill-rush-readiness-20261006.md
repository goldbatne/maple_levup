# SKILL RUSH 설계 준비 현황 보고서

작성일: 2026-10-06 · 대상: `D:/maplestory_levup` 원본 작업 디렉터리

기준 커밋: `fbc85d4c5be1f424c8f64c9b586b8e635ad09962` (`codex/skill-refill-map-bgm-20261006`). 디스크의 현재 소스·CSV·UIBuilder 읽기 결과를 기준으로 작성했다. 기존 미커밋 UI 변경은 보존했으며, UI 설명은 HEAD만이 아니라 현재 작업 파일 기준이다.

판정: **CONFIRMED** = 코드/데이터에서 직접 확인, **INFERRED** = 설계 추론, **NOT_VERIFIED** = 실행 확인 필요, **BLOCKED** = 접근 불가. 이번 Maker 실행·멀티플레이·모바일·청감 검증은 모두 **NOT_RUN**이다. 따라서 CONFIRMED도 런타임 PASS를 뜻하지 않는다. 필요한 소스에는 접근할 수 있었으며 접근 차단으로 인한 BLOCKED 항목은 없다.

조사 범위는 Player Skill 획득→Pool→공급→사용→정리와 그에 직접 연결된 Upgrade/Mid Boss/HUD/연출 부분이다. 게임 전체 감사, 기존 시스템 재설계, 코드·데이터·UI 수정은 수행하지 않았다. MSW 지침에 따라 `.ui`는 UIBuilder의 읽기 API로만 확인했다.

## 1. 현재 Skill Run 구조 한눈에 보기

1. **CONFIRMED** — 실제 일반 Run 획득은 바닥 줍기가 아니라 처치 후 서버 자동 지급이다.
2. `RoomMonster.Dead` → `GameData.GrantRunKillRewards` → `SkillDropManager.TrySpawnFromKill`로 연결된다.
3. 유효한 몬스터 액티브 스킬을 아직 갖지 않은 근처 참가자가 있어야 획득 판정한다.
4. 첫 성공 지급은 Run 공통으로 보장되고, 이후 일반 처치는 10% 판정이다.
5. Party에서는 적격 미보유자 중 한 명에게 지급하며 모두에게 복제 지급하지 않는다.
6. 지급된 SkillID는 플레이어의 `OwnedSkillPool[skillId] = 1`에 등록된다.
7. Pool은 개인별 Run 메모리이며 영구 컬렉션/스킬 해금 기록과 다르다.
8. Run 시작 시 전투 슬롯 5개와 Pool은 비어 있다.
9. Pool 획득 뒤 5초마다 첫 빈칸 하나를 개인별 RNG로 채운다.
10. 복원 추출이므로 서로 다른 칸에 같은 SkillID가 들어올 수 있다.
11. 키보드·버튼 모두 `SkillBar.Use` → `PlayerAttack.RequestUseSkill`로 요청한다.
12. 서버의 `UseSkill`이 행동 가능 상태·슬롯·데이터·종류별 실행 성공을 확인한다.
13. 성공 분기들은 `ConsumeRandomSlot`로 모이며, 본 모험은 즉시 비우고 공급을 기다린다.
14. 튜토리얼만 사용한 칸을 즉시 다른 스킬로 교체한다.
15. 기본 자동공격은 별도 진입 경로이며 슬롯을 소비하지 않는다.
16. **INFERRED** — 본 모험의 성공한 슬롯 소비에 개인별 콤보 상태를 연결하면 Drop/Pool 재설계 없이 도입할 수 있다.

## 2. Skill 획득 구조

### 현재 정상 처치 경로 — CONFIRMED

| 단계 | 실제 함수 / 데이터 | 처리 |
|---|---|---|
| 처치 | `RoomMonster.Dead` | 튜토리얼은 연습 알림만 보낸다. Run은 일반/정예 보상 함수로 분기한다. |
| 참가자 수집 | `GameData.GrantRunKillRewards` | 같은 맵의 Run 참가자 중 처치 위치 반경 12 world units 내 플레이어를 모은다. 막타자만 대상으로 하지 않는다. |
| SkillID 결정 | `SkillDropManager.TrySpawnFromKill` | `MonsterTable.drop_skill_id` → `GameData.GetSkill`; `source=monster`, `slot_type=monster`, 비패시브 조건을 검사한다. |
| 적격자 검사 | `IsPlayerMissingSkill` + 호출부 맵 검사 | 유효 플레이어·Run 참가자·비이탈자·개인 Run 활성·해당 Skill 미보유·같은 맵을 확인한다. 이 함수들에 별도의 생존 검사나 실제 피해 기여량 검사는 없다. |
| 확률 | `firstSkillDropResolved` | 아직 성공 지급이 없으면 보장. 이후 `run_ability_acquire_rate=0.10`; 정예 처치 중에는 정예 확률과 비교해 큰 값을 사용한다. |
| 지급 대상 | `skill_drop:recipient` RNG | 미보유 적격자 목록에서 시작 인덱스를 뽑고, 지급 실패 시 그 목록의 다음 사람을 순회한다. 한 명 성공하면 종료한다. |
| Pool 반영 | `ClaimRunSkillDrop` → `OfferRunAbility` | 중복 재검사 후 `OwnedSkillPool[skillId]=1`. 빈칸이 있고 공급 타이머가 없으면 예약한다. |
| 알림·별도 기록 | `ShowRunAbilityToast`, `StageRogueliteDiscovery`, `UnlockPermanentSkill` | 획득 토스트는 해당 사용자에게만 보낸다. 발견/영구 해금 기록도 갱신하지만 그것이 다음 Run의 Pool을 채우지는 않는다. |

근거: [RoomMonster.Dead](D:/maplestory_levup/RootDesk/MyDesk/Combat/RoomMonster.mlua:437), [GrantRunKillRewards](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:4983), [TrySpawnFromKill](D:/maplestory_levup/RootDesk/MyDesk/Inventory/SkillDropManager.mlua:47), [OfferRunAbility](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:645).

첫 보장은 **개인별 첫 스킬 보장이 아니다**. `SkillDropManager.firstSkillDropResolved` 한 곳에서 관리하며 실제 지급 성공 뒤에만 true로 바뀐다. 모두 보유한 종이면 확률 추첨 전에 종료하므로 첫 보장을 소모하지 않는다. Solo에서는 그 한 명이 받고, Party에서는 공통 기회 한 번을 한 명이 받는다. 다른 적격 사용자로 넘기는 범위도 해당 처치의 근처 미보유자 목록이지, 다른 맵의 Party원 전체가 아니다. `GetActiveMissingParticipants`는 존재하지만 현재 자동 지급 호출 경로에서 사용되지 않는다.

중복은 Pool 개수 증가·성장·즉시 슬롯 공급으로 전환되지 않는다. 모두 보유했고 `eligiblePlayers`가 한 명이면 거절 안내를 사용자별 10초 간격으로 제한한다. `RunFirstEligibleResolved`라는 개인 필드는 남아 있지만 실제 공통 보장의 정본은 아니다.

### World Skill Drop — 남아 있는 별도 경로, CONFIRMED

`SpawnDrop`는 RunID·맵·SkillID·만료 시각·상태·serial을 가진 레코드를 만들고, `MaterializeRecord`가 `skilldrop` 모델을 맵 아래 생성한다. `SkillDrop`에는 서버 Interaction과 모바일 탭 RPC가 있으며 둘 다 `TryClaim`으로 모인다.

`TryClaim` 순서: 유효 Entity/AVAILABLE 레코드 및 인스턴스 일치 → 유효 사용자/활성 Run/참가자 → 같은 맵 → 거리(설정 없으면 1.25) → 개인 Run 활성/미보유 → 레코드와 드롭을 먼저 CLAIMED로 변경 → `ClaimRunSkillDrop` → 실패 시 AVAILABLE 복원, 성공 시 발견·영구 해금 기록 → REMOVED 및 제거.

현재 `SpawnDrop` 호출자는 확인한 소스에서 디버그 생성/검증 메서드뿐이다. 일반 처치의 `TrySpawnFromKill`은 이름과 달리 이를 호출하지 않는다. 따라서 “바닥 드롭을 먹는 단계가 매번 있다”는 전제로 Rush를 설계하면 현재 플레이 흐름과 어긋난다.

근거: [SpawnDrop / MaterializeRecord](D:/maplestory_levup/RootDesk/MyDesk/Inventory/SkillDropManager.mlua:122), [TryClaim](D:/maplestory_levup/RootDesk/MyDesk/Inventory/SkillDropManager.mlua:198), [SkillDrop 입력](D:/maplestory_levup/RootDesk/MyDesk/Inventory/SkillDrop.mlua:64). Mid Boss 연결은 10절에 정리했다.

## 3. OwnedSkillPool

| 항목 | 확인 결과 — CONFIRMED |
|---|---|
| 저장 위치 | 플레이어 Entity의 `PlayerSkillSlots` 컴포넌트, `@TargetUserSync SyncTable<string, integer>` |
| 키/값 | 정본 SkillID → 1. 현재 지급은 수량이 아니라 고유 ID 집합으로 취급한다. |
| 사용자 분리 | 플레이어마다 다른 컴포넌트/테이블. Party원끼리 Pool을 공유하지 않는다. |
| Run 시작 | `BeginRogueliteRun`에서 캡처 가능한 모든 액티브 ID의 값을 nil로 정리한다. |
| 일반 맵 이동 | Pool을 지우지 않는다. `OnMapLeave`는 미처리 선택 후보만 정리한다. 같은 Run 재등록도 `RogueliteRunActive`면 유지한다. |
| Run 종료 | `EndRogueliteRun`에서 Pool·슬롯·타이머·일시 전투 상태를 정리한다. 실제 호출 시점은 13절 참조. |
| 중복/순서 | 동일 키 중복 저장 불가. 획득 순서는 보존하지 않고 `GetRunOwnedSkillIds`가 ID 사전순으로 돌려준다. |
| 최대 보유 수 | 별도의 N종 보유 제한은 없다. 정상 공급 후보는 데이터의 캡처 가능한 액티브 목록으로 제한된다. |
| DB 여부 | Run Runtime 값. 직접 참조 검색 및 `GatherRun` 확인상 `OwnedSkillPool`/`RandomSlots` 직렬화는 없다. 저장되는 레거시 `MonsterSlots`, 영구 `OwnedSkills`/해금과 구별해야 한다. |

근거: [필드](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:4), [목록 생성](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:152), [Run 경계](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:596), [재등록](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:4854), [GatherRun](D:/maplestory_levup/RootDesk/MyDesk/Save/PlayerDBManager.mlua:1418).

### 한 Run에서 얻을 수 있는 종류 수

**CONFIRMED — 디스크 CSV 집계:** SkillTable 112행, MonsterTable 103행. `MonsterTable.drop_skill_id` 역참조 + `GetCapturableActiveSkillIds` 필터를 적용하면 **66종: 공격 59 / 방어 5 / 버프 2**다. SkillTable 전체나 몬스터 수가 그대로 Run Pool 크기는 아니다.

지역별로 `GetMegaAreaSources` → `GetRoomsForMegaArea` → `GetMegaMonsterPool`과 같은 제외 조건을 적용한 일반 액티브 후보는 다음과 같다.

| Mega Area | 일반 몬스터 후보 종 수 | 일반 액티브 SkillID 후보 종 수 | 최종 보스 후보 |
|---|---:|---:|---|
| mega_01 | 16 | 13 | 액티브 보상 보스 4종 중 한 종 선택 |
| mega_02 | 17 | 9 | 동일 |
| mega_03 | 16 | 8 | 동일 |
| mega_04 | 16 | 8 | 동일 |
| mega_05 | 16 | 8 | 동일 |

근거: [SkillTable](D:/maplestory_levup/RootDesk/MyDesk/GameData/SkillTable.csv), [MonsterTable](D:/maplestory_levup/RootDesk/MyDesk/GameData/MonsterTable.csv), [RoomTable](D:/maplestory_levup/RootDesk/MyDesk/GameData/RoomTable.csv), [캡처 필터](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:1178), [지역 후보](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:1739).

**CONFIRMED:** 일반 방은 해당 지역 Pool에서 2~4종, 6~10개체로 조합한다. Mid Boss는 이 일반 조우의 액티브 보상 가능 몬스터를 정예로 승격하므로 별도 신규 SkillID 후보를 더하지 않는다. 최종 보스는 네 후보 중 한 종만 선택한다. 최종 보스 보상은 목표 완료 처리 직전에 일어나며, 완료가 확정되면 곧바로 Pool을 비운다.

**INFERRED:** 최종 보스 전 실전 Pool의 지역별 느슨한 상한은 13/9/8/8/8종이다. 모든 후보를 실제로 만나고 획득한다는 뜻은 아니다. 일반 지급 확률·Seed별 출현 종·방문 경로·Party 분배 때문에 개인 실제 보유는 더 적을 수 있다. 첫 공통 보장만으로 개인 3종 또는 5종 보유가 보장되지는 않는다. 최종 보스 스킬을 더해 단순 상한을 +1 할 수는 있어도 이를 같은 Run의 안정적인 콤보 재료로 기대하면 안 된다. 실제 보유 분포/도달 시간은 **NOT_VERIFIED**다.

## 4. Random 5 Slot

**CONFIRMED — 시간 순서**

1. `BeginRogueliteRun`: 1~5 인덱스를 nil로 초기화; Pool도 비움. 시작 즉시 다섯 개를 주지 않는다.
2. 첫 Pool 추가: 빈칸이 있고 타이머가 없으면 `StartRandomSkillSupply` 호출.
3. `HasEmptyRandomSlot`: 각 인덱스의 nil 또는 빈 문자열을 검사한다. `#SyncTable`에 의존하지 않는다.
4. `StartRandomSkillSupply`: 기존 타이머 정리 후 활성 모드·빈칸·비어 있지 않은 Pool 검사. `SetTimerOnce`로 **5초 뒤 한 번** 예약한다.
5. 타이머 실행: 타이머 ID/`NextSupplyAt` 초기화 → `SupplyOneRandomSkill` → 다시 예약 시도.
6. 공급: ID 정렬 Pool에서 `RogueStreamNextInt("supply:" .. UserId, #pool)`로 하나 추첨. 다른 칸의 ID를 제외하지 않는다.
7. 배치: 1→5 순서로 찾은 **첫 빈칸**. 위치는 랜덤이 아니다.
8. 가득 차면 타이머를 더 예약하지 않는다. 비어 있으면 다음 5초에 또 한 칸 공급한다.
9. 사용: 서버 실행 함수가 false면 슬롯 소비 호출에 도달하지 않는다.
10. 성공: `ConsumeRandomSlot(index, expectedSkillId)`가 인덱스 범위와 현재 내용 일치를 확인한 후 해당 칸만 nil로 만든다.
11. 이미 공급 예약이 있으면 그 마감 시각을 유지한다. 예약이 없으면 소비 시점부터 새 5초를 센다.
12. 빈칸은 그대로 표시하며 다른 칸을 당겨 채우지 않는다.

근거: [공급·소비](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:433), [현재 공급 값](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameBalance.csv:153), [RNG](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:1833), [고정 인덱스 반환](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:1244), [고정 위치 표시](D:/maplestory_levup/RootDesk/MyDesk/UI/SkillBar.mlua:560).

**INFERRED — 코드로 계산한 예:** 꽉 찬 상태에서 A·B를 연속 사용하면 두 칸이 빈다. 먼저 사용한 시점에서 약 5초 후 한 칸, 약 10초 후 다음 한 칸이 채워진다. 이미 타이머가 진행 중이었다면 첫 공급 대기는 5초보다 짧다. 첫 획득 직후 아무것도 사용하지 않으면 다섯 칸을 채우는 데 약 25초가 필요하다. 이는 서버 지연을 제외한 코드상 시간 예시이지 실측이 아니다.

튜토리얼은 별도다. 모든 캡처 액티브를 후보로 다섯 칸을 준비하고 사용한 칸에 기존 ID를 제외한 후보를 즉시 넣는다. 본 Run 콤보는 `TutorialModeActive`를 명시적으로 제외해야 한다.

서버는 `UseSkill(A)` → 성공 분기 → `ConsumeRandomSlot(A)` → 이후 처리한 `UseSkill(B)` → `ConsumeRandomSlot(B)` 순서를 관측할 수 있다. 이것은 **서버 수신/처리 순서**이지 사용자의 네트워크 전송 전 입력 순서 보장은 아니다. 동시 입력·동일 칸 연타의 실기 검증은 **NOT_RUN**이다.

## 5. Skill Use 성공 판정 지점

### 실제 실행 순서 — CONFIRMED

공통 진입: 버튼 클릭 또는 키 입력 → `SkillBar.Use`(조준 방향 포함) → `RequestUseSkill` 서버 RPC의 소유자 검사 → `UseSkill` → `CanActInCurrentRun`(기절·사망·Run 종료·참가/생존 여부) → `GetActiveSkills()[index]` → SkillTable 조회 → 종류별 실행.

| 분기 | 실제 승인·효과·소비 순서 |
|---|---|
| Defense | `UseDefenseSkill` 효과 적용 성공 → `PlayCast` → 슬롯 소비 → true |
| Buff | 유효 효과/값/지속시간 검사 및 버프 상태 적용 → `PlayCast` → 슬롯 소비 → true |
| 즉발 Attack/Area | `ResolveSpatialHit`에서 공격 판정·피해·2차 효과·연출 → `UseSpatialSkill=true` → 슬롯 소비 |
| 지연 Area/Zone | 영역 연출 + 지연/반복 타격 예약 → true → 슬롯 소비 → 이후 타격 |
| Projectile | 목표/벽 끝점 계산 → 투사체 연출 또는 cast 대체 연출 → 착탄 타이머 예약 → true → 슬롯 소비 → 이후 착탄 판정 |
| Dash | 서버 출발/도착점 결정 → 당사자 이동 RPC + 이동 연출 → 도착 타격 예약 → true → 슬롯 소비 → 이후 타격 |

현재 본 Run은 SkillTable 쿨다운 검사를 건너뛰며, 별도의 MP/마나 차감은 이 사용 경로에 없다. 재사용 비용은 슬롯 토큰이다. Run 밖의 투사체/돌진 레거시 분기에는 `StartCooldown` 호출이 남아 있다. 따라서 쿨다운 시작 훅을 본 Run 성공 이벤트로 사용하면 안 된다.

근거: [클라이언트 요청](D:/maplestory_levup/RootDesk/MyDesk/UI/SkillBar.mlua:381), [소유자 검사·UseSkill](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:445), [공간 스킬](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:554), [투사체](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:667), [돌진](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:840).

### 집계 후보 비교

| 후보 | 서버 권위 | 장점 | 위험 / 판정 |
|---|---|---|---|
| `SkillBar.Use` 입력 | 아니오 | 입력을 모두 관측 | 빈칸·실패·기절·종료 요청까지 섞임. 부적합. |
| `RequestUseSkill` 진입 | 예 | 소유자 확인 가능 | 요청이지 성공 아님. 부적합. |
| `UseSkill` true 반환 | 예 | 실행 승인 의미 | 반환점이 여러 개이고, 호출자가 SkillID를 받지 않는다. 또한 현재 소비 함수 반환값을 무시한다. |
| `ConsumeRandomSlot`의 본 Run 성공 분기 | 예 | 모든 현행 슬롯 스킬의 성공 경로가 모이고 ID/index 검사·소비가 한 곳에 있음 | 가장 작은 접점. 튜토리얼/비활성/종료 상태를 별도 제외해야 함. |
| `CalcDamage`/Hit | 예 | 실제 공격 적중 관측 | 다중 대상·반복 피해·기본공격이 섞이고 방어/버프는 누락. 부적합. |
| `SkillEffect.ShowCast`/SFX | 아니오(표현) | 눈·귀 피드백 | 다른 시전자도 사용하고 연출 실패/반복이 게임 성공과 다름. 부적합. |

**추천 — INFERRED:** `ConsumeRandomSlot`에서 **본 Run의 정확한 슬롯 검증과 비우기가 성립한 뒤**, 성공한 SkillID를 개인 콤보 상태로 넘기는 위치가 가장 자연스럽다. 현재 `SkillUseSucceeded` 같은 별도 공통 이벤트가 이미 있는 것은 아니다. 현재 함수가 접점 후보라는 뜻이다.

**CONFIRMED:** 성공은 “사용을 승인하고 실행/효과 예약했다”이며 “적에게 명중했다”가 아니다. 허공 투사체·0명 적중 범위기·벽에 막힌 돌진도 true가 될 수 있다. 방어는 효과 함수가 false인 경우 소비하지 않는다. 적용 성공 후 시각 이펙트가 실패하거나 지연 공격이 맵 변경으로 취소돼도 슬롯을 환불하는 경로는 없다.

**주의 — CONFIRMED/INFERRED 구분:** 현재 `UseSkill`의 다섯 소비 호출은 `ConsumeRandomSlot`의 boolean 반환을 확인하지 않는다. 따라서 `UseSkill=true`와 `소비 성공=true`를 무조건 동일시하면 안 된다(CONFIRMED). 즉발 마지막 타격 안에서 보스 클리어→Run 정리가 먼저 발생하면 뒤의 소비가 실패할 수 있는 호출 순서다(INFERRED, 해당 동시 상황 NOT_VERIFIED). 끝난 Run에 Rush를 다시 켜지 않는 것이 우선이며, 이 경계는 향후 작은 검증 항목이다.

## 6. Skill Identifier

**CONFIRMED:** 정본은 문자열 **`SkillTable.id` / Runtime `skillId`**다. `LoadSkills`가 `skills[id]`로 로드하고, 몬스터 `drop_skill_id`, Pool 키, `RandomSlots[index]`, `GetSkill`, 공격 `attackInfo`가 이 ID로 연결된다.

같은 A가 1번·4번 슬롯에 있더라도 두 소비 호출의 `expectedSkillId`는 같다. A→A 반복을 정확히 구별할 수 있다. 슬롯 번호는 자리일 뿐이며 슬롯 이동으로도 바뀐다. MonsterID는 획득 출처이고, PendingAbilityRevision은 선택 요청 토큰이다. 이들을 스킬 동일성으로 쓰면 안 된다.

**INFERRED:** `lastSkillId`만 비교하면 “직전과 다른가”만 판정한다. A→B→A는 인접 중복은 없지만 서로 다른 3종이 아니다. A/B/C안의 “서로 다른 3~5개”를 **구간 내 전부 고유한 ID**로 해석한다면 사용한 ID 집합이 추가로 필요하다. 이 정의는 구현 전 명확히 정해야 하며 본 보고서는 비교 시 전부 고유한 ID를 기준으로 한다.

근거: [LoadSkills](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:595), [슬롯 소비 ID 검사](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:492), [슬롯 교환](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:795).

## 7. Combo Timer 구현 후보

| 기존 패턴 — CONFIRMED | 용도 | Combo/Rush 적합성 — INFERRED |
|---|---|---|
| `_UtilLogic.ServerElapsedSeconds` | Run 제한시간, 드롭 만료 시각 | 서버 기준 lastUse/endTime 비교에 우선 추천. |
| 서버의 `_UtilLogic.ElapsedSeconds` | 공격 기절·일시 강화·쿨다운·공급 시각 | 서버 안에서 비교하면 사용 가능. 클라이언트 시계와 직접 섞지 않아야 함. |
| `_TimerService:SetTimerOnce` | 슬롯 공급, 지연 피해, 토스트 숨김 | 만료 통지/연출 정리에 적합. 재발동·Run 변경 시 이전 예약 무효화가 필요. |
| 반복 타이머/OnUpdate | 자동공격 탐색, SkillBar 0.3초 갱신, Dash 이동 | HUD 진행도에는 가능. 콤보 판정을 매 프레임 해야 할 필요는 없음. |
| Ratio + Until | `OutgoingBoostRatio/Until`, `NextAttackBoostRatio/Until` | 시간 제한 버프의 패턴은 재사용 가능하지만 기존 상태 칸을 공유하면 충돌. |

**INFERRED:** 서버 성공 소비 시 timestamp 비교로 유효한 체인을 판정하고, HUD만 경과를 표현하는 구성이 단순하다. 만료 때 즉시 화면을 지워야 한다면 예약/가벼운 표시 갱신을 보조로 쓰되, 서버 판정의 정본은 timestamp로 유지하는 편이 자연스럽다. 예약을 추가한다면 사용자·Run revision·재발동 세대가 바뀐 콜백은 적용하지 않아야 한다.

**CONFIRMED:** `PlayerAttack.GetCooldownRemain`에는 서버·클라이언트 `ElapsedSeconds` 차이 때문에 절대 시각을 그대로 빼지 않고 클라이언트에 지속시간을 보내 자체 표시 시계를 만드는 패턴이 있다. `NextSupplyAt`을 그대로 클라이언트 콤보 시계로 재활용해서는 안 된다. Rush의 제한시간/지속시간 수치는 이 보고서에서 정하지 않는다.

근거: [Run 시계](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:3934), [버프](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:368), [시계 분리](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:986).

## 8. Skill 종류별 Combo 적합성

아래 “공통 지점 통과”는 기존 별도 이벤트가 아니라 `UseSkill` 성공 후 `ConsumeRandomSlot` 경로를 뜻한다. 통과 여부는 CONFIRMED, 포함 권고는 INFERRED다. 분류는 배타적이지 않다(예: Area+Projectile+Control).

| 행동 | SkillID / 예 | 슬롯 소비 | 공통 지점 통과 | Combo 후보 |
|---|---|---|---|---|
| 기본 자동공격 | `attackInfo=nil` | 없음 | 아니오 | 제외. 자동으로 콤보가 쌓이면 수동 손패 연계와 달라짐. |
| 일반 이동 | 슬롯 SkillID 없음 | 없음 | 아니오 | 제외. |
| 즉발 Attack / Line / Cone | 있음: `s_mon_snail_dew_trail` | 성공 시 | 예 | 포함 가능. 적중 수와 무관하게 1회. |
| Projectile | 있음: `s_mon_faust` | 발사 승인 시 | 예 | 포함 가능. 착탄/다발탄마다 중복 집계 금지. |
| Area / 지연·지속 영역 | 있음: `s_mon_mushroom` | 실행·예약 승인 시 | 예 | 포함 가능. tick마다 집계하지 않음. |
| 슬롯 Dash | 있음: `s_mon_red_snail` 등 8종 | 출발 승인 시 | 예 | 포함 가능. 실제 이동 완료 성공까지 보장하는 훅은 아님. |
| Defense | 있음: `s_mon_blue_snail` 등 5종 | 효과 성공 시 | 예 | 포함 가능. 공격 연타가 아니라 ‘스킬 연계’라는 설명 필요. |
| Buff | 있음: `s_mon_drumming_bunny`, `s_mon_memory_monk_trainee` | 상태 적용 성공 시 | 예 | 포함 가능. 기존보다 약한/같은 버프를 써도 순증 효과와 성공은 다를 수 있음. |
| Control | 별도 `skill_kind=control`이 아니라 공격의 `secondary_effect` | 모체 스킬 1회 | 예 | 모체 사용만 집계. 디버프 적용 대상마다 추가하지 않음. |
| 피격으로 생긴 밀침·기절 / 강제 이동 | 사용자 슬롯 시전 아님 | 없음 | 아니오 | 제외. |
| 동행 몬스터 공격 | 이 플레이어 슬롯 소비 경로 아님 | 없음 | 아니오 | 제외. 공유 VFX 함수 사용을 콤보로 오인하지 않음. |

**CONFIRMED:** 자동공격은 `RestartAutoAttack` 타이머→`AttackNormal`→`AttackFast(..., nil, ...)`로 실행된다. 수동 Run Skill과 진입·소비는 분리됐지만 `CanActInCurrentRun`, `AttackComponent`, `CalcDamage`는 공유한다. 따라서 “완전히 아무 코드도 공유하지 않는다”는 표현은 부정확하다.

근거: [자동공격](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:91), [방어·버프](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:316), [2차 효과](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:637), [태그 분류](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:1126), [이동 RPC](D:/maplestory_levup/RootDesk/MyDesk/Player/PlayerDash.mlua:29).

## 9. Upgrade 3택과 연결 가능성

현재 정의와 직접 적용 범위는 다음과 같다(CONFIRMED).

| Upgrade | 직접 적용 | 수동 Run Skill 영향 |
|---|---|---|
| attack_speed | `PlayerStats.GetAttackInterval` → 자동공격 타이머 | 슬롯 공급 주기/시전 횟수에는 적용 안 됨. |
| attack_damage | `CalcDamage`의 `attackInfo=nil/empty` 조건 | 기본공격 한정. 스킬 계수에는 직접 적용 안 됨. |
| attack_range | `AttackNormal` 반경 | 수동 스킬의 `skill.range`를 늘리지 않음. |
| extra_target | `BuildBasicAttackTargets` | 수동 스킬 `max_targets`를 늘리지 않음. |
| pierce | 기본공격 주 대상 뒤 추가 타격 | Projectile 스킬의 관통 속성과 별개. |
| move_speed | 일반 `MovementComponent.InputSpeed` | 이동·포지셔닝에는 영향. Dash 거리는 스킬 데이터로 별도 산출. |
| max_hp | Player 최대 HP | 생존에 영향. 스킬 공급에는 영향 없음. |
| damage_reduction | PlayerHit 피해 감소 | 생존에 영향. 스킬 공급에는 영향 없음. |

정본은 `GameData.RogueRunUpgradesByUser[userId]`. 3택은 개인별 후보·revision·mapId를 저장하고 선택 RPC를 검증해 누적 stack을 적용한다. 이번 보고서는 이 접점만 확인했으며 Upgrade 시스템을 재감사하지 않았다.

**INFERRED:** Rush를 Upgrade stack에 일시적으로 더했다가 빼는 방식은 피하는 것이 안전하다. 상한·영구 Run 누적값·3택 상태와 짧은 버프의 수명이 다르다. 기존 Ratio/Until 방식과 `CalcDamage`의 계수 계산 위치는 활용할 수 있지만 Rush 전용 상태를 따로 두고 합산/곱산 규칙을 정해야 한다.

**CONFIRMED:** `OutgoingBoost`는 같은 계열에서 강한 비율/긴 종료시각을 취하며 0.75 상한이 있다. `NextAttackBoost`는 다음 피해 계산에서 소비된다. 둘 다 기본공격과 수동 스킬이 공유하는 `CalcDamage`에서 사용한다. 따라서 기존 필드에 Rush 값을 덮어쓰면 현재 버프와 중첩·만료·초기화가 섞이고, 기본공격에도 적용된다. 범용 modifier registry가 이미 있어서 안전하게 꽂기만 하면 되는 구조로 보아서는 안 된다.

근거: [8종 정의](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:1880), [강화 적용](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:2077), [자동 타격 대상](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:239), [피해 분기·버프](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua:1116), [공격속도](D:/maplestory_levup/RootDesk/MyDesk/Player/PlayerStats.mlua:440), [피해 감소](D:/maplestory_levup/RootDesk/MyDesk/PlayerHit.mlua:141).

## 10. Mid Boss와 연결 가능성

**CONFIRMED:** 현재 코드에서 Mid Boss에 해당하는 접점은 `IsElite` / `RogueEliteRoomId` / `ELITE_UPGRADE`다. 일반 조우 중 액티브 보상 가능 종을 정예로 승격한다.

`RoomMonster.Dead(IsElite)` → `GrantRunEliteKillRewards`가 `RogueEliteKillInProgress=true` 상태로 일반 보상 함수를 호출 → 동일한 자동 지급 경로에서 확률 상향 → 플래그 복원 → `OnRunEliteDefeated` → 정예 완료 및 포털 해제 → `ELITE_UPGRADE` 상자 생성.

정예 스킬 확률 기본값은 `GameData.LoadBalance`의 **0.75 fallback**이며, 실제 판정은 `max(첫 보장 또는 일반 확률, 정예 설정)`이다. 디스크 GameBalance CSV에는 해당 정예 확률 행이 없으므로 “CSV에서 75%를 확인했다”가 아니라 **데이터셋 값이 없을 때 75%가 적용되는 코드**로 확인했다. 이번에 Maker가 로드한 실제 데이터셋 값은 NOT_VERIFIED다.

스킬은 여전히 적격 미보유자 한 명에게 지급된다. 반면 정예 상자의 강화 선택은 `RogueChestOpenedByUser` / `RoguePendingUpgradeChoicesByUser`로 사용자별 관리된다. 상자를 연 후 `DrawRunUpgradeChoices` → 개인 Client view → 선택 RPC → `ApplyRunUpgrade`가 이어진다. 정예 사망 순간 모든 사람에게 스킬·강화를 자동 동시 지급하는 구조가 아니다.

**INFERRED:** Rush는 Mid Boss와 독립적으로 두는 편이 안전하다. Mid Boss는 Pool 확장 기회/기본 전투 강화, Rush는 개인의 성공한 슬롯 사용 연계라는 역할이 이미 나뉜다. 현재 목적에는 정예 드롭·3택 보상 규칙을 바꿀 이유가 없다.

근거: [정예 승격 후보](D:/maplestory_levup/RootDesk/MyDesk/Room/RoomSpawner.mlua:676), [정예 사망 분기](D:/maplestory_levup/RootDesk/MyDesk/Combat/RoomMonster.mlua:452), [정예 보상](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:5027), [정예 기본값](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:501), [상자·선택](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:2192).

## 11. HUD 삽입 후보

**CONFIRMED — UIBuilder 읽기 결과:** [SkillBar.ui](D:/maplestory_levup/ui/SkillBar.ui)는 `/ui/SkillBar` 루트(`DefaultShow=true`, `GroupOrder=1`, `GroupType=0`) 아래 다음 구조다.

```text
/ui/SkillBar
├─ Skill1 … Skill5 (각 Button, 88×88)
│  ├─ Icon (70×70)
│  ├─ Key
│  ├─ Cool
│  └─ Name (현재 비활성)
├─ AbilityOffer (680×270, 기본 비활성)
│  └─ Title / Details / Icon / Replace1…5 / Decline 등
└─ AbilityToast (512×74, 기본 비활성)
   └─ Title / Details / Icon
```

별도 `SlotsRoot`는 없고 다섯 버튼이 루트의 직접 자식이다. 1920×1080 기준 오른쪽 아래 anchor/pivot `(1,0)`에 x=-412,-314,-216,-118,-20 / y=20, 간격 98로 배치된다. 버튼 묶음은 오른쪽에서 20~500, 아래에서 20~108 UI px 영역이다. `Refresh`도 이 x 위치를 유지한다. 스킬바 루트 아래 SafeArea 컨테이너는 없다.

**INFERRED — 후보:** 슬롯 바로 위의 같은 오른쪽 아래 anchor 영역에 작은 Combo 수치/시간선, 단계 도달 때만 짧은 강조를 두는 것이 가장 관련성이 높다. 후보 공간이지 가용 확정 공간은 아니다. `AbilityOffer`는 오른쪽 아래 y=158부터 270 높이를 차지하는 기존 패널이므로 그 표시 조건과 함께 확인해야 한다.

**CONFIRMED:** 화면 상단 중앙에는 `AbilityToast`(top-center, y=-128)와 [GateNotice Banner](D:/maplestory_levup/ui/GateNotice.ui)(top-center, y=-200, 760×120)가 있다. `GateNotice.ShowNotice`는 2.5초 표시 후 숨기는 기존 짧은 메시지 패턴이다. Upgrade 결과도 이를 사용한다. 중앙에는 [RoomProgress의 ResultPanel](D:/maplestory_levup/ui/RoomProgress.ui)이 있고, [PlayerHud](D:/maplestory_levup/ui/PlayerHud.ui)의 보스 HUD·강화 선택 창 등도 별도 사용 중이다.

**INFERRED:** 중앙 강조의 표시/숨김 패턴은 재사용할 수 있지만 GateNotice/AbilityToast 자체를 무조건 공유하면 획득·포털 안내를 덮어쓴다. 지속 Combo는 슬롯 근처, 단계 메시지는 비입력 HUD overlay로 분리하는 것이 자연스럽다. 새 팝업을 열거나 전투 입력을 막을 필요는 없다.

모바일에서 피할 영역은 **CONFIRMED**된 `/ui/DefaultGroup/UIJoystick`(Mobile 전용, 좌하단 중심 310,230 / 약 200×200), 우하단 다섯 슬롯의 터치 영역, 채팅/상단 시스템 버튼, 보스 HP·Run 시간·Party 상태다. 현재 슬롯은 88×88이며 인접 간격은 10 UI px로 여유가 크지 않다. 노치/홈 인디케이터, 실제 화면비·손가락 가림·다중 팝업 중첩은 **NOT_VERIFIED**. 배치 수치만으로 모바일 적합 PASS를 선언하지 않는다.

근거: UIBuilder `read/listEntities/getComponent` 결과, [SkillBar.Refresh](D:/maplestory_levup/RootDesk/MyDesk/UI/SkillBar.mlua:522), [토스트](D:/maplestory_levup/RootDesk/MyDesk/UI/SkillBar.mlua:621), [GateNotice](D:/maplestory_levup/RootDesk/MyDesk/UI/GateNotice.mlua:52).

## 12. VFX/SFX 연출 재사용 가능성

| 공통 경로 — CONFIRMED | 현재 역할 | Rush에 대한 판단 — INFERRED |
|---|---|---|
| `SkillEffect.ShowCast` | 스킬 `sfx_ruid`를 클라이언트에서 재생. 수신자의 `AudioSfxVolume` 반영 | 사운드 API/개인 볼륨 패턴을 재사용 가능. 이 함수 호출을 성공 집계로 쓰지는 않음. |
| `PlayCast / PlayAttackAt / PlayAreaAt / PlayProjectile / PlayDashTravelIfNeeded` | 종류별 연출을 시작하고 같은 맵 사용자에게 필요한 표현 전달 | 기존 코드 호출 구조 활용 가능. 모든 스킬의 유일한 성공 SFX 이벤트는 아님. |
| `SpawnLayerAt` | 맵 아래 `skillcasteffect` 모델 생성, RUID·레이어·scale/alpha·FollowTarget 지정, `SkillCastEffect.Play` | Player 주변 짧은 강조를 표현하는 기존 수단. 과도한 새 효과 시스템은 불필요. |
| `ShowCast`의 호환 경로 | `_EffectService:PlayEffectAttached` | 붙는 단일 이펙트 호출 패턴 존재. 모든 자산이 이 경로라는 뜻은 아님. |
| `_SoundService:PlaySound` | 클라이언트 로컬 재생 또는 서버에서 UserId 지정 | 당사자 UI 단계음에 이용 가능. 현재 조사 범위에서 범용 Rush/UI 사운드 wrapper는 확인하지 못함. |
| `GateNotice.ShowNotice` / `SkillBar.ShowRunAbilityToast` | 짧은 문구와 숨김 타이머 | 단계 강조의 표시 수명 패턴 재사용 가능. 알림 경쟁 정책은 필요. |

Upgrade 결과는 `NotifyRunChestResult`→`GateNotice`; ResultPanel은 결과 상태에 따라 표시하는 별도 창이다. 조사한 코드에서 Boss/Upgrade/Result 전체를 공통으로 묶는 “3단계 강도 연출 API”는 확인되지 않았다. 존재하지 않는 전용 Rush 연출을 이미 재사용 가능하다고 가정하지 않는다.

**INFERRED:** 3/4/5 단계마다 텍스트·짧은 Player 이펙트·당사자 소리의 강도를 달리하는 것은 기존 표현 수단으로 가능하다. 단, 다른 실제 스킬의 `PlayCast(skillId)`를 무작정 호출해 그 스킬 사용처럼 보이게 하는 것보다는 표현 호출/수명 관리 패턴만 재사용하는 편이 명확하다. 동일 맵 전체 방송은 Party 소음/시각 혼잡을 키우므로 개인 HUD·개인음과 월드 VFX의 수신 범위를 구분해야 한다. 자산 선정·청감·성능은 NOT_VERIFIED다.

근거: [PlayCast](D:/maplestory_levup/RootDesk/MyDesk/Combat/SkillEffect.mlua:7), [SpawnLayerAt](D:/maplestory_levup/RootDesk/MyDesk/Combat/SkillEffect.mlua:231), [ShowCast](D:/maplestory_levup/RootDesk/MyDesk/Combat/SkillEffect.mlua:509), [대상별 PlaySound](D:/maplestory_levup/RootDesk/MyDesk/Combat/SkillEffect.mlua:63), [Upgrade 알림](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:1971).

## 13. Multiplayer / Run Reset 안전성

**INFERRED — 상태 소유자 추천:** 플레이어 Entity의 **`PlayerSkillSlots`**가 가장 작고 자연스럽다. 서버가 `comboCount`, `lastSkillId`, `lastSkillUseTime`, `rushLevel`, `rushBuffEndTime`을 소유하고, 필요 표시만 당사자 Sync/RPC로 전달하는 형태다. 구간 전체 고유 ID 조건이라면 사용 ID 집합도 개인별로 필요하다. 이 상태는 현재 구현되어 있지 않다.

근거는 CONFIRMED된 개인 Pool/슬롯·성공 소비·Begin/End Run 경계가 이미 같은 컴포넌트에 있다는 점이다. 전역 `SkillBar @Logic` 또는 `SkillEffect @Logic`의 단일 변수에 콤보를 두면 표현 수명/다른 시전자와 섞일 여지가 생긴다. 서버 `RequestUseSkill` 소유자 검사와 사용자별 컴포넌트 경로를 유지하면 Party 입력을 한 카운터로 합칠 이유가 없다.

| 상황 | 현재 경로 — CONFIRMED | 향후 Rush 처리 후보 — INFERRED |
|---|---|---|
| Run 시작 | `RegisterRunParticipant` → `BeginRogueliteRun` | 개인 상태 전부 초기화, Run 세대 기록. |
| 같은 Run의 방/맵 이동 | `OnMapLeave`는 선택 후보만 정리; 활성 참가자 재등록은 유지 | Pool은 유지. 콤보 시간은 계속 흐르게 하거나 이동 시 끊는 정책을 명시. 단순 timestamp 유지라면 이동이 시간을 멈추지 않음. |
| Run Portal 이동 | `RoomPortal`이 전환 승인→관전자 부활→참가자 Teleport | 별도 Run 시작으로 처리하지 않음. 전환 중 사용/보상 여부는 향후 명시해야 함. |
| 사망 | `PlayerHit.HandleDeath` → `GameData.OnRunPlayerDied`, 생존 false | 짧은 체인/활성 Rush는 사망 즉시 정리 권고. 현재 Pool은 개인 사망만으로 정리하지 않음. |
| Respawn/관전자 재합류 | `ReviveRunSpectatorsAtTransition` → Respawn/생존 true/Teleport | 사망 시 지운 체인을 되살리지 않음. Pool·기존 슬롯 유지 계약과 분리. |
| 최종 보스 클리어 | `CompleteRogueliteRun`의 참가자 루프에서 `EndRogueliteRun` | 같은 경계에서 즉시 초기화. 이후 소비/지연 콜백으로 재활성화하지 않음. |
| 전원 사망/시간 초과 | FAILED 확정 즉시 행동 차단; `EndRogueliteRun`은 10초 후 예약 | End만 기다리지 말고 종료 상태부터 Rush 효과/표시를 비활성으로 간주. |
| 던전 포기 | `AbandonRogueliteParticipant` → `CleanupAbandonedRunPlayer` → `EndRogueliteRun` | 해당 사용자만 정리. 남은 Party원의 콤보에 영향 주지 않음. |
| 결과창 조기 복귀 | `RequestCloseRogueliteResult` → Static Room 이동 | 목적지/엔티티 수명과 무관하게 종료 상태 guard 필요. 특히 FAILED의 지연 정리를 유의. |
| 엔티티 제거/새 Room 인스턴스 | `PlayerSkillSlots.OnEndPlay`는 공급 타이머 해제 | 추가 타이머도 정리. 새 Entity에서는 초기 상태. 재접속 보존은 이번 설계에서 자동 보장하지 않음. |

**NOT_VERIFIED:** 실제 다인 입력 순서, RoomService 이동 시 엔티티 재생성·재접속 복원, 사망과 마지막 시전의 동시 처리, 클리어 직전 지연 타격. 위 표는 코드상의 연결과 설계상 정리 위치이지 멀티플레이 PASS 표가 아니다.

근거: [Begin/End](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua:596), [포털 전환](D:/maplestory_levup/RootDesk/MyDesk/Room/RoomPortal.mlua:310), [사망·실패](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:5220), [포기 정리](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:5306), [부활](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua:5494).

## 14. A/B/C Combo 설계 비교

아래 평가는 모두 **INFERRED**다. “서로 다른”은 체인 구간 내 고유 SkillID로 해석했다. 기존 5슬롯은 계속 한 칸씩 공급되는 재고이지 고정 라운드 손패가 아니다.

| 기준 | A: 고유 3종→Rush 1회→초기화 | B: 고유 3/4/5종→단계 Rush→초기화 | C: 다섯 슬롯 세트의 고유 5종 전부 사용 |
|---|---|---|---|
| 현행 코드 적합성 | 높음. 소비 훅+개인 체인 | 높음. 같은 훅에 단계/중첩 규칙 추가 | 낮음. 세트 시작/끝과 교체·중복 정의가 현재 없음 |
| 구현 난이도 | 낮음~중간 | 중간. 3/4/5 보상·만료·재발동 처리 | 높음. 공급·세트 멤버십·중복 처리 정책 필요 |
| 5슬롯 활용 | 5칸 중 3종 선택, 두 칸을 남길 수 있음 | 5칸을 연쇄 선택하는 목적과 가장 가까움 | 표면상 높지만 5칸=5종이 아니라는 구조적 불일치 |
| 이해 용이성 | 높음. 목표 하나 | 보통. 중간 보상을 받은 뒤 계속 잇는 규칙 설명 필요 | 보통 이하. 중복 손패·중간 공급 시 무엇이 한 세트인지 혼동 |
| 랜덤 공급과 궁합 | 상대적으로 좋음. 작은 Pool에서도 문턱이 낮음 | 좋지만 4·5종은 Pool/추첨 의존도가 큼 | 나쁨. 5종 미만 Pool이면 성립 불가, 5칸 중복도 빈번 |
| Multiplayer 위험 | 낮음~중간. 개인 성공 소비/정리로 제한 가능 | 중간. 개인 단계음·중첩 상태 증가 | 중간~높음. 개인 세트와 보충 상태의 추가 동기화 |
| UI 복잡도 | 낮음. 숫자/남은 시간/한 번 강조 | 중간. 3/4/5단계·효과 상태 표현 | 높음. 세트 구성·사용 완료 표식·재공급 설명 |
| 밸런스 난이도 | 상대적으로 낮음. 한 문턱·한 보상 | 높음. 단계별 보상·계속 잇기 가치·MAX 빈도 | 높음. 세트 완성 가능성부터 공급 정책과 결합 |

“A→B→A도 직전과만 다르면 연계”로 바꾸면 2종 Pool로도 긴 체인이 가능해져 A/B의 접근성이 달라진다. 이는 동일한 설계의 사소한 구현 차이가 아니라 별도 규칙 변경이다.

## 15. 추천 설계

**INFERRED — 현재 구조에는 A안(서로 다른 3종 성공 사용→SKILL RUSH 1회→체인 초기화)을 우선 추천한다.**

이유는 기존 사용·소비 접점 한 곳으로 연결되고, 한 번에 공급되는 양이 한 칸뿐인 현행 재고를 크게 바꾸지 않기 때문이다. 다섯 칸 중 세 종류를 고르므로 방어/기동용 칸을 남길 여지가 있고, 5종 확보·완벽한 손패를 필수 조건으로 만들지 않는다. 최초 보장이 개인별이 아닌 Party 구조에서도 B/C보다 문턱이 낮다. 초기 밸런스 판단도 한 문턱·한 보상으로 좁힐 수 있다.

B안은 요청한 3/4/5 단계 피드백이라는 최종 방향과 가장 가깝다. 다만 지금은 개인 Pool 크기·고유 손패 빈도·빈 슬롯 시간의 실측이 없으므로, 세 단계 모두의 재미와 도달성을 이미 확보했다고 결론 내리기 어렵다. C안은 현재 재고를 세트로 바꾸는 별도 정책이 필요해 이번 최소 침습 목표와 가장 멀다.

이 추천은 구현 승인이나 실제 재미 검증이 아니다. 시간 제한, 실패/중복 입력 시 체인 처리, Rush 보상 수치와 적용 대상은 정하지 않았다.

## 16. 구현 시 예상 수정 파일

모두 **INFERRED**, 향후 구현 범위 후보일 뿐 이번에는 수정하지 않았다.

| 파일 | 예상 역할 |
|---|---|
| [PlayerSkillSlots.mlua](D:/maplestory_levup/RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua) | 개인 콤보/Rush 상태, 성공 소비 접점, Begin/End 정리. 가장 핵심. |
| [PlayerAttack.mlua](D:/maplestory_levup/RootDesk/MyDesk/PlayerAttack.mlua) | 피해 보상을 선택한다면 계수 적용, 기존 버프와 분리. 소비 결과/종료 경계도 확인할 위치. |
| [GameData.mlua](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameData.mlua) | 사망·실패 즉시 정리가 필요할 때 기존 lifecycle에 좁게 연결. Drop/그래프/3택 재작성 대상 아님. |
| [SkillBar.mlua](D:/maplestory_levup/RootDesk/MyDesk/UI/SkillBar.mlua) | 개인 HUD 표시·종료 숨김·단계 강조. 판정 권위는 넣지 않음. |
| [SkillBar.ui](D:/maplestory_levup/ui/SkillBar.ui) | 작은 HUD overlay가 필요할 경우 UIBuilder로만 추가. |
| [SkillEffect.mlua](D:/maplestory_levup/RootDesk/MyDesk/Combat/SkillEffect.mlua) | 월드 VFX를 채택할 때만 좁게 연결. 텍스트/개인음만이면 필수 아님. |
| [GameBalance.csv](D:/maplestory_levup/RootDesk/MyDesk/GameData/GameBalance.csv) | 향후 시간/보상 수치가 확정되면 Maker 데이터 편집 경로로 설정. 현재 5초 값 변경을 전제하지 않음. |

SkillDropManager, MonsterTable, OwnedSkillPool 획득 규칙, DB 저장, Mid Boss/Upgrade 보상 구조를 바꾸는 것은 A안의 필수 작업이 아니다. 별도 Skill Tree·새 Skill 제작·새 대형 UI 시스템도 필요 조건이 아니다.

## 17. 위험 요소

총 10개. “코드에서 확인한 조건”과 “그로 인한 설계상 위험”을 구분한다.

| # | 확인된 조건 — CONFIRMED | 예상 위험 — INFERRED / NOT_VERIFIED |
|---|---|---|
| 1 | 5초마다 한 칸만 공급. 사용 중 기존 예약은 유지 | 짧은 콤보 시간창에서는 재공급 전에 체인이 끝나고, 연속 소비 후 공백이 길 수 있음. 허용 창/실제 성공률 NOT_VERIFIED. |
| 2 | 복원 추출·중복 칸 허용, 첫 보장은 Run 공통 한 번 | 작은 개인 Pool에서는 고유 3종조차 불가능한 구간, 5종 목표에서는 더 큰 랜덤 의존. 실제 Party 편차 NOT_VERIFIED. |
| 3 | 방어·버프도 소비 성공, 허공 공격도 시전 성공 | 적 없는 곳에서 사전 쌓기나 효율 없는 방어 소비가 최적 행동이 될 수 있음. ‘공격 콤보’라는 설명과 충돌 가능. |
| 4 | Consume 반환값을 UseSkill이 확인하지 않음; 입력/피해는 공통 성공 지점과 다름 | 실패 요청을 세거나 다중 적중을 여러 번 셀 위험. 성공한 본 Run 소비 한 곳에서만 집계해야 함. |
| 5 | 피해/공속/관통 Upgrade는 기본공격 중심; 버프 계수는 기본공격·스킬 공통 | Rush 보상의 적용 대상을 잘못 잡으면 기본공격 강화로 변질되거나 스킬 폭딜이 과도해질 가능성. 강도는 아직 미정. |
| 6 | 기존 OutgoingBoost/NextAttackBoost는 전용 상태와 만료 규칙이 있음 | 필드 공유 시 기존 버프 덮어쓰기/연장/상한 충돌. Rush 종료가 다른 버프까지 지울 수 있음. |
| 7 | 즉발 피해는 소비 전, 지연 피해는 소비 후; 지연 콜백은 현재 맵 확인 | Rush를 피해 계산 순간만 읽으면 같은 발동 스킬도 즉발/지연에 따라 혜택이 달라질 수 있음. 시전 시점 고정 여부 결정 필요. |
| 8 | SkillEffect는 여러 시전자와 같은 맵 수신자에 사용 | 동행/Party 스킬과 Rush 표현이 섞이거나 단계음이 과다해질 가능성. 표현 경로에서 집계하면 안 됨. |
| 9 | 하단 5슬롯·모바일 조이스틱·상단 획득/안내·보스 HUD가 존재 | Combo overlay가 조작 영역/중요 안내를 가릴 수 있음. 모바일·중첩 실기 NOT_VERIFIED. |
| 10 | 맵 이동은 Pool 유지, 개인 사망은 Pool 정리 안 함, 실패 End 처리는 지연, 클리어는 즉시 | Run 종료/사망 후 Rush 잔존 또는 지연 콜백 재발동 가능. 종료 guard와 개인 상태 초기화 경계 필요. |

## 18. 결론

1. **현재 구조에 최소 침습으로 넣을 수 있는가?** — **INFERRED: 가능하다.** 본 Run 성공 소비 접점과 개인 상태 수명이 이미 있다. 다만 현재 Rush 구현/런타임 검증 완료를 뜻하지 않는다.
2. **5 Slot 랜덤 시스템과 궁합이 좋은가?** — **INFERRED: 사용 순서를 고르는 A/B와는 좋다.** C의 고정 5종 세트는 중복·한 칸 공급 구조와 맞지 않는다.
3. **가장 자연스러운 집계 지점은?** — `PlayerSkillSlots.ConsumeRandomSlot`의 **본 Run 검증·소비 성공 직후**. 튜토리얼·종료 Run 제외. 별도 성공 이벤트는 현재 없다.
4. **상태 저장 위치는?** — **INFERRED:** PlayerSkillSlots의 사용자별 서버 Runtime 상태. 표시만 당사자 동기화. 영구 DB나 전역 UI 카운터는 아님.
5. **Drop / OwnedSkillPool 변경이 필요한가?** — **INFERRED: 필수 아님.** 현재 일반 Run은 자동 지급이며, 그 획득·Pool 계약을 유지한 채 연결 가능하다.
6. **5초 공급 주기를 변경할 가능성이 있는가?** — **INFERRED: 가능성은 있으나 지금 변경 근거는 부족하다.** 먼저 체인 시간창·Pool 크기·중복 손패·슬롯 공백을 함께 확인해야 한다. B/C가 더 민감하다.
7. **핵심 재미가 실제로 강화될 가능성이 있는가?** — **INFERRED: 있다.** 랜덤 재고를 즉흥적인 사용 순서 선택으로 연결할 수 있다. 반대로 빈칸 대기·방어 낭비·사전 쌓기가 늘 수도 있다. 실제 재미/빈도/밸런스는 **NOT_VERIFIED**, 이번 Maker 검증은 **NOT_RUN**이다.

최종 권고: **A안을 가장 작은 시작점으로 검토하되, 현재 Drop·Pool·Upgrade·Mid Boss는 유지한다.** 이 작업의 결과물은 현황 보고서뿐이며 Combo/Rush·UI·Skill은 구현하지 않았다.
