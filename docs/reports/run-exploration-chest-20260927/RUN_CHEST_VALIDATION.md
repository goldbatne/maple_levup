# 탐험 상자 + Run 랜덤 강화 검증

- 검증 일시: 2026-09-27 KST
- 프로젝트: `D:/maplestory_levup`
- Maker Run: `mega_01`, Seed `271828`, Solo 1P

## 구현 범위

- 일반 몬스터 포션 드랍 비활성화 (`run_potion_drop_rate=0`)
- Seed 기반 탐험 상자 배치
- 회복 상자: 최대 HP의 30% 즉시 회복
- 강화 상자: 현재 상한 미도달 항목 중 균등 추첨, 즉시 적용
- Run 강화 8종과 중첩 상한
- 별도 `Run 강화` HUD 창
- Run 종료 시 상자/개인 강화 상태 초기화

## Seed 재현

동일 Seed `271828`로 Run을 두 번 시작했을 때 아래 5개 상자의 방, 종류, 좌표가 동일했다.

| Room | Map | Type | Position |
|---|---|---|---|
| r_003 | map003 | UPGRADE | (4.268, 1.367) |
| r_002 | map002 | HEAL | (6.536, 1.848) |
| r_02 | map02 | UPGRADE | (7.830, 0.406) |
| r_13 | map13 | UPGRADE | (-4.760, 4.996) |
| r_007 | map007 | UPGRADE | (-8.625, 1.639) |

시작/최종 방에는 상자가 생성되지 않았고, combat/optional_risk 방에만 확률 규칙이 적용됐다.

## Runtime 결과

- 강화 상자 실제 상호작용: `move_speed` 1스택 획득, 상자 제거 PASS
- Run 강화 창: 획득 항목만 `이동속도 +10% ×1`로 표시 PASS
- 회복 상자 실제 상호작용: MaxHP 1000 기준 300 회복 로그 PASS
- 재방문: 이미 연 상자는 다시 생성되지 않음 PASS
- 일반 몬스터 처치: SkillDrop 판정 유지, `[RunPotion] disabled ... dropped=false` PASS
- 다음 Run 초기화: 강화 요약 비어 있음, 공격 간격 0.55, MaxHP 1000, 이동속도 2.4 복원 PASS
- Runtime clean pass: 상자 생성/상호작용 구간 Error 0

## 강화 전수/상한

실제 `RollRunUpgrade` 경로를 반복 실행해 8종 모두 상한까지 도달시켰다.

| Upgrade | Stack |
|---|---:|
| 기본 공격 속도 +15% | 3/3 |
| 기본 공격 피해 +15% | 3/3 |
| 기본 공격 사거리 +15% | 3/3 |
| 기본 공격 추가 대상 +1 | 2/2 |
| 기본 공격 관통 +1 | 2/2 |
| 이동속도 +10% | 3/3 |
| 최대 HP +15% | 3/3 |
| 받는 피해 -10% | 3/3 |

모든 항목 상한 뒤 반환값은 `key=FULL`, `label=모든 Run 강화가 최대 단계입니다.`였다.

적용값 확인:

- 공격 간격: 0.55 → 0.3793103448 (설정 하한 0.30 준수)
- 기본 공격 계수: 1.20 → 1.74, 동일 적 실피해 36 → 52
- 최대 HP: 1000 → 1450, 증가분 450만큼 현재 HP도 증가
- 이동속도: 2.4 → 3.12
- 받는 피해 감소 조회: 0.30
- 추가 대상 Runtime: 한 공격에서 서로 다른 2개 몬스터 동시 피격 확인

## Build / 제한

- Build Error: 0
- 기존 Warning: 2 (`mano` InputSpeed, `bowmaster` AvatarAttackPlayRate)
- 실제 멀티클라이언트 2~4P 상호작용: NOT_RUN
- 파티별 개인 개방/보상과 전원 개방 뒤 제거 로직은 서버 코드 경로로 구현됐으나 이번 Maker 환경에서는 1P Runtime만 확인했다.

## 변경하지 않은 영역

66 Skill 기능/VFX, Skill Drop 확률/규칙, 5슬롯/공급 규칙, Portal, Party 구성, Respawn, Boss 구조는 재설계하지 않았다.
