# 스킬 다양성 개편 현행 결과

원본 프로젝트 `D:/maplestory_levup`의 현재 SkillTable/MonsterTable과 이전 66종 분석·원작 대조표에서 기계적으로 생성했다. 이 보고서 생성기는 게임 파일을 수정하지 않는다.

행 수: 66. PrimaryRole은 중복 없는 주 역할이며 SecondaryRole은 별도 집계한다.

| 주 역할 | 현행 | 요청 목표(±2) | 판정 |
|---|---:|---:|---|
| DIRECT | 19 | 14–18 | 목표 이탈 |
| PROJECTILE | 11 | 8–12 | 범위 안 |
| AREA | 6 | 6–10 | 범위 안 |
| DASH | 7 | 6–10 | 범위 안 |
| DEFENSE | 5 | 4–8 | 범위 안 |
| CONTROL | 13 | 4–8 | 목표 이탈 |
| BUFF | 1 | 3–7 | 목표 이탈 |
| DEBUFF | 4 | 3–7 | 범위 안 |
| SPECIAL | 0 | 0–4 | 범위 안 |

이전 감사 기준에는 `CENTER_DIRECT`가 44/66이었다(`SKILL_BEFORE.csv`). 현행은 중심 즉발 `CENTER_BURST` 5/66이며, 방향·지연·지속·투사체·돌진·방어/강화/제어 판정으로 분화했다. 다만 현행 DIRECT 19, BUFF 1, CONTROL 13은 요청 목표 범위 밖이다. 숫자만 맞추기 위한 역할 재명명은 하지 않았다.

이번 후속 보완에서 바뀐 핵심 역할: 북치는 토끼는 북 연주 공격 강화, 추억의 수호대장·셰이드는 시전자 방어, 슬라임은 점성 감속, 불가사리는 회전 가시 밀기, 엘리쟈는 폭풍 감속, 에인션트 다크골렘은 지진 기절, 변형 스텀피는 뿌리 감속이다. 그 밖의 상태 중심 피해 조정과 66종별 전후 값은 `SKILL_66_CURRENT.csv`를 참조한다.

재검증 중 엘리쟈의 PULL·고대 골렘의 KNOCKBACK은 단일 표적을 폭발 중심에 자동 조준할 때 이동 방향 벡터가 0이라 핵심 제어가 발동하지 않는 문제가 드러났다. 검수만 완화하지 않고 중심 표적에도 적용되는 SLOW/STUN으로 실제 데이터를 고친 뒤 66종을 재실행했다.

Player Maker QA: [SkillRework66] DONE observed=66 pass=66 fail=0 notRun=0 harnessOk=true cleanupOk=true seconds=138.165 (2026-09-25T23:08:09)
MONSTER_SKILL Maker QA: [MonsterSkillRework66] DONE observed=66 pass=66 fail=0 notRun=0 harnessOk=true cleanupOk=true seconds=57.717 (2026-09-25T23:09:45)

QA는 실제 UseSkill/CastSkill 호출, 효과·슬롯·쿨다운 경로의 어댑터 실행 검증이다. 몬스터 66종 각각의 자연 AI 시전, 모든 VFX 프레임의 육안 승인, 실제 전투 체감/밸런스 인증은 아니다.

원작 출처는 행별 SourceType/SourceURL 참조. COMMUNITY_WIKI 항목은 공식 Nexon 원문이 아닌 2차 자료이며 발행·업데이트 시점은 미확인이다. PROJECT_ONLY 모티브는 원작 사실로 간주하지 않는다.

설정·아트 근거가 빈약한 역할을 목표 수치에 맞추기 위해 억지로 추가하지 않았다. 주 역할 분포의 목표 이탈은 미해결 설계 항목으로 남는다.
