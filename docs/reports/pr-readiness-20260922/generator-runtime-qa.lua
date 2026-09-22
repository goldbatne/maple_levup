-- Maker-only idle lobby; actual generator functions, transient state restored.
-- Graph/room selection/encounter composition determinism, NOT physical traversal.
if not Environment:IsMakerPlay() or _GameData.RogueRunActive then
    log_warning('[PRQA] GENERATOR_BLOCKED ACTIVE_OR_NOT_MAKER') return
end
local fields = {'RogueAreaId','RogueSeed','RogueRandomState','RogueRngStates',
    'RogueBossMonsterId','RogueGenerationAttempt','RogueGraph','RogueRoomRoles',
    'RogueEncounters','RogueMainPath','RogueStartRoomId','RogueFinalRoomId','RogueObjectiveType',
    'RogueRunRevision','RogueRunResult','RogueParticipantResults','RogueLoadedSpawnerEntities',
    'RogueRunComplete','RogueRunFailed','RogueObjectiveComplete','RogueTransitionLocked',
    'RoguePendingDiscoveries'}
local saved = {}
for _, key in ipairs(fields) do saved[key] = _GameData[key] end
local function restore()
    for _, key in ipairs(fields) do _GameData[key] = saved[key] end
end
local function canonical(value)
    if type(value) ~= 'table' then return type(value)..':'..tostring(value) end
    local keys = {}
    for key,_ in pairs(value) do keys[#keys+1] = key end
    table.sort(keys, function(a,b) return tostring(a)<tostring(b) end)
    local out = '{'
    for _,key in ipairs(keys) do out=out..canonical(key)..'='..canonical(value[key])..';' end
    return out..'}'
end
local function fingerprint()
    return canonical({_GameData.RogueGraph,_GameData.RogueRoomRoles,_GameData.RogueEncounters,
        _GameData.RogueMainPath,_GameData.RogueBossMonsterId,_GameData.RogueStartRoomId,
        _GameData.RogueFinalRoomId,_GameData.RogueObjectiveType})
end
local pass, fail = 0,0
local ok,err = pcall(function()
    for a=1,5 do
        for s=1,2 do
            restore()
            local area='mega_0'..a
            local seed=922000+a*100+s
            local validPreflight=_GameData:ValidateRogueliteBeforeRoomCreation(area,seed)
            local restored=true
            for _,key in ipairs(fields) do if _GameData[key] ~= saved[key] then restored=false end end
            _GameData.RogueAreaId=area
            _GameData.RogueSeed=seed
            local first=_GameData:GenerateRogueliteGraph()
            local initial=fingerprint()
            -- Global combat RNG draws must not affect the seeded generator.
            for n=1,5 do math.random() end
            local second=_GameData:GenerateRogueliteGraph()
            local same=initial==fingerprint()
            local row=validPreflight and restored and first and second and same
            if row then pass=pass+1 else fail=fail+1 end
            log('[PRQA] GENERATOR_ROW area='..area..' seed='..seed..' valid='..tostring(first and second)
                ..' preflightRestored='..tostring(restored)..' reproducible='..tostring(same)..' pass='..tostring(row))
        end
    end
    restore()
    local invalid=_GameData:ValidateRogueliteBeforeRoomCreation('invalid_qa_area',1)
    local restored=true
    for _,key in ipairs(fields) do if _GameData[key] ~= saved[key] then restored=false end end
    log('[PRQA] GENERATOR_INVALID rejected='..tostring(not invalid)..' restored='..tostring(restored))
end)
restore()
log('[PRQA] GENERATOR_DONE pass='..pass..' fail='..fail..' harnessOk='..tostring(ok)..' error='..tostring(err))
