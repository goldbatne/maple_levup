# 로그라이트 개편 완료 감사 — 2026-09-21

> HISTORICAL / 고정 슬롯 단계의 검사 기록. 이후 Mega Area 전환으로 획득·공급·소비·쿨다운·리스폰 규칙이 바뀌었다. 아래 PASS를 현행 방식의 재검증 결과로 사용하지 않는다. 현행 기준: [CURRENT_GAME_STATE.md](../../CURRENT_GAME_STATE.md). 과거 증거와 결론 본문은 보존한다.

## 판정 기준

- 최종 실행 프로젝트: `D:\maplestory_levup`
- 브랜치/기준 HEAD: `codex/art-packages-cleanup-20260915` / `2eb7498eda8f53440648ef6107d6c933ba55d5c6`
- 스킬 분석 baseline: `skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`
- 작업 트리: 기존 미커밋 변경을 보존한 dirty 상태. reset/revert/일괄 commit을 수행하지 않았다.
- 판정 원칙: 코드 존재는 Runtime PASS가 아니다. Maker 실행, 서버/클라이언트 로그, 실제 PlayerAttack·이동·포탈·사망 이벤트를 분리해 기록했다.

상세 23항목 표는 `REQUIREMENT_MATRIX.csv`, Area 표는 `AREA_RUNTIME_RESULTS.csv`, 66스킬 표는 `SKILL_RUNTIME_FINAL.csv`에 있다.

## [2번 전체 요구사항 완료 매트릭스]

최종 집계는 `PASS_RUNTIME 11`, `PASS_STATIC 10`, `PARTIAL 2`다. PARTIAL은 (1) 실제 2~4인 독립 클라이언트가 없어 협동 Runtime을 수행하지 못한 항목, (2) 현재 맵에 내부 collidable wall geometry가 전혀 없어 벽 관통/충돌을 실제 지형에서 판정할 수 없는 스킬 호환 항목이다. 상세 근거와 이전/최종 상태는 `REQUIREMENT_MATRIX.csv`에 있다.

## [이번에 실제 수정한 파일]

핵심 개편 및 이번 완료 감사에서 직접 수정한 런타임 파일:

- `RootDesk/MyDesk/GameData/GameData.mlua` — Run 상태, 서버 권한, 고정 슬롯/쿨다운, 생성/검증, Objective, 파티 상태.
- `RootDesk/MyDesk/Room/RoomSpawner.mlua` — 결정적 방별 RNG, 안전 스폰, Encounter 일회성/보스 규칙.
- `RootDesk/MyDesk/Room/RoomPortal.mlua` — Run 전환과 실제 도착 좌표 기반 spectator 재합류.
- `RootDesk/MyDesk/Combat/SkillCastEffect.mlua` — VFX layer 적용 nil 오류 수정.
- `RootDesk/MyDesk/PlayerAttack.mlua` — Run 참여/생존/관전 상태 사용 차단과 고정 슬롯 쿨다운 경로.
- `RootDesk/MyDesk/Progress/PlayerCollection.mlua` — Run 확정 능력 지급, 중복 강화 제거, RPG 성장 배율 격리.
- `RootDesk/MyDesk/Save/PlayerDBManager.mlua` — Roguelite 영구 기록 namespace 및 안전 파서.
- `RootDesk/MyDesk/UI/EquipPanel.mlua` — Run 중 레거시 장착 기능 비활성.
- `RootDesk/MyDesk/UI/TraitPanel.mlua` — 신규 모드에서 root/button Disable 및 숨김.
- `RootDesk/MyDesk/Inventory/PlayerInventory.mlua`, `RootDesk/MyDesk/Room/HeroNpc.mlua`, `RootDesk/MyDesk/Room/TownGate.mlua`, `RootDesk/MyDesk/Room/GoddessNpc.mlua`, `RootDesk/MyDesk/Room/RebirthNpc.mlua` — 레거시 진입점 Run guard/비활성.
- `map/map11.map`, `map/map12.map`, `map/map13.map`, `map/map16.map`, `map/map17.map` — Maker Save로 누락 instance metadata 정합화.

이 목록은 전체 dirty worktree 목록이 아니라 이번 개편/감사와 직접 연결된 파일만 적은 것이다. 무관한 사용자 변경은 건드리지 않았다.

## [Area 00~20 Runtime 결과]

