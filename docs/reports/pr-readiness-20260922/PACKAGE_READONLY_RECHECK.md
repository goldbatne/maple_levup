# 독립 커밋 패키지 재검사

검사일: 2026-09-22. 읽기 전용 점검이며 Maker Runtime 결과를 대신하지 않는다.

기준 브랜치: `codex/mega-area-pr-readiness-20260922`.
검사 시 HEAD: `1ec91d5dc95f3638a6e5ac855274a10289070982`.

## 검사 결과

| 검사 | 결과 |
|---|---|
| `node docs/tools/verify-content-coverage.cjs` | exit 0, PASS_STATIC |
| `node docs/tools/test-current-content.cjs` | exit 0, 현행 데이터 + 104개 음성 변이 + CSV/기본값 호환 검사 PASS |
| `node docs/tools/verify-knowledge-base.cjs` | exit 0, 현행 문서 5개 및 링크 10개 PASS_STATIC |
| `git diff --check` | exit 0, 출력 없음 |
| 기존 보호 파일 484개 해시 대조 | 예상 밖 변경 0 |
| 스킬 다양성 기준본 해시 | 변경 0 |
| `docs/art` Git 작업 트리 변경 | 0 |

보호 파일의 변경 3개는 이번 승인 범위와 일치한다.

- `RootDesk/MyDesk/GameData/GameData.mlua`: 마지막 생존자 포기 후 사망 참가자만 남는 경우 종료 판정.
- `RootDesk/MyDesk/Progress/PlayerSkillSlots.mlua`: 추가 소비 시 이미 진행 중인 공급 타이머 유지.
- `RootDesk/MyDesk/UI/AreaSelectPanel.mlua`: 후행 공백 정리.

보존 대조 정본은 `../commit-preparation-20260922/PROTECTED_FILES_BEFORE.json`이다. 아트 파일은 이 484개 목록에 포함되지 않으므로, 아트에 관한 결과는 Git 변경 상태 검사이며 별도 전수 바이트 해시 검사라고 주장하지 않는다.

## 공개 패키지 안전성 범위

앞선 독립 패키지 검사에서 런타임 경로의 ignored 파일과 `.mlua`의 `.codeblock` 짝 누락은 없었다. 기존 삭제 26개 중 실파일 24개는 RootDesk 대체가 있으며 나머지 2개는 Mislocated 디렉터리 메타데이터다. 이동한 JSON형 파일 18개의 식별자 변경은 없었다.

커밋 후보 텍스트와 ZIP/TAR 11개의 텍스트 엔트리 253개에서 인증 토큰·개인키의 명백한 패턴은 발견하지 못했다. 이는 비밀정보 부재의 완전한 증명이 아니다. 이번 재검사에서는 새 QA 스크립트 3개와 `SKILL_RUNTIME_OBSERVED.json`에도 동일한 인증 패턴 및 장문 숫자 계정 식별자 노출이 없었다.

QA 파일은 `docs/reports`에 있어 Maker 런타임 자동 등록 파일이 아니다. `skill-runtime-qa.lua`는 Maker/Solo/테스트 저장 영역을 검사한다. `traverse-and-boss-qa.lua`의 SOLO 표기와 사용자 수 가드 일치 여부는 별도 최종 리뷰 항목으로 전달했다. 이 검사는 스크립트를 실행하지 않았다.

## 제한

- 기존 스킬/맵의 플레이 품질이나 2~4인 동시 접속을 승인한 결과가 아니다.
- 영구 발견 기록의 Abandon 보존 정책은 수정하지 않았다.
- stage, commit, push 또는 외부 업로드를 수행하지 않았다.

## 추가 수정 후 재검사 — 2026-09-22

위의 최초 검사 기록은 당시 상태로 보존한다. 이후 포탈 알림 RPC 수명 수정과 생성 사전검사 상태 복원이 추가되어 아래와 같이 다시 점검했다.

