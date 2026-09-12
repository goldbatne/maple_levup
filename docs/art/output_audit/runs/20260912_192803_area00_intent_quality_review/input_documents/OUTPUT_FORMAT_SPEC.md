# Output Format Spec

## 필수 주 납품 형식

- **frame-separated PNG files are mandatory.** VFX의 주 산출물은 `F00`, `F01`, `F02` ... 형식의 개별 RGBA PNG 프레임이다.
- **contact sheet is optional preview only. sprite sheet is not the primary deliverable.** 시트는 개별 프레임을 대체할 수 없다.
- PNG, RGBA, 실제 alpha 투명 배경. 흰색/검정/체커보드 배경 금지.
- 프레임마다 동일 캔버스, 동일 중심축/피봇, 동일 스케일. 임의 크롭·재중앙화 금지.
- 우측 진행 기준으로 제작하고 런타임 FlipX를 고려한다.
- one-shot. 빈 프레임과 누락 프레임 금지. `F00`부터 끝 프레임까지 연속 번호를 사용한다.
- ICON은 256×256 RGBA PNG 1장, 글자·숫자·UI 프레임·몬스터 본체 금지.

## 표준 규격군

| Profile | 필수 개별 VFX frames | Canvas/frame | Timing | 용도 |
|---|---:|---:|---:|---|
| LOW_ACTIVE | 8 | 256×256 | 0.10s | 저레벨 단일 액티브 |
| MID_AREA_ACTIVE | 8 | 384×384 | 0.10s | 중·고레벨 범위/다중 액티브 |
| BOSS_ACTIVE | 12 | 512×512 | 0.08s | 보스급 액티브 |
| BUFF_SELF | 8 | 256×256 | 0.10s | 자기 중심 버프 |
| PASSIVE_ICON_MOTIF | 6 | 256×256 | 0.10s | 현행 런타임 미적용 참고 모티브 + 아이콘 |

달팽이 파일럿의 8 frames / 0.1 sec / Offset X64 Y0은 LOW_ACTIVE 참고값이다. 모든 스킬에 같은 오프셋을 강제하지 않으며 각 개별 프레임 내부의 공통 피봇은 반드시 유지한다.
