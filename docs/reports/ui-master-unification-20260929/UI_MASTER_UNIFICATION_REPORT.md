# Player-facing UI master style unification

Date: 2026-09-29 (KST). Project: `D:/maplestory_levup`.

## Scope and implementation

The approved Monster Collection remains the visual master. Its layout, colors,
four-column grid, right detail, and three companion slots were not redesigned.
The double inset outline on the collection window was removed. The outer cell
alone owns its perimeter; selection changes that outline's color without
changing its width. The portrait wells, companion portraits, badges and unique
skill icon now have space between their own edge and the parent edge.

The same pale blue-gray body, thin charcoal-gray outer frame, light recessed
slot, cyan selection outline, compact blue/green beveled actions, and dark HUD
variant were applied to the active Lobby, Adventure, Party, Shop, Run HUD,
Run Skill, Run Upgrade, Result, acquisition offer, generic popup, and toast.
Window layouts, click bindings and game logic were not changed. Existing
Monster Collection assets, skill icons and monster portraits were retained.

Static UIBuilder ownership checks: 101 monster cells, three companion slots,
five main window frames, and five battle skill slots all met the expected
single-outline widths. `git diff --check` passed. This is not a pixel-diff
proof for every possible dynamic state.

## Maker screenshots (844 × 475)

| File | Screen | How displayed |
|---|---|---|
| `01_lobby.png` | Lobby | Play start, natural screen |
| `02_monster.png` | Monster Collection | Existing controller `SetOpen(true)` |
| `03_adventure.png` | Adventure | Existing controller `ShowLobbyAreas()` |
| `04_party.png` | Solo Party window | Existing controller `SetPartyWindowOpen(true)` |
| `05_shop.png` | Shop | Existing controller `SetShopOpen(true)` |
| `06_run_hud.png` | Run HUD | Run started through existing `StartSelectedRun()` handler, not a physical UI click |
| `07_run_skill.png` | Filled Run Skill window | Maker-only world drop, real `E` pickup, 5-second supply, then existing controller `SetOpen(true)` |
| `08_run_upgrade.png` | Empty Run Upgrade window | Existing controller `SetRunUpgradeWindowOpen(true)` |
| `09_skill_drop.png` | World drop | Maker-only `DebugSpawnRequest`, not a natural kill |
| `10_boss.png` | Boss HUD and Faust | Maker-only move to final room; real boss entity and damage rendered |
| `11_result.png` | CLEAR result component | Client-only UI-state preview after the boss encounter; **not** proof of natural result presentation |

Border checks: `border_monster_normal_selected.png`,
`border_companion.png`, `border_skill.png`, and `border_run_slots.png`.
The first three show distinct Monster Collection selections and the last shows
filled combat slots. `07_run_skill_empty.png` preserves the compact empty state,
while `07_run_skill_filled_before.png` shows the filled state before its battle
slot visual cleanup. Normal/selected collection cells and companion badges
show no visually doubled border at this resolution; the cyan selected outline
does not increase its configured width.

## Runtime and limitations

Maker workspace refresh and Play returned `ok`. The Build Console contained
**0 Error**. Its four Warning entries were dated 21:36 KST (RunChest
InteractionComponent ×2, Mano InputSpeed, Bowmaster AvatarAttackPlayRate);
none were new to this final refresh.

In the final post-refresh Play session (from approximately 23:37 KST), the
normal Console contained **0 new Runtime Error** and 73 Warning entries.
They concerned existing room-bound/portal behavior while the Instance rooms
and town loaded, not these UI components. The historical console is not being represented as
error-free: it still includes an older, unrelated MakerScript Error from
21:42 KST.

The filled five-slot SkillBar and full Run Skill window were exercised with a
Maker-only drop and actual `E` pickup; no natural monster kill was used for
that capture. The final Run was explicitly abandoned after capture. Visual
states not exercised in this session: a joined four-player Party window, a
naturally presented CLEAR/FAIL Result, and generic PopupGroup/ToastGroup
transitions. Their components were updated with UIBuilder, but those specific
runtime states remain unverified. The game was not committed or pushed.

## Modified in this task

- `ui/EquipWindow.ui`, `ui/AreaSelect.ui`, `ui/PlayerHud.ui`,
  `ui/SkillBar.ui`, `ui/RoomProgress.ui`, `ui/GateNotice.ui`,
  `ui/PopupGroup.ui`, `ui/ToastGroup.ui`
- `RootDesk/MyDesk/UI/EquipPanel.mlua`, `AreaSelectPanel.mlua`,
  `PlayerHud.mlua`, `SkillBar.mlua`
- UIBuilder scripts and captured screenshots in this report directory

Pre-existing unrelated working-tree changes were preserved. No skill, combat,
party, shop-reward, save, map, portal or boss logic was edited for this task.
