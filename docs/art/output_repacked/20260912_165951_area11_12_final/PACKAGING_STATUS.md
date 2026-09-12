# AREA 11·12 packaging status — INCOMPLETE

## Completed: AREA 12

- ZIP: `AREA_12_IMAGES_OUTPUT_V2_4_FINAL_CANDIDATE.zip`
- All 45 role PNG files preserve the selected original ZIP bytes (SHA256 equality).
- INPUT V2.4 canonical paths, file-level OUTPUT_MANIFEST, five RESULT_INFO documents, five labeled previews and the Area overview were rebuilt.
- The new ZIP was checked for CRC, unsafe/duplicate paths, then extracted under `verification_extract/AREA_12_IMAGES_OUTPUT` and checked for actual files, RGBA canvas, SHA256, role/frame counts and required documents.
- Updated preview was opened for visual inspection; text and frame rows are separate, with all twelve Timer frames included.
- User art approval: PENDING. Runtime validation: NOT_RUN.

## Blocked: AREA 11 actual transparency

The built-in image_gen tool produced the requested crown-block shape correction: eyes, muzzle and pink monster torso were removed from the 2x2 projectile sheet. CAST and ICON were used only as style references and remain unchanged.

However, two successful image-edit calls returned RGB images with a painted checkerboard instead of an alpha channel. A local-reference retry also failed before generation. These are NOT valid transparent delivery PNGs and were NOT inserted into a corrected OUTPUT ZIP.

An explicit user question is pending: may Python perform technical background/alpha extraction on ONLY the four tool-edited projectile frames, without drawing new shapes or changing other art? No such extraction has been performed while awaiting that answer. No CLI fallback or placeholder geometry was used.

## Intermediate index and preservation

`CANDIDATE_ZIP_INDEX.csv` includes 19 Area paths and SHA256 values. AREA11 is explicitly `BLOCKED_ALPHA_NO_CORRECTED_PACKAGE` and points to the previously selected original for traceability only; it is NOT a final corrected candidate. The other 17 completed REPACK ZIPs remain unchanged and AREA12 points to the new validated package.

`PROTECTED_ARCHIVE_HASH_CHECK.csv` confirms all 19 selected INPUT and 19 previously selected OUTPUT archives remain unchanged. `PNG_BYTE_PRESERVATION.csv` currently contains the completed AREA12 45 rows; AREA11 rows will be added only after corrected delivery art exists and is validated.

## Continue after alpha permission

1. Process only the actual tool-edited 2x2 projectile sheet into real RGBA, preserve art and validate edge quality on multiple backgrounds.
2. Export F00..F03 to fixed 384×384 full canvases, 0.08s/frame / 0.32s non-loop; maintain normalized (0.5,0.5) pivot and direction-neutral local animation without baked translation or whole-canvas rotation.
3. Inspect enlarged before/after against the cached official MSW resource and approved V2.4 specification; reject artifacts or failed transparency.
4. Build AREA11 with `package_final.py area_11`, using four validated files from `corrected_projectile/`. All other AREA11 role PNGs must preserve bytes.
5. Re-extract/validate the new ZIP, inspect the updated Area11 overview, run `final_index.py`, and produce final change/revalidation reports and comparisons.

No game data/code, RUID, AnimationClip, Maker state, or existing archive was modified. SkillTable registration, DEF passive and dash attachment remain separate runtime questions. The corrected artwork still needs final user approval even after technical packaging succeeds.
