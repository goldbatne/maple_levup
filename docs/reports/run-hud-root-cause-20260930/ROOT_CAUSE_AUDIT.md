# Warning / Run HUD Root Cause Audit

대상: `D:/maplestory_levup`, 2026-09-30 KST. UI 스타일/좌표/밸런스/맵/모델/저장 포맷 변경 없음. commit/push 없음. 기존 미커밋 작업 보존.

## 결과

| Warning / Issue | Root Cause | Real Problem? | Repeated Noise? | Fixed? | Remaining Count | Why |
|---|---|---|---|---|---|---|
| Run HUD `gameRun=false`, `slotRun=true` | 별도 Sync 슬롯 상태와 일회성 RPC 뷰가 독립적으로 전달됨. 클라이언트 준비/맵 전환 후 정본을 재요청하는 복구 경로가 없었음 | YES | NO | YES, 준비 기반 초기화 + 서버 정본 재요청 | 연속 진입 실패 0/3 | 임의 active 대입/수동 Broadcast 없이 검증 |
| RoomBounds missing RectTile | 클라이언트 OnMapEnter가 타일 자식 준비보다 먼저 실행됨 | 실제 타일 누락은 관찰되지 않음; 진단 오분류 | YES | YES | 새 구간 Warning 0 | 기존 카메라 유지/기존 재시도. 서버 누락·재시도 최종 실패 Warning은 보존 |
| RoomPortal / TownGate | maptown Portal_E의 두 컴포넌트 공존. TownGate가 담당하므로 RoomPortal이 입력 등록 전에 반환하는 정상 보호 | 중복 생성 버그 아님 | YES | YES, Info로 변경 | 새 구간 Warning 0 | 입장 동작·토폴로지 변경 없음 |
| TriggerComponent Legacy / LWA-3019 | 기존 포탈 IsLegacy=true | 엔진이 지원/안정성을 보장하지 않는 기술 부채 | 같은 원인이 여러 엔티티·실행공간에 반복 | NO | 전체 새 검증 구간 223 | 새 충돌 방식은 Transform Scale/Rotation 영향이 달라 일괄 false 전환하지 않음 |
| RunChest ColliderType | 모델의 Int32 저장 타입과 native ColliderType enum 불일치 | 직렬화 문제 후보, 실행에서는 OnBeginPlay가 Circle 재설정 | 동일 기존 Build 진단 | NO | 1 | 정수 값 2를 임의 변경/삭제하지 않음 |
| RunChest CircleRadius | 모델 ValueType `number`와 native float 불일치 | 잘못된 타입 표기 확인, 실행에서는 범위 재설정 | 동일 기존 Build 진단 | NO | 1 | 실행 경로/범위 수치를 경고 억제 목적으로 바꾸지 않음 |
| Mano InputSpeed | 모델 Int32와 native float 불일치 | 직렬화 불일치, 실제 적용값 영향 미확정 | 동일 기존 Build 진단 | NO | 1 | 단순 타입 수리도 기존 무시되던 값을 적용할 가능성이 있어 보류 |
| Bowmaster AvatarAttackPlayRate | 모델 Single과 script `number` 선언 불일치 | 직렬화 불일치, 실제 적용값 영향 미확정 | 동일 기존 Build 진단 | NO | 1 | 기본 1.33/모델 1.55 중 현재 적용값을 Boss Runtime에서 검증하지 않아 보류 |

**Build Error 0, Build Warning 4 → 4.** Build 로그의 4개 모델 Warning은 여전히 2026-09-29T21:36:43의 진단 timestamp를 보유한다. 새 Refresh 뒤 Build 결과에서 계속 노출된다는 뜻이며, 새로 발생한 4개 오류라고 해석하지 않는다.

**Runtime Error: 전체 새 구간 1건.** 02:28:33 MakerScript가 @Logic인 AreaSelectPanel을 Entity Component로 잘못 조회해 `c=nil` 오류 발생. QA 호출을 `_AreaSelectPanel:StartSelectedRun()`으로 바로잡았다. 게임 코드에서 발생한 Runtime Error는 관찰되지 않았으며, 정상 Run 검증 시작 02:31:33 이후부터 Stop 02:50:58까지 Runtime Error 0. 과거/전체 Console Error 0이라는 의미가 아니다.

## 계수 기준과 증거

