# 스킬 다양성 원작·설정 대조 후속 상태

대상: `D:/maplestory_levup`의 현재 플레이어 획득 가능 액티브/방어 스킬 66종. 시작 HEAD `5bd7f4de9dbda5ed5b99af4d77a1d5046be26ac5`, 브랜치 `codex/skill-diversity-rework-20260922`. 2026-09-24 작업 시작 시 이미 스킬 코드·CSV와 일부 맵/UI에 미커밋 변경이 있었다. 해당 변경을 reset/revert/일괄 커밋하지 않았다.

## 결과 범위

- `LORE_DESIGN_66.csv`와 `MONSTER_66_DESIGN.md`: 66개 SkillID, 몬스터명/ID, 원작 또는 프로젝트 근거, 직전 판정과 현행 판정, Player 툴팁, MONSTER_SKILL 사용 방향, 아이콘/VFX 식별자, 새 Maker 실행 상태를 행별로 기록했다.
- `VFX_REVIEW_BOARD_01.png`·`VFX_REVIEW_BOARD_02.png`: 기존 PNG의 아이콘과 대표 VFX 프레임을 66종 모두 병렬 대조했다. AREA 00 승인 재사용분은 AREA 00 폴더를 우선했다. 이는 대표 프레임 시각 확인이며 전 프레임 재생이나 실제 판정 확인은 아니다.
- 공식 Nexon의 개별 몬스터 설정 문서를 대부분 확보하지 못했다. 커뮤니티 위키의 World Archive 전사 및 개별 몬스터 페이지는 **공식 원문 URL이 아닌 2차 근거**로 분류했다. 페이지의 최초 발행일 및 어떤 게임 버전의 설명인지는 미확인이다. 프로젝트에서 만든 스킬 모티브(포자, 인형탄, 중력장 등)는 원작 사실로 승격하지 않았다. 프로젝트 자료만 확실한 4개 항목은 `PROJECT_ONLY`다.
- 직전 66종 개편의 11개 행동 어댑터를 유지했다. 66종의 연결·소재·대표 VFX를 대조한 뒤 명백한 판정/설명 불일치 6종만 타입과 툴팁을 보정하고 나머지 60개 툴팁은 기존 문구를 유지했다. **이는 60종의 전술적 다양성이 충분하다는 판정이 아니다.** 기존 Center/Direct 편중 감사 자체는 반복하지 않았다.
- 현행 66종은 주 기능 기준 공격 63종, 방어 3종이다. 공격 63종 중 20종은 감속·약화·기절·밀기·끌기 중 하나를 겸한다. 11개 `behavior`는 대체로 공격의 범위/시점/이동 궤적 분류이므로, 이 숫자만으로 버프·방어·지원·사용 판단의 다양성을 인증할 수 없다. 이 항목은 별도 몬스터별 역할·전술 검토가 필요하다.
- 실제 판정 보정 4종: 주니어 발록 `CENTER_BURST → FRONT_CONE`, 타우로마시스 `CENTER_BURST → DELAYED_BLAST`, 데우 `DAMAGE_ZONE → DELAYED_BLAST`, 마뇽 `CENTER_BURST → FRONT_CONE`. 아이콘/VFX의 방향·시점과 원작/프로젝트 설정을 대조한 결과다. 전후 PNG 근거는 `docs/art/design-review-07-20/20260914_astra_review/AREA_07/s_mon_jr_balrog/`, `AREA_07/s_mon_tauromacis/`, `AREA_13/s_mon_deo/`, `AREA_16/s_mon_manon/`에 있다.
- 추가로 타입/실제 대상 수가 모순된 투사체 2종만 보정했다. 샤크는 `PIERCING_PROJECTILE → PROJECTILE_BLAST`(물상어 탄환이 끝에서 흩어지는 VFX), 마티안은 `PIERCING_PROJECTILE → PROJECTILE`(단발 광선탄 VFX)이다. 둘 다 기존 `max_targets=1`을 보존해 다중 타격을 새로 만들지 않았다. PNG 근거는 `AREA_10/s_mon_shark/`, `AREA_18/s_mon_mateon/`에 있다.
- 스퀴드의 `SLOW` 추가는 기존 동작의 확인된 오류가 아니라 선택적 개선이어서 제외했다. `MonsterAttack.ResolveMonsterSpatialHit`에 시도했던 공통 변경도 이번 몬스터별 정합성 범위 밖이므로 제외했다.
- `SkillID`, 몬스터 연결, 계수, 사거리, 최대 대상, 아이콘/이펙트/투사체 RUID는 이번 후속 보정에서 변경하지 않았다. 5초 랜덤 공급·슬롯 소비 및 다른 게임 시스템도 수정하지 않았다.

## 다양성 비교의 해석

