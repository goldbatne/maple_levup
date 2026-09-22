# 절차생성 Area 로그라이트 구조 개편 보고서

- 작성 시각: 2026-09-20 23:40 KST
- 분석 기준 `baseline_id`: `skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`
- 기준 커밋: `2eb7498eda8f53440648ef6107d6c933ba55d5c6`
- 기준 미커밋 변경 지문: `fe5fd560ce4c992e562fcc91c0ed6c5cc07443de9224eccd4dc428269b351d82`
- 개편 작업본: `C:/Users/dddd/.codex/visualizations/2026/08/30/01a05014-afc4-7e12-839e-e3f24707e98b/roguelite-rework`
- 정적 검증: PASS 21 / FAIL 0
- Maker build/play/log: **NOT_RUN** — Maker MCP는 연결되어 있으나 편집기가 원본 `D:/maplestory_levup`을 열고 있어, 기준본 보호 원칙상 개편본 refresh/play를 실행하지 않았다.

## [기준 baseline_id와 개편 작업본]

스킬 감사 기준본은 `D:/maplestory_levup/docs/reports/skill-diversity-audit/skill-audit-2026-09-20T174133KST-2eb7498eda-wtfe5fd560ce4c`에 보존했다. 개편은 별도 작업본에서 수행했으며, 시작 시 복사한 `RootDesk`, `Mislocated`, `map`, `ui` 476개 파일의 해시가 감사 기준과 일치함을 확인했다.

기준본의 핵심 데이터 SHA-256:

- `SkillTable.csv`: `3A84B837EDC8615E423DCC1DA6A89A0237A36D3C481F310338FBE016A211023B`
- `MonsterTable.csv`: `6783014B6990F67988B4D17D5AE3B0B741896433FCEFE3849449B7E06073B5E2`
- `GameBalance.csv`: `CF4070AF15C35AF12902C859A9EC6F638BDA4FBF9BA15F5B865DDB5B02D38245`

원본 기준본의 스킬 고유 효과·계수·범위·사거리·지속시간·타격 횟수·몬스터 연결·VFX는 개편 대상으로 삼지 않았다. 변경 파일과 개편 후 해시는 `CHANGED_FILE_HASHES.csv`에 기록했다.

## [최종 게임 루프]

구현한 정적 흐름은 다음과 같다.

1. Area 선택
2. 서버가 Area·참가자·Seed·생성기 버전을 포함한 InstanceRoom 키 확정
3. 서버/클라이언트가 같은 설정으로 방 그래프 구성
4. 시작 방 입장, 공통 Run 능력치와 빈 스킬 슬롯 5칸으로 시작
5. 방 단위 일회성 조우, 몬스터 처치
6. 연결된 액티브 능력을 확정 획득
7. 빈 슬롯 자동 장착 또는 5칸이 찼을 때 교체/포기
8. 최종 목표 방의 지정 적 처치
9. 성공 기록 저장, 일시 상태 정리, 마을 복귀

현재 목표 유형은 검증 범위를 줄이기 위해 `FINAL_ENCOUNTER` 한 종류만 연결했다. 열쇠·장치·봉인 목표는 공통 구조에 추가할 수 있지만 이번 구현에서 존재한다고 간주하지 않는다.

## [고정 5슬롯과 능력 교체]

- 신규 모드의 슬롯 수는 `run_skill_slot_max=5`로 설정했다.
- 슬롯은 일회성 재고가 아니라 반복 사용 가능한 장착 슬롯이다.
- 몬스터 처치 시 유효한 액티브 능력만 제공한다.
- 빈 슬롯은 첫 번째 빈칸에 자동 등록한다.
- 동일 `SkillID` 중복 장착을 차단한다.
- 5칸이 찬 상태에서는 후보 하나를 보류하고 슬롯 선택 또는 포기를 기다린다.
- 교체한 기존 스킬은 Run 보관함에 남기지 않는다.
- 슬롯 순서 교환 서버 RPC를 마련했다.
- 보류 후보가 있는 동안 추가 후보를 조용히 덮어쓰지 않는다. 현재는 추가 후보를 지급하지 않고 로그로 남긴다.

마지막 항목은 후보 큐를 새로 만들지 않는 최소 정책이다. 실제 협동·연속 처치에서 이 정책이 충분한지는 Maker 플레이 검증이 필요하다.

## [쿨다운 재사용 및 대체값]

