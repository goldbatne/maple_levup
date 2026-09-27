-- Transient Monster Skill Mode adapter QA.
-- Casts every player-acquirable ability through the real MonsterAttack.CastSkill path.
-- This is not a claim that every monster naturally rolled every skill in one Run.

local tag = "[MonsterSkillRework66]"
if Environment:IsMakerPlay() == false then log_warning(tag .. " BLOCKED NOT_MAKER") return end
local players = {}
for _, u in ipairs(_UserService.UserEntities.Values) do players[#players + 1] = u end
if #players ~= 1 then log_warning(tag .. " BLOCKED SOLO_ONLY") return end
local p = players[1]
local sp = p.CurrentMap ~= nil and p.CurrentMap:GetComponent("script.RoomSpawner") or nil
local hit = p:GetComponent("script.PlayerHit")
local playerAttack = p:GetComponent("script.PlayerAttack")
if sp == nil or hit == nil or #sp.spawned == 0 or not _GameData.RogueRunActive then
    log_warning(tag .. " BLOCKED NO_RUN_TARGET") return
end
local caster = nil
for _, e in ipairs(sp.spawned) do
    if isvalid(e) and e:GetComponent("script.RoomMonster") ~= nil
        and e:GetComponent("script.MonsterAttack") ~= nil and e.KinematicbodyComponent ~= nil then
        caster = e break
    end
end
if caster == nil then log_warning(tag .. " BLOCKED NO_CASTER") return end
local mon = caster:GetComponent("script.RoomMonster")
local ma = caster:GetComponent("script.MonsterAttack")
local ids = _GameData:GetCapturableActiveSkillIds()
if #ids ~= 66 then log_warning(tag .. " BLOCKED COUNT=" .. tostring(#ids)) return end

local oldPos = caster.TransformComponent.WorldPosition
local playerPos = p.TransformComponent.WorldPosition
local oldMaxHp, oldHp = p.PlayerComponent.MaxHp, p.PlayerComponent.Hp
local oldMonsterMaxHp, oldMonsterHp = mon.MaxHp, mon.Hp
local oldShield, oldShieldUntil = mon.ShieldRatio, mon.ShieldUntil
local oldBoost, oldBoostUntil = mon.AttackBoostRatio, mon.AttackBoostUntil
local oldAi = caster.AIChaseComponent ~= nil and caster.AIChaseComponent.Enable or false
local hadPlayerAuto = playerAttack ~= nil and playerAttack.autoAttackTimer ~= 0
local hadSpawnerCheck = sp.checkTimer ~= 0
local otherMonsters = {}
for i, e in ipairs(sp.spawned) do
    if isvalid(e) and e ~= caster then
        otherMonsters[#otherMonsters + 1] = {
            entity = e, pos = e.TransformComponent.WorldPosition,
            ai = e.AIChaseComponent ~= nil and e.AIChaseComponent.Enable or false
        }
    end
end
local beganAt, reviewed, passed, failed = _UtilLogic.ElapsedSeconds, 0, 0, 0

local function cleanup()
    if isvalid(p) then
        p.PlayerComponent.MaxHp, p.PlayerComponent.Hp = oldMaxHp, math.min(oldHp, oldMaxHp)
        p.KinematicbodyComponent:SetWorldPosition(Vector2(playerPos.x, playerPos.y))
        if hadPlayerAuto and playerAttack ~= nil then playerAttack:RestartAutoAttack() end
    end
    if isvalid(caster) then
        caster.KinematicbodyComponent:SetWorldPosition(Vector2(oldPos.x, oldPos.y))
        mon.ShieldRatio, mon.ShieldUntil = oldShield, oldShieldUntil
        mon.AttackBoostRatio, mon.AttackBoostUntil = oldBoost, oldBoostUntil
        mon.MaxHp, mon.Hp = oldMonsterMaxHp, oldMonsterHp
        if caster.AIChaseComponent ~= nil then caster.AIChaseComponent.Enable = oldAi end
    end
    for _, entry in ipairs(otherMonsters) do
        if isvalid(entry.entity) then
            entry.entity.KinematicbodyComponent:SetWorldPosition(
                Vector2(entry.pos.x, entry.pos.y))
            if entry.entity.AIChaseComponent ~= nil then
                entry.entity.AIChaseComponent.Enable = entry.ai
            end
        end
    end
    if isvalid(sp.Entity) and hadSpawnerCheck and sp.checkTimer == 0 then
        sp.checkTimer = _TimerService:SetTimerRepeat(function() sp:Refill() end,
            sp.RespawnCheckInterval)
    end
    log(tag .. " CLEANUP QA_RUN_ABANDON_REQUIRED")
end

local ok, err = pcall(function()
    if ma.attackTimerId ~= 0 then _TimerService:ClearTimer(ma.attackTimerId) ma.attackTimerId = 0 end
    if hadPlayerAuto then _TimerService:ClearTimer(playerAttack.autoAttackTimer) playerAttack.autoAttackTimer = 0 end
    -- 다른 몬스터의 평타/특수 시전이 HP를 깎아 잘못된 PASS를 만들지 않게 격리한다.
    if sp.checkTimer ~= 0 then _TimerService:ClearTimer(sp.checkTimer) sp.checkTimer = 0 end
    if sp.runRespawnTimer ~= 0 then
        _TimerService:ClearTimer(sp.runRespawnTimer)
        sp.runRespawnTimer = 0
    end
    for i, entry in ipairs(otherMonsters) do
        local e = entry.entity
        if e.AIChaseComponent ~= nil then e.AIChaseComponent.Enable = false end
        if e.MovementComponent ~= nil then e.MovementComponent:Stop() end
        local otherAttack = e:GetComponent("script.MonsterAttack")
        if otherAttack ~= nil and otherAttack.attackTimerId ~= 0 then
            _TimerService:ClearTimer(otherAttack.attackTimerId)
            otherAttack.attackTimerId = 0
        end
        e.KinematicbodyComponent:SetWorldPosition(Vector2(playerPos.x - 7 - i * 0.15,
            playerPos.y + 6))
    end
    if caster.AIChaseComponent ~= nil then caster.AIChaseComponent.Enable = false end
    if caster.MovementComponent ~= nil then caster.MovementComponent:Stop() end
    p.PlayerComponent.MaxHp, p.PlayerComponent.Hp = 1000000, 1000000
    mon.MaxHp, mon.Hp = 1000000, 1000000
    log(tag .. " BEGIN count=66 actualMonsterAttackCastSkill=true")
    for _, id in ipairs(ids) do
        local skill = _GameData:GetSkill(id)
        p.KinematicbodyComponent:SetWorldPosition(Vector2(playerPos.x, playerPos.y))
        -- 일부 돌진/근접 스킬의 실제 적 시전 반경은 1유닛보다 좁다.
        -- 사거리 밖 호출을 실행 실패로 오인하지 않도록 유효한 0.35유닛에서 시험한다.
        caster.KinematicbodyComponent:SetWorldPosition(Vector2(playerPos.x - 0.35, playerPos.y))
        p.PlayerComponent.Hp = 1000000
        hit.LastHitTime = -999
        mon.ShieldRatio, mon.ShieldUntil = 0, 0
        mon.AttackBoostRatio, mon.AttackBoostUntil = 0, 0
        mon.NextAttackBoostRatio, mon.NextAttackBoostUntil = 0, 0
        local unboostedDamage = skill.skill_kind == "buff"
            and ma:CalcDamage(caster, p, "") or 0
        local before = p.PlayerComponent.Hp
        local c, used = pcall(function() return ma:CastSkill(mon, skill) end)
        local waitSeconds = 0.3
        if skill.projectile_ruid ~= "" then waitSeconds = _GameData:GetBalance("projectile_seconds") + 0.25 end
        if skill.dash_distance > 0 then waitSeconds = _GameData:GetBalance("skill_dash_seconds") + 0.25 end
        if skill.behavior == "DELAYED_BLAST" or skill.behavior == "DAMAGE_ZONE" then
            waitSeconds = skill.behavior_delay + math.max(0, skill.behavior_ticks - 1) * skill.behavior_interval + 0.25
        end
        waitSeconds = math.max(waitSeconds,
            skill.secondary_duration * skill.enemy_control_scale + 0.2)
        wait(math.min(2.5, math.max(0.3, waitSeconds)))
        local damage = before - p.PlayerComponent.Hp
        local effect = damage > 0
        local effectKind = "damage"
        if skill.skill_kind == "defense" then
            effectKind = "monster_shield"
            effect = mon.ShieldRatio > 0 and mon.ShieldUntil > _UtilLogic.ElapsedSeconds
        elseif skill.skill_kind == "buff" then
            effectKind = "monster_" .. skill.effect_type
            if skill.effect_type == "next_attack_boost" then
                effect = mon.NextAttackBoostRatio >= skill.effect_value
                    and mon.NextAttackBoostUntil > _UtilLogic.ElapsedSeconds
                    and ma:CalcDamage(caster, p, "") > unboostedDamage
                    and mon.NextAttackBoostRatio == 0
            else
                effect = mon.AttackBoostRatio >= skill.effect_value
                    and mon.AttackBoostUntil > _UtilLogic.ElapsedSeconds
                    and ma:CalcDamage(caster, p, "") > unboostedDamage
            end
        end
        local rowPass = c and used == true and effect
        reviewed = reviewed + 1
        if rowPass then passed = passed + 1 else failed = failed + 1 end
        log(tag .. " ROW id=" .. id .. " status=" .. (rowPass and "PASS_RUNTIME" or "FAIL_RUNTIME")
            .. " behavior=" .. tostring(skill.behavior) .. " secondary=" .. tostring(skill.secondary_effect)
            .. " cast=" .. tostring(c and used == true) .. " effect=" .. tostring(effect)
            .. " effectKind=" .. effectKind .. " damage=" .. tostring(damage)
            .. " controlScale=" .. tostring(skill.enemy_control_scale)
            .. " vfx=ACTUAL_PATH_NOT_VISUAL_CERTIFICATION")
        if not c then log_warning(tag .. " EXCEPTION id=" .. id .. " " .. tostring(used)) end
    end
end)
local cleanOk, cleanErr = pcall(cleanup)
if not ok then log_warning(tag .. " HARNESS_EXCEPTION " .. tostring(err)) end
if not cleanOk then log_warning(tag .. " CLEANUP_EXCEPTION " .. tostring(cleanErr)) end
log(tag .. " DONE observed=" .. tostring(reviewed) .. " pass=" .. tostring(passed)
    .. " fail=" .. tostring(failed) .. " notRun=" .. tostring(66 - reviewed)
    .. " harnessOk=" .. tostring(ok) .. " cleanupOk=" .. tostring(cleanOk)
    .. " seconds=" .. tostring(_UtilLogic.ElapsedSeconds - beganAt))
