-- QA assistance: restores current HP to MaxHp during traversal. Does not change stats, skills,
-- damage, monsters, cooldowns, positions, objectives or saved RPG/M2 data.
-- Consequently this is traversal/clear plumbing evidence, NOT unassisted balance evidence.
local started=_UtilLogic.ElapsedSeconds local lastMap='' local heals=0
log('[AuditAreaServer] BEGIN area='.._GameData.RogueAreaId..' seed='.._GameData.RogueSeed..' path='..table.concat(_GameData.RogueMainPath,'>')..' objective='.._GameData.RogueObjectiveType..' hpAssistance=true')
while _UtilLogic.ElapsedSeconds-started<600 do
 if _GameData.RogueRunComplete or _GameData.RogueRunFailed then
  log('[AuditAreaServer] END complete='..tostring(_GameData.RogueRunComplete)..' failed='..tostring(_GameData.RogueRunFailed)..' heals='..heals) break
 end
 for _,p in ipairs(_UserService.UserEntities.Values) do
  if p.CurrentMap~=nil and p.CurrentMap.Name~='maptown' then
   if p.PlayerComponent.Hp>0 and p.PlayerComponent.Hp<p.PlayerComponent.MaxHp then p.PlayerComponent.Hp=p.PlayerComponent.MaxHp heals+=1 end
   if p.CurrentMap.Name~=lastMap then
    lastMap=p.CurrentMap.Name
    wait(0.5)
    local sp=p.CurrentMap:GetComponent('script.RoomSpawner')
    local entries={}
    if sp~=nil then for _,e in ipairs(sp.spawned) do if isvalid(e) then local m=e:GetComponent('script.RoomMonster') local pos=e.TransformComponent.WorldPosition if m~=nil then entries[#entries+1]=e.Name..':'..tostring(pos)..':HP='..tostring(m.MaxHp) end end end end
    table.sort(entries)
    log('[AuditAreaServer] MAP '..lastMap..' monsters='..#entries..' initial='..table.concat(entries,'|'))
   end
  end
 end
 wait(0.1)
end
