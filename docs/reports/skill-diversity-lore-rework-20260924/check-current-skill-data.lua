-- Maker-only readback of the data actually loaded by the running world.
if not Environment:IsMakerPlay() then return end
for _, id in ipairs({"s_mon_drumming_bunny", "s_mon_chief_memory_guardian"}) do
    local skill = _GameData:GetSkill(id)
    local row = _DataService:GetTable("SkillTable"):FindRow("id", id)
    log("[SkillDataReadback] " .. id
        .. " runtime=" .. tostring(skill ~= nil and skill.skill_kind)
        .. "/" .. tostring(skill ~= nil and skill.behavior)
        .. " dataset=" .. tostring(row ~= nil and row:GetItem("skill_kind"))
        .. "/" .. tostring(row ~= nil and row:GetItem("behavior")))
end
