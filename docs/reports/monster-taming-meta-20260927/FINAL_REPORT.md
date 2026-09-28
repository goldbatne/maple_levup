# 몬스터 수집·육성 + Run 동행 전투 구현 결과

분석·구현 기준: `D:/maplestory_levup`, 2026-09-27 KST. 작업 전 안정 지점 `0335fdd` (`codex/monster-taming-meta-20260927`)을 커밋했다. 이후 구현 변경은 **미커밋**이며 push/PR은 하지 않았다. Maker 테스트 저장은 `MakerTest_RoguelitePermanentV1`으로 실제 계정 저장과 분리된다.

## 현재 연결

- MonsterTable 103종 중 명시적 `drop_skill_id`가 실제 SkillTable과 연결된 101종이 수집 대상이다. 히어로·보우마스터 2종은 제외된다. 101종 모두 RoomTable에 최소 한 행이 있다. 이 중 플레이어 액티브/방어 66종만 World Skill Drop을 통해 영구 Skill Collection에 등록·동행 장착할 수 있다. 패시브 연결 몬스터도 테이밍·동행은 가능하나 해당 패시브를 신규 전투 스킬로 만들지 않았다.
- 처치 참가 반경 내 각 플레이어가 독립적으로 첫 테이밍 10%, 중복 3%를 판정한다. 최대 ★5이며 천장은 없다. 기존 `TamedMonsters`가 단계의 원장이고 `OwnedSkills`는 레거시 미러다.
- 동행 성장 초안은 GameBalance에 분리했다: 기본 HP 250/공격 20, ★ 한 단계당 HP +5%, 기본 공격 +4%, 장착 스킬 피해 +3%. 3슬롯 장착은 영구 기록이고 플레이어의 Random 5 Slot과 무관하다. 동행 선택은 로비에서만 가능하다.
- 동행은 RectTile 물리 위치 API로 따라가며, 근처 적에 기본 공격을 하고 기존 SkillTable/Icon/VFX에 연결된 3개 능력을 역할 조건에 따라 사용한다. 적에게 피격돼 HP가 0이면 해당 방에서 재소환하지 않고 안전한 방 전환까지 기다린다. 몬스터 피해 원장은 소유 플레이어 ID에 귀속한다. 플레이어의 직접 스킬/데미지는 영구 ★ 보정을 받지 않는다.
- Rogue 전용 영구 저장 schema 2에 `tamed_monsters`, `permanent_skills`, `monster_loadouts`, `selected_companion`을 추가했다. 기존 schema 1의 발견/클리어 기록을 읽으며 기존 RPG/M2 저장 키는 쓰지 않는다. 과거 M2 계정의 테이밍 수를 Rogue 영구 컬렉션으로 자동 이관하는 정책은 이번에 추가하지 않았다.

## Maker 실제 확인

| # | 항목 | 결과 | 근거/한계 |
|---|---|---|---|
| 1 | 미획득 몬스터 | PASS_STATIC_ONLY | 신규 테스트 저장 `m_snail=0` 로그; 잠금 그리드 렌더 경로 |
| 2–3 | 자연 첫 테이밍·등록 | PASS_RUNTIME | `m_axe_stump` 첫 획득 roll 0.01908 < 0.10; 재진입 시 컬렉션 2/101 |
| 4–5 | 중복·성장 | PARTIAL | Maker 서버 QA에서 `m_axe_stump` ★1의 3% 판정을 실제 함수로 12회 실행해 ★2 달성·저장 확인. 자연 처치 중복 성공은 NOT_RUN. 별도 `m_snail` ★2 주입으로 HP 263, 성장/저장/표시 확인 |
| 6–7 | Skill Drop·영구 스킬 | PASS_RUNTIME | 실제 E 상호작용 `s_mon_axe_stump` 획득; 영구 원장=1, Run 풀=1 |
| 8–10 | 로비·3슬롯·동행 | PASS_RUNTIME/PARTIAL_UI | 서버 요청으로 3개 장착·동행 설정, 저장/재접속 확인. 실제 UI 버튼 포인터 클릭은 NOT_RUN |
| 11–14 | 생성·따라가기·기본공격·3스킬 | PASS_RUNTIME | map001→map002, 추적 위치차 0.8, Basic/LINE_STRIKE/SHIELD/DASH_STRIKE 서버 로그 |
| 15 | 플레이어 Random 5 Slot | PASS_RUNTIME | 드롭 획득 후 5초 공급으로 동일 스킬 5칸, Z 시전 후 한 칸 소비/재공급 로그 |
| 16 | 동행 Kill 보상 | PASS_STATIC_ONLY | 피해 owner 매핑과 근처 참가자 보상 경로 확인. 플레이어 공격을 배제한 독립 막타 실험은 NOT_RUN |
| 17 | Portal 이동 | PASS_RUNTIME | r_001→r_002 실제 이동 후 이전 동행 정리·새 방 1마리 생성 |
| 18 | Boss | PASS_RUNTIME | map05 버섯맘 HUD, 동행 공격 로그 뒤 `MegaBossClear` 확인. 동행 단독 DPS 분리는 NOT_RUN |
| 19–21 | Run 종료·영구/임시 경계 | PASS_RUNTIME | ABANDONED→maptown, 동행 없음, Run OwnedSkillPool=nil, ★/영구 스킬/Loadout/동행 선택 유지 |

마지막 Maker Refresh/Build: **Error 0, Warning 4**(기존 모델/컴포넌트 경고). 마지막 Play 세션에서 로비 저장 재로딩까지 확인했고 Runtime Error **0**. 이전 QA 스크립트의 `Entity:IsValid()` 호출 오류는 테스트 코드 오류였고 게임 코드가 아니며, 수정 후 마지막 실행에서는 재발하지 않았다.

## 남은 검증

- 실제 2–4개 독립 Maker 클라이언트 실행은 이 환경에서 제공되지 않아 **BLOCKED_RUNTIME_MULTIPLAYER**. OwnerUserId·각 플레이어의 Loadout 읽기·Run 참가자 판정은 정적 확인만 했다.
- 101종의 자연 테이밍, 66종의 모든 동행 장착 스킬 AI, 자연 처치에서의 중복 성공, 모든 버튼의 포인터 조작, 동행만으로 Boss 처치는 **NOT_RUN**. 기존 Player/MONSTER_SKILL 66 경로는 이번 작업에서 수정하지 않았지만 전체 재실행 PASS라고 주장하지 않는다.
- 전투 수치와 AI 역할별 조건은 초안이다. 현재 관찰만으로 5 Mega Area 전체 밸런스나 실서비스 멀티 안정성을 확정하지 않는다.

## 변경 파일과 근거

스크립트: `PlayerCollection.mlua`, `CompanionCombat.mlua`(+Maker 생성 codeblock), `PlayerDBManager.mlua`, `SavePermanentData.mlua`, `SkillDropManager.mlua`, `MonsterAttack.mlua`, `GameData.mlua`, `EquipPanel.mlua`, `SkillBar.mlua`, `TraitPanel.mlua`, `StatPanel.mlua`, `InventoryPanel.mlua`.

모델·데이터: `CompanionVisual.model`(ModelBuilder), 두 GameBalance CSV 사본. Mega Area, Portal, 기존 66 SkillTable/VFX, Skill Drop 확률과 60초, Player Random 5 Slot의 기존 구현은 변경하지 않았다.

증거: [수집 화면](ui_lobby.png), [정리된 로비](lobby_clean.png), [전투 동행](companion_run.png), [보스 방](boss_run.png). 상세 원장은 같은 폴더의 6개 CSV와 `UI_AUDIT.md`를 참조한다.
