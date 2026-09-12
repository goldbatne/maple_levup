# Monster Skill Art INPUT↔OUTPUT Audit Rules

## Scope and safety

- Audit root: `D:/maplestory_levup/docs/art/output_audit`.
- Incoming archives: `D:/maplestory_levup/docs/art/output`.
- Per-run extraction workspace: `D:/maplestory_levup/docs/art/output_audit_work/<run_id>`.
- Inspect only OUTPUT ZIP files present in `output` when an audit is explicitly requested. Placing a file there does not start monitoring or an automatic audit.
- Never modify, move, rename, or delete INPUT/OUTPUT archives. Never generate or edit art, change game data/code, upload resources, create AnimationClips, connect RUIDs, run Maker, or import assets during this audit.
- Area 06 is a reserved gap and is not expected.

## Frozen baselines

- Area 01–20 uses the 19 approved INPUT V2.4 ZIPs under `docs/art/images-input-packages-v2_4`.
- Area 00 uses its approved INPUT, approved OUTPUT original archive, resource map, and import/validation records under their existing `docs/art` locations.
- Baselines are selected by internal revision and approval evidence, never by modified time or a download suffix.
- `BASELINE_INDEX.csv` records area, revision, absolute path, and SHA-256. A later run must not silently substitute a different file. Conflicting candidates remain unresolved.

## Output discovery

- Read Area ID from the internal `OUTPUT_MANIFEST`; cross-check the ZIP filename and root directory.
- Missing Areas are `NOT_PROVIDED`, not production failures.
- Multiple different OUTPUT archives for one Area are `VERSION_CONFLICT`; do not choose one automatically, and continue auditing other Areas.
- Missing matching INPUT is `MISSING_INPUT`.
- Extract only after validating CRC, duplicate entries, absolute paths, traversal (`..`), and unsafe link entries.

## Structural and file checks

- Use `PACKAGE_REVISION_V2_4`, `AREA_MANIFEST`, `FULL_ART_SCOPE`, `OUTPUT_REQUIREMENTS`, `ASSET_BINDING_PLAN`, every `GENERATION_SPEC`/`RUNTIME_ROLE_MAP`, and the naming/format specifications as authority.
- Preserve the distinction among `NEW_ART`, `AREA00_APPROVED_REUSE`, and `NO_RUNTIME_ROLE`.
- Check Area, monster/skill IDs, names, type, role, required files, manifests, `RESULT_INFO`, and mandatory previews.
- Validate each role's own frame count, canvas, names, and continuous F00… numbering. Do not impose a universal 8- or 12-frame rule.
- VFX roles are `CAST_VFX`, `PROJECTILE`, and `REFERENCE_VFX`; `ICON` is static. Do not mix or invent absent roles.
- PNG checks include actual RGBA, transparent background pixels, nonblank content, canvas, manifest hash, edge contact, likely rectangular background, and suspicious fragments. RGBA alone is not an alpha-background pass. Edge contact alone is only a clipping suspicion unless corroborated.
- For Area 00 reuse, compare actual bytes/hashes with the approved files. Keep Preview/reference files separate from import originals.
- Cross-check `OUTPUT_MANIFEST`/`RESULT_INFO` claims against actual files. A self-declared PASS is evidence, not authority.

## Visual intent checks

- Inspect actual ICON/VFX frames against the INPUT `MONSTER_IMAGE` and `GENERATION_SPEC`; do not rely only on OUTPUT previews.
- Check monster/Area identity, required motifs and motion, CAST versus PROJECTILE role, VFX↔ICON coherence, passive-reference presentation, and obvious finish/material gaps against Area 00.
- Allowed motifs such as hands, dolls, horns, masks, or equipment fragments are not errors merely because they differ from the monster body.
- Do not force Area 00's exact shape or low-level scale onto unrelated skills.
- Separate objective mismatch from taste. If actual visual inspection was not performed, record `NOT_CHECKED`. Never write `USER_APPROVED` without the user's approval.

## Judgments and actions

- File/spec status: `PASS`, `FAIL`, `NOT_CHECKED`.
- Visual status: `NO_OBVIOUS_ISSUE`, `ISSUE_FOUND`, `NEEDS_USER_REVIEW`, `NOT_CHECKED`.
- Actions: `REPACK`, `REEXTRACT`, `REGENERATE`, `INPUT_CONFLICT`, `USER_REVIEW`.
- Naming/manifest defects use `REPACK`; extraction defects use `REEXTRACT`; only original-art defects use `REGENERATE`.
- Scope actions to the affected monster/role, not an entire Area when avoidable.

## Run records

- Store each run under `output_audit/runs/<run_id>` with `AUDIT_SUMMARY.md`, `AUDIT_SUMMARY.csv`, `AREA_STATUS.csv`, `ACTION_ITEMS.csv`, and evidence images for findings.
- Evidence comparisons mechanically compose INPUT monster image, relevant specification text, and actual OUTPUT assets. They are not new art.
- `LATEST_REPORT.md` points to the newest completed report.
- Reuse prior checks only when audit rules, baseline index, Area 00 references, and the specific INPUT/OUTPUT archive hashes are unchanged. Never promote a previous unknown to PASS automatically.