- 신규 모드에서도 기존 `SkillTable.cooldown`을 사용한다.
- 정상 발동이 확인된 뒤 플레이어별 `SkillReadyAt[skill_id]`를 시작한다.
- 거부된 요청에는 쿨다운을 시작하지 않는다.
- 사용 후 슬롯과 스킬은 유지한다.
- 슬롯 이동·같은 몬스터 재처치·UI 열기/닫기로 쿨다운을 초기화하지 않는다.
- 현재 획득 가능 액티브 66종은 모두 양수 쿨다운을 갖고 있다.
- 누락/0 값의 안전 대체값은 `run_skill_cooldown_fallback=4`초로 분리했다.
- 따라서 현재 데이터에서는 대체값 적용 대상이 0종이며, 새 데이터 오류에 대한 안전장치로만 존재한다.

## [랜덤 공급/슬롯 소비 제거]

신규 모드에서는 아래 경로를 차단했다.

- 5초 공급 타이머
- 보유 풀 랜덤 추첨
- 빈칸 자동 충전
- 사용권 중복 생성
- 성공 사용 시 슬롯 소비
- 긴급/초기 공급
- Trait Weight

레거시 비교 모드의 코드와 저장 필드는 삭제하지 않았고 기능 플래그가 신규 모드가 아닐 때만 동작한다. 신규 Run 시작·종료 시 공급 타이머와 일시 슬롯을 명시적으로 정리한다.

## [기존 스킬에서 변경된 항목]

스킬 자체가 아니라 사용 체계만 변경했다.

- 획득: 확률 포획 → 전투 참여자별 확정 획득 기회
- 장착: 랜덤 재고 → 고정 5슬롯
- 사용 후: 슬롯 소비 → 슬롯 유지
- 재사용: 쿨다운 무시 → 기존 스킬 쿨다운 적용
- 중복 처치: 중복 강화 → 장착/쿨다운 변화 없음
- 영구 수집: 시작 전투력 제공 → 발견 기록만 제공

투사체, 돌진, 범위, 방어 등 기존 실행 함수와 VFX 연결은 유지했다. 새 지형에서의 벽 충돌과 판정 정합성은 아직 런타임 확인하지 않았다.

## [분석 보고서와 달라진 동작]

감사 baseline은 당시 활성 랜덤 SkillBar·테이밍 구조를 분석했다. 개편본에서는 고정 장착과 쿨다운을 사용하므로 다음 감사 필드가 달라진다.

- 실제 입력 후 슬롯 유지 여부
- 재사용 제한
- 획득 경로
- 동일 능력 재획득의 의미
- Run 시작/종료 시 사용 가능 상태
- 지형 충돌이 실제 운용에 미치는 영향

스킬의 효과 다양성 결론을 근거로 스킬을 합치거나 효과를 변경하지 않았다.

## [절차생성 구조와 Area 설정]

현재 구현은 런타임 타일을 무작위로 뿌리지 않는다. 기존 설계 맵 하나를 Room/Chunk 템플릿 하나로 보고 연결 그래프를 절차적으로 구성한다.

생성 데이터:

- `AreaID`
- Area의 기존 Room 풀과 `map_name`
- 시작/최종 후보
- `run_main_path_min=4`, `run_main_path_max=6`
- `run_branch_budget=2`
- Room의 기존 동서남북 연결 호환성
- Area Monster 풀
- Encounter 역할과 예산

생성 절차:

1. 주 경로 길이 선택
2. 방향 호환 Room 연결
3. 선택 위험 가지 추가
4. 시작/최종 Room 확정
5. Room별 조우 몬스터와 수량 확정
6. 시작→최종 도달성, 연결 대칭성, 맵 존재 여부 검사
7. 최대 `run_generator_retry_max=8`회 재시도
8. 실패하면 기존 Area 연결 그래프를 안전 배치로 사용

동적 타일 배치·회전·반전은 만들지 않았다. 이 방식은 현재 MSW 자산과 포탈 구조를 보존하면서 Run마다 경로와 조우 구성을 바꾸는 최소 구현이다.

## [기존 맵 재사용 목록]

`RoomTable` 160행과 실제 `.map` 160개를 대조했다. 누락은 0개다.

- `ROOM_CHUNK_REUSE`: 136
- `SPECIAL_ENCOUNTER_REUSE`: 22
- `NEEDS_ADAPTATION`: 1 (`gate`)
- `REFERENCE_PRESERVE`: 1 (`maptown`)

세부 목록은 `MAP_ASSET_CLASSIFICATION.csv`에 있다. 과거 `map003` 압축 연구는 기준본에 보존했으며 모든 맵에 같은 축소율을 적용하지 않았다.

