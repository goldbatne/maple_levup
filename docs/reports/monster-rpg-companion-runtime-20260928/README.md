# Monster RPG Companion Maker 검증 — 2026-09-28

대상: `D:/maplestory_levup`. 이번 검증에서는 게임 코드·데이터·모델을 수정하지 않았다. Maker Play의 격리 테스트 저장 키 `MakerTest_RoguelitePermanentV1`에서 자연 처치, 테이밍, 편성, 강화를 진행했다. 기존 작업 트리의 미커밋 변경은 그대로 두었고 commit/push하지 않았다.

## 판정 요약

| 항목 | 결과 | Maker 근거·한계 |
|---|---|---|
| Build | PASS | Refresh 후 Build 로그 `Error 0 / Warning 4`. 경고는 RunChest Interaction 2, 마노 InputSpeed, 보우마스터 AvatarAttackPlayRate. |
| 첫 Taming | PASS_RUNTIME | 미보유 `m_stone_golem` 처치 시 `rate=0.1 roll=0.030994402724781`, Lv1 등록 및 `[PlayerDB] 저장 완료 (Run 몬스터 테이밍)`. |
| 중복 Level | PASS_RUNTIME | 같은 몬스터 `count=1 rate=0.03 roll=0.0013454263104803`, 다음 `count=2 rate=0.03 roll=0.00018969364473116` 성공. 재접속 후 Lv3. |
| 성장 정수 | PASS_RUNTIME/STATIC | 두 번째 자연 Run 시작 전 15, 보스 Clear 후 82. 해당 Run의 `[MonsterTame]` 58건은 일반 57 + 보스 1이며 설정 `+1/+10`과 증가량 67이 일치. 참가자별 반경 보상은 `GameData.mlua:3441` 코드 확인, 2인 실제 배분은 미검증. |
| Enhance | PARTIAL | 달팽이 강화 요청 후 정수 20→15, stage 0→1, 로그 `[CompanionEnhance] ... cost=5`. 다음 Run `m_snail stage=2 HP=268.0 enhance=1` 확인(기본 250, 레벨 +5%, 강화 +2%). 기본공격·고유 스킬의 강화 계수와 Player 공격 무영향은 코드 확인; 동일 적/동일 레벨 전후 실제 피해량 비교는 미확인. |
| 3마리 Spawn·편성 | PASS_RUNTIME | 달팽이/스톤골렘/스켈레톤 지휘관 3종 동시 Spawn. 서로 다른 위치. 중복 편성 요청(`slot=2,m_snail`) 후 기존 편성 유지. |
| Formation | PASS_RUNTIME | 서버 좌표 예: Player(-8.22,1.00), 슬롯1(-7.15,0.97), 슬롯2(-8.72,1.85), 슬롯3(-8.80,0.00). 실제 이동 화면에서도 삼각형 유지. |
| 독립 전투 | PARTIAL | 3마리 각각 `[CompanionBasic]` 및 자기 Skill 시전, 개별 HP/사망 상태 확인. 동일 순간 서로 다른 적을 선택하는 시각 증거는 미확보. `CompanionCombat.FindTarget`은 각 Entity 위치에서 독립 탐색함(코드 확인). |
| 고유 Skill | PARTIAL | 정규 편성: 달팽이 `s_mon_snail_dew_trail`, 스톤골렘 `s_mon_stone`, 스켈레톤 지휘관 `s_mon_skeleton_commander`. 추가 보유 편성에서 버섯 DAMAGE_ZONE, 슬라임 FRONT_CONE, 다크 엑스텀프 DELAYED_BLAST, 다크 스텀프 SHIELD, 엑스텀프 FRONT_CONE 시전. 일시적 QA Entity로 빨간 달팽이 DASH_STRIKE, 스타픽시 PROJECTILE, 북치는 토끼 BUFF, 파우스트 PROJECTILE_BLAST 시전. 모두 MonsterTable의 자기 `drop_skill_id`였으며 자유 Loadout은 사용하지 않음. 시전 로그는 확인했지만 각 유형의 실제 디버프·버프 수치/피해 판정을 모두 계측하지는 못함. |
| 패시브 동행 | PASS_RUNTIME | `m_bubbling` 미보유→`rate=0.1 roll=0.091654163827959` 자연 테이밍. 컬렉션 Lv1 및 ‘사용 가능한 액티브 능력 없음’ 표시. 동행 Spawn 로그 `skill=`(빈 값), 기본공격 로그는 있고 Skill 시전 로그·Skill Drop은 없음. |
| 사망/복귀 | PASS_RUNTIME | 동행 피격으로 `defeated`, 해당 맵 `다음 안전 전환까지 소환 보류`; 같은 맵 재소환 없이 포털 이동 뒤 3마리 재생성. |
| Portal | PASS_RUNTIME | 키보드 이동으로 실제 r_001→r_007→r_001 등 `RunPortalRuntime PASS`, 새 맵 3종 Spawn·Formation 복구. 이전 맵 잔류 Entity 전수 계수는 미확인. |
| Boss | PARTIAL | 정규 3마리 편성으로 `r_05`에 진입해 세 CompanionBasic/Skill 로그 뒤 `m_mushmom` 사망, `[MegaBossClear] ...`, Run COMPLETE 및 maptown 복귀 확인. 클리어 순간의 `boss_with_companions.png` 캡처는 실패. 이후 재촬영 자연 Run은 보스 전 사망. |
| 저장/재접속 | PASS_RUNTIME | Maker Stop→Play 후 `maptown`, 달팽이 Lv2/강화1, 스톤골렘 Lv3, 패시브 버블링 Lv1, 정수, 3마리 원래 편성 유지. |
| Player Random 5 Slot 회귀 | PARTIAL | 실제 E로 World Skill Drop `s_mon_snail_dew_trail` 획득, 5초 랜덤 공급으로 같은 SkillID 5칸까지 생성, Z 사용 시 슬롯1만 소비, 뒤 재공급 로그 확인. 기본공격 피해 로그와 회복 상자 E 상호작용(HP 880→1000) 확인. 다른 Run에서 Boss Clear, Run Fail, UI 확인 후 Dungeon Leave로 로비 복귀. 공급 주기의 초 단위 오차, 0.55초 공격 간격 계측, Backtracking 전체 조합은 미확인. |
| Run 정리 | PASS_RUNTIME | Clear/Fail/Abandon 각각 로비 복귀. Run 이후 `RogueliteRunActive=false`, OwnedSkillPool 0, RandomSlots 0, HP 1000. 동행 Entity 로비 미잔류. 편성/성장 등 영구 데이터는 유지. |
| 실제 2–4P | BLOCKED_RUNTIME_MULTIPLAYER | Maker MCP Play context가 `client`, `server_main`, 단일 `server_instance_*`만 제공. 독립 클라이언트 기동 수단을 확인하지 못함. 참가자별 보상/타겟/슬롯은 코드만 확인했으며 멀티 Runtime PASS 아님. |

