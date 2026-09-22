# Maple Levup — Phase 3.6 순수 확률 포획

> 2026-09-16 기준. Phase 4 전에 실제 첫 액티브 포획 경로를 확인하고 신규 모드 천장을 제거한다.

## 확정 계약

- 첫 획득(`OwnedSkills[skill_id] == 0`): 10%.
- 중복 획득(1～4장): 3%.
- 5장: 판정하지 않는다.
- 신규 모드에는 확률 외 강제 성공 조건이 없다.
- `first_capture_pity`와 `duplicate_capture_pity`는 레거시 데이터로만 보존한다.
- 패시브 35종은 판정·획득·알림·랜덤 풀에서 제외한다.
- 중복 강화 ×1.0～×1.8과 보유 장수에 무관한 균등 추첨은 유지한다.

## 포획 공식

`base_rate × capture_rate_global_multiplier × collection_capture_multiplier × monster_capture_modifier`

- `collection_capture_multiplier=1.0`: 향후 확장 Hook이며 현재 성장 효과는 없다.
- `capture_rate_max=1.0`: 최종 상한. 현재 10%/3%에는 영향이 없다.

## 저장 호환

- `SpeciesKills`는 schema v3까지의 포획 실패 카운터로 레거시 보존한다.
- 기존 값을 누적 처치 통계로 마이그레이션하지 않는다.
- schema v4의 `TotalMonsterKills`를 0부터 시작해 성공·실패·패시브·만작과 무관한 실제 처치 통계로 저장한다.
- `OwnedSkills`, 인벤토리, 장비, 보스 기록과 기존 `SpeciesKills`는 그대로 왕복한다.

## 검증 체크리스트

- [x] 첫 액티브의 MonsterTable → SkillTable → OwnedSkills 경로 일치
- [x] 실제 10% 자연 성공과 획득 알림 확인
- [x] 첫 획득 직후 랜덤 풀 반영과 다음 5초 공급 확인
- [x] 중복 3% 자연 성공과 1→2, ×1.2 확인
- [x] 신규 모드에서 천장 강제 성공 없음
- [x] 성공 전후 TotalMonsterKills 연속 증가, SpeciesKills 불변
- [x] 패시브 35종 포획 제외 회귀
- [x] 저장 후 재접속에서 OwnedSkills와 TotalMonsterKills 유지
- [x] Maker 빌드·런타임 오류 0

## Maker 검증 기록

- 주황 버섯 실제 처치 13번째: `roll=0.0107 < 0.1000`, 첫 `포자 살포` 획득.
- 다음 실제 처치 중 `roll=0.0167 < 0.0300`, 2장째 획득. 계수는 `1.10 → 1.32`로 정확히 ×1.2 증가했다.
- 첫 획득 뒤 액티브 풀에 `s_mon_mushroom`이 즉시 포함됐고, 빈 재고에 5초 간격으로 한 칸씩 공급됐다.
- 공급된 스킬 사용 성공 후 해당 칸만 소비됐고 기존 VFX가 정상 재생됐다.
- 패시브 `s_mon_horny_mushroom`만 보유한 상태에서는 풀 0종, 5초 뒤에도 슬롯이 비어 있었다.
- schema v4 저장 후 재접속에서 보유 2장과 누적 처치 22가 왕복했다. 검증 종료 후 시작 시점 저장(보유 1장, 레거시 실패 3, 신규 누적 0)으로 복구했다.
- 최종 Maker 로그: 빌드 오류 0, 런타임 오류 0. 기존 모델 경고 2건은 이번 변경과 무관하다.

## 범위 밖

맵 축소, 탑, 레이드, 장비 재설계, 실제 컬렉션 성장 배율, 패시브 액티브화, Trait 복구는 수행하지 않는다.
