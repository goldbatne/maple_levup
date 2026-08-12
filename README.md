# maple_levup — 방 단위 탑다운 탐험 성장 RPG

메이플스토리 월드(MapleStory Worlds, mLua) 프로젝트. 1인 개발 + AI 협업.

> **성장할수록 세계가 열리는, 방(房) 단위 탑다운 탐험 성장 RPG.**

수직 슬라이스(마을 + 방 5개 / 몬스터 4종 / 직업 2종 / 환생 1회)가 **구현 완료** 상태이고,
그 위에 마을·지역(area) 구조가 올라가 있다. 남은 것은 대표의 직접 플레이 판정과 수치 조율,
그리고 두 번째 지역의 방들이다.

👉 **지금 상태를 한 파일로 보려면 [docs/프로젝트_현황.md](docs/프로젝트_현황.md).**

---

## 처음 온 사람(또는 AI)이 읽을 순서

| # | 문서 | 무엇을 얻는가 |
|---|---|---|
| 1 | **[docs/프로젝트_현황.md](docs/프로젝트_현황.md)** | **지금 어디까지 왔는지 한 파일 스냅샷.** 완료된 것 / 코드는 있는데 배치 안 된 것 / 초안 수치 / 함정 목록. **여기서 시작한다** |
| 2 | **[CLAUDE.md](CLAUDE.md)** | 프로젝트 규칙 · 설계 변경 이력 (정본) |
| 3 | **[docs/인수인계_현재상태.md](docs/인수인계_현재상태.md)** | 문서와 구현이 어긋난 지점의 상세. **기획서를 읽기 전에 읽어야 한다** |
| 4 | **[docs/게임기획서_v0.3.md](docs/게임기획서_v0.3.md)** | 시스템 설계 전체 (게이트 3종 · 슬롯 경제 · 환생 · 스탯 · 지역 구조 §3.3). ⚠ 여기 적힌 것 중 **6개는 아직 구현되지 않았다** — 3번 문서 3절 참고 |
| 5 | **[docs/밸런스_확정수치.md](docs/밸런스_확정수치.md)** | 레벨 곡선 · 몬스터 계단 · 방별 위험도. **수치는 여기가 정본** |
| 6 | **[docs/작업지시서_v2.0.md](docs/작업지시서_v2.0.md)** | T0~T10 태스크별 구현 기록과 실측. "왜 이렇게 됐나"의 근거 |
| 7 | **[AGENTS.md](AGENTS.md)** | MSW 플랫폼 규칙 (AI 작업자 전용). CLAUDE.md가 자동 import한다. **`.model`/`.ui`/`.map` 편집 방법이 여기 있다** |

> 1~5번은 40분이면 읽는다. 6번은 필요할 때 해당 태스크 절만 찾아 읽으면 된다.

`docs/프로젝트_재정리_개발운영_가이드_v1.0.md`는 **히스토리 문서**다. 현행 기준이 아니다.
`docs/밸런스시트_v0.1.xlsx` / `v0.2.xlsx`는 **작업용 스프레드시트**다 — 읽기용 정본은 위 5번.

---

## 코드 지도

