# 전체 AREA 스킬 아트 반입 검증

- 실행 폴더: `ALL_AREAS_20260914_151243`
- 대상: AREA 00–05, AREA 07–20
- AREA 06: 입력/출력 패키지 없음 — 변경 없음
- 상태: **반입 완료 / 파일·연결·리소스 저장소 검증 PASS / Maker 실행 검증 NOT_CHECKED**

## 반입 결과

- AREA 00 수정 후보: 기존 Sprite RUID 23개 이미지 교체
- AREA 01–05, 07–20: 신규 Sprite RUID 687개 생성
- 신규 자산 구성: ICON 99개, VFX 프레임 588개
- 후보 스킬: 99개
- AREA 00 중복 우선 보존: `s_mon_blue_snail`, `s_mon_slime`, `s_mon_snail_dew_trail`
- 실제 SkillTable 신규 후보 연결: 중복 3개를 제외한 96개 스킬
- SkillTable SHA-256: `3a84b837edc8615e423dcc1da6a89a0237a36d3c481f310338fbe016a211023b`

## 검증 결과

각 AREA에서 다음을 검사했다.

- 반입 계획과 RUID 매핑의 누락 여부
- 원본 PNG SHA-256 일치
- PNG가 RGBA이며 유효한 alpha를 포함하는지
- ICON 및 VFX 프레임의 SkillTable 연결
- 프레임 순서와 `sprite_sequence` 연결
- 업로드 RUID가 계정 리소스 저장소에서 `sprite`로 조회되는지
- AREA 00 중복 스킬이 기존 AREA 00 행을 유지하는지

AREA 01–05, 07–20의 687개 자산은 모두 위 검사를 통과했다. AREA별 세부 결과는 같은 폴더의 `AREA_XX_IMPORT_VALIDATION.json`에 저장했다.

## 중심축 메타데이터

신규 RUID 중 1개는 `pivot_x=0.5`, `pivot_y=0.5`가 명시되어 있다. 나머지 686개는 서버 메타데이터에 pivot 항목이 따로 표시되지 않는다. 원본 프레임은 동일 캔버스와 중심축을 유지하지만, Maker에서의 기본 pivot 적용 결과는 실행 검증 항목으로 남긴다.

## 코드 반영

프레임 분리 PNG를 순차 재생하기 위해 다음 파일에 `sprite_sequence` 처리를 추가했다.

- `RootDesk/MyDesk/GameData/GameData.mlua`
- `RootDesk/MyDesk/GameData/GameDataVerify.mlua`
- `RootDesk/MyDesk/Combat/SkillCastEffect.mlua`
- `RootDesk/MyDesk/Combat/SkillEffect.mlua`

정적 변경 검사에서는 공백 오류가 없었다.

## 남은 검증

현재 세션에는 Maker의 `refresh`, 빌드 로그, `play`, `stop` 도구가 제공되지 않아 다음 항목은 확인하지 못했다.

- Maker Refresh 후 mLua 등록 및 빌드 로그
- 실제 전투에서 프레임 재생, 위치, 크기, 기본 pivot
- ICON 표시
- 게임 반입 후 시각적 타이밍

따라서 실행 결과를 PASS로 기록하지 않았으며 상태는 `NOT_CHECKED`이다.
