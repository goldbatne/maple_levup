-- Transient Maker server-instance QA for the 66 player-acquirable abilities.
-- Uses the real PlayerAttack.UseSkill -> Attack/defense/VFX/token-consume path.
-- It changes no persistent collection and blocks DataStorage writes while running.
-- Run only inside a dedicated SOLO Maker Run, then abandon/stop the session.

local tag = "[SkillRework66]"
if Environment:IsMakerPlay() == false then log_warning(tag .. " BLOCKED NOT_MAKER") return end
local players = {}
for _, u in ipairs(_UserService.UserEntities.Values) do players[#players + 1] = u end
if #players ~= 1 then log_warning(tag .. " BLOCKED SOLO_ONLY") return end
local p = players[1]
if not isvalid(p) or p.CurrentMap == nil or p.CurrentMap.Name == "maptown" then
    log_warning(tag .. " BLOCKED NO_RUN") return
end
local slots = p:GetComponent("script.PlayerSkillSlots")
local attack = p:GetComponent("script.PlayerAttack")
local hit = p:GetComponent("script.PlayerHit")
local db = p:GetComponent("script.PlayerDBManager")
local sp = p.CurrentMap:GetComponent("script.RoomSpawner")
if slots == nil or attack == nil or hit == nil or db == nil or sp == nil
    or not _GameData.RogueRunActive or not attack:CanActInCurrentRun() then
    log_warning(tag .. " BLOCKED INVALID_COMPONENTS") return
end
if db.RogueStorageMode ~= true or string.sub(tostring(db.KeyRogue), 1, 10) ~= "MakerTest_" then
    log_warning(tag .. " BLOCKED NON_TEST_STORAGE") return
end
local ids = _GameData:GetCapturableActiveSkillIds()
if #ids ~= 66 then log_warning(tag .. " BLOCKED COUNT=" .. tostring(#ids)) return end

local monsters = {}
for _, e in ipairs(sp.spawned) do
    if isvalid(e) then
        local mon = e:GetComponent("script.RoomMonster")
        if mon ~= nil and not mon.IsDead and e.KinematicbodyComponent ~= nil then
            monsters[#monsters + 1] = { entity = e, mon = mon,
                hp = mon.Hp, maxHp = mon.MaxHp, pos = e.TransformComponent.WorldPosition,
                ai = e.AIChaseComponent ~= nil and e.AIChaseComponent.Enable or false }
        end
    end
end
if #monsters == 0 then log_warning(tag .. " BLOCKED NO_TARGET") return end

local target = monsters[1].entity
local targetMon = monsters[1].mon
local origin = p.TransformComponent.WorldPosition
local originalHp = p.PlayerComponent.Hp
local originalSlots = {}
for i = 1, slots:GetSkillSlotMax() do originalSlots[i] = slots.RandomSlots[i] end
local originalShield, originalShieldUntil = hit.ShieldRatio, hit.ShieldUntil
local originalBoost, originalBoostUntil = attack.OutgoingBoostRatio, attack.OutgoingBoostUntil
local originalNextBoost, originalNextBoostUntil = attack.NextAttackBoostRatio, attack.NextAttackBoostUntil
local originalWriteBlocked = db.StorageWriteBlocked
local hadAuto = attack.autoAttackTimer ~= 0
local hadSpawnerCheck = sp.checkTimer ~= 0
local beganAt, maxSeconds = _UtilLogic.ElapsedSeconds, 330
local reviewed, passed, failed = 0, 0, 0

local function live()
    return isvalid(p) and isvalid(target) and p.CurrentMap == sp.Entity
        and target.CurrentMap == sp.Entity
        and _GameData.RogueRunActive and attack:CanActInCurrentRun()
        and _UtilLogic.ElapsedSeconds - beganAt < maxSeconds
end

local function cleanup()
    if isvalid(p) then
        slots:StopRandomSkillSupply()
        slots:ClearRandomSlots()
        for i = 1, slots:GetSkillSlotMax() do slots.RandomSlots[i] = originalSlots[i] end
        p.KinematicbodyComponent:SetWorldPosition(Vector2(origin.x, origin.y))
        p.PlayerComponent.Hp = originalHp
        hit.ShieldRatio, hit.ShieldUntil = originalShield, originalShieldUntil
        attack.OutgoingBoostRatio, attack.OutgoingBoostUntil = originalBoost, originalBoostUntil
        attack.NextAttackBoostRatio, attack.NextAttackBoostUntil = originalNextBoost, originalNextBoostUntil
        db.StorageWriteBlocked = originalWriteBlocked
        if hadAuto then attack:RestartAutoAttack() end
    end
    if isvalid(sp.Entity) and hadSpawnerCheck and sp.checkTimer == 0 then
        sp.checkTimer = _TimerService:SetTimerRepeat(function() sp:Refill() end,
            sp.RespawnCheckInterval)
    end
    for _, entry in ipairs(monsters) do
        if isvalid(entry.entity) and not entry.mon.IsDead then
            entry.mon.MaxHp, entry.mon.Hp = entry.maxHp, entry.hp
            entry.mon:ResetSkillControls()
            entry.entity.KinematicbodyComponent:SetWorldPosition(Vector2(entry.pos.x, entry.pos.y))
            if entry.entity.AIChaseComponent ~= nil then entry.entity.AIChaseComponent.Enable = entry.ai end
        end
    end
    log(tag .. " CLEANUP QA_RUN_ABANDON_REQUIRED")
end

local ok, err = pcall(function()
    db.StorageWriteBlocked = true
    slots:StopRandomSkillSupply()
    if hadAuto then _TimerService:ClearTimer(attack.autoAttackTimer) attack.autoAttackTimer = 0 end
    -- 고정 표적 검증 중 방 리스폰이 새 표적을 끼워 넣지 않게 감시를 잠시 중단한다.
    if sp.checkTimer ~= 0 then _TimerService:ClearTimer(sp.checkTimer) sp.checkTimer = 0 end
    if sp.runRespawnTimer ~= 0 then
        _TimerService:ClearTimer(sp.runRespawnTimer)
        sp.runRespawnTimer = 0
    end
    for _, entry in ipairs(monsters) do
        entry.mon.MaxHp, entry.mon.Hp = 1000000, 1000000
        if entry.entity.AIChaseComponent ~= nil then entry.entity.AIChaseComponent.Enable = false end
        if entry.entity.MovementComponent ~= nil then entry.entity.MovementComponent:Stop() end
        local ma = entry.entity:GetComponent("script.MonsterAttack")
        if ma ~= nil and ma.attackTimerId ~= 0 then _TimerService:ClearTimer(ma.attackTimerId) ma.attackTimerId = 0 end
    end
    log(tag .. " BEGIN count=66 actualUseSkill=true saveWritesBlocked=true")
    local previousDash = false
    for _, id in ipairs(ids) do
        if not live() then break end
        local skill = _GameData:GetSkill(id)
        if skill == nil then error("MISSING_SKILL " .. tostring(id)) end
        slots:StopRandomSkillSupply()
        slots:ClearRandomSlots()
        slots.RandomSlots[1], slots.RandomSlots[2] = id, id
        p.KinematicbodyComponent:SetWorldPosition(Vector2(origin.x, origin.y))
        p.PlayerComponent.Hp = p.PlayerComponent.MaxHp
        hit.ShieldRatio, hit.ShieldUntil = 0, 0
        attack.OutgoingBoostRatio, attack.OutgoingBoostUntil = 0, 0
        attack.NextAttackBoostRatio, attack.NextAttackBoostUntil = 0, 0
        -- 지연/지속 영역은 첫 표적을 판정 중심에 놓는다. 중심에서는
        -- PULL/KNOCKBACK 방향 벡터가 0이므로 두 번째 표적에서 이동을 검증한다.
        local offCenterImpulse = (skill.secondary_effect == "PULL"
            and skill.behavior == "PROJECTILE_BLAST")
            or ((skill.secondary_effect == "PULL" or skill.secondary_effect == "KNOCKBACK")
                and (skill.behavior == "DAMAGE_ZONE" or skill.behavior == "DELAYED_BLAST"))
        for i, entry in ipairs(monsters) do
            entry.mon.MaxHp, entry.mon.Hp = 1000000, 1000000
            entry.mon:ResetSkillControls()
            -- ResetSkillControls는 추적 AI를 다시 켠다. 고정 QA 표적은
            -- 매 행마다 재차 비활성화하고 남은 이동 명령도 취소한다.
            if entry.entity.AIChaseComponent ~= nil then
                entry.entity.AIChaseComponent.Enable = false
            end
            if entry.entity.MovementComponent ~= nil then
                entry.entity.MovementComponent:Stop()
            end
            -- 다른 몬스터가 돌진/광역 판정에 끼어 우연한 피해를 PASS로 만들지 않는다.
            local x, y = origin.x - 7 - i * 0.15, origin.y + 6
            if i == 1 then
                local distance = 1.0
                if skill.dash_distance > 0 then distance = skill.dash_distance end
                if skill.behavior == "DAMAGE_ZONE" or skill.behavior == "DELAYED_BLAST" then
                    distance = math.min(skill.range > 0 and skill.range
                        or _GameData:GetBalance("player_attack_range"), 5)
                end
                x, y = origin.x + distance, origin.y
            elseif i == 2 and offCenterImpulse then
                -- 중심에 정확히 맞은 몬스터는 당길 방향이 0이다. 광역 효과는
                -- 중심 밖의 두 번째 몬스터로 검증한다.
                local centerDistance = 1.0
                if skill.behavior == "DAMAGE_ZONE" then
                    centerDistance = math.min(skill.range > 0 and skill.range
                        or _GameData:GetBalance("player_attack_range"), 5)
                end
                -- DELAYED_BLAST에서는 두 번째 표적을 앞쪽(3.8)에 놓아
                -- 그 지점이 조준 중심이 되고 첫 표적(5.0)이 비중심 피해·이동 증인이 된다.
                -- 뒤쪽(6.2)에 두면 사거리 밖이거나 충돌 판정 한 개만 잡혀
                -- 첫 표적의 피해 0으로 잘못 실패할 수 있다.
                local offset = skill.behavior == "DELAYED_BLAST" and -1.2 or 1.2
                x, y = origin.x + centerDistance + offset, origin.y
            end
            entry.entity.KinematicbodyComponent:SetWorldPosition(Vector2(x, y))
        end
        -- 실제 돌진 뒤에는 클라이언트 이동 동기화가 서버의 QA 재배치를 잠시
        -- 덮어쓸 수 있다. 다음 스킬이 빗나간 것으로 오인하지 않도록 기다린다.
        wait(previousDash and 2.0 or 0.2)
        local beforePlayerPos = p.TransformComponent.WorldPosition
        local beforeTargetPos = target.TransformComponent.WorldPosition
        local before = targetMon.Hp
        local unboostedDamage = skill.skill_kind == "buff"
            and attack:CalcDamage(p, target, "") or 0
        local cooldownBefore = attack.SkillReadyAt[id]
        local c1, u1 = pcall(function() return attack:UseSkill(1, 1, 0) end)
        slots:StopRandomSkillSupply()
        local firstConsumed = slots.RandomSlots[1] == nil and slots.RandomSlots[2] == id
        local c2, u2 = pcall(function() return attack:UseSkill(2, 1, 0) end)
        slots:StopRandomSkillSupply()
        local bothConsumed = slots.RandomSlots[1] == nil and slots.RandomSlots[2] == nil
        local cooldownUnchanged = attack.SkillReadyAt[id] == cooldownBefore
        local waitSeconds = 0.35
        if skill.projectile_ruid ~= "" then waitSeconds = _GameData:GetBalance("projectile_seconds") + 0.25 end
        if skill.dash_distance > 0 then waitSeconds = _GameData:GetBalance("skill_dash_seconds") + 0.25 end
        if skill.behavior == "DELAYED_BLAST" or skill.behavior == "DAMAGE_ZONE" then
            waitSeconds = skill.behavior_delay + math.max(0, skill.behavior_ticks - 1) * skill.behavior_interval + 0.25
        end
        wait(math.min(2.5, math.max(0.25, waitSeconds)))
        local damage = before - targetMon.Hp
        local effect = damage > 0
        local effectKind = "damage"
        if skill.skill_kind == "defense" then
            effectKind = "shield"
            effect = skill.effect_type == "shield" and hit.ShieldRatio > 0 and hit.ShieldUntil > _UtilLogic.ElapsedSeconds
        elseif skill.skill_kind == "buff" then
            effectKind = skill.effect_type
            if skill.effect_type == "next_attack_boost" then
                effect = attack.NextAttackBoostRatio >= skill.effect_value
                    and attack.NextAttackBoostUntil > _UtilLogic.ElapsedSeconds
                    and attack:CalcDamage(p, target, "") > unboostedDamage
                    and attack.NextAttackBoostRatio == 0
            else
                effect = skill.effect_type == "attack_boost"
                    and attack.OutgoingBoostRatio >= skill.effect_value
                    and attack.OutgoingBoostUntil > _UtilLogic.ElapsedSeconds
                    and attack:CalcDamage(p, target, "") > unboostedDamage
            end
        end
        local secondaryObserved = skill.secondary_effect == ""
        if skill.secondary_effect ~= "" then
            local witness = (offCenterImpulse and skill.behavior ~= "DELAYED_BLAST")
                and monsters[2] or monsters[1]
            secondaryObserved = witness ~= nil
                and witness.mon.LastControlEffect == skill.secondary_effect
        end
        local rowPass = c1 and u1 == true and c2 and u2 == true and firstConsumed
            and bothConsumed and cooldownUnchanged and effect and secondaryObserved
        reviewed = reviewed + 1
        if rowPass then passed = passed + 1 else failed = failed + 1 end
        log(tag .. " ROW id=" .. id .. " status=" .. (rowPass and "PASS_RUNTIME" or "FAIL_RUNTIME")
            .. " behavior=" .. tostring(skill.behavior) .. " secondary=" .. tostring(skill.secondary_effect)
            .. " use1=" .. tostring(c1 and u1 == true) .. " use2=" .. tostring(c2 and u2 == true)
            .. " consume1=" .. tostring(firstConsumed) .. " consume2=" .. tostring(bothConsumed)
            .. " noCooldown=" .. tostring(cooldownUnchanged) .. " effectKind=" .. effectKind
            .. " effect=" .. tostring(effect)
            .. " secondaryObserved=" .. tostring(secondaryObserved) .. " damage=" .. tostring(damage)
            .. " vfx=ACTUAL_PATH_NOT_VISUAL_CERTIFICATION")
        if not c1 then log_warning(tag .. " EXCEPTION id=" .. id .. " call=1 " .. tostring(u1)) end
        if not c2 then log_warning(tag .. " EXCEPTION id=" .. id .. " call=2 " .. tostring(u2)) end
        if not rowPass then
            log_warning(tag .. " FAIL_CONTEXT id=" .. id
                .. " player=" .. tostring(beforePlayerPos)
                .. " target=" .. tostring(beforeTargetPos)
                .. " targetAfter=" .. tostring(target.TransformComponent.WorldPosition))
        end
        previousDash = skill.dash_distance > 0
    end
end)
local cleanOk, cleanErr = pcall(cleanup)
if not ok then log_warning(tag .. " HARNESS_EXCEPTION " .. tostring(err)) end
if not cleanOk then log_warning(tag .. " CLEANUP_EXCEPTION " .. tostring(cleanErr)) end
log(tag .. " DONE observed=" .. tostring(reviewed) .. " pass=" .. tostring(passed)
    .. " fail=" .. tostring(failed) .. " notRun=" .. tostring(66 - reviewed)
    .. " harnessOk=" .. tostring(ok) .. " cleanupOk=" .. tostring(cleanOk)
    .. " seconds=" .. tostring(_UtilLogic.ElapsedSeconds - beganAt))