- Area 00: 실제 fresh solo Run에서 이동, 전투, reach_exit, clear, maptown 복귀, reset 확인.
- Area 01: 실제 room 전환 시 pending 정리, PlayerHit 사망에 의한 FAIL, maptown 복귀, 다음 Run 초기화 확인.
- Area 02~05 및 07~20: 각 Area seed 2026으로 실제 InstanceRoom 생성, BFS 기반 실제 `MovementComponent` 이동, 실제 포탈 전환, 몬스터/보스 스폰, Objective, Clear, maptown 복귀, reset 확인. 각 로그의 Error 수는 0.
- Area 06: 예약 결번이므로 N/A.
- 주의: Area 02~20 전수 주행은 구조 검증을 빠르게 끝내기 위해 서버 HP 회복 보조를 사용했다. 따라서 `완주 가능 구조`는 Runtime PASS지만 `자연 밸런스 완주`를 인증하지 않는다.
- Area 05의 직선 이동 QA가 물 타일에서 정체된 기록은 실제 맵 실패가 아니라 QA 경로 실패다. 타일 BFS로 재검증해 Clear했다.

## [Seed 검증 결과]

- 전체 20 Area에 고정 seed `2026`과 Area별 추가 seed 1개, 총 40건.
- Start/Goal, main path, branch budget, final room, graph 연결, template/role/encounter/objective가 동일 입력에서 반복 생성될 때 일치했다.
- 맵 생성 RNG와 전투 RNG는 분리되어 전투 호출 전후 layout이 변하지 않았다.
- 생성 retry는 상한이 있고, 실패 시 결정적 fallback DFS를 사용한다. 무한 retry는 확인되지 않았다.
- 원본 증빙: `seed-v2-reproduction-final.json`.

## [66 Skill Runtime 결과]

- PASS: 66
- FAIL: 0
- 수정: 공통 VFX layer 적용 경로 1건(`SkillCastEffect.mlua`) 수정. 스킬 고유 효과/계수/범위/연결은 변경하지 않았다.
- 남은 NOT_RUN: 스킬 발동 자체는 0. 다만 각 VFX의 모든 프레임을 사람이 육안 승인하는 아트 검수는 이번 Runtime 기능 감사에 포함하지 않았다.

각 SkillID는 실제 `PlayerAttack` 경로로 두 차례 이상 발동되었다. 첫 발동 성공, 즉시 재사용 차단, cooldown 종료 후 재사용, 슬롯 유지, 실제 피해 또는 방어 적용, VFX dispatch를 로그로 확인했다. 원본 로그는 `runtime-skills-v2.json`, 결과표는 `SKILL_RUNTIME_FINAL.csv`다.

지형 호환 한계: 현재 163개 맵과 Area 00 Runtime 표본에서 내부 collidable RectTile 및 독립 wall collider가 0개다. 따라서 투사체/돌진/AoE의 `내부 벽` 상호작용은 현재 콘텐츠에서는 재현할 벽이 없어 `NO_COLLIDABLE_WALL`이다. 문·포탈·통로 이동은 실제 검증했지만, 미래에 collidable wall 청크를 추가할 때 별도 회귀가 필요하다. 이 제한 때문에 스킬을 일괄 수정하지 않았다.

## [고정 5슬롯 예외 결과]

- 0/1/4/5개 상태 표시 및 서버 상태 PASS.
- 빈 슬롯 첫 등록 PASS.
- Full 상태에서 pending 생성, 기존 스킬 교체, 획득 포기 PASS.
- 동일 SkillID 장착/동일 pending 중복 차단 PASS.
- 빠른 연속 처치 시 FIFO pending queue 유지 PASS.
- pending 상태의 실제 room 전환, Run Clear, Run Fail에서 정리 PASS.
- 스킬 사용 후 슬롯 유지 PASS.
- 자동 덮어쓰기, 슬롯 중복, 랜덤 공급, 사용 후 소멸은 관찰되지 않았다.

## [Cooldown 결과]

- 현재 플레이어 사용 가능 66개 모두 양수 cooldown 데이터 보유. 누락/0건 0.
- 66개 모두 실제 첫 사용, 즉시 재사용 거절, 만료 후 재사용 성공.
- 슬롯 위치 이동, 교체, 포기, 재획득으로 cooldown이 초기화되지 않았다.
- 정상 발동 후 대상이 빗나갈 수 있어도 cooldown은 유지되고, 서버가 거절한 요청은 cooldown을 소비하지 않는다.

