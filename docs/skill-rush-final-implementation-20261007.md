# SKILL RUSH FINAL IMPLEMENTATION REPORT

검증일: 2026-10-07. 기존 작업 디렉터리에서 구현했으며 worktree·커밋·PR은 만들지 않았다.

**결론: 핵심 기능 구현 및 Maker 단일 플레이 검증 완료. 제출 전 최종 승인에는 독립 2인 접속, 실제 모바일 터치, 초반 획득 빈도 추가 플레이 검수가 남아 있다.**

## 1. 변경 파일

- `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`: 서버 연계, 대상 사용자 동기화, 소비/공급/초기화 연결.
- `RootDesk/MyDesk/PlayerAttack.mlua`: 독립된 `skill_rush` 단일 native hit.
- `RootDesk/MyDesk/GameData/GameData.mlua`: 태그 캐시, 설정 fallback, 참가자 초기화.
- `RootDesk/MyDesk/GameData/GameBalance.csv`: 연계 수/시간/배율 5개 설정.
- `RootDesk/MyDesk/UI/SkillBar.mlua`: 기존 슬롯 외곽선 및 HUD 표시.
- `ui/SkillBar.ui`: 비상호작용 `RushHud` 1개 추가. 기존 버튼 위치·아이콘·바탕 유지.
- `tools/build-skill-rush-ui.cjs`: 재실행 가능한 UIBuilder 마이그레이션.
- `.maplestory-skill-maker-ledger.md`: 이번 범위의 검증 원장 추가; 이전 원장 보존.
- 이 보고서와 `docs/skill-rush-maker-evidence-20261007.json`: 실제 로그 발췌.

UIBuilder 직렬화로 숫자 표현 및 줄바꿈 변경이 포함된다. UI를 raw JSON으로 수정하지 않았다.

## 2. 확정 규칙

서로 다른 SkillID 3개, 진행 사이 6초. 처음부터 끝까지 유지되는 태그 교집합을 사용한다. 교집합이 끊기면 현재 스킬부터 1단계로 재시작한다. 설정은 `skill_rush_required_count=3`, `skill_rush_window_seconds=6`이다.

## 3. 태그 원장

`GameData.GetSkillRushTags`가 기존 데이터에서 set을 한 번 생성해 캐시한다. SkillTable/MonsterTable 재로드 시 캐시를 무효화한다. 별도 스킬 카탈로그, 수동 SkillID 매핑, Pool의 sourceMonster 필드는 만들지 않았다.

## 4. 스킬 타입

실제 분기 우선순위에 따라 defense / buff / projectile / dash / line / cone / zone을 유도하고, `target_mode=area`와 제어 효과에는 area / control을 추가한다. zone은 실제 `DAMAGE_ZONE` 동작에 대응한다. 모든 공격에 붙는 광범위한 attack 태그는 없다. 66개 실제 획득 액티브의 태그를 Maker 서버에서 조회했다.

## 5. MegaArea

기존 `GetMegaMonsterPool`과 `GetMegaBossPool` → MonsterTable.drop_skill_id를 사용한다. 각 풀은 기존 MegaArea/Room 연결을 따른다. 스킬이 여러 지역에 등장하면 모든 mega 태그를 보유할 수 있다.

## 6. Family

신뢰할 기존 family 필드가 없어 추가하지 않았다. 이름·ID 접두사·그림을 보고 계열을 추정하지 않는다.

## 7. 연계 진입점

`ConsumeRandomSlot`이 기대 SkillID와 실제 슬롯을 확인하고 슬롯을 비운 뒤에만 `ProgressSkillRush`를 호출한다. 실제 UseSkill, 키보드 입력, 정확한 슬롯 소비를 검증했다. 불일치 요청은 슬롯과 연계 모두 변경하지 않았다.

## 8. 서버 권한

PlayerSkillSlots 인스턴스의 `_T`에 사용 ID, 교집합, 진행 시각, 타이머 revision을 보관한다. count/mask만 TargetUserSync, 성공 알림은 소유자 대상 Client RPC다. 클라이언트가 태그나 피해를 결정하지 않는다. 영구 저장·공유 파티 연계 상태를 추가하지 않았다.

## 9. 금색 테두리

기존 버튼의 native OutlineColor/OutlineWidth만 변경한다. 단계 1은 얇은 금색, 단계 2는 밝은 금색과 약한 밝기 변화다. 아이콘·바탕색은 변경하지 않는다. 같은 SkillID의 중복 슬롯은 mask에서 제외된다. 최초 별도 선 렌더러 방식은 시각 검수 후 제거했다.

## 10. HUD

