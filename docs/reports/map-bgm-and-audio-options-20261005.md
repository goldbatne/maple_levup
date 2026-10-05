# 원작 지역 BGM 연결 및 소리 옵션 점검

작성일: 2026-10-05. 판정: **파일 반영·정적 검증 완료 / Maker 재생 검증 대기**.

## 적용 의도와 범위

랜덤 Run에서 선택된 지역의 원작 메이플스토리 BGM을 듣도록 연결했다. 분위기 검색 결과의 설명만으로 곡을 결정하지 않았다. 공식 MSW 리소스의 `path`, `subPath`, 원작 맵 이름 태그를 확인하고 기존 RoomTable/AreaTable의 지역·방 이름에 대응시켰다.

- 기존 맵 162개에 맵 루트 `MOD.Core.SoundComponent` 추가.
- RoomTable 등록 맵 159개, 기존 프로토타입 맵 3개 포함. 프로토타입은 부모 지역과 같은 곡 사용.
- 고유 원작 BGM 37곡. 공식 리소스 일괄 조회 37/37 성공.
- Bgm / PlayOnEnable / Loop / KeepBGM / Enable 활성화, Mute 비활성화, Pitch 1, 기본 믹싱 Volume 0.35.
- 음악을 무작위로 따로 뽑는 것이 아니라 **무작위로 선택된 맵에 대응하는 곡**을 사용한다.
- 같은 RUID를 쓰는 방 사이에서는 native KeepBGM의 연속 재생을 사용하도록 설정했다. 다른 지역·세부 구역의 곡으로는 맵 진입 시 전환하는 native 방식이다. 실제 전환 청취는 아직 하지 않았다.
- 원작에 없는 프로젝트 전용 방 이름은 실제 원작 지역의 필드/실내 BGM을 재사용했다. 모든 프로젝트 방이 원작에 동일 이름으로 존재한다고 주장하지 않는다.

## 지역과 곡

| 프로젝트 지역 | 기본 원작 곡 | 구역별 추가 곡 |
|---|---|---|
| 메인 마을 헤네시스 | FloralLife | 없음 |
| 메이플 아일랜드·리스항구 | MapleLeaf | 리스항구: AboveTheTreetops |
| 헤네시스 근교 | CavaBien | 머쉬맘 오솔길: FloralLife |
| 페리온 | HighlandStar | 없음 |
| 엘리니아 | MoonlightShadow | 나무던전: MissingYou |
| 커닝시티 | Subway | 공사장·추락주의: BadGuys |
| 노틸러스 | Nautilus | 화물칸: inNautilus |
| 슬리피우드 | AncientMove | 늪 입구: SleepyWood / 발록·신전: EvilEyes |
| 오르비스 | Shinin'Harbor | 없음 |
| 엘나스 산맥 | WarmRegard | 없음 |
| 아쿠아로드 | BlueWorld | 심해: DeepSee / 피아누스 동굴: AquaCave |
| 루더스 호수·에오스탑 | FunnyTimeMaker | 없음 |
| 루디브리엄 | FantasticThinking | 공장: WaltzForWork / 시간 구역: WhereverYouAre |
| 니할 사막 | HotDesert | 붉은 모래·잠자는 사막: SunsetDesert |
| 마가티아 | Dispute | 없음 |
| 무릉도원 | MureungHill | 과수원·숲: MureungForest |
| 미나르숲 | Minar'sDream | 와이번: DragonNest / 마뇽: AcientForest |
| 시간의 신전 | Remembrance | 없음 |
| 지구방위본부 | LetsHuntAliens | 제노 격납고: ForTheGlory |
| 미래의 문 | knightsStronghold | 시그너스 정원: CygnusGarden |
| 황혼의 페리온 | destructionPerion | 없음 |

곡 표기는 공식 리소스의 원본 `subPath`를 유지했다. `AcientForest`, `DeepSee`도 정본 태그의 표기다. 전체 맵별 RUID 및 원작 태그는 `map-bgm-mapping-20261005.json`에 있다.

## 기존 소리 옵션

정적 코드 점검에서 별도 게임 전용 음악/효과음 설정창이나 저장 로직, native 설정을 덮어쓰는 음악 볼륨·음소거 코드를 발견하지 않았다.

- 이번 BGM은 `Bgm = true`인 native SoundComponent를 사용한다.
- 기존 스킬 SFX는 SkillEffect의 `_SoundService:PlaySound` 경로를 유지했다. GameBalance의 `skill_sfx_volume = 0.6`도 변경하지 않았다.
- 몬스터 공격 SFX의 기존 native PlaySound 및 AttackSfxVolume 0.6도 유지했다.
- BGM의 0.35는 제작자 기본 믹싱 값이다. 사용자의 옵션 슬라이더 값을 35%로 강제 설정한 것이 아니다.
- 별도 옵션창은 추가하지 않았다. 현재 목적이 음악/효과음 조절뿐이라면 기존 MSW 옵션을 우선 유지하는 것을 권장한다.

