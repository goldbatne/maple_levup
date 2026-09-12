# PILOT 달팽이 스킬 Images 2.5 반입·검증 보고서

## 적용 결과

- 원본 보존: `pilot-snail-images25/output/OUT_SNAIL_DEW_TRAIL_SHEET_ORIGINAL.png`
- 정규화 시트: `1024×512` RGBA
- 분할 결과: `256×256` RGBA 8장, 빈 프레임 0장
- 순서: `f00 → f07`
- 공통 원점: 원본 시트 기준 `(64,128)`, AnimationClip의 각 프레임 `Offset X 64 / Y 0`으로 재현
- 프레임 지연: 각 `0.1초` (총 `0.8초`)
- AnimationClip: `fx_mon_snail_dew_trail`
- AnimationClip RUID: `74cd5784067849bf865c80b2f2ebf795`
- 스킬 ID/이름: `s_mon_snail_dew_trail` / `이슬 미끄럼길`
- 스킬 값: ATK `0.9`, 쿨다운 `5초`, 범위 `2.5`, 범위 대상 최대 `3`, 이펙트 스케일 `0.65`
- 달팽이 `m_snail`의 드랍 스킬을 신규 스킬 ID로 연결했으며 기존 `s_mon_snail` 행은 보존했다.

Sprite RUID 전체 목록은 `pilot-snail-images25/output/RESOURCE_MANIFEST.md`에 기록했다.

## 확인된 검증

- 입력 이미지 `1774×887`, RGBA, 실제 알파 `0~255`, 투명 모서리 확인.
- 비율 변경 없이 `1024×512`로 정규화했다. 자르기·트리밍·프레임별 재중앙화·디자인 수정은 하지 않았다.
- 8개 Sprite가 계정 Resource Storage의 `sprite/skill`에 등록되고 메타데이터 조회에 성공했다.
- Maker AnimationClip Editor에서 8프레임 순서, 공통 오프셋, 0.1초 지연 및 재생을 확인했다.
- 계정 Resource Storage의 `animationclip/skill` 검색에서 위 AnimationClip RUID와 설명을 재조회했다.

## 반입 중 확인된 문제

- 원본의 비표준 크기는 2:1 비율을 유지한 전체 리사이즈로 해결했다.
- LANCZOS 리사이즈로 프레임 외곽에 알파값 1의 링잉 픽셀이 있으나, 알파 16 초과 경계 접촉은 0이고 눈에 보이는 프레임 절단은 없었다.
- 프로젝트 안의 기존 미추적 중복 복사본 때문에 Maker Console에 `[LEA-3015] Duplicate EntryKey`가 999건 이상 누적되어 있다. 해당 파일은 이번 작업 소유가 아니므로 삭제·이동하지 않았다. 이 상태는 새 CSV 반영을 위한 Refresh와 r_001/r_006 Play 검증을 신뢰할 수 없게 만드는 외부 차단 요인이다.

## 런타임 검증 상태

- AnimationClip 자체 Maker 재생: 통과.
- `layer_ruids` 및 `m_snail.drop_skill_id` 파일 연결: 완료.
- r_001/r_006, 플레이어/몬스터, 좌/우 방향 Play 검증: 기존 Duplicate EntryKey 오류가 제거되기 전까지 미완료. 완료했다고 간주하지 않는다.
