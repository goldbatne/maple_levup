-- End only this isolated Maker QA run. No live account data is used.
if not Environment:IsMakerPlay() or not _GameData.RogueRunActive then
    log_warning("[SkillQA] NO_ACTIVE_MAKER_RUN") return
end
local players = _UserService.UserEntities.Values
if players == nil or #players ~= 1 then
    log_warning("[SkillQA] SOLO_REQUIRED_FOR_CLEANUP") return
end
local player = players[1]
local db = player:GetComponent("script.PlayerDBManager")
if db == nil or db.RogueStorageMode ~= true
    or string.sub(tostring(db.KeyRogue), 1, 10) ~= "MakerTest_" then
    log_warning("[SkillQA] TEST_STORAGE_REQUIRED_FOR_CLEANUP") return
end
local userId = player.PlayerComponent.UserId
log("[SkillQA] ABANDON_TEST_RUN user=" .. tostring(userId))
local ok = _GameData:AbandonRogueliteParticipant(userId)
log("[SkillQA] ABANDON_TEST_RUN_RESULT=" .. tostring(ok)
    .. " active=" .. tostring(_GameData.RogueRunActive))