## [Seed 재현과 유효성 검사]

InstanceRoom 키에 Area, Seed, 생성기 버전, 참가자 ID를 기록한다. 맵 생성에는 별도 LCG 상태를 사용하여 전투 난수와 분리했다. 다음 항목을 Run 상태에 보관한다.

- Seed
- 생성기 버전
- 선택된 Room 역할
- 연결 그래프
- Room별 조우
- 시작/최종 Room
- 재시도 후 안전 배치 사용 여부

정적 검증에서 20개 Area의 원본 안전 배치가 시작점에서 보스 방까지 도달 가능함을 확인했다. 실제 InstanceRoom에서 같은 Seed가 같은 포탈·조우로 나타나는지는 **NOT_RUN**이다.

## [Area 목표와 클리어]

- 초기 공통 목표: 최종 공간의 지정 조우 처치
- 목표 완료는 서버가 한 번만 확정한다.
- 완료 참가자의 Area clear 영구 기록을 갱신한다.
- 3초 후 Run 슬롯을 정리하고 참가자를 `maptown`으로 이동한다.
- 모든 방 전멸을 문 개방 조건으로 만들지 않았다.
- 일반 Room 조우는 한 번 배치되며 무한 리스폰하지 않는다.

## [솔로 검증]

정적 경로:

- AreaSelect가 서버 Run 시작 요청
- 참가자 목록이 비면 요청자 1인으로 검증
- InstanceRoom 생성 후 Entry map 이동
- 빈 고정 슬롯으로 시작
- 몬스터 처치→액티브 능력 제안
- 최종 조우 처치→완료→마을 복귀
- 솔로 사망→전원 사망 판정→Run 실패

이 흐름은 코드/데이터 확인만 했으며 Maker 실제 시작→완료/실패는 **NOT_RUN**이다.

## [협동 인원별 검증]

서버 구조는 1~4인 참가자 목록, Area별 준비 상태, 같은 대기 맵 검증, 참가자 고정, 중도 난입 차단, 동일 참가자 재접속, 개인 슬롯, 개인별 획득 기회, 전원 사망 실패를 지원하도록 작성했다. 준비하지 않은 접속자를 ID만으로 Run에 이동시키지 못하게 했다.

기존 `AreaSelectPanel`을 최소 협동 준비 흐름으로 재사용했다. Area를 처음 누르면 해당 Area에 준비되고, 같은 Area를 다시 누르면 같은 대기 맵에서 그 Area에 준비한 최대 4인을 서버가 모아 시작한다. 창을 닫으면 준비를 해제한다. 별도의 대형 로비 UI는 만들지 않았다.

- 솔로 정적 연결: 구현
- 2~4인 서버 기반과 준비 RPC: 구현 초안
- 기존 Area 선택창 기반 준비/시작: 구현 초안
- 참가자 명단·개별 준비 상태를 보여주는 전용 로비 UI: **미완료**
- 2~4인 실제 Maker 플레이: **NOT_RUN**

## [HP 배율과 획득 권한]

- HP 배율: `1 + run_hp_scale_per_extra_player(0.25) × (시작 인원 - 1)`
- 1/2/3/4인: 1.00 / 1.25 / 1.50 / 1.75
- 시작 인원으로 고정하며 사망·맵 이동으로 기존 몬스터 HP를 재계산하지 않는다.
- 공격력과 개체 수에는 같은 배율을 중복 적용하지 않는다.
- 보스 역할은 별도 `run_boss_hp_multiplier=4`를 적용한다.
- 몬스터 사망 시 `run_participation_radius=12` 안의 생존 참가자에게 각자 독립 제안한다.
- 같은 사망 이벤트의 Room 조우 처리는 일회성 상태로 중복 방지한다.

12 world units 근접 판정은 복잡한 피해 기여도 대신 사용한 초기 정책이다. 방어/지원 참여자의 실제 인정 체감과 맵 반대편 제외 여부는 런타임 확인이 필요하다.

## [사망/전환/이탈/재접속]

- 사망자는 일반 RPG 부활 대신 관전 상태로 기록한다.
- 전원 사망이면 Run 실패를 확정한다.
- 생존 참가자가 포탈 반경 4 world units 안에 모였을 때만 서버가 전환을 한 번 확정한다.
- 확정된 전환은 모인 생존 참가자를 모두 같은 목적지로 이동시킨다.
- 생존자가 안전한 Room 전환을 수행할 때 관전자 재합류 경로를 호출한다.
- 재합류로 슬롯과 쿨다운을 초기화하지 않는다.
- 비참가자의 InstanceRoom 진입은 마을로 되돌린다.
- 연결 끊김은 `run_reconnect_grace_seconds=90` 유예를 기록한다.
- 동일 사용자 재접속은 참가자로 복구한다.