- 현행 데이터 검사, 문서 검사, 104개 음성 변이 회귀 검사, `git diff --check` 모두 다시 exit 0.
- `test-portal-notice-regression.cjs`: PASS_STATIC, 음성 테스트 4개.
- `test-preflight-state-regression.cjs`: PASS_STATIC, 생성 상태 필드 20개·관련 helper 18개·음성 테스트 3개.
- 기존 `prepare-commit-inventory.cjs`로 커밋 파일 목록과 해시를 갱신했다.
- 보호 파일 484개 중 예상 변경은 5개이며, 예상 밖 변경 0개·추가 보호 파일 0개·분석 baseline 변경 0개.
- 변경된 5개는 `GameData.mlua`, `PlayerSkillSlots.mlua`, `RoomPortal.mlua`, `AreaSelectPanel.mlua`, `GateNotice.mlua`다.
- `docs/art` 작업 트리 변경 0개.
- 추가된 generator QA 및 회귀 도구를 포함해 이 폴더의 텍스트 파일 9개를 점검했으며 인증 토큰·개인키·장문 숫자 계정 식별자 패턴 검출은 없었다.
- `traverse-and-boss-qa.lua`에 실제 참가자 수 1명 가드가 추가된 것을 확인했다. 최초 검사 때 전달한 SOLO 표기 불일치는 해결됐다.

인벤토리 생성은 성공했으나 Git이 사용자 전역 ignore 파일의 읽기 권한 경고를 출력했다. 저장소 내부 `.gitignore`와 실제 커밋 후보 목록은 확인했으며, 이 경고를 테스트 실패나 런타임 오류로 계산하지 않았다.

이 추가 검사에서도 Maker Runtime을 실행하지 않았다. generator QA의 실제 실행과 플레이 회귀 결과는 주 실행 보고서의 범위이며, 여기의 PASS_STATIC을 Runtime 승인으로 사용하지 않는다.

## 사용자 승인 발견 기록 정책 반영 후 최종 재검사 — 2026-09-22

이전 절의 정책 보류는 아래 승인 이후 해소되었다. Abandon은 이번 Run의 신규 몬스터·능력 발견만 폐기하고, 기존 영구 기록은 보존한다.

- 신규 발견은 `GameData.RoguePendingDiscoveries[userId]` 서버 메모리 원장에만 기록된다. `GatherRogueliteRecords()`가 읽는 영구 컬렉션에 임시 대입하지 않는다.
- CLEAR/FAILED 확정 뒤 기존 영구 기록에 추가 병합하며, Abandon은 해당 참가자의 임시 기록만 폐기한다. 늦은 Clear/중복 종료의 상태 가드를 확인했다.
- 기존 저장 payload와 저장 namespace는 변경하지 않았다. 기존·미등록 식별자를 삭제하는 rollback은 없다.
- `test-discovery-settlement.cjs`: PASS_STATIC_AND_POLICY_MODEL. 소스 음성 테스트 2개와 저장/포기/종료/개인 이탈/새 Run 등 정책 모델 8개 통과.
- 현행 데이터 검사, 문서 검사(링크 11개), 음성 변이 104개, 포탈 회귀 검사, 사전검사 복원 검사(현재 필드 21개), `git diff --check`를 다시 실행해 모두 exit 0.
- 보호 파일 484개 중 예상 변경은 최종 6개다. 기존 5개에 `RootDesk/MyDesk/Progress/PlayerCollection.mlua`가 추가됐다. 예상 밖 변경 0개·보호 파일 추가 0개·분석 baseline 변경 0개.
- 추가 QA 텍스트에서 인증 토큰·개인키의 명백한 패턴 검출은 없었다.

재접속 범위는 구분한다. 살아 있는 동일 Instance에 기존 참가자가 다시 등록되는 경우 terminal 분기에서 발견 정산을 호출하는 코드는 있다. 그러나 Instance/서버 메모리가 이미 사라진 뒤 임시 발견을 복원하거나 오프라인 참가자에게 지속적으로 전달하는 장치는 구현되지 않았다. 실제 멀티 재접속 Runtime도 이 독립 검사에서 수행하지 않았다.

이 최종 재검사는 게임 파일을 수정하지 않았으며 보고서와 기존 인벤토리 출력만 갱신했다. Maker의 실제 저장 테스트와 빌드 결과는 주 실행 보고서로 확인해야 한다.

## 보스 HUD 최소 수정 후 재검사

- 최종 보호 파일 484개 유지, 추가·삭제 0. 예상 변경 7개에 PlayerHud.mlua가 추가되었으며 나머지 477개 해시는 기준과 동일.
- 정적 6스크립트 모두 exit 0: 현행 데이터, 104개 음성 변이, 문서 5개/링크 11개, 포탈 4개 음성, preflight 21필드/18 helper/3개 음성, 발견 정산 2개 음성/8개 정책 모델.
- 독립 검토자는 이 재검사에서 게임 파일 변경·Maker 실행을 하지 않았다. 최종 실제 HUD 화면과 새 Build는 주 실행 보고서 및 FINAL_HUD_EVIDENCE.json에 분리 기록한다.