native 음악/효과음 분류를 사용하므로 기존 플랫폼 설정을 따르는 구성이지만, **옵션 슬라이더가 실제 재생 볼륨에 반영되는지와 재접속 후 유지되는지는 Runtime 미검증**이다. 소스 구조 확인만으로 옵션 적용 PASS를 기록하지 않는다. 이전 Maker 음소거 설정이나 운영체제 볼륨은 이번에 변경하지 않았다.

## 실제 검증 결과

| 검사 | 결과 | 근거 |
|---|---|---|
| 맵별 BGM 설정 | PASS 162/162 | MapBuilder로 다시 읽어 RUID·BGM 플래그·볼륨 확인 |
| 원작 리소스 정보 | PASS 37/37 | 공식 path/subPath/원작 맵 태그 조회 |
| 공식 리소스 존재 | PASS 37/37 | getResourcesBatch의 반환 ID와 type=bgm 확인 |
| 누락 | 0 | 모든 기존 .map에 1개씩 루트 SoundComponent |
| 비음악 맵 데이터 변경 | 0 | HEAD와 비교, 추가 SoundComponent 및 componentNames만 제외하면 전체 데이터 동일 |
| 타일·포탈·좌표·방 설정 | 변경 없음 | 위 전체 데이터 비교 |
| 전투·UI·스킬 SFX 파일 | 변경 없음 | tracked 변경 파일은 기존 .map 162개뿐 |
| 숫자 표기·줄바꿈 | 보존 | 의미 변경 없는 기계적 서식 보존 후 재검사 |
| Maker Refresh | NOT_RUN | 현재 호출 목록에 Maker 제어 도구 없음 |
| Maker Build / Warning | NOT_RUN / 확인 불가 | Build·로그 도구 없음 |
| Maker Play / Runtime Error | NOT_RUN / 확인 불가 | Play·로그 도구 없음 |
| 지역 전환·중복 재생·청취 | NOT_TESTABLE | 실제 Play 실행 없음 |
| native 옵션 실제 조절·저장 | NOT_RUN | 실제 설정 조작 및 청취 없음 |

검증 상세: `map-bgm-validation-20261005.json`.

## 남은 Maker 확인

1. 저장된 프로젝트에 Refresh 후 Build. 신규 sound/RUID 오류와 기존 경고를 구분한다.
2. Play에서 헤네시스 진입 후 BGM 확인.
3. 자연 Run에서 서로 다른 지역 이동 시 해당 곡으로 전환하는지, 이전 곡이 겹쳐 남지 않는지 확인.
4. 같은 곡의 방 사이에서는 음악이 불필요하게 처음부터 재시작하지 않는지 확인.
5. 피아누스·시그너스 등 세부 구역과 마을 복귀의 곡 확인.
6. 기존 옵션에서 음악을 0/중간/최대로 바꿔 BGM만 조절되는지 확인. 효과음 옵션으로 스킬 SFX도 별도로 확인.
7. Stop → Play 및 재접속 후 사용자 소리 설정 유지 확인.

Maker를 종료하거나 재시작하지 않았으며 commit/push도 하지 않았다.

## 자료와 재현 도구

- 공식 BGM 메타데이터: `map-bgm-official-catalog-20261005.json` (공식 bgm 리소스 456개 및 원작 맵 태그).
- `tools/audit_map_bgm.cjs`: 공식 메타데이터 조회.
- `tools/apply_map_bgm.cjs`: 기본 실행은 dry run, `--write`만 MapBuilder로 기존 맵의 BGM을 반영.
- `tools/preserve_map_number_format.cjs`: 의미를 바꾸지 않는 숫자/파일 끝 서식 보존.
- `tools/verify_map_bgm.cjs --official`: 전체 맵과 HEAD의 비음악 데이터 비교 및 공식 RUID 조회. 게임 실행 검증을 대체하지 않는다.
- [MSW 공식 BGM 설정 가이드](https://maplestoryworlds-creators.nexon.com/en/docs?postId=825): 맵 SoundComponent의 Bgm/PlayOnEnable 사용.
- 프로젝트 native SoundComponent 정의: `Environment/NativeScripts/Component/SoundComponent.d.mlua` (KeepBGM 조건 포함).

msw-search 스킬의 원작 리소스 태그 검증 절차와 msw-general의 MapBuilder 규칙을 적용했다. msw-scripting 검증 원칙에 따라 실행하지 못한 Maker 검사는 PASS가 아닌 NOT_RUN으로 분리했다.
