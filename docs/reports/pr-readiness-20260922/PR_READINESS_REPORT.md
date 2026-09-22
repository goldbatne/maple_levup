# 커밋·PR 제출 전 추가 검증 — 2026-09-22

대상: `D:/maplestory_levup`. 브랜치: `codex/mega-area-pr-readiness-20260922`.
비교 base: `1ec91d5dc95f3638a6e5ac855274a10289070982` (기존 PR #182 병합 후 main).
기존 사용자 미커밋 개편·UI·엔트리 복구 작업을 보존하여 제출한다. 이 문서는 이전 정리 보고서의 후속이며 과거 실패/검사 결과를 덮어쓰지 않는다.

## PR 판단

**리뷰 제출 가능, 즉시 병합 승인 아님.** 실제 독립 멀티클라이언트 검증은 남는다. 사용자는 Abandon 시 이번 Run 새 도감 기록도 버리도록 확정했다. PR 작성자는 자기 PR의 독립 승인자로 처리되지 않는다.

현행 규칙은 **Mega Area / Run OwnedSkillPool / 랜덤 일회성 5재고 / 5초 공급 / 성공 소비 / 플레이어 스킬 쿨다운 우회**다. 과거 고정 장착·재사용 쿨다운 보고서를 이번 acceptance 기준으로 사용하지 않는다.

## 발견하여 수정한 문제

| 문제 | 근거 | 수정과 재검증 |
|---|---|---|
| 추가 스킬 소비 때 이미 진행 중인 공급 타이머 재시작 | Runtime 예정 시각 230.894 → 232.231로 밀림 | `PlayerSkillSlots.ConsumeRandomSlot`: timer가 없을 때만 시작. 수정 후 85.188 → 85.188 유지 |
| 마지막 생존자만 포기하면 사망 참가자가 ACTIVE Run에 남음 | 실제 생산 함수 본문 서버 상태 재현: FAILED 기대, ACTIVE 관측 | `GameData.AbandonRogueliteParticipant`: 남은 참가자의 전원 사망 검사. 수정 후 마지막 생존자 이탈 FAILED / 생존자 존재 ACTIVE / Solo ABANDONED. **SERVER_SIM**, 실제 멀티 아님 |
| 맵 전환 중 포탈 엔티티 Client RPC 실패 | `RoomPortal.TryPass` 메서드 상대 54행 LEA-3032 | 안내를 `GateNotice` Logic RPC로 이동, 전환 잠금 중 중복 안내 방지. 같은 Mega 05 경로에서 오류 재발 없음 |
| 생성 사전 검사가 일부 로비 상태를 복구하지 않음 | GenerateRogueliteGraph가 재설정하는 8필드가 사전 검사 snapshot에서 빠짐 | revision/result/participantResults/spawners/complete/failed/objective/lock 보존 추가. 생성기 본문·난수·콘텐츠 변경 없음 |
| 데이터 검사기의 거짓 양성 | 빈 필수 테이블·빈 이름·비숫자 실행 값이 통과 | 필수 필드 검사와 104개 음성 회귀. 선택적 빈칸·정상 0값은 보존 |
| AreaSelectPanel 빈 줄 탭 10곳 | 이전 `git diff --check` 실패 | 공백만 제거, 비공백 토큰 동일. 현재 diff check 통과 |
| 포기한 Run의 새 발견이 자동저장으로 영구화됨 | 사용자 확인: 이번 Run의 새 발견도 버림 | 참가자별 서버 pending 원장에만 기록. CLEAR/FAILED 확정 시 추가 정산, ABANDON은 pending만 폐기. 기존 영구 ID·미등록 미래 ID는 삭제하지 않음 |
| 제한시간 없는 보스전에 남은 시간 00:00 표시 | 실제 Area 5 화면 및 RoomSpawner의 Run limit=0 | PlayerHud가 동기화된 BossTimeLimitSeconds를 따라 시간 텍스트만 숨김. 새 Build 후 파우스트 이름·HP 유지, timerEnabled=false·빈 텍스트 및 실제 화면 확인 |

스킬 계수·범위·프레임·VFX, 포획률, 공급 간격, 몬스터 수치는 이번 보정에서 바꾸지 않았다.

## Maker 실행 증거

실제 Maker MCP Refresh → Play → 로그를 사용했다. execute_script의 dispatch 성공만으로 PASS 처리하지 않았다. UI 클릭 주입이 동작하지 않은 경우 실제 Client UI handler를 호출했으며 사람 마우스 클릭 시험과 구분한다.

| Mega Area | Seed / Mode | 관측 |
|---|---|---|
| 01 | 635551 / NORMAL | 키보드 이동·포탈 통과·자연 처치·첫 능력 획득·5초 공급·중복 5재고·Z/X 연속 소비·창 닫기·Abandon |
| 01 | 92201 / NORMAL | 주 경로 9방, 8포탈 전환, 파우스트 실제 기본공격 처치 → CLEAR → 로비 |
| 02 | 92202 / MONSTER_SKILL | 66종 실제 UseSkill 검사와 별도 새 Run의 포탈 전환·엘리쟈 처치 → CLEAR → 로비 |
| 03 | 92203 / NORMAL | 주 경로 9방, 8포탈 전환, 피아누스 처치 → CLEAR → 로비 |
| 04 | 92204 / MONSTER_SKILL | 주 경로 8방, 7포탈 전환, 태륜 처치 → CLEAR → 로비. 이 시험에서 포탈 안내 RPC 오류 발견 |
| 05 | 92205 / NORMAL | 수정 후 주 경로 8방, 7포탈 전환·도도 처치 → CLEAR → 로비. 같은 Seed RPC 오류 재발 없음 |

포탈/보스 반복 시험은 QA가 **실제 연결 포탈 위치로 플레이어만 배치**한 뒤 실제 `RoomPortal.TryPass`와 기본공격을 사용했다. Graph·목표 완료·보스 HP를 강제 지정하지 않았다. 모든 방의 장애물을 사람 입력으로 걸어서 확인했다는 뜻은 아니다.

Area 5 첫 시험은 고정 왼쪽 접근 보조가 외곽 포탈을 다시 밟아 완료되지 않았다. QA 접근을 안쪽으로 보정했다. 두 번째 시험은 초기 55초 관측창에서 ACTIVE였고, 이어진 실제 자동공격으로 14:51:47 보스 사망, 14:51:50 로비 복귀했다. 제한시간 내 완료한 것처럼 바꾸지 않는다. 최종 공개 QA 도구의 관측 상한은 90초다.

## 66종 스킬 검사

- 66/66 `PASS_OBSERVED`, 132회 실제 `PlayerAttack.UseSkill` 발동.
- 동일 SkillID 두 재고를 연속 사용: 지정 슬롯만 소비, 다른 재고 보존, 개별 cooldown ledger 불변, 공격 피해 또는 방어 상태 적용 관측.
- 첫 배치 120초 QA 상한으로 61개 관측 후 중단. 나머지 5개는 별도 재실행하여 확인. 중단된 시험을 전수 통과로 처리하지 않았다.
- 테스트 전용 Maker namespace, transient QA 슬롯/타깃 사용. 저장 쓰기 차단 후 원래 transient 값 복원 및 QA Run 포기.
- 실제 VFX 호출 경로는 실행했지만 **66종의 그림/위치/알파를 모두 눈으로 승인한 것은 아님**. 모든 벽/통로 조합, 방어의 실피해 흡수, 멀티 네트워크 동시성은 별도 미검증.
- 원시 행: [SKILL_RUNTIME_OBSERVED.json](SKILL_RUNTIME_OBSERVED.json), 재현 도구: [skill-runtime-qa.lua](skill-runtime-qa.lua).

## 정적 검사와 보존

- 현행 데이터: 몬스터 103 / 스킬 정의 112 / 플레이어 사용 가능 66 / 비활성 패시브 35. ID 중복을 스킬 수로 세지 않음.
- 기본 데이터 검사, 현행 문서·링크 검사, 음성 회귀 104개, 포탈 회귀 4개, preflight 상태 회귀 3개, `git diff --check` 통과.
- 보호 파일 484개 중 이번 수정에 해당하는 7개 source 이외 예상 밖 변경 없음. 나머지 477개 해시 동일. 스킬 분석 baseline 해시 변경 없음. 아트는 Git 변경 0이며 별도 전수 바이트 재검사라고 표현하지 않음.
- 기존 `.git/index.lock`은 프로세스 없음·오래된 0바이트 lock임을 확인하고 `.git/index.lock.stale-20260922-prqa`로 보존 이동했다. 사용자 게임 파일 삭제 없음.
- 새 파일은 보고서·검사 도구다. 기존 게임 소스 수정은 GameData, PlayerSkillSlots, RoomPortal, GateNotice, AreaSelectPanel, PlayerCollection, PlayerHud의 7개. 이 PR 전체에는 사용자가 이미 작성한 Mega Area/맵/UI/데이터 변경도 포함된다.
- 독립 패키지 검사: [PACKAGE_READONLY_RECHECK.md](PACKAGE_READONLY_RECHECK.md).

## 남은 승인·검증 항목

1. **정책 확정·반영:** `PlayerCollection.GrantRogueliteAbility`는 새 발견을 `RoguePendingDiscoveries[userId]`에만 기록한다. Abandon은 이 Run의 pending만 버리고 이전 영구 도감은 보존한다. DB 직렬화 원장에 넣었다가 되돌리는 방식은 사용하지 않는다. 같은 서버 Run이 살아 있는 동안 재접속한 참가자의 terminal 정산 경로는 있지만, **Instance/서버 메모리가 소멸한 뒤 offline pending 복원·전달은 미구현**이며 멀티 저장 검증 완료로 표현하지 않는다.
2. **BLOCKED_RUNTIME_MULTIPLAYER:** 연결 도구는 단일 client/server 및 instance 실행 컨텍스트만 제공한다. 독립 2~4클라이언트 생성 도구는 확인되지 않았다. `DebugRoguePartyStateSimulation`은 순수 모델 시험이고, 1.25/1.50/1.75 계산 확인이지 실제 협동/Spawn HP 인증이 아니다.
3. **NOT_RUN:** 모든 66종의 VFX 시각 전수 승인·전체 벽/통로 호환, 모든 Seed의 사람 입력 완주, 실제 멀티 이탈/재접속.
4. 포탈 LEA-3032 수정 전 발생 로그, QA 관측 코드의 잘못된 `h` 접근과 존재하지 않는 `GetRunOwnedSkillCount` 호출 오류 각 1건, Area 5 QA 중단 기록을 삭제하거나 PASS로 덮지 않았다. 후자의 개수 관측은 실제 OwnedSkillPool 순회로 수정하여 재실행했다.
5. Skill loader 미제공과 직접 Skill 경로 읽기 승인 거절은 우회하지 않았다. 기존 코드 패턴에 근거한 최소 수정만 수행했다.

최종 Build/Seed/Fail-reset 관측은 아래 후속 절과 `MAKER_EVIDENCE.json`에 기록한다. 정적 검사 통과를 사용자 아트 승인이나 독립 PR 승인으로 표현하지 않는다.

## 최종 저장·초기화 관측

- 사용자 확정 정책: **ABANDON은 이번 Run의 새 발견도 폐기**. 기존 영구 도감은 유지.
- 전용 `MakerTest_PRQA_Discovery_20260922_*` 키를 만들어 실제 `PlayerDBManager.SaveNow → BatchGetAndWait → DecodeRogueliteRecord`로 확인했다. 기존 계정 키를 초기화·덮어쓰기해서 테스트하지 않았다.
- 실제 reward 메서드에 미발견 몬스터/스킬을 QA 입력했다. 자연 처치가 아닌 **보상 경로 주입 테스트**이며 앞의 자연 전투 시험과 구분한다.
- ABANDON: pending=true / serializer 제외=true / 실제 저장 재조회 제외=true / 기존 기록 보존=true. 실제 확인창 handler로 포기 후 로비 복귀. 다시 읽은 일반 MakerTest 키와 전용 ABANDON 키 모두 신규 ID 없음.
- FAILED: 테스트용 치명 피해를 실제 `PlayerHit.OnHit`로 전달하여 사망 경로 실행. FAILED 확정 / 신규 발견 정산 / pending 제거. 전용 FAILED 키 실제 재조회에 신규 ID 존재. 일반 MakerTest 키에는 주입한 신규 ID가 없음.
- CLEAR: Mega 01 Seed 92303에서 실제 마노 기본공격 처치 후 CLEAR 확정. 15:23:25 전용 CLEAR 키 재조회에 신규 ID 존재, 원래 MakerTest 키에는 없음. QA 보상 주입과 실제 보스 처치를 구분한다.
- 포기 뒤 다음 Run: pool=0, slot1=nil, HP=1000, pending 비어 있음, 신규 발견 없음.
- 사망 뒤 로비: pool=0, 공급 timer=0, HP=1000. 다음 Run: pool=0, slot1=nil, HP=1000, pending 비어 있음, objective=false.
- 테스트 키는 추적 가능한 QA 기록으로 남겼으며 사용자 영구 저장을 삭제하지 않았다. 실제 독립 클라이언트의 강제 종료/재접속 시험으로 확대 해석하지 않는다.

## 생성 재현·빌드

- 5 Mega Area × 서로 다른 Seed 2개 = **10건**, 매 건 실제 서버 생성기를 두 번 실행하여 Graph/Room role/Encounter 구성/Main path/Boss/Start/Final/Objective를 정규화 비교했다. 중간 global math.random 소비와 무관하게 동일 결과.
- 10/10 valid·reproducible·preflightRestored, 실패 0. 잘못된 Area 거부 및 상태 복구도 확인.
- 초기 스폰의 개별 픽셀 좌표나 모든 물리 지형 통과를 이 결과로 인증하지 않는다.
- 정책 수정 후 Build는 15:10:06, 보스 HUD까지 반영한 최종 Build는 **2026-09-22 15:29:08, Error 0 / 기존 Warning 2**다. Warning은 InputSpeed, AvatarAttackPlayRate.
- 첫 6개 source 수정은 `883439b7107eca895ad0e9fcebefbf53d6026525`에 기존 게임 개편과 함께 커밋했다. PlayerHud의 시간 표시 수정은 이 보고서를 포함한 후속 커밋에 분리한다. 이전 실패 로그는 증빙에 남긴다.
- 최종 HUD 회귀: Mega 01 Seed 92304, 실제 포탈 7회 전환 후 파우스트 HUD 확인(15:31:14). 시간 숨김·이름·HP 유지. 보스 미처치 상태에서 실제 포기 handler로 ABANDONED(15:31:51). 이 최종 실행 구간 Runtime Error 0. 잘못된 QA Area ID `01` 요청은 서버가 경고 후 거부했고 실제 ID `mega_01`로 재실행했다.

## 실제 화면

- [로비 HUD](evidence/lobby-hud.png): 이름 중앙, HP 중심, Level/EXP 숨김.
- [Area 선택](evidence/area-selection.png), [파티 창](evidence/party-window.png).
- [자연 전투](evidence/natural-combat.png), [보유 능력 창](evidence/owned-ability-window.png).
- [던전 나가기 확인창](evidence/abandon-confirm.png), [Area 5 실제 보스](evidence/area05-boss.png).
- [최종 보스 HUD: 시간 표시 제거](evidence/boss-hud-no-legacy-timer.png), [최종 재빌드·HUD 로그](FINAL_HUD_EVIDENCE.json).

화면은 Maker가 반환한 PNG를 그대로 복사했다. 합성·재생성·게임 아트 수정 없음.

## Stage 전체 검사 시 추가 확인

앞선 `git diff --check` PASS는 당시 tracked 변경 검사다. 모든 보존 자료를 stage한 전체 `git diff --cached --check`에서는 역사 문서의 Markdown 줄바꿈·EOF 공백과 두 baseline 복원 패치 내부 공백 경고가 남는다. 최종 528건 중 504건은 두 보존 패치다. 기준본 해시를 지키기 위해 과거 자료를 재작성하거나 검사를 완화하지 않았다. 충돌 마커는 없다. 새 QA 파일의 EOF 공백 2건만 정리했고, 게임 소스·UI·맵 및 현행 도구·이번 PR 보고서 범위는 별도 staged check를 수행한다. 전체 역사 자료 포함 검사를 PASS로 표현하지 않는다.

15:32:52 실제 클라이언트에서 마지막 포기 후 `map=maptown` 확인, Maker Play 종료.
