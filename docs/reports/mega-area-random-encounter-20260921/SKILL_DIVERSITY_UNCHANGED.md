# 스킬 다양성 보존 확인

- 기준: 기존 스킬 다양성 감사 보고서와 현재 `SkillTable`.
- 현재 플레이어 사용 가능 액티브/방어 스킬: 66개.
- 역할 집계: Center 44 / Projectile 12 / Rush 7 / Defense 3.
- `SkillTable.csv`와 `SkillTable.userdataset`은 이번 개편에서 바이트 변경 없음(`git diff --exit-code` 0).
- 피해 계수, 범위, 사거리, 지속시간, 타격 횟수, 몬스터 연결, VFX RUID는 수정하지 않았다.
- 바뀐 것은 Run 사용 체계뿐이다: 스킬 획득 후 `OwnedSkillPool`에 고유 등록되고, 5초 공급으로 전투 재고에 복원 추출되며, 성공 사용 시 해당 재고 한 칸만 소비한다.
- Run 모드에서는 기존 스킬별 플레이어 쿨다운을 적용하지 않는다. Monster Skill 모드의 적 사용은 기존 `SkillTable.cooldown`을 사용한다.
