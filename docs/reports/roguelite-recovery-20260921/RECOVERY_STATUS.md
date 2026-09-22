# 로그라이트 복구 진행 및 실제 검증

> 후속 갱신: [LOBBY_RUNTIME_FOLLOWUP.md](LOBBY_RUNTIME_FOLLOWUP.md), 2026-09-21. 아래는 초기 검증 이력이다. Save 승인 후 maptown에서 실제 인스턴스를 시작하여 입장 및 실패/클리어 로비 복귀 moved=1을 확인했다. 기존 moved=0/저장 승인 대기 문구는 과거 테스트 조건의 기록이며 현행 차단 사유가 아니다. 중복 시작/Run 내부 시작 차단도 후속 검증했다. 다른 미검증 항목은 자동 통과시키지 않는다.

대상: `D:/maplestory_levup`, 2026-09-21. **전체 완료 아님.**
브랜치 `codex/art-packages-cleanup-20260915`, HEAD `2eb7498eda8f53440648ef6107d6c933ba55d5c6` 위의 미커밋 작업 트리다. 기존 변경을 reset/revert/일괄 커밋하지 않았다.

## 보호 범위

- 작업 전 복원 자료: `pre-recovery.zip`, SHA-256 `EA72C01706ED4F739056585DD9F87D80295A586F1EFF8BAA578F209AD58FA198`.
- 이전 스킬 감사 baseline 및 roguelite-rework 사본은 수정하지 않았다.
- 현재 SkillTable SHA-256 `3a4af00f0cc9ef3439e9c4cbda4e80f0cfe86cd4072202ad5b08a994a5828c36`, MonsterTable `6783014b6990f67988b4d17d5ae3b0b741896433fcefe3849449b7e06073b5e2`: 이번 작업 시작 기준과 동일.
- 스킬 계수/범위/타격 수/몬스터 매칭/VFX를 변경하지 않았다.
- Maker 테스트는 `MakerTest_RoguelitePermanentV1`만 사용한다. 신규 모드에서 기존 Perm/Run을 쓰지 않는다. 실계정의 이전 손실 여부를 조사하거나 추정 복구하지 않았다.
- Maker Play는 마지막에 중지했다. 커밋/PR 없음.

## 실제 수정

| 파일 | 변경 |
|---|---|
| `RootDesk/MyDesk/Save/PlayerDBManager.mlua` | 독립 저장 키/schema 1, Maker 전용 키, 필수 데이터 로드 실패 시 저장 잠금, 미등록 식별자 보존, 설정 키 배치 저장, 빈 중첩 table 직렬화 대응, 로드 null 검사, profileCode 로그 제거 |
| `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua` | 후보 FIFO/중복 제거/정리 정책, 요청 revision, Run 종료 공통 정리, 서버 쿨다운과 클라이언트 표시·방어막 정리 |
| `RootDesk/MyDesk/Progress/PlayerTravel.mlua` | 인스턴스→정적 Room 이동 분리, 피격 콜백의 yield 오류를 피하도록 지연 호출 |
| `RootDesk/MyDesk/GameData/GameData.mlua` | 서버 확정 그래프의 클라이언트 전달, 지정 목표 몬스터 확인, Area 00·01 도달형 목표 설정, 생존자 최종방 집결 확인, 그래프 검증/fallback 거부, 재등록 회복 방지, 종료 타이머 Run revision 보호, 로비 전환 결과 기록 |
| `RootDesk/MyDesk/Room/RoomPortal.mlua` | 이전 맵의 중복 전환 요청 차단, 전환 후 도달 목표 검사 |
| `RootDesk/MyDesk/UI/SkillBar.mlua` 및 `ui/SkillBar.ui` | 독립 획득 선택 패널·대기 수·교체/포기, 전투 단축키의 오교체 제거, 실제 5개 키만 등록 |
| `RootDesk/MyDesk/UI/RoomProgressHud.mlua` | Run 시작 후에도 갱신되도록 구독, 실제 목표/결과 표시, 우측 지도와 분리한 레이아웃 |
| `RootDesk/MyDesk/UI/PlayerHud.mlua` | 신규 모드 전반 레벨/EXP 숨김(배경 포함), 도달형/종료 후 잘못된 보스 HUD 숨김 |
| `RootDesk/MyDesk/UI/StatPanel.mlua`, `InventoryPanel.mlua` | 로비에서도 신규 모드의 투자/장비 버튼 및 창 비활성 |
| `RootDesk/MyDesk/UI/WorldMapPanel.mlua` | 원래 고정 연결 대신 서버 Run 연결 표시, 테이밍 확률/장비 대신 능력 확정 획득 안내, 타입 주석 경고 정리 |

