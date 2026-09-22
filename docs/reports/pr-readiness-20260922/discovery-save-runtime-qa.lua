-- Dedicated Maker SOLO only. Writes ONE new MakerTest_PRQA_* storage key.
-- Never clears/overwrites an existing account key. No natural-kill claim.
-- Grant a real, previously undiscovered Monster/Skill ID through the production
-- reward method (QA-injected kill reward), serialize/read back through PlayerDBManager.
-- ABANDON is confirmed separately via the actual client UI handler.
local settlement = 'ABANDON'
if not Environment:IsMakerPlay() or not _GameData.RogueRunActive then return end
local users = {}
for _,u in ipairs(_UserService.UserEntities.Values) do users[#users+1]=u end
if #users~=1 then log_warning('[PRQA] DISCOVERY_BLOCKED SOLO_ONLY') return end
local p=users[1]
local db=p:GetComponent('script.PlayerDBManager')
local c=p:GetComponent('script.PlayerCollection')
local slots=p:GetComponent('script.PlayerSkillSlots')
if db==nil or c==nil or slots==nil or not db.RogueStorageMode
    or db.KeyRogue~='MakerTest_RoguelitePermanentV1' then
    log_warning('[PRQA] DISCOVERY_BLOCKED NON_TEST_STORAGE') return
end
local monsterId, skillId = '', ''
for _,mid in ipairs(_GameData:GetAllMonsterIds()) do
    local m=_GameData:GetMonster(mid)
    local s=m.drop_skill_id~='' and _GameData:GetSkill(m.drop_skill_id) or nil
    if s~=nil and (s.skill_kind=='attack' or s.skill_kind=='defense')
        and c.RogueDiscoveredMonsters[mid]==nil and c.RogueDiscoveredAbilities[m.drop_skill_id]==nil then
        monsterId=mid skillId=m.drop_skill_id break
    end
end
if monsterId=='' then log_warning('[PRQA] DISCOVERY_BLOCKED NO_UNDISCOVERED_TEST_ID') return end
local originalKey=db.KeyRogue
local qaKey='MakerTest_PRQA_Discovery_20260922_'..settlement..'_'..math.floor(_UtilLogic.ElapsedSeconds*1000)
local old=db:GatherRogueliteRecords()
local oldMonsters=old.discovered_monsters or {}
local oldAbilities=old.discovered_abilities or {}
local ok,err=pcall(function()
    c:GrantRogueliteAbility(monsterId,_GameData:GetMonster(monsterId))
    local pending=_GameData.RoguePendingDiscoveries[p.PlayerComponent.UserId]
    local gathered=db:GatherRogueliteRecords()
    local excluded=(gathered.discovered_monsters or {})[monsterId]==nil
        and (gathered.discovered_abilities or {})[skillId]==nil
    db.KeyRogue=qaKey
    db:SaveNow('PRQA isolated pending serialization')
    local loaded={}
    local readOk=db:BatchGetAndWait(p.PlayerComponent.ProfileCode,{qaKey},loaded)
    local raw=loaded[qaKey]
    local decoded=raw and db:DecodeRogueliteRecord(raw.Value,false) or nil
    local storedExcluded=readOk and decoded~=nil and decoded.discovered_monsters[monsterId]==nil
        and decoded.discovered_abilities[skillId]==nil
    local oldPreserved=decoded~=nil
    if decoded~=nil then
        for id,v in pairs(oldMonsters) do if decoded.discovered_monsters[id]~=v then oldPreserved=false end end
        for id,v in pairs(oldAbilities) do if decoded.discovered_abilities[id]~=v then oldPreserved=false end end
    end
    log('[PRQA] DISCOVERY_SAVED kind='..settlement..' monster='..monsterId..' skill='..skillId
        ..' pending='..tostring(pending~=nil and pending.monsters[monsterId]==1 and pending.abilities[skillId]==1)
        ..' excluded='..tostring(excluded)..' readbackExcluded='..tostring(storedExcluded)
        ..' oldPreserved='..tostring(oldPreserved)..' qaKey='..qaKey)
end)
if (settlement~='FAILED' and settlement~='CLEAR') or not ok then db.KeyRogue=originalKey end
log('[PRQA] DISCOVERY_HARNESS ok='..tostring(ok)..' error='..tostring(err))
if ok and settlement=='FAILED' then
    -- Real death path with QA-injected lethal damage; not natural monster combat.
    p:GetComponent('script.PlayerHit'):OnHit(p,p.PlayerComponent.Hp+100,false,'PRQA_FAILURE',1)
    log('[PRQA] FAIL_SETTLEMENT result='.._GameData.RogueRunResult
        ..' permanentMonster='..tostring(c.RogueDiscoveredMonsters[monsterId]==1)
        ..' permanentAbility='..tostring(c.RogueDiscoveredAbilities[skillId]==1)
        ..' pendingCleared='..tostring(_GameData.RoguePendingDiscoveries[p.PlayerComponent.UserId]==nil))
    db:SaveNow('PRQA isolated FAILED settlement')
    -- Keep isolated key until the entity leaves; lobby uses the normal MakerTest key.
end
