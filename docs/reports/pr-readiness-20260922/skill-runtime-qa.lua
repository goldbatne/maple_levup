-- Transient Maker server-instance QA, not production gameplay or natural acquisition.
-- Execute only in a dedicated SOLO QA Run. Do not use a real-account namespace.
-- Does not call OfferRunAbility, modify OwnedSkillPool, or call a save method.
-- Calls actual PlayerAttack.UseSkill twice for every currently eligible ability.
-- After completion/interruption, ABANDON this QA Run: damage/encounter telemetry
-- is intentionally not restored by inventing values. Then stop Maker Play.
-- Scope: cast/actual damage or shield state/token consumption/cooldown bypass.
-- NOT certified here: wall compatibility, VFX art/position, natural acquisition,
-- shield damage absorption, UI input, multiplayer, or any save/reconnect result.

local tag = "[MegaAudit66]"
if Environment:IsMakerPlay() == false then log_warning(tag .. " HARNESS_BLOCKED NOT_MAKER") return end
local players = {}
for _, u in ipairs(_UserService.UserEntities.Values) do players[#players + 1] = u end
if #players ~= 1 then log_warning(tag .. " HARNESS_BLOCKED SOLO_ONLY") return end
local p = players[1]
if not isvalid(p) or p.CurrentMap == nil or p.CurrentMap.Name == "maptown" then
    log_warning(tag .. " HARNESS_BLOCKED NO_QA_RUN") return
end
local slots = p:GetComponent("script.PlayerSkillSlots")
local attack = p:GetComponent("script.PlayerAttack")
local hit = p:GetComponent("script.PlayerHit")
local db = p:GetComponent("script.PlayerDBManager")
local map = p.CurrentMap
local sp = map:GetComponent("script.RoomSpawner")
if slots == nil or attack == nil or hit == nil or db == nil or sp == nil
    or not slots.RogueliteRunActive or not slots.RandomModeActive
    or not _GameData.RogueRunActive or not attack:CanActInCurrentRun()
    or p.KinematicbodyComponent == nil then
    log_warning(tag .. " HARNESS_BLOCKED INVALID_RUN_COMPONENTS") return
end
if db.RogueStorageMode ~= true or string.sub(tostring(db.KeyRogue), 1, 10) ~= "MakerTest_" then
    log_warning(tag .. " HARNESS_BLOCKED NON_TEST_STORAGE") return
end
local ids = _GameData:GetCapturableActiveSkillIds()
if #ids ~= 66 then log_warning(tag .. " HARNESS_BLOCKED COUNT=" .. tostring(#ids)) return end

local monsters = {}
for _, entity in ipairs(sp.spawned) do
    if isvalid(entity) then
        local mon = entity:GetComponent("script.RoomMonster")
        if mon ~= nil and not mon.IsDead and entity.KinematicbodyComponent ~= nil then
            local ma = entity:GetComponent("script.MonsterAttack")
            monsters[#monsters + 1] = {
                entity = entity, mon = mon, hp = mon.Hp, maxHp = mon.MaxHp,
                pos = entity.TransformComponent.WorldPosition,
                ai = entity.AIChaseComponent ~= nil and entity.AIChaseComponent.Enable or false,
                attackTimerWasRunning = ma ~= nil and ma.attackTimerId ~= 0
            }
        end
    end
end
if #monsters == 0 then log_warning(tag .. " HARNESS_BLOCKED NO_LIVE_TARGET") return end
local target = monsters[1].entity
local originalPos = p.TransformComponent.WorldPosition
local originalSlots = {}
for i = 1, slots:GetSkillSlotMax() do originalSlots[i] = slots.RandomSlots[i] end
local originalShield = hit.ShieldRatio
local originalShieldUntil = hit.ShieldUntil
local originalWriteBlocked = db.StorageWriteBlocked
local hadAutoAttack = attack.autoAttackTimer ~= 0
local hadSupply = slots.randomSupplyTimer ~= 0
local beganAt = _UtilLogic.ElapsedSeconds
local maxSeconds = 240
local passed, failed, reviewed = 0, 0, 0
local interrupted = false

local function stillValid()
    return isvalid(p) and isvalid(target) and p.CurrentMap == map
        and slots.RogueliteRunActive and _GameData.RogueRunActive
        and attack:CanActInCurrentRun()
        and _UtilLogic.ElapsedSeconds - beganAt < maxSeconds
end

local function totalHp()
    local value = 0
    for _, entry in ipairs(monsters) do
        if isvalid(entry.entity) and not entry.mon.IsDead then value = value + entry.mon.Hp end
    end
    return value
end

local function restoreTransientState()
    if isvalid(p) then
        slots:StopRandomSkillSupply()
        slots:ClearRandomSlots()
        if slots.RogueliteRunActive and p.CurrentMap == map then
            for i = 1, slots:GetSkillSlotMax() do slots.RandomSlots[i] = originalSlots[i] end
            p.KinematicbodyComponent:SetWorldPosition(Vector2(originalPos.x, originalPos.y))
            hit.ShieldRatio = originalShield
            hit.ShieldUntil = originalShieldUntil
            if hadAutoAttack then attack:RestartAutoAttack() end
            if hadSupply then slots:StartRandomSkillSupply() end
        end
        db.StorageWriteBlocked = originalWriteBlocked
    end
    for _, entry in ipairs(monsters) do
        if isvalid(entry.entity) and not entry.mon.IsDead then
            entry.mon.MaxHp = entry.maxHp
            entry.mon.Hp = entry.hp
            entry.entity.KinematicbodyComponent:SetWorldPosition(Vector2(entry.pos.x, entry.pos.y))
            if entry.entity.AIChaseComponent ~= nil then entry.entity.AIChaseComponent.Enable = entry.ai end
        end
    end
    -- Enemy attack repeat timer IDs cannot be restored as old timer handles.
    -- Therefore this dedicated QA encounter must be discarded via Abandon.
    log(tag .. " CLEANUP transient HP/positions/slots/shield restored where valid; ABANDON_QA_RUN_REQUIRED")
end

local ok, harnessError = pcall(function()
    db.StorageWriteBlocked = true
    slots:StopRandomSkillSupply()
    if hadAutoAttack then _TimerService:ClearTimer(attack.autoAttackTimer) attack.autoAttackTimer = 0 end
    for _, entry in ipairs(monsters) do
        entry.mon.MaxHp = 1000000
        entry.mon.Hp = 1000000
        if entry.entity.AIChaseComponent ~= nil then entry.entity.AIChaseComponent.Enable = false end
        if entry.entity.MovementComponent ~= nil then entry.entity.MovementComponent:Stop() end
        local ma = entry.entity:GetComponent("script.MonsterAttack")
        if ma ~= nil and ma.attackTimerId ~= 0 then _TimerService:ClearTimer(ma.attackTimerId) ma.attackTimerId = 0 end
    end
    log(tag .. " BEGIN count=" .. tostring(#ids) .. " mode=random_consumable saveWritesBlocked=true suppliedSlots=QA_ONLY")
    for _, id in ipairs(ids) do
        if not stillValid() then interrupted = true break end
        local skill = _GameData:GetSkill(id)
        if skill == nil then error("DATA_LOOKUP_FAILED " .. tostring(id)) end
        slots:StopRandomSkillSupply()
        slots:ClearRandomSlots()
        slots.RandomSlots[1] = id
        slots.RandomSlots[2] = id
        p.KinematicbodyComponent:SetWorldPosition(Vector2(originalPos.x, originalPos.y))
        local direction = originalPos.x > 0 and -1 or 1
        local distance = skill.dash_distance > 0 and skill.dash_distance or 1.1
        if skill.projectile_ruid ~= "" then distance = math.min(math.max(skill.range * 0.4, 0.3), 1.1) end
        target.KinematicbodyComponent:SetWorldPosition(Vector2(originalPos.x + direction * distance, originalPos.y))
        wait(0.12)
        if not stillValid() then interrupted = true break end
        local hpBefore = totalHp()
        local deadlineBefore = attack.SkillReadyAt[id]
        local castOneAt = _UtilLogic.ElapsedSeconds
        local callOne, usedOne = pcall(function() return attack:UseSkill(1, direction, 0) end)
        slots:StopRandomSkillSupply()
        local firstOnly = slots.RandomSlots[1] == nil and slots.RandomSlots[2] == id
        local callTwo, usedTwo = pcall(function() return attack:UseSkill(2, direction, 0) end)
        local castTwoAt = _UtilLogic.ElapsedSeconds
        slots:StopRandomSkillSupply()
        local bothConsumed = slots.RandomSlots[1] == nil and slots.RandomSlots[2] == nil
        local noOtherTokens = true
        for i = 3, slots:GetSkillSlotMax() do if slots.RandomSlots[i] ~= nil then noOtherTokens = false end end
        local unchangedCooldown = attack.SkillReadyAt[id] == deadlineBefore
        local delay = math.max(_GameData:GetBalance("projectile_seconds"), _GameData:GetBalance("skill_dash_seconds"), 0.2) + 0.3
        wait(math.min(delay, 1.5))
        if not stillValid() then interrupted = true break end
        local damage = hpBefore - totalHp()
        local effect = false
        local effectKind = "damage"
        if skill.skill_kind == "defense" then
            effectKind = "shield_state"
            effect = skill.effect_type == "shield" and math.abs(hit.ShieldRatio - math.min(skill.effect_value, 0.9)) < 0.0001
                and hit.ShieldUntil > castTwoAt
        else effect = damage > 0 end
        local rowPass = callOne and usedOne == true and callTwo and usedTwo == true
            and firstOnly and bothConsumed and noOtherTokens and unchangedCooldown and effect
        reviewed = reviewed + 1
        if rowPass then passed = passed + 1 else failed = failed + 1 end
        log(tag .. " ROW id=" .. id .. " status=" .. (rowPass and "PASS_OBSERVED" or "FAIL_OR_SETUP_REVIEW")
            .. " first=" .. tostring(callOne and usedOne == true) .. " secondImmediate=" .. tostring(callTwo and usedTwo == true)
            .. " interval=" .. tostring(castTwoAt - castOneAt) .. " firstSlotOnly=" .. tostring(firstOnly)
            .. " bothConsumed=" .. tostring(bothConsumed) .. " cooldownUnchanged=" .. tostring(unchangedCooldown)
            .. " effect=" .. tostring(effect) .. " effectKind=" .. effectKind .. " damage=" .. tostring(damage)
            .. " vfx=REAL_CAST_PATH_NOT_VISUALLY_CERTIFIED")
        if not callOne then log_warning(tag .. " CAST_EXCEPTION id=" .. id .. " call=1 detail=" .. tostring(usedOne)) end
        if not callTwo then log_warning(tag .. " CAST_EXCEPTION id=" .. id .. " call=2 detail=" .. tostring(usedTwo)) end
    end
end)
-- Even a harness error goes through cleanup. This does not fabricate a game PASS.
local cleanupOk, cleanupError = pcall(restoreTransientState)
if not ok then log_warning(tag .. " HARNESS_EXCEPTION " .. tostring(harnessError)) end
if not cleanupOk then log_warning(tag .. " HARNESS_CLEANUP_EXCEPTION " .. tostring(cleanupError) .. " STOP_PLAY_REQUIRED") end
log(tag .. " DONE observed=" .. tostring(reviewed) .. " pass=" .. tostring(passed) .. " fail=" .. tostring(failed)
    .. " notRun=" .. tostring(#ids - reviewed) .. " interrupted=" .. tostring(interrupted)
    .. " harnessOk=" .. tostring(ok) .. " cleanupOk=" .. tostring(cleanupOk)
    .. " seconds=" .. tostring(_UtilLogic.ElapsedSeconds - beganAt) .. " ABANDON_QA_RUN_REQUIRED")
