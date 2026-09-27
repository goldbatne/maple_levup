# 66종 스킬 VFX 정합성 검수 — 2026-09-26

## 기준과 범위

- 확정 기능: `docs/reports/skill-diversity-final-20260925/SKILL_66_FINAL_DESIGN.csv`의 고유 `SkillID` 66개.
- 실제 연결: `RootDesk/MyDesk/GameData/MonsterTable.csv`의 `drop_skill_id` 및 Maker가 로드한 `SkillTable` (`Mislocated/MyDesk/GameData/SkillTable.csv`)을 대조했다. 66개 모두 연결을 확인했다.
- 원작 정체성 판단은 기준 CSV의 `Lore/Identity 근거`를 계승했다. 이번 검수는 새 스토리·스킬 기능 조사나 재설계가 아니다.
- 신규 PNG/Icon/AnimationClip 제작·교체 없음. SkillID, 몬스터 연결, Icon RUID, 피해 계수, 사거리, 제어/버프 기능, 5초 공급, 슬롯 소모는 변경하지 않았다.

## 실제 변경

| 스킬 | 기존 화면 문제 | VFX만 변경한 내용 | Maker 근거 |
| --- | --- | --- | --- |
| 추억의 신관 `s_mon_memory_monk_trainee` | 8프레임의 큰 전방 베기가 자기 강화 기도보다 공격처럼 읽힘 | 기존 승인 프레임 중 F00/F01/F06/F07을 시전자 몸 오버레이로 재사용. 높이 +0.55, 연출 0.6초. 다음 공격 +50%, 12초라는 **기능**은 그대로. | Maker 데이터 로그: 1 layer/4 frames/0.6s/+0.55. [변경 전](evidence/before-after/monk_before.png) · [변경 후](evidence/before-after/monk_after.png) |
| 정식기사 C `s_mon_official_knight_c` | 0.8초 제자리 뇌전 베기가 0.2초 돌진과 분리되어 보임 | 같은 8프레임의 앞 4장은 제한된 돌진 경로를 0.2초 따라가고, 뒤 4장은 도착 판정점에서 0.2초 재생. Player·MONSTER_SKILL 모두 적용. 피해/대상 판정은 그대로. | Maker 데이터 로그: 1 layer/8 frames/0.4s. [변경 전](evidence/before-after/knight_before.png) · [변경 후](evidence/before-after/knight_after.png) |

변경 코드: `RootDesk/MyDesk/Combat/SkillEffect.mlua`, `RootDesk/MyDesk/PlayerAttack.mlua`, `RootDesk/MyDesk/MonsterAttack.mlua`; 변경 데이터는 위 SkillTable의 두 행 중 VFX 프레임·재생시간·오프셋에 한정된다. 기존 몬스터/게임 데이터의 다른 변경은 이번 작업에서 되돌리거나 덮어쓰지 않았다.

## 66종 확인 결과

- [66종 개별 결과표](SKILL_66_VFX_VISUAL_REVIEW.csv): 각 Monster/Skill/확정 기능/현 VFX RUID/정체성 근거/변경 여부/Player·Monster 화면 근거를 기록했다.
- 실제 Maker의 `PlayerAttack:UseSkill`와 `MonsterAttack:CastSkill` 경로를 각각 66종 호출했다. 최신 성공 기록은 **Player 66/66, Monster 66/66**이다. 실패했던 초기 슬라임 몬스터 QA는 시전자 거리 보정 후 재실행했고 8회 허용을 확인했다. 중간의 Play-mode 이탈/재시작도 실패 기록을 지우지 않고 남겼다.
- 모든 스킬에 Player/Monster Maker 스크린샷 쌍을 확보하고 [5종씩 묶은 비교판](VFX_BOARD_01_05.png)부터 `VFX_BOARD_66_66.png`까지 확인했다. 짧은 연출이 최초 캡처에 잡히지 않은 빨간 달팽이·파이어보어·블러드 하프·루나픽시·마티안·키메라·슬라임은 추가 연속 캡처로 다시 보았다.
- 샘플 화면에서 **추가로 확정된 기능↔VFX 불일치는 발견되지 않았다**. 그래서 다른 64종의 VFX는 유지했다. 다만 시그너스·변형된 스텀피의 대형 지속 이펙트는 화면 점유율이 커 자연 전투 중 가독성을 `NEEDS_USER_REVIEW`로 남겼다. 본 정지 화면 검수를 사용자 아트 승인으로 기록하지 않는다.
- 시각 판정은 `PASS_SAMPLED` 64종, `NEEDS_USER_REVIEW` 2종이다. `PASS_SAMPLED`는 실제 Maker 시전과 캡처 프레임에서 명백한 불일치가 없다는 뜻이다. 66종 모두를 자연 Run에서 처음부터 끝까지 연속 영상으로 검수했다거나, 모든 Seed·벽/통로에서 타이밍 오류가 절대 0이라는 뜻은 아니다.

## Maker Build/Runtime

- 마지막 Refresh 후 Build 로그: `Error` 0. `Info` 12건과 기존 모델 경고 2건(마노 `InputSpeed`, 보우마스터 `AvatarAttackPlayRate`)이 남아 있다.
- 마지막 재시작한 Play 세션 normal 로그 1,353건 중 `Error` 0. Maker에서 수정된 두 스킬의 로드 값과 양측 실제 시전 성공을 재확인했다.
- 자연 Run으로 66종을 순회하는 방식은 이번 환경에서 확인하지 못했다. Run 맵 전환 시 서버 참가자는 존재하지만 클라이언트 `LocalPlayer`가 없고 화면이 검게 되는 현상을 관찰해, 저장 쓰기를 막고 map01의 보이는 격리 QA 세션에서 동일한 실제 시전 함수를 사용했다. 이 Run 전환 문제는 본 VFX 작업 범위 밖이라 게임 로직을 임의 수정하지 않았다.
- 정지 화면은 0.2~0.4초의 프레임 순서·투사체 실제 이동 궤적을 완전히 증명하지 못한다. 특히 기사 C의 이동 4프레임/도착 4프레임은 코드 경로 및 시전 결과 화면까지 검증했지만 고속 연속 영상/자연 전투 판정은 추가 확인이 필요하다.

## 결론과 남은 검증

확정 VFX 문제 2종은 기존 자산을 재사용해 수정했다. 66종 모두 Maker 시전과 Player/Monster 샘플 화면은 확인했지만, **자연 Run 전체와 고속 연속 동작 검증까지 끝났다고 주장하지 않는다**. 따라서 요청한 절대적 완료 조건(모든 상황의 위치·방향·타이밍 오류 0)은 아직 완전 입증되지 않았다. 미검증 부분은 별도 기능 변경 없이 남긴다. git commit/push는 하지 않았다.