```
RootDesk/MyDesk/
  GameData/      GameData.mlua ...... 모든 정적 데이터 조회의 유일한 창구 (@Logic)
                 *.csv + *.userdataset  7종 — 밸런스/스킬/몬스터/방/직업/랜드마크/지역
                 GameDataVerify.mlua   기동 시 데이터 정합성 전수 검사 — 로그부터 여기를 본다
  Combat/        CombatFormula.mlua .. 데미지 **산술** 단일 지점 (@Logic). 계수·DEF를 받아 숫자를 낸다
                 RoomMonster.mlua .... 몬스터 HP·DEF·EXP·ATK, 피격·사망 (@Component)
  Player/        PlayerStats.mlua .... 스탯 4종, 레벨·EXP, 서버 권한 분배 (@Component)
                 PlayerTopDownAnim.mlua  상하 이동 시 좌우 스프라이트 유지
                 MoveInputGuard.mlua ... 이동 입력 제어
  Progress/      LevelCurve.mlua ..... 성장 곡선 계산 (@Logic)
                 PlayerCollection.mlua  포획 판정 · 40킬 천장 (@Component)
                 PlayerSkillSlots.mlua  슬롯 경제 · 확장 2축 (@Component)
                 Rebirth.mlua ........ 환생 판정/실행/랜드마크 (@Logic)
                 ProgressLog.mlua .... 진행 로깅 5종 (@Logic)
  Room/          RoomPortal / RoomGate / RoomSpawner / RoomCamera / ReturnPortal
                 TownGate.mlua ....... 마을 동쪽 문 = **지역(area) 이동의 유일한 출입구**
                                       갈 수 있는 곳 1곳이면 바로, 2곳 이상이면 선택 창
                 PortalGuard.mlua .... 포탈 재진입 방지
                 RebirthNpc.mlua ..... 마을 환생 NPC
  Save/          PlayerDBManager.mlua  로드·저장·스로틀 (@Component)
                 SaveRunData / SavePermanentData (@Struct — 회차/영구 분리)
  UI/            StatPanel / EquipPanel / GateNotice / RebirthHud / RebirthConfirmPanel
                 SkillBar.mlua ....... 스킬 **수동 사용** 창구. 버튼 탭과 키보드
                                       (Z X C V B N M, 맨 왼쪽 슬롯부터)가 같은 Use()를 탄다
                 PlayerHud.mlua ...... 상시 HP·EXP·레벨
                 AreaSelectPanel.mlua  마을 게이트의 지역 선택 창
  PlayerAttack.mlua ... 자동 공격 + **어느 스탯으로 때릴지 고르는 곳** (CalcDamage)
  PlayerHit.mlua ...... HP 차감 · 사망 → 시작방 · i-frame
  MonsterAttack.mlua .. 몬스터 → 플레이어 공격 + DEF 감쇄
                        ↑ 셋 다 MSW 샘플 유래라 루트에 있다 (폴더로 옮기지 않았다)
  Models/        Monsters(4) · Terrain(2) · Npc(1)

map/    maptown(마을) + map01~map05 (전부 RectTile 탑다운, TileMapMode = 1)
ui/     11개
Global/ DefaultPlayer.model 등 — 엔진 기본. 새 파일을 만들지 말 것
```

### 손대기 전에 알아야 할 5가지

1. **TileMapMode = 1 (RectTile 탑다운).** 움직이는 엔티티는 `KinematicbodyComponent`.
   짝을 틀리면 **에러 없이** 안 움직인다.
2. **수치 하드코딩 금지.** 전부 `GameData/*.csv` → `_GameData:GetBalance(key)`.
3. **데미지·스탯·EXP·포획·환생·저장은 서버에서만.** 클라는 입력과 연출만.
4. **`.model` / `.ui` / `.map`은 빌더로만 편집한다.** 생 JSON 편집 금지 (AGENTS.md 참고).
5. **`.mlua`를 고치면 Maker `refresh`가 필요하다.** `.codeblock`은 자동 생성이니 손대지 말 것.

---

## 자주 하는 작업 — 순서대로

### 몬스터 1종 추가

`m_skeleton`(T10-4)이 가장 최근 사례다. 작업지시서 T10-4 절에 전 과정이 남아 있다.

1. **스프라이트를 먼저 찾는다** — `msw-search` 스킬로 **리소스팩** 검색(개별 스프라이트 말고).
   STAND / MOVE / HIT / DIE 4종 RUID를 얻는다.
2. `GameData/MonsterTable.csv`에 행 추가 — `id,name,level,hp,def,exp,drop_skill_id,model_id`.
   수치는 `docs/밸런스_확정수치.md` §4 계단에서 그 레벨 값을 그대로 쓴다.
3. `GameData/SkillTable.csv`에 포획 스킬 행 추가 — `scaling_stat`은 ATK / INT / LUK 중 하나.
4. `Models/Monsters/<이름>.model` 생성 — **템플릿에서 새로 조립하지 말고
   기존 몬스터 모델을 `ModelBuilder.read()`로 읽어 복제**한다. 우리 몬스터는 13컴포넌트
   구성이 정본에서 조금 벗어나 있어서, 새로 조립하면 차이를 손으로 맞춰야 하고
   하나 빠뜨리면 **조용히 다르게 동작한다.** RUID·히트박스·`MonsterId`만 바꾼다.