원래 기준(이전 개편 전)에는 `CENTER_DIRECT` 44종, 투사체 12종, 돌진 7종, 방어 3종이었다. 직전 미커밋 개편에서 66종이 11가지 실제 행동 어댑터로 분화되었고, 이번 보정에서 중심 즉발 8→5종, 전방 부채꼴 12→14종, 지연 폭발 7→9종, 지속 장판 9→8종, 관통 투사체 3→1종이 되었다. **이번 후속 작업이 66종 전부에 새 메커니즘을 추가한 것은 아니다.** 전투 판단의 실질적 개선 정도는 자연 전투 및 Player/MONSTER_SKILL 실제 실행 확인 전에는 확정하지 않는다.

## 검증 상태

| 항목 | 결과 | 근거/한계 |
|---|---|---|
| 66개 SkillID·몬스터·아이콘/VFX 참조 | PASS_STATIC_ONLY | `verify-skill-lore-redesign.cjs`, 기존 `verify-skill-diversity-rework.cjs` — 실제 Maker 리소스 로드 인증은 아님 |
| 6개 판정·해당 6개 툴팁의 CSV 반영 | PASS_STATIC_ONLY | `verify-skill-lore-redesign.cjs` |
| 변경 데이터의 Player/Monster 어댑터 연결 | PASS_STATIC_ONLY | GameData 로더와 두 Attack 코드의 분기 존재 검사. 실제 타격·방향·VFX 렌더 확인 아님 |
| Maker Refresh/Build | NOT_RUN | 이 세션의 도구 목록에 Maker 호출·빌드 로그 도구가 제공되지 않음 |
| 변경 후 Player 66종 실행 | NOT_RUN | 2026-09-23 기존 QA는 변경 전 결과. 현재 결과로 재인증 금지 |
| 변경 후 MONSTER_SKILL 66종 실행 | NOT_RUN | 2026-09-23 기존 QA는 이번 데이터/공통 몬스터 수정 전 결과 |
| 보스 제어·지형·자연 전투·UI 66종 확인 | NOT_RUN | 정적 검사로 PASS 불가 |

`node docs/tools/verify-skill-lore-redesign.cjs` 출력: `PASS_STATIC_ONLY`, 66종, 판정 6, 보조 효과 0, 툴팁 6, 실패 0. `node docs/tools/verify-skill-diversity-rework.cjs`도 66종/11 행동의 기존 정적 계약을 통과했다. `git diff --check` 통과. 이 결과는 Maker Build Error 0 또는 Runtime Error 0을 의미하지 않는다.

## 남은 필수 실행

Maker 연결이 가능해지면 현재 프로젝트를 Refresh/Build하고, **현행 코드·데이터로** Player 사용과 MONSTER_SKILL의 변경 영향 범위를 실행해야 한다. 실제 판정, HP 변화, 방향·지형 충돌, 부가 효과/보스 저항, VFX 위치·재생, 슬롯 소비, 5초 공급 불변, UI 툴팁을 분리하여 기록한다. 새로 바뀐 6개 판정이 우선 회귀 대상이다. 모든 66종의 Run 전수 실행은 이번 몬스터별 설정 정합성 판단의 선행 조건으로 삼지 않는다. 미실행 항목을 PASS로 기재하지 않는다.

시각적 미해결도 분리한다. `SkillEffect.PlayAttackAt`은 현재 좌우 FlipX만 전달하므로 상하·대각선 조준의 전방/직선 판정과 가로형 원화가 실제 화면에서 같은 방향으로 보이는지 미확인이다. 샤크의 프로젝트 스킬 이름 `포식자의 수류탄`과 현재 수류탄보다 물상어형으로 보이는 VFX도 사용자 아트 해석 확인 대상으로 남긴다. 이 불확실성만으로 승인 원화·SkillID를 임의 교체하지 않았다.

역할 검토에서 블러드 하프도 별도로 보류했다. [커뮤니티 위키의 World Archive 전사](https://maplestorywiki.net/w/Blood_Harp)는 노래로 상대의 명중률을 낮춘다고 설명하지만, 현재 `s_mon_blood_harp`는 직선 피해만 준다. 이는 몬스터 개성의 미반영 후보이나, 프로젝트 `PlayerHit.mlua`와 `PlayerStats.mlua`에는 회피/명중 확률 판정을 의도적으로 폐기한 기록이 있다. 스킬 하나를 맞추기 위해 전체 명중 시스템을 복구하는 것은 이번 '틀린 부분만 수정' 범위를 넘으므로 효과를 추측해 대체하지 않았다.

## 출처와 안전 범위

원작 자료는 각 행의 URL을 확인한다. 예를 들어 [타우로마시스](https://maplestorywiki.net/w/Tauromacis), [마뇽](https://maplestorywiki.net/w/Manon), [스퀴드](https://maplestorywiki.net/w/Squid)는 커뮤니티 위키 페이지이며 공식 Nexon 인증 자료가 아니다. 개별 능력의 이름·이펙트는 프로젝트 SkillTable/기존 PNG에서 확인한 자료와 구분했다. Git commit/push 없음.