스킬바 위 작은 `RUSH 1 / 3`, `RUSH 2 / 3`; 0단계에서는 숨김. 성공은 `SKILL RUSH ×N`으로 0.8초 유지한다. 실제 클라이언트 검사에서 0.4초에는 표시, 1.2초에는 숨김이었다. HUD는 raycast 비활성, CanvasGroup의 BlocksRaycasts/Interactable도 false다.

## 11. 배율

최종 공통 태그 1개 → ×3, 2개 → ×4, 3개 이상 → ×5. 세 경우 모두 실제 서버에서 성공 로그와 상태 초기화를 확인했다. 필요 스킬 수는 배율에 따라 늘어나지 않는다.

## 12. 피해 경로

`ResolveSkillRush` → native `AttackFast(..., "skill_rush", Monster)` → 정확한 대상 필터 → `CalcSkillRushDamage` → 기존 HitEvent/RoomMonster 경로다. 직접 HP 차감 구현은 없다. 유효 공격력은 `PlayerStats.GetTotalAtk()`에서 읽고 CombatFormula 및 상대 실드를 적용한다.

기본공격 damage/pierce/extra_target/range 강화 및 OutgoingBoost/NextAttackBoost 값을 피니셔 계수에 합산하지 않는다. NextAttackBoost 0.5가 피니셔 후에도 0.5로 유지됨을 확인했다.

## 13. 대상 선택

최소 연결 범위로 기존 `PickNearestBasicTarget`을 재사용한다. 안정적으로 보존된 '이번 시전 주대상' 참조가 없는 현재 구조에서 새 타깃 추적 파이프라인은 만들지 않았다. **현재 구현은 기본 사거리 안의 가장 가까운 유효 적**이다. 동일 맵, RoomMonster, 생존 및 HP>0을 다시 확인한다. 기본공격 range/pierce 강화는 이 탐색에 적용하지 않는다.

대상이 없으면 추가 피해만 생략하며 성공·리필·표시는 정상 처리된다. 주대상 우선순위 확장이 필요하면 별도 후속 범위다.

## 14. 성공 리필

성공 시 기존 `SupplyOneRandomSkill()`을 정확히 한 번 호출한다. 통제된 5슬롯 실험에서 소비 후 2칸이 남은 상태가 3칸으로 증가했다. 새 추첨 알고리즘이나 새 공급 타이머는 없다.

## 15. 5초 타이머

성공 전후 timer ID와 NextSupplyAt이 동일했고, 기존 예약 시각의 다음 공급도 실행됐다. 중복 스킬 사용은 연계 시각을 갱신하지 않는다. 이전 만료 콜백 취소 후 새 연계가 살아 있는 revision 시나리오도 확인했다.

## 16. 초기화

Begin/End Run, OnMapLeave, 확정 포털 전환, 사망, 실패 확정, 보스 클리어, Entity OnEndPlay에 연결했다. 실제 방 이동과 포털 판정에서 count=0, Pool 유지, 공급 시각 유지 확인. 사망/실패는 count 1→0 및 mask=0을 즉시 확인했다. 보스 클리어 후 complete=true, count=0, run=false였다.

## 17. 멀티플레이

상태는 플레이어 컴포넌트별이며 소유자만 동기화한다. 파티 전환의 ResetParticipantSkillRush는 각 참가자의 독립 상태를 초기화한다. **독립된 2개 클라이언트 실접속은 환경 부재로 BLOCKED**이며 멀티 PASS를 주장하지 않는다.

## 18. VFX/SFX

별도 몬스터 스킬 VFX를 피니셔로 도용하지 않았다. 기존 세 번째 스킬 연출, native 피해 숫자, 짧은 금색 성공 HUD를 사용한다. 새 사운드는 추가하지 않았다.

## 19. Maker 실측

| 항목 | 실제 결과 |
|---|---|
| 고유 3연계, 중복 count/time 유지 | PASS |
| 중복 금색 제외, 전체 교집합 단절 시 재시작 | PASS |
| ×3/×4/×5, 대상 없음 성공 | PASS |
| 즉시 1칸 리필, 같은 timer/deadline, 다음 5초 공급 | PASS |
| 기본 6초 만료, 취소된 이전 타이머가 새 연계에 영향 없음 | PASS |
| 실제 키보드 Z·C·V 소비·연계 | PASS |
| defense / line / cone / buff / projectile / dash / zone / delayed / control 시전 | PASS, 대표 표본 |
| 튜토리얼 즉시 교체 및 연계 제외 | PASS |
| 일반 / 엘리트 / 보스 추가 피해 | PASS |
| 방 / 포털 / Begin / End / 사망·실패 / 보스 클리어 | PASS |
| 독립 2인 접속 | BLOCKED |
| 실제 모바일 터치·기기별 화면 | NOT CHECKED |

