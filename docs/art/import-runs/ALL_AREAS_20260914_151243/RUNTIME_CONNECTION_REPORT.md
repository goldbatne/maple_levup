# AREA 스킬 아트 Maker 실행 연결 검증

- 검증일: 2026-09-14
- 검증 월드: `6ab29f6a728e4b33931679be708ca6b1`
- Play 맵: `map001`

## 결과

**PASS**

- 검증 AREA: 20개(AREA 00–05, AREA 07–20)
- AREA 06: 반입 대상 없음
- AREA별 스킬 확인: 104건
- 중복을 제외한 고유 스킬: 101개
- 실제 VFX 시전 요청: 69건
- 다층 이펙트 스폰 로그: 72건
- `SkillEffect` 오류: 0건
- 빌드 오류: 0건

일부 스킬은 다층 레이어를 사용하므로 VFX 시전 요청 수보다 스폰 로그가 3건 많다.

## 실제 확인 경로

각 AREA마다 Play 상태의 `server_main`에서 다음을 수행했다.

1. `_GameData:GetSkill(skill_id)`로 스킬 로드
2. `icon_ruid`가 비어 있지 않은지 확인
3. VFX 대상은 `effect_ruid` 또는 `effect_layers`가 존재하는지 확인
4. 실제 플레이어 엔티티를 caster로 사용해 `_SkillEffect:PlayCast(...)` 호출
5. `[다층 이펙트]` 스폰 로그와 `SkillEffect` 오류 로그 확인

AREA별 증거는 `AREA_XX_RUNTIME_CONNECTION.json`에 저장했다.

## SkillTable 등록 확인

`SkillTable` 파일은 로컬에서 `Mislocated/MyDesk/GameData`에 있지만, Play 상태에서 `_GameData:GetSkill`이 전체 대상 스킬을 정상 반환했다. 따라서 현재 Maker 세션에는 이름 `SkillTable` 데이터셋이 실제 등록되어 있으며, 앞선 등록 불확실성은 해소됐다.

## 빌드 경고

스킬 아트 연결과 무관한 기존 경고 2건이 남아 있다.

- `model://mano`: `MovementComponent.InputSpeed`
- `model://bowmaster`: `MonsterAttack.AvatarAttackPlayRate`

빌드 오류는 없다.

## 검증 범위

이번 검증은 데이터 로드와 실제 이펙트 스폰 연결을 확인했다. 각 프레임의 화면상 크기·pivot·애니메이션 미감은 별도의 시각 검증 범위다.
