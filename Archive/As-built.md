# Maple Levup — As-built log

> Running record of the world's implementation. AI/handoff reference, not a user-facing planning contract.

## Current state (by system)

| System | Built | Where (key files) | Notes / gotchas |
|---|---|---|---|
| Map | 160 RectTile maps | `map/` | Shared, non-instance structure; M1 does not edit maps |
| Combat | Feature-flagged nearest-target basic attack + active monster skills | `PlayerAttack.mlua`, `MonsterAttack.mlua`, `RoomMonster.mlua` | Flag off restores legacy AoE basic attack/contact-box monster attack |
| Collection | Permanent monster-skill ownership and stack count | `Progress/PlayerCollection.mlua` | `OwnedSkills` is the new random pool source |
| Skill slots | Legacy MonsterSlots + Phase 1 server runtime hand | `Progress/PlayerSkillSlots.mlua` | 1–5 owned actives direct; 6+ five random slots; runtime hand is not saved |
| Skill UI | Five-button hotbar with random empty-slot state | `UI/SkillBar.mlua`, `ui/SkillBar.ui` | UI hierarchy unchanged; existing icons/VFX/cooldown retained |
| Save | Permanent/run split | `Save/PlayerDBManager.mlua` | M1 does not migrate schema; runtime random hand is ephemeral |

## Standing issues & handoff rules

| Issue / rule | Workaround / rule | Count | First → last seen |
|---|---|---:|---|
| Maker runtime evidence unavailable from this task | Keep runtime-dependent Phase items 🟡 until actual refresh/build/play/log verification | 1 | 09-15 → 09-15 |

## Log

### 2026-09-15 Seed — surveyed on toolkit adoption

Existing project has 101 captureable monsters, 112 skill rows, 160 RectTile maps, permanent collection/save, shared-field combat, equipment, boss, rebirth/tier/stat/area-gate systems. M1 is deliberately limited to a feature-flagged combat-loop prototype; later systems remain unchanged.

### 2026-09-15 M1 Phase 1 — static implementation complete, runtime pending

Added data-backed feature flag and settings, nearest-live-monster single basic attack, separate monster detection/attack range, server-owned random skill hand, successful-use consumption, five-second single-slot supply, and fixed random empty-slot UI. Existing skill rows, cooldowns, VFX, permanent collection/save schema, maps, jobs, rebirth, stats, and area locks remain unchanged. Static checks passed; Maker build/play/log evidence is not available in this task, so M1 remains at user-test pending rather than complete.