5. `GameData/RoomTable.csv`의 `monster_id`를 새 종으로 바꾸거나 새 방에 배치.
6. 검증: `refresh` → `play` → 로그에서 `[RoomMonster] 스폰 …` 과
   `[GameDataVerify] [몬스터] … [공식 일치]` 두 줄을 확인.

### 방 1개 추가

1. `GameData/RoomTable.csv`에 행 추가. 컬럼 18개는 이렇다:

   ```
   id, name, room_type, conn_north, conn_south, conn_east, conn_west,
   gate_type, gate_key, gate_value, map_name,
   monster_id, monster_count, monster_level, is_start, area_id,
   portal_x, portal_y
   ```

   - ⚠ **`portal_x` / `portal_y`는 이 방 포탈의 좌표 절대값이다.** 다른 방에서 **이 방으로**
     들어올 때 도착 지점을 여기서 계산한다. 맵 폭이 28칸이 아니면 **반드시 맞춰야 한다** —
     안 맞추면 타일 밖에 떨어진다. 마을(14칸 폭)이 실제로 그렇게 깨졌다.
     기존 맵 5개는 `13,1`, 마을은 `6,1`.

   - `room_type` = `hunt` / `gate` / `boss` / `town`.
     **`boss`면 회차당 1마리만 스폰**된다.
   - `area_id` = 이 방이 속한 지역(`AreaTable.csv`). 마을은 어느 지역에도 속하지
     않으므로 비워 둔다. 값이 있으면 `GameDataVerify`가 AreaTable에 있는지 확인한다.
   - `monster_level` — **비워 두면 `MonsterTable`의 기본 레벨을 그대로 쓴다**(0으로 읽힌다).
     값을 넣으면 그 레벨로 HP·DEF·EXP·ATK를 다시 계산한다.
   - `is_start` = 시작방(사망·환생 시 돌아오는 곳). 하나만 `true`.
     지금은 **마을(`r_town`)**이 그 방이다. 이 한 칸을 옮기면 사망 복귀·환생 복귀·
     보스방 귀환 포탈 셋이 코드 수정 없이 같이 따라간다.
   - **연결은 양방향으로** — 새 방의 `conn_west`에 `r_04`를 넣었으면
     `r_04`의 `conn_east`에도 새 방을 넣어야 한다.
     `GameDataVerify`가 기동 시 `깨진 연결 N개`로 잡아 준다.

2. `map/mapNN.map` 생성 — **RectTile 템플릿에서** (`MapBuilder`).
   맵 모드는 파일로 바꿀 수 없다. 기존 맵 구조는 이렇다:
   `mapNN / Background / MapleMapLayer / SpawnLocation / RectTileMap / Portal_E · Portal_W · …`

3. ⚠ **`Global/SectorConfig.config`에 `map://mapNN`을 등록한다.**
   여기 없으면 **맵이 아예 로드되지 않는다.** 현재 `map01`~`map05`가 등록돼 있다.
   `Global/`에 새 *파일*을 만들지 말라는 규칙이지, 이 값 등록은 필요한 작업이다.

4. 맵 **루트 엔티티**에 `script.RoomSpawner`와 `script.RoomCamera`를 붙인다.
   - `RoomSpawner`는 `GetRoomByMapName(self.Entity.Name)`으로 방을 찾는다 →
     **맵 이름과 `map_name`이 반드시 같아야 한다** (`RoomMonster`·`RoomPortal`·
     `ReturnPortal`·`PlayerDBManager`도 같은 규칙을 쓴다).
   - `RoomCamera`는 RoomTable을 보지 않는다. `RectTileMapComponent`의 타일 경계에서
     카메라 범위를 계산한다 — 타일을 안 깔면 경고가 뜨고 카메라가 안 잡힌다.
   - 방 크기가 28×16이 아니면 `RoomSpawner`의 `SpawnMinX/MaxX/MinY/MaxY` 4개를 조정한다.

