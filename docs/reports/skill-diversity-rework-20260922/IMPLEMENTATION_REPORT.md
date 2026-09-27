# 스킬 다양성 개편 — 진행 및 검증 보고

기준 프로젝트: `D:/maplestory_levup`, 작업 브랜치 `codex/skill-diversity-rework-20260922`, 시작 HEAD `5bd7f4d`. 이 문서는 완료 선언이 아니다. 2026-09-23 Maker 연결 복구 후 Refresh/Build와 플레이어·몬스터 각 66종의 스크립트 QA를 재실행했다. Git commit/push는 하지 않았다.

## 1. 개편 목표

Mega Area의 랜덤 5슬롯 일회성 능력 구조를 보존하면서, 플레이어 획득 가능 액티브/방어 66종의 실제 공간 판정과 부가 효과를 분화한다.
HEAD의 SkillTable 112행과 현재 112행을 ID로 비교하면 기존 컬럼의 변화는 정확히 `description` 66행, `coefficient` 10행이다. 나머지 46개 스킬의 기존 컬럼과 66개 스킬의 RUID/ID/몬스터 연결 필드는 유지됐다. 새 Behavior 컬럼은 별도 추가했다.

## 2. 기준 프로젝트 상태

현재 데이터 기준 112개 스킬 정의 중 몬스터 연결 능력 101개, 그중 사용 가능한 액티브/방어 66개, 비활성 패시브 35개다. 연결되지 않은 레거시 `s_mon_snail` 1개는 이번 개편 대상이 아니다. 원래 실행 구조는 CENTER_DIRECT 44, PROJECTILE 12, DASH_STRIKE 7, SHIELD 3이었다. 개편 전 행별 원본 값은 `SKILL_BEFORE.csv`에 보존했다.

## 3. 66 Skill 전체 목록

`SKILL_REDESIGN_MATRIX.csv`와 `SKILL_AFTER.csv`에 66/66 행을 기록했다. 양쪽 파일은 SkillID·MonsterID·이름을 기준으로 대응한다.

## 4. 기존 다양성 문제

44종은 시전자 중심의 즉발 원형 판정으로 묶였다. 몬스터·스킬명·VFX가 달라도 위치와 방향 판단은 비슷했다. 12종 투사체도 착탄 역할이 크게 분화되지 않았다.

## 5. Redesign 원칙

이름·몬스터 정체성·기존 아이콘과 VFX 참조를 보존하고, 공통 Behavior와 필요한 소수의 제어 효과를 데이터로 지정했다. 66개의 SkillID별 일회성 분기 대신 공통 판정 함수를 사용한다. `SKILL_BEFORE_AFTER.csv`는 실제 수치·문구 변화를 행별로 보여준다. 지속 영역은 3틱 총 피해를 관리하기 위해 각 틱 계수를 기존의 약 1/3로, 확산 3발은 중첩 위험을 고려해 계수를 기존의 약 1/2로 설정했다. 이는 실제 피해 분포의 변경이며 최종 밸런스 확정은 아니다.

## 6. 공통 Behavior 구현

`CENTER_BURST` 8, `FRONT_CONE` 12, `LINE_STRIKE` 8, `DELAYED_BLAST` 7, `DAMAGE_ZONE` 9, `PROJECTILE` 2, `PROJECTILE_BLAST` 6, `PIERCING_PROJECTILE` 3, `SPREAD_PROJECTILE` 1, `DASH_STRIKE` 7, `SHIELD` 3이다. `GameData.mlua`가 SkillTable의 behavior/폭/지연/틱/간격/부가 효과/몬스터·보스 배율을 읽고, `PlayerAttack.mlua`와 `MonsterAttack.mlua`가 이를 실행한다. 지연·지속형의 타격 종료 전에는 몬스터 특수 시전 예약을 해제하지 않도록 했다.

## 7. 변경하지 않은 Skill

기본 역할을 보존한 7종 돌진과 3종 방어가 포함된다. 일부 단일 투사체도 그대로 유지했다. 상세 Keep/Change 판정과 근거는 Matrix에 있다.

## 8. 변경한 Skill

기존 중심 즉발 중 상당수를 전방/선형/지연/지속형으로 바꾸고, 12종 투사체를 단일·착탄 광역·관통·확산으로 분화했다. 20종에는 Slow/Weaken/Stun/Pull/Knockback 중 하나를 추가했다. 각 스킬의 변경 전후 계수·범위·툴팁은 비교 CSV에 있다.

## 9. VFX 재사용 방식

