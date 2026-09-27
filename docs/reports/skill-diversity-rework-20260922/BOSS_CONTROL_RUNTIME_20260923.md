# 보스 제어 효과 Maker 검사 (2026-09-23)

Maker Play의 기존 `map05`에서 실제 스폰된 머쉬맘(`RoomMonster:IsBossRoom()=true`, 시작 HP 9650)을 대상으로 했다. `PlayerAttack.ApplySecondaryEffects`에 실제 보스 충돌 컴포넌트를 전달해 공통 제어 어댑터를 실행했다. 이는 스킬 키 입력부터 피해 판정까지의 통합 검사는 아니다.

| SkillID | 효과 | 관찰 |
|---|---|---|
| `s_mon_mushroom` | SLOW | 보스 `SlowRatio=0.0875`, 위치 이동 없음 |
| `s_mon_tauromacis` | STUN | 보스 `StunUntil` 잔여 약 0.1845초, 위치 이동 없음 |
| `s_mon_fairy` | WEAKEN | 보스 `WeakenRatio=0.063`, 위치 이동 없음 |
| `s_mon_king_clang` | KNOCKBACK | 보스 위치 이동 없음 |
| `s_mon_dodo` | PULL | 보스 위치 이동 없음 |

각 검사 사이 `ResetSkillControls()`를 호출했고 종료 시 다시 초기화했다. 위 수치는 `boss_control_scale=0.35`가 적용된 결과다. 보스를 맵 밖으로 옮기지 않는 정책은 관찰됐지만, 보스 전투 중 실제 플레이어 스킬 적중·시각 효과·연속 기절 안전성은 별도 검사 대상이다.
