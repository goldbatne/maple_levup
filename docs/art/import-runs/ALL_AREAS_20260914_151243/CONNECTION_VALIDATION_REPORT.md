# 스킬 아트 연결 검증

- 검증 시각: 2026-09-14
- 범위: AREA 00–05, AREA 07–20

## 최종 판정

**정적 연결 PASS / Maker 데이터셋 등록 PASS / 실제 VFX 스폰 PASS**

- 몬스터와 스킬 연결: 99/99
- 대상 고유 스킬: 101개
- 신규 RUID: 687개 모두 계정 리소스 저장소에서 `sprite`로 조회
- AREA 00 기존 Sprite RUID: 23개 교체 상태 유지
- Maker Refresh: PASS
- 빌드 오류: 0
- Play 데이터 로드: PASS
- 실제 VFX 시전 요청: 69건
- 다층 이펙트 스폰 로그: 72건
- SkillEffect 오류: 0건

`SkillTable`은 로컬에서 `Mislocated/MyDesk/GameData`에 있지만, Play 상태의 `_GameData:GetSkill`을 통해 모든 대상 스킬이 정상 조회됐다. 현재 Maker 세션에 데이터셋이 등록되어 있음이 확인됐다.

AREA별 실행 증거는 같은 폴더의 `AREA_XX_RUNTIME_CONNECTION.json`에 저장되어 있다. 화면상 크기·pivot·프레임 미감은 이번 연결 검증에 포함하지 않았다.
