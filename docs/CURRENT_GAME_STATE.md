# 현재 구현 기준 — Mega Area / 2026-09-22

이 문서는 현재 코드·데이터의 설명이다. 새로운 기획 승인이나 전수 Runtime 인증이 아니다. 기존 스킬 감사 baseline은 별도 보존한다.

## 현재 플레이 루프

Mega Area와 NORMAL / MONSTER_SKILL 선택 → 솔로 또는 파티 준비 → Seed 기반 방 구성 → 혼합 조우 → Run 능력 풀 확대 → 5칸 랜덤 재고 소비 → 최종 보스 → Clear / Fail / Abandon → 로비.

| 항목 | 현행 구현 | 근거 |
|---|---|---|
| 능력 보유 | Run `OwnedSkillPool`, 영구 ★ 강화 없음 | `PlayerSkillSlots.OfferRunAbility`, `PlayerCollection.GetAbilityMultiplier` 관련 Run 분기 |
| 획득 | 첫 적격 능력 보장, 이후 적격 처치 10% | `PlayerSkillSlots.TryAcquireRunAbility`, `run_ability_acquire_rate` |
| 전투 슬롯 | 최대 5칸 일회성 재고, 동일 SkillID 중복 가능 | `SupplyOneRandomSkill`, `ConsumeRandomSlot` |
| 공급 | 빈 슬롯에 5초마다 1개 | `StartRandomSkillSupply`, `run_skill_supply_interval` |
| 사용 | 성공한 슬롯 소비, Run 플레이어 개별 cooldown 우회 | `PlayerAttack` Run 분기 |
| 보유 능력 창 | 현재 Run 능력의 정보 표시; 임의 장착 UI 아님 | `EquipPanel`, `rebuild-run-owned-skills-window.cjs` |
| 기본 수치 | HP 1000 / 공격 35 / 방어 10 (잠정 설정) | `GameBalance.csv`, `PlayerStats` Run 분기 |
| 지역 | 기존 20개 Area → 5개 Mega Area, AREA 06 없음 | Mega Area mapping 및 `GameData` |
| 저장 | 기존 RPG/M2 저장 보존, Run과 영구 기록 분리 | `PlayerDBManager`, `SavePermanentData`, `PlayerSkillSlots` |
| 도감 정산 | 이번 Run 새 발견은 서버 임시 원장. CLEAR/FAILED 시 반영, ABANDON 시 폐기. 이전 영구 도감 유지 | `GameData.RoguePendingDiscoveries`, `PlayerCollection.FinalizeRogueliteDiscoveries` |

`GameBalance.csv`의 일부 설명 열과 코드의 과거 주석에는 고정 장착/쿨다운 문구가 남아 있다. 값과 실행 분기는 위와 같으며 이 문서 정리에서 게임 데이터나 주석은 수정하지 않았다. 향후 기능 변경 때 설명 열도 함께 갱신한다.

## 데이터 집계와 검증 범위

- MonsterTable 정의 103종: 일반 연결 101종 + 히어로/보우마스터 2종.
- SkillTable 전체 112개: monster source 102개 + boss source 10개.
- 실제 몬스터 drop 연결 101개: 액티브/방어 66개 + 비활성 패시브 35개.
- 연결되지 않은 `s_mon_snail / 몸통 박치기` 1개는 레거시. 현재 달팽이는 `s_mon_snail_dew_trail`과 연결한다.
- 데이터에 패시브가 존재한다는 것은 Run 획득/실행 가능하다는 뜻이 아니다.
- 프레임형 VFX는 `layer_types=sprite_sequence`, 한 레이어 안 프레임은 쉼표, 레이어 간 구분은 `|`다. `SkillEffect`/`SkillCastEffect`가 이 형식을 실행한다.

## 정적 검사

프로젝트 루트에서 실행:

```text
node docs/tools/verify-content-coverage.cjs
node docs/tools/test-current-content.cjs
node docs/tools/verify-knowledge-base.cjs
node docs/tools/audit-mega-connectivity.cjs
```

첫 검사는 CSV 열/중복 ID/몬스터·스킬·방·지역 연결/레이어 배열과 개별 프레임 RUID/현행 설정을 검사한다. 필수 테이블이 비어 있거나 필수 이름이 누락된 경우, 실행 숫자 열에 비숫자·무한대·필수값 누락이 있는 경우도 거부한다. 기존 기본값을 사용하는 선택적 숫자 빈칸과 `cooldown=0`은 허용한다. 서버에서 실제 리소스가 재생됐음을 인증하지 않는다. 회귀 테스트는 메모리 복사본의 104개 오류와 빈칸·0 쿨다운 호환성을 검사하며 납품 데이터는 바꾸지 않는다.

기존 RPG 검사는 `--legacy-rpg`로 보존한다. 이전 레이어 개수·스택·RPG UI 기대값 때문에 실패할 수 있으며 현행 검사를 대신하지 않는다. 기존 실패를 통과로 덮어쓰지 않는다.

## Runtime 증거의 적용 시점

- [PR 제출 전 추가 검증](reports/pr-readiness-20260922/PR_READINESS_REPORT.md): 현행 66종의 실제 발동·소비·효과 관측, QA 위치 보조를 사용한 5개 Mega Area 완료. 스킬 VFX 전수 시각 승인이나 멀티 인증이 아니다.
- [Mega Area 개편 결과](reports/mega-area-random-encounter-20260921/FINAL_MIGRATION_SUMMARY.md): 현행 공급/소비 기반. 사람 입력만으로 모든 중간 통로 완주한 검증은 NOT_RUN이라고 기록되어 있다.
- [연결/리스폰 결과](reports/mega-area-connectivity-respawn-20260921/FINAL_REPORT.md): 이후 포탈 및 연결 보정.
- [파티/나가기 UI 결과](reports/party-area-ui-20260921/FINAL_REPORT.md).
- [버튼 크기](reports/ui-button-size-audit-20260922/UI_BUTTON_SIZE_AUDIT.md), [RPG HUD 잔재 제거](reports/roguelite-ui-residue-audit-20260922/ROGUELITE_UI_RESIDUE_AUDIT.md).
- 실제 2~4클라이언트 협동은 미검증. 단일 서버 상태 검사를 협동 Runtime PASS로 승격하지 않는다.
- 개편 전 66개 스킬 발동 증거는 역사 자료다. 당시 슬롯 유지/쿨다운 검증은 현행 슬롯 소비/쿨다운 우회 검증과 다르다.

## 보존 자료와 커밋

스킬 감사 baseline과 승인 아트, 과거 맵 비교본은 삭제/덮어쓰기 대상이 아니다. `docs/reports/commit-preparation-20260922/`의 파일 분류와 해시 목록으로 이번 정리를 추적한다. 스테이징/커밋/PR은 별도 실제 결과로 기록한다.
