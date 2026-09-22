-- MakerTest SOLO only: QA positions the player at actual connected portals.
-- Calls real RoomPortal.TryPass, does not change graph/objective/monster HP.
-- Not proof of human-input traversal of all terrain. Actual basic attack kills boss.
if not Environment:IsMakerPlay() then return end
local players = {}
for _, user in ipairs(_UserService.UserEntities.Values) do players[#players+1] = user end
if #players ~= 1 then log_warning('[PRQA] TRAVERSE_BLOCKED SOLO_ONLY') return end
local p = players[1]
if not isvalid(p) or not _GameData.RogueRunActive then return end
local db = p:GetComponent("script.PlayerDBManager")
if db == nil or string.sub(tostring(db.KeyRogue),1,10) ~= "MakerTest_" then
    log_warning('[PRQA] TRAVERSE_BLOCKED NON_TEST_STORAGE') return
end
local path = _GameData.RogueMainPath
local area = _GameData.RogueAreaId
log("[PRQA] TRAVERSE_BEGIN area=" .. area .. " seed=" .. _GameData.RogueSeed .. " nodes=" .. #path)
for index = 2, #path do
    if not isvalid(p) or not _GameData.RogueRunActive or _GameData.RogueRunFailed then
        log("[PRQA] TRAVERSE_INTERRUPTED area=" .. area) return
    end
    local current = _GameData:GetRoomByMapName(p.CurrentMap.Name)
    local target = path[index]
    if current.id ~= path[index-1] then log("[PRQA] TRAVERSE_FAIL unexpected_source=" .. current.id) return end
    local found = false
    for _,entity in ipairs(p.CurrentMap.Children:ToTable()) do
        local portal = entity:GetComponent("script.RoomPortal")
        if portal ~= nil and _GameData:GetRunRoomConnection(current.id, portal.direction) == target then
            local pos = entity.TransformComponent.WorldPosition
            p.KinematicbodyComponent:SetWorldPosition(Vector2(pos.x,pos.y))
            portal:TryPass(p)
            found = true
            break
        end
    end
    if not found then log("[PRQA] TRAVERSE_FAIL missing_portal=" .. current.id .. ">" .. target) return end
    wait(2)
    if not isvalid(p) then log("[PRQA] TRAVERSE_FAIL player_missing") return end
    local arrived = _GameData:GetRoomByMapName(p.CurrentMap.Name)
    if arrived.id ~= target then log("[PRQA] TRAVERSE_FAIL arrival=" .. arrived.id .. " expected=" .. target) return end
    log("[PRQA] PORTAL_VERIFIED area=" .. area .. " from=" .. current.id .. " to=" .. target)
end
wait(1)
local sp = p.CurrentMap:GetComponent("script.RoomSpawner")
local boss = nil
for _,entity in ipairs(sp.spawned) do
    if isvalid(entity) then
        local monster = entity:GetComponent("script.RoomMonster")
        if monster ~= nil and monster.MonsterId == _GameData.RogueBossMonsterId then boss=entity break end
    end
end
if not isvalid(boss) then log("[PRQA] BOSS_FAIL not_spawned area=" .. area) return end
local monster = boss:GetComponent("script.RoomMonster")
local deadline = _UtilLogic.ElapsedSeconds+90
log("[PRQA] BOSS_BEGIN area=" .. area .. " id=" .. monster.MonsterId .. " hp=" .. monster.Hp)
while isvalid(p) and isvalid(boss) and not monster.IsDead and _UtilLogic.ElapsedSeconds < deadline do
    if p.PlayerComponent:IsDead() then log("[PRQA] BOSS_FAIL player_dead area=" .. area) return end
    local pos=boss.TransformComponent.WorldPosition
    -- Stay on the arena-facing side; a fixed left offset can re-enter an edge portal.
    local inwardX = pos.x < 0 and 1 or -1
    p.KinematicbodyComponent:SetWorldPosition(Vector2(pos.x+inwardX,pos.y))
    wait(0.5)
end
log("[PRQA] BOSS_END area=" .. area .. " result=" .. _GameData.RogueRunResult .. " objective=" .. tostring(_GameData.RogueObjectiveComplete))