- 이전 Optical 세션 01:50~02:00:32의 73 Warning은 기존 `../ui-optical-polish-20260930/session-evidence.json` 재집계: Legacy 67 + TownGate 3 + Bounds 3. 73개 독립 결함이 아니다.
- 이번 수정 전 새 재현 구간(02:12:42~02:22:23): Legacy 66 + TownGate 2 + Bounds 2 = **70**. `before-evidence.json`.
- 수정 후 첫 Run까지, 포기 이전(02:27:59~02:32:15): Legacy 66 + TownGate 0 + Bounds 0 = **66**.
- 수정 후 전체 3 Run/왕복/보스/로비/Stop 구간(02:27:59~02:50:58): Legacy **223**, 기타 Warning **0**. 서버 187 / 클라이언트 36. 방문/재로딩 횟수가 달라 총수 223과 이전 70을 같은 노출량으로 비교하면 안 된다.
- `warning-counts.json`: Map/Portal별 발생 횟수. `after-evidence.json`: 원문 Warning, 스택, HUD/포탈/드롭/보스 증거. 사용자 식별자는 새 보고용 증거에서 마스킹.
- `preclear-warnings.json`, `pre-final-errors.json` 및 기존 모든 증거를 삭제하지 않았다.
- MCP execute_script 1회 응답 timeout(보스 구간 02:46 이후). 이 호출은 PASS 증거로 사용하지 않았고, 이후 실제 Portal/Boss/Clear 로그와 로비 상태 조회로 확인했다. 위 QA Runtime Error 1건과 별개의 도구 실패다.

## 1. Build Warning 원문

Maker MCP가 반환한 message 전문 그대로다. 이 도구의 Build 출력은 현지화된 문장 대신 MODIssue 마크업을 반환했다. 사람이 보는 렌더링 문장을 추측하여 만들어 쓰지 않았다. 모든 항목의 owner/subOwner는 null, stackTrace는 빈 배열이다. Entity 식별은 ownerId 사용.

### RunChest / InteractionComponent / ColliderType / LWA-4012

Entity: `model://runchest`

```text
<MODIssueFormat>LWA&Default&4012&0</MODIssueFormat><MODIssueArg>ColliderType</MODIssueArg><MODIssueArg>InteractionComponent</MODIssueArg>
```

### RunChest / InteractionComponent / CircleRadius / LWA-4012

Entity: `model://runchest`

```text
<MODIssueFormat>LWA&Default&4012&0</MODIssueFormat><MODIssueArg>CircleRadius</MODIssueArg><MODIssueArg>InteractionComponent</MODIssueArg>
```

### Mano / MovementComponent / InputSpeed / LWA-4012

Entity: `model://mano`

```text
<MODIssueFormat>LWA&Default&4012&0</MODIssueFormat><MODIssueArg>InputSpeed</MODIssueArg><MODIssueArg>MovementComponent</MODIssueArg>
```

### Bowmaster / MonsterAttack / AvatarAttackPlayRate / LWA-4012

Entity: `model://bowmaster`

```text
<MODIssueFormat>LWA&Default&4012&0</MODIssueFormat><MODIssueArg>AvatarAttackPlayRate</MODIssueArg><MODIssueArg>MonsterAttack</MODIssueArg>
```

ModelBuilder로 읽은 현재 모델: `RootDesk/MyDesk/Models/Items/RunChest.model`, `RootDesk/MyDesk/Models/Monsters/Mano.model`, `RootDesk/MyDesk/Models/Monsters/Bowmaster.model`. Native 정의는 `Environment/NativeScripts/Component/InteractionComponent.d.mlua`, `MovementComponent.d.mlua`. 스크립트 정의는 `RootDesk/MyDesk/MonsterAttack.mlua:74`.

확인한 값은 각각 2/Int32, 1.35/number, 1/Int32, 1.55/Single. `RootDesk/MyDesk/Inventory/RunChest.mlua:29`는 런타임에 enum Circle, CircleRadius=range를 다시 설정한다. 모델 타입 불일치는 확인했으나 4012의 엔진 내부 판단/적용값까지 완전히 확정했다고 주장하지 않는다. 이번에는 이 3개 모델을 수정하지 않았으며 Chest Interaction, Mano Boss, Bowmaster의 모델 변경 후 회귀는 **NOT_RUN(모델 변경 없음)**. 동행 마노의 전투 로그를 Mano Boss 회귀로 대신 집계하지 않는다.

## 2. Run HUD 원인과 수정

기존 실패 증거: 01:56:44 client `gameRun=false slotRun=true map=map001`; 01:58:01 server `active=true result=ACTIVE`; 01:58:14 수동 Broadcast 후 복구. 이번 수정 전 재현 Run은 정상으로 들어가 실패가 매번 발생하는 문제는 아니었다.

확인한 코드 경로:

