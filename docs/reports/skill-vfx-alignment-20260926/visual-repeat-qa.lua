-- Maker-only visual sampling. The caller substitutes the three identifiers below.
-- Repeats the real player/monster cast path so a short VFX can be captured.
-- Uses a visible Maker-only map01 session; transient Run authority is restored
-- before exit. Never writes collection/save data.
local tag = "[SkillVFXQA]"
local skillId = "__SKILL_ID__"
local monsterId = "__MONSTER_ID__"
local side = "__SIDE__"
local castLimit = __CAST_COUNT__
if not Environment:IsMakerPlay() then log_warning(tag .. " BLOCKED NOT_MAKER") return end
local players = _UserService.UserEntities.Values
if players == nil or #players ~= 1 then log_warning(tag .. " BLOCKED SOLO_ONLY") return end
local player = players[1]
local db = player:GetComponent("script.PlayerDBManager")
local attack = player:GetComponent("script.PlayerAttack")
local slots = player:GetComponent("script.PlayerSkillSlots")
local hit = player:GetComponent("script.PlayerHit")
local map = player.CurrentMap
local sp = map ~= nil and map:GetComponent("script.RoomSpawner") or nil
if map == nil or map.Name ~= "map01" then
    log_warning(tag .. " BLOCKED NOT_VISIBLE_MAP01") return
end
local skill = _GameData:GetSkill(skillId)
local monsterRecord = _GameData:GetMonster(monsterId)
if db == nil or attack == nil or slots == nil or hit == nil or sp == nil
    or skill == nil or monsterRecord == nil or monsterRecord.drop_skill_id ~= skillId
    then
    log_warning(tag .. " BLOCKED WRONG_TEST_CONTEXT id=" .. skillId) return
end
local g = _GameData
local userId = player.PlayerComponent.UserId
local originalRun = {
    active = g.RogueRunActive, complete = g.RogueRunComplete,
    failed = g.RogueRunFailed, result = g.RogueRunResult,
    ids = g.RogueParticipantIds, alive = g.RogueAliveParticipants,
}
local originalWriteBlocked = db.StorageWriteBlocked
local originalPosition = player.TransformComponent.WorldPosition
local originalHp, originalMaxHp = player.PlayerComponent.Hp, player.PlayerComponent.MaxHp
local originalSlot = slots.RandomSlots[1]
local originalMode, originalSlotRun = slots.RandomModeActive, slots.RogueliteRunActive
local originalNextBoost, originalNextBoostUntil = attack.NextAttackBoostRatio, attack.NextAttackBoostUntil
local originalBoost, originalBoostUntil = attack.OutgoingBoostRatio, attack.OutgoingBoostUntil
local originalShield, originalShieldUntil = hit.ShieldRatio, hit.ShieldUntil
local castGap = 0.4
if skill.skill_kind == "buff" or skill.skill_kind == "defense" then
    -- Self effects must be visibly attributable to the monster, not to the
    -- adjacent QA player who is not the recipient of the buff/shield.
    castGap = 2.5
elseif skill.dash_distance > 0 then
    castGap = math.min(2.5, skill.dash_distance * 0.8)
elseif skill.projectile_ruid ~= "" then
    castGap = math.min(2.0, math.max(0.4, skill.range * 0.5))
elseif skill.range > 0 then
    castGap = math.min(1.5, math.max(0.35, skill.range * 0.35))
end
local hadAuto = attack.autoAttackTimer ~= 0
local hadSpawner = sp.checkTimer ~= 0
local target, caster, casterAttack, casterMonster
local parked = {}
for _, e in ipairs(sp.spawned) do
    if isvalid(e) and e.KinematicbodyComponent ~= nil then
        local mon = e:GetComponent("script.RoomMonster")
        if mon ~= nil then
            parked[#parked + 1] = { e = e, pos = e.TransformComponent.WorldPosition,
                hp = mon.Hp, maxHp = mon.MaxHp,
                ai = e.AIChaseComponent ~= nil and e.AIChaseComponent.Enable or false }
            if target == nil then target = e end
        end
    end
