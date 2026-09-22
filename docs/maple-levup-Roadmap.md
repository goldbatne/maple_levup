# Maple Levup — Milestone roadmap

> 🔖 Cross-milestone direction: vision · release criteria · one slot per milestone · Backlog.
> This is NOT a GDD — the active milestone's contract is its `-M<n>-GDD.md`.
> Last updated: 2026-09-17

## Vision & release criteria

- Vision: 몬스터를 테이밍·성장시키고 그 능력을 균등 랜덤 5슬롯으로 직접 사용해 보스를 공략하는 탑다운 수집형 액션 RPG.
- Release criteria: 몬스터 컬렉션·중복 ★성장·비전투 동행·랜덤 능력 전투, 자동 레벨 성장, 자유 지역 진입, 유형별 사냥터, 보스 챌린지가 런타임에서 검증된다.

## Milestones

| M | Theme (one line) | Status |
|---|---|---|
| M1 | 기능 플래그 기반 랜덤 스킬 전투 핵심 → `maple-levup-M1-GDD.md` | ✅ Maker verified |
| M2 | 실제 포획 액티브 66종 태그, 가중 랜덤과 초기 특성 → `maple-levup-M1-Phase2.md` | ✅ Maker verified |
| M3 | 환생·전직·직접 4스탯·지역 입장 제한 제거와 저장 마이그레이션 → `maple-levup-M1-Phase3.md` | ✅ Maker verified |
| M3.5 | Trait 신규 모드 비활성, 첫/중복 포획 분리, 패시브 포획 제외 → `maple-levup-M1-Phase3.5.md` | ✅ Maker verified |
| M3.6 | 천장 없는 순수 확률 포획과 실제 첫 포획 E2E → `maple-levup-M1-Phase3.6.md` | ✅ Maker verified |
| M4 | 대표 사냥터 압축 검증 → `maple-levup-M1-Phase4.md` | 🧪 78.1% 평지 원칙 verified; type-by-type rollout held |
| M2A | `TamedMonsters` schema v5, 101종 컬렉션, 액티브 66종 연동, 패시브 35종 수집, 비전투 동행 → `maple-levup-M2A.md` | 🟡 Implemented; Maker verification pending |
| M2B | 대표 3종 동행 효과 | ⛔ M2A 플레이 확인 전 미착수 |
| M5 | 10층 탑, 최초 클리어 성장, 솔로/파티 개인 보상 | planned |
| M6 | 레이드 보스 1종, 인원별 HP, 버프 중첩, 참여자 보상 | candidate |

## Backlog (wanted, not yet slotted)

- 패시브 전용 몬스터 35종의 액티브 대체 능력 — M2A에서는 수집·동행만 허용, 후속 범위 미정
- 기존 히어로·보우마스터 보스/장비의 비전직 콘텐츠 재배치 — M3 기획 결정 후 처리
