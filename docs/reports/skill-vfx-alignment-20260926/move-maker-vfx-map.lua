-- Visual QA only: move within the active Run to a room's configured portal point.
if not Environment:IsMakerPlay() or not _GameData.RogueRunActive then
    log_warning("[SkillVFXQA] MOVE BLOCKED NO_RUN") return
end
local players = _UserService.UserEntities.Values
if players == nil or #players ~= 1 then
    log_warning("[SkillVFXQA] MOVE BLOCKED SOLO_ONLY") return
end
local player = players[1]
if not isvalid(player) or not _GameData:IsRunParticipant(player.PlayerComponent.UserId) then
    log_warning("[SkillVFXQA] MOVE BLOCKED PARTICIPANT") return
end
local roomId = _GameData.RogueMainPath[2]
local room = roomId and _GameData:GetRoom(roomId) or nil
if room == nil then log_warning("[SkillVFXQA] MOVE BLOCKED NO_ROOM") return end
local x, y = tonumber(room.portal_x) or 0, tonumber(room.portal_y) or 0
_TeleportService:TeleportToMapPosition(player, Vector3(x, y, 0), room.map_name)
log("[SkillVFXQA] MOVE_TO_ROOM map=" .. room.map_name .. " x=" .. tostring(x)
    .. " y=" .. tostring(y))