5. 양쪽 방에 포탈 엔티티를 배치한다 (`Models/Terrain/RoomPortal.model`).
   ⚠ **`script.RoomPortal`의 `direction` 속성을 반드시 설정한다** (`east`/`west`/`north`/`south`).
   목적지를 `room.connections[direction]`으로 찾기 때문에, 비워 두면 **에러 없이**
   아무 데도 가지 않는다.

6. 게이트를 걸려면 `gate_type`에 `stat` / `key` / `rebirth` 중 하나 + `gate_key`·`gate_value`.
   판정 코드는 이미 3종 모두 있다 — 데이터만 채우면 된다.

### 지역 1개 추가

방은 지역(area) 단위로 묶이고, **마을 동쪽 문(`maptown/Portal_E`, `script.TownGate`)이
지역 이동의 유일한 출입구**다. 잠긴 지역은 문이 잠기는 게 아니라 **목록에 뜨지 않는다.**

1. `GameData/AreaTable.csv`에 행 추가 — `id, name, entry_room_id, default_unlocked, sort_order, note`.
   `entry_room_id`는 그 지역의 첫 방. **비워 두면 해금돼 있어도 목록에서 빠진다**
   (경고 로그가 남는다). 방을 다 만든 뒤에 채우는 것을 전제로 한 동작이다.
2. 그 지역의 방들을 위 "방 1개 추가"대로 만들고 `area_id`에 지역 id를 넣는다.
3. 해금 조건을 건다. 지금 있는 축은 **랜드마크 보상**(`LandmarkTable`의 `reward_type=area`)
   하나다. 환생 처리(`Progress/Rebirth.mlua`)가 `PlayerSkillSlots.UnlockedAreas`에 기록하고
   당사자에게 `GateNotice`로 알린다.
4. 진입 판정을 새로 짜지 말 것. **`PlayerSkillSlots:IsAreaUnlocked(areaId)` 하나만 쓴다** —
   서버·클라 양쪽에서 같은 답이 나오도록 `@ExecSpace`를 붙이지 않은 함수다.

⚠ 마을 문 엔티티에는 `script.RoomPortal`을 붙이지 말 것. 둘 다 붙으면 트리거를 같이 물어
서로 먼저 보내려고 싸운다. (안전장치로 RoomPortal이 스스로 물러나지만, 애초에 붙이지 않는다.)

### 수치 하나 바꾸기

1. `GameData/GameBalance.csv`의 값만 고친다. **코드 수정은 필요 없다.**
2. `docs/밸런스_확정수치.md`를 다시 생성한다 (그 문서 맨 아래 "재생성 방법").
3. 종별로 달라야 하는 값이면 `GameBalance`가 아니라 **해당 테이블에 컬럼을 추가**한다
   (예: 몬스터별 ATK를 다르게 하려면 `MonsterTable`에 `atk` 컬럼).

---

## 개발 흐름

```
작업지시서의 태스크 하나 → 구현 → Maker에서 직접 실행 검증 → 완료 조건(✅) 통과 → 커밋 → PR
```

- **한 번에 한 태스크만.** 완료 조건을 통과하지 못하면 다음으로 넘어가지 않는다.
- 커밋 메시지: `[T3] 데미지 공식 구현 (서버)`
- 검증 루프: `stop → clear_logs → refresh → logs(build) → play → logs(normal) → stop`
- **런타임 결과를 실제 도구 호출 없이 주장하지 말 것.** "돌려봤다"는 로그가 있어야 참이다.

## 환경 세팅

```bash
cp .mcp.json.example .mcp.json
```

- `.mcp.json`에 토큰이 들어가므로 **커밋 금지** (`.gitignore`에 있음).
- `.claude/skills/`와 `hooks/`는 저장소에 없다 — MSW 공식 플러그인이며 `skills-lock.json`의
  source·hash로 복원된다. 플러그인 없이 작업하면 AGENTS.md의 스킬 로딩 지시는 건너뛰고
  `Environment/NativeScripts/**/*.d.mlua`(엔진 API 정의, 커밋돼 있음)를 직접 읽으면 된다.
