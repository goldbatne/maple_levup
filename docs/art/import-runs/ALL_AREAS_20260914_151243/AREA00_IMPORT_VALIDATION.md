# AREA 00 import validation

## Status

- Import: PASS
- Runtime playback: NOT_CHECKED
- Follow-up: validate playback in Maker, then refine only observed failures

## Applied resources

- Existing sprite RUID data replaced: 23 frames
- Dew Trail: F00-F07 (8)
- Blue Shell: F03-F05 (3)
- Mano Rainbow Wave: F00-F11 (12)
- Unchanged icons and unchanged VFX frames were not re-uploaded.

## Import checks

- All 23 update requests completed successfully.
- All 23 RUIDs resolve as `sprite` after update.
- Every updated sprite kept `pivot_x=0.5`, `pivot_y=0.5`.
- The five AREA 00 AnimationClip RUIDs still resolve as `animationclip`.
- SkillTable RUID values were not changed.
- Candidate and source packages were not modified.

## Runtime checks still required

- Frame playback order and interval
- In-game scale and offset
- Facing-direction behavior
- Clipping against the actual game camera
- Visual connection with the existing skill icon

The current session has resource-storage access but no Maker play/log/screenshot tools. Runtime claims are therefore intentionally left as `NOT_CHECKED`.