기존 `icon_ruid`, `effect_ruid`, `projectile_ruid`, `layer_ruids`는 변경하지 않았다. 생성 스크립트가 66개 모두의 원본 참조와 현재 참조가 바이트 문자열 기준으로 같음을 검증한다. 실행 경로에서 사용 위치/방향을 바꿨으나 실제 화면 품질·크롭 검수는 별도다.

## 10. Control/Status 규칙

Slow/Stun/Weaken/Impulse는 RoomMonster 공통 API로, 몬스터의 플레이어 대상 제어는 PlayerDash 클라이언트 표현과 서버 발동 경로로 분리했다. 보스에는 부가 제어량/시간 0.35배를 적용하며 위치 강제 이동은 적용하지 않는다. 일반 몬스터가 사용하는 제어에는 0.6배를 적용한다. 각 효과의 종료 타이머는 독립 serial로 관리한다. Stun은 몬스터 평타·특수 시전과 플레이어 서버 공격 요청도 제한하며, 거부된 플레이어 요청에서는 랜덤 슬롯을 소비하지 않는다.

Maker map05 머쉬맘의 공통 보스 제어 어댑터에서 Slow/Stun/Weaken 감소와 Knockback/Pull 위치 면역을 확인했다(BOSS_CONTROL_RUNTIME_20260923.md). PlayerDash의 클라이언트 이동·제어 복구 수정 후 평지 돌진, Knockback, Stun 키 입력을 실제 확인했다(TERRAIN_MOVEMENT_RUNTIME_20260923.md). 보스에게 실제 플레이어 스킬을 적중시키는 통합 전투와 멀티 대상 전달은 아직 NOT_RUN이다.

## 11. Player Random SkillBar 호환

기존 5초 공급과 슬롯 소비의 게임 코드는 변경하지 않았다. 최종 Maker의 66종 PlayerAttack.UseSkill 전수 검사에서 각 스킬을 두 번 실행해 각각의 토큰 소비와 SkillReadyAt 불변을 확인했다. 마지막 검사 결과는 PLAYER_SKILL_RUNTIME.csv 및 PLAYER_SKILL_RUNTIME_FINAL_20260923.csv다. 이 검사는 물리 이동의 66종 전수 인증이나 VFX 육안 승인이 아니다. 검사용 클라이언트 위치를 고정해 포털 이동이 측정에 섞이지 않게 했다.

node docs/tools/verify-skill-diversity-rework.cjs 결과는 PASS_STATIC(112 Skill, 103 Monster, 대상 66, Behavior 11). 이 정적 검사는 Maker Build/Runtime을 대신하지 않는다.

## 12. MONSTER_SKILL 호환

MONSTER_SKILL 시전자는 대상 플레이어 방향으로 전방/선형/투사체를 사용하고, 지연·지속형은 시전 시점의 위치를 기준으로 한다. 초기 QA에서 다른 몬스터의 평타와 특수 시전이 피해 결과에 끼어 거짓 양성이 발생해, 다른 몬스터·리스폰을 격리한 후 실제 MonsterAttack.CastSkill 66종을 다시 실행했다. 최종 66/66은 MONSTER_SKILL_RUNTIME.csv 및 MONSTER_SKILL_RUNTIME_FINAL_20260923.csv에 기록했다. 해당 검사에서는 실제 시전 반환값과 피해 또는 실드를 확인했다. 자연 AI 선택·부가 제어 전수·지형·멀티는 포함하지 않는다. 앞선 실패 실험은 삭제하지 않고 날짜별 CSV와 본문에 구분해 보존한다.

## 13. Tooltip 변경

66종 `description`을 기능/방향/주요 부가 효과와 맞춰 작성했다. `TOOLTIP_AUDIT.csv`의 일치 판정은 데이터·코드 정적 확인이다. 2026-09-23 Maker Play에서 `EquipPanel:SetOpen(true)`→`ClickRow(1)`→`SetOpen(false)`를 실행하고 실제 화면을 캡처했다. Run 보유 능력 상세에 이름·제공 몬스터·유형·새 설명이 표시됐고 쿨다운 문구는 보이지 않았으며 닫은 뒤 패널/마스크가 사라졌다. 단, 66종의 모든 개별 UI 행을 육안 검수한 것은 아니다.

## 14. Player 66 Skill Runtime

