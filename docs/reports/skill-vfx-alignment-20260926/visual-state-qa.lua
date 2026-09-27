if not Environment:IsMakerPlay() then return end
local players = _UserService.UserEntities.Values
local player = players and players[1] or nil
if not isvalid(player) then log("[SkillVFXQA] STATE NO_PLAYER") return end
local map = player.CurrentMap
local sp = map and map:GetComponent("script.RoomSpawner") or nil
log("[SkillVFXQA] STATE map=" .. tostring(map and map.Name)
    .. " position=" .. tostring(player.TransformComponent.WorldPosition)
    .. " runActive=" .. tostring(_GameData.RogueRunActive)
    .. " spawner=" .. tostring(sp ~= nil)
    .. " monsters=" .. tostring(sp and #sp.spawned or -1))