시각 캡처 시에만 런타임 연계 시간을 60초, 성공 문구를 15초로 잠시 고정했다. 제품 설정은 6초/0.8초이며 별도로 검증했다. 피해 격리 실험에서는 자동공격/AI 정지, 적 HP 증가, 실드/강화 주입을 사용했다. 이는 테스트 인스턴스에만 적용했고 소스에 테스트 치트를 넣지 않았다.

## 20. 오류 상태

최종 Maker Refresh 후 Build Error 0, 기존 Warning 7. 경고는 기존 daily count/collection pilot/model 속성 항목으로 Rush 변경과 무관하다. 마지막 검증 세션의 Rush Runtime Error 0. 탐색용 MakerScript에서 잘못된 컨텍스트·Entity 임시 필드·JSON 직렬화 오류가 있었으며 해당 스니펫을 수정한 뒤 본 검증을 수행했다. 이를 기능 오류 0과 혼동하지 않도록 분리한다. `git diff --check` 통과.

## 21. 판정 범위

핵심 연계/피해/리필/초기화는 실제 Maker PASS. 기존 66종의 ID·효과·데이터 행은 수정하지 않았지만 이번에 66종 전체를 재시전한 것은 아니다. Upgrade 3선택의 UI 전수 회귀, 독립 멀티, 모바일 전체 검수를 완료했다고 주장하지 않는다.

## 22. 자연 전투 빈도

02:14:56~02:18:33, 약 3분 37초의 키보드 이동·기본공격·스킬 사용 표본. 전투방 진입 위치만 테스트로 이동했고 Pool은 0에서 시작했다. 불타는 멧돼지 첫 획득 보장은 작동했으며 이후 같은 종은 중복 풀 추가 없이 유지됐다. 페어리 2회는 각각 0.41449/0.54058로 기존 10% 판정에 실패했다. 종료 시 Pool=1, 자연 Rush 성공=0이었다.

한 방·한 시드의 짧은 표본이므로 전체 Run의 획득 불가능을 증명하지 않는다. 다만 초반 체험이 늦다는 위험은 확인됐으며, 여러 방/시드 및 엘리트 보상까지 포함한 추가 표본이 필요하다.

## 23. 보스 수치와 체감 한계

공격력 35, 방어 적용 후 ×3=90 / ×5=149. ×4에 50% 실드가 있으면 60. 엘리트는 528→408(120), 머쉬맘 보스는 960→811(149, 약 15.5%)이었다. 원 스킬 27+24+39와 피니셔 120이 각각 들어가 총 210 감소했다. 단발로 보스를 삭제하지 않지만 실제 발동 빈도까지 포함한 장기 DPS 균형 판정은 아직 아니다.

## 24. 드롭 변경 여부

변경하지 않았다. 기존 첫 획득 보장/10% 일반 획득/엘리트 정책/종 중복 처리/Pool 구조를 보존했다. 추가 표본에서 3종 확보가 지속적으로 늦는 것이 재현되면 초기 획득 보정부터 작게 검토하는 편이 타당하다.

## 25. 남은 항목과 최종 답변

- 제출 가능? **기능 구현본은 준비됐지만 최종 출시 검증 완료로는 판단하지 않는다.** 멀티·모바일·초반 체험 확인이 남았다.
- 랜덤 5슬롯의 의미? 가능한 다음 슬롯만 금색으로 안내하고 중복은 제외하므로 선택할 이유가 생겼다.
- 테두리 명확성? PC 캡처에서 1/2단계 및 중복 제외를 확인했다. 실제 모바일은 미검증이다.
- 피니셔 균형? 단발 수치는 과도한 보스 삭제가 아니었다. 빈도 포함 평가는 추가 플레이가 필요하다.
- 드롭 조정? 당장 변경하지 않았다. 초반 3종 확보 시간은 후속 검수 우선순위다.
- 기능 추가 vs 마무리? **새 기능보다 위 검수와 가독성·획득 속도 조정이 우선**이다.

### 증거

- [Maker 로그 발췌](skill-rush-maker-evidence-20261007.json)
- [1단계 PC 화면](<C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20261007_021342_641.png>)
- [2단계 PC 화면](<C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20261007_021405_672.png>)
- [성공 HUD 화면](<C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20261007_021917_745.png>)

Maker는 검증 후 edit 상태로 중지했다. 앱을 종료하거나 재실행하지 않았다. 테스트는 기존 Maker 로컬 데이터에서 실행됐으므로 통상 클리어 보상 처리는 발생했지만, 운영 저장소 초기화나 별도 저장 데이터 편집은 하지 않았다.
