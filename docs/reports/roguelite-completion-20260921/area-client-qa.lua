-- Movement and owner skill RPC only. No teleport, kill, objective or clear shortcut.
-- Run with area-server-observer.lua. HP assistance must be reported separately from normal play.
local started=_UtilLogic.ElapsedSeconds
local lastRoom='' local lastLog=0 local nextCast=0
local route={} local routeIndex=1 local routeKey='' local routeRetry=0
local function buildRoute(map,pos,dest)
 local tm=map:GetFirstChildComponentByTypeName('RectTileMapComponent',true)
 if tm==nil then return nil end
 local water=map:GetComponent('script.NautilusWaterBoundary')
 local function key(x,y) return tostring(x)..','..tostring(y) end
 local a=tm:ToCellPosition(pos) local b=tm:ToCellPosition(dest)
 local queue={{x=a.x,y=a.y}} local parents={} local seen={[key(a.x,a.y)]=true} local head=1 local found=nil
 while head<=#queue and head<=4096 do
  local n=queue[head] head+=1
  if n.x==b.x and n.y==b.y then found=n break end
  for _,d in ipairs({{1,0},{-1,0},{0,1},{0,-1}}) do
   local x=n.x+d[1] local y=n.y+d[2] local k=key(x,y)
   if not seen[k] then
    seen[k]=true local tile=tm:GetTile(x,y)
    if tile~=nil and not tile.IsCollidable and (water==nil or tile.Name~=water.waterTileName) then
     queue[#queue+1]={x=x,y=y} parents[k]=n
    end
   end
  end
 end
 if found==nil then return nil end
 local reverse={} local n=found
 while n.x~=a.x or n.y~=a.y do
  reverse[#reverse+1]=tm:ToWorldPosition(n.x,n.y) n=parents[key(n.x,n.y)]
 end
 local result={}
 for i=#reverse,1,-1 do result[#result+1]=reverse[i] end
 result[#result+1]=dest
 return result
end
while _UtilLogic.ElapsedSeconds-started<600 do
 local p=_UserService.LocalPlayer
 if not isvalid(p) or p.CurrentMap==nil then wait(0.1) continue end
 if p.CurrentMap.Name=='maptown' then log('[AuditAreaClient] LOBBY elapsed='..tostring(_UtilLogic.ElapsedSeconds-started)) break end
 local ok,err=pcall(function()
  local g=_GameData local room=g:GetRoomByMapName(p.CurrentMap.Name)
  if room==nil then return end
  if lastRoom~=room.id then log('[AuditAreaClient] ENTER '..room.id) lastRoom=room.id end
  local nextId=nil
  for i=1,#g.RogueMainPath-1 do if g.RogueMainPath[i]==room.id then nextId=g.RogueMainPath[i+1] end end
  local dest=nil local combat=false
  if nextId~=nil then
   for _,e in ipairs(p.CurrentMap.Children:ToTable()) do
    if not isvalid(e) then continue end
    local q=e:GetComponent('script.RoomPortal')
    if q~=nil and g:GetRunRoomConnection(room.id,q.direction)==nextId then dest=e.TransformComponent.WorldPosition break end
   end
  else
   local distance=100000
   local pos=p.TransformComponent.WorldPosition
   for _,e in ipairs(p.CurrentMap.Children:ToTable()) do
    if not isvalid(e) then continue end
    local m=e:GetComponent('script.RoomMonster')
    if m~=nil and not m.IsDead then
     local ep=e.TransformComponent.WorldPosition local dx=ep.x-pos.x local dy=ep.y-pos.y
     local d=dx*dx+dy*dy
     if d<distance then dest=ep distance=d combat=true end
    end
   end
  end
  if dest==nil then p.MovementComponent:Stop() return end
  local pos=p.TransformComponent.WorldPosition
  local dx=dest.x-pos.x local dy=dest.y-pos.y local len=math.sqrt(dx*dx+dy*dy)
  local now=_UtilLogic.ElapsedSeconds
  local tm=p.CurrentMap:GetFirstChildComponentByTypeName('RectTileMapComponent',true)
  local goal=tm:ToCellPosition(dest)
  local k=room.id..':'..tostring(goal.x)..','..tostring(goal.y)
  if routeKey~=k or now>routeRetry then
   route=buildRoute(p.CurrentMap,pos,dest) routeIndex=1 routeKey=k routeRetry=now+300
   if route==nil then log('[AuditAreaClient] NO_TILE_ROUTE room='..room.id..' target='..k) end
  end
  if route~=nil and len>(combat and 0.9 or 0.1) then
   while routeIndex<#route do
    local w=route[routeIndex] local wx=w.x-pos.x local wy=w.y-pos.y
    if wx*wx+wy*wy>0.04 then break end
    routeIndex+=1
   end
   local w=route[routeIndex] local wx=w.x-pos.x local wy=w.y-pos.y local wl=math.sqrt(wx*wx+wy*wy)
   if wl>0.01 then p.MovementComponent:MoveToDirection(Vector2(wx/wl,wy/wl),0.016) else p.MovementComponent:Stop() end
  else p.MovementComponent:Stop() end
  if now>nextCast and len<4 then
   local attack=p:GetComponent('script.PlayerAttack')
   local slots=p:GetComponent('script.PlayerSkillSlots')
   if attack~=nil and slots~=nil then for i=1,5 do if slots.RandomSlots[i]~=nil and slots.RandomSlots[i]~='' then attack:RequestUseSkill(i,dx,dy) end end end
   nextCast=now+1
  end
  if now-lastLog>10 then log('[AuditAreaClient] WALK room='..room.id..' remaining='..tostring(len)..' finalCombat='..tostring(combat)) lastLog=now end
 end)
 if not ok then log('[AuditAreaClient] TRANSITION_RETRY '..tostring(err)) wait(0.3) end
 wait(0.016)
end
local p=_UserService.LocalPlayer
if isvalid(p) then p.MovementComponent:Stop() end
log('[AuditAreaClient] END')
