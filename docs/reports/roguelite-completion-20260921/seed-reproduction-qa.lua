local g=_GameData
local saved={}
local fields={"RogueAreaId","RogueSeed","RogueRandomState","RogueGraph","RogueRoomRoles","RogueEncounters","RogueMainPath","RogueStartRoomId","RogueFinalRoomId","RogueObjectiveType","RogueGenerationAttempt"}
for _,k in ipairs(fields) do saved[k]=g[k] end
local ids={}
for k,_ in pairs(g.areas) do if #g:GetRoomsForArea(k)>1 then ids[#ids+1]=k end end
table.sort(ids)
local function signature()
 local out={}
 for _,r in ipairs(g:GetRoomsForArea(g.RogueAreaId)) do
  for _,dir in ipairs({"north","east","south","west"}) do out[#out+1]=r..":"..dir.."="..tostring((g.RogueGraph[r] or {})[dir]) end
  local e=g.RogueEncounters[r] or {}
  out[#out+1]=r..":map="..g.rooms[r].map_name..":role="..tostring(g.RogueRoomRoles[r])..":monster="..tostring(e.monster_id)..":count="..tostring(e.monster_count)
 end
 return g.RogueStartRoomId.."~"..g.RogueFinalRoomId.."~"..g.RogueObjectiveType.."~"..table.concat(g.RogueMainPath,">").."~"..table.concat(out,"|")
end
for _,id in ipairs(ids) do
 for _,seed in ipairs({2026,math.floor(_UtilLogic:RandomDouble()*1000000)+1}) do
  g.RogueAreaId=id g.RogueSeed=seed
  local ok=g:GenerateRogueliteGraph() local sig=signature()
  _UtilLogic:RandomDouble()
  local ok2=g:GenerateRogueliteGraph()
  local branches=0 for _,role in pairs(g.RogueRoomRoles) do if role=="optional_risk" then branches+=1 end end
  log("[AuditSeedV2] "..id.." seed="..seed.." valid="..tostring(ok).." repeat="..tostring(ok2 and sig==signature()).." path="..table.concat(g.RogueMainPath,">").." branches="..branches.." final="..g.RogueFinalRoomId.." attempt="..g.RogueGenerationAttempt)
 end
end
for _,k in ipairs(fields) do g[k]=saved[k] end
log("[AuditSeed] DONE restored lobby state")
