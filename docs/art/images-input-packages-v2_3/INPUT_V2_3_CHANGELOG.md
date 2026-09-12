# INPUT V2.3 CHANGELOG

- V2.2 19 packages remain untouched; V2.3 is a separate revision.
- Enumerated 594 role rows: 99 monster/skill pairs × 6 standard visual roles.
- Expanded 11 prior PROJECTILE KEEP items to NEW_ART. Stumpy remains PROJECTILE+ICON without invented CAST.
- Every actual projectile uses a separate 4×0.08=0.32s non-loop file set within unchanged 0.35s life.
- Preserved Area 00 approved reuse for exactly three pairs: s_mon_snail_dew_trail, s_mon_blue_snail, s_mon_slime.
- Passive ICON and REFERENCE_VFX remain production scope; REFERENCE runtime_use=false.
- Dedicated HIT/PERSISTENT visual roles remain NO_RUNTIME_ROLE because current code has no corresponding asset path.
- Multiple CAST layers use COMPOSITE_BAKED_ONE_CLIP, retaining the source layer timing/offset/drift recipe in ASSET_BINDING_PLAN.
- Game values, actual behavior, source monster images, style library, OUTPUT, resources, and game files were not changed.