1. 서버 PlayerDBManager 로드 완료 → GameData.RegisterRunParticipant → SendRogueliteView. 슬롯에는 TargetUser Sync 상태가 별도로 전달된다.
2. GameData의 RogueRunActive는 이 슬롯 Sync와 별개인 일반 상태. 클라이언트 ApplyRogueliteView RPC가 표시 상태를 갱신한다.
3. 기존 초기 UI 연결은 OnBeginPlay에서 0.5초 후 한 번 실행. UI가 늦게 준비되거나 맵 전환에서 뷰를 놓친 경우 클라이언트 ready 확인/정본 재요청이 없었다.
4. PlayerHud/RoomProgressHud는 GameData 상태를 사용하고 SkillBar는 슬롯 상태도 사용하므로 두 UI가 다른 ACTIVE 판단을 할 수 있었다.

**확정한 결함은 복구 불가능한 일회성 초기 전달 계약과 두 상태 채널의 불일치다.** 이전 실패 순간에 엔진이 정확히 어느 RPC를 버렸는지, 초기화가 직전 값을 덮었는지까지 보여주는 엔진 추적 로그는 없어 그 세부 이벤트 순서는 미확정이다. UI reset 코드가 ACTIVE를 명시적으로 false로 덮는 경로는 발견하지 못했다. 단순 네트워크 패킷 손실로 단정하지 않는다.

수정(`Mislocated/MyDesk/GameData/GameData.mlua`):

- OnUpdate: LocalPlayer와 필수 UI 엔티티가 실제 준비된 때 한 번 초기화. 기존 0.5초 타이머 제거, 새 고정 대기시간 추가 안 함.
- 기존 0.2초 UI 갱신에서 현재 맵과 마지막 수신 맵, 슬롯 Sync ACTIVE와 뷰 ACTIVE의 일치 여부 확인.
- 초기 준비/맵 변경/불일치 시 즉시 서버 snapshot 요청. 미해결 재요청은 1초 rate limit, 서버 0.5초 rate limit. 정상 동기화 상태에서는 요청 안 함. 8회 지연 시 진단 Warning 유지.
- 서버 senderUserId/현재 Entity/현재 맵/기존 Run 참가자 검증. 비활성 서버는 maptown 요청만 응답. 등록/진행/보상 상태를 바꾸지 않는 읽기 전용 RPC.
- payload에 viewMap 추가. 현재 맵과 다른 지연 응답은 무시하고 현재 맵 정본을 다시 요청.
- 기존 슬롯/HP/UI 디자인은 변경하지 않음. 테스트 중 수동 Broadcast나 RogueRunActive 강제 대입 없음.

## 3. RoomBounds

MapBuilder로 maptown/map001/map003의 RectTileMap 자식 존재와 448타일을 확인. 원래 RectTileMap이 없는 정상 방으로 판정한 것이 아니다.

수정 전 02:14:23 map001의 missing 경고 직후 같은 시각 타일 448칸 경계 계산과 카메라 적용 성공. 02:22:23 읽기 조회에서 ready=true/tiles=true. 수정 후에도 map001(02:33:57→02:34:00), map004(02:36:03)에서 준비 대기→정상 계산을 확인했다. 서버 경계는 정상 계산됐고 서버 누락 경고는 관찰되지 않았다.

- 임시 fallback: 새 타일 경계가 준비될 때까지 기존 카메라 설정 유지. 새 bounds를 임의 값으로 만들지 않음. roomReady=false 동안 해당 RoomCamera의 clamp를 건너뜀. 기존 0.1초 × 최대 40회 재시도 유지.
- 타일 준비 대기를 최초 한 번 Info로 기록. 서버의 실제 타일 부재/빈 타일/최종 재시도 실패 Warning은 유지.
- 마지막 재시도에서 성공했는데도 실패 Warning을 출력할 수 있던 조건을 `not applied`로 수정.
- RoomCamera bounds를 Companion/Monster/Portal이 직접 참조하는 경로는 검색에서 발견하지 못함. 카메라/플레이어 경계에는 준비 구간 영향이 있으나 이번 정상 이동/왕복에서 이상은 관찰되지 않음. 영구 누락 사례를 정상이라고 숨기지 않음.

## 4. TownGate / Legacy Trigger

maptown/Portal_E 한 엔티티에 RoomPortal과 TownGate가 함께 존재. RoomPortal.OnBeginPlay가 TownGate를 찾으면 Trigger 이벤트 등록 전에 반환한다. 이는 의도된 입장 담당 분리이며 중복 엔티티 생성 증거가 아니다. 보호 동작 그대로 두고 해당 로그만 Info로 낮췄다.

