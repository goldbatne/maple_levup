# 66종 스킬 VFX 의미 정합성 — 2026-09-26

## 범위와 판정

- 기준: `docs/reports/skill-diversity-final-20260925/SKILL_66_FINAL_DESIGN.csv`의 66 SkillID와 `docs/reports/skill-vfx-alignment-20260926/SKILL_66_VFX_VISUAL_REVIEW.csv`.
- 결과: **KEEP 47 / ADJUST 19 / REWORK 0**. 상세 근거와 Player·Monster 판정은 [SKILL_66_VFX_MEANING_REVIEW.csv](SKILL_66_VFX_MEANING_REVIEW.csv)에 한 행씩 기록했다.
- 수정 전 66종 × Player/Monster를 Maker에서 각 8회 실제 시전하여 132/132 `qaOk=true`와 화면 캡처를 얻었다. 수정 영향 19종은 같은 경로에서 양쪽 38/38 재실행하여 `qaOk=true`를 확인했다. Maker 자동 재시작 때 끊긴 마지막 고대 암흑 골렘 2회는 새 Play 세션에서 별도 재실행했다. 로그는 `maker-visual-runs.jsonl`과 `after_final/maker-visual-runs.jsonl`이다.
- `PASS_SAMPLED`는 실제 시전 로그와 캡처 장면에서 역할의 반대 의미가 보이지 않았다는 뜻이다. 애니메이션의 모든 프레임·모든 실제 전투 조합에 대한 무조건적 미술 승인은 아니다. **검수 장면에서 남은 명백한 의미 불일치 0종**이며, 최종 미술 취향 승인은 사용자에게 있다.

## 실제 변경

| 분류 | SkillID | 수정 이유와 VFX 보정 |
|---|---|---|
| DEBUFF | `s_mon_fairy`, `s_mon_octopus` | 자신을 강화하는 듯 보이던 가루/먹물을 전방 적중 위치에 작게 표시하고, 실제 WEAKEN이 적용된 대상 위에 기존 프레임을 활용한 보라 표식을 효과 시간 동안 부착. 빗나가면 표식 없음. |
| BUFF | `s_mon_drumming_bunny` | 큰 지면 폭발처럼 보이던 북·별 프레임을 0.62배로 줄여 시전자 몸 가까이에 배치. 자기 강화임을 강조. |
| CONTROL | `s_mon_king_clang` | 집게가 시전자를 감싸 방어막처럼 보이던 연출을 전방으로 1.25 world unit 이동하고 0.82배로 줄여 밀치기 방향을 표시. |
| 조준 지점형 15종 | `s_mon_mushroom`, `s_mon_dark_axe_stump`, `s_mon_tauromacis`, `s_mon_eliza`, `s_mon_squid`, `s_mon_chronos`, `s_mon_timer`, `s_mon_meercat`, `s_mon_homun`, `s_mon_deo`, `s_mon_zeno`, `s_mon_advanced_knight_b`, `s_mon_cygnus`, `s_mon_ancient_dark_golem`, `s_mon_mutant_stumpy` | 기존에는 시전자 자리에도 동일 연출이 생기고 타격 시 다시 겹쳐 실제 구역을 잘못 알릴 수 있었다. 이제 조준 지점에 1회 표시하고, 피해·제어 종료 시점까지 보이도록 프레임 재생 길이를 맞춤. 반복 판정·수치는 그대로. |
| 대형 구역 추가 조정 | `s_mon_cygnus`, `s_mon_mutant_stumpy` | 캐릭터를 가리던 기존 꽃/뿌리 프레임의 알파만 0.72로 낮춤. 범위·크기·원화는 유지. |

19종은 위 집합의 중복을 제외한 개수다. `REWORK=0`은 새 원화나 새 RUID가 필요할 정도의 역할 반전은 확인하지 못했다는 뜻이다. 47종은 기존 시각 자산과 배치를 유지했다.

## 전후 화면과 전체 근거

- [19종 수정 후 Player/Monster 비교표](ADJUSTED_19_AFTER_OVERVIEW.png)
- [포자 장판](evidence/comparison/s_mon_mushroom_player.png), [요정 약화](evidence/comparison/s_mon_fairy_player.png), [옥토퍼스 약화](evidence/comparison/s_mon_octopus_player.png)
- [북토끼 자기 강화](evidence/comparison/s_mon_drumming_bunny_player.png), [킹 블록퍼스 밀치기](evidence/comparison/s_mon_king_clang_monster.png)
- [시그너스 구역](evidence/comparison/s_mon_cygnus_player.png), [변형 스텀피 뿌리](evidence/comparison/s_mon_mutant_stumpy_monster.png)
- 전체 66종의 수정 전 원본 캡처: `evidence/player/`, `evidence/monster/`, `VFX_BOARD_01_05.png`부터 `VFX_BOARD_66_66.png`까지의 Contact Board. 수정 후 캡처: `after_final/evidence/`; 짧은 프레임의 보충 캡처는 `after_fast/evidence/`.

## Build, Runtime, 보존

- Maker Stop → Refresh → 새 Play를 실제 실행했다. 마지막 Build Console: **Error 0, Warning 2, Info 13**. Warning 2는 기존 마노 `MovementComponent.InputSpeed`, 보우마스터 `AvatarAttackPlayRate` 모델 경고다. Info에는 새 `PlayAreaAt`의 정적 추론 알림 1건이 있으나 실제 Player/Monster 호출은 성공했다.
- 마지막 Runtime Console 6,658건에서 Error/Exception/stack traceback 0건. 시전 성공은 `[SkillVFXQA] DONE side=... id=... accepted=8 qaOk=true`로 판별했다. 캡처는 실제 Maker 화면이며, 독립적인 아트 생성물이 아니다.
- `SkillTable.csv` SHA-256: `12EA875FF194A721CB1491D4CA3B45ACD0156D7B6ABA25EAF95130E9BD848A32` — 작업 전과 동일. `MonsterTable.csv` SHA-256: `6783014B6990F67988B4D17D5AE3B0B741896433FCEFE3849449B7E06073B5E2` — 변경 없음. SkillID/Monster 연결·피해 계수·판정·스킬 역할·Tooltip·Icon/PNG·5초 공급·슬롯 규칙은 변경하지 않았다.
- 게임 소스 수정: `RootDesk/MyDesk/Combat/SkillEffect.mlua`, `RootDesk/MyDesk/Combat/SkillCastEffect.mlua`, `RootDesk/MyDesk/PlayerAttack.mlua`, `RootDesk/MyDesk/MonsterAttack.mlua`. PlayerAttack/MonsterAttack의 변경은 **VFX 호출 위치와 중복 재생 억제**, 약화 적용 성공 시 표식 호출뿐이다. 검수 스크립트·보고서·작업 원장도 갱신했다.
- 이 검수는 별도 격리된 Maker 테스트 맵의 반복 시전과 화면 표본이다. 실제 모든 Area·Boss 조합, 모든 애니메이션 프레임, 여러 클라이언트 동시 화면은 검증하지 않았다. 원화의 최종 사용자 승인도 대체하지 않는다.
- git commit/push는 하지 않았다.
