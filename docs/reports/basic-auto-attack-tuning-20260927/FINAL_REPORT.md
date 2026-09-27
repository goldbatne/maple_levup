# 기본/자동 공격 전투 체감 1차 조정

검증일: 2026-09-27 KST

## 변경 범위

- `GameBalance.csv`
  - `player_attack_interval`: `1.0` -> `0.55`
  - `player_attack_target_scan_interval`: `0.10` 신규 설정
- `PlayerAttack.mlua`
  - 공격 가능 시각(`nextAutoAttackAt`)과 대상 탐색 타이머를 분리했다.
  - 탐색은 0.10초마다 수행하되 실제 공격은 0.55초보다 빨라지지 않는다.
  - 대상이 없던 탐색 틱은 공격 주기를 소비하지 않는다.
  - 기본 공격의 단일 대상, 사거리 1.0, 피해 계산, 최근접 대상 선택은 유지했다.

## Before / After

| 항목 | Before | After |
|---|---:|---:|
| 기본 공격 간격 | 1.00초 | 0.55초 |
| 이론상 초당 공격 횟수 | 1.00 | 1.82 |
| 대상 탐색 반응 | 공격 타이머와 결합 | 0.10초 독립 탐색 |
| 기본 공격 피해 | 36 | 36 (변경 없음) |
| 일반 몬스터 HP / DEF | 240 / 6 | 240 / 6 (변경 없음) |
| 일반 몬스터 필요 타수 | 7회 | 7회 (변경 없음) |
| 첫 타격~7타 처치 시간 | 약 6.0초 | 약 3.3초 |

## Maker 자연 전투 결과

- Skill 0 상태: 실제 Run 첫 전투에서 기본 공격만으로 달팽이 1마리를 처치했다. 피해 36, 7타 구조를 확인했다.
- 1마리: 공격 텀이 눈에 띄게 줄었고 처치 후 Skill Drop이 정상 생성됐다.
- 3~4마리: 다수 접근 시 단일 기본 공격만으로 안전하게 정리되지는 않았다. 기본 공격은 안정적인 보조 수단이고 Skill의 가치가 유지됐다.
- 6~10마리 Mixed Encounter: 실제 Room에서 다종 몬스터를 대상으로 연속 공격을 확인했다. 초 단위 로그에 동일 초 2회 공격이 반복되어 0.55초 cadence가 적용됐다.
- Target 전환: 파란 달팽이 처치(`14:30:10`) 뒤 다음 다크 엑스텀프 공격(`14:30:11`)으로 이어졌다. 죽은 대상 고정이나 1초 전체 재대기는 관찰되지 않았다.
- Skill Drop 전/후: 바닥 Drop을 E로 획득한 뒤 기존 5초 공급과 슬롯 표시가 정상 동작했다.
- Skill 사용 후: Z 스킬 사용으로 한 슬롯이 소비된 뒤 기본 공격이 다음 주기부터 다시 이어졌다.
- Portal 이동 후: 이전 자연 Run에서 `map004 -> map04` 이동 뒤 기본 공격이 자동 재개됐다.
- Boss: 활성 Mega Run(`mega_01`, seed `2226463`)의 실제 그래프 경로를 플레이어 키 입력으로 통과해 `r_05 / map05` 보스실에 도달했다. 머쉬맘 HP 960에 기본 공격 36이 `960 → 924 → 888 → 852 → ...`로 연속 적용됐고, 2026-09-27 16:04:01~16:04:07 로그에서 약 0.5~1.0초 단위(설정 0.55초)의 반복 타격을 확인했다. 보스 공격(23 피해)과 기본 공격이 동시에 정상 처리됐으며, 이후 Run 완료 및 로비 복귀까지 확인했다. 기본 공격만으로도 보스에 지속 기여할 수 있지만 27회가 필요한 구조라 Skill의 순간 화력·다수전 가치가 유지된다. `PASS_RUNTIME`.

## 로그 근거

- 변경 후 설정 로그: `자동 공격 주기 0.55초 / 대상 탐색 0.1초`
- 기본 공격: `ATK=35 vs DEF=6.0`, 계수 `1.200`, 피해 `36`
- 일반 몬스터: HP `240`, DEF `6`
- `14:30:06~14:30:10`: 파란 달팽이 7타 처치
- `14:30:10~14:30:14`: 다음 다크 엑스텀프 자동 전환 및 연속 공격

## 시각 증빙

- 1마리 처치 및 Skill Drop: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260927_143006_057.png`
- Skill Drop 획득 후 5슬롯 공급: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260927_143038_942.png`
- 3~4마리 이상 접근 조우: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260927_143154_773.png`
- 보스 맵 확인(활성 Run 밖, PASS 근거 아님): `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260927_143833_742.png`
- 실제 Run 보스실 진입: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260927_160244_179.png`
- 실제 Run 머쉬맘 교전: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260927_160346_548.png`

## 빌드 / 런타임

- Maker Build: Error 0, Warning 2 (기존 `MovementComponent.InputSpeed`, `MonsterAttack.AvatarAttackPlayRate` 경고)
- 최종 clean restart 이후 Runtime Error/Fatal: 0
- 긴 검증 세션 중 Error 2건은 프로젝트 코드가 아니라 진단용 `MakerScript` 호출에서 발생했다. 최종 재시작 구간에는 재발하지 않았다.

## 범위 준수

- 피해, 사거리, 단일 대상 수를 변경하지 않았다.
- Skill Drop, 66 Skill, VFX, Random 5 Slot, Respawn, Party, Portal, Boss, Potion 확률을 변경하지 않았다.
- git commit/push를 수행하지 않았다.