## [Random SkillBar 제거 결과]

빈 슬롯이 있는 상태로 6.2초 이상 관찰했으며 5초 자동 공급, 랜덤 추첨, 긴급 공급, 첫 스킬 특례, use-token 생성이 없었다. 스킬 사용 뒤 슬롯은 유지됐다. 레거시 데이터/코드는 보존되지만 신규 Run 실행 경로에는 진입하지 않았다.

## [Objective 결과]

실제로 구현·검증한 ObjectiveType은 두 가지다.

- `reach_exit`: Area 00/01. final room 도달/출구 진행 경로.
- `defeat_final_guardian`: Area 02~20(06 제외). 최종 방 보스 사망으로 목표 완료.

장치 활성화, 열쇠, 봉인 제거는 현재 실행 구현 완료로 주장하지 않는다. enum/기획 예시만으로 PASS 처리하지 않았다.

## [Encounter/Respawn 결과]

- 일반 room encounter와 final guardian spawn을 실제 확인.
- 한 room에서 기존 몬스터 4개를 실제 기본공격으로 처치한 뒤 5초 후 alive=0, `spawnedOnce=true`, spawnIndex 불변을 확인했다.
- 동일 몬스터의 동일 능력은 한 Run에서 재지급되지 않았다.
- Clear한 room의 무한 respawn은 관찰되지 않았다.
- 안전 후보 타일에서 스폰하며 플레이어/포탈/벽 셀 회피 검사를 사용한다. 현재 내부 collidable wall 자체는 없다.

## [RPG/성장 비활성 결과]

실제 Runtime에서 Level 200, STR 999, DEX 888, INT 777, LUK 666으로 일시 변경해도 Run 기본값은 HP 1000, ATK 35, MATK 35, DEF 10, LUK 0, MoveSpeed 2.4, AttackInterval 1.0으로 동일했다. Run 중 EXP 추가는 차단됐다. 장비 점수 25의 장비를 임시 장착해도 전투 기본 수치가 변하지 않았다. 테스트 직후 값을 복구했다.

따라서 Level/EXP/Job/Rebirth/직접 스탯/Equipment Growth/Duplicate Growth/Trait/Taming Companion은 신규 Run 전투력에 합산되지 않는다.

## [HUD/UI 결과]

- 필요한 HUD: HP, 고정 5슬롯, 단축키, cooldown, Objective/진행도 확인.
- 획득 UI: Monster/Skill 정보, 아이콘, cooldown, 교체/포기 경로 확인.
- Run 중 레거시 장착 기능은 비활성.
- Trait root와 button은 실제 Client Runtime에서 Enable=false, Visible=false 확인.
- Goddess/Rebirth NPC는 roguelite mode에서 TouchEvent 자체를 등록하지 않는다.
- 스탯/장비성장/전직/환생/Trait/테이밍/랜덤 공급/PvP 진입 경로는 Run 중 숨김 또는 서버 guard 처리.
- 실제 협동 참가자 HUD는 독립 클라이언트 부재로 Runtime 미검증.

## [Save/Reset 결과]

- Roguelite 영구 기록은 `MakerTest_RoguelitePermanentV1` 테스트 namespace와 별도 schema/파서를 사용했다.
- 합성 save 14종(누락, 잘못된 타입, 레거시 형태 포함)을 실제 Runtime 파서로 검사해 14/14 PASS, 외부 storage write 0.
- Clear/Fail 뒤 HP, slots, cooldown, pending, objective, generated room state가 다음 Run에 넘어가지 않았다.
- 영구 discovered ability/monster/Area clear 기록과 Run 전투 상태를 분리했다.
- 기존 RPG/M2 데이터 삭제나 reset은 수행하지 않았다.

## [Server Authority 결과]

서버가 Run participant, seed/layout, spawn/death, reward eligibility, slot equip/replace, skill/cooldown/damage, objective, transition, clear/fail을 확정한다. 실제 Client negative probe로 잘못된 slot 99 사용, stale pending revision, invalid swap, instance 내부 forged Run start를 보냈고 서버는 모두 거절했으며 현재 Run 상태가 변하지 않았다.

## [1P 결과]