2026-09-23 21:40:16~21:42:53 Maker NORMAL Run의 전용 인스턴스 map006에서 투사체 벽 가림 수정 이후 실제 PlayerAttack.UseSkill 66종을 다시 검사했다. 최종 로그: [SkillRework66] DONE observed=66 pass=66 fail=0 notRun=0 harnessOk=true cleanupOk=true seconds=159.232. 이 구간의 Error 로그는 0건이다. 검사 결과 행은 기존 PLAYER_SKILL_RUNTIME.csv 및 PLAYER_SKILL_RUNTIME_FINAL_20260923.csv와 동일했다. 검사는 주 표적 HP 변화/실드, 부가 효과, 두 번의 발동·슬롯 토큰 소비, 플레이어 쿨다운 비적용을 확인한다.

검사 도중 발견한 두 가지를 별도 수정했다. 실제 돌진의 타격점을 클라이언트 이동 RPC 이후 계산해 판정이 약 1.9유닛 앞서는 게임 경쟁 상태를 PlayerAttack.DashSkill의 출발점 선캡처로 고쳤다. QA에서는 ResetSkillControls가 추적 AI를 다시 켜는 점, 광역 PULL 정중앙 대상은 방향 벡터가 0인 점을 반영해 표적을 고정하고 중심 외곽 표적을 추가했다. 앞선 64/66·65/66 실행은 원인 분석 기록이지 최종 PASS가 아니다. VFX 행의 ACTUAL_PATH_NOT_VISUAL_CERTIFICATION은 실제 실행 경로를 뜻할 뿐 육안 품질 승인이나 새 지형 전수 PASS가 아니다.

## 15. Monster Mode Runtime

2026-09-23 21:09:11~21:10:06 Maker MONSTER_SKILL Run에서 MonsterAttack.CastSkill을 66종 실제 호출했다. 기록된 로그: [MonsterSkillRework66] DONE observed=66 pass=66 fail=0 notRun=0 harnessOk=true cleanupOk=true seconds=57.244. 해당 구간 Error 0건. 이는 **투사체 벽 가림 수정 전** 소스에 대한 66/66 결과다. 최초 재검사 63/66은 다른 몬스터의 평타·특수 시전이 HP 변화에 섞인 검사 결함이었다. 수정한 QA는 나머지 몬스터와 리스폰을 격리하고 시전 반환값도 함께 검사한다. 벽 가림 수정 후 대표 몬스터 투사체의 막힌/열린 경로는 별도 Maker Play로 검증했으나, 수정 후 Monster 66종 전수 재실행은 NOT_RUN이다. 자연 AI·모든 부가 제어의 화면 체감·멀티·VFX 육안 검사는 이 수치에 포함되지 않는다.

## 16. Random Battle Sample

Maker에서 서로 다른 Seed의 NORMAL 3회와 MONSTER_SKILL 3회의 시작·이동·포털·첫 교전 샘플을 확보했다(NATURAL_BATTLE_SAMPLES_20260923.csv). 이는 돌진 좌표 경쟁 상태와 PlayerDash 클라이언트 이동을 고치기 **전**의 샘플이다. 여섯 번 모두 완주가 아니며, 대부분 사용 시점에는 살아 있는 적이 없어 hits=0이었다. 최종 코드로 NORMAL 3 Run + MONSTER_SKILL 3 Run의 자연 전투 완주와 사용감은 NOT_RUN이다. 따라서 재미·판독성·Utility 가치를 확정하지 않는다.

## 17. 다양성 Before / After

`DIVERSITY_BEFORE_AFTER.md` 참조. 시전자 중심 즉발은 44→8, Primary 구조는 4→11, 최대 동일 구조 그룹은 44→12다. 이 숫자만으로 최종 재미를 판정하지 않는다. 현재 정적 기준 잠정 평가는 **일부 편중**이다.

## 18. 기존 시스템 Regression

첫 능력 100%·이후 10%, OwnedSkillPool, 5초 공급, 슬롯 소비 코드는 직접 변경하지 않았다. 이전 첫 교전 6회에서 첫 획득·5초 공급·소비를 관찰했으나 최종 돌진 수정 후 전체 자연 Run 회귀는 NOT_RUN이다. 돌진 물리 이동을 바로잡은 뒤 격리하지 않은 QA에서 연속 돌진이 활성 포털에 닿아 map006→map001 전환이 발생했다. 포털 구조는 변경하지 않았으며, 의도된 접촉과 오발 판정은 남아 있다. Potion·Respawn·Boss·Party·Dungeon Leave의 최종 코드 통합 회귀도 완료로 기록하지 않는다.

## 19. Build

마지막 게임 코드 수정(투사체 벽 가림) 후 Maker Refresh와 Build Console에서 Error 0건, 기존 모델 Warning 2건(마노 MovementComponent.InputSpeed, 보우마스터 MonsterAttack.AvatarAttackPlayRate)을 확인했다(2026-09-23 21:33:53). 빌드에는 LIA 정보 진단 10건이 남아 있다. Player 66종 QA는 이 소스 상태에서 재실행했다. Monster 66종 QA의 보관 결과는 수정 이전의 결과이므로 최종 소스 전체 회귀 PASS라고 쓰지 않는다. git diff --check와 정적 검증 스크립트도 통과했다.

