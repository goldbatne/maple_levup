-- Maker-only smoke test on the visible edit map. No persistent data is written.
if not Environment:IsMakerPlay() then return end
local users = _UserService.UserEntities.Values
local p = users and users[1] or nil
if not isvalid(p) or p.CurrentMap == nil or p.CurrentMap.Name ~= "map01" then
    log_warning("[SkillVFXQA] STAGE_BLOCKED no visible map01 player") return
end
local db = p:GetComponent("script.PlayerDBManager")
local slots = p:GetComponent("script.PlayerSkillSlots")
local attack = p:GetComponent("script.PlayerAttack")
local hit = p:GetComponent("script.PlayerHit")
local sp = p.CurrentMap:GetComponent("script.RoomSpawner")
if db == nil or slots == nil or attack == nil then
    log_warning("[SkillVFXQA] STAGE_BLOCKED component missing") return
end
local g = _GameData
local userId = p.PlayerComponent.UserId
local save = {
    active = g.RogueRunActive, complete = g.RogueRunComplete,
    failed = g.RogueRunFailed, result = g.RogueRunResult,
    participantIds = g.RogueParticipantIds, alive = g.RogueAliveParticipants,
    slot = slots.RandomSlots[1], mode = slots.RandomModeActive,
    slotRun = slots.RogueliteRunActive, writeBlocked = db.StorageWriteBlocked,
    hp = p.PlayerComponent.Hp, maxHp = p.PlayerComponent.MaxHp,
}
local parked = {}
if sp ~= nil then
    for _, enemy in ipairs(sp.spawned) do
        if isvalid(enemy) and enemy.AIChaseComponent ~= nil then
            parked[#parked + 1] = {entity = enemy, enabled = enemy.AIChaseComponent.Enable}
        end
    end
end
local ok, err = pcall(function()
    db.StorageWriteBlocked = true
    g.RogueRunActive = true
    g.RogueRunComplete = false
    g.RogueRunFailed = false
    g.RogueRunResult = "ACTIVE"
    g.RogueParticipantIds = {userId}
    g.RogueAliveParticipants = {[userId] = true}
    slots.RandomModeActive = true
    slots.RogueliteRunActive = true
    p.PlayerComponent.MaxHp = 1000000
    p.PlayerComponent.Hp = 1000000
    if hit ~= nil then hit.LastHitTime = -999 end
    for _, enemy in ipairs(parked) do enemy.entity.AIChaseComponent.Enable = false end
    local skillId = "s_mon_memory_monk_trainee"
    local casts = 0
    for i = 1, 80 do
        slots.RandomSlots[1] = skillId
        if attack:UseSkill(1, 1, 0) then casts = casts + 1 end
        if i == 1 then log("[SkillVFXQA] STAGE_BEGIN " .. skillId) end
        wait(0.35)
    end
    log("[SkillVFXQA] STAGE_CASTS " .. skillId .. " " .. tostring(casts))
end)
slots:StopRandomSkillSupply()
slots.RandomSlots[1] = save.slot
slots.RandomModeActive = save.mode
slots.RogueliteRunActive = save.slotRun
p.PlayerComponent.MaxHp = save.maxHp
p.PlayerComponent.Hp = save.hp
for _, enemy in ipairs(parked) do
    if isvalid(enemy.entity) then enemy.entity.AIChaseComponent.Enable = enemy.enabled end
end
g.RogueRunActive = save.active
g.RogueRunComplete = save.complete
g.RogueRunFailed = save.failed
g.RogueRunResult = save.result
g.RogueParticipantIds = save.participantIds
g.RogueAliveParticipants = save.alive
db.StorageWriteBlocked = save.writeBlocked
if not ok then log_warning("[SkillVFXQA] STAGE_ERROR " .. tostring(err)) end
log("[SkillVFXQA] STAGE_DONE ok=" .. tostring(ok))