실제 관전 카메라, 재접속 네트워크 타이밍, 전환 동시 요청 경쟁은 **NOT_RUN**이다.

## [UI와 저장]

신규 HUD:

- HP 유지
- 레벨/EXP 숨김
- 고정 5슬롯, 단축키, 슬롯별 쿨다운 표시
- Room/목표 진행과 Seed/생성기 버전 표시
- 보스 HUD를 최종 목표 HUD로 재사용
- 능력 후보는 기존 알림과 SkillBar 클릭/Escape 입력을 재사용

신규 모드에서 숨김/차단:

- 스탯 투자
- 장비/아이템 퀵슬롯
- 환생/전직
- 기존 월드맵 진행
- 랜덤 공급 표시
- 테이밍/동행/별 강화

컬렉션 UI는 기존 101칸을 발견 기록으로 재사용하고 전투력이나 시작 스킬을 지급하지 않는다.

저장은 기존 RPG/M2 필드를 삭제하지 않고 기존 Perm 데이터 안의 별도 `RoguelitePermanent` namespace에 schema/discovered/clears/optional/settings만 보존한다. 장착 스킬, 쿨다운, HP, 후보, 목표, 생성 상태는 영구 저장하지 않는다.

## [기존 데이터 및 분석 기준본 보호]

- 원본 `D:/maplestory_levup`은 개편 코드의 편집 대상으로 사용하지 않았다.
- 기존 RPG/M2 저장 필드는 읽기 호환을 위해 보존했다.
- 신규 모드 시작 능력치에 레벨·장비·환생·Trait·테이밍 단계를 합산하지 않는다.
- 기존 스킬/몬스터 CSV의 식별자와 연결을 변경하지 않았다.
- 실제 계정 데이터, 인증 정보, 비밀키를 보고서에 포함하지 않았다.

## [실제 수정 파일]

런타임 23개:

1. `RootDesk/MyDesk/PlayerAttack.mlua`
2. `RootDesk/MyDesk/PlayerHit.mlua`
3. `RootDesk/MyDesk/RoomMonster.mlua`
4. `RootDesk/MyDesk/GameData/GameBalance.csv`
5. `RootDesk/MyDesk/GameData/GameData.mlua`
6. `RootDesk/MyDesk/GameData/PlayerStats.mlua`
7. `RootDesk/MyDesk/Progress/PlayerCollection.mlua`
8. `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`
9. `RootDesk/MyDesk/Room/RoomPortal.mlua`
10. `RootDesk/MyDesk/Room/RoomSpawner.mlua`
11. `RootDesk/MyDesk/Save/PlayerDBManager.mlua`
12. `RootDesk/MyDesk/Save/SavePermanentData.mlua`
13. `RootDesk/MyDesk/UI/AreaSelectPanel.mlua`
14. `RootDesk/MyDesk/UI/EquipPanel.mlua`
15. `RootDesk/MyDesk/UI/GoddessPanel.mlua`
16. `RootDesk/MyDesk/UI/InventoryPanel.mlua`
17. `RootDesk/MyDesk/UI/ItemQuickSlotBar.mlua`
18. `RootDesk/MyDesk/UI/PlayerHud.mlua`
19. `RootDesk/MyDesk/UI/RebirthConfirmPanel.mlua`
20. `RootDesk/MyDesk/UI/RoomProgressHud.mlua`
21. `RootDesk/MyDesk/UI/SkillBar.mlua`
22. `RootDesk/MyDesk/UI/StatPanel.mlua`
23. `RootDesk/MyDesk/UI/WorldMapPanel.mlua`

계획/검증 문서:

- `BASELINE_AND_WORKCOPY.md`
- `ROGUELITE-GDD.md`
- `ROADMAP.md`
- `CHANGED_FROM_SKILL_AUDIT.md`
- `MAP_ASSET_CLASSIFICATION.csv`
- `CHANGED_FILE_HASHES.csv`
- `STATIC_VERIFICATION.md`
- `verify-roguelite-rework.ps1`
- 본 보고서

## [Maker 빌드/런타임 결과]

