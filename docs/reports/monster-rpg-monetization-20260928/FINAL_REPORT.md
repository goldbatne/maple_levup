# Monster RPG 성장 경제·Monetization 기반 — 2026-09-28

대상은 `D:/maplestory_levup` 원본 프로젝트다. 기존 미커밋 동행/전투 변경은 보존했고 commit/push하지 않았다. Maker Play는 기존 계정의 실서비스 저장이 아닌 `MakerTest_RoguelitePermanentV1` 키를 사용했다.

## 구현

| 항목 | 상태 | 내용 |
|---|---|---|
| Product Catalog | PASS_DEV | `MonsterProductCatalog` 데이터셋 3종. 가격 0/PlatformProductId 공란은 미출시 DEV 설정이며 실결제 아님. |
| Monster Selection Ticket | PASS_SERVER | 구매성 지급 후 기존 101칸 컬렉션에서 몬스터 선택. 미보유 Lv1, 보유 Lv+1, 서버에서 수집 가능/상한/잔량 검사. |
| Growth Essence Pack | PASS_SERVER | 기존 `MonsterGrowthCurrency` 원장에 합산. 별도 정수 재화 없음. |
| Growth Core Pack | PASS_SERVER | 신규 `MonsterGrowthCore` 영구 원장에 합산. |
| 무료 Core | PARTIAL | Mega Area 완료의 참가자별 서버 후처리에서 설정값 1개 지급. Run에서 완료 메서드 경로로 검증했으나 이번 변경 후 자연 Boss 처치 재실행은 못했다. |
| Core로 Monster Level +1 | PASS_SERVER | 로비에서 보유/비용/상한 검증 후 Core 차감과 MonsterLevels 증가를 같은 영구 저장 확인 경로로 처리. |
| 구매 서버 검증 | PASS_DEV / BLOCKED_PLATFORM | `WorldShopService.SetProcessPurchaseCallback` 사용. 실제 상품 ID가 등록되지 않아 플랫폼 거래는 수행하지 않았다. Maker DEV 요청도 동일 `ProcessReward`를 사용한다. |
| 중복 거래 | PASS_RECENT | PurchaseId 원장 확인 후 지급. 즉시 재전송과 Maker 재접속 후 동일 ID 모두 재지급되지 않았다. 성공한 플랫폼 콜백 중복은 다시 지급하지 않고 ACK한다. |
| 구매 제한 | PARTIAL | NONE, DAILY 3회, WEEKLY 2회를 데이터/서버에서 처리. DAILY/ WEEKLY Maker 한도 실측. ACCOUNT_ONCE와 UTC 기간 경계는 미실행. |
| 저장 이관 | PARTIAL | v1–v3를 v4로 읽고 새 필드는 0/빈 원장으로 초기화. v3 합성 데이터의 몬스터 Lv/강화/정수/편성 보존 확인. 실제 구계정 v3 재접속은 미실행. |
| 재접속 | PASS | Maker Stop→Play에서 v4 Core, Monster Lv/Enhance, 정수, 구매 영수증, Area Clear 유지. |
| 무료 성장 | PARTIAL | 기존 자연 테이밍·중복·정수·강화 실측 보고서를 재사용. 이번에는 무료 Core 서버 완료 경로만 추가 확인; 무구매 신규 계정 E2E는 미실행. |
| 3 Companion | PASS_START | 이번 Run 입장 후 3 Entity Spawn 확인. 자연 전투/Portal은 직전 Runtime 보고서의 결과를 재사용했다. |
| Random 5 Slot | PARTIAL_REUSED | 직전 Runtime 보고서에서 획득/5초 공급/슬롯 소비 확인. 이번 Run은 입장 직후 빈 슬롯만 확인. 관련 코드는 변경하지 않았다. |
| Boss Regression | PARTIAL_REUSED | 직전 보고서의 실제 Boss 처치 기록과 이번 `CompleteRogueliteRun` 서버 경로 확인. 이번 변경 후 자연 보스전 전체 재실행은 하지 않았다. |
| Build | PASS | 최종 Refresh/Play에서 Error 0, Info 53, 기존 Warning 4. |
| Runtime | PASS_CLEAN_SESSION | 최종 로그 초기화 후 Play에서 Error 0. 이전 QA 스크립트가 Run 인스턴스 플레이어를 server_main에서 조회해 발생시킨 nil `p` 오류 1건은 게임 코드가 아닌 테스트 호출 오류로 별도 기록. |

## 저장·거래 설계