대표 Trigger: maptown Portal_E BoxSize 3×3, map001 E 1.5×1.5/W 3×3, map003 E/N/S/W 1.5×1.5; Legacy=true, offset 0. Native TriggerComponent 정의상 새 방식은 Transform 회전/Scale 영향을 받으며 ColliderOffset/구 BoxOffset의 의미도 달라 단순 flag 전환은 같은 동작을 보장하지 않는다. 현재 포탈은 실제 TriggerEnter→TryPass로 정상 이동했다. **TECH_DEBT 유지**, 맵/포탈 collider 값/연결 일괄 수정 없음. 엔진 경고를 필터로 숨기지도 않았다.

## 5. 실제 Maker 검증

Refresh → Build 로그 확인 → Play. UI 버튼을 클릭했다고 주장하지 않는다. Maker mouse 도구는 엔진 Button을 클릭하지 못하므로 기존 UI 컨트롤러 StartSelectedRun/정상 Abandon 요청을 MCP Execute Script로 호출했다. 게임 상태/획득/진행/서버 뷰를 강제 설정하지 않았으며 맵 이동은 Maker keyboard_input 방향키로 수행했다.

| Run | 시작 | 자동 상태 확인 | Map | Objective | HP | Companion | SkillBar | Run 메뉴 | 수동 Broadcast |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 02:31:33 | 02:31:48 | map001 | PASS | PASS | PASS | PASS | PASS | 없음 |
| 2 | 02:32:42 | 02:33:17 | map001 | PASS | PASS | PASS | PASS | PASS | 없음 |
| 3 | 02:33:48 | 02:34:18 | map001 | PASS | PASS | PASS | PASS | PASS | 없음 |

표의 시각은 테스트 조회 시각이며 HUD가 그때까지 지연됐다는 뜻이 아니다. 세 Run 모두 client GameData/slots ACTIVE=true, objective와 네 HUD root Enable=true. Run 3의 실제 화면은 `run3_hud_auto.png`.

- Run 1/2는 정상 ABANDON→로비→새 Run. 초기화마다 client-ready→server snapshot→ApplyRogueliteView 로그 확인.
- Portal 왕복: 02:36:03 `r_001 --east--> r_004`, 02:37:08 `r_004 --west--> r_001`; 실제 OnTriggerEnter→TryPass 스택. map004 진입 직후 자동 snapshot 요청/응답 확인. 별도 Broadcast 호출 안 함.
- Skill Drop: 자연 전투의 m_fairy 0.09276/0.07072 roll→AVAILABLE→MATERIALIZE→CREATE(02:38:47~48) 확인. 이번 회귀는 생성/유지 경로 확인이며 직접 획득 버튼/사용까지 확인한 것으로 확장하지 않음.
- 보스방 경로: `r_001→r_004→r_002→r_02→r_04→r_24→r_23→r_17→r_11→r_05`. Run 3 Seed=595231, Generator=3.
- 02:46:15 정상 포탈로 r_05/map05 입장. 02:46:30 `MegaBossClear boss death confirmed ... m_mushmom`, `RoomSpawner 보스전 종료 ... 격파`. 동행 포함 실제 전투 결과이며 직접 보스 사망/클리어 호출 안 함.
- 02:47:55 `map=maptown active=false result=IDLE`, 실제 로비 화면 `after_boss_lobby.png`. 02:50:58까지 로그 확인 후 Play 종료.
- 재시도 지연/Bounds 실패 Warning 0. 실제 멀티클라이언트, 모든 Seed/맵, 고의 네트워크 손실 검증은 수행하지 않음.

## 6. 수정 파일 / 잔여 한계

| 파일 | 이번 수정 |
|---|---|
| Mislocated/MyDesk/GameData/GameData.mlua | 준비 기반 UI 초기화 / 서버 정본 재요청 / 응답 맵 검증 |
| RootDesk/MyDesk/Room/RoomCamera.mlua | transient 준비 진단 구분 / 마지막 재시도 성공 시 오경고 방지 |
| RootDesk/MyDesk/Room/RoomPortal.mlua | TownGate 담당 정상 보호 로그 Warning→Info |

`git diff --check` PASS. source SHA256:

```text
GameData   c652f9d0ff0ac302357e543bfea15899c2682bcc1947398ef5ea47ba4655375d
RoomCamera 09368da9709eaf0faa04d9b0df7d68dfc97754356257bde94e9f112209e885f2
RoomPortal 0be6183422a2f6d63aaa719ae7eae01ba41ba1b3b71dcbf0d466d535456b8a49
```

이번 root-cause/최소 수정/3 Run HUD 검증 범위는 종료한다. **경고 전부 해소/전체 게임 무결함으로 선언하지 않는다.** 모델 4개 진단의 실제 적용값 영향, Legacy collider 이관, 이전 실패 순간의 엔진 내부 RPC 순서는 남은 한계다. UI FINAL baseline과 기존 사용자 변경은 보존했다.
