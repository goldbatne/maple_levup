local p=_UserService.LocalPlayer
local steps=0
while steps<1800 do
 p=_UserService.LocalPlayer
 if not isvalid(p) or p.CurrentMap==nil then wait(0.1) steps+=1 continue end
 if p.CurrentMap.Name=="maptown" then break end
 local g=_GameData local room=g:GetRoomByMapName(p.CurrentMap.Name)
 if room==nil then wait(0.1) steps+=1 continue end
 local nextId=nil
 for i=1,#g.RogueMainPath-1 do if g.RogueMainPath[i]==room.id then nextId=g.RogueMainPath[i+1] end end
 if nextId==nil then log("[AuditWalk] FINAL map="..p.CurrentMap.Name) break end
 local worked,err=pcall(function()
 local portal=nil
 for _,e in ipairs(p.CurrentMap.Children:ToTable()) do
  local q=e:GetComponent("script.RoomPortal")
  if q~=nil and g:GetRunRoomConnection(room.id,q.direction)==nextId then portal=e end
 end
 if portal==nil then log("[AuditWalk] FAIL missing portal room="..room.id) return end
 local pos=p.TransformComponent.WorldPosition local dest=portal.TransformComponent.WorldPosition
 local dx=dest.x-pos.x local dy=dest.y-pos.y local len=math.sqrt(dx*dx+dy*dy)
 if len>0.1 then p.MovementComponent:MoveToDirection(Vector2(dx/len,dy/len),0) end
 if steps%100==0 then log("[AuditWalk] room="..room.id.." next="..nextId.." pos="..tostring(pos).." distance="..tostring(len)) end
 end)
 if not worked then wait(0.3) end
 steps+=1 wait(0.05)
end
if isvalid(p) then p.MovementComponent:Stop() log("[AuditWalk] END map="..p.CurrentMap.Name.." steps="..tostring(steps)) end
