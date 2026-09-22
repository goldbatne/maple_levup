-- Maker server-instance only. QA targets/slots are transient; does not touch saved collection.
-- Calls the real PlayerAttack.UseSkill path. No cooldown deadline is cleared between rounds.
local p=nil
for _,u in ipairs(_UserService.UserEntities.Values) do p=u break end
if not isvalid(p) or p.CurrentMap.Name=="maptown" then log_error("[Audit66] NO_RUN") return end
local slots=p:GetComponent("script.PlayerSkillSlots")
local attack=p:GetComponent("script.PlayerAttack")
local hit=p:GetComponent("script.PlayerHit")
local sp=p.CurrentMap:GetComponent("script.RoomSpawner")
if slots==nil or attack==nil or sp==nil or not slots.RogueliteRunActive then log_error("[Audit66] INVALID_CONTEXT") return end
if attack.autoAttackTimer~=0 then _TimerService:ClearTimer(attack.autoAttackTimer) attack.autoAttackTimer=0 end
local target=nil
for _,e in ipairs(sp.spawned) do
 if isvalid(e) then
  local m=e:GetComponent("script.RoomMonster")
  if m~=nil and not m.IsDead then
   if target==nil then target=e end
   if e.AIChaseComponent~=nil then e.AIChaseComponent.Enable=false end
   if e.MovementComponent~=nil then e.MovementComponent:Stop() end
   local a=e:GetComponent("script.MonsterAttack")
   if a~=nil and a.attackTimerId~=0 then _TimerService:ClearTimer(a.attackTimerId) a.attackTimerId=0 end
  end
 end
end
if target==nil then log_error("[Audit66] NO_TARGET") return end
local m=target:GetComponent("script.RoomMonster")
local beforeHP=m.Hp local beforeMax=m.MaxHp
m.MaxHp=1000000 m.Hp=1000000
local ids=_GameData:GetCapturableActiveSkillIds()
log("[Audit66] BEGIN count="..tostring(#ids).." isolatedTarget=true permanentMutation=false")
for round=1,2 do
 for i,id in ipairs(ids) do
  if not isvalid(p) or not isvalid(target) or not slots.RogueliteRunActive then log_error("[Audit66] INTERRUPTED") return end
  local skill=_GameData:GetSkill(id)
  slots:ClearRandomSlots()
  local offered=slots:OfferRunAbility(_GameData:GetMonsterIdByDropSkillId(id),id)
  local pos=p.TransformComponent.WorldPosition
  local direction=pos.x>0 and -1 or 1
  local distance=skill.dash_distance>0 and skill.dash_distance or 1.1
  target.KinematicbodyComponent:SetWorldPosition(Vector2(pos.x+direction*distance,pos.y))
  wait(0.2)
  local hp=m.Hp
  local called,used=pcall(function() return attack:UseSkill(1,direction,0) end)
  if not called then log_error("[Audit66] CAST_ERROR id="..id.." error="..tostring(used)) used=false end
  local immediate=false
  if called then immediate=attack:UseSkill(1,direction,0) end
  local remain=attack:GetCooldownRemain(id)
  wait(0.65)
  local delta=hp-m.Hp
  local effect=skill.skill_kind=="defense" and hit.ShieldRatio==skill.effect_value or delta>0
  local duplicate=slots:OfferRunAbility(_GameData:GetMonsterIdByDropSkillId(id),id)
  log("[Audit66] ROW round="..round.." id="..id.." offered="..tostring(offered).." used="..tostring(used).." immediate="..tostring(immediate).." remain="..tostring(remain).." retained="..tostring(slots.RandomSlots[1]==id).." damage="..tostring(delta).." effect="..tostring(effect).." duplicate="..tostring(duplicate).." shield="..tostring(hit.ShieldRatio))
 end
end
m.MaxHp=beforeMax m.Hp=beforeHP
slots:ClearRandomSlots()
log("[Audit66] DONE; isolated encounter ends with this QA Run; no natural acquisition claim")
