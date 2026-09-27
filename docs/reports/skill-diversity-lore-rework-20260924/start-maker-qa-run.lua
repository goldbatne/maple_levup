-- Transient Maker-only QA setup. No persistent account fields are changed.
if not Environment:IsMakerPlay() then log_warning("[SkillQA] NOT_MAKER") return end
local players = _UserService.UserEntities.Values
if players == nil or #players ~= 1 then log_warning("[SkillQA] SOLO_REQUIRED") return end
local player = players[1]
if not isvalid(player) or player.CurrentMap == nil then
    log_warning("[SkillQA] PLAYER_NOT_READY") return
end
log("[SkillQA] before map=" .. tostring(player.CurrentMap.Name)
    .. " user=" .. tostring(player.PlayerComponent.UserId))
if player.CurrentMap.Name ~= "maptown" then
    _TeleportService:TeleportToMapPosition(player, Vector3(0, 0, 0), "maptown")
    log("[SkillQA] TELEPORT_TO_TEST_LOBBY")
    return
end
local db = player:GetComponent("script.PlayerDBManager")
if db == nil or db.RogueStorageMode ~= true
    or string.sub(tostring(db.KeyRogue), 1, 10) ~= "MakerTest_" then
    log_warning("[SkillQA] TEST_STORAGE_REQUIRED") return
end
log("[SkillQA] START_REQUEST storage=" .. tostring(db.KeyRogue)
    .. " active=" .. tostring(_GameData.RogueRunActive))
_GameData:StartRogueliteAreaValidated("mega_01",
    { player.PlayerComponent.UserId }, 102401, "NORMAL")
log("[SkillQA] START_CALLED active=" .. tostring(_GameData.RogueRunActive))
