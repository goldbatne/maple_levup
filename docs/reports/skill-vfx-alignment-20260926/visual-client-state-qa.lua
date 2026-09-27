local player = _UserService.LocalPlayer
if not isvalid(player) then
    local users = _UserService.UserEntities.Values
    log("[SkillVFXQA] CLIENT NO_LOCAL_PLAYER users=" .. tostring(users and #users or -1))
    player = users and users[1] or nil
end
if not isvalid(player) then return end
local map = player.CurrentMap
local camera = player.CameraComponent
log("[SkillVFXQA] CLIENT map=" .. tostring(map and map.Name)
    .. " playerPos=" .. tostring(player.TransformComponent.WorldPosition)
    .. " camera=" .. tostring(camera ~= nil)
    .. " sprite=" .. tostring(player.SpriteRendererComponent ~= nil))
