-- Transient Maker-only QA navigation, not a game-content mutation.
if not Environment:IsMakerPlay() or not _GameData.RogueRunActive then
    log_warning("[SkillQA] RUN_REQUIRED") return
end
local players = _UserService.UserEntities.Values
if players == nil or #players ~= 1 then log_warning("[SkillQA] SOLO_REQUIRED") return end
local player = players[1]
if not isvalid(player) or not _GameData:IsRunParticipant(player.PlayerComponent.UserId) then
    log_warning("[SkillQA] RUN_PARTICIPANT_REQUIRED") return
end
local roomId = _GameData.RogueMainPath[2]
local room = roomId and _GameData:GetRoom(roomId) or nil
if room == nil then log_warning("[SkillQA] NO_GRAPH_COMBAT_ROOM") return end
log("[SkillQA] MOVE_TO_COMBAT_MAP room=" .. roomId .. " map=" .. room.map_name)
_TeleportService:TeleportToMapPosition(player, Vector3(0, 0, 0), room.map_name)
