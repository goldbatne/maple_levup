# AREA 00 Images 2.5 반입 보고서

## 결과

Area 00 대상 5종의 최종 VFX 프레임 44장과 아이콘 5장, 총 49개 PNG를 원본 픽셀 그대로 계정 Resource Storage에 등록했다. 각 몬스터별 AnimationClip 5개를 Maker에서 구성하고 기존 `skill_id`의 `icon_ruid` 및 `layer_ruids` 계열 필드에 연결했다.

- 원본 보존본: `AREA_00_IMAGES_OUTPUT_ORIGINAL.zip`
- 원본 SHA-256: `5271fa0682c4cc76caaf6f4e5627c5fbf3c70ec87fe911b9e5398afb770f6853`
- 원본 크기: 8,167,454 bytes
- 자동 검증 결과: `AREA_00_OUTPUT_VALIDATION.md`, `AREA_00_OUTPUT_VALIDATION.json`
- 상세 RUID 매핑: `AREA_00_IMAGES_RESOURCE_MAP.csv`
- 디자인 수정, 재생성, 스프라이트 시트 재분할, autocrop, recenter: 수행하지 않음

## 입력 자동 검증

`OUTPUT_MANIFEST`, `RESULT_INFO`, 실제 VFX/ICON 파일을 상호 대조했다.

| monster_id | skill_id | VFX | 캔버스 | ICON | 결과 |
|---|---|---:|---|---|---|
| `m_snail` | `s_mon_snail_dew_trail` | F00~F07, 8장 | 384×384 RGBA | 256×256 RGBA | 통과 |
| `m_blue_snail` | `s_mon_blue_snail` | F00~F07, 8장 | 256×256 RGBA | 256×256 RGBA | 통과 |
| `m_red_snail` | `s_mon_red_snail` | F00~F07, 8장 | 256×256 RGBA | 256×256 RGBA | 통과 |
| `m_mano` | `s_mon_mano` | F00~F11, 12장 | 512×512 RGBA | 256×256 RGBA | 통과 |
| `m_slime` | `s_mon_slime` | F00~F07, 8장 | 256×256 RGBA | 256×256 RGBA | 통과 |

모든 PNG는 실제 알파 채널을 포함하고, 각 애니메이션 안에서 캔버스 크기가 같으며, 빈 프레임과 순번 누락이 없다.

## 최종 리소스 매핑

| 몬스터 | 스킬 | ICON RUID | AnimationClip RUID |
|---|---|---|---|
| 달팽이 | 이슬 미끄럼길 | `c0699b32529049c68de3d13022479bf9` | `6097484d513a4fde82ad15557fdc81d3` |
| 파란 달팽이 | 푸른 껍질 | `6e7da13ea5924763bebb7aa4b851eb96` | `f1fc98b763c24a0bb99d8ce8453a4c8f` |
| 빨간 달팽이 | 붉은 껍질 돌진 | `12d807f89a284616a966513250bc3b7c` | `b61e270e3118440680f2a51d12255693` |
| 마노 | 마노의 무지개 파동 | `0cf7d9ac7fa4460a897c5f5e8ce47c51` | `b71327c616e64d678ee1ab4e60512ea2` |
| 슬라임 | 끈적한 몸통 | `79543e5ad88d423ba676e55d69aa432c` | `0ea4bec10d4c43f3aaded74dec60ca44` |

AnimationClip은 입력 프레임 순서대로 구성했다. 프레임 간격은 0.1초이며 8프레임 클립은 0.8초, 마노 12프레임 클립은 1.2초로 `SkillTable`의 레이어 수명과 맞췄다. Sprite 피봇은 모두 `(0.5, 0.5)`로 등록했고, 런타임 레이어는 입력 캔버스를 보존하기 위해 scale `1`, offset/drift `0`을 사용한다.

## 프로젝트 연결 변경

변경 파일은 `RootDesk/MyDesk/GameData/SkillTable.csv` 한 곳이다. 대상 5행에서 아래 시각 필드만 갱신했다.

- `icon_ruid`
- `layer_ruids`
- `layer_types`
- `layer_styles`
- `layer_delays`
- `layer_durations`
- `layer_scales`
- `layer_offsets_x`, `layer_offsets_y`
- `layer_drifts_x`, `layer_drifts_y`

