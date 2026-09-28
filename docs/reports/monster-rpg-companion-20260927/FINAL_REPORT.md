# Monster RPG companion 개편 검증 기록

기준 프로젝트: `D:\maplestory_levup`  
시작 기준 HEAD: `0335fdd` (기존 미커밋 M2 변경 위에 작업; 기존 변경 보존)  
검증 상태: **정적 데이터·코드 연결 확인, Maker 빌드/Runtime 미확인**  
커밋·푸시: 수행하지 않음

## 적용 내용

- 로비 컬렉션의 기존 5개 버튼 중 1~3번을 서로 다른 소유 몬스터 편성, 4번을 재화 강화로 재사용했다. 5번의 임의 스킬 편집은 숨겼다. 고유 스킬명과 설명은 읽기 전용이다.
- Run에서 소유자별로 편성 몬스터 최대 3마리를 생성하도록 바꿨다. 각 동행에는 `OwnerUserId`와 `SlotIndex`가 있으며, 비전투 시 0°/120°/240° Anchor로 이동한다. 전투 중에는 개별 타겟을 찾아 접근하고, 투사체 스킬 보유 시 사거리를 유지하며, 대상이 없어지면 편성 위치로 돌아간다. 대상 접근 좌표도 슬롯별로 분산한다.
- 동행의 특수 스킬은 `MonsterTable.drop_skill_id` 하나만 설정한다. 플레이어의 임의 `MonsterSkillLoadouts`는 신규 모드에서 요청을 거부하고, 저장 원본은 보존한다. 패시브 연결 몬스터는 기본 공격만 한다. 소유자별 특수 시전 간격은 0.35초 초기값이다.
- 첫 테이밍은 Lv.1, 중복 성공은 레벨 +1이다. 10%/3% 확률은 기존 값 그대로이고 신규 상한은 Lv.20 설정값이다. 별도 강화 상한도 +20이다. 처치 자격을 받은 각 플레이어에게 일반 1, 보스 10 성장 정수를 서버에서 자동 지급한다. 강화 비용은 `5 + 현재 강화 단계 × 2`다. 수치는 모두 초기 설정값으로 조정 가능하다.
- 레벨·강화는 동행의 HP/기본 공격/고유 스킬 피해 또는 자기 방어·강화 효과에만 적용한다. 플레이어의 기본 공격과 Random SkillBar에는 합산하지 않는다.
- Companion이 쓰러지면 해당 슬롯만 현재 방에서 복귀하지 않고, 다음 맵 전환에서 다시 생성한다. Run 종료 시 3개 엔티티를 정리한다.
- Rogue 저장 스키마를 v3으로 올렸다. 기존 `tamed_monsters` ★값을 초기 `monster_levels`에, `selected_companion`을 첫 편성 슬롯에 대응시킨다. 기존 `monster_loadouts`와 알 수 없는 저장 항목은 삭제하지 않는다. 레벨·강화·정수·3칸 편성은 영구 저장하고, HP/엔티티는 저장하지 않는다.

## 확인한 근거

- `MonsterTable.csv`와 `SkillTable.csv`를 ID로 결합: 테이밍 가능한 101종, 고유 활성/방어 66종, 패시브 등 비활성 35종. 고유 SkillID 중복 연결 0건. 동행 표시 RUID 존재 101/101.
- `CompanionCombat.Configure`가 MonsterTable의 `drop_skill_id`만 읽는지, 로비 요청이 동일 몬스터 중복 편성을 거부하는지, 새 Rogue 저장 필드가 읽기/쓰기에 모두 있는지 소스에서 확인했다.
- 설정 CSV 두 사본의 새 키가 일치하고, Maker의 오래된 import 복사본을 위한 `GameData.LoadBalance` fallback도 넣었다.
- `git diff --check` 통과. 감사 생성 스크립트 실행 통과.

## 아직 확인하지 못한 것

Maker 전용 `refresh`/`play`/`logs` 도구가 이번 세션의 연결 목록에 없다. 열려 있는 Maker 창은 확인했지만 UI 화면 캡처가 두 번 시간 초과되어 조작 가능한 화면 상태를 얻지 못했다. 따라서 **Build Error 0이나 Runtime PASS를 주장하지 않는다.** 다음 항목은 `NOT_RUN`이다.

- 첫/중복 자연 테이밍, 실제 재화 획득 및 강화, 저장·재접속
- 3마리 동시 생성, Formation/추적/독립 전투/고유 스킬/사망·다음 방 복귀
- Portal, Boss, Player Random 5 Slot, Skill Drop, 상자 회귀
- 2~4인 멀티클라이언트 성능과 동기화

동행 66종의 실제 판정 및 시각 연출도 이번에는 전수 Runtime PASS가 아니다. 각 테스트 CSV에 `NOT_RUN`을 유지했다. Maker 연결이 회복되면 Refresh → Build 로그 → 대표 유형별 실제 플레이 → 재접속/Run 종료 검증이 필요하다.

## 변경 파일

이번 요청의 신규 변경: `RootDesk/MyDesk/Progress/PlayerCollection.mlua`, `RootDesk/MyDesk/Combat/CompanionCombat.mlua`, `RootDesk/MyDesk/Save/PlayerDBManager.mlua`, `RootDesk/MyDesk/UI/EquipPanel.mlua`, 두 `GameBalance.csv`, `Mislocated/MyDesk/GameData/GameData.mlua`, 이 보고서의 생성 도구와 CSV. 이미 작업 트리에 있던 다른 변경은 되돌리거나 커밋하지 않았다.