- `RoguelitePermanentV1` payload의 `schema_version=4`: `growth_core`, `monster_selection_tickets`, `purchase_receipts`, `purchase_receipt_order`, `purchase_limits` 추가. 기존 몬스터/장비/Run 기록을 초기화하지 않는다.
- Maker는 `MakerTest_RoguelitePermanentV1`에만 저장한다. 실계정 `Perm`/`Run`을 QA 목적으로 초기화하지 않았다.
- 유료성 지급·선택권 사용·코어 소비는 같은 서버 영구 키의 동기 저장이 성공해야 확정된다. 저장 실패 시 런타임 수치와 payload를 되돌리는 경로를 둔다. 기존 Rogue 영구 저장도 순서 보장을 위해 동기 쓰기로 직렬화했다. 이 변경의 실제 운영 지연/크레딧 비용은 별도 부하 테스트가 필요하다.
- Purchase ID는 최근 256개를 순환 보존하고, 지난 DAILY/WEEKLY 제한 버킷은 제거한다. 이는 단일 저장 레코드의 무한 성장을 막는다. 256건을 넘어 오래된 성공 ID가 재전달될 때의 방어는 플랫폼의 성공 ACK 재전달 정책 검증 전까지 **실결제 출시 차단 조건**이다.
- WEEKLY는 UTC 월요일 시작 7일 버킷이다. DEV 테스트 중 구 임시 버킷에서 새 버킷 공식으로 바뀌어 MakerTest의 한 주간 누적 테스트 구매량은 실제 출시 계정의 한도 예시가 아니다. 최종 새 버킷에서는 2회 뒤 세 번째 요청이 거부됐다.
- 현 카탈로그의 `Price=0`, `PlatformProductId=""`는 실제 판매 설정이 아니다. 플랫폼 상품 등록·가격 확인·실거래 콜백/환불/장기 재전달 검증 전에는 실결제 완료로 보고하지 않는다.

## Maker 근거

- `schema=4 core=0 ticket=0 essence=200 shop=true ready=true` 로드 확인.
- DEV 상품 A 지급 → 선택권 1; 컬렉션 선택 경로에서 `m_red_snail` Lv0→1. 보유 `m_slime`은 선택권으로 Lv1→2.
- 상품 B 후 정수 200→220, 이후 DAILY 총 3회로 260/3회, 4번째 거부. 정수 5를 사용해 `m_red_snail` Enhance +1, 재접속 후 정수 255.
- 상품 C 후 Core 0→3; `m_red_snail` 코어 사용으로 Lv1→2/Core 3→2. 미보유 `m_blue_snail` 사용 거부; 임시 Lv20 상한에서는 차감 거부 후 테스트 값을 Lv2로 복구.
- 동일 `DEV:IDEMPOTENCY:20260928` 요청은 첫 번째 true·두 번째 false, 티켓 0→1→1. Maker 재접속 후 다시 false.
- 선택권 상한은 Maker 격리 데이터의 `m_red_snail`을 임시 Lv20으로 두고 클라이언트 RPC를 보냈다. 티켓 1/Lv20이 유지됐고 테스트 값을 Lv2로 복구했다.
- `mega_01` Run에 3 Companion Spawn 확인. `CompleteRogueliteRun`을 QA 스크립트가 직접 호출해 Core 2→3, Area Clear 8→9, 동기 저장, 로비 복귀 확인. 이는 보스 자연 처치 검증이 아니다.
- 재접속 시 `schema=4`, `m_red_snail Lv2/+1`, `m_slime Lv2`, Core 3, 정수 255, 티켓 0, `mega_01` Clear 9 확인(주간 상품 추가 DEV 테스트 전의 값).
- 최종 Refresh/Play 새 세션: Build Error 0/Warning 4, Runtime Error 0. 기존 세 Balance 키 누락 경고 0건.

## UI

로비 전용 상점 버튼과 3개 상품 카드, DEV TEST/제한 표시, 선택권 사용 버튼을 추가했다. 선택권은 기존 101칸 컬렉션 격자를 재사용한다. 컬렉션 상세에는 Level/Enhance/정수/Core 및 `[코어로 Level +1]`을 표시한다. Maker 화면에서 패널과 격자 표시를 확인했다: [상점 화면](shop_dev_products.png), [선택 격자](ticket_monster_grid.png).

Maker MCP `mouse_input`은 엔진 관리 ButtonClickEvent를 클릭하지 못한다. UI 핸들러/클라이언트 RPC를 `maker_execute_script`로 호출한 것이며, 실제 마우스·터치 클릭 PASS로 주장하지 않는다.

## 남은 확인

1. 플랫폼 상품 3종 등록 및 정확한 PlatformProductId/가격 설정 후 실제 결제→서버 콜백→저장→재접속, 실패/환불/오래된 재전달 시나리오 확인. 현재는 BLOCKED_PLATFORM.
2. 실제 v3 저장 계정의 읽기 전용 백업을 둔 이관 Play, 새 계정 무구매 E2E, ACCOUNT_ONCE 및 날짜/주간 경계 검증.
3. 이번 코드로 자연 Boss Kill → 무료 Core, 3 Companion 자연 Boss/Player SkillBar/Portal 회귀. 이전 결과는 재사용했으나 이번 변경 후 전수 재실행은 아니다.
4. 모바일 실버튼 클릭과 상점/선택 UI 입력 차단·닫기 동작 검증.

관련 테스트: [상품](PRODUCT_CATALOG.csv), [25개 검증](PURCHASE_RUNTIME_TEST.csv), [Core](GROWTH_CORE_TEST.csv), [이관](SAVE_MIGRATION_TEST.csv), [중복 거래](DUPLICATE_TRANSACTION_TEST.csv), [무료 진행](FREE_PROGRESS_TEST.csv).