end
if side == "PLAYER" and target == nil then log_warning(tag .. " BLOCKED NO_TARGET") return end
local castCount = 0
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
    player.PlayerComponent.MaxHp, player.PlayerComponent.Hp = 1000000, 1000000
    slots:StopRandomSkillSupply()
    if hadAuto then _TimerService:ClearTimer(attack.autoAttackTimer) attack.autoAttackTimer = 0 end
    if hadSpawner then _TimerService:ClearTimer(sp.checkTimer) sp.checkTimer = 0 end
    for i, entry in ipairs(parked) do
        local mon = entry.e:GetComponent("script.RoomMonster")
        mon.MaxHp, mon.Hp = 1000000, 1000000
        if entry.e.AIChaseComponent ~= nil then entry.e.AIChaseComponent.Enable = false end
        if entry.e.MovementComponent ~= nil then entry.e.MovementComponent:Stop() end
        local ma = entry.e:GetComponent("script.MonsterAttack")
        if ma ~= nil and ma.attackTimerId ~= 0 then _TimerService:ClearTimer(ma.attackTimerId) ma.attackTimerId = 0 end
        entry.e.KinematicbodyComponent:SetWorldPosition(Vector2(
            originalPosition.x - 7 - i * 0.2, originalPosition.y + 5))
    end
    if side == "PLAYER" then
        local distance = skill.dash_distance > 0 and skill.dash_distance or 1.0
        if skill.behavior == "DAMAGE_ZONE" or skill.behavior == "DELAYED_BLAST" then
            distance = math.min(skill.range > 0 and skill.range or 2, 4)
        end
        target.KinematicbodyComponent:SetWorldPosition(Vector2(
            originalPosition.x + distance, originalPosition.y))
    else
        caster = _SpawnService:SpawnByModelId(monsterRecord.model_id,
            "SkillVFXQA_" .. monsterId, Vector3(originalPosition.x - castGap,
                originalPosition.y, 0), map)
        if not isvalid(caster) then error("CASTER_MODEL_SPAWN_FAILED " .. monsterRecord.model_id) end
        casterMonster = caster:GetComponent("script.RoomMonster")
        casterAttack = caster:GetComponent("script.MonsterAttack")
        if casterMonster == nil or casterAttack == nil then error("CASTER_COMPONENT_MISSING") end
        casterMonster.MonsterId = monsterId
        if caster.AIChaseComponent ~= nil then caster.AIChaseComponent.Enable = false end
        if caster.MovementComponent ~= nil then caster.MovementComponent:Stop() end
        if casterAttack.attackTimerId ~= 0 then
            _TimerService:ClearTimer(casterAttack.attackTimerId)
            casterAttack.attackTimerId = 0
        end
        player.PlayerComponent.MaxHp, player.PlayerComponent.Hp = 1000000, 1000000
    end
    log(tag .. " BEGIN side=" .. side .. " id=" .. skillId .. " monster=" .. monsterId)
    for i = 1, castLimit do
        if not isvalid(player) or player.CurrentMap ~= map or not g.RogueRunActive then break end
        if side == "PLAYER" then
            player.KinematicbodyComponent:SetWorldPosition(Vector2(
                originalPosition.x, originalPosition.y))
            slots.RandomSlots[1] = skillId
            local fired = attack:UseSkill(1, 1, 0)
            if fired then castCount = castCount + 1 end
        else
            caster.KinematicbodyComponent:SetWorldPosition(Vector2(
                originalPosition.x - castGap, originalPosition.y))
            player.PlayerComponent.Hp = 1000000
            hit.LastHitTime = -999
            local fired = casterAttack:CastSkill(casterMonster, skill)
            if fired then castCount = castCount + 1 end
        end
        if i == 1 or i % 6 == 0 then
            log(tag .. " CAST side=" .. side .. " id=" .. skillId
                .. " iteration=" .. tostring(i) .. " accepted=" .. tostring(castCount))
        end
        wait(0.4)
    end
end)
slots:StopRandomSkillSupply()
slots.RandomSlots[1] = originalSlot
slots.RandomModeActive = originalMode
slots.RogueliteRunActive = originalSlotRun
db.StorageWriteBlocked = originalWriteBlocked
g.RogueRunActive = originalRun.active
g.RogueRunComplete = originalRun.complete
g.RogueRunFailed = originalRun.failed
g.RogueRunResult = originalRun.result
g.RogueParticipantIds = originalRun.ids
g.RogueAliveParticipants = originalRun.alive
if isvalid(player) then
    player.PlayerComponent.MaxHp, player.PlayerComponent.Hp = originalMaxHp, originalHp
    player.KinematicbodyComponent:SetWorldPosition(Vector2(originalPosition.x, originalPosition.y))
    attack.NextAttackBoostRatio, attack.NextAttackBoostUntil = originalNextBoost, originalNextBoostUntil
    attack.OutgoingBoostRatio, attack.OutgoingBoostUntil = originalBoost, originalBoostUntil
    hit.ShieldRatio, hit.ShieldUntil = originalShield, originalShieldUntil
    if hadAuto then attack:RestartAutoAttack() end
end
if isvalid(caster) then caster:Destroy() end
for _, entry in ipairs(parked) do
    if isvalid(entry.e) then
        local mon = entry.e:GetComponent("script.RoomMonster")
        if mon ~= nil and not mon.IsDead then mon.MaxHp, mon.Hp = entry.maxHp, entry.hp end
        entry.e.KinematicbodyComponent:SetWorldPosition(Vector2(entry.pos.x, entry.pos.y))
        if entry.e.AIChaseComponent ~= nil then entry.e.AIChaseComponent.Enable = entry.ai end
    end
end
if hadSpawner and sp.checkTimer == 0 then
    sp.checkTimer = _TimerService:SetTimerRepeat(function() sp:Refill() end,
        sp.RespawnCheckInterval)
end
if not ok then log_warning(tag .. " ERROR id=" .. skillId .. " " .. tostring(err)) end
log(tag .. " DONE side=" .. side .. " id=" .. skillId .. " accepted=" .. tostring(castCount)
    .. " qaOk=" .. tostring(ok))
