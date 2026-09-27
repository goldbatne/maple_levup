# World Skill Drop 최종 검증 보고서

- 검증 일시: 2026-09-27 13:05~13:13 KST
- 프로젝트: `D:/maplestory_levup`
- 범위: World Skill Drop UI, 절대 60초 수명, 방 이동 복원, Run 단위 첫 보장, 획득/공급 연계, Run 종료 정리
- 제외: 체력 상자, 스탯, 기본 공격, 스킬 기능/수치, Mega Area·Party·Portal·Respawn·Potion 구조 변경

## 결과 요약

| 항목 | 결과 | 근거 |
|---|---|---|
| Skill Drop 시각 표현 | PASS_RUNTIME | 월드 `PixelRendererComponent` 기반 금색/암색 Skill Frame + 기존 Icon, 이름, 남은 시간, E 상호작용 |
| 30초/10초 표시 | PASS_RUNTIME | 30초 이하 카운트다운, 10초 이하 `!` 및 적색/주황 경고 프레임 육안 확인 |
| 다중 Drop 가독성 | PASS_RUNTIME | 4개 Drop 동시 화면에서 화면을 가리지 않고 개별 Skill Frame으로 구분 |
| 절대 60초 Lifetime | PASS_RUNTIME | `spawn_time`/`expire_time` 논리 레코드로 유지, 방 복귀 시 남은 47.55초로 복원 |
| 만료 후 Backtracking | PASS_RUNTIME | 5초 QA Drop이 다른 방에서 만료된 뒤 복귀해도 재생성되지 않음 |
| Run 첫 보장 | PASS_RUNTIME/SERVER_SIM | 모든 참여자가 보유 시 미소비, 최초 유효 Kill에서 100% 1개 생성, 이후 10% |
| Party 공유 보장 | PASS_STATIC/SERVER_SIM | 활성 참가자 누락 여부를 서버에서 합산하고 Kill당 Run 공유 Roll 1회. 2~4 독립 클라이언트는 환경상 미실행 |
| 중복 보유 | PASS_RUNTIME | `SKIP_ALL_OWNED`, Drop 미생성, 첫 보장 미소비 |
| 동시 Claim | PASS_RUNTIME | 동일 serial에 첫 Claim 성공/두 번째 실패, 레코드 1회 제거 |
| OwnedSkillPool 연계 | PASS_RUNTIME | `Run 능력 풀 추가 s_mon_red_snail` 확인 |
| 5초 Random Supply | PASS_RUNTIME | Claim 후 13:10:15부터 5초 간격으로 1~5번 공급 확인 |
| Run 종료 정리 | PASS_RUNTIME | `RUN_ABANDONED count=1`, `INSTANCE_END count=0`, 이후 Drop/Supply timer 재실행 없음 |
| Build | PASS | Error 0, 기존 비관련 Warning 2 |
| Runtime | PASS | Error/Fatal 0 |

## 핵심 로그

```text
[SkillDropRoll] SKIP_ALL_OWNED monster=m_blue_snail skill=s_mon_blue_snail first_resolved=false
[SkillDropRoll] scope=RUN_SHARED monster=m_red_snail skill=s_mon_red_snail missing=1 first=true ... chance=1.00 dropped=true
[SkillDropRoll] FIRST_GUARANTEE_CONSUMED run=1:mega_01:927104 serial=11
[QA_SKILL_DROP_RULE] ... repeatedEligible=3 spawned=true delta=1 firstBefore=false firstAfter=true
[SkillDropRoll] scope=RUN_SHARED monster=m_slime skill=s_mon_slime missing=1 first=false ... chance=0.10 dropped=false
[QA_SKILL_DROP_CLAIM] serial=11 first=true second=false remainingRecord=false
[SkillSlots] Run 능력 풀 추가 s_mon_red_snail (m_red_snail)
[SkillSlots] 랜덤 공급  1번 ← s_mon_red_snail
[SkillSlots] 랜덤 공급  2번 ← s_mon_red_snail
[SkillDropRecord] SUSPEND map=map001 count=1 reason=QA_MAP_UNLOAD
[SkillDropRecord] MATERIALIZE serial=8 map=map001 remain=47.55
[SkillDropRecord] RESTORE map=map001 count=1
[SkillDropRecord] REMOVE serial=9 reason=EXPIRED map=map001
[SkillDrop] CLEAR_ALL reason=RUN_ABANDONED count=1 first_guarantee_reset=true
[SkillDrop] CLEAR_ALL reason=INSTANCE_END count=0 first_guarantee_reset=true
```

## 증빙 이미지

- [60초 표시](evidence/skill_drop_final_60s.png)
- [30초 표시](evidence/skill_drop_final_30s.png)
- [10초 경고](evidence/skill_drop_final_10s.png)
- [E 상호작용](evidence/skill_drop_final_interact.png)
- [다중 Drop](evidence/skill_drop_final_multiple.png)
- [Backtracking 복원](evidence/skill_drop_final_backtracking.png)
- [만료 후 Backtracking](evidence/skill_drop_final_expired_backtracking.png)

## 변경 파일

- `RootDesk/MyDesk/Inventory/SkillDropManager.mlua`
- `RootDesk/MyDesk/Inventory/SkillDrop.mlua`
- `RootDesk/MyDesk/Room/RoomPortal.mlua`
- `RootDesk/MyDesk/Room/RoomSpawner.mlua`
- `RootDesk/MyDesk/GameData/GameData.mlua`
- `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`
- `RootDesk/MyDesk/Models/Items/SkillDrop.model`

## 제한

- 실제 독립 2~4인 Maker 멀티클라이언트 Runtime은 현재 단일 클라이언트 환경에서 수행하지 못했다.
- Run 공유 첫 보장, 참가자별 누락 판정, Kill당 단일 Drop 생성은 서버 코드와 Maker 서버 시뮬레이션으로 검증했다.
- Git commit/push는 수행하지 않았다.
