# INPUT V2.2 CHANGELOG

- Source: immutable 19 V2.1 ZIPs. Area 00, prior INPUT/OUTPUT, game data/code unchanged.
- Stumpy: removed current CAST generation contract; PROJECTILE+ICON only. 4×0.08=0.32s non-loop frame contract fits the unchanged 0.35s projectile lifetime.
- 12 monster projectile skills: separated data range, player/monster targeting_range, impact_radius=0.8, impact_delay=0.35, max_targets.
- Existing 11 non-Stumpy projectile assets remain KEEP and outside required art scope.
- 15 EXCLUDE_STYLE info files: current classification moved to one top section; previous values retained only as history.
- 35 passive specs/maps: REFERENCE_VFX preview-only, runtime_use=false; no CAST delivery instruction.
- 19 OUTPUT examples: labeled/overview previews mandatory; separate contact sheet optional.
- AREA 20 DEF passive and six dash execution warnings recorded without game changes.
- Status axes split: PACKAGE_VALIDATION / GENERATION_READY / RUNTIME_VALIDATION / ART_APPROVAL.
