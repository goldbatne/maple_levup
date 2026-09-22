# Legacy entry-point audit (in progress)

2026-09-21, original project `D:/maplestory_levup`. These findings are static, not exploited on an account. Existing UI hiding does not establish server-side rejection.

| Entry | Evidence | Impact | Status |
|---|---|---|---|
| `Inventory/PlayerInventory.mlua:UseItem` | Owner RPC forwards to inventory/Heal/RemoveItem without Run-mode guard | A retained legacy potion could heal and consume old inventory in the new mode | Confirmed missing guard; runtime negative test pending |
| `Inventory/PlayerInventory.mlua:SetEquipSlot` | Owner RPC can mutate `Equipped` and call avatar/save paths without Run-mode guard | Unused RPG equipment remains remotely mutable | Confirmed missing guard; runtime negative test pending |
| `Progress/PlayerCollection.mlua:RequestSetCompanion/RefreshCompanion/OnUpdate` | Tamed count check exists, Run-mode exclusion does not | Old selected companion can be spawned/follow in the new mode | Confirmed missing guard; runtime negative test pending |
| `Room/HeroNpc.mlua:SendToTrial` | Sends player to job map without Run-mode guard | Old trial navigation can bypass the Run graph | Confirmed missing guard; runtime negative test pending |
| `Room/TownGate.mlua:SendToArea` | Legacy direct-map teleport without Run-mode guard | Direct legacy entry can bypass InstanceRoom setup | Confirmed missing guard; runtime negative test pending |

Scope: reject these legacy operations in roguelite mode, preserve old data and legacy implementation. No new items, skills, growth, or companion features.

Separate investigation, not yet confirmed bugs: delayed attack callbacks across map/death; projectile wall intersection; dash endpoint versus wall stop. Do not infer intended wall-piercing behavior solely from current VFX.
