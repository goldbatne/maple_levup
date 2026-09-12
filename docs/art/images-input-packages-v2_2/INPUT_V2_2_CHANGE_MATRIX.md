# INPUT V2.2 change matrix

| Change | Before in V2.1 | Current V2.2 | Project evidence | Affected Area | Game change |
|---|---|---|---|---|---|
| Stumpy delivery role | Spec/runtime map said CAST_VFX 12f and projectile KEEP while binding plan said PROJECTILE replace | PROJECTILE 4f + ICON, target projectile_ruid; no CAST delivery | SkillTable baseline row s_mon_stumpy; SkillEffect.mlua:149-194; SkillProjectile.mlua:39-81; SkillProjectile.model:20-68 | 02 | none |
| Stumpy playback period | 12×0.08=0.96s vs 0.35s entity life | non-loop 4×0.08=0.32s complete playback, 0.03s margin | GameBalance.csv:21; SkillProjectile.mlua:39-59; model has no playback speed/loop property | 02 | none |
| Projectile range semantics | Five actual-effect sentences could be read as range-sized impact radius | immutable planning text retained; runtime fields split into targeting_range / impact_radius=0.8 / impact_delay=0.35 / max_targets | PlayerAttack.mlua:277-323,483-504; MonsterAttack.mlua:383-402,450-529; GameBalance.csv:21,24 | 02,03,08,10,11,14,15,17,18 | none |
| Existing projectile scope | ambiguous optional redraw wording | Stumpy replace only; other 11 projectile_ruid rows KEEP pending approval | SkillTable baseline projectile_ruid fields; ASSET_BINDING_PLAN_V2_2.csv | 03,08,10,11,14,15,17,18 | none |
| EXCLUDE_STYLE info | old UNKNOWN/LEGACY and layered-VFX header coexisted with V2.1 synchronized block | one `현행 분류 — V2.2`; old values history-only | STYLE_INDEX.csv + 183 preview classification; 15 EXCLUDE_STYLE rows | all 19 | none |
| Preview obligation | tree example called PREVIEW optional while lower contract required labeled/overview | labeled_preview + AREA_OVERVIEW mandatory; separate contact sheet optional | OUTPUT_NAMING_SPEC.md / OUTPUT_FORMAT_SPEC.md | all 19 | none |
| Passive VFX role | runtime-none statement coexisted with generic CAST one-shot template | REFERENCE_VFX preview-only, runtime_use=false; ICON UI role | GameData.mlua passive load; PlayerStats.mlua:527-576; no passive PlayCast call | all 19 / 35 placements | none |
| Delayed CAST position | attachment timing was underspecified | caster position sampled when delayed SpawnLayer executes; map entity drifts afterward | SkillEffect.mlua:55-60,83-117; SkillCastEffect.mlua | all Areas with delayed layers | none |
| Dash visual vs hit point | calculated destination could be mistaken for CAST origin | six-skill warning retained: calculated hit point vs server-observed caster position | PlayerAttack.mlua:386-479; SkillEffect.mlua:83-117; MonsterAttack.mlua:354-443 | 02,05,07,09,12,20 | none |
| Stone-mask DEF passive | package described DEF passive without exposing verifier/calculation conflict | generation READY; runtime UNRESOLVED | GameDataVerify.mlua:188-200; PlayerStats.mlua:527-576 | 20 | none |
| Status wording | READY/PASS could combine package, runtime, and art meanings | four axes recorded independently | PACKAGE_STATUS_V2_2.md; validator | all 19 | none |

The attached V2.1 crosscheck ZIP was treated as a candidate review. The project evidence column is the applied basis.
