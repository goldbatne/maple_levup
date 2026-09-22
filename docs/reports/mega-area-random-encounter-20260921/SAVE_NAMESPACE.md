# 저장과 서버 상태 분리

## 영구 기록

DataStorage 키 `RoguelitePermanentV1`에 다음만 저장한다.

- 발견 몬스터
- 발견 능력
- Mega Area 클리어 기록
- 선택 조우 기록
- 키 설정 등 승인된 설정

레거시 RPG/M2 저장 키는 읽기 호환을 위해 보존하지만 신규 Run 전투력에는 합산하지 않는다.

## Run 상태

아래 값은 해당 InstanceRoom의 서버 권한 상태로 유지하고 Run 종료 시 폐기한다.

- MegaAreaID / Seed / Mode / CurrentSubzone
- 생성 그래프 / 역할 / 혼합 Encounter / 보스
- 참가자 / 생존 / 연결 이탈 시각
- 플레이어별 OwnedSkillPool / 5칸 재고 / 다음 공급 시각
- HP / 포션 드롭 엔티티
- Objective / Clear / Fail
- 실제 피해 원장과 결과 요약

서버 프로세스 재시작을 넘기는 중간 Run 복원 저장은 이번 범위에서 만들지 않았다. 같은 InstanceRoom에 대한 기존 참가자 재합류 상태는 서버 원장이 권한 있게 유지한다.
