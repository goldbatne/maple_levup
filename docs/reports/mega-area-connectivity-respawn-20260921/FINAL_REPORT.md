# Mega Area 연결·리스폰 마무리 보고서

- 프로젝트: `D:\maplestory_levup`
- 검증일: 2026-09-21 KST
- 범위: 기존 Mega Area 5개 구조의 포탈 연결, 탐험 리스폰, UI 정리, 보스 전용 클리어
- 비범위: 신규 장르/스킬/VFX/성장/Area/Boss/Mode 추가

## 결과 요약

- Maker Refresh: PASS
- Build: Error 0, 기존 모델 Warning 2 (Mano InputSpeed, Bowmaster AvatarAttackPlayRate)
- 정적 전수: map 파일 163개, RoomTable 160개, 레거시 연결 333개
- Mega Run 후보 내부 방향 호환 도달 불가 맵: 0개
- 생성 그래프 실제 포탈 왕복: 총 110/110 PASS
- 탐험 일반몹 리스폰: 6~10초 지연, 목표 개체수 복원 PASS
- 보스방 일반 개체 리스폰: 비활성 PASS_STATIC
- 보스 전용 클리어: 5/5 PASS_RUNTIME
- 실패/로비 복귀/인스턴스 정리: PASS_RUNTIME
- UI: 레거시 월드맵·컬렉션 미노출, 간결 목표 HUD, 소형 획득 토스트, OwnedSkillPool 분리 PASS_RUNTIME

## 실제 수정

- `RootDesk/MyDesk/Room/RoomPortal.mlua`: 생성 그래프 edge 기반 포탈 활성화, 실제 반대 포탈 도착, 미사용 레거시 포탈 비활성
- `RootDesk/MyDesk/Room/RoomSpawner.mlua`: 비보스 탐험방 지연 리스폰, 부족분 재계산, 안전 스폰
- `RootDesk/MyDesk/GameData/GameData.mlua`: 6~10초 리스폰 설정, 정확한 최종 보스 사망만 클리어
- `Mislocated/MyDesk/GameData/GameBalance.csv`: 리스폰 지연·플레이어 안전거리 설정
- `RootDesk/MyDesk/UI/RoomProgressHud.mlua`: 목표 HUD 압축
- `RootDesk/MyDesk/UI/SkillBar.mlua`, `ui/SkillBar.ui`: 보유 능력과 전투 재고 분리, 소형 토스트
- `RootDesk/MyDesk/UI/EquipPanel.mlua`: Run 컬렉션 UI 비활성
- `RootDesk/MyDesk/UI/WorldMapPanel.mlua`: Run 레거시 지도 비활성
- `RootDesk/MyDesk/Progress/PlayerCollection.mlua`: 능력 획득 중앙 중복 배너 제거
- `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`: 획득 토스트 전달

## 포탈

`RoomPortal.RefreshRunBinding`은 현재 생성된 `RogueGraph[roomId][direction]`가 있을 때만 포탈을 켠다. 전환 시 목표 맵의 실제 역방향 RoomPortal 위치를 찾아 안쪽으로 2.5 world unit 이동한 안전 도착점을 쓴다. 목표 포탈이 없으면 근사 좌표로 강행하지 않고 전환을 거부한다.

Maker에서 5개 Seed의 생성 그래프를 깊이 우선 왕복하며 모든 활성 edge를 실제 Trigger 진입으로 확인했다. 상세 110행은 `PORTAL_RUNTIME_EXHAUSTIVE.csv`에 있다.

## 리스폰

일반 탐험방은 생존 개체가 Encounter TargetPopulation보다 적어지면 6~10초 뒤 부족분을 다시 계산하여 보충한다. 리스폰 위치는 맵 타일/충돌, 포탈, SpawnLocation, 플레이어 안전거리를 검사한다. 리스폰 몬스터는 기존 RoomMonster 사망 경로를 그대로 사용하므로 능력 판정, 독립 포션 RNG, 피해 장부가 유지된다. 최종 보스방은 일반 Population 리스폰 대상이 아니다.

## 보스 전용 클리어

최종 맵 도착 상태에서 `complete=false`, `objective=false`를 확인한 뒤 정확한 `RogueBossMonsterId`를 실제 기본공격으로 처치했다. 5개 Mega 모두 `[MegaBossClear]` 뒤에만 완료되었고 인스턴스가 닫힌 뒤 maptown으로 복귀했다.

## UI

Run 화면에는 디버그 그래프/Seed/Pool/Supply 텍스트와 레거시 월드맵·컬렉션이 없다. 목표는 “보스를 찾아 처치하세요.”만 보여 준다. OwnedSkillPool은 고유 능력 수/아이콘을 보여 주고, 아래 5칸 랜덤 전투 재고와 분리된다. 능력 획득은 상단 소형 2.5초 토스트만 표시하며 중앙 GateNotice 중복은 제거했다.

## 런타임 주의

- 포탈 전수 QA는 플레이어를 실제 활성 포탈 Trigger 위치로 이동시켜 `OnTriggerEnter -> TryPass` 전환과 목표 CurrentMap을 확인했다. 맵 이동 API로 성공을 위조하지 않았다.
- 보스 처치는 보스 HP만 QA용으로 1로 낮춘 뒤 기존 자동 기본공격/HitEvent/RoomMonster.Dead 경로를 사용했다.
- 리스폰은 실제 기본공격 사망과 6.86초/8.14초 타이머 후 Population 복원을 확인했다.
- 독립 2~4인 멀티클라이언트는 이번 범위에서 실행하지 않았다. 기존 단일 Maker 클라이언트 제약과 동일하다.

## 판정

현재 Maker 단일 클라이언트에서 수행 가능한 Mega Area 연결·리스폰·UI·보스 클리어 마무리는 완료했다. 실제 2~4인 독립 클라이언트 동시 검증만 환경 제약으로 BLOCKED이다.