## 오류·경고

- Build: Error 0, Warning 4.
- Normal 로그: Error 1. 이는 **이번 검증용 조회 스크립트가 존재하지 않는 `GetMonsterEnhanceStage`를 호출해 발생한 `[LEA-2011]`**이다. 올바른 `GetMonsterEnhance`로 재조회했고 게임 코드 호출 경로에서는 같은 오류를 보지 않았다. 따라서 무조건 ‘Runtime Error 0’으로 보고하지 않는다.
- Normal Warning 613(최종 로그 조회 시점): 대부분 기존 Portal Trigger의 Legacy/모델 경고, UI 초기화 중 누락 Balance Key(`roguelite_run_mode_enabled`, `phase1_random_combat_enabled`, `phase3_simplified_growth_enabled`), `RoomBounds`의 RectTileMapComponent 경고다. 이번 요청이 검증 전용이라 수정하지 않았다. 실제 Portal 이동은 성공했지만 경고의 모든 영향이 없다고 결론내리지는 않는다.
- Maker 입력 제한: `maker_mouse_input`은 엔진 UI 버튼을 클릭하지 못했다. Run 시작/편성/강화/던전 나가기는 실제 클라이언트 UI 핸들러·RPC를 `maker_execute_script`로 호출했다. 플레이 이동·처치·Skill Drop E·SkillBar Z·상자 E는 Maker 키보드 입력과 실제 Play였다. UI 물리 클릭 검증은 별개로 남는다.

## 화면 증거

- [3_companions_lobby.png](3_companions_lobby.png): 로비 컬렉션의 3종 편성.
- [3_companions_formation.png](3_companions_formation.png): Run 시작 삼각 Formation.
- [3_companions_combat.png](3_companions_combat.png): 3마리와 Player의 일반 조우.
- [portal_after_companions.png](portal_after_companions.png): 포털 뒤 동일 3종 복구.
- [monster_level_enhance.png](monster_level_enhance.png): Lv2 달팽이와 정수 차감 후 강화 상태.
- [passive_companion_collection.png](passive_companion_collection.png): 버블링 동행·액티브 없음 표시.
- [world_skill_drop.png](world_skill_drop.png): 바닥 Skill Drop 상호작용 직전.
- [chest_heal.png](chest_heal.png): 상자 E 상호작용 직전(회복 결과는 로그·HP로 확인).

요청된 `own_skill_cast.png`, `boss_with_companions.png`는 시전/보스와 3종이 한 프레임에서 명확히 식별되는 캡처를 얻지 못하여 **제작하지 않았다**. 시전과 Boss Clear는 런타임 로그로 각각 확인됐지만 사진 증명과 구분한다.

## 잔여 검증

1. 강화 전후 동일 조건의 실제 동행 기본공격·고유 Skill 피해 차이, Player 공격·랜덤 Skill 무영향의 수치 계측.
2. 다양한 동시 적 배치에서 3마리 서로 다른 타겟 선택 화면/상태 계측.
3. Projectile/Dash/Buff/Debuff의 시전 로그를 넘어 실제 효과 판정, 3마리와 보스가 함께 보이는 화면.
4. 실제 독립 2–4인 클라이언트의 보상·편성·포털·보스 테스트.
5. UI 버튼의 실제 마우스/터치 클릭 경로.

따라서 **검증 완료로 선언하지 않는다**. Maker에서 자연 테이밍·중복·성장 정수·3종 Formation/전투·Portal/복귀·Boss Clear·저장·Player SkillBar 회귀는 확인됐지만 위 항목은 PARTIAL/BLOCKED다.