UI 변경은 기존 UIBuilder를 사용했다. `RoomProgress.ui` 쓰기는 UNKNOWN open 오류로 실패해 원본은 보존했다. 해당 모드의 배치는 문서화된 UITransform 속성으로 런타임 적용한다. 별도 원화 제작 없음.

## 확인된 오류와 처리

1. 없는 저장 키의 Value=null을 JSONDecode에 전달: nil/빈 문자열 가드 추가. 새 세션 로드 확인.
2. SyncTable에 존재하지 않는 Clear 호출: 알려진 SkillID 키에 nil 대입으로 변경. 이후 Run 시작 및 종료 실행 확인.
3. 중첩 빈 table의 JSONEncode UnknownType: 실제 Maker에서 `{settings={}}`가 실패하고 scalar/비어 있지 않은 객체는 성공함을 분리 재현했다. 직렬화 사본에서 빈 컨테이너만 생략하고 로드 시 빈 table로 복원. dirty는 저장 성공 전 내리지 않는다.
4. 서버 Run=true인데 클라이언트 GameData=false: `clientRun=false slotRun=true hud=false`로 재현. 서버 뷰 전달 후 `active=true seed=92105 hud=true` 확인.
5. 피격 이벤트에서 Room 이동의 yield 불가: 타이머 경유로 수정. 이후 해당 예외는 재발하지 않았지만 실제 정적 로비 이동은 여전히 실패한다.
6. 포탈 이동 보조 테스트에서 전환 후 이전 포탈 RPC의 유효하지 않은 TargetUserId: 현재 맵 일치 가드 추가. 최신 가드의 연속 포탈 회귀는 미완료.

과거 실패 로그는 `runtime-evidence.json`에 보존했다. 이후 수정됐다고 과거 기록을 지우지 않았다.

## 검증 결과 (Maker 시각 원문 기준)

| 항목 | 결과 및 한계 |
|---|---|
| 새 Build Console | 마지막 읽기 Error 0 / Warning 2 / Info 0. 경고는 07:20:16의 mano InputSpeed, bowmaster AvatarAttackPlayRate 기록이 남아 있음. 새로 재현된 경고라고 주장하지 않음 |
| 자연 처치→능력 | 07:45:03 달팽이 실제 공격/사망→1번 장착. 당시 저장 실패도 함께 기록. 수정 후 07:48:26 같은 경로 저장 완료 |
| 저장 왕복 | 07:51:42 `reloadDiscovery=1 loaded=true`. Maker 전용 키의 발견 기록만 확인. 실제 운영 저장 이관은 NOT_RUN |
| 연속 후보 | 7종 능력을 테스트 서버에서 주입해 5칸+후보2 구성. 제작/자연 획득 7종 실측은 아님 |
| 중복 요청 | 같은 revision으로 교체 요청 2회: 첫 후보만 교체, 다음 스텀피 후보 유지. 이후 포기 요청 실행 |
| UI | 실제 화면에서 선택 패널, 5칸, HP, 목표 표시 확인. 클릭 도구만으로 버튼 성공이 입증되지 않아 RPC 검증과 구분. 모든 메뉴 ESC/Mask 전수 검증은 미완료 |
| 고정 슬롯/쿨다운 | 08:01:37 사용 후 `s_mon_snail_dew_trail` 유지 및 남은 쿨다운 4.503초 표시. 모든 스킬 유형의 벽 충돌 검증 아님 |
| 도달형 목표 | seed 92107, r_001→r_006→r_003→r_00a. 위치 보조 및 실제 RoomPortal 경로로 전환. 07:58:18 COMPLETE/클리어 저장. 자연 탐색 완주·지형 충돌 통과로 집계하지 않음 |
| 실패 정리 | 08:01:58 OnRunPlayerDied를 테스트 호출. 08:02:02 슬롯 nil/후보 정리/active=false. 피격 사망 풀 플레이 테스트는 아님 |
| 다음 Run | 08:02:11 빈 5슬롯 시작 로그, 08:02:24 seed92109 pending0 failed=false HP1000. 같은 Maker 맵 재사용의 조우 초기화는 별도 미검증 |
| 쿨다운 완전 초기화 | 실패 검사에서 비교한 파란 달팽이 readyAt은 실패 전에도 nil이었다. 따라서 비어 있지 않은 쿨다운의 종료 초기화까지 실증했다고 주장하지 않음 |
| 로비 복귀 | **FAIL**: 08:02:01 `moved=0 requested=1`, 플레이어 map001 잔류. 완료/실패 후 자연적인 메뉴 복귀 루프는 미완료 |
| 생성 반복 검사 | Area 02 seed2026에서 fallback 연결 검증 거부 확인. 전체 반복 검사는 도중 중지했고 Run 시작 요청과 겹쳐 최종 집계하지 않음. 전 Area Seed 재현 PASS 아님 |
| 협동 | **NOT_RUN**. 현재 도구에서 실제 컨텍스트는 client 1개 + TestPlayInstance 서버. 2~4인 실행/재접속 지원 완료로 보고하지 않음 |