- Maker build: **NOT_RUN**
- Maker play: **NOT_RUN**
- Maker build log: **NOT_RUN**
- Maker normal log: **NOT_RUN**
- 이유: Maker MCP 화면과 콘솔 파일 경로에서 현재 편집기가 원본 `D:/maplestory_levup`을 열고 있음을 확인했다. 개편 작업본이 아닌 원본을 refresh/play하면 사용자의 감사 기준 환경을 바꾸므로 실행하지 않았다.
- 확인 화면: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_edit_20260920_235527_079.png`

현재 원본 Maker의 읽기 전용 로그에는 이미 다음 항목이 있었다. 이는 개편본을 refresh/build한 결과가 아니므로 개편 회귀로 계산하지 않는다.

- Build Console 3건: `GetTamedCount` 관련 LIA 1건, 기존 모델 속성 경고 2건
- Normal Console 17건: `Mislocated/MyDesk`와 `RootDesk/MyDesk` 사이의 기존 중복 EntryKey (`LEA-3015`)
- 기준본 보존 지시 때문에 원본 중복 파일을 삭제·이동하지 않았다.

정적 검증 결과:

- PASS: 21
- FAIL: 0
- 변경 런타임 파일: 23
- AreaTable: 20
- RoomTable/맵 존재: 160/160
- 원본 안전 배치 도달 가능: 20/20 Area
- 몬스터→능력 매핑: 101 (액티브 66, 패시브 35)
- 액티브 쿨다운 누락/0: 0

## [NOT_RUN과 미완료]

NOT_RUN:

- 실제 InstanceRoom 생성/이동
- 동일 Seed의 실제 포탈·조우 재현
- 솔로 성공/실패 전체 흐름
- 투사체 벽 충돌
- 돌진 벽 관통·지형 이탈
- 범위 공격의 벽 너머 판정
- 2~4인 HP 배율, 개인 획득, 목표 공유
- 관전/안전 전환 재합류
- 이탈/90초 재접속
- UI Mask·입력 차단·중앙 패널 잔존
- DataStorage 신규 namespace 왕복 저장

미완료:

- 참가자 명단·상태를 보여주는 전용 협동 로비 UI
- 목표 유형 확장(장치/열쇠/봉인)
- 문제 스킬별 새 지형 호환 보정
- 관전자 전용 카메라·표시

## [남은 버그]

실행 전에는 확정 버그로 분류할 수 없으므로 아래는 위험 항목이다.

1. InstanceRoom 생성 직후 각 map의 Logic 초기화 순서와 RoomKey 파싱 시점
2. 여러 플레이어가 같은 프레임에 최종 목표·포탈 요청을 보낼 때의 중복 경쟁
3. 재접속 이벤트와 실제 플레이어 Entity 재생성 시점 차이
4. 기존 UI의 Mask/입력 차단 상태가 숨김 처리 후 남을 가능성
5. `RoomMonster`의 정규화 수치가 기존 스킬 계수와 맞는지에 대한 실전 난이도
6. 연속 처치 중 후보 하나가 이미 보류된 경우 후속 획득 기회가 사라지는 최소 정책
7. 개편 사본에도 기준본과 동일하게 복사된 `Mislocated` 중복 EntryKey를 Maker 연결 전에 별도 보존/제외하는 작업

## [사용자 스킬 검토 후 판단할 항목]

사용자가 감사 HTML에서 스킬별 효과를 확인한 뒤 별도 판단할 항목:

- 기존 쿨다운 수치가 고정 슬롯 체계에서 적절한지
- 기본 대체 쿨다운 4초의 향후 대상
- 벽 관통을 고유 기능으로 유지할 스킬과 환경 오류로 막을 스킬
- 돌진의 지형 경계 처리
- 유사 구조 스킬 간 선택 가치
- 능력 후보가 연속 발생할 때 큐가 필요한지
- Encounter 정규화 수치와 보스 HP 4배의 실제 난이도

이 항목들은 본 개편에서 스킬 자체를 선제 수정하는 근거로 사용하지 않았다.

## 결론

분리 작업본에는 고정 5슬롯·기존 쿨다운·확정 능력 획득·Seed 기반 Room 그래프·일회성 조우·최종 목표·별도 영구 기록·서버 참가자/HP/획득/사망 구조의 **정적 프로토타입**이 구현되어 있다. 정적 검사 16개는 통과했지만 Maker MCP 부재로 실제 실행 인증은 하지 못했다. 따라서 현재 상태를 “런타임 완성”이나 “1~4인 지원 완료”로 표기해서는 안 되며, 다음 필수 단계는 원본이 아닌 이 분리 작업본을 Maker에 연결하여 build/play/log 검증과 협동 준비 UI를 완성하는 것이다.
