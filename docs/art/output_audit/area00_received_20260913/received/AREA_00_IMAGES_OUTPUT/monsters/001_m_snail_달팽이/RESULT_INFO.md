# RESULT INFO — 달팽이 / 이슬 미끄럼길

- monster_id: `m_snail`
- skill_id: `s_mon_snail_dew_trail`
- skill_type: `액티브`
- boss: `N`
- VFX: 8 frames, 384×384 RGBA PNG, 0.10 sec/frame
- ICON: 256×256 RGBA PNG
- generation tool: `native image generation/editing — version/model unverified`
- post-process: source sprite-sheet cells separated without per-frame auto-crop; one common VFX transform per skill was applied to preserve shared canvas/axis/scale, then exported as individual RGBA PNGs.

## Quality gate

- Intent: **PASS** — manifest/spec의 monster_id, skill_id, 이름, 타입, 역할을 유지
- Identity: **PASS** — 각 몬스터 고유 소재 모티브를 사용하고 몬스터 본체는 미삽입
- Rendering: **PASS** — 유색 외곽/그림자, 중간톤, 제한된 밝은 코어와 입체 재질 확인
- Alpha: **PASS** — RGBA, 실제 0~255 alpha 및 반투명 픽셀 검사
- Motion: **PASS** — 준비→성장→절정→해체→fade 순서로 프레임 변화
- Stability: **PASS** — 동일 스킬 VFX에 공통 좌표 변환 적용, 개별 자동 크롭 없음
- Icon: **PASS** — 256×256 RGBA, VFX와 공통 색·형태 언어
- Isolation: **PASS** — 개별 자산에 텍스트/UI/몬스터 본체 없음

## Notes

- 이미지 생성 모델의 정확한 버전/모델 식별자는 검증되지 않아 지정 문구로 기록함.
