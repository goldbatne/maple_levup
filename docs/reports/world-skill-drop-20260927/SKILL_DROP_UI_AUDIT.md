# Skill Drop UI 육안 감사

## 최종 형태

- 월드 렌더러가 지원하는 `PixelRendererComponent`로 Skill Frame을 구성했다.
- 프레임 중앙은 투명하게 유지하여 기존 Skill Icon을 가리지 않는다.
- Icon은 기존 RUID 연결을 그대로 사용한다.
- 이름/획득 안내와 E 상호작용은 기존 Interaction UI 경로를 재사용한다.
- UI 전용 RUID를 `SpriteRendererComponent`에 넣지 않았다.

## 상태별 확인

| 상태 | 육안 결과 | 판정 | 증빙 |
|---|---|---|---|
| 생성 직후 | 금색/암색 Skill Frame, Icon, 이름, E 상호작용이 읽힘 | PASS | [60초](evidence/skill_drop_final_60s.png) |
| 30초 이하 | 남은 시간이 초 단위로 표시됨 | PASS | [30초](evidence/skill_drop_final_30s.png) |
| 10초 이하 | `!` 접두와 적색/주황 경고 프레임으로 긴급도가 구분됨 | PASS | [10초](evidence/skill_drop_final_10s.png) |
| 상호작용 | 기존 E 키 안내가 Skill Drop에 연결됨 | PASS | [상호작용](evidence/skill_drop_final_interact.png) |
| 다중 Drop | 4개 Drop이 작은 독립 프레임으로 보이며 전투 화면을 과도하게 가리지 않음 | PASS | [다중](evidence/skill_drop_final_multiple.png) |
| 방 복귀 | 동일 논리 Drop이 남은 절대 시간으로 다시 표시됨 | PASS | [복귀](evidence/skill_drop_final_backtracking.png) |
| 만료 후 복귀 | 만료된 Drop은 다시 나타나지 않음 | PASS | [만료](evidence/skill_drop_final_expired_backtracking.png) |

## 기존 Interaction UI와의 차이

- 기존 방식은 상호작용 텍스트가 중심이어서 아이템과 스킬을 시각적으로 즉시 구분하기 어려웠다.
- 최종 방식은 Drop 자체에 Skill Frame을 붙여, 멀리서도 “획득 가능한 스킬”임을 먼저 전달한다.
- E 키 상호작용은 별도 대형 패널을 추가하지 않고 기존 안내를 유지한다.
- 여러 Drop이 있을 때 텍스트를 상시 크게 펼치지 않아 화면 혼잡을 줄였다.

## 결론

최종 UI는 기존 Icon 자산과 Interaction 경로를 보존하면서 Skill Drop 의미, 남은 시간, 긴급도, 다중 배치 가독성을 충족한다. 새로운 이미지 아트는 제작하지 않았다.