## 남은 작업 — 순서를 유지

1. **Maker 미저장 상태 확인 및 정적 로비 기동**: 현재 map01 편집 상태의 Save는 미저장 사용자 맵을 덮을 수 있어 도구 승인에서 거부됐다. 우회하지 않음. 사용자가 저장 상태를 확인한 뒤 maptown 기동/Room 이동을 검사해야 한다. 이번 변경으로 `엔트리 저장 실패`의 재시작 내구성이 해결됐다고 주장하지 않는다.
2. R03/R04: Mislocated의 디렉터리 메타데이터 4개는 임의 삭제하지 않았다. Save/Refresh/재시작 후 엔트리·테이블 위치 안정성 미완료.
3. R07/R11: fallback의 원본 최종방 선택과 도달형 목표의 정합성, 주경로 길이/가지길 예산 검증, 비공개/미검증 Area 노출 정책 추가 확인. 그래프 검사와 실제 타일 통과 가능성은 별개.
4. R09: 협동 준비 명단 및 모든 메뉴/ESC/Mask/모바일 입력 회귀. 새 선택 패널의 스킬 효과 설명 상세 표시 추가 점검.
5. R10: 로비 복귀, 다음 Run 조우 재생성, 비영(非零) 쿨다운/방어막 종료 초기화, 내부 이동/부활 쿨다운 보존의 대조 검증.
6. R11: 실제 투사체/돌진/범위 스킬의 벽·출입구·VFX 판정 위치를 대표 유형부터 검증. 고유 효과는 수정하지 않음.
7. R12: 독립된 2/3/4 클라이언트에서 참여 보상·집결·관전·유예·재접속. 단일 컨텍스트 함수 호출을 멀티 실측으로 대체하지 않음.
8. R13: 남은 2개 모델 경고의 현재 등록값/메타데이터 확인. 확인 없이 속성을 삭제하지 않음.

## 현행 문서 및 이미지

- 위험 목록 원문: `../ROGUELITE_RECOVERY_RISKS_20260921.md` (당시 관찰 이력).
- 현재 작업 상태: `../../Roguelite-Recovery-Phase.md`와 이 파일.
- 과거 Archive/As-built 및 M1/M2 문서는 역사 자료이며 현행 로그라이트 지침이 아니다. 보존 기준본은 수정하지 않음.
- `maker_play_20260921_075146_931.png`: 획득 후보2/교체 패널 (중간 상태).
- `maker_play_20260921_075830_191.png`: 도달형 완료/로비 미복귀 (중간 상태, 이후 잘못된 보스 HUD 숨김 수정).
- `maker_play_20260921_080224_854.png`: 다음 Run HUD.
- `runtime-evidence.json`: 선별 로그. 계정 식별 숫자는 마스킹. 실제 저장 payload는 미포함.

**판정: 핵심 수정 및 부분 런타임 확인. 전체 복구/솔로 완주/협동 완료는 승인할 수 없음.**