## 20. Runtime Error

투사체 벽 가림 수정 후 Player 66종 구간의 Maker normal Error는 0건이었다. Monster 66종 전수 구간도 당시 Error 0건이었으나 수정 전 소스였다. 이전 임시 MakerScript의 nil 출력 오류 2건은 게임 .mlua와 분리한다. 별도 map141 지형 실험에서 테스트용 직접 텔레포트로 maptown으로 옮기는 도중 [LEA-3015] CannotLoad 2건이 발생했다. 따라서 모든 Maker 세션을 합쳐 Runtime Error 0이라고 주장하지 않는다. 이후 별도 Maker NORMAL Run에서 map001→map006 실제 포털 전환과 예약 Zone 피해 중단을 오류 0건으로 확인했다. 앞선 강제 텔레포트 오류는 별도 테스트 방법의 기록으로 유지한다.

## 21. FAIL

기록된 66+66 격리 QA에서 실패 행은 0이나 Monster 66종은 벽 가림 수정 전 결과다. 전체 완료 조건은 미충족이다. map141 벽 근처 돌진에서 실제 플레이어 도착 y=3.99와 서버 타격 중심 y=3.6의 차이(약 0.39유닛)가 남았고, 강제 텔레포트 지형 실험은 [LEA-3015] 2건을 냈다. 정상 포털의 Zone 예약 피해 중단과 투사체의 벽 뒤 피해 차단은 플레이어·몬스터 대표 사례에서 확인했다. 돌진의 포털 오발 여부와 Zone 이펙트 잔류는 아직 확정하지 못했다(TERRAIN_MOVEMENT_RUNTIME_20260923.md). 이 대표 사례들을 SkillID 지형 전수 PASS로 대체하지 않는다.

## 22. NOT_RUN

최종 코드 기준 미실행: 수정 후 Monster 66종 전수 회귀, NORMAL 3회 + MONSTER_SKILL 3회 자연 Run 완주 및 실제 전투 체감, 모든 VFX의 화면 판독·아이콘과의 일치, 투사체 12종 전체의 벽·폭발·관통 지형 검사, 돌진 7종의 벽·포털·경계·끼임 전수, Zone 전환 후 이펙트 개체 육안 정리, 보스 통합 적중과 방어 피감 실측, Skill Window 66종 개별 시각 검사, Potion·Respawn·Party·Dungeon Leave 통합 회귀, 2~4인 동시 스킬 실행. 대표 투사체의 벽 가림, 대표 1종 Skill Window 열기/선택/닫기와 보스 공통 제어 어댑터는 별도 확인했지만 전수 결과로 확장하지 않는다.

## 23. BLOCKED

2026-09-24 현재 이 Codex 세션의 도구 목록에는 Maker Play/로그/스크립트 호출이 제공되지 않는다. 기존 Maker 실행 로그는 보존하지만, 이 세션에서 Monster 66종 재실행이나 남은 자연 Run을 완료했다고 주장할 수 없다. 재연결 전에는 해당 런타임 검증만 **BLOCKED_SESSION_TOOL**로 구분한다. 2~4인 독립 클라이언트 실행 가능 여부는 아직 검토·실행하지 않았으므로 환경상 불가능하다고 단정하지 않고 NOT_RUN으로 둔다.

## 24. 실제 수정 파일

게임 파일: RootDesk/MyDesk/GameData/SkillTable.csv, RootDesk/MyDesk/GameData/GameData.mlua, RootDesk/MyDesk/PlayerAttack.mlua, RootDesk/MyDesk/MonsterAttack.mlua, RootDesk/MyDesk/Combat/RoomMonster.mlua, RootDesk/MyDesk/Player/PlayerDash.mlua. 분석/QA: docs/tools/build-skill-diversity-rework.cjs, docs/tools/verify-skill-diversity-rework.cjs, 이 폴더의 CSV·MD·QA Lua. 기존 ui/AreaSelect.ui, ui/PlayerHud.ui, map/map01.map의 다른 변경은 보존했고 이번 스킬 다양성 작업으로 집계하지 않는다. map/map141.map은 Maker가 runSpawn 기본값을 물질화해 수정 상태가 되었으며 스킬 구현 성과로 집계하지 않고 보존한다. Git commit/push는 하지 않았다.
