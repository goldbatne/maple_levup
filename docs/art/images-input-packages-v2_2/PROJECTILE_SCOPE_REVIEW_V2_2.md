# PROJECTILE SCOPE REVIEW — V2.2

12개 몬스터 투사체의 현행 역할을 코드 기준으로 분리했다. `range`는 targeting, 착탄 피해는 공통 `projectile_hit_radius`다.

| Area | monster | skill | data range | player targeting | monster targeting | impact radius | delay | max targets | required art | existing projectile |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| area_02 | `m_stumpy` | `s_mon_stumpy` | 5 | 5 | 3.335 | 0.8 | 0.35 | unlimited | PROJECTILE+ICON replace | replace planned |
| area_03 | `m_faust` | `s_mon_faust` | 4 | 4 | 2.668 | 0.8 | 0.35 | unlimited | CAST_VFX+ICON | KEEP; extra approval needed |
| area_08 | `m_star_pixie` | `s_mon_star_pixie` | 6 | 6 | 4.002000000000001 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |
| area_08 | `m_lunar_pixie` | `s_mon_lunar_pixie` | 6.4 | 6.4 | 4.268800000000001 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |
| area_10 | `m_shark` | `s_mon_shark` | 6.5 | 6.5 | 4.335500000000001 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |
| area_11 | `m_king_bloctopus` | `s_mon_king_bloctopus` | 6.8 | 6.8 | 4.5356000000000005 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |
| area_14 | `m_roid` | `s_mon_roid` | 7 | 7 | 4.6690000000000005 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |
| area_14 | `m_chimera` | `s_mon_chimera` | 6.8 | 6.8 | 4.5356000000000005 | 0.8 | 0.35 | unlimited | CAST_VFX+ICON | KEEP; extra approval needed |
| area_15 | `m_peach_monkey` | `s_mon_peach_monkey` | 7 | 7 | 4.6690000000000005 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |
| area_15 | `m_tae_roon` | `s_mon_tae_roon` | 6.6 | 6.6 | 4.4022 | 0.8 | 0.35 | unlimited | CAST_VFX+ICON | KEEP; extra approval needed |
| area_17 | `m_dodo` | `s_mon_dodo` | 7 | 7 | 4.6690000000000005 | 0.8 | 0.35 | unlimited | CAST_VFX+ICON | KEEP; extra approval needed |
| area_18 | `m_mateon` | `s_mon_mateon` | 7.4 | 7.4 | 4.9358 | 0.8 | 0.35 | 1 | CAST_VFX+ICON | KEEP; extra approval needed |

- PlayerAttack.ThrowSkill은 skill.range 안에서 조준 대상을 고른다 (`PlayerAttack.mlua:277-323`).
- MonsterAttack.CastSkill은 skill.range×boss_skill_range_multiplier로 대상을 탐색한다 (`MonsterAttack.mlua:383-402,469-485`).
- 양쪽 ResolveThrowHit은 projectile_hit_radius를 착탄점 CircleShape에 쓴다 (`PlayerAttack.mlua:483-504`, `MonsterAttack.mlua:506-529`).
- 원래 actual_effect 문구의 큰 반경 숫자는 확정 기획/데이터 값으로 보존했으며 현행 착탄 피해 반경으로 단정하지 않는다.