PASS_RUNTIME. 신규 상태/기존 저장 상태, Clear, Fail, Clear/Fail 후 재시작, 초기화, 고정 슬롯, cooldown, Objective, encounter, save 분리를 실제 Maker 단일 Client에서 검증했다.

## [2P 결과]

BLOCKED_RUNTIME_MULTIPLAYER. Maker MCP가 노출한 실제 Client context는 1개뿐이었다. 서버식 HP scale 계산과 협동 상태 머신은 static/server simulation으로 검증했다.

## [3P 결과]

BLOCKED_RUNTIME_MULTIPLAYER. 사유는 2P와 동일하다.

## [4P 결과]

BLOCKED_RUNTIME_MULTIPLAYER. 사유는 2P와 동일하다.

## [PASS_RUNTIME]

- Area 00, 02~20(06 제외) 시작/생성/이동/전투/목표/Clear/복귀/초기화.
- Area 01 room 전환/pending 정리/Fail/복귀/재시작.
- 66개 스킬 발동/판정/VFX dispatch/cooldown/슬롯 유지.
- 고정 5슬롯 예외와 pending 교체/포기.
- RPG 성장·장비 격리, 저장 파서, one-shot encounter, legacy Trait/NPC 비활성.
- Solo 핵심 regression.

## [PASS_STATIC]

- Seed 40건 재현, generator validator/fallback/retry bound.
- 163개 map 분류와 20 Area pool 연결.
- 서버 권한 코드 감사, 협동 participant/rejoin/leave 상태, HP scale 함수.
- 30초 강제 온보딩 로직 부재.
- 두 가지 ObjectiveType 구현 범위.

## [FAIL]

- 최종 Build Error: 0.
- 최종 Runtime Error: 0.
- 기능 FAIL: 0.
- 중간에 발견한 `SkillCastEffect` nil Apply 오류와 map metadata 누락은 수정 후 동일 경로를 재검증했다.

## [BLOCKED]

- 실제 2~4인 독립 멀티클라이언트 Runtime.
- 실제 멀티에서 동일 layout/objective/monster 동기화, 개인 능력 획득, 관전·안전지점 재합류, 재접속·이탈 유예.
- 내부 collidable wall이 있는 새 지형에서의 투사체/돌진/AoE 벽 상호작용. 현재 콘텐츠에는 해당 wall geometry가 없다.

## [NOT_RUN]

- 플레이어 스킬 66개의 기능 발동 기준 NOT_RUN은 0.
- Area 02~20(06 제외) Runtime 구조 검증 기준 NOT_RUN은 0.
- 2~4인 협동은 단순 NOT_RUN이 아니라 환경 제한이 확인된 BLOCKED다.
- 66개 VFX 전체 프레임의 사람 육안 미술 승인은 수행하지 않았다.

## [남은 실제 미완료]

1. 실제 2~4 독립 클라이언트 협동 Runtime.
2. 향후 내부 collidable wall 템플릿을 추가할 경우 projectile/rush/AoE 지형 회귀.
3. 자연 밸런스 조건으로 Area 02~20 장시간 완주 측정. 이번 전수 주행은 구조 검증용 HP assist를 사용했다.
4. 모든 VFX 프레임의 수동 시각 승인. 기능/VFX 호출은 확인했으나 아트 품질 전수검수는 별도다.

## Build 및 기존 Warning

최종 Play 종료 후 Maker Refresh는 `status=ok`로 완료됐다. 최종 Maker Build Console은 Error 0이다. 최신 build 시각의 동적 타입 관련 Info 3건이 있고, 기존 Warning 2건(`mano MovementComponent.InputSpeed`, `bowmaster MonsterAttack.AvatarAttackPlayRate`)은 개편 전 모델 warning으로 현재 Run 오류를 만들지 않았다. 이번 범위에서 억지로 수정하지 않았다.

## 결론

2번 프롬프트의 현재 단일 Maker 환경에서 수행 가능한 Solo/Area/Skill/UI/Save 작업은 완료했다. 실제 멀티클라이언트 Runtime은 환경 제약으로 BLOCKED다. 또한 현재 콘텐츠에 내부 collidable wall geometry가 없어 해당 벽 지형 스킬 호환은 미래 청크 추가 시 별도 검증이 필요하다. 따라서 `모든 요구가 무조건 완료`라고 표현하지 않고, 위 두 제한을 명시한 상태로 완료 판정을 남긴다.
