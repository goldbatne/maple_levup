# ChatGPT Images 2.5 입력 이미지 manifest

기준 문서: ../../PILOT_SNAIL_SKILL_IMAGES25_RUNBOOK.md 7절

준비일: 2026-09-10

업로드 순서: REF_01 → REF_02 → REF_03 → REF_04 → REF_05

## REF_01_SNAIL_BODY.png

- 역할: 달팽이의 색, 작은 체급, 둥근 비율 참고
- 출처 animationclip: 2db94405cf0445f5be2b60a02c21dda5
- 사용 프레임: frame 0
- 실제 Sprite RUID: 2d4e2f4ae33e48ff9cf2dd0cf7e9cf16
- 원본: 40×28 RGBA
- 가공: 픽셀을 보존하는 nearest-neighbor 7배 확대 후 320×240 투명 캔버스 중앙 배치
- 최종: 320×240 RGBA
- SHA-256: c3c6d8205e19f4403346c6b2d91e26385b47f9b4ea109401508e12724c0c079b

## REF_02_BODY_TACKLE_LOWLEVEL.png

- 역할: 현행 저레벨 달팽이 스킬의 화면 점유율과 이펙트 밀도 참고
- 배열: 위 3칸은 주동작 레이어, 아래 3칸은 타격 레이어
- 주동작 animationclip: 0207c85c05dd4c4eac12f9ee735d0545
  - frame 0: d217ecdf0a86439e8b23c8d3077a30d2
  - frame 2: 1af1b8a4915f4763908701bb89b3a48a
  - frame 4: dc3524a390774fecab73f269cc24a210
- 타격 animationclip: 997628810df4448f9e534bc426d6794a
  - frame 1: 3df1e75dfd774c15beb71fe38af9a87a
  - frame 3: 13041098fe2f492eba9ea4c53d57aa19
  - frame 5: 1b5758b9749846a9a9c84da07293610a
- 가공: 실제 투명 Sprite PNG를 320×240 셀에 원본 배율로 중앙 배치한 3×2 접촉 시트
- 최종: 960×480 RGBA
- SHA-256: a3d13af4ba406960988b9dfd4559919d7848e977eacfcf59ca2a22144aeb3873

## REF_03_SLASH_BLAST_STYLE.png

- 역할: 준비→절정→소멸 리듬, 3단 명암, 타격 순간의 가독성 참고
- 프로젝트 스킬: s_hero_01 슬래시 블러스트
- 출처 animationclip: eaa71284041b4c8390c32ade11286e16
- 사용 프레임:
  - frame 0: 8a96e5caed9349c38c623492d3b41a1d
  - frame 3: eabc1a7d7f064f56ba688b19c1b84cae
  - frame 6: 4b0276e5a8f04aa48425842f522335f8
  - frame 9: 81a286e4886c4d7ba33225002242d62d
- 가공: 실제 투명 Sprite PNG를 320×240 셀에 원본 배율로 중앙 배치한 4×1 접촉 시트
- 최종: 1280×240 RGBA
- SHA-256: db24f2fcbad8fa570e192e0d19826b9421fd7880ff763d325395e4772ec2efbd

## REF_04_BRANDISH_STYLE.png

- 역할: 가로 진행감, 잔상 굵기 변화, 끝 프레임의 파편화 참고
- 프로젝트 스킬: s_hero_02 브랜디쉬
- 출처 animationclip: 8b26a0cdb63d455e82d1ca0fddf5e139
- 사용 프레임:
  - frame 1: 8fcbc58cafde4f519c0f1e479b9ee424
  - frame 3: 2d3a640055d44a60ab8ab320a4048873
  - frame 6: b4fb563e45bf495f8100643605b053ca
  - frame 9: 4559e5c63e1e4d469b0a9c7f95e9f427
- frame 0은 4×4의 거의 빈 준비 프레임이라 외부 AI가 빈 셀로 오인하지 않도록 frame 1을 선택했다.
- 가공: 실제 투명 Sprite PNG를 320×240 셀에 원본 배율로 중앙 배치한 4×1 접촉 시트
- 최종: 1280×240 RGBA
- SHA-256: b9866d82c4b6bf4f851825db9939f9471107ec42f747e1f2b903b0e361afdbff

## REF_05_AREA00_BACKGROUND.png

- 역할: area_00의 모래색 바닥에서 신규 초록·청록 이펙트의 명도 대비 참고
- 왼쪽 장면: map001 / r_001 버섯마을 외곽
- 오른쪽 장면: map006 / r_006 작은 숲속 샛길
- 확보: Maker 편집 화면의 실제 RectTileMap 뷰포트에서 UI·캐릭터·검은 바깥 영역이 없는 구간을 각각 잘라 좌우 결합
- 최종: 760×475 RGB
- SHA-256: 342759cd9cce91f375223949dade1282b273b3d5c8dc779a7efb2af6fdaafa53
- 참고: Play 캡처도 시도했으나 기존 미추적 복제 폴더의 중복 EntryKey 로드 오류 때문에 타일이 단색으로 표시되어 채택하지 않았다. 프로젝트 파일을 임의로 이동·삭제하지 않고, 정상 타일이 보이는 편집 뷰포트를 사용했다.

## 사용 주의

- 외부 ChatGPT Images에는 위 5개 PNG만 번호순으로 첨부한다.
- 이 manifest와 런북은 프롬프트 확인용이며 이미지 첨부 대상으로 세지 않는다.
- REF_03과 REF_04의 검격 모양이나 공격 메커니즘을 복제하지 않는다. 각각 명암·프레임 리듬과 가로 잔상 정리만 참고한다.
- REF_02의 기존 몸통 박치기를 신규 스킬 모양으로 복제하지 않는다. 저레벨 규모만 참고한다.