`monster_id`, `skill_id`, 스킬명, 타입, 계수, 쿨다운, 판정, 효과, 실제 동작 및 `MonsterTable.drop_skill_id`는 변경하지 않았다.

## Maker Play 검증

실제 Maker MCP Play에서 검증했다.

1. `r_001` / `map001`
   - `s_mon_snail_dew_trail`을 플레이어 시전자 기준 오른쪽/왼쪽으로 각각 재생했다.
   - 같은 스킬을 스폰된 몬스터 시전자로 재생했다.
   - 세 경우 모두 `[다층 이펙트] 이슬 미끄럼길 #1 clip` 로그와 스폰 성공을 확인했다.
2. `r_006` / `map006`
   - 5개 스킬 모두 플레이어/오른쪽과 몬스터/왼쪽 조합으로 재생했다.
   - 10회 모두 각 스킬의 `[다층 이펙트] ... #1 clip` 로그가 발생했고 `스폰 실패` 또는 `모르는 레이어 자원 형식` 로그는 없었다.
   - 붉은 껍질 돌진을 좌우로 각각 화면 캡처해 캐릭터 왼쪽/오른쪽으로 정확히 반전되는 것을 확인했다.
   - 마노의 무지개 파동은 512×512 캔버스와 중심 피봇이 인게임에서 흔들리지 않고 캐릭터 중심에 재생되는 것을 화면으로 확인했다.
3. 런타임 데이터 재조회
   - 5개 `skill_id` 모두 새 ICON RUID와 새 AnimationClip RUID를 `_GameData:GetSkill()`에서 확인했다.
   - `m_snail`, `m_blue_snail`, `m_red_snail`, `m_mano`, `m_slime`의 `drop_skill_id`가 기존 5개 `skill_id`를 그대로 가리키는 것을 확인했다.

검증 캡처:

- 마노 중심/피봇: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260911_133104_351.png`
- 붉은 껍질 돌진 왼쪽: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260911_133232_307.png`
- 붉은 껍질 돌진 오른쪽: `C:/Users/dddd/AppData/LocalLow/nexon/MapleStory Worlds/McpScreenshots/maker_play_20260911_133310_522.png`

## 작업 중 확인된 문제

### 반입 과정에서 해결한 문제

초기 Sprite 업로드 완료 응답에서 이름과 subcategory 메타데이터가 비어 있어 Maker Resource Picker의 `Skill` 검색 결과에 정확히 나타나지 않았다. 바이너리를 삭제하거나 다시 올리지 않고 49개 기존 RUID의 메타데이터만 갱신해 이름, 설명, `subcategory=skill`, 피봇 `(0.5, 0.5)`를 복구했다. RUID는 바뀌지 않았다.

### 기존 프로젝트 문제 — 미수정

- `Mislocated/`와 `RootDesk/MyDesk/RootDesk/` 아래의 중복 EntryKey 때문에 Maker Console에 `[LEA-3015] CannotLoad`가 다수 존재한다. 사용자 지시대로 파일을 삭제하거나 이동하지 않았다.
- Build Console의 기존 경고 2건: `mano`의 `MovementComponent.InputSpeed`, `bowmaster`의 `MonsterAttack.AvatarAttackPlayRate` 미사용 경고. 이번 반입과 무관하며 수정하지 않았다.
- 런타임의 `s_mon_mutant_stone_mask passive_stat='DEF'` 오류는 Area 00 반입과 무관한 기존 데이터 문제라 수정하지 않았다.
- r_006 첫 자동 테스트에서 플레이어 저장 위치가 r_001이라 사용자를 찾지 못했으며, 이후 공식 `_TeleportService:TeleportToMapPosition` 경로로 r_006에 이동시킨 뒤 검증을 완료했다. 리소스나 스킬 동작 오류는 아니었다.

## 결론

Area 00의 5개 스킬 VFX와 5개 아이콘은 Resource Storage 등록, AnimationClip 구성, `SkillTable` 연결, 기존 포획/드랍 연결 보존, r_001/r_006 플레이어·몬스터 및 좌우 방향 런타임 검증까지 완료했다. Area 00 외 데이터는 이 반입 작업에서 변경하지 않았다.
