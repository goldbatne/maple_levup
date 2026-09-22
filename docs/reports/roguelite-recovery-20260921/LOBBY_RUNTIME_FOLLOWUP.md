# 로비 → 실제 Run → 로비 후속 검증

2026-09-21. 실행 프로젝트 `D:/maplestory_levup`. 브랜치 `codex/art-packages-cleanup-20260915`, HEAD `2eb7498eda8f53440648ef6107d6c933ba55d5c6` + 기존 미커밋 변경. 아래 시각은 Maker 로그 원문이다.

## 결론

실제 정적 maptown에서 시작하면 Run 인스턴스 입장과 실패/클리어 후 로비 복귀가 모두 `moved=1`이다. 과거 `moved=0`은 인스턴스 맵에서 직접 Play하여 `TestPlayInstance`에서 시험했던 조건과 구분해야 한다. 이번 결과만으로 모든 Area/지형/협동 검증 완료를 의미하지 않는다.

## 원본 보호 및 변경

- 사용자 승인에 따라 Maker Save 호출 → maptown 전환. Save 도구의 응답은 비동기 요청 접수이므로 별도 저장 완료 콜백으로 표현하지 않는다. 이후 Refresh/Play 가능했고 새 엔트리 저장 실패는 로그에서 발견되지 않았다. Maker 재시작 내구성은 NOT_RUN.
- 복원 자료 `pre-lobby-save-20260921.tar`: 464개 파일, 25,733,632바이트. SHA-256 `5471f5f9f8d1bf663b2729c8181f1a9b02966a7b6b04edb8dcdd93f3a2cb9ef7`. 생성과 Save 요청이 시간상 겹쳤으므로 원자적 저장 전 스냅샷이라고 주장하지 않는다. Save 후 코드 수정 전 비교에서 464개 파일 모두 현재 바이트와 동일했다.
- 이번 후속 소스 변경: `RootDesk/MyDesk/GameData/GameData.mlua`만. `CanStartRogueliteFromLobby`로 정적 maptown/Run 미실행/입장 중 아님을 서버 확인한다. 준비·시작 요청에 공통 적용하고 `RogueStartingUsers`로 중복 시작을 잠근다.
- 실제 Room 생성을 우회하던 TestPlayInstance 전용 시작 분기를 제거했다. Maker 검증도 maptown에서 시작해야 한다. 스킬 고유 동작 변경 없음.
- SkillTable SHA-256 `3a4af00f0cc9ef3439e9c4cbda4e80f0cfe86cd4072202ad5b08a994a5828c36`, MonsterTable `6783014b6990f67988b4d17d5ae3b0b741896433fcefe3849449b7e06073b5e2`: 이전 기준과 동일. 감사 baseline/별도 rework/맵/VFX를 수정하지 않았다. reset·커밋 없음.

## 실제 검증

|항목|근거|판정 및 범위|
|---|---|---|
|Refresh/Build|최종 Build Console Error 0, Warning 2|경고 2개는 07:20:16 기존 기록(mano InputSpeed, bowmaster AvatarAttackPlayRate). 새 오류 없음|
|로비 기동/실제 Run|08:10:13 maptown → 08:10:14 seed92121 moved=1|실제 server_main → 신규 인스턴스|
|실패 후 로비|08:10:49 실패 → 08:10:52 moved=1 → 08:10:59 maptown active=false|OnRunPlayerDied 시험 호출. 자연 피격 사망 검증 아님|
|Area 선택·준비·시작|08:12:16 UI 컨트롤러 Show/Choose → seed535623 moved=1|실제 UI 컨트롤러 호출. 물리 마우스 클릭 성공으로 집계하지 않음|
|자연 처치·능력|08:12:28 달팽이 사망, slot1 s_mon_snail_dew_trail|실제 기본공격 경로. 능력 주입 아님|
|사용/내부 이동 쿨다운|08:13:13 SkillBar 사용 후 readyAt=37.304; map004와 map003에서도 같은 값|SkillID 기한 보존. 이동 시점까지 유효 잔여 시간이 있었다고 단정하지 않음|
|연속 포탈/클리어|08:13:13~19 r001→r004→r003→r00a, COMPLETE 및 기록 저장|포탈 좌표로 위치 보조 후 실제 자동 트리거. 자연 탐색 완주/타일 전수 검증 아님|
|종료 정리/복귀|08:13:22 readyAt=nil 및 moved=1; 08:13:39 maptown active=false slot1=nil|이전에 존재하던 쿨다운 키 제거 확인|
|다음 Run|08:13:40 seed92123 moved=1·빈 5슬롯, 08:13:53 신규 달팽이 처치/획득|새 인스턴스 시작 확인. 이 seed는 fallback valid=true 로그가 있어 생성 정책 검증은 별도 미완료|
|중복 시작 방지|08:15:58 seed92124/92125 연속 요청 중 92124만 시작|단일 클라이언트 요청 재진입 검사 통과|
|Run 중 재시작 방지|08:16:22 내부에서 시작/준비 요청 각각 거부|새 인스턴스 추가 없음|

선별 원문 로그: `lobby-runtime-evidence.json`. 계정 식별자는 마스킹했고 저장 payload는 넣지 않았다.

## 오류·경고 구분

- 테스트 조회문이 없는 `RunSkillSlots`(08:12:32), `PlayerStats.HP`(08:13:02)를 참조해 오류를 냈다. 실제 슬롯 필드는 `RandomSlots`다. 이는 테스트 도구 조회 오류이며 게임 실행 코드 오류로 집계하지 않는다. 콘솔 전체가 무오류였다고도 표현하지 않는다.
- maptown의 RoomBounds RectTileMapComponent 탐색 경고, Portal_E Legacy TriggerComponent 및 TownGate/RoomPortal 중복 책임 경고는 잔존한다. 임의 컴포넌트 삭제 없음.
- 전체 작업 트리 `git diff --check`는 기존 CRLF를 포함한 방대한 공백 경고로 실패했다. 관련 소스/Phase 문서만 `core.whitespace=cr-at-eol`로 검사한 결과는 통과. 무관한 파일 포맷을 일괄 변경하지 않았다.

## 남은 작업

1. 생성 fallback의 도달형 최종방/주경로/가지길 계약, 생성 실패 시 입장 방지. 전체 Area/Seed 검사와 실제 타일 통과 검사는 아직 완료되지 않았다.
2. UI 전체 메뉴 ESC/Mask/실제 클릭/모바일 및 획득 패널 효과 설명 점검.
3. 자연 사망·부활, 투사체/돌진/광역 지형 판정 및 동시 입력 회귀.
4. 실제 2/3/4인 협동·이탈·재접속: NOT_RUN. 1클라이언트만 실행했다.
5. 엔트리 저장 재시작 내구성, 모델 경고 및 town 경고 처리.
6. 시작 잠금 중 native Room API 예외가 발생하는 실패 경로는 미검증이다.

Maker는 마지막에 중지했고 편집 맵은 maptown이다. 다음 Play도 maptown을 기준으로 한다. 전체 복구 완료/아트 승인/협동 지원 완료 판정은 하지 않는다.
