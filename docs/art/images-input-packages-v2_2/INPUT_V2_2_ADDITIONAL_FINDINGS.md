# INPUT V2.2 ADDITIONAL FINDINGS

## Corrected input errors

- Stumpy had a PROJECTILE replacement plan but CAST output text; unified to PROJECTILE+ICON.
- Stumpy 12×0.08=0.96s could not complete within the 0.35s entity life. The image contract is now 4×0.08=0.32s non-loop, with no gameplay timing change.
- Five projectile descriptions treated skill.range as damage radius. The immutable planning text remains in `actual_effect`; current execution is separately recorded as targeting_range vs impact_radius.
- EXCLUDE_STYLE, Preview, and passive REFERENCE_VFX instructions were duplicated/conflicting; current instructions are now single-source.

## Runtime/design conflicts left unchanged

- `s_mon_mutant_stone_mask` passive_stat=DEF is rejected by GameDataVerify and is not consumed by PlayerStats.GetCollectionBonus("DEF").
- Current Maker-registered SkillTable is unresolved; filename candidates are not treated as proof.
- Six dash skills retain calculated-hit-point vs CAST-caster-position warning.
- Eleven existing projectile artworks remain KEEP pending separate scope approval.

## Evidence distinction

- Attached crosscheck ZIP is a review input, not an instruction source. Every applied item was rechecked against the project files listed in the evidence table.
- RUNTIME_VALIDATION is NOT_RUN/UNRESOLVED because Maker execution was prohibited.
