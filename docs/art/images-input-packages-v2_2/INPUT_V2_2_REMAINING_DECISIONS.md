# Runtime and design conflicts — V2.2

## AREA 20 / s_mon_mutant_stone_mask

- 확정 데이터: passive_stat=DEF (변경하지 않음).
- GameDataVerify는 STR/DEX/INT/LUK만 허용해 DEF를 오류로 기록한다 (`GameDataVerify.mlua:188-200`).
- PlayerStats.GetCollectionPoints는 전달받은 이름과 passive_stat이 같은 항목을 합산하지만, GetCollectionBonus("DEF")는 DEX 포인트만 사용한다 (`PlayerStats.mlua:527-576`). DEF collection point를 파생 방어력에 더하는 호출은 확인되지 않았다.
- 결론: 현행 계산에서 스킬 passive_stat=DEF는 방어력 보너스로 소비되지 않는 기획/실행 충돌이다. 게임 데이터·검증·계산 코드는 V2.2에서 변경하지 않았다.
- GENERATION_READY는 아트 입력 기준 READY, RUNTIME_VALIDATION은 UNRESOLVED다.

## Current Maker SkillTable

- 정상 경로 SkillTable 파일은 삭제 상태이며 Mislocated 후보가 있다. `_DataService:GetTable("SkillTable")` 이름 조회만으로 현재 Maker 등록 EntryKey를 식별할 수 없다.
- V2.2는 기준 커밋 데이터와 V2.1 확정 패키지를 사용하지만 현재 Maker 등록 테이블과 같다고 단정하지 않는다. RUNTIME_VALIDATION=NOT_RUN.

## Six dash skills

- 플레이어 피해점은 계산 도착점, PlayCast는 호출 뒤 서버가 보는 caster 위치를 사용하므로 일치가 보장되지 않는다.
- 지연 CAST는 Timer 후 SpawnLayer 실행 시점의 caster 좌표를 읽고, 스폰 뒤 맵 엔티티에 drift가 적용된다.
- 몬스터 공통 CastSkill에는 dash_distance 이동 분기가 없다. 경고를 유지하며 이번에 코드를 바꾸지 않는다.

## Projectile scope

- 비행/피해 지연 0.35초와 착탄 반경 0.8wu는 유지했다.
- 스텀피만 PROJECTILE+ICON 교체 계획이다. 나머지 11종 projectile_ruid는 KEEP이며 추가 승인 없이 비행체 아트 범위를 늘리지 않았다.
